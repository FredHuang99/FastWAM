"""One H100, frozen inputs, temporary diagnostic hooks; zero optimizer updates."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import math
from pathlib import Path
import signal
import time
import traceback

from .grasp_bridge import files, read, sha, signature, verify, write
from .memory_probe import VARIANTS, stop_check


def tensor_statistics(value):
    import torch
    with torch.no_grad(), torch.autocast("cuda", enabled=False):
        x = value.detach().float()
        if not bool(torch.isfinite(x).all()):
            raise FloatingPointError("Non-finite diagnostic activation")
        return {"shape": list(x.shape), "dtype": str(value.dtype),
                "rms": float(x.square().mean().sqrt()), "max_abs": float(x.abs().max())}


def slot_statistics(value):
    import numpy as np
    # Small 32x1024 CPU statistics. No stochastic operation or model-state change.
    x = value.detach().float().cpu().numpy().astype(np.float64)
    if x.ndim != 3 or x.shape[1:] != (32, 1024) or not np.isfinite(x).all():
        raise ValueError("Expected finite [B,32,1024] memory slots")
    x = x[0]
    norm = np.linalg.norm(x, axis=1)
    gram = x @ x.T
    cosine = gram / np.maximum(np.outer(norm, norm), 1e-30)
    eigenvalues = np.maximum(np.linalg.eigvalsh(gram), 0)
    probability = eigenvalues / max(float(eigenvalues.sum()), 1e-30)
    nonzero = probability[probability > 0]
    return {"centered_norm_ratio": float(np.linalg.norm(x - x.mean(0)) / max(np.linalg.norm(x), 1e-30)),
            "min_cosine": float(cosine.min()), "mean_token_norm": float(norm.mean()),
            "rank_one_energy_fraction": float(probability[-1]),
            "effective_rank": float(np.exp(-(nonzero * np.log(nonzero)).sum()))}


@contextmanager
def variant(model, mode):
    """Change only memory math/readout within this scope; restore instance methods."""
    import torch
    if mode not in VARIANTS:
        raise ValueError(f"Unknown probe mode: {mode}")
    if mode == "original":
        yield
        return
    changed = []
    def replace(module, name, replacement):
        previous = module.__dict__.get(name)
        present = name in module.__dict__
        changed.append((module, name, present, previous))
        setattr(module, name, replacement)
    try:
        original_read = model.memory.read
        def read_memory(*args, **kwargs):
            if kwargs:
                raise ValueError("Expected positional production memory inputs")
            if mode == "mean_readout":
                value = original_read(*args)
                return value.mean(1, keepdim=True).expand_as(value).contiguous()
            with torch.autocast("cuda", enabled=False):
                converted = [value.float() if isinstance(value, torch.Tensor) and value.is_floating_point()
                             else value for value in args]
                return original_read(*converted)
        replace(model.memory, "read", read_memory)
        if mode == "memory_fp32":
            for injector in model.memory.injectors.values():
                original_forward = injector.forward
                def forward(action, readout, gate_scale=1.0, original=original_forward):
                    with torch.autocast("cuda", enabled=False):
                        return original(action.float(), readout.float(), gate_scale)
                replace(injector, "forward", forward)
        yield
    finally:
        for module, name, present, previous in reversed(changed):
            if present:
                setattr(module, name, previous)
            else:
                delattr(module, name)


class Collector:
    """Observe actual Q/K/V and residuals; derived weights never replace SDPA."""
    def __init__(self, memory):
        self.memory = memory
        self.handles = []
        self.qkv = {}
        self.counts = {}
        self.records = {"reader": [], "attention": [], "injection": [], "query_components": []}
        self.arrays = {}
        self.injected_readout = None
        self.injected_readout_statistics = None

    def __enter__(self):
        from .modules import Attention
        for name, module in self.memory.named_modules():
            if isinstance(module, Attention):
                for part in ("q", "k", "v"):
                    def save(_module, _args, result, name=name, part=part):
                        self.qkv.setdefault(name, {})[part] = result.detach()
                    self.handles.append(getattr(module, part).register_forward_hook(save))
                def attention(module, args, result, name=name):
                    self.observe_attention(name, module, args)
                self.handles.append(module.register_forward_hook(attention))
        for index, block in enumerate(self.memory.reader):
            def reader(_module, _args, result, index=index):
                self.records["reader"].append({"layer": index, **slot_statistics(result)})
                self.arrays[f"reader_{index}"] = result.detach().float().cpu().numpy()
            self.handles.append(block.register_forward_hook(reader))
        def query(_module, args):
            actual = args[0]
            self.records["query_input"] = slot_statistics(actual)
            self.records["learned_queries"] = tensor_statistics(self.memory.queries)
            self.records["shared_condition"] = tensor_statistics(actual - self.memory.queries[None])
            self.arrays["query_input"] = actual.detach().float().cpu().numpy()
        self.handles.append(self.memory.reader[0].register_forward_pre_hook(query))
        for name in ("history_projection", "text_projection", "proprio_projection"):
            def component(_module, args, result, name=name):
                if args[0].ndim == 2:
                    self.records["query_components"].append({"component": name, **tensor_statistics(result)})
            self.handles.append(getattr(self.memory, name).register_forward_hook(component))
        for layer, module in self.memory.injectors.items():
            def injection(_module, args, result, layer=layer):
                delta = result.detach().float() - args[0].detach().float()
                # action_velocity converts the returned residual to the frozen
                # expert's dtype after the injector; capture that effective delta.
                effective = result.detach().to(args[0].dtype).float() - args[0].detach().float()
                if self.injected_readout is not args[1]:
                    self.injected_readout = args[1]
                    self.injected_readout_statistics = slot_statistics(args[1])
                self.records["injection"].append({"layer": int(layer), "gate": float(_module.gate.detach()),
                    "raw_delta": tensor_statistics(delta), "effective_delta": tensor_statistics(effective),
                    "readout": self.injected_readout_statistics})
            self.handles.append(module.register_forward_hook(injection))
        return self

    def observe_attention(self, name, module, args):
        import torch
        with torch.no_grad(), torch.autocast("cuda", enabled=False):
            values = self.qkv.pop(name)
            q, k, v = [values[part].float() for part in ("q", "k", "v")]
            def split(value):
                return value.unflatten(-1, (module.heads, value.shape[-1] // module.heads)).transpose(1, 2)
            scores = split(q) @ split(k).transpose(-1, -2) / (q.shape[-1] // module.heads) ** .5
            valid = args[2] if len(args) > 2 else None
            if valid is not None:
                scores = scores.masked_fill(~valid[:, None, None, :], -float("inf"))
            weights = scores.softmax(-1)
            if not bool(torch.isfinite(weights).all()):
                raise FloatingPointError("Non-finite derived attention weights")
            entropy = -(weights * weights.clamp_min(1e-30).log()).sum(-1)
            valid_count = k.shape[1] if valid is None else int(valid[0].sum())
            entropy = entropy / max(math.log(max(valid_count, 2)), 1e-30)
            count = self.counts.get(name, 0)
            self.counts[name] = count + 1
            centered_v = v - v.mean(1, keepdim=True)
            record = {"module": name, "call": count, "q_dtype": str(values["q"].dtype),
                "k_dtype": str(values["k"].dtype), "v_dtype": str(values["v"].dtype),
                "normalized_entropy": float(entropy.mean()),
                "max_weight": float(weights.max()), "v_centered_norm_ratio": float(centered_v.norm() / v.norm().clamp_min(1e-30)),
                "query_to_query_weight_max_difference": float((weights - weights.mean(-2, keepdim=True)).abs().max()),
                "scope": "FP32 weights derived from actual projected Q/K; diagnostic only; production SDPA output unchanged"}
            self.records["attention"].append(record)
            if name.startswith("injectors.") and count in (0, 9):
                self.arrays[name.replace(".", "_") + f"_weights_{count}"] = weights.cpu().numpy()

    def __exit__(self, *_):
        for handle in self.handles:
            handle.remove()
        self.qkv.clear()
        self.injected_readout = None


def assemble(model, encoders, cfg, folder, window):
    import numpy as np
    import torch
    from PIL import Image
    from .common import ReleaseNormalizer
    from .data import observation_tensor
    from .history import resolve_online, select_ids
    from .model import encode_latent, encode_text
    item = window["item"]
    device = next(model.memory.parameters()).device
    norm = ReleaseNormalizer(cfg["paths"]["stats"])
    sampling = resolve_online(cfg, item["task"], item["seed"], item["anchor"])
    if sampling != window["sampling"]:
        raise ValueError("Actual T/phase differs from frozen sampling identity")
    chosen = select_ids(range(item["anchor"] + 1), item["anchor"], sampling["period"], phase=sampling["phase"])
    raw = {row["frame_id"]: row for row in window["observations"]}
    if sorted(raw) != chosen:
        raise ValueError("Frozen raw observations differ from exact selected IDs")
    features = []
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        text, text_valid = encode_text(encoders[1], encoders[2], item["instruction"], device)
        for index in chosen:
            row = raw[index]
            arrays = []
            for name in row["images"]:
                with Image.open(folder / name) as image:
                    arrays.append(np.ascontiguousarray(image.convert("RGB")))
            if row.get("pixels_sha256"):
                import hashlib
                if [hashlib.sha256(x.tobytes()).hexdigest() for x in arrays] != row["pixels_sha256"]:
                    raise ValueError("Expert rendered pixels changed")
            mosaic = observation_tensor(arrays, device)
            proprio = norm.normalize(torch.tensor(row["proprio"], dtype=torch.float32, device=device)[None], "state")
            latent = encode_latent(encoders[0], mosaic)
            feature, _, _ = model.backbone.encode_observation(latent, text, proprio, keep_kv=False)
            features.append(feature[0])
        native_target = torch.as_tensor(item["targets"], dtype=torch.float32, device=device)[None]
        batch = {"latent": latent, "proprio": proprio, "text": text, "text_valid": text_valid,
                 "history": torch.stack(features)[None], "frame_ids": torch.tensor(chosen, device=device)[None],
                 "history_valid": torch.ones(1, len(chosen), dtype=torch.bool, device=device),
                 "actions": norm.normalize(native_target, "action"),
                 "action_valid": torch.ones(1, 32, dtype=torch.bool, device=device),
                 "t": torch.tensor([item["anchor"]], device=device)}
    return batch, native_target


def receipt(directory, identity, result):
    write(directory / "result.json", result)
    mapping = {name: value for name, value in files(directory).items()
               if name != "COMPLETE.json" and not name.endswith(".log") and name != "progress.json"}
    write(directory / "COMPLETE.json", {"identity": identity, "files": mapping})


def reuse(directory, identity, output):
    if (directory / "COMPLETE.json").exists():
        value = read(directory / "COMPLETE.json")
        if value["identity"] != identity:
            raise ValueError(f"Completed case identity differs: {directory}")
        verify(directory, value["files"])
        return read(directory / "result.json")
    if directory.exists():
        destination = output / "interrupted" / f"{directory.name}_{time.time_ns()}"
        destination.parent.mkdir(parents=True, exist_ok=True)
        directory.rename(destination)
    directory.mkdir(parents=True)
    return None


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--gpu-uuid", required=True)
    args = parser.parse_args()
    output, root = args.output.resolve(), args.root.resolve()
    directory = output / "probe"
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: (_ for _ in ()).throw(InterruptedError("Memory worker stopped")))
    started = time.monotonic()
    try:
        import numpy as np
        import torch
        from .common import ReleaseNormalizer
        from .diagnosis_gpu import load_weight
        from .eval_state import cuda_gpu_uuid
        from .integration_contract import configure_numerics
        from .model import S1Model, load_observation_encoders
        bound = read(output / "IDENTITY.json")
        run_identity = signature(bound)
        spec, cfg = bound["protocol"], bound["config"]
        if (torch.cuda.device_count() != 1 or cuda_gpu_uuid(0) != args.gpu_uuid
                or torch.cuda.get_device_capability(0) != (9, 0)):
            raise ValueError("Expected the bound single H100")
        configure_numerics(cfg)
        write(directory / "progress.json", {"stage": "model_load", "completed": 0, "total": 24})
        print("[model_load] frozen base/encoders; no dense cache or simulator; initialization ETA unknown", flush=True)
        device = torch.device("cuda:0")
        model = S1Model(cfg, device).eval()
        encoders = load_observation_encoders(cfg, device)
        weight_binding = {"weights": {name: {"path": str(root / value["relative"]), "sha256": value["sha256"]}
                                      for name, value in bound["weights"].items()}, "resources": bound["resources"]}
        load_weight(model, weight_binding, "step_002000")
        normalizer = ReleaseNormalizer(cfg["paths"]["stats"])
        windows = read(output / "WINDOWS.json")
        prepared = {}
        for window in windows:
            stop_check(output)
            write(directory / "progress.json", {"stage": "encode_frozen_window", "case": window["id"], "completed": 0, "total": 24})
            encode_started = time.monotonic()
            batch, targets = assemble(model, encoders, cfg, output / "inputs" / window["id"], window)
            prepared[window["id"]] = (window, batch, targets)
            print(f"[encode] {window['id']} history={len(window['observations'])} elapsed={time.monotonic()-encode_started:.1f}s", flush=True)
        controls = {}
        # Condition-only checkpoints reveal whether slot similarity predates S1.
        # No action sample is added to the fixed 24-case budget.
        for label in ("step_000000", "step_002000"):
            load_weight(model, weight_binding, label)
            for key, (window, batch, targets) in prepared.items():
                stop_check(output)
                with torch.no_grad(), Collector(model.memory) as collector:
                    _, _, readout = model.conditions(batch)
                controls[label + "/" + key] = {"readout": slot_statistics(readout), "trace": collector.records}
        write(directory / "controls.json", controls)
        parameter_versions = {name: parameter._version for name, parameter in model.memory.named_parameters()}
        results, durations = [], []
        references = {"put_train_initial": "put_back_block_train_initial_2000", "swap_val_initial": "swap_blocks_val_initial_2000"}
        for key, (window, batch, targets) in prepared.items():
            baselines = {}
            for noise_name in spec["noises"]:
                noise_info = window["noise"][noise_name]
                noise_path = output / "inputs" / key / noise_info["path"]
                if sha(noise_path) != noise_info["sha256"]:
                    raise ValueError("Frozen noise changed")
                noise = torch.from_numpy(np.load(noise_path, allow_pickle=False)).to(device)
                for mode in VARIANTS:
                    stop_check(output)
                    case_identity = signature({"run": run_identity, "window": window, "noise": noise_name, "mode": mode})
                    case_dir = directory / "cases" / f"{key}_{noise_name}_{mode}"
                    value = reuse(case_dir, case_identity, output)
                    if value is None:
                        write(directory / "progress.json", {"stage": "action_sample", "case": key, "mode": mode,
                              "noise": noise_name, "completed": len(results), "total": 24,
                              "case_started_unix": time.time(),
                              "remaining_sample_seconds": np.mean(durations) * (24-len(results)) if durations else None})
                        case_started = time.monotonic()
                        with torch.no_grad(), variant(model, mode), Collector(model.memory) as collector:
                            _, _, pre_readout = model.conditions(batch)
                            # sample builds its own conditions, so the reader is observed
                            # twice. This also checks repeatability of the actual inputs.
                            actions, readout = model.sample(batch, noise)
                        torch.cuda.synchronize(device)
                        if not torch.equal(pre_readout, readout):
                            raise ValueError("Same frozen conditions produced different readouts")
                        native = normalizer.denormalize(actions)
                        current = native.detach().cpu().numpy()
                        exact_reference = None
                        if mode == "original" and noise_name == "production" and key in references:
                            with np.load(output / "references" / (references[key] + ".npz")) as reference:
                                expected = reference["normalized_actions"]
                            actual = actions[0].cpu().numpy()
                            exact_reference = bool(np.array_equal(expected, actual))
                            if not exact_reference:
                                delta = float(np.max(abs(expected - actual)))
                                raise ValueError(f"Instrumented original path differs from authenticated previous output: {key}, max_abs={delta}")
                        if mode == "original":
                            baselines[noise_name] = current.copy()
                        if noise_name not in baselines:
                            raise ValueError("Original case must precede its counterfactuals")
                        error = (native[:, :16] - targets[:, :16]).float()
                        arm = [0,1,2,3,4,5,7,8,9,10,11,12]
                        stats = slot_statistics(readout)
                        value = {"case": key, "noise": noise_name, "mode": mode,
                            "arm_rmse_first16_rad": float(error[..., arm].square().mean().sqrt()),
                            "wrist_mae_first16_rad": float(error[..., 12].abs().mean()),
                            "gripper_mae_first16": error[..., [6,13]].abs().mean((0,1)).cpu().tolist(),
                            "joint_mae_first16": error.abs().mean((0,1)).cpu().tolist(),
                            "max_action_delta_from_original": float(np.max(abs(current - baselines[noise_name]))),
                            "readout_centered_norm_ratio": stats["centered_norm_ratio"], "readout_min_cosine": stats["min_cosine"],
                            "readout_statistics": stats, "exact_historical_reference": exact_reference,
                            "frame_ids": batch["frame_ids"].cpu().tolist(), "sampling": window["sampling"],
                            "seconds": time.monotonic()-case_started, "optimizer_updates": 0}
                        write(case_dir / "trace.json", collector.records)
                        np.savez_compressed(case_dir / "trace.npz", **collector.arrays,
                            normalized_actions=actions.cpu().numpy(), native_actions=current,
                            target=targets.cpu().numpy(), readout=readout.float().cpu().numpy(),
                            noise=noise.cpu().numpy(), frame_ids=batch["frame_ids"].cpu().numpy())
                        receipt(case_dir, case_identity, value)
                    else:
                        with np.load(case_dir / "trace.npz") as stored:
                            if mode == "original":
                                baselines[noise_name] = stored["native_actions"].copy()
                    if value["seconds"] > spec["case_timeout_seconds"]:
                        raise TimeoutError(f"Bounded action case exceeded time budget: {case_dir}")
                    results.append(value)
                    durations.append(value["seconds"])
                    eta = float(np.mean(durations) * (24-len(results)))
                    write(directory / "progress.json", {"stage": "action_sample", "case": key, "mode": mode,
                          "completed": len(results), "total": 24, "remaining_sample_seconds": eta})
                    print(f"[probe] {len(results)}/24 {key} noise={noise_name} mode={mode} "
                          f"arm_RMSE={value['arm_rmse_first16_rad']:.6f}rad elapsed={time.monotonic()-started:.1f}s "
                          f"remaining_sampling~{eta:.0f}s (encoding/backward/pack excluded)", flush=True)
        gradients = []
        for key, (window, batch, targets) in prepared.items():
            stop_check(output)
            grad_dir = directory / "gradients" / key
            grad_identity = signature({"run": run_identity, "case": window, "tau": spec["gradient_tau"], "mode": "original"})
            value = reuse(grad_dir, grad_identity, output)
            if value is None:
                write(directory / "progress.json", {"stage": "FM_backward_no_update", "case": key,
                      "completed": 24, "total": 24, "remaining_sample_seconds": 0})
                model.zero_grad(set_to_none=True)
                noise = torch.from_numpy(np.load(output / "inputs" / key / window["noise"]["production"]["path"], allow_pickle=False)).to(device)
                try:
                    loss, detail = model(batch, noise, torch.tensor([spec["gradient_tau"]], device=device))
                    if not bool(torch.isfinite(loss)):
                        raise FloatingPointError("Non-finite fixed-condition FM loss")
                    loss.backward()
                    values = {name: float(p.grad.float().norm()) for name, p in model.memory.named_parameters() if p.grad is not None}
                    if not values or not all(np.isfinite(list(values.values()))):
                        raise FloatingPointError("Missing/non-finite memory gradients")
                    if any(p.grad is not None or p.requires_grad for p in model.backbone.parameters()):
                        raise ValueError("Base must remain frozen without gradients")
                    value = {"case": key, "tau": spec["gradient_tau"], "loss": float(loss.detach()),
                             "unweighted_fm": float(detail["unweighted_fm"].mean()),
                             "parameter_gradients": values, "optimizer_updates": 0}
                    receipt(grad_dir, grad_identity, value)
                finally:
                    model.zero_grad(set_to_none=True)
            gradients.append(value)
            print(f"[backward] {len(gradients)}/4 {key} tau={spec['gradient_tau']} updates=0", flush=True)
        for record in bound["weights"].values():
            if sha(root / record["relative"]) != record["sha256"]:
                raise ValueError("Checkpoint file changed during probe")
        if parameter_versions != {name: parameter._version for name, parameter in model.memory.named_parameters()}:
            raise ValueError("Memory parameters were modified during a zero-update probe")
        if len(results) != 24 or len(gradients) != 4:
            raise ValueError("Fixed probe budget incomplete")
        error_path = directory / "ERROR.json"
        if error_path.exists():
            destination = output / "interrupted" / f"ERROR_{time.time_ns()}.json"
            destination.parent.mkdir(parents=True, exist_ok=True)
            error_path.rename(destination)
        receipt(directory, run_identity, {"cases": results, "gradients": gradients, "controls": controls,
            "action_samples": 24, "FM_backward_probes": 4, "optimizer_updates": 0, "simulation_episodes": 0,
            "weight_files_unchanged": True, "seconds": time.monotonic()-started})
        write(directory / "progress.json", {"stage": "complete", "completed": 24, "total": 24,
              "remaining_sample_seconds": 0, "optimizer_updates": 0})
        print("[complete] 24 samples + 4 backward probes; checkpoints unchanged; review before any repair/pilot", flush=True)
    except BaseException:
        write(directory / "ERROR.json", {"traceback": traceback.format_exc()})
        raise


if __name__ == "__main__":
    main()

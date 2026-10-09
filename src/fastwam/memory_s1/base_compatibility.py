"""Offline inference compatibility diagnostics; no training or cache rebuild."""
from __future__ import annotations

import argparse
from pathlib import Path
import time

import h5py
import torch

from .common import (ReleaseNormalizer, append_jsonl, atomic_json, code_version,
                     load_config, read_json, seed_for, sha256)
from .data import mosaic_rgb, observation_tensor, official_decoder
from .model import S1Model, encode_latent, encode_text, load_observation_encoders
from .native_reference import build_reference, native_actions
from .protocol import format_task_prompt, inference_contract, verify_released_prompt


def difference(actual, expected, atol=0.02, rtol=0.02):
    actual, expected = actual.detach().float(), expected.detach().float()
    error = (actual - expected).abs()
    finite = bool(torch.isfinite(actual).all() and torch.isfinite(expected).all())
    return {"mae": float(error.mean()), "maximum_abs": float(error.max()),
            "allclose": finite and bool(torch.allclose(actual, expected, atol=atol, rtol=rtol)),
            "atol": atol, "rtol": rtol, "finite": finite}


def kv_differences(custom, native):
    if len(custom[0]) != len(native[0]) or len(custom[1]) != len(native[1]):
        raise ValueError("Custom and native KV layer counts differ.")
    return [{"layer": layer, "k": difference(k, nk), "v": difference(v, nv)}
            for layer, (k, nk, v, nv) in enumerate(zip(custom[0], native[0], custom[1], native[1]))]


def kv_passed(rows):
    return bool(rows) and all(row["k"]["allclose"] and row["v"]["allclose"] for row in rows)


@torch.no_grad()
@torch.autocast("cuda", enabled=False)
def compare_case(model, reference, encoders, mosaic, proprio, instruction, noise_seed):
    vae, text_encoder, tokenizer = encoders
    device = mosaic.device
    text, valid = encode_text(text_encoder, tokenizer, instruction, device)
    native_text, native_mask = reference.encode_prompt(format_task_prompt(instruction))
    native_latent = reference._encode_input_image_latents_tensor(mosaic.to(torch.bfloat16), tiled=False)
    with torch.autocast("cuda", dtype=torch.bfloat16):
        latent = encode_latent(vae, mosaic)
        _, kv, context = model.backbone.encode_observation(latent, text, proprio)
        # Use the native latent/context inputs to isolate the Video DiT implementation.
        _, shared_kv, shared_context = model.backbone.encode_observation(native_latent, native_text, proprio)
    native_context = reference._append_proprio_to_context(native_text, native_mask, proprio)
    expert = reference.video_expert
    prepared = expert.prepare(x=native_latent, timestep=torch.zeros(1, device=device, dtype=torch.bfloat16),
                              context=native_context[0], context_mask=native_context[1], action=None,
                              fuse_vae_embedding_in_latents=expert.fuse_vae_embedding_in_latents)
    tokens, _, modulation, ctx, ctx_mask, freqs, _, _, _, tokens_per_frame = prepared
    mask = reference._build_mot_attention_mask(tokens.shape[1], 32, tokens_per_frame, device)
    native_k, native_v = reference.mot.prefill_video_cache_tensor(
        tokens, freqs, modulation, ctx, ctx_mask, mask[:tokens.shape[1], :tokens.shape[1]])
    noise = torch.randn(1, 32, 14, generator=torch.Generator(device="cpu").manual_seed(noise_seed)).to(device)
    trace, shared_trace = [], []
    actions = noise.to(torch.bfloat16).clone()
    timesteps, deltas = reference.infer_action_scheduler.build_inference_schedule(10, device, actions.dtype, shift_override=1.0)
    for step, (timestep, delta) in enumerate(zip(timesteps, deltas)):
        native_velocity = reference._denoise_action_with_video_cache(
            actions, timestep[None], native_context[0], native_context[1], native_k, native_v, mask[tokens.shape[1]:])
        with torch.autocast("cuda", dtype=torch.bfloat16):
            custom_velocity = model.backbone.action_velocity(actions, timestep[None], context, kv, model.memory, None, 0.0)
            # Use identical native KV/context to isolate the Action DiT implementation.
            shared_velocity = model.backbone.action_velocity(
                actions, timestep[None], native_context, (native_k, native_v), model.memory, None, 0.0)
        trace.append({"step": step, "timestep": float(timestep), **difference(custom_velocity, native_velocity)})
        shared_trace.append({"step": step, "timestep": float(timestep), **difference(shared_velocity, native_velocity)})
        actions = reference.infer_action_scheduler.step(native_velocity, delta, actions)
    custom, _ = model.sample({}, noise, gate_scale=0.0, prepared_conditions=(kv, context, None))
    # This invokes the original complete infer_action, including its own text and VAE paths.
    native = native_actions(reference, mosaic, proprio, noise_seed, instruction=instruction)[None]
    report = {"text": difference(text, native_text, 0.0, 0.0),
              "latent": difference(latent, native_latent, 0.0, 0.0),
              "context": difference(context[0], native_context[0], 0.0, 0.0),
              "context_same_latent": difference(shared_context[0], native_context[0], 0.0, 0.0),
              "kv_layers": kv_differences(kv, (native_k, native_v)),
              "kv_same_latent_layers": kv_differences(shared_kv, (native_k, native_v)),
              "velocity_trace": trace, "normalized_actions": difference(custom, native),
              "velocity_same_kv_trace": shared_trace,
              "custom_normalized_actions": custom[0].cpu().tolist(), "native_normalized_actions": native[0].cpu().tolist(),
              "text_valid_tokens": int(valid.sum()), "noise_seed": noise_seed}
    checks = {key: report[key]["allclose"] for key in
              ("text", "latent", "context", "context_same_latent", "normalized_actions")}
    checks.update(kv=kv_passed(report["kv_layers"]),
                  kv_same_latent=kv_passed(report["kv_same_latent_layers"]),
                  velocity=all(row["allclose"] for row in trace),
                  velocity_same_kv=all(row["allclose"] for row in shared_trace))
    report["checks"] = checks
    report["failed_checks"] = [key for key, passed in checks.items() if not passed]
    report["passed"] = all(checks.values())
    return report


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--episodes-per-task", type=int, default=2)
    parser.add_argument("--anchors", default="0,64,128")
    args = parser.parse_args()
    if args.episodes_per_task <= 0:
        parser.error("episodes-per-task must be positive")
    anchors = sorted(set(int(i) for i in args.anchors.split(",")))
    if not anchors or min(anchors) < 0 or any(i % 16 for i in anchors):
        parser.error("anchors must be nonnegative multiples of 16")
    cfg = load_config(args.config)
    verify_released_prompt(cfg["root"])
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    if (output / "cases.jsonl").exists():
        raise ValueError("Existing compatibility report: preserve it and use a new output directory.")
    manifest = read_json(Path(cfg["paths"]["prepared"]) / "manifest.json")
    approval = read_json(Path(cfg["paths"]["prepared"]) / "alignment_approved.json")
    from .common import fingerprint
    if approval.get("manifest_sha") != fingerprint(manifest) or approval.get("approved") is not True:
        raise ValueError("Prepared data must retain its reviewed alignment approval.")
    records = []
    for task in ("put_back_block", "swap_blocks"):
        candidates = sorted((r for r in manifest["episodes"] if r["task"] == task and r["split"] == "val"), key=lambda r: r["episode_id"])
        if len(candidates) < args.episodes_per_task:
            raise ValueError(f"Not enough validation episodes for {task}")
        records.extend(candidates[:args.episodes_per_task])
    device = torch.device("cuda:0")
    torch.manual_seed(cfg["seed"])
    print("[load] loading one shared base and encoders; no model downloads", flush=True)
    loading_started = time.monotonic()
    model = S1Model(cfg, device).eval()
    print(f"[load] base and memory ready; seconds={time.monotonic() - loading_started:.1f}", flush=True)
    encoders = load_observation_encoders(cfg, device)
    reference = build_reference(model.backbone, encoders)
    print(f"[load] VAE/T5/tokenizer ready; total_seconds={time.monotonic() - loading_started:.1f}", flush=True)
    decoder = official_decoder(Path(cfg["root"]) / cfg["closed_loop"]["simulator_root"])
    normalizer = ReleaseNormalizer(cfg["paths"]["stats"])
    results, started = [], time.monotonic()
    total = sum(sum(i < r["length"] for i in anchors) for r in records)
    for record in records:
        raw = Path(cfg["root"]) / record["raw"]
        if sha256(raw) != record["raw_sha256"]:
            raise ValueError(f"Raw episode checksum changed: {raw}")
        episode = torch.load(Path(cfg["paths"]["prepared"]) / record["file"], map_location="cpu", weights_only=True)
        with h5py.File(raw, "r") as file:
            for index in (i for i in anchors if i < record["length"]):
                mosaic = observation_tensor([decoder(file[key][index]) for key in record["camera_paths"]], device)
                state = normalizer.normalize(episode["states"][index][None].to(device), "state")
                noise_seed = seed_for(cfg["seed"], index, len(results), "base-compatibility-noise")
                row = compare_case(model, reference, encoders, mosaic, state, record["instruction"], noise_seed)
                row.update(task=record["task"], episode_id=record["episode_id"], frame_id=index,
                           prompt=format_task_prompt(record["instruction"]))
                append_jsonl(output / "cases.jsonl", row)
                results.append(row)
                eta = (time.monotonic() - started) / len(results) * (total - len(results))
                print(f"[compatibility] {len(results)}/{total} passed={row['passed']} "
                      f"failed={row['failed_checks']} latent_mae={row['latent']['mae']:.6g} "
                      f"action_mae={row['normalized_actions']['mae']:.6g} ETA={eta:.1f}s", flush=True)
    print("[provenance] verifying base/VAE/T5 checksums and recording code version", flush=True)
    result = {"complete": True, "passed": all(r["passed"] for r in results), "cases": len(results),
              "comparison_version": "isolated_precision_v3",
              "failed_cases": [{"episode_id": r["episode_id"], "frame_id": r["frame_id"],
                                "failed_checks": r["failed_checks"]} for r in results if not r["passed"]],
              "inference_contract": inference_contract(), "base_sha256": sha256(cfg["paths"]["base"]),
              "stats_sha256": sha256(cfg["paths"]["stats"]), "vae_sha256": sha256(cfg["paths"]["vae"]),
              "t5_sha256": sha256(cfg["paths"]["t5"]), "code": code_version(cfg["root"]),
              "seconds": time.monotonic() - started,
              "scope": "Same resized RGB mosaic and state normalizer; original eager model methods. Numerical compatibility does not approve basic manipulation."}
    atomic_json(output / "summary.json", result)
    print(f"[complete] passed={result['passed']} report={output / 'summary.json'}", flush=True)
    raise SystemExit(0 if result["passed"] else 2)


if __name__ == "__main__":
    main()

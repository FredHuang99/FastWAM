"""5090 closed-loop diagnosis, step 2 (plan v10 E.2 / node N1, 11-11): WHY the 5090 renders differently.

firstrender (11-11 13:54) settled the first question: the 5090 policy on the A100's frame-0 request reproduces the
A100's first chunk (lag-0 arm RMSE 0.0015 <= 0.01), so the policy numerics are fine; the 5090's own camera images
differ from the A100's (mean |diff| 3.7-4.1 levels, 16-19 % of pixels > 8 levels, max 84-170) and that alone shifts
the chunk by two targets. RMBench renders with SAPIEN's path tracer: shader "rt", 32 samples per pixel, path depth 8,
OIDN denoiser (envs/_base_task.py setup_scene). This script, run with the SIMULATOR python inside the RMBench root,
renders frame 0 of one official scene under several render settings and compares every variant with
  (a) the A100's frame-0 request of the same scene (relayed: closed_loop/check_from_a100/request_000000.pkl),
  (b) a second render of the same variant (is the renderer deterministic on this machine?),
  (c) optionally frame 0 of training demos (--demos N): the hdf5 images the policy was trained on, with the demo's
      seed from the task's seed.txt (is this machine's render closer to the training images than the A100's?).
Variants (name: shader / samples per pixel / denoiser): default rt/32/oidn (= RMBench), rt32_none, rt128_oidn,
rt256_none, raster (shader "default", no path tracing). Pre-registered reading:
  - rt256_none much closer to the A100 than rt32_none (mean |diff| down >= 40 %): the difference is path-tracing
    noise; both machines converge to the same image and the 32-sample noise realisation differs by GPU;
  - default vs default (b) not identical: the 5090 render is not even deterministic;
  - every variant >= 3 levels from the A100: a scene / asset / camera difference (versions), not noise.
Read-only (writes its report and pictures under report/). Prints package versions first.

  cd /workspace/FastWAM/resources/RMBench && /opt/rmbench-fused-env/bin/python -B -u \
     /workspace/FastWAM-memory2/scripts/memory_v2/migrate/render_check.py --task put_back_block --seed 4300030 \
     --reference /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/check_from_a100/request_000000.pkl --demos 2
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import random
import subprocess
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

O = Path(os.environ.get("MEMV2_OUT", "/workspace/FastWAM-memory2/outputs/memory_v2"))
FROZEN = Path("/workspace/FastWAM/scripts/memory_s1")
BJ = timezone(timedelta(hours=8))
CAMERAS = ("head_camera", "left_camera", "right_camera")
VARIANTS = {"default": ("rt", 32, "oidn"), "rt32_none": ("rt", 32, "none"), "rt128_oidn": ("rt", 128, "oidn"),
            "rt256_none": ("rt", 256, "none"), "rt512_none": ("rt", 512, "none"), "rt1024_none": ("rt", 1024, "none"),
            "raster": ("default", None, None)}
LINES = []


def say(*parts):
    line = " ".join(str(p) for p in parts)
    print(line, flush=True)
    LINES.append(line)


def versions():
    say("## versions")
    say("python", sys.version.split()[0], sys.executable)
    for name in ("sapien", "numpy", "torch", "mplib", "transforms3d", "trimesh", "cv2"):
        try:
            module = __import__(name)
            say(f"  {name} {getattr(module, '__version__', '?')} {getattr(module, '__file__', '')}")
        except Exception as error:                      # noqa: BLE001 (report and go on)
            say(f"  {name}: not importable ({type(error).__name__})")
    try:
        import sapien
        root = Path(sapien.__file__).parent
        libs = sorted({p.name for p in root.rglob("*") if p.suffix in (".so",) or ".so." in p.name})
        say("  sapien shared libraries:", ", ".join(x for x in libs if any(k in x.lower() for k in ("oidn", "optix", "vulkan", "svulkan", "sapien")))[:600])
    except Exception:                                    # noqa: BLE001
        pass
    for var in ("VK_ICD_FILENAMES", "NVIDIA_DRIVER_CAPABILITIES", "CUDA_VISIBLE_DEVICES", "SAPIEN_RENDERER_DEVICE"):
        say(f"  env {var}={os.environ.get(var)}")
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=index,name,driver_version,memory.used", "--format=csv,noheader"],
                             capture_output=True, text=True, timeout=30).stdout.strip()
        say("  nvidia-smi:", out.replace("\n", " | "))
    except Exception:                                    # noqa: BLE001
        say("  nvidia-smi: unavailable")


def patch_render(variant):
    """Make RMBench's setup_scene use this variant's settings (its own calls are replaced)."""
    import sapien.render as render
    shader, spp, denoiser = VARIANTS[variant]
    if not hasattr(render, "_mwam_original"):
        render._mwam_original = {k: getattr(render, k) for k in (
            "set_camera_shader_dir", "set_ray_tracing_samples_per_pixel", "set_ray_tracing_denoiser",
            "set_ray_tracing_path_depth")}
    original = render._mwam_original
    render.set_camera_shader_dir = lambda _value: original["set_camera_shader_dir"](shader)
    render.set_ray_tracing_samples_per_pixel = (
        lambda value: original["set_ray_tracing_samples_per_pixel"](spp if spp is not None else value))
    render.set_ray_tracing_denoiser = (
        lambda value: original["set_ray_tracing_denoiser"](denoiser if denoiser is not None else value))
    render.set_ray_tracing_path_depth = original["set_ray_tracing_path_depth"]


def frame0(environment, config, seed, ordinal, is_test):
    random.seed(seed)
    environment.setup_demo(now_ep_num=ordinal, seed=seed, is_test=is_test, **config)
    observation = environment.get_obs()
    images = [np.ascontiguousarray(observation["observation"][c]["rgb"], dtype=np.uint8) for c in CAMERAS]
    state = np.asarray(observation["joint_action"]["vector"], dtype=np.float32)
    environment.close_env()
    return images, state


def compare(a, b):
    d = np.abs(a.astype(np.int16) - b.astype(np.int16))
    return {"mean": float(d.mean()), "max": int(d.max()), "over8": float((d > 8).mean() * 100),
            "mean_rgb_a": [round(float(x), 1) for x in a.reshape(-1, 3).mean(0)],
            "mean_rgb_b": [round(float(x), 1) for x in b.reshape(-1, 3).mean(0)]}


def row(name, other, pairs):
    cells = [compare(a, b) for a, b in pairs]
    mean = sum(c["mean"] for c in cells) / len(cells)
    over = sum(c["over8"] for c in cells) / len(cells)
    say(f"| {name} | {other} | " + " | ".join(f"{c['mean']:.2f} / {c['over8']:.1f} % / {c['max']}" for c in cells)
        + f" | {mean:.2f} / {over:.1f} % |")
    return {"mean": mean, "over8": over, "cameras": cells}


def reference_images(path):
    req = pickle.loads(Path(path).read_bytes())
    obs = sorted(req["observations"], key=lambda r: int(r["frame_id"]))[0]
    return [np.frombuffer(b, dtype=np.uint8).reshape(s) for b, s in zip(obs["images"], obs["shapes"])], req


def demo_images(task, k):
    """Frame 0 of training demo k (hdf5) and its seed from seed.txt; (None, None) when either is missing."""
    import h5py
    root = Path.cwd() / "data/demo_clean" / task
    seeds_file = next((p for p in (root / "seed.txt", root / "aloha_agilex/seed.txt") if p.is_file()), None)
    files = sorted((root / "aloha_agilex/data").glob("*.hdf5"))
    if seeds_file is None:
        say(f"  no seed.txt under {root}: " + ", ".join(sorted(p.name for p in root.iterdir())[:12]))
        return None, None
    seeds = [int(x) for x in seeds_file.read_text().split()]
    if k >= len(files) or k >= len(seeds):
        return None, None
    images = []
    with h5py.File(files[k], "r") as f:
        keys = next((ks for ks in ([f"observation/{c}/rgb" for c in CAMERAS],
                                   [f"vision/{c}/colors" for c in ("cam_head", "cam_left_wrist", "cam_right_wrist")])
                     if all(x in f for x in ks)), None)
        if keys is None:
            say(f"  {files[k].name}: no camera keys; top level {list(f.keys())}")
            return None, None
        for key in keys:
            value = f[key][0]
            if isinstance(value, np.ndarray) and value.dtype == np.uint8 and value.ndim == 3:
                images.append(np.ascontiguousarray(value))
                continue
            import cv2
            raw = np.frombuffer(value.tobytes() if isinstance(value, np.ndarray) else bytes(value), dtype=np.uint8)
            img = cv2.imdecode(raw, cv2.IMREAD_COLOR)
            if img is None:
                say(f"  {key}: undecodable frame 0 ({type(value).__name__}, {getattr(value, 'dtype', '')})")
                return None, None
            images.append(np.ascontiguousarray(img[:, :, ::-1]))            # BGR -> RGB
    say(f"  demo {k}: {files[k].name}, keys {keys[0]} ..., shapes {[x.shape for x in images]}, seed {seeds[k]}")
    return images, seeds[k]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--task", default="put_back_block")
    ap.add_argument("--seed", type=int, default=4300030)
    ap.add_argument("--ordinal", type=int, default=0, help="the scene's ordinal in the bank (setup_demo now_ep_num)")
    ap.add_argument("--reference", default=str(O / "closed_loop/check_from_a100/request_000000.pkl"))
    ap.add_argument("--variants", nargs="+", default=["default", "rt32_none", "rt128_oidn", "rt256_none", "raster"],
                    choices=list(VARIANTS))
    ap.add_argument("--demos", type=int, default=0, help="also compare with frame 0 of the first N training demos")
    args = ap.parse_args()
    stamp = datetime.now(BJ).strftime("%Y%m%d_%H%M")
    pictures = O / "report" / f"render_check_{stamp}"
    pictures.mkdir(parents=True, exist_ok=True)
    say(f"# RENDER_CHECK {datetime.now(BJ):%Y-%m-%d %H:%M} task {args.task} seed {args.seed} (cwd {Path.cwd()})")
    versions()
    ref, req = reference_images(args.reference)
    say(f"reference: {args.reference} (task {req.get('task')}, seed {req.get('episode_seed')}, frame "
        f"{sorted(int(r['frame_id']) for r in req['observations'])[0]})")
    if req.get("task") != args.task or int(req.get("episode_seed", -1)) != args.seed:
        say("WARNING: the reference request is another scene; comparison (a) is meaningless")

    sys.path[:0] = [str(FROZEN)]
    import sim_eval                                     # frozen memory_s1 code, imported read-only
    official = sim_eval.load_official()
    results = {}

    def probe(task, environment, config, model, start, **unused):
        config["eval_mode"] = True
        config["render_freq"] = 0
        say("\n## (a) / (b) frame 0 vs the A100 reference and vs a second render (mean |diff| / % > 8 / max, "
            "per camera head / left / right; last column the mean)")
        say("| variant | vs | head | left | right | mean |")
        say("|---|---|---|---|---|---|")
        for variant in args.variants:
            try:
                patch_render(variant)
                t0 = time.monotonic()
                first, state = frame0(environment, config, args.seed, args.ordinal, True)
                seconds = time.monotonic() - t0
                second, _ = frame0(environment, config, args.seed, args.ordinal, True)
                results[variant] = {"vs_a100": row(variant, "A100", list(zip(first, ref))),
                                    "vs_self": row(variant, "itself", list(zip(first, second))),
                                    "setup_and_render_seconds": round(seconds, 1)}
                say(f"|  | setup + first render {seconds:.1f} s |  |  |  |  |")
                np.savez_compressed(pictures / f"{variant}.npz", *first)
                if variant == "default":
                    ref_state = np.asarray(sorted(req["observations"], key=lambda r: int(r["frame_id"]))[0]["proprio"])
                    say(f"|  | proprio max |diff| vs A100 {float(np.abs(state - ref_state).max()):.2e} |  |  |  |  |")
            except Exception:                            # noqa: BLE001 (one variant failing must not hide the rest)
                say(f"| {variant} | FAILED | {traceback.format_exc().splitlines()[-1][:120]} |  |  |  |")
        np.savez_compressed(pictures / "a100_reference.npz", *ref)
        if args.demos:
            say("\n## (c) frame 0 of training demos: this machine's render vs the hdf5 images (the training distribution)")
            say("| render | demo seed | head | left | right | mean |")
            say("|---|---|---|---|---|---|")
            for k in range(args.demos):
                try:
                    images, seed = demo_images(args.task, k)
                    if images is None:
                        break
                    for variant in ("default", "rt256_none"):
                        patch_render(variant)
                        rendered, _ = frame0(environment, config, seed, k, False)
                        if [x.shape for x in rendered] != [x.shape for x in images]:
                            import cv2
                            images = [cv2.resize(x, (r.shape[1], r.shape[0]), interpolation=cv2.INTER_AREA)
                                      for x, r in zip(images, rendered)]
                            say(f"|  | hdf5 images resized to the render size {rendered[0].shape} |  |  |  |  |")
                        results[f"demo{k}_{variant}"] = row(f"{variant} demo {k}", str(seed), list(zip(rendered, images)))
                        np.savez_compressed(pictures / f"demo{k}_{variant}.npz", *rendered)
                    np.savez_compressed(pictures / f"demo{k}_hdf5.npz", *images)
                except Exception:                        # noqa: BLE001
                    say(f"| demo {k} | FAILED | {traceback.format_exc().splitlines()[-1][:120]} |  |  |  |")
        return 0, 0, 0

    official.eval_policy = probe
    official.eval_function_decorator = lambda policy, name: lambda config: None
    try:
        official.main({"task_name": args.task, "task_config": "demo_clean", "ckpt_setting": "render_check",
                       "policy_name": "deploy_policy", "instruction_type": "seen", "seed": 42})
    except SystemExit:
        pass
    path = O / "report" / f"RENDER_CHECK_{stamp}.md"
    path.write_text("\n".join(LINES) + "\n", encoding="utf-8")
    (O / "report" / f"RENDER_CHECK_{stamp}.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
    print(f"RENDER_CHECK: {path}\npictures (npz per variant): {pictures}", flush=True)


if __name__ == "__main__":
    main()

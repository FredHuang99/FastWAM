"""Plan v12 AL0 (Opus checklist 1): what differs between our machines' closed-loop pipelines, before any replay.

  collect --machine NAME [--episodes FOLDER:LABEL ...] [--search ROOT --labels L ...]
      writes outputs/fullft/align/AL0_<NAME>.json: host (CPU model, cores, memory, GPU, driver), thread variables,
      the policy python (torch, CUDA, cuDNN, numpy), the SIMULATOR python's packages (probed in that python: sapien and
      its bundled libraries incl. Open Image Denoise / PhysX, numpy, mplib, transforms3d, trimesh, torch, warp,
      curobo), Open Image Denoise folders under /opt, sha256 of the simulator-side code (RMBench envs + task configs,
      the frozen memory_s1 simulator code, sim_worker / sim_adapter), the render settings lines of _base_task.py, and
      the FIRST logged step of every listed episode (object poses before the first target, robot joint state).
  compare A.json B.json [C.json ...]
      prints every item that differs, and per task the paired scenes' first-step differences (object position in mm,
      joint state max |diff|). Readings (plan v12 F.1, written before this ran):
        a simulator-side package (sapien, physics, motion planning, numpy) version, its bundled libraries, the
        simulator-side code or a solver / thread setting differs  -> "physics suspect"
        any paired scene with an object position difference > 0.1 mm at the first step -> "scene generation differs"
        floor: >= 40 paired scenes (put 31-50 + swap 1-20 between the A100 and the 5090), else the pose part has no
        reading
Read-only except the JSON it writes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import socket
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

R = Path("/workspace/FastWAM-memory2")
O = R / "outputs/memory_v2"
FW = Path("/workspace/FastWAM")
OUT = Path(os.environ.get("ALIGN_OUT", str(R / "outputs/fullft/align")))
BJ = timezone(timedelta(hours=8))
SIM_PACKAGES = ("sapien", "numpy", "mplib", "transforms3d", "trimesh", "torch", "warp", "curobo", "scipy", "open3d")
SIM_KEYS = ("sapien", "numpy", "mplib", "torch", "warp", "curobo", "sapien_libs")
SIM_PROBE = r"""
import json, os, sys
out = {"python": sys.version.split()[0], "executable": sys.executable}
for name in %r:
    try:
        m = __import__(name)
        out[name] = getattr(m, "__version__", "?")
    except Exception as e:
        out[name] = "not importable: " + type(e).__name__
try:
    import sapien
    from pathlib import Path
    root = Path(sapien.__file__).parent
    out["sapien_libs"] = sorted(p.name for p in root.rglob("*") if ".so" in p.name and any(
        k in p.name.lower() for k in ("oidn", "denoise", "physx", "optix", "vulkan", "sapien")))
except Exception as e:
    out["sapien_libs"] = "unavailable: " + type(e).__name__
print("PROBE " + json.dumps(out))
""" % (SIM_PACKAGES,)


def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception as e:                                                  # noqa: BLE001
        return f"failed: {e!r}"


def sha_tree(paths):
    """sha256 over the sorted (relative path, content) of the files; also per-file digests."""
    h, files = hashlib.sha256(), {}
    for base, pattern in paths:
        base = Path(base)
        if not base.exists():
            files[f"{base}/{pattern}"] = "missing"
            continue
        for p in sorted(base.glob(pattern)):
            if p.is_file():
                d = hashlib.sha256(p.read_bytes()).hexdigest()
                files[str(p.relative_to(base.parent))] = d[:16]
                h.update(str(p.relative_to(base.parent)).encode())
                h.update(d.encode())
    return h.hexdigest()[:16], files


def simulator_python():
    try:
        ident = json.loads((FW / "outputs/s1_dense_joint_h100_v1/IDENTITY.json").read_text())
        py = ident["config"]["closed_loop"]["simulator_python"]
    except Exception:                                                       # noqa: BLE001
        py = ""
    py = os.environ.get("SIM_PY") or py
    if not py or not Path(py).exists():
        py = next((p for p in ("/opt/rmbench-fused-env/bin/python", "/opt/rmbench-a100-env/bin/python",
                               "/opt/rmbench-env/bin/python") if Path(p).exists()), "")
    return py


def first_steps(pairs):
    """{task: {seed: {"objects": {name: [x, y, z, qw, qx, qy, qz]}, "joints": [...], "source": folder}}}."""
    out = {}
    for folder, label in pairs:
        base = Path(folder) if Path(folder).is_absolute() else O / folder
        for f in sorted(base.glob(f"{label}/on/*/seed_*/executed_actions.jsonl")):
            task, seed = f.parent.parent.name, f.parent.name.split("_", 1)[1]
            if not seed.isdigit():                       # seed_<n>_interrupted_<...>: an aborted attempt, not a scene
                continue
            with open(f, encoding="utf-8") as fh:
                line = fh.readline()
            if not line.strip():
                continue
            row = json.loads(line)
            objs = {k: list(v.get("p", [])) + list(v.get("q", [])) for k, v in (row.get("objects_before") or {}).items()
                    if isinstance(v, dict) and "p" in v}
            out.setdefault(task, {})[seed] = {"objects": objs, "joints": row.get("physical_before"),
                                              "source": str(base)}
    return out


def cmd_collect(args):
    import importlib
    info = {"machine": args.machine, "time": f"{datetime.now(BJ):%F %T}", "hostname": socket.gethostname(),
            "platform": platform.platform()}
    info["cpu"] = sh("lscpu | grep -E 'Model name|^CPU\\(s\\)|Thread\\(s\\) per core|Socket\\(s\\)|Flags' | "
                     "sed 's/Flags:.*\\(avx512f\\).*/Flags: has avx512f/; s/Flags:.*/Flags: (no avx512f)/'")
    info["memory"] = sh("grep MemTotal /proc/meminfo")
    info["gpu"] = sh("nvidia-smi --query-gpu=index,name,driver_version --format=csv,noheader")
    info["env"] = {k: os.environ.get(k) for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "CUDA_VISIBLE_DEVICES",
                                                  "VK_ICD_FILENAMES", "NVIDIA_DRIVER_CAPABILITIES", "SIM_PY", "CUROBO",
                                                  "MWAM_OIDN", "MWAM_OIDN_LIB", "LD_PRELOAD")}
    pol = {"python": sys.version.split()[0], "executable": sys.executable}
    for name in ("torch", "numpy"):
        try:
            pol[name] = importlib.import_module(name).__version__
        except Exception as e:                                              # noqa: BLE001
            pol[name] = f"not importable: {type(e).__name__}"
    try:
        import torch
        pol["cuda"], pol["cudnn"] = torch.version.cuda, torch.backends.cudnn.version()
    except Exception:                                                       # noqa: BLE001
        pass
    info["policy_python"] = pol
    py = simulator_python()
    info["simulator_python"] = py
    probe = {}
    if py:
        env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV", "CONDA_PREFIX")}
        try:
            r = subprocess.run([py, "-c", SIM_PROBE], capture_output=True, text=True, timeout=300, env=env,
                               cwd=str(FW / "resources/RMBench") if (FW / "resources/RMBench").exists() else None)
            line = next((l for l in r.stdout.splitlines() if l.startswith("PROBE ")), None)
            probe = json.loads(line[6:]) if line else {"error": (r.stderr or r.stdout)[-600:]}
        except Exception as e:                                              # noqa: BLE001
            probe = {"error": repr(e)}
    info["simulator_packages"] = probe
    info["oidn_under_opt"] = sh("ls -d /opt/oidn* 2>/dev/null") or "none"
    rmb = FW / "resources/RMBench"
    info["code"] = {}
    for name, paths in (("rmbench_envs", [(rmb / "envs", "*.py")]), ("rmbench_task_config", [(rmb / "task_config", "*.yml")]),
                        ("rmbench_robot_config", [(rmb / "envs/robot", "*.py"), (rmb / "assets/embodiments", "*/config.yml")]),
                        ("frozen_sim_code", [(FW / "scripts/memory_s1", "sim_*.py"), (FW / "scripts/memory_s1", "deploy_policy.py")]),
                        ("memwam_sim_code", [(R / "src/fastwam/memory_v2/sim", "*.py")])):
        digest, files = sha_tree(paths)
        info["code"][name] = {"digest": digest, "files": files}
    info["render_lines"] = sh(f"grep -n -E 'set_ray_tracing|set_camera_shader|denoiser|samples_per_pixel|path_depth|"
                              f"timestep|set_timestep|solver|iterations' {rmb}/envs/_base_task.py | head -30")
    pairs = [tuple(x.rsplit(":", 1)) for x in args.episodes]
    if args.search:
        root = Path(args.search) if Path(args.search).is_absolute() else O / args.search
        for label in args.labels:
            for d in sorted(root.glob(f"**/{label}")):
                if d.is_dir() and (d / "on").is_dir() and "/h200/" not in str(d) and "/check_from" not in str(d):
                    pairs.append((str(d.parent), label))
    info["episode_sources"] = [f"{f}:{l}" for f, l in pairs]
    info["first_steps"] = first_steps(pairs)
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"AL0_{args.machine}.json"
    path.write_text(json.dumps(info, indent=1) + "\n", encoding="utf-8")
    n = {t: len(v) for t, v in info["first_steps"].items()}
    print(f"AL0 {args.machine}: simulator python {py}; sapien {probe.get('sapien')}; first steps {n}")
    print(f"AL0 FILE: {path}")


def flat(d, prefix=""):
    out = {}
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(flat(v, key + "."))
        else:
            out[key] = v
    return out


def cmd_compare(args):
    docs = [json.loads(Path(p).read_text()) for p in args.files]
    names = [d["machine"] for d in docs]
    skip = ("time", "first_steps", "episode_sources", "hostname")
    flats = [flat({k: v for k, v in d.items() if k not in skip}) for d in docs]
    keys = sorted(set().union(*flats))
    print(f"AL0 compare: {' | '.join(names)}")
    print("\n## items that differ")
    physics = []
    for k in keys:
        vals = [f.get(k, "(absent)") for f in flats]
        if len({json.dumps(v, sort_keys=True) for v in vals}) > 1:
            print(f"- {k}: " + " | ".join(f"{n}={json.dumps(v)[:160]}" for n, v in zip(names, vals)))
            if k.startswith("simulator_packages.") and any(s in k for s in SIM_KEYS) or k.startswith("code.") \
                    or k.startswith("render_lines") or k.startswith("env.OMP") or k.startswith("env.MKL"):
                physics.append(k)
    print("\n## first logged step of the same scenes (pairwise)")
    scene_diff, paired_total = [], 0
    for i in range(len(docs)):
        for j in range(i + 1, len(docs)):
            a, b = docs[i]["first_steps"], docs[j]["first_steps"]
            for task in sorted(set(a) & set(b)):
                seeds = sorted((x for x in set(a[task]) & set(b[task]) if x.isdigit()), key=int)
                if not seeds:
                    continue
                if i == 0 and j == 1:
                    paired_total += len(seeds)
                worst_pos, worst_joint, over = 0.0, 0.0, []
                for s in seeds:
                    oa, ob = a[task][s]["objects"], b[task][s]["objects"]
                    for name in set(oa) & set(ob):
                        d = max(abs(x - y) for x, y in zip(oa[name][:3], ob[name][:3])) * 1000
                        worst_pos = max(worst_pos, d)
                        if d > 0.1:
                            over.append((s, name, round(d, 3)))
                    ja, jb = a[task][s].get("joints"), b[task][s].get("joints")
                    if ja and jb:
                        worst_joint = max(worst_joint, max(abs(x - y) for x, y in zip(ja, jb)))
                scene_diff += over
                print(f"- {names[i]} vs {names[j]} {task}: paired {len(seeds)}; max object position diff "
                      f"{worst_pos:.4f} mm; max joint diff {worst_joint:.2e}; scenes > 0.1 mm: {len({x[0] for x in over})}"
                      + (f" e.g. {over[:3]}" if over else ""))
    print("\n## readings (plan v12 AL0)")
    print("physics suspect: " + ("YES (" + ", ".join(physics[:12]) + ")" if physics else "no"))
    if paired_total < 40:
        print(f"scene generation: no reading (paired scenes between {names[0]} and {names[1]}: {paired_total} < 40)")
    else:
        print("scene generation: " + ("DIFFERS" if scene_diff else "same (all paired first steps within 0.1 mm)"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("collect")
    c.add_argument("--machine", required=True)
    c.add_argument("--episodes", nargs="*", default=[])
    c.add_argument("--search", default="")
    c.add_argument("--labels", nargs="*", default=[])
    m = sub.add_parser("compare")
    m.add_argument("files", nargs="+")
    args = ap.parse_args()
    {"collect": cmd_collect, "compare": cmd_compare}[args.cmd](args)


if __name__ == "__main__":
    main()

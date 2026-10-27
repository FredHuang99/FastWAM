"""Installation check of a closed-loop host (CPU only; no GPU memory is used).

    CUDA_VISIBLE_DEVICES="" PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/check_install.py

Checks, each printed OK / FAIL:
  1 policy env: python / torch versions
  2 dense identity: the dense delivery authenticates its prepared cache, its code and the repo sources (this is the
    transfer-integrity check after copying from another host)
  3 the A2C e3 checkpoint loads and has memory + action weights
  4 scene banks and the reference smoke run are present
  5 simulator env: sapien / torch / curobo import (subprocess, CPU only)
  6 Vulkan ICD files (rendering)
Exit code 1 if any check FAILs.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
O = REPO / "outputs" / "memory_v2"
failed = []


def report(name, ok, detail=""):
    print(f"{'OK  ' if ok else 'FAIL'} {name}: {detail}", flush=True)
    if not ok:
        failed.append(name)


def main():
    import torch
    report("1 policy env", True, f"python {sys.version.split()[0]}, torch {torch.__version__}, cuda build {torch.version.cuda}")
    try:
        from fastwam.memory_v2 import dense
        from fastwam.memory_v2.train_v2 import load_config
        cfg = load_config(REPO / "configs/memory_v2/train_v2_A.yaml", [])
        spec = dense.DenseSpec.from_dict(cfg.dense)
        common, identity = dense.bind(spec)
        drift = dense.SOFTWARE_DRIFT.get(str(spec.output.resolve()), {})
        report("2 dense identity", True, f"authenticated {spec.output} (software drift: {sorted(drift) or 'none'})")
    except Exception as error:                                  # noqa: BLE001
        report("2 dense identity", False, repr(error)[:600])
    ck = O / "a2C/checkpoints/update_002010.pt"
    try:
        state = torch.load(ck, map_location="cpu", weights_only=False, mmap=True)
        report("3 checkpoint", bool(state.get("memory")) and bool(state.get("action")),
               f"{ck.name}: update {state.get('update')}, memory {len(state['memory'])} / action {len(state['action'] or {})} tensors")
    except Exception as error:                                  # noqa: BLE001
        report("3 checkpoint", False, repr(error)[:300])
    banks = sorted(p.name for p in (O / "closed_loop").glob("scenes_*"))
    smoke = list((O / "closed_loop/smoke_exec8").glob("*/*/*/seed_*/result.json"))
    report("4 scene banks / smoke reference", bool(banks) and bool(smoke), f"{len(banks)} banks {banks}; smoke episodes {len(smoke)}")
    ident = json.loads((Path(cfg.dense["output"]) / "IDENTITY.json").read_text())
    sim_py = (ident["config"].get("closed_loop") or {}).get("simulator_python", "/opt/rmbench-fused-env/bin/python")
    code = ("import sapien, torch; import importlib.util as u; "
            "print('sapien', sapien.__version__, 'torch', torch.__version__, 'cuda build', torch.version.cuda, "
            "'curobo', bool(u.find_spec('curobo')))")
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV")}
    env["CUDA_VISIBLE_DEVICES"] = ""
    root = Path(cfg.dense["root"]) / (ident["config"].get("closed_loop") or {}).get("simulator_root", "resources/RMBench")
    try:
        out = subprocess.run([sim_py, "-c", code], capture_output=True, text=True, timeout=300, env=env, cwd=str(root))
        report("5 simulator env", out.returncode == 0, (out.stdout.strip() or out.stderr.strip()[-400:]) + f"  ({sim_py}, cwd {root})")
    except Exception as error:                                  # noqa: BLE001
        report("5 simulator env", False, repr(error)[:300])
    icd = [str(p) for d in ("/etc/vulkan/icd.d", "/usr/share/vulkan/icd.d") for p in Path(d).glob("*.json")]
    report("6 vulkan ICD", True, f"{icd or 'none (closed_loop.sh render generates one; check the render probe)'}")
    print("INSTALL CHECK " + ("FAILED: " + ", ".join(failed) if failed else "OK"))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

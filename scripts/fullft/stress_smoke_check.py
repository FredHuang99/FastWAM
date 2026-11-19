"""11-19 19:55 (Opus, plan v14 E16 / v15 E16b, E24): smoke check of the new per-task stress triggers (inject.TRIGGERS:
rearrange_blocks after the first release, swap_T after the second, press_button when the first press is confirmed),
run on models that already exist, before any clock model of these tasks has a closed-loop result. Every smoke episode
of <folder>/<label>/on/<task> must show exactly one injection, all k frames shown (visible arm) and the validity fields
logged. Exit 0 = PASS. Usage: stress_smoke_check.py <folder under closed_loop> <label> <task> <k>"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1_verdict import O, episode  # noqa: E402

folder, label, task, k = O / sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
dirs = sorted((folder / label / "on" / task).glob("seed_*"))
if not dirs:
    print("SMOKE: no episode"); sys.exit(1)
ok = True
for d in dirs:
    e = episode(folder, label, task, int(d.name[5:]))
    s = (e or {}).get("stress") or {}
    print(f"SMOKE {task} seed {d.name[5:]}: finished {e is not None}, success {e and e['success']}, injections "
          f"{e and e['injected']}, " + json.dumps({x: s.get(x) for x in ("frame", "k", "arm", "active_arm", "open_frame",
                                                                          "shown", "displacement_m", "counters_changed",
                                                                          "arm_return_rad")}))
    ok &= bool(e) and e["injected"] == 1 and s.get("shown") == s.get("k") == k and "displacement_m" in s
print("SMOKE:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)

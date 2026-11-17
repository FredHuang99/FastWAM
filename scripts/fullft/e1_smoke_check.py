"""Plan v13 E1 smoke check (11-17, Opus): the one smoke episode (ledger model, airgrasp, visible, swap scene 1) must
show exactly one injection with all its frames shown and the validity fields logged; prints the ledger entries the
injected frames produced (the debounce question: an in-place air-grasp may write nothing). Exit 0 = the E1 cards run."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1_verdict import O, episode  # noqa: E402

folder, label, task = O / "e1smoke", "ar2_prop_e30_e1airgrasp_vis", "swap_blocks"
dirs = sorted((folder / label / "on" / task).glob("seed_*"))
if not dirs:
    print("SMOKE: no episode"); sys.exit(1)
seed = int(dirs[0].name[5:])
e = episode(folder, label, task, seed)
s = (e or {}).get("stress") or {}
print(f"SMOKE seed {seed}: finished {e is not None}, success {e and e['success']}, injections {e and e['injected']}")
print(json.dumps({k: s.get(k) for k in ("frame", "inject", "k", "arm", "active_arm", "open_frame", "shown",
                                        "displacement_m", "counters_changed", "arm_return_rad")}))
print(f"ledger entries from the injected frames: {e and e['entries_injected']}")
ok = bool(e) and e["injected"] == 1 and s.get("shown") == s.get("k") == 32 and "displacement_m" in s
print("SMOKE:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)

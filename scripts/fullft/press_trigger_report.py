"""11-20 08:10 (Opus, plan v15 E24; descriptive, read-only): for the press trigger smoke episodes, where the injection
fell relative to the presses: the simulator's press counters (closed_loop_stages.analyse_press) give the executed-
target index of every left / middle press; the injection frame comes from stress.jsonl. The E24 card asks for the pause
BETWEEN two presses with at least one press left; this prints whether the first counted press came before the
injection. Usage: press_trigger_report.py <folder under closed_loop> <label>"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e1_verdict import O  # noqa: E402
import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location("press_gap", Path(__file__).resolve().parent / "press_gap.py")
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)
cls = pg.cls
folder, label = O / sys.argv[1], sys.argv[2]
for d in sorted((folder / label / "on" / "press_button").glob("seed_*")):
    st = [json.loads(x) for x in (d / "stress.jsonl").read_text().splitlines() if x.strip()] if (d / "stress.jsonl").exists() else []
    snaps, counters = cls.read_rows(d / "executed_actions.jsonl")
    r = cls.analyse_press(snaps, counters)
    presses = sorted(r["press_times_1"] + r["press_times_2"])
    inj = int(st[0]["frame"]) if st else None
    before = [t for t in presses if inj is not None and t <= inj]
    print(f"{d.name}: cards {r['card_1']}/{r['card_2']}; injection at frame {inj} (trigger event frame "
          f"{st[0].get('open_frame') if st else None}); press targets {presses[:6]}; presses counted before the "
          f"injection: {len(before)}; executed targets logged {len(counters)}")

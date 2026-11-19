"""Plan v13 E9 (event-indexed images, ar2_arev) and plan v15 E25 (time-indexed images, ar2_tw) verdicts, and the image-
column comparison of the G3 gate (scripts/fullft/G3_GATE_REGISTERED.txt). Readings registered by Fable (plan v13
section 3 E9, 11-17; plan v15 section 3 E25 and the E9 joint table, 11-19 noon) and the user (G3 addition, 11-19 13:45);
this script written 11-19 19:50 BJ, before either model exists (E9 trains on the old H200, E25 on the new H200). A40.
Cells (closed_loop/e9): no stress swap / put 1-100, labels ar2_arev_e30 / ar2_tw_e30; pause 64 and 256 frames visible /
hidden swap 1-50, labels <model>_p64_vis ... (E1's injection point and validity); E9 descriptive: event frames off
(MWAM_EVFRAMES=off), swap 1-50, label ar2_arev_e30_evoff.
  E9 (registered): swap >= 95/100 -> INDEX SUFFICES; <= 75/100 -> BODY CONTENT MATTERS; otherwise PARTIAL;
    floor put >= 90/100. Joint reading (plan v15): BODY CONTENT MATTERS -> the 2x2 differs in the content column;
    INDEX SUFFICES -> a history covering the episode suffices, body state is the cheapest content, E25 decides the
    index for images; PARTIAL -> report e10, e20 too.
  E25 (registered): swap >= 95/100 -> LONG VISUAL SUFFICES; <= 75/100 -> NOT ENOUGH; otherwise PARTIAL; floor put
    >= 90/100. Stress (floors: valid pairs >= 45, hidden >= 35/50): some level Delta <= -8/50 with p < 0.05 ->
    CLOCK READ WITH IMAGES; both levels Delta >= -5/50 -> NOT READ; otherwise UNDECIDED. With E22a (the body-state
    clock at the same level, E22A_VERDICT.json): images hurt where the clock is not -> CONTENT DECIDES; both hurt at
    256 -> the index decides; neither -> no clock reading on swap.
  G3 image column (per level): E25 Delta <= -8/50 with p < 0.05 AND E9 Delta >= -5/50 -> EVENT INDEX BETTER (IMAGES);
    both >= -5/50 -> does not count; otherwise undecided. Floors as E25's.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/e9e25_verdict.py      Writes outputs/fullft/E9E25_VERDICT.json.
"""
from __future__ import annotations

import json

import v15_common as vc  # noqa: E402

E9, E25 = "ar2_arev_e30", "ar2_tw_e30"


def no_stress(label):
    folder = vc.O / "e9"
    sw = vc.results(folder, label, "swap_blocks", vc.seeds("swap_blocks", 100))
    pu = vc.results(folder, label, "put_back_block", vc.seeds("put_back_block", 100))
    return {"swap": sum(sw.values()), "swap_finished": len(sw), "put": sum(pu.values()), "put_finished": len(pu)}


def word(ns, hi, lo, names):
    if ns["swap_finished"] < 95 or ns["put_finished"] < 95:
        return "WAIT"
    if ns["put"] < 90:
        return f"NO VERDICT (floor: put {ns['put']}/100 < 90)"
    return names[0] if ns["swap"] >= hi else names[1] if ns["swap"] <= lo else "PARTIAL"


def main():
    s50 = vc.seeds("swap_blocks", 50)
    folder = vc.O / "e9"
    out = {}
    n9, n25 = no_stress(E9), no_stress(E25)
    out["E9"] = {"no_stress": n9, "verdict": word(n9, 95, 75, ("INDEX SUFFICES", "BODY CONTENT MATTERS"))}
    out["E25"] = {"no_stress": n25, "verdict": word(n25, 95, 75, ("LONG VISUAL SUFFICES", "NOT ENOUGH"))}
    off = vc.results(folder, f"{E9}_evoff", "swap_blocks", s50)
    out["E9"]["event_frames_off_swap_1_50"] = f"{sum(off.values())}/{len(off)} (descriptive)"
    cells = {}
    for m in (E9, E25):
        for L in (64, 256):
            cells[f"{m}_p{L}"] = vc.stress_cell(folder, f"{m}_p{L}_vis", f"{m}_p{L}_hid", "swap_blocks", s50, 35)
    out["cells"] = cells
    st = [cells[f"{E25}_p{L}"]["state"] for L in (64, 256)]
    if "WAIT" in st:
        out["E25"]["stress"] = "WAIT"
    elif "HURT" in st:
        out["E25"]["stress"] = "CLOCK READ WITH IMAGES"
    elif all(s == "NOT HURT" for s in st):
        out["E25"]["stress"] = "NOT READ"
    else:
        out["E25"]["stress"] = "UNDECIDED"
    e22 = vc.F / "E22A_VERDICT.json"
    if e22.exists():
        clk = {c["level"]: c["state"] for c in json.loads(e22.read_text())["swap_blocks"]["clock"]}
        img = {L: cells[f"{E25}_p{L}"]["state"] for L in (64, 256)}
        if any(img[L] == "HURT" and clk.get(L) == "NOT HURT" for L in (64, 256)):
            joint = "CONTENT DECIDES"
        elif img[256] == "HURT" and clk.get(256) == "HURT":
            joint = "THE INDEX DECIDES"
        elif all(img[L] == "NOT HURT" for L in (64, 256)) and all(clk.get(L) == "NOT HURT" for L in (64, 256)):
            joint = "NO CLOCK READING ON SWAP"
        else:
            joint = "WAIT / MIXED"
        out["E25"]["with_E22a"] = {"images": img, "body_clock": clk, "reading": joint}
    g3 = {}
    for L in (64, 256):
        a, b = cells[f"{E25}_p{L}"], cells[f"{E9}_p{L}"]
        if "WAIT" in (a["state"], b["state"]):
            g3[L] = "WAIT"
        elif "FLOOR NOT MET" in (a["state"], b["state"]):
            g3[L] = "NO READING (floor)"
        elif a["state"] == "HURT" and b["delta"] >= -5:
            g3[L] = "EVENT INDEX BETTER (IMAGES)"
        elif a["delta"] >= -5 and b["delta"] >= -5:
            g3[L] = "DOES NOT COUNT"
        else:
            g3[L] = "UNDECIDED"
    out["G3_image_column"] = g3
    print(f"E9: {out['E9']}\nE25: {out['E25']}\nG3 image column: {g3}")
    vc.write("E9E25_VERDICT.json", out)


if __name__ == "__main__":
    main()

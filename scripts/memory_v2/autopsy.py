"""Autopsy of one queue5 task: why did it pass / fail, and which pre-registered explanations do the records support.

    /opt/mwam/bin/python scripts/memory_v2/autopsy.py --id X1-exec8            -> outputs/memory_v2/autopsy/AUTOPSY_X1-exec8.md
    /opt/mwam/bin/python scripts/memory_v2/autopsy.py --id X1-exec8 --no-phase  (skip the expert-bank match; no dense cache)

Six fixed sections (week plan v3 5.2):
  1 result vs threshold           verdict, pass_if / inconclusive_if evaluated, headline counts vs the reference
  2 training health               loss first/last, guard, offline on/off/null curve, PR, pattern table (lr / action
                                  pathway / memory unused), for the trained run or the run behind the checkpoint
  3 closed-loop funnel            stage reach per condition, first failed stage, paired counts vs reference / null
  4 failure classes (automatic)   simulator error / never lifted / same block again (swap) / unseen state / phase
                                  regression / idling >= 48 targets / empty-air close, two example seeds each
  5 explanations                  the task's failure_explanations, each condition evaluated on the records
  6 next step                     the task's pre-registered on_pass / on_fail
The class counts are also written to the task state (metrics.classes) so later tasks / the weekly report can use them.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


q5 = load("queue5", REPO / "scripts/memory_v2/queue5.py")
cls = load("closed_loop_stages", REPO / "scripts/memory_v2/closed_loop_stages.py")

ORDER = {"put_back_block": ("lifted", "centre", "pressed", "stage1", "regrasp", "returned", "success"),
         "swap_blocks": ("lifted", "s1", "s2", "s3", "pressed", "success")}
PRIORITY = ("sim_error", "never_lifted", "same_block_again", "unseen_state", "phase_regression", "idle", "empty_air_close")
CLASS_TEXT = {
    "sim_error": "simulator / worker error (ERROR.json, no result)",
    "never_lifted": "block never lifted >= 5 cm (grasp failure)",
    "same_block_again": "swap: after S1 the same block was moved again (memory decision wrong / phase forgotten)",
    "unseen_state": ">= 50% of post-press targets farther from every expert target than the val q99 (off-distribution)",
    "phase_regression": "post-press targets match expert phases P0-P3 more than P4/P5 (went back in the task)",
    "idle": "a stretch of >= 48 targets with no arm motion (> 0.01 rad) and no gripper change",
    "empty_air_close": "a gripper closed in the air (> 8 cm from every block, no contact)",
}


def fmt(v, nd=4):
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def run_of_checkpoint(path):
    p = Path(str(path))
    return p.parents[1].name if p.parent.name == "checkpoints" else None


# ============================================================================ per-episode classification
def rows_of(d):
    return [json.loads(l) for l in (d / "executed_actions.jsonl").read_text().splitlines() if l.strip()]


def right_ee_min_after_press(rows, press_t):
    if press_t is None:
        return None
    best = None
    for r in rows[press_t:]:
        ee = ((r.get("joint_details") or {}).get("right") or {}).get("ee_pose")
        b = (r.get("objects_after") or {}).get("block")
        if ee and b:
            d = math.dist(ee["p"][:3], b["p"][:3])
            best = d if best is None else min(best, d)
    return best


def classify(task, a, rows, bank):
    tags = []
    if not a.get("lifted"):
        tags.append("never_lifted")
    if task == "swap_blocks" and a.get("second_move") == "same block again":
        tags.append("same_block_again")
    info = {}
    if bank is not None and task == "put_back_block" and a.get("pressed"):
        e = bank.episode(rows)
        after = e["after"]
        if after["n"]:
            info["after_press_median_dist"] = float(np.median(after["dist"]))
            info["after_press_far_frac"] = after["far"] / after["n"]
            early = sum(p < 4 for p in after["phase_ids"] if p >= 0)
            late = sum(p >= 4 for p in after["phase_ids"])
            info["after_press_early_phase_frac"] = early / after["n"]
            if info["after_press_far_frac"] >= 0.5:
                tags.append("unseen_state")
            if early > late:
                tags.append("phase_regression")
    targets = np.asarray([r["target"] for r in rows if r.get("target") is not None], dtype=np.float64)
    if len(targets) >= 48:
        from fastwam.memory_v2.motion import still_runs
        runs = still_runs(targets, arm_eps=0.01, gripper_eps=0.05, min_length=48)
        if runs:
            longest = max(runs, key=lambda x: x["length"])
            info["longest_idle"] = longest
            tags.append("idle")
    closes = cls.gripper_closes_rows(rows, task)
    info["empty_air_closes"] = sum(c["kind"] == "empty-air" for c in closes)
    if info["empty_air_closes"]:
        tags.append("empty_air_close")
    if task == "put_back_block":
        info["right_ee_block_min_after_press_m"] = right_ee_min_after_press(rows, a.get("press_t"))
    return tags, info


def first_failed(task, a):
    for k in ORDER[task]:
        if not a.get(k):
            return k
    return None


# ============================================================================ sections
def section_result(task, s):
    m, r = s.get("metrics", {}) or {}, s.get("reference", {}) or {}
    out = ["## 1. Result vs threshold", "",
           f"- verdict: **{s.get('verdict')}**  (rc {s.get('rc')}, interrupted {s.get('interrupted')}, {s.get('start')} -> {s.get('end')})",
           f"- hypothesis: {task.get('hypothesis', '-')}",
           f"- pass_if: `{task.get('pass_if')}`"]
    for key in ("pass_if", "inconclusive_if"):
        expr = task.get(key)
        if expr:
            try:
                out.append(f"  - `{key}` on the records -> {q5.evaluate_expr(expr, m, r)}")
            except Exception as error:             # noqa: BLE001
                out.append(f"  - `{key}` could not be evaluated: {error!r}")
    if m.get("pass_if_error") or m.get("metrics_error"):
        out.append(f"- metric error: {m.get('pass_if_error') or m.get('metrics_error')}")
    cells = [(k, v) for k, v in m.items() if "/" in k and isinstance(v, dict) and "n" in v]
    if cells:
        out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                "|---|---|" + "---|" * len(ORDER[cells[0][0].split('/')[0]]) + "---|---|---|"]
        for k, v in sorted(cells):
            stages = ORDER[k.split("/")[0]]
            ref = r.get(k)
            refs = (" ".join(f"{st}={ref.get(st, 0)}" for st in stages) + f" prog={ref.get('progress_mean', 0):.3f} (n={ref['n']})"
                    if ref else "-")
            dec = f"{v.get('correct', 0)}/{v.get('decided', 0)}"
            if v.get("pressed_given_centre") is not None:
                dec += f"; P(press|centre) {v['pressed_given_centre']:.2f} ({v.get('pressed_after_centre', 0)}/{v.get('centred', 0)})"
            out.append(f"| {k} | {v['n']} | " + " | ".join(str(v.get(st, 0)) for st in stages)
                       + f" | {v.get('progress_mean', 0):.3f} | {dec} | {refs} |")
        prog = []
        for t, c in (m.get("prog_on_vs_null") or {}).items():
            prog.append(f"- **{t} progress on - null: {c['delta']:+.3f} (95% CI {c['ci']}), sign-flip p = {c['p']:.4f}, "
                        f"n = {c['n']} paired scenes** (on {c['mean_a']:.3f} / null {c['mean_b']:.3f})")
        for mode, cs in (m.get("prog_vs_reference") or {}).items():
            for t, c in cs.items():
                prog.append(f"- {t}/{mode} progress this - reference: {c['delta']:+.3f} (95% CI {c['ci']}), p = {c['p']:.4f}, "
                            f"n = {c['n']} (this {c['mean_a']:.3f} / reference {c['mean_b']:.3f})")
        for t, c in (r.get("prog_on_vs_null") or {}).items():
            prog.append(f"- reference {t} progress on - null: {c['delta']:+.3f} (95% CI {c['ci']}), p = {c['p']:.4f}, n = {c['n']}")
        if prog:
            out += [""] + prog
    if m.get("errors"):
        out.append(f"\n- episodes with ERROR.json and no result: {m['errors']}")
    if task["kind"] == "closed_loop":
        extra = [f"decision gaps {m.get('decision_gaps')}", f"policy {m.get('policy_seconds_mean')} s / decision"]
        if m.get("candidates_logged"):
            extra.append(f"{m['candidates_logged']} candidates, non-first chosen in {m.get('choice_nonzero_frac')} of decisions")
        if m.get("parity_decisions") is not None:
            extra.append(f"parity vs reference run: {m['parity_decisions']} decisions, first max |diff| "
                         f"{m.get('parity_first_max_abs')}, max |diff| {m.get('parity_max_abs')}, reference policy "
                         f"{m.get('policy_seconds_ref')} s / decision")
        out.append("- " + "; ".join(extra))
    if task["kind"] in ("train", "eval"):
        out.append(f"- headline: {q5.headline(task, m)}")
    return out


def section_training(task, s):
    out = ["", "## 2. Training health", ""]
    run = task.get("run") or (run_of_checkpoint(task["checkpoint"]) if task.get("checkpoint") else None)
    if not run:
        return out + ["n/a"]
    m = q5.train_metrics(run)
    pr = q5.pr_metrics(run)
    note = "" if task.get("run") else " (the run behind the evaluated checkpoint)"
    out.append(f"run `{run}`{note}: updates {m.get('updates')}, complete {m.get('complete')}, guard {m.get('guard')}, "
               f"{fmt(m.get('seconds_per_update'), 1)} s/update")
    out.append(f"- FM loss median of the first / last 30 updates: {fmt(m.get('fm_first'))} -> {fmt(m.get('fm_last'))} "
               f"(x{fmt(m.get('fm_ratio'), 2)})")
    curve = m.get("eval_curve") or []
    if curve:
        out += ["", "| update | on | off | null |", "|---|---|---|---|"]
        out += [f"| {c['update']} | {fmt(c.get('on'))} | {fmt(c.get('off'))} | {fmt(c.get('null'))} |" for c in curve]
    if pr:
        out.append("- PR (val, 300 pairs): " + "  ".join(f"{k} {fmt(v, 3)}" for k, v in sorted(pr.items())))
    flags = []
    if not m.get("updates"):
        flags.append(f"no training records ({q5.O / run / 'metrics.jsonl'} missing or empty)")
    if m.get("fm_ratio") and m["fm_ratio"] > 1.0:
        flags.append("FM loss ROSE over training -> learning rate / instability (probe: 3e-5 rose x1.19-1.44)")
    if len(curve) >= 2:
        c0, c1 = curve[0], curve[-1]
        if c0.get("off") and c1.get("off") and c1["off"] >= 0.97 * c0["off"]:
            flags.append("offline OFF error did not fall -> the action pathway did not learn")
        if c1.get("on") and c1.get("null") and c1["on"] >= 0.95 * c1["null"]:
            flags.append("offline ON not better than NULL -> the memory is not used")
        if c0.get("on") and c1.get("on") and c1["on"] > 1.10 * c0["on"]:
            flags.append("offline ON error rose > 10% -> over-fitting / drift")
    if m.get("guard"):
        flags.append(f"guard tripped: {m['guard']}")
    diff = q5.config_diff(run, task["reference_run"]) if task.get("reference_run") else None
    if diff is not None:
        keys = [k for k in diff if k not in ("name", "output")]
        out.append(f"- config vs `{task['reference_run']}`: " + (", ".join(f"{k}: {diff[k][0]} (ref {diff[k][1]})"
                                                                     for k in keys) or "identical"))
    log = q5.O / run / "stdout.log"
    if log.exists():
        lines = log.read_text(errors="replace").splitlines()[-400:]
        errs = [l for l in lines if re.search(r"Traceback|Error|out of memory|Killed", l) and "WARNING" not in l]
        if errs:
            flags.append(f"stdout errors (last): {errs[-1][:200]}")
    out += ["", "pattern check: " + ("; ".join(flags) if flags else "no anomaly (loss fell, off fell, on < null)")]
    return out


def section_closed_loop(task, s, use_phase):
    m, r = s.get("metrics", {}) or {}, s.get("reference", {}) or {}
    folders = task.get("folders") or [task.get("output")]
    eps = q5.episodes(folders, task["label"], task.get("modes"), task.get("tasks"))
    out = ["", "## 3. Closed-loop funnel", ""]
    first = defaultdict(Counter)
    for (t, mode, seed), a in eps.items():
        first[f"{t}/{mode}"][first_failed(t, a) or "(succeeded)"] += 1
    for cell, c in sorted(first.items()):
        out.append(f"- {cell}: first failed stage {dict(c)}")
    for name, key in (("memory on vs null (only on / only null)", "on_vs_null"), ):
        for t, cell in (m.get(key) or {}).items():
            out.append(f"- {t} {name}: " + "  ".join(f"{k} {v[0]}/{v[1]} (p={q5.sign_p(v[0], v[1]):.3f})"
                                                     for k, v in cell.items()) + f"  n={next(iter(cell.values()))[2]}")
    for mode, cells in (m.get("vs_reference") or {}).items():
        for t, cell in cells.items():
            out.append(f"- {t}/{mode} vs reference (only this / only reference): "
                       + "  ".join(f"{k} {v[0]}/{v[1]} (p={q5.sign_p(v[0], v[1]):.3f})" for k, v in cell.items())
                       + f"  n={next(iter(cell.values()))[2]}")
    # ------------------------------------------------------------------------ section 4
    out += ["", "## 4. Failure classes (automatic, failed episodes only)", ""]
    bank, bank_note = None, ""
    if use_phase and any(t == "put_back_block" and a.get("pressed") and not a.get("success") for (t, _, _), a in eps.items()):
        try:
            sys.path.insert(0, str(REPO / "scripts/memory_v2"))
            bank = load("phase_match", REPO / "scripts/memory_v2/phase_match.py").ExpertBank("put_back_block")
            bank_note = (f"expert bank: {bank.n_train} train demos, val distance q50 {bank.q50:.3f} q99 {bank.q99:.3f} "
                         "(rad, grippers x0.5)")
        except Exception as error:                 # noqa: BLE001
            bank_note = f"phase match unavailable ({error!r}): unseen_state / phase_regression not classified"
    if bank_note:
        out.append(f"- {bank_note}")
    counts, examples, infos = defaultdict(Counter), defaultdict(list), defaultdict(list)
    for (t, mode, seed), a in sorted(eps.items()):
        if a.get("success"):
            continue
        cell = f"{t}/{mode}"
        rows = rows_of(Path(a["dir"]))
        tags, info = classify(t, a, rows, bank)
        infos[cell].append(info)
        counts[cell]["failed"] += 1
        for tag in tags:
            counts[cell][tag] += 1
        primary = next((p for p in PRIORITY if p in tags), "other")
        counts[cell][f"primary:{primary}"] += 1
        for tag in tags:
            if len(examples[(cell, tag)]) < 2:
                examples[(cell, tag)].append((seed, a, info))
    for t, mode, seed, e in q5.error_dirs(folders, task["label"], task.get("modes"), task.get("tasks")):
        cell = f"{t}/{mode}"
        counts[cell]["sim_error"] += 1
        counts[cell]["failed"] += 1
        counts[cell]["primary:sim_error"] += 1
        if len(examples[(cell, "sim_error")]) < 2:
            err = str((q5.read_json(e, {}) or {}).get("error", ""))[-300:]
            examples[(cell, "sim_error")].append((seed, {"error": err}, {}))
    if not counts:
        out.append("no failed episodes")
    for cell, c in sorted(counts.items()):
        out.append(f"\n**{cell}**: {c['failed']} failed episodes")
        out += ["", "| class | episodes | primary | meaning |", "|---|---|---|---|"]
        for tag in PRIORITY:
            if c[tag]:
                out.append(f"| {tag} | {c[tag]} | {c[f'primary:{tag}']} | {CLASS_TEXT[tag]} |")
        if c["primary:other"]:
            out.append(f"| other | - | {c['primary:other']} | none of the classes (failed at a later stage cleanly) |")
        vals = infos[cell]
        d = [v["after_press_median_dist"] for v in vals if v.get("after_press_median_dist") is not None]
        ee = [v["right_ee_block_min_after_press_m"] for v in vals if v.get("right_ee_block_min_after_press_m") is not None]
        if d:
            out.append(f"\n- post-press distance to the nearest expert target: median over episodes {statistics.median(d):.3f} "
                       f"(baseline A2C e3 1.18; in-distribution q50 {bank.q50 if bank else float('nan'):.3f})")
        if ee:
            out.append(f"- closest right end-effector to the block after the press: median {statistics.median(ee):.3f} m "
                       f"(< 0.03 m = the hand reached the block)")
        air = [v.get("empty_air_closes", 0) for v in vals]
        if air:
            out.append(f"- empty-air closes per failed episode: mean {sum(air) / len(air):.2f}")
        for tag in PRIORITY:
            for seed, a, info in examples.get((cell, tag), []):
                desc = (a.get("error") or f"furthest={a.get('furthest')} events={a.get('events', [])[:6]}")
                extra = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in info.items() if v is not None}
                out.append(f"- example {tag}: seed {seed}: {desc}  {extra}")
                if a.get("dir") and tag in ("unseen_state", "phase_regression", "idle"):
                    start = (a.get("press_t") or 1) if tag != "idle" else (info.get("longest_idle", {}).get("start", 0) + 1)
                    lines = cls.trace_episode(Path(a["dir"]) / "executed_actions.jsonl", cell.split("/")[0], start, 24)[:6]
                    out += ["  ```"] + [f"  {l}" for l in lines] + ["  ```"]
    return out, {cell: dict(c) for cell, c in counts.items()}


def section_explanations(task, s, classes):
    m, r = s.get("metrics", {}) or {}, s.get("reference", {}) or {}
    out = ["", "## 5. Explanations: supported / not supported by the records", ""]
    items = task.get("failure_explanations") or []
    if not items:
        return out + ["(none pre-registered)"]
    env_c = defaultdict(Counter, {k: Counter(v) for k, v in classes.items()})
    for item in items:
        expr, text = item.get("if"), item.get("then", "")
        try:
            hit = q5.evaluate_expr(expr, m, r, c=env_c)
            mark = "SUPPORTED" if hit else "not supported"
        except Exception as error:                 # noqa: BLE001
            mark = f"not evaluable ({error!r})"
        out.append(f"- [{mark}] `{expr}` -> {text}")
    return out


def section_next(task, s):
    v = s.get("verdict")
    pick = task.get("on_pass") if v == "PASS" else task.get("on_fail") if v == "FAIL" else task.get("on_inconclusive")
    out = ["", "## 6. Next step (pre-registered)", ""]
    out.append(f"- verdict {v}: {pick or '(nothing pre-registered for this verdict: decide at the next decision point)'}")
    if v in ("ERROR", "INCONCLUSIVE"):
        out.append(f"- task log: {q5.Q / 'tasks' / (task['id'] + '.log')} (last lines below)")
        log = q5.Q / "tasks" / f"{task['id']}.log"
        if log.exists():
            out += ["  ```"] + [f"  {l[:200]}" for l in log.read_text(errors="replace").splitlines()[-12:]] + ["  ```"]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--id", required=True)
    ap.add_argument("--no-phase", action="store_true", help="skip the expert-bank match (needs the dense cache)")
    args = ap.parse_args()
    tasks = {t["id"]: t for t in q5.load_tasks()}
    task = q5.effective(tasks[args.id])
    s = q5.state(args.id)
    lines = [f"# AUTOPSY {args.id} - {s.get('verdict', s.get('status'))}",
             f"generated {datetime.now(q5.BJ):%Y-%m-%d %H:%M} Beijing; kind {task['kind']}; lane {task.get('lane')}", ""]
    lines += section_result(task, s)
    lines += section_training(task, s)
    classes = {}
    if task["kind"] in ("closed_loop", "analysis"):
        more, classes = section_closed_loop(task, s, not args.no_phase)
        lines += more
    else:
        lines += ["", "## 3. Closed-loop funnel", "", "n/a", "", "## 4. Failure classes", "", "n/a"]
    lines += section_explanations(task, s, classes)
    lines += section_next(task, s)
    q5.AUTOPSY.mkdir(parents=True, exist_ok=True)
    path = q5.AUTOPSY / f"AUTOPSY_{args.id}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if classes:
        st = q5.state(args.id)
        st.setdefault("metrics", {})["classes"] = classes
        q5.write_json(q5.Q / "state" / f"{args.id}.json", st)
    print(f"[autopsy] {path}")


if __name__ == "__main__":
    main()

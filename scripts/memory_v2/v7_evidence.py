"""Evidence for plan v7 from files that already exist (CPU, read only; nothing is trained or evaluated).

1. Where along the noise level does memory act?  probes.jsonl of every training run holds, every 25 updates,
   history_sensitivity: the relative L2 change of the velocity when the history is replaced (null = masked,
   shuffle_time, swap = another sample's history) at tau in {0.3, 0.6, 0.8, 0.9, 0.95, 1.0}, and the learned
   tau-gate g_l(tau) of each injected layer. Reported: the last probe of each run, plus the objective it was
   trained with (tau_mode / weight_mode / endpoint), so runs trained WITHOUT the high-noise objective
   (v2_A_bfull*, the released bell weighting) are the control for "memory acts at high noise only because we
   trained it there".
2. Offline FM error per tau, memory on vs null (the last eval/update_*.json of each run).
3. Which injected layers carry the memory: g_l(tau) per layer at tau = 1.0 / 0.9 / 0.5 / 0.1.
4. How much of a closed-loop episode is policy time: result.json policy_seconds_mean x decisions / wall_seconds,
   per (label, mode, task), over every finished episode under closed_loop/ (decides what step distillation buys).

    PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/v7_evidence.py [--runs a2C_6ep v2_A_bfull ...]
Writes outputs/memory_v2/report/V7_EVIDENCE_<time>.md (+ .json).
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path

O = Path(os.environ.get("MEMV2_OUT", "/workspace/FastWAM-memory2/outputs/memory_v2"))
BJ = timezone(timedelta(hours=8))
RUNS = ["v2_A_bfull", "v2_A_bfull_s19", "v2_A_memory_only", "v2_A_cf", "v2_A_cf_s19", "a2C", "a2C_6ep",
        "a2C_onestage_6ep", "a2C_nopairs_ours", "a2B0_6ep", "v2_press_cf", "v2_press_cf_lm8", "v2_press_cf_mix",
        "press_6ep", "press_6ep_lm8", "press_6ep_mix"]
GATE_TAUS = (1.0, 0.9, 0.5, 0.1)


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def last_jsonl(path):
    last = first = None
    try:
        with Path(path).open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                first = row if first is None else first
                last = row
    except OSError:
        pass
    return first, last


def fmt(v, digits=3):
    return "-" if v is None else (f"{v:.{digits}f}" if isinstance(v, (int, float)) else str(v))


def at_tau(profile, tau):
    """Value of a {'tau': [...], key: [...]} profile at the tau closest to `tau`."""
    taus = profile.get("tau") or []
    if not taus:
        return None
    j = min(range(len(taus)), key=lambda i: abs(taus[i] - tau))
    return j


def run_section(runs):
    rows, gates, fm = [], [], []
    for run in runs:
        d = O / run
        if not d.exists():
            continue
        cfg = (read_json(d / "CONFIG.json", {}) or {}).get("config", {})
        obj = (cfg.get("memory_v2") or {}).get("objective", {})
        hist = (cfg.get("memory_v2") or {}).get("history", {})
        objective = (f"{obj.get('tau_mode', '?')}/{obj.get('weight_mode', '?')}"
                     f"{'+endpoint' if obj.get('endpoint_weight') else ''} drop={obj.get('memory_dropout', '?')}")
        first, last = last_jsonl(d / "probes.jsonl")
        sens = (last or {}).get("sensitivity") or {}
        taus = sens.get("tau") or []
        row = {"run": run, "objective": objective, "landmark_stride": hist.get("landmark_stride"),
               "strides": hist.get("landmark_strides"), "update": (last or {}).get("update"), "tau": taus}
        for variant in ("null", "shuffle_time", "swap", "swap_content"):
            if variant in sens:
                row[variant] = sens[variant]
        rows.append(row)
        gate = (last or {}).get("gate") or {}
        if gate.get("tau"):
            g = {"run": run, "layers": {}}
            for layer, values in gate.items():
                if layer == "tau":
                    continue
                g["layers"][layer] = {t: values[at_tau(gate, t)] for t in GATE_TAUS}
            gates.append(g)
        evals = sorted((d / "eval").glob("update_*.json"))
        if evals:
            overall = (read_json(evals[-1], {}) or {}).get("overall", {})
            cell = {"run": run, "eval": evals[-1].name}
            for k, v in overall.items():
                if "/fm_tau" in k and k.split("/")[0] in ("on", "null", "off"):
                    cell[k] = v
            fm.append(cell)
    return rows, gates, fm


def latency_section():
    groups = {}
    for res in (O / "closed_loop").glob("**/seed_*/result.json"):
        r = read_json(res, {}) or {}
        if not r.get("wall_seconds") or r.get("policy_seconds_mean") is None:
            continue
        key = (r.get("label"), r.get("mode"), r.get("task"))
        g = groups.setdefault(key, {"n": 0, "policy_s": [], "decisions": [], "wall_s": [], "sim_s": [], "steps": set()})
        g["n"] += 1
        g["policy_s"].append(float(r["policy_seconds_mean"]))
        g["decisions"].append(int(r.get("decisions") or 0))
        g["wall_s"].append(float(r["wall_seconds"]))
        if r.get("simulator_seconds") is not None:
            g["sim_s"].append(float(r["simulator_seconds"]))
        g["steps"].add(r.get("steps"))
    out = []
    for (label, mode, task), g in sorted(groups.items(), key=lambda kv: (-kv[1]["n"], str(kv[0]))):
        share = [p * d / w for p, d, w in zip(g["policy_s"], g["decisions"], g["wall_s"]) if w > 0]
        out.append({"label": label, "mode": mode, "task": task, "n": g["n"],
                    "policy_seconds_per_decision": statistics.median(g["policy_s"]),
                    "decisions": statistics.median(g["decisions"]), "wall_minutes": statistics.median(g["wall_s"]) / 60,
                    "policy_share": statistics.median(share) if share else None,
                    "steps": sorted(str(s) for s in g["steps"])})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", nargs="*", default=RUNS)
    args = ap.parse_args()
    rows, gates, fm = run_section(args.runs)
    lat = latency_section()
    now = datetime.now(BJ)
    lines = [f"# V7 evidence ({now:%F %T}; read-only, from existing probes / evals / episodes)", "",
             "## 1. Memory effect along the noise level: relative change of the velocity when the history is replaced",
             "(last probe of each run; tau = 1 is pure noise; larger = the velocity depends more on the history)", ""]
    taus = sorted({t for r in rows for t in r["tau"]})
    if rows:
        lines += ["| run | objective | stride | update | variant | " + " | ".join(f"tau {t:g}" for t in taus) + " |",
                  "|---|---|---|---|---|" + "---|" * len(taus)]
        for r in rows:
            for variant in ("null", "shuffle_time", "swap"):
                if variant not in r:
                    continue
                vals = dict(zip(r["tau"], r[variant]))
                lines.append(f"| {r['run']} | {r['objective']} | {r['landmark_stride']}{'/mix' if r['strides'] else ''} | "
                             f"{r['update']} | {variant} | " + " | ".join(fmt(vals.get(t)) for t in taus) + " |")
    else:
        lines.append("(no probes.jsonl found)")
    lines += ["", "## 2. Offline FM error per tau (last in-training eval): memory on vs null", ""]
    fm_keys = sorted({k for c in fm for k in c if "/fm_tau" in k}, key=lambda k: (k.split("/")[0], float(k.split("tau")[1])))
    if fm:
        lines += ["| run | eval | " + " | ".join(fm_keys) + " |", "|---|---|" + "---|" * len(fm_keys)]
        for c in fm:
            lines.append(f"| {c['run']} | {c['eval']} | " + " | ".join(fmt(c.get(k), 4) for k in fm_keys) + " |")
    lines += ["", "## 3. Learned tau-gate g_l(tau) per injected layer (last probe)", ""]
    for g in gates:
        layers = sorted(g["layers"], key=lambda x: int(x))
        lines += [f"**{g['run']}**", "", "| tau | " + " | ".join(f"layer {l}" for l in layers) + " |",
                  "|---|" + "---|" * len(layers)]
        for t in GATE_TAUS:
            lines.append(f"| {t:g} | " + " | ".join(fmt(g["layers"][l][t]) for l in layers) + " |")
        lines.append("")
    lines += ["## 4. Closed-loop time: policy share of an episode", "",
              "| label | mode | task | n | policy s / decision | decisions | wall min | policy share | steps |",
              "|---|---|---|---|---|---|---|---|---|"]
    for c in lat[:40]:
        lines.append(f"| {c['label']} | {c['mode']} | {c['task']} | {c['n']} | {fmt(c['policy_seconds_per_decision'], 2)} | "
                     f"{fmt(c['decisions'], 0)} | {fmt(c['wall_minutes'], 1)} | {fmt(c['policy_share'], 2)} | {','.join(c['steps'])} |")
    rep = O / "report" / f"V7_EVIDENCE_{now:%Y%m%d_%H%M}.md"
    rep.parent.mkdir(parents=True, exist_ok=True)
    rep.write_text("\n".join(lines) + "\n", encoding="utf-8")
    rep.with_suffix(".json").write_text(json.dumps({"sensitivity": rows, "gates": gates, "fm": fm, "latency": lat},
                                                   indent=1, default=str), encoding="utf-8")
    print("\n".join(lines))
    print(f"\nV7_EVIDENCE: {rep}")
    return 0 if (rows or lat) else 1


if __name__ == "__main__":
    raise SystemExit(main())

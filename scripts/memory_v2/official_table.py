"""Official-protocol table (week plan v5 C): rows X7 / A2C / B0-6ep x {put_back, swap} at execute 8, the 100 official
seed-42 scenes, pooled over shards and machines, and the pre-registered tests (v5 C.2):

    O-swap / O-put   X7 on - null, paired progress (exact sign-flip permutation, two-sided), pass: p < 0.05 and delta > 0
    O-x7-vs-a2c      X7-on - A2C-on, paired progress + paired success (sign test)
    O-attrib         X7-null - B0-6ep-null, paired progress: pass if the bootstrap 95% CI lies inside [-0.1, 0.1]
    secondary        X7-on - B0-null, A2C on - null, A2C-null - B0-null; success rates (Wilson 95%); stage counts;
                     decision correctness (swap: 2nd move takes the other block; put_back: block back on its own mat);
                     P(press | centre) for put_back

Pairs are formed on (task, seed) present in both arms, so scenes that differ between the A100 and H200 banks drop out
(n is printed). H200 episodes are read from closed_loop/h200/... after the sync (see the ops doc).

    PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/official_table.py      -> outputs/memory_v2/report/OFFICIAL_*.md/json
"""
import json
import math
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import queue5 as q  # noqa: E402

PUT, SWAP = "put_back_block", "swap_blocks"
CL = "closed_loop"
ROWS = {
    (SWAP, "X7"): ([f"{CL}/official/swap8_x7_s{k}" for k in range(3)], "a2C6_e6_exec8", "A100"),
    (SWAP, "A2C"): ([f"{CL}/h200/official/swap8_a2c"], "a2C_e3_exec8", "H200"),
    (SWAP, "B0"): ([f"{CL}/official/swap8_b0_s{k}" for k in range(3)], "a2B0_e6_exec8", "A100"),
    (PUT, "X7"): ([f"{CL}/h200/official_pilot", f"{CL}/official/put_x7_s0", f"{CL}/official/put_x7_s1"], "a2C6_e6",
                  "H200 scenes 1-30, A100 31-100"),
    (PUT, "A2C"): ([f"{CL}/h200/official_pilot"], "a2C_e3_exec8", "H200"),
    (PUT, "B0"): ([f"{CL}/h200/official/put8_b0_s{k}" for k in range(2)], "a2B0_e6_exec8", "H200"),
}


def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [round(max(0.0, (c - r) / d) * 100), round(min(1.0, (c + r) / d) * 100)]


def load():
    eps = {}
    for (task, model), (folders, label, where) in ROWS.items():
        missing = [f for f in folders if not q.resolve(f).exists()]
        eps[(task, model)] = q.episodes([f for f in folders if f not in missing], label, None, [task])
        eps[(task, model, "missing")] = missing
    return eps


def mode_rows(eps, task, model, mode):
    return {seed: a for (t, md, seed), a in eps[(task, model)].items() if t == task and md == mode}


def compare(eps, task, a, b):
    """a = (model, mode), b = (model, mode): paired progress + success on common seeds."""
    ra, rb = mode_rows(eps, task, *a), mode_rows(eps, task, *b)
    common = sorted(set(ra) & set(rb))
    if not common:
        return {"n": 0}
    pa = [q.progress(task, ra[s]) for s in common]
    pb = [q.progress(task, rb[s]) for s in common]
    diffs = [round(x - y, 6) for x, y in zip(pa, pb)]
    only_a = sum(bool(ra[s].get("success")) and not bool(rb[s].get("success")) for s in common)
    only_b = sum(bool(rb[s].get("success")) and not bool(ra[s].get("success")) for s in common)
    return {"n": len(common), "mean_a": round(q.mean(pa), 3), "mean_b": round(q.mean(pb), 3), "delta": round(q.mean(diffs), 3),
            "ci": q.bootstrap_ci(diffs), "p": round(q.perm_p(diffs), 5),
            "success_a": sum(bool(ra[s].get("success")) for s in common),
            "success_b": sum(bool(rb[s].get("success")) for s in common),
            "only_a": only_a, "only_b": only_b, "success_sign_p": round(q.sign_p(only_a, only_b), 4)}


def row_stats(eps, task, model, mode):
    r = mode_rows(eps, task, model, mode)
    n = len(r)
    if not n:
        return None
    k = sum(bool(a.get("success")) for a in r.values())
    stages = {s: sum(bool(a.get(s)) for a in r.values()) for s in q.STAGES[task]}
    correct = [a.get("choice_correct") for a in r.values() if a.get("choice_correct") is not None]
    out = {"n": n, "success": k, "rate": round(100 * k / n), "ci": wilson(k, n),
           "progress": round(q.mean(q.progress(task, a) for a in r.values()), 3), "stages": stages,
           "choice_correct": f"{sum(correct)}/{len(correct)}" if correct else "-"}
    if task == PUT:
        out["p_press_given_centre"] = f"{stages['pressed']}/{stages['centre']}" + \
            (f" = {stages['pressed'] / stages['centre']:.2f}" if stages["centre"] else "")
    return out


def fmt_cmp(c):
    if not c.get("n"):
        return "no common scenes"
    return (f"{c['mean_a']:.3f} vs {c['mean_b']:.3f}, delta {c['delta']:+.3f} [{c['ci'][0]:+.3f}, {c['ci'][1]:+.3f}], "
            f"p={c['p']:.4f}, n={c['n']}; success {c['success_a']} vs {c['success_b']} "
            f"(only A {c['only_a']} / only B {c['only_b']}, sign p={c['success_sign_p']:.3f})")


def main():
    eps = load()
    out = {"time": q.now_bj(), "rows": {}, "tests": {}}
    lines = [f"# Official protocol table ({q.now_bj()}; execute 8; 100 official seed-42 scenes per task)", ""]
    miss = {f"{t}/{m}": eps[(t, m, 'missing')] for (t, m) in ROWS if eps[(t, m, 'missing')]}
    if miss:
        lines += [f"**Missing folders (rows incomplete):** {miss}", ""]
    lines += ["## Rows", "", "| task | model | where | mode | n | success % [95% CI] | progress | stages reached | "
              "decision correct | P(press|centre) |", "|---|---|---|---|---|---|---|---|---|---|"]
    for (task, model), (folders, label, where) in ROWS.items():
        for mode in ("on", "null"):
            s = row_stats(eps, task, model, mode)
            if not s:
                continue
            out["rows"][f"{task}/{model}/{mode}"] = s
            st = " ".join(f"{k}={v}" for k, v in s["stages"].items())
            lines.append(f"| {task} | {model} ({label}) | {where} | {mode} | {s['n']} | {s['success']} = {s['rate']}% "
                         f"{s['ci']} | {s['progress']:.3f} | {st} | {s['choice_correct']} | {s.get('p_press_given_centre', '-')} |")
    lines += ["", "References: FastWAM 0 / 0; RM-WAM 70 / 62; Mem-0 90 / 67; MaP-WAM 100 / 97; MemoryWAM, SimpleMemVLA 100 / 100 "
              "(put_back / swap).", "", "## Pre-registered tests (v5 C.2)", ""]
    for task, name in ((SWAP, "O-swap"), (PUT, "O-put")):
        c = compare(eps, task, ("X7", "on"), ("X7", "null"))
        ok = c.get("n") and c["p"] < 0.05 and c["delta"] > 0
        out["tests"][name] = {**c, "verdict": "PASS" if ok else "FAIL"}
        lines.append(f"- **{name}** X7 on - null: {fmt_cmp(c)} -> **{'PASS' if ok else 'FAIL'}**")
    for task in (SWAP, PUT):
        c = compare(eps, task, ("X7", "on"), ("A2C", "on"))
        out["tests"][f"O-x7-vs-a2c/{task}"] = c
        lines.append(f"- **O-x7-vs-a2c** {task}: X7-on vs A2C-on: {fmt_cmp(c)}")
    for task in (SWAP, PUT):
        c = compare(eps, task, ("X7", "null"), ("B0", "null"))
        ok = c.get("n") and -0.1 <= c["ci"][0] and c["ci"][1] <= 0.1
        out["tests"][f"O-attrib/{task}"] = {**c, "verdict": "PASS" if ok else "FAIL"}
        lines.append(f"- **O-attrib** {task}: X7-null vs B0-null: {fmt_cmp(c)} -> **{'PASS' if ok else 'FAIL'}** "
                     "(pass: 95% CI inside [-0.1, 0.1])")
    lines += ["", "## Secondary comparisons", ""]
    for task in (SWAP, PUT):
        for a, b, what in ((("X7", "on"), ("B0", "null"), "memory effect against the never-history model"),
                           (("A2C", "on"), ("A2C", "null"), "A2C memory effect"),
                           (("A2C", "null"), ("B0", "null"), "A2C null vs B0-6ep null"),
                           (("X7", "null"), ("A2C", "null"), "X7 null vs A2C null (does the null branch weaken with training?)")):
            c = compare(eps, task, a, b)
            out["tests"][f"{task}/{a[0]}-{a[1]}_vs_{b[0]}-{b[1]}"] = c
            lines.append(f"- {task}: {a[0]}-{a[1]} vs {b[0]}-{b[1]} ({what}): {fmt_cmp(c)}")
    R = q.O / "report"
    R.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(q.BJ).strftime("%Y%m%d_%H%M")
    (R / f"OFFICIAL_{stamp}.json").write_text(json.dumps(out, indent=1, default=str))
    md = R / f"OFFICIAL_{stamp}.md"
    md.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nOFFICIAL: {md}")


if __name__ == "__main__":
    main()

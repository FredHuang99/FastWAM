"""11-27 (Opus; plan v21 6.1 / 6.5 / section 8): writes the plan v21 A40 tasks into scripts/memory_v2/jobs/queue5_tasks.yaml.
The queue takes the FIRST runnable task of the file, so the order in the file is the priority:
  block 1 (inserted right after 'tasks:'): MAIN of cards 20 / 21 / 22 (new versions first, plan v20 rule) + verdicts;
  block 2 (right after block 1): zero-training diagnostics on the A40 GPUs - diagnostic 2 (ranking reading audit),
           diagnostic 5(a) (swap_T masks), the rearrange re-tests (rearr_pw e30 second noise draw; 256-frame pause);
  block 3 (right after block 2): e10 / e20 of cards 20 / 21 (described);
  block 4 (appended at the END of the file, lowest priority): the 'learns fast' step A evaluations (plan v21 6.7),
           written by --step-a once the export inventory is done.
Run once per block (an id already in the file is never written twice):
  python3 scripts/fullft/gen_v21_tasks.py --blocks 1 2 3
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
YAML = ROOT / "scripts/memory_v2/jobs/queue5_tasks.yaml"
EXP = "/workspace/FastWAM-memory2/outputs/fullft/exports"
PY = "cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python"

# diagnostic 2 scenes (plan v21 6.5): the sorted order at position 1-2 / 4-5 of the expert's walk, the 15 smallest scene
# ids each (RANKING_SPLIT.json 'expert_position_of_sorted', identical for both models; fixed 11-27 01:55 before any run)
D2_P12 = [4300001, 4300003, 4300006, 4300007, 4300008, 4300012, 4300014, 4300016, 4300017, 4300024, 4300026, 4300027,
          4300028, 4300030, 4300031]
D2_P45 = [4300000, 4300002, 4300004, 4300005, 4300009, 4300011, 4300013, 4300015, 4300018, 4300019, 4300020, 4300021,
          4300022, 4300035, 4300037]


def q(s):
    return '"' + s.replace('"', '\\"') + '"'


def fetch(run, tag, why, timeout=240):
    return f"""- id: A40-fetch-{run}-{tag}
  lane: a40cpu
  kind: shell
  need_mib: 0
  timeout_h: {timeout}
  hypothesis: {q(f"fetch {run}_{tag} from the relay ({why}; sha256 checked; waits until it is there)")}
  command: "RUN={run} TAG={tag} bash /workspace/FastWAM-memory2/scripts/fullft/export_fetch.sh"
  pass_if: "m['rc'] == 0"
"""


def loop(tid, after, why, ckpt, label, task, args, output, env=None, timeout=12, smoke=False):
    env = env or {}
    env_s = ", ".join([f'MWAM_TEXT_SOURCE: "cache"'] + [f'{k}: "{v}"' for k, v in env.items()])
    a = ", ".join(q(x) for x in args)
    s = f"""- id: {tid}
  lane: a40
  kind: closed_loop
  after: [{", ".join(after)}]
  requires_pass: [{", ".join(after)}]
  need_mib: 30000
  timeout_h: {timeout}
  hypothesis: {q(why)}
  checkpoint: {ckpt}
  label: {label}
  modes: ["on"]
  scenes: [closed_loop/scenes_seed42_n100_{task}]
  tasks: [{task}]
  online_args: [{a}]
  output: {output}
  env: {{{env_s}}}
"""
    if smoke:
        s += "  pass_if: \"m.get('episodes', 0) >= 1\"\n"
    return s


def shell(tid, after, why, command, timeout=2):
    return f"""- id: {tid}
  lane: a40cpu
  kind: shell
  after: [{", ".join(after)}]
  need_mib: 0
  timeout_h: {timeout}
  hypothesis: {q(why)}
  command: {q(command)}
  pass_if: "m['rc'] == 0"
"""


CARDS = {"rearr_ar_pw": "card 20", "rearr_arprop_pw": "card 21", "rearr_pw_s18": "card 22"}


def block1():
    out = ["# " + "-" * 115,
           "# 11-27 02:10 (Opus; plan v21 6.1 / section 8, prompt v21 part 3.2): MAIN of cards 20 / 21 / 22 (new H200; readings",
           "# registered verbatim in gaas_queue.txt above their lines, commit a1aa519, before any run). Placed first in the file",
           "# (new versions' MAIN first). rearrange_blocks 1-100, seed-42 bank, default noise, execute 8, closed_loop/v21.",
           "# Verdicts: scripts/fullft/v21_verdict.py c20 / c21 / c22 (written before any episode).", ""]
    for run, card in CARDS.items():
        why = f"plan v21 {card}, new H200"
        out.append(fetch(run, "e30", why))
        out.append(loop(f"A40-v21-{run}-smoke", [f"A40-fetch-{run}-e30", "A40-prep2-rearrange_blocks"],
                        f"smoke: {run}_e30, rearrange_blocks scene 1, one episode finishes on the A40 (closed_loop/v21smoke)",
                        f"{EXP}/{run}_e30/export_e30.pt", f"{run}_e30_smoke", "rearrange_blocks",
                        ["--execute", "8", "--limit", "1"], "closed_loop/v21smoke", timeout=3, smoke=True))
        for k in range(10):
            out.append(loop(f"A40-v21-{run}-s{k}", [f"A40-v21-{run}-smoke"],
                            f"plan v21 {card} MAIN (registered 11-27 in gaas_queue.txt above {run}): {run}_e30 on "
                            f"rearrange_blocks 1-100; shard {k} of 10",
                            f"{EXP}/{run}_e30/export_e30.pt", f"{run}_e30", "rearrange_blocks",
                            ["--execute", "8", "--limit", "100", "--shard", f"{k}/10"], "closed_loop/v21"))
    shards = lambda run: [f"A40-v21-{run}-s{k}" for k in range(10)]     # noqa: E731
    out.append(shell("A40-V21-C20-verdict", shards("rearr_ar_pw"),
                     "plan v21 card 20 verdict: v21_verdict.py c20 (D = rearr_pw - rearr_ar_pw, SESOI +0.15 -> RECORD "
                     "NEEDED / WEIGHTING ALONE SUFFICES / UNCERTAIN); log pushed",
                     f"{PY} scripts/fullft/v21_verdict.py c20"))
    out.append(shell("A40-V21-C21-verdict", shards("rearr_arprop_pw"),
                     "plan v21 card 21 verdict: v21_verdict.py c21 (non-inferiority of the old writer, margin -0.10 -> OLD "
                     "WRITER SUFFICES / TIMELY WRITER NEEDED / UNCERTAIN) + rearr_ledger.py write delay; log pushed",
                     f"{PY} scripts/fullft/v21_verdict.py c21 && PYTHONPATH=src /opt/mwam/bin/python "
                     f"scripts/fullft/rearr_ledger.py v21:rearr_arprop_pw_e30 v20:rearr_pw_e30"))
    out.append(shell("A40-V21-C22-report", shards("rearr_pw_s18"),
                     "plan v21 card 22 (described only): v21_verdict.py c22 - success and classes of seed 18 beside "
                     "rearr_pw seed 17, the mean of the two seeds; log pushed",
                     f"{PY} scripts/fullft/v21_verdict.py c22"))
    return "\n".join(out) + "\n"


def block2():
    out = ["# " + "-" * 115,
           "# 11-27 02:10 (Opus; plan v21 6.5, P0, zero training): diagnostics on the A40 GPUs. Described only.",
           "# Diagnostic 2 (ranking reading audit): 30 scenes fixed 11-27 01:55 (D2_P12 / D2_P45 in gen_v21_tasks.py: the",
           "# sorted order at position 1-2 / 4-5 of the expert's walk, the 15 smallest scene ids each); body record e30: record",
           "# off (MWAM_LEDGER=off), first frame masked, the two near frames masked (MWAM_HIST_MASK first / near); three-frame",
           "# e30: first / near masked. 150 episodes, closed_loop/diag2; beside the unmodified e6 runs of the same scenes.",
           "# Diagnostic 5(a) (swap_T): swapT_ar e30 first / near masked; swapT_arprop e30 first / near masked and record off;",
           "# scenes 1-50, closed_loop/diag5; beside e6.",
           "# Rearrange re-tests (plan v21 6.5): rearr_pw e30 again with MWAM_NOISE_SALT=r2, 1-100 (closed_loop/r2); 256-frame",
           "# pause visible / hidden, 1-50 each (E16's injection, event:pause:256:history|hidden; closed_loop/v21rt).", ""]
    seeds = [f"blocks_ranking_try:{s}" for s in D2_P12 + D2_P45]
    d2 = {"ranking_arprop_e30": [("off", {"MWAM_LEDGER": "off"}), ("mfirst", {"MWAM_HIST_MASK": "first"}),
                                 ("mnear", {"MWAM_HIST_MASK": "near"})],
          "ranking_ar_e30": [("mfirst", {"MWAM_HIST_MASK": "first"}), ("mnear", {"MWAM_HIST_MASK": "near"})]}
    ids2 = []
    for model, conds in d2.items():
        for name, env in conds:
            for k in range(3):
                tid = f"A40-diag2-{model.split('_e30')[0]}-{name}-s{k}"
                ids2.append(tid)
                out.append(loop(tid, ["A40-prep2-blocks_ranking_try"],
                                f"plan v21 diagnostic 2 (described): {model} {name} on the 30 audit scenes of ranking; "
                                f"shard {k} of 3", f"{EXP}/{model}/export_e30.pt", f"{model}_{name}",
                                "blocks_ranking_try", ["--execute", "8", "--seeds", *seeds, "--shard", f"{k}/3"],
                                "closed_loop/diag2", env=env, timeout=24))
    # MWAM_OBJECT_LOG=1 (sim_adapter.py, logging only): T-block poses for swapT_split.measure in the report
    d5 = {"swapT_ar_e30": [("mfirst", {"MWAM_HIST_MASK": "first", "MWAM_OBJECT_LOG": "1"}),
                           ("mnear", {"MWAM_HIST_MASK": "near", "MWAM_OBJECT_LOG": "1"})],
          "swapT_arprop_e30": [("mfirst", {"MWAM_HIST_MASK": "first", "MWAM_OBJECT_LOG": "1"}),
                               ("mnear", {"MWAM_HIST_MASK": "near", "MWAM_OBJECT_LOG": "1"}),
                               ("off", {"MWAM_LEDGER": "off", "MWAM_OBJECT_LOG": "1"})]}
    ids5 = []
    for model, conds in d5.items():
        for name, env in conds:
            for k in range(5):
                tid = f"A40-diag5a-{model.split('_e30')[0]}-{name}-s{k}"
                ids5.append(tid)
                out.append(loop(tid, ["A40-prep2-swap_T"],
                                f"plan v21 diagnostic 5(a) (described): {model} {name} on swap_T 1-50; shard {k} of 5",
                                f"{EXP}/{model}/export_e30.pt", f"{model}_{name}", "swap_T",
                                ["--execute", "8", "--limit", "50", "--shard", f"{k}/5"], "closed_loop/diag5", env=env))
    idsr = []
    for k in range(10):
        tid = f"A40-rt-rearr_pw-r2-s{k}"
        idsr.append(tid)
        out.append(loop(tid, ["A40-prep2-rearrange_blocks"],
                        f"plan v21 6.5 rearrange re-test (described): rearr_pw_e30 on rearrange_blocks 1-100 with "
                        f"MWAM_NOISE_SALT=r2 (the main-table cell's second pass); shard {k} of 10",
                        f"{EXP}/rearr_pw_e30/export_e30.pt", "rearr_pw_e30", "rearrange_blocks",
                        ["--execute", "8", "--limit", "100", "--shard", f"{k}/10"], "closed_loop/r2",
                        env={"MWAM_NOISE_SALT": "r2"}))
    for arm in ("history", "hidden"):
        short = "vis" if arm == "history" else "hid"
        for k in range(5):
            tid = f"A40-rt-rearr_pw-p256{short}-s{k}"
            idsr.append(tid)
            out.append(loop(tid, ["A40-prep2-rearrange_blocks"],
                            f"plan v21 6.5 rearrange re-test (described, E16's injection): rearr_pw_e30, pause 256 "
                            f"{short}, rearrange_blocks 1-50; shard {k} of 5",
                            f"{EXP}/rearr_pw_e30/export_e30.pt", f"rearr_pw_e30_p256_{short}", "rearrange_blocks",
                            ["--execute", "8", "--limit", "50", "--stress", f"event:pause:256:{arm}", "--shard", f"{k}/5"],
                            "closed_loop/v21rt", timeout=24))
    out.append(shell("A40-DIAG2-report", ids2,
                     "plan v21 diagnostic 2 described: diag_v21.py diag2 (success per condition beside the unmodified e6 "
                     "runs, by position group; ranking_split.py classes); log pushed",
                     f"{PY} scripts/fullft/diag_v21.py diag2"))
    out.append(shell("A40-DIAG5A-report", ids5,
                     "plan v21 diagnostic 5(a) described: diag_v21.py diag5a (success per condition beside e6, 1-50; "
                     "swapT_split.py classes); log pushed",
                     f"{PY} scripts/fullft/diag_v21.py diag5a"))
    out.append(shell("A40-REARRRT-report", idsr,
                     "plan v21 6.5 rearrange re-tests described: diag_v21.py rearrrt (r2 success and classes beside the "
                     "default draw; pause 256 visible / hidden, paired counts); log pushed",
                     f"{PY} scripts/fullft/diag_v21.py rearrrt"))
    return "\n".join(out) + "\n"


def block3():
    out = ["# " + "-" * 115,
           "# 11-27 02:10 (Opus; plan v21 6.1): e10 / e20 of cards 20 / 21, described (after the MAIN evaluations and the",
           "# diagnostics), closed_loop/v21; the verdict scripts are run again to add them (the MAIN reading is unchanged).", ""]
    ids = {}
    for run in ("rearr_ar_pw", "rearr_arprop_pw"):
        for tag in ("e10", "e20"):
            out.append(fetch(run, tag, f"plan v21 {CARDS[run]}, new H200"))
            for k in range(10):
                tid = f"A40-v21-{run}-{tag}-s{k}"
                ids.setdefault(run, []).append(tid)
                out.append(loop(tid, [f"A40-fetch-{run}-{tag}", "A40-prep2-rearrange_blocks"],
                                f"plan v21 {CARDS[run]} described: {run}_{tag} on rearrange_blocks 1-100; shard {k} of 10",
                                f"{EXP}/{run}_{tag}/export_{tag}.pt", f"{run}_{tag}", "rearrange_blocks",
                                ["--execute", "8", "--limit", "100", "--shard", f"{k}/10"], "closed_loop/v21"))
    out.append(shell("A40-V21-C20-e1020-report", ids["rearr_ar_pw"] + ["A40-V21-C20-verdict"],
                     "plan v21 card 20: v21_verdict.py c20 again once e10 / e20 are evaluated; log pushed",
                     f"{PY} scripts/fullft/v21_verdict.py c20"))
    out.append(shell("A40-V21-C21-e1020-report", ids["rearr_arprop_pw"] + ["A40-V21-C21-verdict"],
                     "plan v21 card 21: v21_verdict.py c21 again once e10 / e20 are evaluated; log pushed",
                     f"{PY} scripts/fullft/v21_verdict.py c21"))
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--blocks", nargs="+", type=int, default=[1, 2, 3])
    args = ap.parse_args()
    text = YAML.read_text()
    have = set(re.findall(r"^- id: (\S+)", text, re.M))
    new = "".join({1: block1, 2: block2, 3: block3}[b]() for b in sorted(args.blocks))
    ids = re.findall(r"^- id: (\S+)", new, re.M)
    dup = [i for i in ids if i in have] + [i for i in set(ids) if ids.count(i) > 1]
    if dup:
        raise SystemExit(f"ids already in the file / repeated: {dup[:8]}")
    head, sep, rest = text.partition("\ntasks:\n")
    assert sep, "no 'tasks:' line"
    YAML.write_text(head + sep + new + "\n" + rest)
    print(f"inserted {len(ids)} tasks after 'tasks:' (blocks {args.blocks})")


if __name__ == "__main__":
    main()

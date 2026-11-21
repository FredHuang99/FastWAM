#!/usr/bin/env bash
# mwam5090, 11-21 14:25 BJ (Opus, plan v18 Z1; the user approved at 14:21). GPU1 only (PF_GPUS, default 1). Test time.
# All arms use the oracle ledger (MWAM_LEDGER=oracle: true press counters, zero writing delay), press scenes 1-100:
#   1 smoke (scene 1, 200 targets): every registered press of button 1 / 2 must have a decision at the very frame the
#     counter shows it, with that press in the decision's ledger; any failure: stop (nothing else runs)
#   2 Z1  --replan replan (closed_loop/tim, label press_count_e30_oracle_replan): re-decide at the press, press read
#   3 Z1b --replan blind  (closed_loop/tim, label press_count_e30_oracle_blind): the same re-decision, press hidden
#   after 2 and 3: z1_verdict.py (registered reading in its header) and the ledger / timing audits; relay diag/z1_verdict
#   4 only if MAIN is UNCERTAIN (the registered extension): Z0 and Z1 again with MWAM_NOISE_SALT=r2 (closed_loop/tim2),
#     then z1_verdict.py --extended
#   docker exec -d -e PF_GPUS=1 mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/z1_eval_5090.sh
# Own log: outputs/fullft/Z1_EVAL_5090_<time>.txt. Rerunnable: finished episodes are skipped.
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
EX=$R/outputs/fullft/exports
F=$R/outputs/fullft
LOG=$F/Z1_EVAL_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[z1] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
unset MWAM_LEDGER MWAM_NOISE_SALT MWAM_LEDGER_LAG MWAM_EVENT_DELTA MWAM_EVENT_MIN_PATH MWAM_EVENT_PROVISIONAL
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python; [ -x $HFPY ] || HFPY=$PY
BANK=$O/closed_loop/scenes_seed42_n100_press_button
PF_GPUS=${PF_GPUS:-1}
CK=$EX/press_count_e30/export_e30.pt
echo "[z1] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPUs $PF_GPUS"
[ -f $CK ] || { echo "[z1] no $CK on this machine: stop"; exit 1; }
grep -q '_oracle_fresh' src/fastwam/memory_v2/online.py || { echo "[z1] online.py has no oracle trigger (git pull): stop"; exit 1; }
pgrep -f "[o]racle_eval_5090.sh|[t]iming_eval_5090.sh|[r]eplan_eval_5090.sh" >/dev/null && { echo "[z1] another 5090 evaluation chain runs: stop"; exit 1; }

empty() { local u; u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 2>/dev/null | tr -d ' '); [[ "$u" =~ ^[0-9]+$ ]] && [ "$u" -lt 2000 ]; }
gpu_ok() { nvidia-smi -i $1 --query-gpu=index --format=csv,noheader >/dev/null 2>&1; }
claim() { until empty $1 && sleep 90 && empty $1; do sleep 120; done; echo "[z1] $(date '+%F %T') GPU $1 claimed"; }
n_done() { ls $O/closed_loop/$1/$2/on/press_button/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json'; }
G=""; for g in $PF_GPUS; do gpu_ok $g && { G=$g; break; }; done
[ -n "$G" ] || { echo "[z1] no allowed GPU answers (PF_GPUS=$PF_GPUS): stop"; exit 1; }

run() {        # folder, label, from-scene, replan mode ("" = none), then env assignments
  local fo=$1 l=$2 from=$3 rp=$4; shift 4
  local extra=(); [ -n "$rp" ] && extra=(--replan $rp)
  claim $G
  for sh in 0 1; do for pass in 1 2; do
    ( for a in "$@"; do export "$a"; done
      CUDA_VISIBLE_DEVICES=$G $PY -m fastwam.memory_v2.online run --checkpoint $CK --label $l --scenes $BANK \
        --tasks press_button --execute 8 "${extra[@]}" --output $O/closed_loop/$fo --from-scene $from --limit 50 \
        --shard $sh/2 >> $O/closed_loop/${fo}_$l.log 2>&1 )
    echo "[z1] $(date '+%F %T') $fo:$l scenes from $from shard $sh/2 pass $pass exit code $?; finished $(n_done $fo $l)"
  done; done
}

echo "[z1] $(date '+%F %T') ===== 1 smoke (oracle + re-decision at the press, scene 1, 200 targets) on GPU $G"
claim $G
MWAM_LEDGER=oracle CUDA_VISIBLE_DEVICES=$G $PY -m fastwam.memory_v2.online run --checkpoint $CK \
  --label press_count_e30_oracle_replan --scenes $BANK --tasks press_button --execute 8 --replan replan --max-targets 200 \
  --output $O/closed_loop/tsmoke --limit 1 >> $O/closed_loop/tsmoke_z1.log 2>&1
echo "[z1] $(date '+%F %T') smoke exit code $?"
$PY - <<'EOF' || { echo "[z1] SMOKE FAILED: stop (nothing else runs)"; exit 1; }
import json
from pathlib import Path
O = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/tsmoke/press_count_e30_oracle_replan/on/press_button")
res = sorted(O.glob("seed_*/result.json"))
assert res, "no smoke episode"
d = res[0].parent
r = json.loads(res[0].read_text())
rows = [json.loads(x) for x in (d / "executed_actions.jsonl").read_text().splitlines() if x.strip()]
dec = {json.loads(x)["frame_id"]: json.loads(x) for x in (d / "decisions.jsonl").read_text().splitlines() if x.strip()}
regs = [i + 1 for i, x in enumerate(rows) for c in ("press_cnt_1", "press_cnt_2")
        if int((x.get("objects_after") or {}).get(c) or 0) > int((x.get("objects_before") or {}).get(c) or 0)]
regs = [f for f in regs if f < len(rows)]
rp = [json.loads(x) for x in (d / "replan.jsonl").read_text().splitlines() if x.strip()] if (d / "replan.jsonl").exists() else []
print(f"[smoke] {len(rows)} targets, {r['decisions']} decisions, {len(rp)} re-decisions at {[x['frame'] for x in rp]}; "
      f"presses (buttons 1 / 2) registered at {regs}; command_to_execution_exact {r['command_to_execution_exact']}")
assert regs, "no press in 200 targets"
for f in regs:
    assert f in dec, f"no decision at the press frame {f}"
    assert any(e[2] == "bottom" and int(e[3]) == f for e in dec[f]["ledger"]), f"the press at {f} is not in that decision's ledger"
print("[smoke] PASS")
EOF

verdict() {
  $PY scripts/fullft/z1_verdict.py "$@" 2>&1 | tail -n 9
  for l in press_count_e30_oracle_replan press_count_e30_oracle_blind; do
    [ "$(n_done tim $l)" -ge 50 ] || continue
    $PY scripts/fullft/press_ledger_audit.py tim:$l 2>&1 | grep -E "^==|over-pressing|visibility delay" | head -n 3
    $PY scripts/fullft/press_timing_audit.py --describe tim:$l --out $F/PRESS_TIMING_AUDIT_$l.json 2>&1 | grep -E "O3 chain|O5 deciding" | head -n 2
  done
  $HFPY scripts/memory_v2/migrate/relay.py put $F/Z1_VERDICT.json --prefix diag/z1_verdict 2>&1 | tail -n 1
}
echo "[z1] $(date '+%F %T') ===== 2 Z1 (re-decide at the press, press read), scenes 1-50 and 51-100"
run tim press_count_e30_oracle_replan 1 replan MWAM_LEDGER=oracle
run tim press_count_e30_oracle_replan 51 replan MWAM_LEDGER=oracle
verdict
echo "[z1] $(date '+%F %T') ===== 3 Z1b (re-decide at the press, press hidden), scenes 1-50 and 51-100"
run tim press_count_e30_oracle_blind 1 blind MWAM_LEDGER=oracle
run tim press_count_e30_oracle_blind 51 blind MWAM_LEDGER=oracle
verdict
if grep -q '"Z1": "UNCERTAIN"' $F/Z1_VERDICT.json; then
  echo "[z1] $(date '+%F %T') ===== 4 registered extension: Z0 and Z1 with noise r2, scenes 1-100"
  run tim2 press_count_e30_oracle 1 "" MWAM_LEDGER=oracle MWAM_NOISE_SALT=r2
  run tim2 press_count_e30_oracle 51 "" MWAM_LEDGER=oracle MWAM_NOISE_SALT=r2
  run tim2 press_count_e30_oracle_replan 1 replan MWAM_LEDGER=oracle MWAM_NOISE_SALT=r2
  run tim2 press_count_e30_oracle_replan 51 replan MWAM_LEDGER=oracle MWAM_NOISE_SALT=r2
  verdict --extended
fi
echo "[z1] $(date '+%F %T') ===== all done"

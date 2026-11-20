#!/usr/bin/env bash
# mwam5090, 11-20 22:00 BJ (Opus, plan v17; the user took over the Fable review of plan v16 in full at 20:47).
# GPU1 only (PF_GPUS, default 1). Read-only first, then test time only (no training):
#   0 G4-0 now (CPU, while T1 / T2 still run on GPU1): press_timing_audit.py (O1 denominator table, O3 chain, O5 delay
#     decomposition; reading registered in its header) on the three press_count e30 runs (g1, sel, rep), described on
#     press_v3c e30 (g1, sel); JSON to the relay (diag/press_timing_audit)
#   1 waits until timing_eval_5090.sh (T1 / T2) has finished (at most 14 h), then timing_meaning.py (how to read the
#     registered T1 / T2 words: manipulation check, prov over-presses, lag16 e1, dose) to the relay (diag/timing_verdict)
#   2 smoke (scene 1): --replan off for 48 targets must decide at 0, 8, ..., 40 and its first decision must equal the
#     g1 baseline's first decision of the same scene (max |diff| < 0.01); --replan replan for 160 targets must log at
#     least one re-decision and pass the command-to-execution check. Any failure: stop (nothing else runs).
#   3 T2b replan arm  (closed_loop/tim, label press_count_e30_replan), scenes 1-50
#   4 T2b blind arm   (closed_loop/tim, label press_count_e30_blind),  scenes 1-50
#   after 3 and 4: replan_verdict.py (registered reading in its header), the press ledger audit and the timing audit of
#   the new runs; verdict JSON to the relay (diag/replan_verdict). Rerunnable: finished episodes are skipped.
#   docker exec -d -e PF_GPUS=1 mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/replan_eval_5090.sh
# Own log: outputs/fullft/REPLAN_EVAL_5090_<time>.txt
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
EX=$R/outputs/fullft/exports
F=$R/outputs/fullft
LOG=$F/REPLAN_EVAL_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[rp] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
unset MWAM_LEDGER MWAM_NOISE_SALT MWAM_LEDGER_LAG MWAM_EVENT_DELTA MWAM_EVENT_MIN_PATH MWAM_EVENT_PROVISIONAL
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python; [ -x $HFPY ] || HFPY=$PY
BANK=$O/closed_loop/scenes_seed42_n100_press_button
PF_GPUS=${PF_GPUS:-1}
CK=$EX/press_count_e30/export_e30.pt
echo "[rp] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPUs $PF_GPUS"
[ -f $CK ] || { echo "[rp] no $CK on this machine: stop"; exit 1; }
grep -q "class ReplanDriver" src/fastwam/memory_v2/online.py || { echo "[rp] online.py has no ReplanDriver (git pull): stop"; exit 1; }

echo "[rp] $(date '+%F %T') ===== 0 G4-0 timing audit (CPU, read-only)"
$PY scripts/fullft/press_timing_audit.py --primary g1:press_count_e30 sel:press_count_e30 rep:press_count_e30 \
  --describe g1:press_v3c_e30 sel:press_v3c_e30 --out $F/PRESS_TIMING_AUDIT.json 2>&1 | tail -n 70
$HFPY scripts/memory_v2/migrate/relay.py put $F/PRESS_TIMING_AUDIT.json --prefix diag/press_timing_audit 2>&1 | tail -n 1

i=0
while pgrep -f "[t]iming_eval_5090.sh" >/dev/null && [ $i -lt 168 ]; do
  [ $i = 0 ] && echo "[rp] $(date '+%F %T') T1 / T2 chain still runs: waiting (at most 14 h)"; sleep 300; i=$((i + 1)); done
pgrep -f "[t]iming_eval_5090.sh" >/dev/null && { echo "[rp] T1 / T2 chain still running after 14 h: stop"; exit 1; }
echo "[rp] $(date '+%F %T') ===== G4a: how to read the T1 / T2 words (timing_meaning.py, descriptive)"
$PY scripts/fullft/timing_meaning.py 2>&1 | tail -n 9
$HFPY scripts/memory_v2/migrate/relay.py put $F/TIMING_MEANING.json --prefix diag/timing_verdict 2>&1 | tail -n 1

empty() { local u; u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 2>/dev/null | tr -d ' '); [[ "$u" =~ ^[0-9]+$ ]] && [ "$u" -lt 2000 ]; }
gpu_ok() { nvidia-smi -i $1 --query-gpu=index --format=csv,noheader >/dev/null 2>&1; }
claim() { until empty $1 && sleep 90 && empty $1; do sleep 120; done; echo "[rp] $(date '+%F %T') GPU $1 claimed"; }
n_done() { ls $O/closed_loop/$1/$2/on/press_button/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json'; }
G=""; for g in $PF_GPUS; do gpu_ok $g && { G=$g; break; }; done
[ -n "$G" ] || { echo "[rp] no allowed GPU answers (PF_GPUS=$PF_GPUS): stop"; exit 1; }

echo "[rp] $(date '+%F %T') ===== 2 smoke on GPU $G"
claim $G
for m in off replan; do
  mt=$([ $m = off ] && echo 48 || echo 160)
  CUDA_VISIBLE_DEVICES=$G $PY -m fastwam.memory_v2.online run --checkpoint $CK --label press_count_e30_rp$m --scenes $BANK \
    --tasks press_button --execute 8 --replan $m --max-targets $mt --output $O/closed_loop/tsmoke --limit 1 \
    >> $O/closed_loop/tsmoke_rp$m.log 2>&1
  echo "[rp] $(date '+%F %T') smoke $m exit code $?"
done
$PY - <<'EOF' || { echo "[rp] SMOKE FAILED: stop (nothing else runs)"; exit 1; }
import json, sys
from pathlib import Path
import numpy as np
O = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop")
def rows(p): return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
off = sorted((O / "tsmoke/press_count_e30_rpoff/on/press_button").glob("seed_*/result.json"))
rep = sorted((O / "tsmoke/press_count_e30_rpreplan/on/press_button").glob("seed_*/result.json"))
assert off and rep, "smoke episodes missing"
d = off[0].parent
dec = rows(d / "decisions.jsonl")
frames = [r["frame_id"] for r in dec]
assert frames == list(range(0, 48, 8)), f"off schedule {frames}"
ref = O / "g1/press_count_e30/on/press_button" / d.name / "decisions.jsonl"
r0 = rows(ref)[0]
diff = float(np.abs(np.asarray(dec[0]["normalized_actions"]) - np.asarray(r0["normalized_actions"])).max())
print(f"[smoke] off: decisions at {frames}; first decision vs g1 {d.name}: max |diff| {diff:.2e}")
assert diff < 1e-2, "first decision differs from the baseline"
res = json.loads(rep[0].read_text())
rp = rows(rep[0].parent / "replan.jsonl") if (rep[0].parent / "replan.jsonl").exists() else []
print(f"[smoke] replan: {res['executed_targets']} targets, {res['decisions']} decisions, {len(rp)} re-decisions "
      f"(first at {rp[0]['frame'] if rp else None}, jump {rp[0]['joint_jump_rad'] if rp else None}); "
      f"command_to_execution_exact {res['command_to_execution_exact']}")
assert res["command_to_execution_exact"] and rp, "no re-decision in 160 targets or execution mismatch"
print("[smoke] PASS")
EOF

verdict() {
  $PY scripts/fullft/replan_verdict.py 2>&1 | tail -n 9
  $PY scripts/fullft/press_ledger_audit.py tim:$1 2>&1 | grep -E "^==|over-pressing|visibility delay|READING" | head -n 6
  $PY scripts/fullft/press_timing_audit.py --describe tim:$1 --out $F/PRESS_TIMING_AUDIT_$1.json 2>&1 | grep -E "O1 READING|O5 deciding|O3 chain" | head -n 4
  $HFPY scripts/memory_v2/migrate/relay.py put $F/REPLAN_VERDICT.json --prefix diag/replan_verdict 2>&1 | tail -n 1
}
arm() {        # mode
  local l=press_count_e30_$1
  [ "$(n_done tim $l)" -ge 50 ] && { echo "[rp] $l: already done"; verdict $l; return; }
  echo "[rp] $(date '+%F %T') ===== T2b $1 arm on GPU $G (scenes 1-50)"
  claim $G
  for sh in 0 1; do for pass in 1 2; do
    CUDA_VISIBLE_DEVICES=$G $PY -m fastwam.memory_v2.online run --checkpoint $CK --label $l --scenes $BANK \
      --tasks press_button --execute 8 --replan $1 --output $O/closed_loop/tim --limit 50 --shard $sh/2 \
      >> $O/closed_loop/tim_$l.log 2>&1
    echo "[rp] $(date '+%F %T') $l shard $sh/2 pass $pass exit code $?; finished $(n_done tim $l)"
  done; done
  verdict $l
}
arm replan
arm blind
echo "[rp] $(date '+%F %T') ===== both arms done"
$PY scripts/fullft/replan_verdict.py

#!/usr/bin/env bash
# mwam5090, 11-21 01:30 BJ (Opus, plan v18; the user approved at 00:58: replace T2b by the oracle-ledger test, pause W1,
# add two baseline replicates for the noise band). GPU1 only (PF_GPUS, default 1). Test time only, no training.
#   1 waits until timing_eval_5090.sh (T1 / T2) has finished (at most 14 h), then timing_meaning.py (G4a with all four
#     arms and the T2 typing) to the relay (diag/timing_verdict)
#   2 smoke (scene 1, 200 targets): the oracle ledger must hold 'bottom' entries readable one frame after the step that
#     pressed (confirmed = frame + 1) and the job must carry oracle_counts; any failure: stop (nothing else runs)
#   3 Z0 oracle (MWAM_LEDGER=oracle; closed_loop/tim, label press_count_e30_oracle), press scenes 1-50 and 51-100
#   4 oracle_verdict.py (registered reading in its header) + ledger / timing audits of the oracle run; relay diag/oracle_verdict
#   5 N0 noise: the baseline again with MWAM_NOISE_SALT=r2 (closed_loop/nz2) on scenes 1-50
#   6 only if step 4 says UNCERTAIN (the registered extension): the oracle with MWAM_NOISE_SALT=r2 on 1-100
#     (closed_loop/tim2), then oracle_verdict.py --extended
#   7 N0 noise: MWAM_NOISE_SALT=r3 (closed_loop/nz3) on 1-50; noise_band.py; relay diag/noise_band
#   docker exec -d -e PF_GPUS=1 mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/oracle_eval_5090.sh
# Own log: outputs/fullft/ORACLE_EVAL_5090_<time>.txt. Rerunnable: finished episodes are skipped.
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
EX=$R/outputs/fullft/exports
F=$R/outputs/fullft
LOG=$F/ORACLE_EVAL_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[or] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
unset MWAM_LEDGER MWAM_NOISE_SALT MWAM_LEDGER_LAG MWAM_EVENT_DELTA MWAM_EVENT_MIN_PATH MWAM_EVENT_PROVISIONAL
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python; [ -x $HFPY ] || HFPY=$PY
BANK=$O/closed_loop/scenes_seed42_n100_press_button
PF_GPUS=${PF_GPUS:-1}
CK=$EX/press_count_e30/export_e30.pt
echo "[or] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPUs $PF_GPUS"
[ -f $CK ] || { echo "[or] no $CK on this machine: stop"; exit 1; }
grep -q "def oracle_presses" src/fastwam/fullft/online.py || { echo "[or] online.py has no oracle ledger (git pull): stop"; exit 1; }
pgrep -f "[r]eplan_eval_5090.sh" >/dev/null && { echo "[or] the T2b chain (replan_eval_5090.sh) is still there: stop it first"; exit 1; }

i=0
while pgrep -f "[t]iming_eval_5090.sh" >/dev/null && [ $i -lt 168 ]; do
  [ $i = 0 ] && echo "[or] $(date '+%F %T') T1 / T2 chain still runs: waiting (at most 14 h)"; sleep 300; i=$((i + 1)); done
pgrep -f "[t]iming_eval_5090.sh" >/dev/null && { echo "[or] T1 / T2 chain still running after 14 h: stop"; exit 1; }
echo "[or] $(date '+%F %T') ===== G4a: timing_meaning.py (all four arms, T2 typing)"
$PY scripts/fullft/timing_meaning.py 2>&1 | tail -n 9
$HFPY scripts/memory_v2/migrate/relay.py put $F/TIMING_MEANING.json --prefix diag/timing_verdict 2>&1 | tail -n 1
$HFPY scripts/memory_v2/migrate/relay.py put $F/TIMING_VERDICT.json --prefix diag/timing_verdict 2>&1 | tail -n 1

empty() { local u; u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 2>/dev/null | tr -d ' '); [[ "$u" =~ ^[0-9]+$ ]] && [ "$u" -lt 2000 ]; }
gpu_ok() { nvidia-smi -i $1 --query-gpu=index --format=csv,noheader >/dev/null 2>&1; }
claim() { until empty $1 && sleep 90 && empty $1; do sleep 120; done; echo "[or] $(date '+%F %T') GPU $1 claimed"; }
n_done() { ls $O/closed_loop/$1/$2/on/press_button/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json'; }
G=""; for g in $PF_GPUS; do gpu_ok $g && { G=$g; break; }; done
[ -n "$G" ] || { echo "[or] no allowed GPU answers (PF_GPUS=$PF_GPUS): stop"; exit 1; }

run() {        # folder, label, from-scene, then env assignments; two shards of 25, two passes each
  local fo=$1 l=$2 from=$3; shift 3
  claim $G
  for sh in 0 1; do for pass in 1 2; do
    ( for a in "$@"; do export "$a"; done
      CUDA_VISIBLE_DEVICES=$G $PY -m fastwam.memory_v2.online run --checkpoint $CK --label $l --scenes $BANK \
        --tasks press_button --execute 8 --output $O/closed_loop/$fo --from-scene $from --limit 50 --shard $sh/2 \
        >> $O/closed_loop/${fo}_$l.log 2>&1 )
    echo "[or] $(date '+%F %T') $fo:$l scenes from $from shard $sh/2 pass $pass exit code $?; finished $(n_done $fo $l)"
  done; done
}

echo "[or] $(date '+%F %T') ===== 2 smoke (oracle, scene 1, 200 targets) on GPU $G"
claim $G
MWAM_LEDGER=oracle CUDA_VISIBLE_DEVICES=$G $PY -m fastwam.memory_v2.online run --checkpoint $CK --label press_count_e30_oracle \
  --scenes $BANK --tasks press_button --execute 8 --max-targets 200 --output $O/closed_loop/tsmoke --limit 1 \
  >> $O/closed_loop/tsmoke_oracle.log 2>&1
echo "[or] $(date '+%F %T') smoke exit code $?"
$PY - <<'EOF' || { echo "[or] SMOKE FAILED: stop (nothing else runs)"; exit 1; }
import json
from pathlib import Path
O = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/tsmoke/press_count_e30_oracle/on/press_button")
res = sorted(O.glob("seed_*/result.json"))
assert res, "no smoke episode"
d = res[0].parent
job = json.loads((d / "job.json").read_text())
assert job.get("oracle_counts") is True, "job without oracle_counts"
dec = [json.loads(x) for x in (d / "decisions.jsonl").read_text().splitlines() if x.strip()]
bottoms = {tuple(e[:4]) for r in dec for e in r["ledger"] if e[2] == "bottom"}
rows = [json.loads(x) for x in (d / "executed_actions.jsonl").read_text().splitlines() if x.strip()]
regs = [i + 1 for i, r in enumerate(rows) if int((r.get("objects_after") or {}).get("press_cnt_1") or 0)
        > int((r.get("objects_before") or {}).get("press_cnt_1") or 0)]
print(f"[smoke] {len(rows)} targets; button-1 presses registered at {regs}; oracle bottoms {sorted(bottoms)}")
assert regs, "no press of button 1 in 200 targets"
assert all(c - f == 1 for f, _, _, c in bottoms), "a bottom entry not written one frame after its press step"
last = max(r["frame_id"] for r in dec)
assert {c for _, _, _, c in bottoms} >= {f for f in regs if f <= last}, "a registered press is missing from the ledger"
print("[smoke] PASS")
EOF

verdict() {
  $PY scripts/fullft/oracle_verdict.py "$@" 2>&1 | tail -n 6
  $PY scripts/fullft/press_ledger_audit.py tim:press_count_e30_oracle 2>&1 | grep -E "^==|over-pressing|visibility delay|READING" | head -n 6
  $PY scripts/fullft/press_timing_audit.py --describe tim:press_count_e30_oracle --out $F/PRESS_TIMING_AUDIT_oracle.json 2>&1 \
    | grep -E "O1 READING|O5 deciding|O3 chain" | head -n 4
  $HFPY scripts/memory_v2/migrate/relay.py put $F/ORACLE_VERDICT.json --prefix diag/oracle_verdict 2>&1 | tail -n 1
}
echo "[or] $(date '+%F %T') ===== 3 Z0 oracle, scenes 1-50 and 51-100"
run tim press_count_e30_oracle 1 MWAM_LEDGER=oracle
run tim press_count_e30_oracle 51 MWAM_LEDGER=oracle
verdict
echo "[or] $(date '+%F %T') ===== 5 N0 baseline replicate r2, scenes 1-50"
run nz2 press_count_e30 1 MWAM_NOISE_SALT=r2
if grep -q '"ORACLE": "UNCERTAIN"' $F/ORACLE_VERDICT.json; then
  echo "[or] $(date '+%F %T') ===== 6 registered extension: oracle with noise r2, scenes 1-100"
  run tim2 press_count_e30_oracle 1 MWAM_LEDGER=oracle MWAM_NOISE_SALT=r2
  run tim2 press_count_e30_oracle 51 MWAM_LEDGER=oracle MWAM_NOISE_SALT=r2
  verdict --extended
fi
echo "[or] $(date '+%F %T') ===== 7 N0 baseline replicate r3, scenes 1-50"
run nz3 press_count_e30 1 MWAM_NOISE_SALT=r3
$PY scripts/fullft/noise_band.py 2>&1 | tail -n 6
$HFPY scripts/memory_v2/migrate/relay.py put $F/NOISE_BAND.json --prefix diag/noise_band 2>&1 | tail -n 1
echo "[or] $(date '+%F %T') ===== all done"

#!/usr/bin/env bash
# mwam5090 container (plan v10 nodes N8 / G1): closed loop of a fullft export on the official scenes.
#   1 relay get exports/<RUN>_<TAG> from hhyfred/memwam-fullft (once), sha256 check
#   2 smoke: put scene 1, 8 targets (the fullft session loads, decides, logs its history ids)
#   3 put_back 1-N, then swap 1-N (resumable, two passes), 10 steps, execute 8, mode on
#   4 stage table; with N >= 50 the pre-registered G1 verdict (plan v10 F.1 N8):
#        PASS: put success >= 43/50 AND swap success >= 43/50; PARTIAL: both >= 30/50; else FAIL
#        non-degenerate floor: lifted >= 48/50 on both tasks and >= 48/50 episodes finished per task (else no verdict)
#      with N < 50 it is a progress check only (no verdict).
# Usage: docker exec -d -e RUN=ar_2task -e TAG=e10 -e N=20 -e GPU=0 mwam5090 bash .../scripts/fullft/g1_loop.sh
# Optional (11-11, plan v11): TASKS="put_back_block" (one task per GPU, e.g. put on GPU0 and swap on GPU1 in parallel;
# a one-task run prints its table but no verdict), SKIP_SMOKE=1, VERDICT_ONLY=1 (no GPU, no fetch: the stage table and
# the verdict over every episode of this label, after the per-task runs).
# Own log: outputs/memory_v2/report/G1_<RUN>_<TAG>[_<task>|_verdict]_<time>.txt
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
RUN=${RUN:?}; TAG=${TAG:?}; N=${N:-20}; GPU=${GPU:-0}
TASKS=${TASKS:-"put_back_block swap_blocks"}; VERDICT_ONLY=${VERDICT_ONLY:-0}; SKIP_SMOKE=${SKIP_SMOKE:-0}
SUFFIX=""; [ "$(echo $TASKS | wc -w)" -eq 1 ] && SUFFIX="_$TASKS"; [ "$VERDICT_ONLY" = 1 ] && SUFFIX="_verdict"
WANT_VERDICT=0; { [ "$VERDICT_ONLY" = 1 ] || [ "$(echo $TASKS | wc -w)" -ge 2 ]; } && WANT_VERDICT=1
LOG=$O/report/G1_${RUN}_${TAG}${SUFFIX}_$(date +%Y%m%d_%H%M).txt
mkdir -p $O/report
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[g1] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
step() { echo; echo "[g1] $(date '+%F %T') ===== $*"; }
cd $R
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$GPU" | tr -d ' ')
echo "GPU $GPU: $used MiB in use; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60)"
[ "$VERDICT_ONLY" = 1 ] || [ "$used" -lt 2000 ] || { echo "GPU $GPU is not empty: stopping"; exit 1; }
export PYTHONPATH=$R/src CUDA_VISIBLE_DEVICES=$GPU PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
PY=/opt/mwam/bin/python
E=$R/outputs/fullft/exports/${RUN}_${TAG}
CK=$E/export_${TAG}.pt
LABEL=${RUN}_${TAG}
if [ "$VERDICT_ONLY" != 1 ]; then
step "1 export"
if [ ! -f "$CK" ]; then
  /opt/hf-tools/bin/python scripts/memory_v2/migrate/relay.py get --prefix exports/${RUN}_${TAG} --repo hhyfred/memwam-fullft --out $E \
    2>&1 | grep -v "Processing\|Download\|%|" || exit 1
fi
(cd $E && sha256sum -c export_${TAG}.pt.sha256) || { echo "sha256 mismatch: delete $E and rerun"; exit 1; }
if [ "$SKIP_SMOKE" != 1 ]; then
step "2 smoke: put scene 1, 8 targets"
$PY -m fastwam.memory_v2.online run --checkpoint $CK --label ${LABEL}_smoke --scenes $O/closed_loop/scenes_seed42_n100_put_back_block \
  --tasks put_back_block --limit 1 --execute 8 --max-targets 8 --output $O/closed_loop/g1_smoke > $O/closed_loop/g1_smoke_${LABEL}.log 2>&1
echo "smoke exit code $?"; grep -E "decide|done|Error|error" $O/closed_loop/g1_smoke_${LABEL}.log | tail -n 5
fi
for t in $TASKS; do
  step "3 closed loop $t scenes 1-$N"
  for pass in 1 2; do
    $PY -m fastwam.memory_v2.online run --checkpoint $CK --label $LABEL --scenes $O/closed_loop/scenes_seed42_n100_$t \
      --tasks $t --limit $N --execute 8 --output $O/closed_loop/g1 >> $O/closed_loop/g1_${LABEL}.log 2>&1
    echo "pass $pass exit code $?; finished: $(ls $O/closed_loop/g1/$LABEL/on/$t/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json')"
  done
done
fi
step "4 stage table"
$PY scripts/memory_v2/loop_peek.py --folder closed_loop/g1 --label $LABEL --out /dev/null
$PY - "$LABEL" "$N" "$WANT_VERDICT" <<'PYEOF'
import importlib.util, sys
from pathlib import Path
R = Path("/workspace/FastWAM-memory2")
spec = importlib.util.spec_from_file_location("queue5", R / "scripts/memory_v2/queue5.py")
q = importlib.util.module_from_spec(spec); spec.loader.exec_module(q)
label, n, want = sys.argv[1], int(sys.argv[2]), sys.argv[3] == "1"
eps = q.episodes([str(R / "outputs/memory_v2/closed_loop/g1")], label, modes=["on"])
rows = {}
for (task, mode, seed), a in eps.items():
    rows.setdefault(task, []).append(a)
for task, rs in sorted(rows.items()):
    print(f"{task}: finished {len(rs)}, success {sum(bool(a.get('success')) for a in rs)}, lifted "
          f"{sum(bool(a.get('lifted')) for a in rs)}, mean progress {q.mean(q.progress(task, a) for a in rs):.3f}")
if n < 50:
    print(f"G1 progress check (N={n} < 50): no verdict"); raise SystemExit
if not want:
    print("one-task run: no verdict here (run VERDICT_ONLY=1 after both tasks)"); raise SystemExit
put, swap = rows.get("put_back_block", []), rows.get("swap_blocks", [])
floor = all(len(r) >= 48 and sum(bool(a.get("lifted")) for a in r) >= 48 for r in (put, swap))
sp, ss = (sum(bool(a.get("success")) for a in r) for r in (put, swap))
verdict = "NO VERDICT (floor)" if not floor else ("PASS" if sp >= 43 and ss >= 43 else
                                                   "PARTIAL" if sp >= 30 and ss >= 30 else "FAIL")
print(f"G1 VERDICT: {verdict} (put {sp}/50, swap {ss}/50)")
PYEOF

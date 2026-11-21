#!/usr/bin/env bash
# mwam5090, 11-22 (Opus, plan v19 3.2 acceptance before D1 / D2 train). GPU1 only (PF_GPUS, default 1); read-only for
# every existing result. Steps (any failure stops the chain; nothing trains here):
#   1 theta of the in-place repeat count on the 50 press demos (repeat_theta.py): every press pair of every demo right
#   2 bit parity on the CPU: with every new part off, one training update equals commit 5dcb216 (deed_parity_cpu.py)
#   3 two smoke exports from the RELEASED weights (fake_export.py; not models of ours, never compared):
#       d2_smoke   the D2 configuration (press, provisional write, in-place count with theta from 1, record
#                  augmentation, decision weighting, next-event head)
#       d1b_smoke  the D1 arm (b) configuration (three-frame, two tasks, decision weighting + next-event head)
#   4 closed loop, one scene each (press_button scene 1 with d2_smoke, swap_blocks scene 1 with d1b_smoke), 160
#     executed targets: the episode must finish, log >= 10 decisions, and (d2) every logged ledger entry must carry its
#     count (5 fields: frame, arm, kind, confirmed, count)
#   then DEED_SMOKE_OK (or DEED_SMOKE_FAILED) in outputs/fullft with theta; the user pastes the tail, Opus commits the
#   training gate scripts/fullft/GO_deed with theta.
# 11-22 03:15 fix (first run 18:32 container time: the press episode ended in ERROR.json, no decision): the D2 smoke
# export named no data.roots, so the online policy (MWAM_TEXT_SOURCE=cache) could not find the press instruction's
# cached text [inferred from fullft/online.py _cache_text; the ERROR.json is now printed]. The D2 smoke now names the
# press cache (as the real D2 line does) and gets new names (d2_smoke2_th<theta>, label d2_smoke2); the D1 (b) smoke
# uses the two-task cache if this machine has it, else T5 for its instruction. A failed check prints the ERROR.json.
#   docker exec -d -e PF_GPUS=1 mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/deed_smoke_5090.sh
# Own log: outputs/fullft/DEED_SMOKE_5090_<time>.txt
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
O=$R/outputs/memory_v2
LOG=$F/DEED_SMOKE_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
cd $R
rm -f $F/DEED_SMOKE_OK $F/DEED_SMOKE_FAILED
fail() { echo "[deed] $(date '+%F %T') FAILED: $*"; echo "$*" > $F/DEED_SMOKE_FAILED; exit 1; }
trap 'rc=$?; echo "[deed] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
unset MWAM_LEDGER MWAM_NOISE_SALT MWAM_LEDGER_LAG MWAM_EVENT_DELTA MWAM_EVENT_MIN_PATH MWAM_EVENT_PROVISIONAL
PY=/opt/mwam/bin/python
G=${PF_GPUS:-1}
echo "[deed] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-70); GPU $G"
grep -q "repeat_theta" src/fastwam/fullft/history.py || fail "history.py has no repeat_theta (git pull)"

V3C=$F/events/events_press_button_v3c.json
[ -s $V3C ] || V3C=/mnt/hf/relay_mirror/memwam-diag-v1/diag/press_v3c/events_press_button_v3c.json
[ -s $V3C ] || fail "no events_press_button_v3c.json"
EV2="$F/events/events_put_back_block.json,$F/events/events_swap_blocks.json"

echo "[deed] ===== 1 theta (events $V3C)"
$PY scripts/fullft/repeat_theta.py --events $V3C || fail "theta: not every press pair separable (REPEAT_THETA.json)"
TH=$($PY -c "import json; print(round(json.load(open('$F/REPEAT_THETA.json'))['theta'], 4))")
echo "[deed] theta $TH"

echo "[deed] ===== 2 bit parity with the parts off (CPU)"
$PY scripts/fullft/deed_parity_cpu.py || fail "parity"

echo "[deed] ===== 3 smoke exports (released weights + the new parts' zero start)"
D2=$F/exports/d2_smoke2_th$TH/export_e0.pt
D1=$F/exports/d1b_smoke/export_e0.pt
PRESS_ROOT=$O/press/dense_press_button_v1
[ -f $PRESS_ROOT/RECORDS.json ] || fail "no press cache $PRESS_ROOT"
$PY scripts/fullft/fake_export.py --out $D2 --set name=d2_smoke2 "data.roots=[$PRESS_ROOT]" "data.tasks=[press_button]" "data.events=[$V3C]" \
  history.variant=arprop history.event_max=32 history.lag=0 history.ordinal=16 history.event_delta=0.012 \
  history.event_min_path=0.015 history.event_provisional=0.002 history.repeat_theta=$TH history.ledger_drop_p=0.3 \
  history.ledger_over_p=0.3 model.decision_weight=3 model.next_event_loss=0.1 || fail "d2 export"
$PY scripts/fullft/fake_export.py --out $D1 --set name=d1b_smoke "data.events=[$EV2]" model.decision_weight=3 \
  model.next_event_loss=0.1 || fail "d1b export"

empty() { local u; u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 2>/dev/null | tr -d ' '); [[ "$u" =~ ^[0-9]+$ ]] && [ "$u" -lt 2000 ]; }
empty $G || fail "GPU $G is in use: nothing started (rerun when it is free)"

loop() {        # export, label, task, text source
  local bank=$O/closed_loop/scenes_seed42_n100_$3
  [ -e $bank ] || fail "no scene bank $bank"
  echo "[deed] ===== 4 closed loop $2 ($3 scene 1, 160 targets) on GPU $G; text from $4"
  MWAM_TEXT_SOURCE=$4 CUDA_VISIBLE_DEVICES=$G $PY -m fastwam.memory_v2.online run --checkpoint $1 --label $2 --scenes $bank --tasks $3 \
    --execute 8 --max-targets 160 --output $O/closed_loop/dsmoke --limit 1 >> $O/closed_loop/dsmoke_$2.log 2>&1 \
    || fail "$2 closed loop exit code $? (tail of $O/closed_loop/dsmoke_$2.log: $(tail -n 3 $O/closed_loop/dsmoke_$2.log | tr '\n' ' ' | cut -c1-400))"
  $PY - "$O/closed_loop/dsmoke/$2/on/$3" "$2" <<'EOF' || fail "$2 closed-loop check"
import json, sys
from pathlib import Path
root, label = Path(sys.argv[1]), sys.argv[2]
res = sorted(root.glob("seed_*/result.json"))
dec = sorted(root.glob("seed_*/decisions.jsonl")) or sorted(root.glob("**/decisions.jsonl"))
if not res or not dec:
    print(f"[deed] {label}: result.json {len(res)}, decisions.jsonl {len(dec)} under {root}")
    for e in sorted(root.glob("seed_*/ERROR.json")):
        print(f"[deed] {e}: {json.loads(e.read_text()).get('error', '')[-1500:]}")
    sys.exit(1)
rows = [json.loads(x) for x in dec[0].read_text().splitlines() if x.strip()]
entries = [e for r in rows for e in (r.get("ledger") or [])]
ok = len(rows) >= 10
if label.startswith("d2"):
    ok = ok and all(len(e) == 5 for e in entries)
print(f"[deed] {label}: result {json.loads(res[0].read_text()).get('success')}, {len(rows)} decisions, "
      f"{len(entries)} logged ledger entries (last {entries[-1] if entries else None}); {'OK' if ok else 'BAD'}")
sys.exit(0 if ok else 1)
EOF
}
for e in $O/closed_loop/dsmoke/d2_smoke/on/press_button/seed_*/ERROR.json; do      # the first run's error, for the record
  [ -f "$e" ] && echo "[deed] first run's $e: $(cut -c1-1200 "$e")"
done
TWO=/workspace/FastWAM/outputs/s1_dense_joint_h100_v1/RECORDS.json
T1=cache; [ -f $TWO ] && grep -q swap_blocks $TWO || T1=t5
loop $D2 d2_smoke2 press_button cache
loop $D1 d1b_smoke swap_blocks $T1
echo "theta $TH; $(date '+%F %T'); $(git -c safe.directory='*' log --oneline -1 | cut -c1-12)" > $F/DEED_SMOKE_OK
echo "[deed] $(date '+%F %T') DEED SMOKE OK: theta $TH (Opus commits GO_deed with this theta)"

#!/usr/bin/env bash
# mwam5090, 11-13 afternoon: fill both GPUs until the first AR+PROP export (ar2_prop e10, ~11-14 00:50). Descriptive.
#   GPU1: S  ledger smoke: a released-weights export with history.variant=arprop (fake_export.py) through the closed loop,
#            put scene 1 and swap scene 1, 20 decisions each -> the online ledger path (EventDetector, ledger_entries,
#            ledger_tensor, check_ledger_slots) runs end to end before the real ar2_prop e10 arrives. Not a model of ours.
#         O  Obs-AR learning curve: e10 and e20 on observe_and_pickup 1-50 (e30 = W1: 4/50), + the history probe on e30,
#            + the field list of one observe_and_pickup episode row (to write its stage parser = the W1 grasp floor)
#   GPU0: X  N7 e30 on scenes 51-100 of both tasks (same label ar_2task_e30): the AR arm of the registered ledger
#            comparison's 51-100 extension ("between -> extend both arms to 51-100") and the 100-scene official table
# Each lane waits for its GPU to be empty for 90 s. Fixed pipeline: OIDN 2.0.1, text from the training cache.
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/day3b_5090.sh
# Own log: outputs/fullft/DAY3B_5090_<time>.txt
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
LOG=$R/outputs/fullft/DAY3B_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[day3b] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python
EX=$R/outputs/fullft/exports
echo "[day3b] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60)"
empty() { [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 | tr -d ' ')" -lt 2000 ]; }
claim() { until empty $1 && sleep 90 && empty $1; do sleep 120; done; echo "[day3b] $(date '+%F %T') GPU $1 claimed"; }
n_done() { ls $O/closed_loop/$1/$2/on/$3/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json'; }
loop() {    # GPU, checkpoint, label, task, folder, extra args...
  local g=$1 ck=$2 l=$3 t=$4 out=$5; shift 5
  for pass in 1 2; do
    CUDA_VISIBLE_DEVICES=$g $PY -m fastwam.memory_v2.online run --checkpoint $ck --label $l \
      --scenes $O/closed_loop/scenes_seed42_n100_$t --tasks $t --execute 8 --output $O/closed_loop/$out "$@" \
      >> $O/closed_loop/${out}_$l.log 2>&1
    echo "[day3b] $(date '+%F %T') $l $t pass $pass exit code $?; finished $(n_done $out $l $t)"
  done
}
fetch() {   # run tag
  local E=$EX/${1}_$2
  [ -f $E/export_$2.pt ] || $HFPY scripts/memory_v2/migrate/relay.py get --prefix exports/${1}_$2 --repo hhyfred/memwam-fullft \
      --out $E 2>&1 | grep -v "Processing\|Download\|%|"
  (cd $E && sha256sum -c export_$2.pt.sha256)
}
lane1() {
  claim 1
  echo "[day3b] ===== S ledger smoke (released weights, arprop; not a model of ours)"
  SM=$EX/arprop_smoke/export_e0.pt
  [ -f $SM ] || CUDA_VISIBLE_DEVICES=1 $PY scripts/fullft/fake_export.py --out $SM --set history.variant=arprop \
      history.event_max=32 history.lag=4 2>&1 | tail -n 2
  for t in put_back_block swap_blocks; do
    CUDA_VISIBLE_DEVICES=1 $PY -m fastwam.memory_v2.online run --checkpoint $SM --label arprop_smoke \
      --scenes $O/closed_loop/scenes_seed42_n100_$t --tasks $t --limit 1 --execute 8 --max-targets 160 \
      --output $O/closed_loop/g1_smoke > $O/closed_loop/g1_smoke_arprop_$t.log 2>&1
    echo "[day3b] smoke $t exit code $?; errors: $(grep -c 'ERROR\|Traceback' $O/closed_loop/g1_smoke_arprop_$t.log)"
  done
  $PY - <<'PYSM'
import json
from pathlib import Path
root = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/g1_smoke/arprop_smoke/on")
for d in sorted(root.glob("*/seed_*")):
    rows = [json.loads(s) for s in (d / "decisions.jsonl").read_text().splitlines() if s.strip()] if (d / "decisions.jsonl").exists() else []
    led = [r.get("ledger") for r in rows]
    print(f"  smoke {d.parent.name}: decisions {len(rows)}, rows with a ledger entry {sum(bool(x) for x in led)}, "
          f"max entries {max([len(x or []) for x in led] or [0])}, ERROR.json {(d / 'ERROR.json').exists()}, "
          f"last ledger {led[-1] if led else None}")
print("LEDGER SMOKE: the closed loop ran the arprop path" if any(root.glob("*/seed_*/decisions.jsonl")) else "LEDGER SMOKE: NO decisions")
PYSM
  for tag in e10 e20; do
    echo "[day3b] ===== O obs_ar $tag on observe_and_pickup 1-50"
    fetch obs_ar $tag || { echo "obs_ar $tag export missing or sha256 mismatch: skipped"; continue; }
    loop 1 $EX/obs_ar_$tag/export_$tag.pt obs_ar_$tag observe_and_pickup w1 --limit 50
  done
  $PY - <<'PYOBS'
import json
from pathlib import Path
for tag in ("e10", "e20", "e30"):
    d = Path(f"/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/w1/obs_ar_{tag}/on/observe_and_pickup")
    res = [json.loads(p.read_text()) for p in sorted(d.glob("seed_*/result.json")) if p.parent.name[5:].isdigit()]
    print(f"  obs_ar {tag}: finished {len(res)}, success {sum(bool(r.get('success')) for r in res)}")
row = next(Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/w1/obs_ar_e30/on/observe_and_pickup").glob("seed_*/executed_actions.jsonl"))
first = json.loads(row.read_text().splitlines()[0])
def shape(v, depth=0):
    if isinstance(v, dict):
        return "{" + ", ".join(f"{k}: {shape(x, depth + 1)}" for k, x in list(v.items())[:12]) + "}" if depth < 3 else "{...}"
    if isinstance(v, list):
        return f"list[{len(v)}]" + (f" of {shape(v[0], depth + 1)}" if v and depth < 3 else "")
    return type(v).__name__
print("  obs executed_actions row fields:", shape(first)[:1500])
PYOBS
  echo "[day3b] ===== history probe on obs_ar e30"
  until empty 1; do sleep 60; done
  CUDA_VISIBLE_DEVICES=1 $PY scripts/fullft/hist_probe.py --export $EX/obs_ar_e30/export_e30.pt 2>&1 | grep -vi warn | grep -vE "^  [0-9]+/[0-9]+$" | tail -n 4
}
lane0() {
  claim 0
  CK=$EX/ar_2task_e30/export_e30.pt
  echo "[day3b] ===== X N7 e30 on scenes 51-100"
  loop 0 $CK ar_2task_e30 swap_blocks g1 --from-scene 51 --limit 50
  loop 0 $CK ar_2task_e30 put_back_block g1 --from-scene 51 --limit 50
  $PY scripts/memory_v2/loop_peek.py --folder closed_loop/g1 --label ar_2task_e30 --out /dev/null 2>/dev/null | grep -E "/on |n=" | head -n 4
}
lane1 & P1=$!
lane0 & P0=$!
wait $P1 $P0     # never a bare `wait` after `exec > >(tee)`

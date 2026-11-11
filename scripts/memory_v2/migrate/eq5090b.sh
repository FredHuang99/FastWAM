#!/usr/bin/env bash
# mwam5090 container (11-11, plan v10 node N1): is the 5090 closed loop equivalent to the A100 now that the simulator
# loads Open Image Denoise 2.3.3 (online.py apply_denoiser_fix; render 0.49 levels from the A100)?
#   1 relay get diag/a100_x7_stages (the A100's per-scene stages of X7's official episodes, export_stages.py)
#   2 first decision of put_back seed 4300030 vs the A100's first 8 targets (lag 0..3 arm RMSE)
#   3 X7 on, 10 steps, execute 8, official scenes: put_back 1-20, swap 1-20 (resumable, two passes)
#   4 stage tables and the PAIRED progress difference 5090 - A100 on the same scenes
# Pre-registered (plan v10 F.1 N1, written before the run):
#   equivalent  = per task |mean paired progress difference| <= 0.05 with its 95 % CI containing 0, AND put lifted
#                 >= 18/20, AND swap step 1 >= 18/20
#   first-decision check: lag-0 arm RMSE <= 0.01 (11-11 before the fix: 0.040 at lag 0, 0.0054 at lag 2)
#   non-degenerate floor: the A100 reference has lifted >= 18/20 on these put scenes and s1 >= 18/20 on these swap
#   scenes (otherwise no verdict); a scene missing on either side is dropped from the pairing (reported)
#   equivalent -> the 5090 runs verdict-bearing closed loops (evaluation farm); otherwise -> no verdicts on the 5090,
#   paired table goes to the autopsy, evaluation stays on the A100 / H200
# GPU ${GPU:-0} only, must be empty. Own log: report/EQ5090B_<time>.txt
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/memory_v2/migrate/eq5090b.sh     (about 2-3 h)
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
LOG=$O/report/EQ5090B_$(date +%Y%m%d_%H%M).txt
mkdir -p "$O/report" "$O/closed_loop"
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[eq5090b] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
step() { echo; echo "[eq5090b] $(date '+%F %T') ===== $*"; }
cd "$R"
GPU=${GPU:-0}
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$GPU" | tr -d ' ')
echo "GPU $GPU: $used MiB in use; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60)"
[ "$used" -lt 2000 ] || { echo "GPU $GPU is not empty: stopping"; exit 1; }
[ -e /opt/oidn-2.3.3/lib/libOpenImageDenoise.so.2 ] || { echo "OIDN 2.3.3 missing: run migrate/oidn_fix.sh first"; exit 1; }
export PYTHONPATH=$R/src CUDA_VISIBLE_DEVICES=$GPU PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
PY=/opt/mwam/bin/python
CK=$O/a2C_6ep/checkpoints/update_004020.pt
REF=$O/closed_loop/check_from_a100/x7_official_stages.json

step "1 relay get the A100's per-scene stages"
/opt/hf-tools/bin/python scripts/memory_v2/migrate/relay.py get --prefix diag/a100_x7_stages --out $O/closed_loop/check_from_a100 \
  || echo "relay get failed: the paired comparison will be skipped (run export_stages.py on the A100 first)"

step "2 first decision of put_back seed 4300030"
FIRST=$O/closed_loop/eq5090b_first
$PY -m fastwam.memory_v2.online run --checkpoint $CK --label x7_first_oidn --scenes $O/closed_loop/scenes_seed42_n100_put_back_block \
  --tasks put_back_block --seeds put_back_block:4300030 --execute 8 --max-targets 8 --output $FIRST > $FIRST.log 2>&1
echo "run exit code $?; denoiser line: $(grep -m1 'Open Image Denoise' $FIRST.log)"
echo "OIDN errors in the simulator log: $(grep -rc 'OIDN Error' $FIRST $FIRST.log 2>/dev/null | awk -F: '{s+=$NF} END {print s+0}')"
$PY - <<'EOF'
import json, numpy as np
from pathlib import Path
O = Path("/workspace/FastWAM-memory2/outputs/memory_v2")
ref = json.loads(Path("/workspace/FastWAM-memory2/scripts/memory_v2/migrate/ref_a100_put_4300030.json").read_text())["targets"]
rows = [json.loads(l)["target"] for l in next((O / "closed_loop/eq5090b_first").glob("*/*/put_back_block/seed_4300030/executed_actions.jsonl")).read_text().splitlines()[:8]]
ARM = list(range(6)) + list(range(7, 13))
for s in range(4):
    n = min(len(ref), len(rows)) - s
    d = (np.asarray(ref[:n]) - np.asarray(rows[s:s + n]))[:, ARM]
    print(f"  lag {s}: arm RMSE {float(np.sqrt((d ** 2).mean())):.4f}")
EOF

run_bank() {   # task, first N scenes
  step "3 closed loop $1: X7 on, 10 steps, execute 8, official scenes 1-$2"
  for pass in 1 2; do
    $PY -m fastwam.memory_v2.online run --checkpoint $CK --label x7_eq5090b --scenes $O/closed_loop/scenes_seed42_n100_$1 \
      --tasks "$1" --limit "$2" --execute 8 --output $O/closed_loop/eq5090b >> $O/closed_loop/eq5090b_run.log 2>&1
    echo "pass $pass exit code $?; finished: $(ls $O/closed_loop/eq5090b/x7_eq5090b/on/$1/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json')"
  done
}
run_bank put_back_block 20
run_bank swap_blocks 20
echo "OIDN errors in the run log: $(grep -c 'OIDN Error' $O/closed_loop/eq5090b_run.log)"

step "4 stage tables and the paired comparison"
$PY scripts/memory_v2/loop_peek.py --folder closed_loop/eq5090b --label x7_eq5090b --out /dev/null
$PY - <<'EOF'
import importlib.util, json
from pathlib import Path
R = Path("/workspace/FastWAM-memory2")
spec = importlib.util.spec_from_file_location("queue5", R / "scripts/memory_v2/queue5.py")
q = importlib.util.module_from_spec(spec); spec.loader.exec_module(q)
ref_path = R / "outputs/memory_v2/closed_loop/check_from_a100/x7_official_stages.json"
eps = q.episodes([str(R / "outputs/memory_v2/closed_loop/eq5090b")], "x7_eq5090b", modes=["on"])
mine = {}
for (task, mode, seed), a in eps.items():
    mine.setdefault(task, {})[str(seed)] = a
if not ref_path.exists():
    print("no A100 export: paired comparison skipped; verdict pending"); raise SystemExit
ref = json.loads(ref_path.read_text())["episodes"]
verdict = True
for task, key, floor in (("put_back_block", "lifted", 18), ("swap_blocks", "s1", 18)):
    m, r = mine.get(task, {}), ref.get(task, {})
    seeds = sorted(set(m) & set(r), key=int)
    diffs = [q.progress(task, m[s]) - r[s]["progress"] for s in seeds]
    ci = q.bootstrap_ci(diffs) if diffs else [None, None]
    mine_n = sum(bool(m[s].get(key)) for s in seeds)
    ref_n = sum(bool(r[s].get(key)) for s in seeds)
    delta = q.mean(diffs) if diffs else float("nan")
    ok_floor = ref_n >= floor
    ok = bool(diffs) and abs(delta) <= 0.05 and ci[0] <= 0 <= ci[1] and mine_n >= floor
    verdict = verdict and ok and ok_floor
    print(f"{task}: 5090 scenes {len(m)}, A100 scenes {len(r)}, paired n={len(seeds)}; progress 5090 {q.mean(q.progress(task, m[s]) for s in seeds):.3f} vs A100 "
          f"{q.mean(r[s]['progress'] for s in seeds):.3f}; delta {delta:+.3f} CI [{ci[0]:+.3f}, {ci[1]:+.3f}]; "
          f"{key}: 5090 {mine_n}/{len(seeds)}, A100 {ref_n}/{len(seeds)}; success 5090 "
          f"{sum(bool(m[s].get('success')) for s in seeds)} vs A100 {sum(bool(r[s].get('success')) for s in seeds)}; "
          f"{'floor ok' if ok_floor else 'FLOOR NOT MET (no verdict)'}; {'equivalent' if ok else 'NOT equivalent'}")
print("EQ5090B VERDICT:", "EQUIVALENT" if verdict else "NOT EQUIVALENT (or no verdict)")
EOF

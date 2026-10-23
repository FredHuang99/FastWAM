#!/usr/bin/env bash
# Simulator readiness on this A100, end to end, BEFORE any long job:
#   1. embodiment configs: regenerate assets/embodiments/**/<name>.yml from <name>_tmp.yml with ASSETS_PATH = this
#      checkout (the official scripts/update_embodiment_config_path.py step, never run here: the configs still point
#      to the dataset author's /home/ubuntu/Desktop/RoboHorizon). Overwritten files are backed up first.
#   2. sapien / mplib source patches of the official RMBench install (_install.sh): check, apply if missing (backup).
#   3. other absolute foreign paths anywhere in the evaluation folders (report).
#   4. REAL gate: one complete expert episode per task through the production planner (setup_demo + play_once with
#      CuRobo, rendering, instruction freeze) in a scratch folder.
# Only if every step passes: prints READY and starts the full scene-bank planning (seed 17, 10 per task) in the
# background on the same GPU. Otherwise prints NOT READY with the failing log tail; nothing long is started.
#   bash /workspace/FastWAM-memory2/scripts/memory_v2/sim/sim_ready.sh <container GPU index, default 0>
set -u
G=${1:-0}
R=/workspace/FastWAM/resources/RMBench
SPY=/opt/rmbench-fused-env/bin/python
PY=/opt/mwam/bin/python
CL=/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop
STAMP=$(date -u +%Y%m%d_%H%M%S)
BK=$CL/rmbench_backup/$STAMP
mkdir -p $CL/logs
FAIL=0
echo "== simulator readiness $STAMP UTC  GPU $G  checkout $R"

echo "-- 1. embodiment configs"
$PY - "$R" "$BK" <<'PY' || FAIL=1
import re, shutil, sys
from pathlib import Path
R, BK = Path(sys.argv[1]), Path(sys.argv[2])
emb = R / "assets/embodiments"

def foreign(text):
    return sorted({m for m in re.findall(r"(/[A-Za-z0-9_.\-/]+?)/assets/", text) if m != str(R)})

def scan():
    bad = {}
    for p in sorted(emb.rglob("*.yml")):
        if not p.name.endswith("_tmp.yml"):
            f = foreign(p.read_text(errors="replace"))
            if f:
                bad[str(p.relative_to(R))] = f
    return bad

before = scan()
print(f"   before: {len(before)} config files point outside the checkout: {sorted({x for v in before.values() for x in v})}")
templates = sorted(emb.rglob("*_tmp.yml"))
changed = 0
for t in templates:
    target = t.with_name(t.name[:-len("_tmp.yml")] + ".yml")
    new = t.read_text().replace("${ASSETS_PATH}", str(R)).replace("$ASSETS_PATH", str(R))
    if target.exists() and target.read_text() == new:
        continue
    if target.exists():
        backup = BK / target.relative_to(R)
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, backup)
    target.write_text(new)
    changed += 1
print(f"   templates *_tmp.yml: {len(templates)}; regenerated {changed} configs with ASSETS_PATH={R} (backups: {BK})")
after = scan()
if after:                      # configs without a template: rewrite the foreign prefix the same way (backup first)
    for rel, prefixes in after.items():
        p = R / rel
        backup = BK / rel
        if not backup.exists():
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, backup)
        text = p.read_text()
        for prefix in prefixes:
            text = text.replace(prefix + "/assets/", str(R) + "/assets/")
        p.write_text(text)
    print(f"   rewrote the foreign prefix in {len(after)} configs without a template")
    after = scan()
for k, v in list(after.items())[:10]:
    print(f"     ! still foreign: {k}: {v}")
missing = []
for p in sorted(emb.rglob("*.yml")):
    if not p.name.endswith("_tmp.yml"):
        for ref in re.findall(r"(%s/[^\s'\",\]]+)" % re.escape(str(R)), p.read_text(errors="replace")):
            if not Path(ref).exists():
                missing.append(f"{p.relative_to(R)} -> {ref}")
for m in missing[:10]:
    print(f"     ! referenced file missing: {m}")
print(f"   after: foreign={len(after)} missing_references={len(missing)}")
sys.exit(1 if after or missing else 0)
PY

echo "-- 2. sapien / mplib patches of the official RMBench install"
SAP=$(env -u PYTHONPATH $SPY -c "import sapien, os; print(os.path.dirname(sapien.__file__))" 2>/dev/null)
MPL=$(env -u PYTHONPATH $SPY -c "import mplib, os; print(os.path.dirname(mplib.__file__))" 2>/dev/null)
U=$SAP/wrapper/urdf_loader.py; P=$MPL/planner.py
if grep -qE '"r"\) as f' $U; then
  mkdir -p $BK/site-packages/sapien/wrapper && cp -p $U $BK/site-packages/sapien/wrapper/
  sed -i -E 's/("r")(\))( as)/\1, encoding="utf-8") as/g' $U && echo "   sapien urdf_loader: utf-8 patch APPLIED (backup in $BK)"
else
  echo "   sapien urdf_loader: utf-8 patch already present"
fi
if grep -q 'or collide or not within_joint_limit' $P; then
  mkdir -p $BK/site-packages/mplib && cp -p $P $BK/site-packages/mplib/
  sed -i -E 's/(if np.linalg.norm\(delta_twist\) < 1e-4 )(or collide )(or not within_joint_limit:)/\1\3/g' $P \
    && echo "   mplib planner: screw-plan collision patch APPLIED (backup in $BK)"
else
  echo "   mplib planner: screw-plan patch already present ($(grep -c 'within_joint_limit' $P) occurrences of within_joint_limit)"
fi

echo "-- 3. foreign absolute paths elsewhere in the evaluation folders (report only)"
grep -rIl --include=*.yml --include=*.yaml --include=*.json --include=*.py -e '/home/ubuntu/' -e 'RoboHorizon' \
  $R/env_cfg $R/envs $R/scripts $R/description 2>/dev/null | head -20 | sed 's/^/   ? /'

echo "-- 4. gate: one complete expert episode per task (production planner, scratch folder)"
T=$CL/sim_ready_test_$STAMP
mkdir -p $T
cd /workspace/FastWAM-memory2
export PYTHONPATH=/workspace/FastWAM-memory2/src OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 CUDA_VISIBLE_DEVICES=$G
if [ $FAIL = 0 ]; then
  for task in put_back_block swap_blocks; do
    start=$(date +%s)
    timeout 2400 $PY -m fastwam.memory_v2.online plan --tasks $task --seed 17 --episodes 1 --output $T > $T/$task.log 2>&1
    rc=$?
    echo "   $task: exit $rc after $(( $(date +%s) - start )) s   (log $T/$task.log)"
    grep -E '\[scene-plan\]|\[plan\].*complete' $T/$task.log | tail -n 3 | sed 's/^/     /'
    if [ $rc != 0 ]; then
      FAIL=1
      echo "   --- last lines of the failing log:"
      grep -v -E 'UserWarning|warn\(' $T/$task.log | tail -n 25 | sed 's/^/     /'
      break
    fi
  done
else
  echo "   skipped (step 1 failed)"
fi
nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader | sed 's/^/   GPU /'

if [ $FAIL = 0 ]; then
  echo "READY"
  LOG=$CL/logs/plan_seed17_n10.log
  nohup bash /workspace/FastWAM-memory2/scripts/memory_v2/jobs/closed_loop.sh plan $G 17 10 > $LOG 2>&1 &
  echo "full scene-bank planning started in the background (pid $!): tail -f $LOG"
else
  echo "NOT READY"
fi

#!/bin/bash
# NTU GaaS login node, 11-22 (Opus; user 13:16: a finished run's resume.pt goes once its exports are uploaded). The home
# was full (932 GB, 0 free) and every job died at 05:21. Removes, and lists what it removes:
#   * <run>/resume.pt of a FINISHED run (SUMMARY.json) whose last export is on the relay (.relayed_e30 or .relayed_final)
#   * ar_2task/resume.pt once ar2_long has SUMMARY.json (on this machine it was only the seed of ar2_long, joined from
#     the old H200's parts; the original stays on the old H200)
#   * <run>/resume.pt.partial (an unfinished copy written when the disk filled; never read)
#   * <run>/export_<tag>.pt with .relayed_<tag> whose size equals the relay's listing (user 13:19: exports may go once
#     uploaded; the .sha256 stays). An export without the marker or with another size on the relay stays.
# Everything else stays and is listed with the reason. Refuses while any job of ours is queued or running (a trainer
# could be writing). Dry run unless --yes.
#   cd ~/mwam/FastWAM-memory2 && bash scripts/gaas/clean_finished.sh [--yes]
set -u
R=$HOME/mwam/FastWAM-memory2
F=$R/outputs/fullft
YES=0; [ "${1:-}" = --yes ] && YES=1
live=$(qstat -u "$(id -un)" 2>/dev/null | awk 'NR > 5 && ($10 == "Q" || $10 == "R" || $10 == "H")' | wc -l)
[ "$live" -gt 0 ] && { echo "[clean] $live job(s) of ours queued or running: nothing removed"; exit 1; }
echo "[clean] $(date '+%F %T') home before: $(df -h $HOME | tail -n 1 | awk '{print $3" used, "$4" free"}'); $([ $YES = 1 ] && echo REMOVING || echo 'dry run (add --yes)')"
gone() { local f=$1 why=$2; echo "  remove $(du -sh "$f" | cut -f1)  $f  ($why)"; [ $YES = 1 ] && rm -f "$f"; }
for f in $F/*/resume.pt; do
  [ -f "$f" ] || continue
  d=$(dirname "$f"); run=$(basename "$d")
  if [ "$run" = ar_2task ] && [ -f $F/ar2_long/SUMMARY.json ]; then gone "$f" "seed of ar2_long, which finished"; continue; fi
  if [ -f $d/SUMMARY.json ] && { [ -f $d/.relayed_e30 ] || [ -f $d/.relayed_final ]; }; then
    gone "$f" "finished; $(ls $d/.relayed_* | xargs -n1 basename | tr '\n' ' ')"
  elif [ -f $d/SUMMARY.json ]; then echo "  keep   $f  (finished, but no .relayed_e30 / .relayed_final)"
  else echo "  keep   $f  (not finished: needed to resume)"; fi
done
for f in $F/*/*.partial; do [ -f "$f" ] && gone "$f" "unfinished copy from the full disk"; done
HFPY=$HOME/mwam/envs/hf-tools/bin/python
for f in $F/*/export_e*.pt; do
  [ -f "$f" ] || continue
  d=$(dirname "$f"); run=$(basename "$d"); tag=$(basename "$f" .pt); tag=${tag#export_}
  [ -f $d/.relayed_$tag ] || { echo "  keep   $f  (no .relayed_$tag)"; continue; }
  got=$(cd $R && $HFPY scripts/memory_v2/migrate/relay.py ls --prefix exports/${run}_$tag --repo hhyfred/memwam-fullft 2>/dev/null \
        | awk -v n="export_$tag.pt" '$1 == n {print $2}')
  if [ -n "$got" ] && [ "$got" = "$(stat -c %s "$f")" ]; then gone "$f" "on the relay, same size"
  else echo "  keep   $f  (relay size '${got:-none}' vs local $(stat -c %s "$f"))"; fi
done
[ $YES = 1 ] && echo "[clean] home after: $(df -h $HOME | tail -n 1 | awk '{print $3" used, "$4" free"}')"

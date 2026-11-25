#!/usr/bin/env bash
# 11-26 02:20 (Opus; user 02:17 "同意你的做法"). Exit 0 if a run's LAST export is on the relay: .relayed_final exists, or
# the highest N among the run's export_eN.pt files and .relayed_eN markers has its .relayed_eN marker. Before this, only
# .relayed_e30 counted, so a run whose last export is e45 / e60 (swapT_long) kept its 72 GB resume.pt for good; with
# export_final.pt never relayed or removed (12 GB per finished run), the home filled on 11-25 ~20:54.
#   bash scripts/gaas/last_export_relayed.sh <run dir>
d=${1:?run dir}
[ -f "$d/.relayed_final" ] && exit 0
last=$(ls "$d"/export_e*.pt "$d"/.relayed_e* 2>/dev/null | sed -n 's#.*_e\([0-9][0-9]*\)\(\.pt\)\{0,1\}$#\1#p' | sort -n | tail -n 1)
[ -n "$last" ] && [ -f "$d/.relayed_e$last" ]

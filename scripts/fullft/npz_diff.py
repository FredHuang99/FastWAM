"""Plan v12 AL2 at zero GPU cost: compare saved frame-0 renders (render_check.py pictures: one npz per variant, the
three cameras head / left / right as arr_0..arr_2) from different machines and denoiser versions.
  /opt/mwam/bin/python scripts/fullft/npz_diff.py --ref a100_oidn201=PATH --ref a100_oidn233=PATH \
      --glob 'outputs/memory_v2/report/render_check_*/default.npz'
Prints mean |diff| (levels) / % pixels > 8 / max per camera and their mean, for every globbed file vs every --ref and
the refs against each other. Readings (AL2, written in plan v12 F.1): (a) the same input through two denoiser versions
>= 0.25 levels -> the denoiser version is the main source; (b) two machines with the SAME denoiser version: <= 0.05 ->
the path tracing before the denoiser is the same on both machines.
"""
import argparse
import glob
from pathlib import Path

import numpy as np


def load(path):
    z = np.load(path)
    return [z[k] for k in sorted(z.files, key=lambda k: int(k.split("_")[1]))]


def diff(a, b):
    cells = []
    for x, y in zip(a, b):
        if x.shape != y.shape:
            return f"shape {x.shape} vs {y.shape}"
        d = np.abs(x.astype(np.int16) - y.astype(np.int16))
        cells.append((float(d.mean()), float((d > 8).mean() * 100), int(d.max())))
    m = sum(c[0] for c in cells) / len(cells)
    o = sum(c[1] for c in cells) / len(cells)
    return " | ".join(f"{c[0]:.2f} / {c[1]:.2f} % / {c[2]}" for c in cells) + f" | mean {m:.3f} / {o:.2f} %"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref", action="append", default=[], help="name=path")
    ap.add_argument("--glob", default="")
    args = ap.parse_args()
    refs = [(x.split("=", 1)[0], load(x.split("=", 1)[1])) for x in args.ref]
    print("| A | B | head | left | right | mean |")
    for i in range(len(refs)):
        for j in range(i + 1, len(refs)):
            print(f"| {refs[i][0]} | {refs[j][0]} | {diff(refs[i][1], refs[j][1])} |")
    for f in sorted(glob.glob(args.glob)) if args.glob else []:
        img = load(f)
        for name, r in refs:
            print(f"| {Path(f).parent.name}/{Path(f).name} | {name} | {diff(img, r)} |")


if __name__ == "__main__":
    main()

"""Inference-only copy of a memory_v2 training checkpoint (drops the optimizer state, loss history and RNG).

The closed loop reads only update / memory / action / config / backend, so the slim file behaves identically there
(12 GB -> ~4 GB for an A2C checkpoint). The source file is not touched.

    /opt/mwam/bin/python scripts/memory_v2/slim_checkpoint.py <in.pt> <out.pt>
"""
import sys

import torch

KEEP = ("update", "memory", "action", "config", "backend")


def main():
    src, dst = sys.argv[1], sys.argv[2]
    state = torch.load(src, map_location="cpu", weights_only=False, mmap=True)
    slim = {k: state[k] for k in KEEP if k in state}
    slim["slimmed_from"] = src
    torch.save(slim, dst)
    back = torch.load(dst, map_location="cpu", weights_only=False)
    for part in ("memory", "action"):
        a, b = state.get(part), back.get(part)
        if a is None:
            assert b is None, part
            continue
        assert a.keys() == b.keys(), part
        assert all(torch.equal(a[k], b[k]) for k in a), part
    print(f"wrote {dst}: keys {sorted(slim)}; memory {len(slim['memory'])} tensors, "
          f"action {0 if slim.get('action') is None else len(slim['action'])} tensors; verified equal")


if __name__ == "__main__":
    main()

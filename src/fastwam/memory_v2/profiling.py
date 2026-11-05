"""Optional wall-clock profile of a training update (plan v7, P0: where do the 45 s / update go?).

Off unless MEMV2_PROFILE=1. When on, every section synchronises CUDA on entry and exit, so the times are real GPU
times (and the run is a little slower than an unprofiled one). Sections nest; a nested section's time is also
counted in its parent. Usage:

    from .profiling import PROFILE
    with PROFILE.section("batch"):
        ...
    PROFILE.step_done()            # once per update; the first `warmup` updates are discarded
    PROFILE.summary()              # {section: {mean_s, total_s, calls_per_update}}
"""
from __future__ import annotations

import os
import time
from collections import defaultdict
from contextlib import contextmanager


class StepProfiler:
    def __init__(self, enabled: bool = False, warmup: int = 1):
        self.enabled = bool(enabled)
        self.warmup = int(warmup)
        self.reset()

    def reset(self):
        self.steps = 0
        self.kept = 0
        self.total = defaultdict(float)
        self.calls = defaultdict(int)
        self._current = defaultdict(float)
        self._current_calls = defaultdict(int)
        self._stack = []

    @staticmethod
    def _sync():
        try:
            import torch
            if torch.cuda.is_available() and torch.cuda.is_initialized():
                torch.cuda.synchronize()
        except Exception:                      # profiling must never break training
            pass

    @contextmanager
    def section(self, name: str):
        if not self.enabled:
            yield
            return
        self._sync()
        full = "/".join(self._stack + [name])
        self._stack.append(name)
        start = time.perf_counter()
        try:
            yield
        finally:
            self._sync()
            self._current[full] += time.perf_counter() - start
            self._current_calls[full] += 1
            self._stack.pop()

    def step_done(self):
        if not self.enabled:
            return
        self.steps += 1
        if self.steps > self.warmup:
            self.kept += 1
            for k, v in self._current.items():
                self.total[k] += v
            for k, v in self._current_calls.items():
                self.calls[k] += v
        self._current = defaultdict(float)
        self._current_calls = defaultdict(int)

    def summary(self) -> dict:
        n = max(1, self.kept)
        return {k: {"mean_s": round(self.total[k] / n, 4), "total_s": round(self.total[k], 3),
                    "calls_per_update": round(self.calls[k] / n, 2)}
                for k in sorted(self.total, key=lambda k: (k.count("/"), -self.total[k]))}

    def table(self) -> str:
        s = self.summary()
        step = s.get("update", {}).get("mean_s")
        lines = [f"profile over {self.kept} updates (after {self.warmup} warm-up)",
                 "| section | s / update | share of update | calls / update |", "|---|---|---|---|"]
        for k, v in s.items():
            share = f"{v['mean_s'] / step:.1%}" if step else "-"
            lines.append(f"| {k} | {v['mean_s']:.3f} | {share} | {v['calls_per_update']} |")
        return "\n".join(lines)


PROFILE = StepProfiler(enabled=os.environ.get("MEMV2_PROFILE", "") not in ("", "0"),
                       warmup=int(os.environ.get("MEMV2_PROFILE_WARMUP", "1")))

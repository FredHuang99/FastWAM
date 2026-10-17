"""memory_v2: read-time-selection history memory for FastWAM (no learnable-query bottleneck).

Import submodules explicitly; this package does not import torch at import time so
that `fastwam.memory_v2.analysis` and `fastwam.memory_v2.config` work without it.
"""

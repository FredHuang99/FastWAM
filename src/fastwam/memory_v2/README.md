# memory_v2 — read-time-selection memory ("Memory Must Speak First")

`memory_s1` is untouched (Codex identity hashes depend on it). Everything new lives here,
in `configs/memory_v2/` and `scripts/memory_v2/`.

## Why a v2

| memory_s1 finding | memory_v2 response |
|---|---|
| 32 learnable queries `U` (RMS 0.02) + broadcast context (RMS 0.96) → slots identical (cos > 0.9995), self-attention shrinks the remaining 2 % to 0.2 % | **No query bottleneck.** The 32 action tokens of each injected ActionDiT layer are the queries; what is read depends on the noisy action, the noise level and the layer |
| Injector attention over identical slots is uniform → q/k gradients ≈ 0, memory = one bias vector | Memory tokens keep per-patch detail of every selected frame (optional pooling) |
| Current frame inside the history → reader can lower the loss without the past | Current frame excluded by default (it already reaches ActionDiT through its 30-layer KV) |
| Gate 1e-3 shrinks every gradient into the reader by 1000× | Zero-initialised output projection: exact base reproduction at init, full-size gradients after the first step |
| Bell weight is 0 at τ = 1, < 10 % of the weight mass above τ = 0.8 with uniform τ; inference commits in the first steps from τ = 1 | `mixture` τ sampling + `bell_floor` weight + unit-weight τ = 1 endpoint term |
| No way to ask "how much does memory matter here" | Memory dropout trains a learned **null-memory** branch → classifier-free memory guidance at high noise; learned **τ-gate** g_l(τ) as a read-out |
| Temporal order not guaranteed | Relative-age + absolute-index sinusoid per frame, role embedding (anchor/landmark/recent) |

## Modules

* `config.py` — `HistoryPolicyConfig`, `MemoryV2Config`, `ObjectiveConfig`, `GuidanceConfig`, `V2Config.from_dict`.
* `history.py` — `select_history` (single source of truth offline/online), `EpisodeArchive` (append-only, per env slot, idempotent, signature-bound), `collate_history`.
* `modules.py` — `MemoryTokenizer`, `ReadTimeInjector`, `TauGate`, `MemoryV2Modules`.
* `model.py` — `MemoryV2Model` over an adapter protocol (`encode / prepare / block / post`), `FastWAMActionAdapter` for the released frozen MoT; `sample` with memory CFG and x0 traces.
* `objectives.py` — τ samplers, released bell weight (verified against the scheduler), `compute_loss` (FM + endpoint + memory dropout), `paired_endpoint_loss` (for blueprint-S2 pairs), identifiability d(τ) and τ_c.
* `metrics.py` — `history_sensitivity` (null / shuffled time / swapped history vs τ), `attention_report`, `token_geometry`, `branch_commitment`, `gate_profile`.
* `analysis.py` — NumPy-only: objective mass above τ, near-present branch distances from demos, slot-collapse simulation.

## Tests

```bash
python -m pytest src/fastwam/memory_v2/tests -q          # CPU, tiny backbone, < 1 min
python scripts/memory_v2/check_adapter_parity.py --config configs/memory_s1/s1_variable_t_h100.yaml \
    --output outputs/memory_v2/checks/adapter_parity.json   # GPU, released weights + dense cache
python scripts/memory_v2/slot_collapse.py                 # NumPy only
python scripts/memory_v2/tau_crossover.py --config configs/memory_s1/s1_variable_t_h100.yaml \
    --stage 0.35 1.0 --output outputs/memory_v2/analysis/tau_crossover.json
```

The torch tests were written without a torch runtime in the authoring sandbox; run them on
the training container before anything else. `test_history.py` was executed (7/7 pass).

## train_v2 (dense-joint data, branch-A layout)

Evidence that set the defaults (A335 audit, 2026-10-18):

* A335 offline arm RMSE is ~3x the C+256 source on every task/split, **including the
  train split** (put/train 0.050 -> 0.158 rad), and FM error is 3-7x higher at every tau.
* A's own training loss rose from median 0.015 (update 1) to ~0.06-0.08 in lock-step with
  the LR warm-up (Spearman 0.74 during warm-up; sustained >1.5x from update 42, LR 5e-5).
  `python scripts/memory_v2/loss_vs_lr.py --updates <run>/history --output loss_vs_lr.json --plot loss_vs_lr.png`
  => optimisation failure of fresh AdamW at peak 1e-4 on an already-converged ActionDiT,
  not over-fitting and not the last 8 updates.

Hence:

* start from **C+256 (`init_checkpoint: source`)**, not A335;
* ActionDiT/Video DiT/proprio **frozen**; only memory_v2 trains (zero-init output:
  INIT_PARITY.json checks memory on == null == off exactly before update 1);
* ActionDiT co-training is opt-in (`optim.lr_action`), refused above 2e-5 without
  `--allow-high-action-lr`;
* guards: training FM loss > 2x its initial median, or memory-on offline arm RMSE
  > 1.1x memory-off => save + GUARD.json + stop.

```bash
cd /workspace/FastWAM && git switch memory2
export PYTHONPATH=/workspace/FastWAM/src
PY=/opt/mwam/bin/python
$PY -m pytest src/fastwam/memory_v2/tests -q
# 1) frozen post-Video-DiT features of every frame (~35 GiB bf16, once)
$PY -m fastwam.memory_v2.train_v2 features --config configs/memory_v2/train_v2_A.yaml
# 2) throughput / memory check, no files written except logs
$PY -m fastwam.memory_v2.train_v2 train --config configs/memory_v2/train_v2_A.yaml --dry-run 3
# 3) training (N GPUs: torchrun --standalone --nproc_per_node=N -m fastwam.memory_v2.train_v2 train ...)
$PY -m fastwam.memory_v2.train_v2 train --config configs/memory_v2/train_v2_A.yaml
# 4) full 401-window evaluation of a checkpoint (modes on/off/null, optional guidance)
$PY -m fastwam.memory_v2.train_v2 evaluate --config configs/memory_v2/train_v2_A.yaml \
    --checkpoint outputs/memory_v2/v2_A_memory_only/checkpoints/update_000670.pt --windows 0 --guidance 1.5 2
```

Run outputs: `CONFIG.json`, `INIT_PARITY.json`, `metrics.jsonl` (loss, FM per tau bin,
dropped fraction, grad norm, s/update), `probes.jsonl` (tau-gate profile, attention mass per
role at tau 0.95/0.5/0.1, history sensitivity vs tau), `eval/update_*.json`, `checkpoints/`.
`touch <output>/STOP.json` stops at the next update boundary with a checkpoint.

## Phase-0 protocol check

```bash
$PY scripts/memory_v2/phase0_protocol.py run --checkpoint source \
    --checkpoint A335=/migration/runs/a327_gpu4_v1/checkpoints/update_000335/mp_rank_00_model_states.pt \
    --output outputs/memory_v2/phase0
$PY scripts/memory_v2/phase0_protocol.py summarize --output outputs/memory_v2/phase0
```

Per window and checkpoint: inference shift {1, 5} x memory_s1 gate {1, 0}, arm/gripper RMSE,
executed prefix 16 vs 24, FM error at tau 0.1/0.5/0.9/0.95/1.0. `gate1_shift1` reproduces the
dense EVALUATION.json; `gate0` tells whether an A335 regression lives in the ActionDiT or in the
memory path. Closed-loop {shift} x {execute 16/24} is deferred until a non-regressed base is chosen
(the dense physical harness hard-codes execute 24 and has two frozen scenes).

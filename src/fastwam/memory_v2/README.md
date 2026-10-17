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

## Not here yet (by design)

* `train_v2.py` — written after dense-joint A/335 is available, reusing its data/image contract
  (float two-stage mosaic, predict 32 / execute 24, landmark stride 24) and its trainable-ActionDiT
  masters through a second adapter.
* Phase-0 protocol check (shift 1 vs 5, execute 16 vs 24) — run on A/335.

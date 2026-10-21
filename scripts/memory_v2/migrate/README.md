# memory_v2: A100 -> AWS H100 (p5.4xlarge) migration

What moves (logical paths are kept; the H100 container bind-mounts them back):

| group | source | notes |
|---|---|---|
| dense_code | /restore-tmp/dense_joint_v1 | Codex delivery code (`common`, `model_path`) |
| fastwam_repo | /workspace/FastWAM git-tracked + untracked-not-ignored | no resources/, outputs/ |
| dense_output | /workspace/FastWAM/outputs/s1_dense_joint_h100_v1 | all but DeepSpeed optimizer shards |
| resources | traced weight files + their sibling files | only what the code actually opened |
| memory2_outputs | /workspace/FastWAM-memory2/outputs | checkpoints: update_001340.pt only |
| features | outputs/memory_v2/features_dense_v1 | `SKIP=features` to rebuild on the H100 instead |
| simulator | resources/RMBench (no data/), resources/PyTorch3D | `SKIP=simulator` if no closed loop |
| hf_cache | traced files under /root/.cache/huggingface | tokens are never included |

Code comes from GitHub `memory2`; the training env is rebuilt on `nvcr.io/nvidia/pytorch:25.11-py3`
(the dense receipt's torch 2.10 / CUDA 13 stack) plus the A100 venv-only packages.

A100: `a100_pack.sh local` (records, traces, manifest, stage) -> `hf auth login` -> `a100_pack.sh upload`.
H100 host: `h100_host.sh`. Container: `h100_restore.sh system|download|code|env|verify|test|reference|simulator`.

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

## 8-GPU evaluation box on AWS (plan v7, P0; 11-05)

Rented by the day (p5.48xlarge = 8 x H100, or p5en.48xlarge = 8 x H200) only to run closed-loop evaluations.
Training stays on our own H200s. The environment is the same as the H100 migration above (same HF payload repo,
same `nvcr.io/nvidia/pytorch:25.11-py3` image = the H200's torch 2.10 stack), so a model trained on the H200 is
evaluated with the same software.

1. Host: `bash aws_host.sh` (any number of H100 / H200; prints GPU count, CPU cores, RAM; container `mwam-aws`).
2. Container: `bash scripts/memory_v2/migrate/h100_restore.sh system`, then `hf auth login` (typed by the user;
   tokens are never stored by these scripts), then `download code env verify simulator` (`test` / `reference` are
   optional on an evaluation-only box).
3. Inputs for the tasks of the day: the slim checkpoints (`slim_checkpoint.py`) and the scene banks they use, copied
   from the training host (rsync / HF, same layout under `outputs/memory_v2`), plus any reference folders a
   `compare` / `reference` / `parity_with` field names.
4. Pool: on the host `C=mwam-aws bash scripts/memory_v2/jobs/host_pool.sh start --lanes aws --gpus 0,1,2,3,4,5,6,7`;
   evaluation tasks for the box use `lane: aws` and `parallel: 3` (after P0-par3 passes on the H200).
5. Before the first verdict on a new GPU type, one parity task (same checkpoint, same scenes as an existing H200 run,
   `parity_with`, first-decision max |action difference|) — H100 vs H200 numerics are not assumed equal.
6. Results go back as the episode folders (`closed_loop/<output>`), synced to the training host under
   `closed_loop/aws/...`; verdicts are computed where the reference episodes are.

Throughput is bound by CPU (one simulator per running episode): with 3 copies per GPU, 24 episodes run at once;
choose the instance by `nproc` (aws_host.sh prints it).

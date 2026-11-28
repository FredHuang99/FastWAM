# pool5 report 2026-11-29 01:37:05 (6e4b37a15066)

```
== pool5 2026-11-29 01:37:05 on 6e4b37a15066: dispatcher pid 828112 ALIVE (last beat 2026-11-29 01:36:51); allowed GPUs [0, 1, 2, 3]; lanes ['loop', 'train', 'extra', 'gpu0', 'cpu']; nothing new starts after 01-05 23:59
   GPU 0:  12100/40960 MiB,   0% busy  -> A100-E22h-clock-p1024-hid-swap-s0
   GPU 1:  29718/40960 MiB,   0% busy  -> BUSY, not a queue task (another user, or ours started outside the queue)
   GPU 2:  25052/40960 MiB,   0% busy  -> BUSY, not a queue task (another user, or ours started outside the queue)
   GPU 3:  20909/40960 MiB,  69% busy  -> A100-E22h-ledger-p256-hid-put-s4
   queue5 lane processes: cpu:stopped extra:stopped gpu0:stopped loop:stopped train:stopped
   tasks: 356 done, 5 running, 3336 pending, 101 on hold

RUNNING
  A100-C36FB-fetch-ow shell       GPU None  attempt 1  since 11-29 01:08  [pool]    last write 3 min ago
  A100-C36FB-fetch-ref shell       GPU None  attempt 1  since 11-29 01:08  [pool]    last write 3 min ago
  A100-C36FB-gate    shell       GPU None  attempt 1  since 11-29 01:08  [pool]    last write 8 min ago
  A100-E22h-ledger-p256-hid-put-s4 closed_loop GPU 3  attempt 1  since 11-29 01:02  [pool]  5/10 episodes  ETA 11-29 02:04 (0.5 h)    last write 0 min ago
  A100-E22h-clock-p1024-hid-swap-s0 closed_loop GPU 0  attempt 1  since 11-29 01:35  [pool]  0/10 episodes  ETA ?    last write 0 min ago

QUEUE (pool lanes, in start order)
  A100-C36FB-smoke   closed_loop after A100-C36FB-gate, A100-C36FB-fetch-ow
  A100-C36FB-ow-s0   closed_loop after A100-C36FB-smoke
  A100-C36FB-ref-s0  closed_loop after A100-C36FB-smoke, A100-C36FB-fetch-ref
  A100-C36FB-ow-s1   closed_loop after A100-C36FB-smoke
  A100-C36FB-ref-s1  closed_loop after A100-C36FB-smoke, A100-C36FB-fetch-ref
  A100-C36FB-ow-s2   closed_loop after A100-C36FB-smoke
  A100-C36FB-ref-s2  closed_loop after A100-C36FB-smoke, A100-C36FB-fetch-ref
  A100-C36FB-ow-s3   closed_loop after A100-C36FB-smoke
  A100-C36FB-ref-s3  closed_loop after A100-C36FB-smoke, A100-C36FB-fetch-ref
  A100-C36FB-ow-s4   closed_loop after A100-C36FB-smoke
  A100-C36FB-ref-s4  closed_loop after A100-C36FB-smoke, A100-C36FB-fetch-ref
  A100-C36FB-ow-s5   closed_loop after A100-C36FB-smoke
  A100-C36FB-ref-s5  closed_loop after A100-C36FB-smoke, A100-C36FB-fetch-ref
  A100-C36FB-ow-s6   closed_loop after A100-C36FB-smoke
  A100-C36FB-ref-s6  closed_loop after A100-C36FB-smoke, A100-C36FB-fetch-ref
  A100-C36FB-ow-s7   closed_loop after A100-C36FB-smoke
  A100-C36FB-ref-s7  closed_loop after A100-C36FB-smoke, A100-C36FB-fetch-ref
  A100-C36FB-ow-s8   closed_loop after A100-C36FB-smoke
  A100-C36FB-ref-s8  closed_loop after A100-C36FB-smoke, A100-C36FB-fetch-ref
  A100-C36FB-ow-s9   closed_loop after A100-C36FB-smoke
  A100-C36FB-ref-s9  closed_loop after A100-C36FB-smoke, A100-C36FB-fetch-ref
  A100-C36FB-verdict shell       after A100-C36FB-ow-s0, A100-C36FB-ref-s0, A100-C36FB-ow-s1, A100-C36FB-ref-s1, A100-C36FB-ow-s2, A100-C36FB-ref-s2, A100-C36FB-ow-s3, A100-C36FB-ref-s3, A100-C36FB-ow-s4, A100-C36FB-ref-s4, A100-C36FB-ow-s5, A100-C36FB-ref-s5, A100-C36FB-ow-s6, A100-C36FB-ref-s6, A100-C36FB-ow-s7, A100-C36FB-ref-s7, A100-C36FB-ow-s8, A100-C36FB-ref-s8, A100-C36FB-ow-s9, A100-C36FB-ref-s9
  A100-C36FB-gate-r2 shell       after A100-C36FB-verdict
  A100-C36FB-ow-r2-s0 closed_loop after A100-C36FB-gate-r2
  A100-C36FB-ref-r2-s0 closed_loop after A100-C36FB-gate-r2
  A100-C36FB-ow-r2-s1 closed_loop after A100-C36FB-gate-r2
  A100-C36FB-ref-r2-s1 closed_loop after A100-C36FB-gate-r2
  A100-C36FB-ow-r2-s2 closed_loop after A100-C36FB-gate-r2
  A100-C36FB-ref-r2-s2 closed_loop after A100-C36FB-gate-r2
  A100-C36FB-ow-r2-s3 closed_loop after A100-C36FB-gate-r2
  A100-C36FB-ref-r2-s3 closed_loop after A100-C36FB-gate-r2
  A100-C36FB-ow-r2-s4 closed_loop after A100-C36FB-gate-r2
  A100-C36FB-ref-r2-s4 closed_loop after A100-C36FB-gate-r2
  A100-C36FB-ow-r2-s5 closed_loop after A100-C36FB-gate-r2
  A100-C36FB-ref-r2-s5 closed_loop after A100-C36FB-gate-r2
  A100-C36FB-ow-r2-s6 closed_loop after A100-C36FB-gate-r2
  A100-C36FB-ref-r2-s6 closed_loop after A100-C36FB-gate-r2
  A100-C36FB-ow-r2-s7 closed_loop after A100-C36FB-gate-r2
  A100-C36FB-ref-r2-s7 closed_loop after A100-C36FB-gate-r2
  A100-C36FB-ow-r2-s8 closed_loop after A100-C36FB-gate-r2
  A100-C36FB-ref-r2-s8 closed_loop after A100-C36FB-gate-r2
  A100-C36FB-ow-r2-s9 closed_loop after A100-C36FB-gate-r2
  A100-C36FB-ref-r2-s9 closed_loop after A100-C36FB-gate-r2
  A100-C36FB-verdict-r2 shell       after A100-C36FB-ow-r2-s0, A100-C36FB-ref-r2-s0, A100-C36FB-ow-r2-s1, A100-C36FB-ref-r2-s1, A100-C36FB-ow-r2-s2, A100-C36FB-ref-r2-s2, A100-C36FB-ow-r2-s3, A100-C36FB-ref-r2-s3, A100-C36FB-ow-r2-s4, A100-C36FB-ref-r2-s4, A100-C36FB-ow-r2-s5, A100-C36FB-ref-r2-s5, A100-C36FB-ow-r2-s6, A100-C36FB-ref-r2-s6, A100-C36FB-ow-r2-s7, A100-C36FB-ref-r2-s7, A100-C36FB-ow-r2-s8, A100-C36FB-ref-r2-s8, A100-C36FB-ow-r2-s9, A100-C36FB-ref-r2-s9
  AL4a-e10b-swap-s0  closed_loop on hold
  AL4a-e10b-swap-s1  closed_loop on hold
  A100-E22h-clock-p1024-hid-swap-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A100-E22h-clock-p1024-hid-swap-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A100-E22h-clock-p1024-hid-swap-s3 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A100-E22h-clock-p1024-hid-swap-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A100-E22h-ledger-p1024-hid-swap-s0 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A100-E22h-ledger-p1024-hid-swap-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A100-E22h-ledger-p1024-hid-swap-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A100-E22h-ledger-p1024-hid-swap-s3 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A100-E22h-ledger-p1024-hid-swap-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A100-E22h-pack-hid2 shell       after A100-E22h-ledger-p256-hid-put-s4, A100-E22h-clock-p1024-hid-swap-s0, A100-E22h-clock-p1024-hid-swap-s1, A100-E22h-clock-p1024-hid-swap-s2, A100-E22h-clock-p1024-hid-swap-s3, A100-E22h-clock-p1024-hid-swap-s4, A100-E22h-ledger-p1024-hid-swap-s0, A100-E22h-ledger-p1024-hid-swap-s1, A100-E22h-ledger-p1024-hid-swap-s2, A100-E22h-ledger-p1024-hid-swap-s3, A100-E22h-ledger-p1024-hid-swap-s4

FAILURES SEEN (latest per task)
  T2                 attempt 2: rc=1: non-zero exit  -> now done PASS
  PB-events2         attempt 3: rc=1: non-zero exit  -> now done ERROR
  PB-parity          attempt 3: rc=1: non-zero exit  -> now done ERROR
  PB-parity2         attempt 3: rc=1: non-zero exit  -> now done ERROR
  PB-plan            attempt 3: rc=2: non-zero exit  -> now done PASS
  PB-s1-A            attempt 2: rc=1: non-zero exit  -> now done PASS
  ADDx-a100-e30-swap-s4 attempt 3: 5 episodes ended with ERROR.json (re-run retries only those)  -> now done DONE
  ADDx-a100-e30-swap-s5 attempt 2: 5 episodes ended with ERROR.json (re-run retries only those)  -> now done DONE
  ADDx-a100-e30-swap-s6 attempt 3: 1 episodes ended with ERROR.json (re-run retries only those)  -> now done DONE
  ADDx-a100-e30-swap-s7 attempt 2: 2 episodes ended with ERROR.json (re-run retries only those)  -> now done DONE

LATEST VERDICTS
  11-28 22:35  A100-E22h-clock-p256-hid-put-s2 DONE          put_back_block/on n=35 lifted=35 centre=35 pressed=34 stage1=34 regrasp=34 returned=35 success=34 prog=0.98
  11-28 23:02  A100-E22h-clock-p256-hid-put-s3 DONE          put_back_block/on n=43 lifted=43 centre=43 pressed=42 stage1=42 regrasp=42 returned=43 success=42 prog=0.98
  11-28 23:35  A100-E22h-clock-p256-hid-put-s4 DONE          put_back_block/on n=50 lifted=50 centre=50 pressed=49 stage1=49 regrasp=49 returned=50 success=49 prog=0.99
  11-29 00:01  A100-E22h-ledger-p256-hid-put-s0 DONE          put_back_block/on n=14 lifted=14 centre=14 pressed=14 stage1=14 regrasp=14 returned=14 success=14 prog=1.00
  11-29 00:34  A100-E22h-ledger-p256-hid-put-s1 DONE          put_back_block/on n=25 lifted=25 centre=25 pressed=25 stage1=25 regrasp=25 returned=25 success=25 prog=1.00
  11-29 01:00  A100-E22h-ledger-p256-hid-put-s2 DONE          put_back_block/on n=33 lifted=33 centre=33 pressed=33 stage1=33 regrasp=33 returned=33 success=33 prog=1.00
  11-29 01:14  A100-C36FB-prep    PASS          rc=0
  11-29 01:34  A100-E22h-ledger-p256-hid-put-s3 DONE          put_back_block/on n=45 lifted=45 centre=45 pressed=45 stage1=45 regrasp=45 returned=45 success=45 prog=1.00
```

## A100-C36FB-prep (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-C36FB-prep.log):
```
  File "/migration/raid_runtime_v1/payload/memory2/scripts/memory_v2/migrate/relay.py", line 81, in <module>
    main()
  File "/migration/raid_runtime_v1/payload/memory2/scripts/memory_v2/migrate/relay.py", line 49, in main
    names = [x.path for x in api.list_repo_tree(args.repo, path_in_repo=prefix, repo_type="model", recursive=True)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hf-tools/lib/python3.12/site-packages/huggingface_hub/hf_api.py", line 3969, in list_repo_tree
    for path_info in paginate(path=tree_url, headers=headers, params={"recursive": recursive, "expand": expand}):
  File "/opt/hf-tools/lib/python3.12/site-packages/huggingface_hub/utils/_pagination.py", line 36, in paginate
    hf_raise_for_status(r)
  File "/opt/hf-tools/lib/python3.12/site-packages/huggingface_hub/utils/_http.py", line 886, in hf_raise_for_status
    raise _format(RemoteEntryNotFoundError, message, response, repo_type=repo_type, repo_id=repo_id) from e
huggingface_hub.errors.RemoteEntryNotFoundError: 404 Client Error. (Request ID: Root=1-6b0b0aa2-57d35e3b3a6ace1529b863b8;09996107-3bc8-42ed-be3a-d7df57e891b3)

Entry Not Found for url: https://huggingface.co/api/models/hhyfred/memwam-diag-v1/tree/main/diag%2Fbank_swap_T_a40?recursive=true&expand=false.
diag/bank_swap_T_a40 does not exist on "main"
waiting for diag/bank_swap_T_a40 2026-11-28 17:08:50
[relay] get hhyfred/memwam-diag-v1/diag/bank_swap_T_a40/bank_swap_T_a40.tgz -> outputs/fullft/bank_swap_T_a40/bank_swap_T_a40.tgz (17125 bytes)
[relay] get hhyfred/memwam-diag-v1/diag/bank_swap_T_a40/bank_swap_T_a40.tgz.sha256 -> outputs/fullft/bank_swap_T_a40/bank_swap_T_a40.tgz.sha256 (86 bytes)
bank_swap_T_a40.tgz: OK
[prep] 2026-11-28 17:13:55 swap_T; disk: /dev/nvme1n1p1  7.0T  6.2T  459G  94% /migration
swap_T: outputs/memory_v2/closed_loop/scenes_seed42_n100_swap_T/swap_T.json complete (100 scenes, next seed 4300108)
[text] swap_T: 'Swap the poses of the two T-blocks, including both position and orientation.' -> cache/swap_T_episode_0000000/encodings.pt (62 MiB; 50 training episodes share the instruction)
[text] swap_T: 2 files checked against dense_swap_T_v1/RELAY_MANIFEST.json (sha256); marker .text_only
[text] swap_T: 'Swap the poses of the two T-blocks, including both position and orientation.' -> cache/swap_T_episode_0000000/encodings.pt (50 training episodes share it); fingerprint 0e5f5bc1105d
[prep] 2026-11-28 17:14:08 swap_T ready
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A100-C36FB-prep.log):
```

[pool] 2026-11-29 01:08:42 exec A100-C36FB-prep GPU None 
[pool] 2026-11-29 01:08:49 A100-C36FB-prep: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-C36FB-prep.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-C36FB-prep.md
[queue5] 2026-11-29 01:14:15 A100-C36FB-prep: PASS  rc=0
```

## A100-C36FB-fetch-ow (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-C36FB-fetch-ow.log):
```

[queue5] 2026-11-29 01:08:48 $ bash -c RUN=swapT_ow TAG=e30 bash /workspace/FastWAM-memory2/scripts/fullft/export_fetch.sh
[fetch] 2026-11-28 17:08:50 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 17:13:52 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 17:18:53 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 17:23:54 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 17:28:55 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 17:33:56 waiting for exports/swapT_ow_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A100-C36FB-fetch-ow.log):
```

[pool] 2026-11-29 01:08:42 exec A100-C36FB-fetch-ow GPU None 
[pool] 2026-11-29 01:08:48 A100-C36FB-fetch-ow: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-C36FB-fetch-ow.log
```

## A100-C36FB-fetch-ref (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-C36FB-fetch-ref.log):
```

[queue5] 2026-11-29 01:08:48 $ bash -c RUN=swapT_arprop_h2 TAG=e30 bash /workspace/FastWAM-memory2/scripts/fullft/export_fetch.sh
[fetch] 2026-11-28 17:08:50 waiting for exports/swapT_arprop_h2_e30 on the relay
[fetch] 2026-11-28 17:13:52 waiting for exports/swapT_arprop_h2_e30 on the relay
[fetch] 2026-11-28 17:18:53 waiting for exports/swapT_arprop_h2_e30 on the relay
[fetch] 2026-11-28 17:23:54 waiting for exports/swapT_arprop_h2_e30 on the relay
[fetch] 2026-11-28 17:28:55 waiting for exports/swapT_arprop_h2_e30 on the relay
[fetch] 2026-11-28 17:33:56 waiting for exports/swapT_arprop_h2_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A100-C36FB-fetch-ref.log):
```

[pool] 2026-11-29 01:08:42 exec A100-C36FB-fetch-ref GPU None 
[pool] 2026-11-29 01:08:48 A100-C36FB-fetch-ref: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-C36FB-fetch-ref.log
```

## A100-C36FB-gate (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-C36FB-gate.log):
```

[queue5] 2026-11-29 01:08:48 $ bash -c cd /workspace/FastWAM-memory2 && /opt/mwam/bin/python scripts/fullft/c36fb_gate.py
[c36fb-gate] 2026-11-29 01:08:49 waiting until 2026-11-29 12:00 +0800 (10.9 h left)
[c36fb-gate] 2026-11-29 01:18:49 waiting until 2026-11-29 12:00 +0800 (10.7 h left)
[c36fb-gate] 2026-11-29 01:28:49 waiting until 2026-11-29 12:00 +0800 (10.5 h left)
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A100-C36FB-gate.log):
```

[pool] 2026-11-29 01:08:42 exec A100-C36FB-gate GPU None 
[pool] 2026-11-29 01:08:48 A100-C36FB-gate: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-C36FB-gate.log
```

## A100-v22-smoke (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-v22-smoke.log):
```
[decide] 2026-11-28 08:30:35 ar2_prop_e30_a100smoke/on swap_blocks seed=4300000 frame=0/1000 hist=0 policy=1.1s elapsed=9s
[decide] 2026-11-28 08:30:58 ar2_prop_e30_a100smoke/on swap_blocks seed=4300000 frame=32/1000 hist=2 policy=0.7s elapsed=32s
[decide] 2026-11-28 08:31:23 ar2_prop_e30_a100smoke/on swap_blocks seed=4300000 frame=64/1000 hist=3 policy=0.7s elapsed=57s
[decide] 2026-11-28 08:31:49 ar2_prop_e30_a100smoke/on swap_blocks seed=4300000 frame=96/1000 hist=3 policy=0.7s elapsed=82s
[decide] 2026-11-28 08:32:15 ar2_prop_e30_a100smoke/on swap_blocks seed=4300000 frame=128/1000 hist=3 policy=0.6s elapsed=109s
[decide] 2026-11-28 08:32:39 ar2_prop_e30_a100smoke/on swap_blocks seed=4300000 frame=160/1000 hist=3 policy=0.7s elapsed=133s
[decide] 2026-11-28 08:33:01 ar2_prop_e30_a100smoke/on swap_blocks seed=4300000 frame=192/1000 hist=3 policy=0.7s elapsed=155s
[decide] 2026-11-28 08:33:26 ar2_prop_e30_a100smoke/on swap_blocks seed=4300000 frame=224/1000 hist=3 policy=0.7s elapsed=180s
[decide] 2026-11-28 08:33:52 ar2_prop_e30_a100smoke/on swap_blocks seed=4300000 frame=256/1000 hist=3 policy=0.7s elapsed=206s
[decide] 2026-11-28 08:34:18 ar2_prop_e30_a100smoke/on swap_blocks seed=4300000 frame=288/1000 hist=3 policy=0.7s elapsed=232s
[decide] 2026-11-28 08:34:43 ar2_prop_e30_a100smoke/on swap_blocks seed=4300000 frame=320/1000 hist=3 policy=0.7s elapsed=257s
[decide] 2026-11-28 08:35:07 ar2_prop_e30_a100smoke/on swap_blocks seed=4300000 frame=352/1000 hist=3 policy=0.6s elapsed=280s
[decide] 2026-11-28 08:35:29 ar2_prop_e30_a100smoke/on swap_blocks seed=4300000 frame=384/1000 hist=3 policy=0.6s elapsed=303s
[decide] 2026-11-28 08:35:54 ar2_prop_e30_a100smoke/on swap_blocks seed=4300000 frame=416/1000 hist=3 policy=0.6s elapsed=328s
[decide] 2026-11-28 08:36:20 ar2_prop_e30_a100smoke/on swap_blocks seed=4300000 frame=448/1000 hist=3 policy=0.6s elapsed=353s
[decide] 2026-11-28 08:36:44 ar2_prop_e30_a100smoke/on swap_blocks seed=4300000 frame=480/1000 hist=3 policy=0.6s elapsed=378s
[decide] 2026-11-28 08:37:09 ar2_prop_e30_a100smoke/on swap_blocks seed=4300000 frame=512/1000 hist=3 policy=0.7s elapsed=402s
[decide] 2026-11-28 08:37:31 ar2_prop_e30_a100smoke/on swap_blocks seed=4300000 frame=544/1000 hist=3 policy=0.7s elapsed=425s
[decide] 2026-11-28 08:37:57 ar2_prop_e30_a100smoke/on swap_blocks seed=4300000 frame=576/1000 hist=3 policy=0.6s elapsed=450s
[closed-loop] 2026-11-28 08:38:06 done  ar2_prop_e30_a100smoke/on swap_blocks seed=4300000 success=True targets=584/1000 reward=1.0 lift=0.10095816850662231  521s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_prop_e30_a100smoke/onswap_blocks        1     1.00  [0.21,1.00]      1.00    1.00      584        -        -        -    0.7

[summary] 1 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/a100smoke/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A100-v22-smoke.log):
```

[pool] 2026-11-28 16:27:24 exec A100-v22-smoke GPU 0 
[pool] 2026-11-28 16:27:29 A100-v22-smoke: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-v22-smoke.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-v22-smoke.md
[queue5] 2026-11-28 16:38:14 A100-v22-smoke: PASS  swap_blocks/on n=1 lifted=1 s1=1 s2=1 s3=1 pressed=1 success=1 prog=1.00
```

## A100-E22h-clock-p256-hid-swap-s0 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-clock-p256-hid-swap-s0.log):
```
  ar2_clock_e30_p1024_hid/on vs ar2_clock_e30_p256_vis/on  50     7       0       0       43  1.000
  ar2_clock_e30_p1024_hid/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_hid/on  50     7       0       0       43  1.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_hid2/on  20     3       0      17        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_vis/on  50     7       0       0       43  1.000
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_hid2/on  20     3       0      17        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_clock_e30_p256_vis/on  20     3      17       0        0  0.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_hid/on  20    20       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_vis/on  20    20       0       0        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 520 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A100-E22h-clock-p256-hid-swap-s0.log):
```

[pool] 2026-11-28 16:57:22 exec A100-E22h-clock-p256-hid-swap-s0 GPU 0 
[pool] 2026-11-28 16:57:27 A100-E22h-clock-p256-hid-swap-s0: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-clock-p256-hid-swap-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-clock-p256-hid-swap-s0.md
[queue5] 2026-11-28 18:29:02 A100-E22h-clock-p256-hid-swap-s0: DONE  swap_blocks/on n=20 lifted=20 s1=20 s2=20 s3=20 pressed=20 success=20 prog=1.00
```

## A100-E22h-clock-p256-hid-swap-s1 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-clock-p256-hid-swap-s1.log):
```
  ar2_clock_e30_p1024_hid/on vs ar2_clock_e30_p256_vis/on  50     7       0       0       43  1.000
  ar2_clock_e30_p1024_hid/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_hid/on  50     7       0       0       43  1.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_hid2/on  19     3       0      16        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_vis/on  50     7       0       0       43  1.000
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_hid2/on  19     3       0      16        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_clock_e30_p256_vis/on  19     3      16       0        0  0.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_hid/on  19    19       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_vis/on  19    19       0       0        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 519 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A100-E22h-clock-p256-hid-swap-s1.log):
```

[pool] 2026-11-28 16:57:22 exec A100-E22h-clock-p256-hid-swap-s1 GPU 3 
[pool] 2026-11-28 16:57:28 A100-E22h-clock-p256-hid-swap-s1: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-clock-p256-hid-swap-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-clock-p256-hid-swap-s1.md
[queue5] 2026-11-28 18:29:00 A100-E22h-clock-p256-hid-swap-s1: DONE  swap_blocks/on n=19 lifted=19 s1=19 s2=19 s3=19 pressed=19 success=19 prog=1.00
```

## A100-E22h-clock-p256-hid-swap-s2 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-clock-p256-hid-swap-s2.log):
```
  ar2_clock_e30_p1024_hid/on vs ar2_clock_e30_p256_vis/on  50     7       0       0       43  1.000
  ar2_clock_e30_p1024_hid/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_hid/on  50     7       0       0       43  1.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_hid2/on  39     6       0      33        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_vis/on  50     7       0       0       43  1.000
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_hid2/on  39     6       0      33        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_clock_e30_p256_vis/on  39     6      33       0        0  0.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_hid/on  39    39       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_vis/on  39    39       0       0        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 539 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A100-E22h-clock-p256-hid-swap-s2.log):
```

[pool] 2026-11-28 18:30:31 exec A100-E22h-clock-p256-hid-swap-s2 GPU 0 
[pool] 2026-11-28 18:30:37 A100-E22h-clock-p256-hid-swap-s2: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-clock-p256-hid-swap-s2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-clock-p256-hid-swap-s2.md
[queue5] 2026-11-28 20:01:22 A100-E22h-clock-p256-hid-swap-s2: DONE  swap_blocks/on n=39 lifted=39 s1=39 s2=39 s3=39 pressed=39 success=39 prog=1.00
```

## A100-E22h-clock-p256-hid-swap-s3 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-clock-p256-hid-swap-s3.log):
```
  ar2_clock_e30_p1024_hid/on vs ar2_clock_e30_p256_vis/on  50     7       0       0       43  1.000
  ar2_clock_e30_p1024_hid/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_hid/on  50     7       0       0       43  1.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_hid2/on  40     7       0      33        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_vis/on  50     7       0       0       43  1.000
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_hid2/on  40     7       0      33        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_clock_e30_p256_vis/on  40     7      33       0        0  0.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_hid/on  40    40       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_vis/on  40    40       0       0        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 540 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A100-E22h-clock-p256-hid-swap-s3.log):
```

[pool] 2026-11-28 18:30:31 exec A100-E22h-clock-p256-hid-swap-s3 GPU 3 
[pool] 2026-11-28 18:30:37 A100-E22h-clock-p256-hid-swap-s3: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-clock-p256-hid-swap-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-clock-p256-hid-swap-s3.md
[queue5] 2026-11-28 20:01:24 A100-E22h-clock-p256-hid-swap-s3: DONE  swap_blocks/on n=40 lifted=40 s1=40 s2=40 s3=40 pressed=40 success=40 prog=1.00
```

## A100-E22h-clock-p256-hid-swap-s4 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-clock-p256-hid-swap-s4.log):
```
  ar2_clock_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_hid/on  50     7       0       0       43  1.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_hid2/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_vis/on  50     7       0       0       43  1.000
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_hid2/on  64    21       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_clock_e30_p256_vis/on  64    21      43       0        0  0.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_hid/on  50    50       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_hid/on  14    14       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_vis/on  14    14       0       0        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 564 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A100-E22h-clock-p256-hid-swap-s4.log):
```

[pool] 2026-11-28 20:02:43 exec A100-E22h-clock-p256-hid-swap-s4 GPU 0 
[pool] 2026-11-28 20:02:49 A100-E22h-clock-p256-hid-swap-s4: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-clock-p256-hid-swap-s4.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-clock-p256-hid-swap-s4.md
[queue5] 2026-11-28 21:33:32 A100-E22h-clock-p256-hid-swap-s4: DONE  swap_blocks/on n=50 lifted=50 s1=50 s2=50 s3=50 pressed=50 success=50 prog=1.00
```

## A100-E22h-clock-p256-hid-put-s0 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-clock-p256-hid-put-s0.log):
```
  ar2_clock_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_hid/on  50     7       0       0       43  1.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_hid2/on  46     7       0      39        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_vis/on  50     7       0       0       43  1.000
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_hid2/on  56    17       0      39        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_clock_e30_p256_vis/on  56    17      39       0        0  0.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_hid/on  46    46       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_vis/on  46    46       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_hid/on  10    10       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_vis/on  10    10       0       0        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 556 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A100-E22h-clock-p256-hid-put-s0.log):
```

[pool] 2026-11-28 20:02:43 exec A100-E22h-clock-p256-hid-put-s0 GPU 3 
[pool] 2026-11-28 20:02:49 A100-E22h-clock-p256-hid-put-s0: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-clock-p256-hid-put-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-clock-p256-hid-put-s0.md
[queue5] 2026-11-28 21:02:04 A100-E22h-clock-p256-hid-put-s0: DONE  put_back_block/on n=10 lifted=10 centre=10 pressed=10 stage1=10 regrasp=10 returned=10 success=10 prog=1.00
```

## A100-E22h-clock-p256-hid-put-s1 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-clock-p256-hid-put-s1.log):
```
  ar2_clock_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_hid/on  50     7       0       0       43  1.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_hid2/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_vis/on  50     7       0       0       43  1.000
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_hid2/on  74    31       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_clock_e30_p256_vis/on  74    31      43       0        0  0.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_hid/on  50    50       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_hid/on  24    24       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_vis/on  24    24       0       0        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 574 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A100-E22h-clock-p256-hid-put-s1.log):
```

[pool] 2026-11-28 21:03:17 exec A100-E22h-clock-p256-hid-put-s1 GPU 3 
[pool] 2026-11-28 21:03:23 A100-E22h-clock-p256-hid-put-s1: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-clock-p256-hid-put-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-clock-p256-hid-put-s1.md
[queue5] 2026-11-28 22:02:11 A100-E22h-clock-p256-hid-put-s1: DONE  put_back_block/on n=24 lifted=24 centre=24 pressed=24 stage1=24 regrasp=24 returned=24 success=24 prog=1.00
```

## A100-E22h-clock-p256-hid-put-s2 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-clock-p256-hid-put-s2.log):
```
  ar2_clock_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_hid/on  50     7       0       0       43  1.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_hid2/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_vis/on  50     7       0       0       43  1.000
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_hid2/on  85    41       0      43        1  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_clock_e30_p256_vis/on  85    41      43       0        1  0.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_hid/on  50    50       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_hid/on  35    34       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_vis/on  35    34       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 585 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A100-E22h-clock-p256-hid-put-s2.log):
```

[pool] 2026-11-28 21:34:45 exec A100-E22h-clock-p256-hid-put-s2 GPU 0 
[pool] 2026-11-28 21:34:51 A100-E22h-clock-p256-hid-put-s2: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-clock-p256-hid-put-s2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-clock-p256-hid-put-s2.md
[queue5] 2026-11-28 22:36:10 A100-E22h-clock-p256-hid-put-s2: DONE  put_back_block/on n=35 lifted=35 centre=35 pressed=34 stage1=34 regrasp=34 returned=35 success=34 prog=0.98
```

## A100-E22h-clock-p256-hid-put-s3 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-clock-p256-hid-put-s3.log):
```
  ar2_clock_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_hid/on  50     7       0       0       43  1.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_hid2/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_clock_e30_p256_vis/on  50     7       0       0       43  1.000
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_hid2/on  93    49       0      43        1  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_clock_e30_p256_vis/on  93    49      43       0        1  0.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_hid/on  50    50       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_hid/on  43    42       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_vis/on  43    42       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 593 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A100-E22h-clock-p256-hid-put-s3.log):
```

[pool] 2026-11-28 22:03:16 exec A100-E22h-clock-p256-hid-put-s3 GPU 3 
[pool] 2026-11-28 22:03:22 A100-E22h-clock-p256-hid-put-s3: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-clock-p256-hid-put-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-clock-p256-hid-put-s3.md
[queue5] 2026-11-28 23:02:36 A100-E22h-clock-p256-hid-put-s3: DONE  put_back_block/on n=43 lifted=43 centre=43 pressed=42 stage1=42 regrasp=42 returned=43 success=42 prog=0.98
```

## A100-E22h-clock-p256-hid-put-s4 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-clock-p256-hid-put-s4.log):
```
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_hid2/on 100    56       0      43        1  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid2/on   5     5       0       0        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_clock_e30_p256_vis/on 100    56      43       0        1  0.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_hid/on  50    50       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_hid2/on   5     5       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid2/on   5     5       0       0        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_hid2/on   5     5       0       0        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000
  ar2_prop_e30_p256_hid2/on vs ar2_prop_e30_p256_vis/on   5     5       0       0        0  1.000

[summary] 605 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A100-E22h-clock-p256-hid-put-s4.log):
```

[pool] 2026-11-28 22:37:12 exec A100-E22h-clock-p256-hid-put-s4 GPU 0 
[pool] 2026-11-28 22:37:18 A100-E22h-clock-p256-hid-put-s4: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-clock-p256-hid-put-s4.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-clock-p256-hid-put-s4.md
[queue5] 2026-11-28 23:36:17 A100-E22h-clock-p256-hid-put-s4: DONE  put_back_block/on n=50 lifted=50 centre=50 pressed=49 stage1=49 regrasp=49 returned=50 success=49 prog=0.99
```

## A100-E22h-ledger-p256-hid-put-s0 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-ledger-p256-hid-put-s0.log):
```
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_hid2/on 100    56       0      43        1  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid2/on  14    14       0       0        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_clock_e30_p256_vis/on 100    56      43       0        1  0.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_hid/on  50    50       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_hid2/on  14    14       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid2/on  14    14       0       0        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_hid2/on  14    14       0       0        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000
  ar2_prop_e30_p256_hid2/on vs ar2_prop_e30_p256_vis/on  14    14       0       0        0  1.000

[summary] 614 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A100-E22h-ledger-p256-hid-put-s0.log):
```

[pool] 2026-11-28 23:03:56 exec A100-E22h-ledger-p256-hid-put-s0 GPU 3 
[pool] 2026-11-28 23:04:02 A100-E22h-ledger-p256-hid-put-s0: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-ledger-p256-hid-put-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-ledger-p256-hid-put-s0.md
[queue5] 2026-11-29 00:01:27 A100-E22h-ledger-p256-hid-put-s0: DONE  put_back_block/on n=14 lifted=14 centre=14 pressed=14 stage1=14 regrasp=14 returned=14 success=14 prog=1.00
```

## A100-E22h-ledger-p256-hid-put-s1 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-ledger-p256-hid-put-s1.log):
```
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_hid2/on 100    56       0      43        1  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid2/on  25    25       0       0        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_clock_e30_p256_vis/on 100    56      43       0        1  0.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_hid/on  50    50       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_hid2/on  25    25       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid2/on  25    25       0       0        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_hid2/on  25    25       0       0        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000
  ar2_prop_e30_p256_hid2/on vs ar2_prop_e30_p256_vis/on  25    25       0       0        0  1.000

[summary] 625 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A100-E22h-ledger-p256-hid-put-s1.log):
```

[pool] 2026-11-28 23:37:12 exec A100-E22h-ledger-p256-hid-put-s1 GPU 0 
[pool] 2026-11-28 23:37:18 A100-E22h-ledger-p256-hid-put-s1: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-ledger-p256-hid-put-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-ledger-p256-hid-put-s1.md
[queue5] 2026-11-29 00:34:58 A100-E22h-ledger-p256-hid-put-s1: DONE  put_back_block/on n=25 lifted=25 centre=25 pressed=25 stage1=25 regrasp=25 returned=25 success=25 prog=1.00
```

## A100-E22h-ledger-p256-hid-put-s2 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-ledger-p256-hid-put-s2.log):
```
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_hid2/on 100    56       0      43        1  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid2/on  33    32       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_clock_e30_p256_vis/on 100    56      43       0        1  0.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_hid/on  50    50       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_hid2/on  33    32       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid2/on  33    32       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_hid2/on  33    33       0       0        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000
  ar2_prop_e30_p256_hid2/on vs ar2_prop_e30_p256_vis/on  33    33       0       0        0  1.000

[summary] 633 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A100-E22h-ledger-p256-hid-put-s2.log):
```

[pool] 2026-11-29 00:02:41 exec A100-E22h-ledger-p256-hid-put-s2 GPU 3 
[pool] 2026-11-29 00:02:47 A100-E22h-ledger-p256-hid-put-s2: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-ledger-p256-hid-put-s2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-ledger-p256-hid-put-s2.md
[queue5] 2026-11-29 01:00:30 A100-E22h-ledger-p256-hid-put-s2: DONE  put_back_block/on n=33 lifted=33 centre=33 pressed=33 stage1=33 regrasp=33 returned=33 success=33 prog=1.00
```

## A100-E22h-ledger-p256-hid-put-s3 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-ledger-p256-hid-put-s3.log):
```
  ar2_clock_e30_p1024_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_hid2/on 100    56       0      43        1  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid2/on  45    44       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_clock_e30_p256_vis/on 100    56      43       0        1  0.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_hid/on  50    50       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_hid2/on  45    44       0       1        0  1.000
  ar2_clock_e30_p256_hid2/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_hid/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p1024_vis/on  50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid2/on  45    44       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p1024_hid/on vs ar2_prop_e30_p1024_vis/on  50    50       0       0        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_hid2/on  45    45       0       0        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000
  ar2_prop_e30_p256_hid2/on vs ar2_prop_e30_p256_vis/on  45    45       0       0        0  1.000

[summary] 645 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A100-E22h-ledger-p256-hid-put-s3.log):
```

[pool] 2026-11-29 00:35:58 exec A100-E22h-ledger-p256-hid-put-s3 GPU 0 
[pool] 2026-11-29 00:36:04 A100-E22h-ledger-p256-hid-put-s3: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-ledger-p256-hid-put-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-ledger-p256-hid-put-s3.md
[queue5] 2026-11-29 01:34:30 A100-E22h-ledger-p256-hid-put-s3: DONE  put_back_block/on n=45 lifted=45 centre=45 pressed=45 stage1=45 regrasp=45 returned=45 success=45 prog=1.00
```

## A100-E22h-ledger-p256-hid-put-s4 (running, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-ledger-p256-hid-put-s4.log):
```
[decide] 2026-11-28 17:27:15 ar2_prop_e30_p256_hid2/on put_back_block seed=4300024 frame=0/500 hist=0 policy=0.5s elapsed=7s
[decide] 2026-11-28 17:27:37 ar2_prop_e30_p256_hid2/on put_back_block seed=4300024 frame=32/500 hist=2 policy=0.6s elapsed=29s
[decide] 2026-11-28 17:28:00 ar2_prop_e30_p256_hid2/on put_back_block seed=4300024 frame=64/500 hist=3 policy=0.7s elapsed=52s
[decide] 2026-11-28 17:28:23 ar2_prop_e30_p256_hid2/on put_back_block seed=4300024 frame=96/500 hist=3 policy=0.7s elapsed=75s
[decide] 2026-11-28 17:28:48 ar2_prop_e30_p256_hid2/on put_back_block seed=4300024 frame=128/500 hist=3 policy=0.6s elapsed=100s
[decide] 2026-11-28 17:29:16 ar2_prop_e30_p256_hid2/on put_back_block seed=4300024 frame=160/500 hist=3 policy=0.7s elapsed=128s
[decide] 2026-11-28 17:29:41 ar2_prop_e30_p256_hid2/on put_back_block seed=4300024 frame=192/500 hist=3 policy=0.7s elapsed=153s
[decide] 2026-11-28 17:30:07 ar2_prop_e30_p256_hid2/on put_back_block seed=4300024 frame=224/500 hist=3 policy=0.7s elapsed=179s
[decide] 2026-11-28 17:30:31 ar2_prop_e30_p256_hid2/on put_back_block seed=4300024 frame=256/500 hist=3 policy=0.7s elapsed=203s
[decide] 2026-11-28 17:30:56 ar2_prop_e30_p256_hid2/on put_back_block seed=4300024 frame=288/500 hist=3 policy=0.6s elapsed=228s
[decide] 2026-11-28 17:31:31 ar2_prop_e30_p256_hid2/on put_back_block seed=4300024 frame=320/500 hist=3 policy=0.7s elapsed=263s
[closed-loop] 2026-11-28 17:31:42 done  ar2_prop_e30_p256_hid2/on put_back_block seed=4300024 success=True targets=332/500 reward=1.0 lift=0.12166845798492432  331s
[closed-loop] 2026-11-28 17:31:42 start ar2_prop_e30_p256_hid2/on put_back_block seed=4300029 target_limit=500 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/ar2_prop_e30_p256_hid2/on/put_back_block/seed_4300029
[decide] 2026-11-28 17:32:31 ar2_prop_e30_p256_hid2/on put_back_block seed=4300029 frame=0/500 hist=0 policy=0.5s elapsed=7s
[decide] 2026-11-28 17:32:53 ar2_prop_e30_p256_hid2/on put_back_block seed=4300029 frame=32/500 hist=2 policy=0.7s elapsed=29s
[decide] 2026-11-28 17:33:17 ar2_prop_e30_p256_hid2/on put_back_block seed=4300029 frame=64/500 hist=3 policy=0.7s elapsed=53s
[decide] 2026-11-28 17:33:41 ar2_prop_e30_p256_hid2/on put_back_block seed=4300029 frame=96/500 hist=3 policy=0.6s elapsed=77s
[decide] 2026-11-28 17:34:05 ar2_prop_e30_p256_hid2/on put_back_block seed=4300029 frame=128/500 hist=3 policy=0.6s elapsed=100s
[decide] 2026-11-28 17:34:28 ar2_prop_e30_p256_hid2/on put_back_block seed=4300029 frame=160/500 hist=3 policy=0.7s elapsed=124s
[decide] 2026-11-28 17:34:53 ar2_prop_e30_p256_hid2/on put_back_block seed=4300029 frame=192/500 hist=3 policy=0.7s elapsed=149s
[decide] 2026-11-28 17:35:19 ar2_prop_e30_p256_hid2/on put_back_block seed=4300029 frame=224/500 hist=3 policy=0.7s elapsed=175s
[decide] 2026-11-28 17:35:45 ar2_prop_e30_p256_hid2/on put_back_block seed=4300029 frame=256/500 hist=3 policy=0.6s elapsed=200s
[decide] 2026-11-28 17:36:09 ar2_prop_e30_p256_hid2/on put_back_block seed=4300029 frame=288/500 hist=3 policy=0.6s elapsed=225s
[decide] 2026-11-28 17:36:34 ar2_prop_e30_p256_hid2/on put_back_block seed=4300029 frame=320/500 hist=3 policy=0.7s elapsed=250s
[decide] 2026-11-28 17:37:10 ar2_prop_e30_p256_hid2/on put_back_block seed=4300029 frame=352/500 hist=3 policy=0.6s elapsed=286s
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A100-E22h-ledger-p256-hid-put-s4.log):
```

[pool] 2026-11-29 01:02:00 exec A100-E22h-ledger-p256-hid-put-s4 GPU 3 
[pool] 2026-11-29 01:02:07 A100-E22h-ledger-p256-hid-put-s4: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-ledger-p256-hid-put-s4.log
```

## A100-E22h-clock-p1024-hid-swap-s0 (running, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-clock-p1024-hid-swap-s0.log):
```

[queue5] 2026-11-29 01:35:52 $ /opt/mwam/bin/python -m fastwam.memory_v2.online run --checkpoint /workspace/FastWAM-memory2/outputs/fullft/exports/ar2_clock_e30/export_e30.pt --label ar2_clock_e30_p1024_hid2 --modes on --scenes /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/scenes_seed42_n100_swap_blocks --output /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22 --tasks swap_blocks --execute 8 --limit 50 --shard 0/5 --stress event:pause:1024:hidden
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A100-E22h-clock-p1024-hid-swap-s0.log):
```

[pool] 2026-11-29 01:35:45 exec A100-E22h-clock-p1024-hid-swap-s0 GPU 0 
[pool] 2026-11-29 01:35:52 A100-E22h-clock-p1024-hid-swap-s0: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A100-E22h-clock-p1024-hid-swap-s0.log
```

## verdicts in the last 24.0 h

- A100-C36FB-prep: **PASS** (2026-11-29 01:14:08) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-C36FB-prep.md
- A100-v22-smoke: **PASS** (2026-11-28 16:38:08) swap_blocks/on n=1 lifted=1 s1=1 s2=1 s3=1 pressed=1 success=1 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-v22-smoke.md
- A100-E22h-clock-p256-hid-swap-s0: **DONE** (2026-11-28 18:28:47) swap_blocks/on n=20 lifted=20 s1=20 s2=20 s3=20 pressed=20 success=20 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-clock-p256-hid-swap-s0.md
- A100-E22h-clock-p256-hid-swap-s1: **DONE** (2026-11-28 18:28:45) swap_blocks/on n=19 lifted=19 s1=19 s2=19 s3=19 pressed=19 success=19 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-clock-p256-hid-swap-s1.md
- A100-E22h-clock-p256-hid-swap-s2: **DONE** (2026-11-28 20:00:57) swap_blocks/on n=39 lifted=39 s1=39 s2=39 s3=39 pressed=39 success=39 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-clock-p256-hid-swap-s2.md
- A100-E22h-clock-p256-hid-swap-s3: **DONE** (2026-11-28 20:01:00) swap_blocks/on n=40 lifted=40 s1=40 s2=40 s3=40 pressed=40 success=40 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-clock-p256-hid-swap-s3.md
- A100-E22h-clock-p256-hid-swap-s4: **DONE** (2026-11-28 21:33:02) swap_blocks/on n=50 lifted=50 s1=50 s2=50 s3=50 pressed=50 success=50 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-clock-p256-hid-swap-s4.md
- A100-E22h-clock-p256-hid-put-s0: **DONE** (2026-11-28 21:01:55) put_back_block/on n=10 lifted=10 centre=10 pressed=10 stage1=10 regrasp=10 returned=10 success=10 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-clock-p256-hid-put-s0.md
- A100-E22h-clock-p256-hid-put-s1: **DONE** (2026-11-28 22:01:59) put_back_block/on n=24 lifted=24 centre=24 pressed=24 stage1=24 regrasp=24 returned=24 success=24 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-clock-p256-hid-put-s1.md
- A100-E22h-clock-p256-hid-put-s2: **DONE** (2026-11-28 22:35:55) put_back_block/on n=35 lifted=35 centre=35 pressed=34 stage1=34 regrasp=34 returned=35 success=34 prog=0.98
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-clock-p256-hid-put-s2.md
- A100-E22h-clock-p256-hid-put-s3: **DONE** (2026-11-28 23:02:19) put_back_block/on n=43 lifted=43 centre=43 pressed=42 stage1=42 regrasp=42 returned=43 success=42 prog=0.98
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-clock-p256-hid-put-s3.md
- A100-E22h-clock-p256-hid-put-s4: **DONE** (2026-11-28 23:35:59) put_back_block/on n=50 lifted=50 centre=50 pressed=49 stage1=49 regrasp=49 returned=50 success=49 prog=0.99
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-clock-p256-hid-put-s4.md
- A100-E22h-ledger-p256-hid-put-s0: **DONE** (2026-11-29 00:01:17) put_back_block/on n=14 lifted=14 centre=14 pressed=14 stage1=14 regrasp=14 returned=14 success=14 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-ledger-p256-hid-put-s0.md
- A100-E22h-ledger-p256-hid-put-s1: **DONE** (2026-11-29 00:34:46) put_back_block/on n=25 lifted=25 centre=25 pressed=25 stage1=25 regrasp=25 returned=25 success=25 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-ledger-p256-hid-put-s1.md
- A100-E22h-ledger-p256-hid-put-s2: **DONE** (2026-11-29 01:00:16) put_back_block/on n=33 lifted=33 centre=33 pressed=33 stage1=33 regrasp=33 returned=33 success=33 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-ledger-p256-hid-put-s2.md
- A100-E22h-ledger-p256-hid-put-s3: **DONE** (2026-11-29 01:34:13) put_back_block/on n=45 lifted=45 centre=45 pressed=45 stage1=45 regrasp=45 returned=45 success=45 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A100-E22h-ledger-p256-hid-put-s3.md

## dispatcher log (pool.log, last 40 lines)
```
[pool] 2026-11-21 19:58:46 A100-SWL-lag32-s1: started on GPU 2 (attempt 1, exec pid 1171575)
[pool] 2026-11-21 22:29:49 A100-SWL-lag64-s0: started on GPU 0 (attempt 1, exec pid 1186459)
[pool] 2026-11-21 22:55:57 A100-SWL-lag64-s1: started on GPU 3 (attempt 1, exec pid 1188884)
[pool] 2026-11-21 23:39:36 A100-E22-clock-p1024-vis-swap-s0: started on GPU 2 (attempt 1, exec pid 1192193)
[pool] 2026-11-22 02:23:04 A100-E22-clock-p1024-hid-swap-s0: started on GPU 1 (attempt 1, exec pid 1203707)
[pool] 2026-11-22 02:49:32 A100-E22-clock-p1024-vis-swap-s1: started on GPU 0 (attempt 1, exec pid 1206098)
[pool] 2026-11-22 03:15:59 A100-E22-clock-p1024-hid-swap-s1: started on GPU 3 (attempt 1, exec pid 1208125)
[pool] 2026-11-22 03:41:21 A100-E22-clock-p1024-vis-swap-s2: started on GPU 2 (attempt 1, exec pid 1209546)
[pool] 2026-11-22 06:24:35 A100-E22-clock-p1024-hid-swap-s2: started on GPU 1 (attempt 1, exec pid 1217824)
[pool] 2026-11-22 06:45:00 A100-E22-clock-p1024-vis-swap-s3: started on GPU 0 (attempt 1, exec pid 1218673)
[pool] 2026-11-22 07:10:57 A100-E22-clock-p1024-hid-swap-s3: started on GPU 3 (attempt 1, exec pid 1220020)
[pool] 2026-11-22 07:35:10 A100-E22-clock-p1024-vis-swap-s4: started on GPU 2 (attempt 1, exec pid 1221591)
[pool] 2026-11-22 10:19:30 A100-E22-clock-p1024-hid-swap-s4: started on GPU 1 (attempt 1, exec pid 1229594)
[pool] 2026-11-22 10:41:36 A100-E22-ledger-p1024-vis-swap-s0: started on GPU 0 (attempt 1, exec pid 1230950)
[pool] 2026-11-22 11:06:58 A100-E22-ledger-p1024-hid-swap-s0: started on GPU 3 (attempt 1, exec pid 1232588)
[pool] 2026-11-22 11:43:57 A100-E22-ledger-p1024-vis-swap-s1: started on GPU 2 (attempt 1, exec pid 1234786)
[pool] 2026-11-22 13:48:35 A100-E22-ledger-p1024-hid-swap-s1: started on GPU 0 (attempt 1, exec pid 1242242)
[pool] 2026-11-22 14:13:21 A100-E22-ledger-p1024-vis-swap-s2: started on GPU 3 (attempt 1, exec pid 1244130)
[pool] 2026-11-22 14:28:15 A100-E22-ledger-p1024-hid-swap-s2: started on GPU 1 (attempt 1, exec pid 1244902)
[pool] 2026-11-22 14:49:12 A100-E22-ledger-p1024-vis-swap-s3: started on GPU 2 (attempt 1, exec pid 1246519)
[pool] 2026-11-22 16:59:00 A100-E22-ledger-p1024-hid-swap-s3: started on GPU 0 (attempt 1, exec pid 1254157)
[pool] 2026-11-22 17:24:30 A100-E22-ledger-p1024-vis-swap-s4: started on GPU 3 (attempt 1, exec pid 1256309)
[pool] 2026-11-22 17:39:49 A100-E22-ledger-p1024-hid-swap-s4: started on GPU 1 (attempt 1, exec pid 1257195)
[pool] 2026-11-28 16:27:24 A100-v22-smoke: started on GPU 0 (attempt 1, exec pid 1318477)
[pool] 2026-11-28 16:57:22 A100-E22h-clock-p256-hid-swap-s0: started on GPU 0 (attempt 1, exec pid 1319260)
[pool] 2026-11-28 16:57:22 A100-E22h-clock-p256-hid-swap-s1: started on GPU 3 (attempt 1, exec pid 1319261)
[pool] 2026-11-28 18:30:31 A100-E22h-clock-p256-hid-swap-s2: started on GPU 0 (attempt 1, exec pid 1325945)
[pool] 2026-11-28 18:30:31 A100-E22h-clock-p256-hid-swap-s3: started on GPU 3 (attempt 1, exec pid 1325946)
[pool] 2026-11-28 20:02:43 A100-E22h-clock-p256-hid-swap-s4: started on GPU 0 (attempt 1, exec pid 1332528)
[pool] 2026-11-28 20:02:43 A100-E22h-clock-p256-hid-put-s0: started on GPU 3 (attempt 1, exec pid 1332529)
[pool] 2026-11-28 21:03:17 A100-E22h-clock-p256-hid-put-s1: started on GPU 3 (attempt 1, exec pid 1337970)
[pool] 2026-11-28 21:34:45 A100-E22h-clock-p256-hid-put-s2: started on GPU 0 (attempt 1, exec pid 1340965)
[pool] 2026-11-28 22:03:16 A100-E22h-clock-p256-hid-put-s3: started on GPU 3 (attempt 1, exec pid 1343687)
[pool] 2026-11-28 22:37:12 A100-E22h-clock-p256-hid-put-s4: started on GPU 0 (attempt 1, exec pid 1347258)
[pool] 2026-11-28 23:03:56 A100-E22h-ledger-p256-hid-put-s0: started on GPU 3 (attempt 1, exec pid 1349925)
[pool] 2026-11-28 23:37:12 A100-E22h-ledger-p256-hid-put-s1: started on GPU 0 (attempt 1, exec pid 1353495)
[pool] 2026-11-29 00:02:41 A100-E22h-ledger-p256-hid-put-s2: started on GPU 3 (attempt 1, exec pid 1356160)
[pool] 2026-11-29 00:35:58 A100-E22h-ledger-p256-hid-put-s3: started on GPU 0 (attempt 1, exec pid 1359553)
[pool] 2026-11-29 01:02:00 A100-E22h-ledger-p256-hid-put-s4: started on GPU 3 (attempt 1, exec pid 1362434)
[pool] 2026-11-29 01:35:45 A100-E22h-clock-p1024-hid-swap-s0: started on GPU 0 (attempt 1, exec pid 1366204)
```
## lane cpu log (last 10 lines)
```
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_PG-A-final.md
[queue5] 2026-10-29 00:57:07 PG-A-final: PASS  put_back_block/null n=50 lifted=48 centre=45 pressed=4 stage1=4 regrasp=1 returned=4 success=1 prog=0.33; put_back_block/on n=50 lifted=48 centre=44 pressed=22 stage1=22 regrasp=18 returned=13 success=10 prog=0.51; put_back_block on/null only pressed 18/0 p=0.000; put_back_block dprog on-null +0.180 [0.1033, 0.26] p=0.0001 n=50
[queue5] 2026-10-29 00:57:07 no runnable task (pending, waiting on dependencies: []); re-checking every 5 min
[queue5.sh] 2026-10-29 15:46:35 lane cpu GPU none; 52308ca queue5_restart.sh: a killed lane left as a zombie counts as exited (10-29 22:47: four lanes stopped but were reported as not exited and not restarted)
[queue5] 2026-10-29 23:46:35 lane cpu on GPU None; tasks /migration/raid_runtime_v1/payload/memory2/scripts/memory_v2/jobs/queue5_tasks.yaml; deadline 2026-11-02 08:00 Beijing
[queue5] 2026-10-29 23:46:36 no runnable task (pending, waiting on dependencies: ['X7-H8']); re-checking every 5 min
[queue5] 2026-10-29 23:51:46 X7-H8: start (analysis); log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/X7-H8.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_X7-H8.md
[queue5] 2026-10-29 23:55:30 X7-H8: PASS  swap_blocks/null n=34 lifted=30 s1=26 s2=12 s3=2 pressed=4 success=2 prog=0.36; swap_blocks/on n=34 lifted=34 s1=34 s2=28 s3=13 pressed=15 success=11 prog=0.64; swap_blocks on/null only s2 17/1 p=0.000; swap_blocks dprog on-null +0.279 [0.1618, 0.3922] p=0.0001 n=34
[queue5] 2026-10-29 23:55:30 no runnable task (pending, waiting on dependencies: []); re-checking every 5 min
```

disk free: 459G

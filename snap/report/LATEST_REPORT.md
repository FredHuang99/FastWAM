# pool5 report 2026-11-29 01:52:55 (GPU18)

```
== pool5 2026-11-29 01:52:55 on GPU18: dispatcher pid 473 ALIVE (last beat 2026-11-29 01:52:23); allowed GPUs [0, 1, 2, 3]; lanes ['a40', 'a40cpu']; nothing new starts after 01-05 23:59; dropped as unhealthy (back automatically once healthy): [4, 5, 6, 7]
   GPU 0:  45334/46068 MiB, 100% busy  -> BUSY, not a queue task (another user, or ours started outside the queue)
   GPU 1:  23959/46068 MiB, 100% busy  -> BUSY, not a queue task (another user, or ours started outside the queue)
   GPU 2:  32725/46068 MiB,   0% busy  -> BUSY, not a queue task (another user, or ours started outside the queue)
   GPU 3:  45430/46068 MiB, 100% busy  -> BUSY, not a queue task (another user, or ours started outside the queue)
   GPU 4: 1000000/46068 MiB, 100% busy  -> BUSY, not a queue task (another user, or ours started outside the queue)   (not allowed)
   GPU 5: 1000000/46068 MiB, 100% busy  -> BUSY, not a queue task (another user, or ours started outside the queue)   (not allowed)
   GPU 6: 1000000/46068 MiB, 100% busy  -> BUSY, not a queue task (another user, or ours started outside the queue)   (not allowed)
   GPU 7: 1000000/46068 MiB, 100% busy  -> BUSY, not a queue task (another user, or ours started outside the queue)   (not allowed)
   queue5 lane processes: 
   tasks: 2290 done, 47 running, 1360 pending, 101 on hold

RUNNING
  A40-fetch-ar2_pw-e30 shell       GPU None  attempt 1  since 11-28 03:37  [pool]    last write 3 min ago
  A40-fetch-ranking_drop-e30 shell       GPU None  attempt 1  since 11-27 11:26  [pool]    last write 2 min ago
  A40-fetch-rearr_pw_long_s18-e60 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-rearr_pw_long-e60 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-rearr_pw_h100_s18-e30 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-rearr_pw_h100-e30 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-rearr_pw_h100_long_s18-e60 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-rearr_pw_h100_long-e60 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-obs_cf800-e10 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-rearr_joint3-e30 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-swapT_joint3_ow-e30 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-press_cd-e30 shell       GPU None  attempt 1  since 11-28 16:58  [pool]    last write 4 min ago
  A40-fetch-swapT_ow-e30 shell       GPU None  attempt 1  since 11-28 16:28  [pool]    last write 3 min ago
  A40-fetch-swapT_ow_s18-e30 shell       GPU None  attempt 1  since 11-28 16:28  [pool]    last write 3 min ago
  A40-fetch-swapT_ar_ow-e30 shell       GPU None  attempt 1  since 11-28 16:28  [pool]    last write 3 min ago
  A40-fetch-swapT_ar_ow_s18-e30 shell       GPU None  attempt 1  since 11-28 16:28  [pool]    last write 3 min ago
  A40-fetch-press_cd-e10 shell       GPU None  attempt 1  since 11-28 16:58  [pool]    last write 4 min ago
  A40-fetch-press_cd-e20 shell       GPU None  attempt 1  since 11-28 16:58  [pool]    last write 4 min ago
  A40-fetch-rearr_pw_long_s18-e45 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-rearr_pw_long-e45 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-rearr_pw_h100_long_s18-e45 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-rearr_pw_h100_long-e45 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-rearr_ar_pw_s18-e30 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-rearr_arprop_pw_s18-e30 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-rearrange_ar_s18-e30 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-rearrange_arprop_s18-e30 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-ranking_v3a_s18-e30 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-ranking_v3a_s18-e20 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-swapT_joint3_s18-e30 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-rearr_joint3-e10 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-rearr_joint3-e20 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-swapT_joint3_ow-e10 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-swapT_joint3_ow-e20 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-obs_cf800-e5 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-rearr_pw_s19-e30 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-rearr_pw_h100_s19-e30 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-rearr_pw_h100_s20-e30 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-swapT_ar_s18-e30 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-ranking_arprop_s18-e30 shell       GPU None  attempt 1  since 11-28 17:08  [pool]    last write 4 min ago
  A40-fetch-cover_none-e30 shell       GPU None  attempt 1  since 11-24 18:22  [pool]    last write 3 min ago
  A40-fetch-battery_count-e30 shell       GPU None  attempt 2  since 11-22 12:45  [pool]    last write 4 min ago
  A40-fetch-obs_s800_20-e10 shell       GPU None  attempt 1  since 11-27 13:16  [pool]    last write 2 min ago
  A40-fetch-obs_s800_20-e20 shell       GPU None  attempt 1  since 11-27 13:16  [pool]    last write 2 min ago
  A40-fetch-obs_s800_s18-e10 shell       GPU None  attempt 1  since 11-27 13:16  [pool]    last write 2 min ago
  A40-fetch-obs_s1600-e5 shell       GPU None  attempt 1  since 11-27 13:16  [pool]    last write 2 min ago
  A40-fetch-obs_s1600-e10 shell       GPU None  attempt 1  since 11-27 13:16  [pool]    last write 2 min ago
  A40-E22h-fetch-hid2 shell       GPU None  attempt 1  since 11-28 16:58  [pool]    last write 4 min ago

QUEUE (pool lanes, in start order)
  A40-v21-ar2_pw-smoke closed_loop after A40-fetch-ar2_pw-e30
  A40-v21-ar2_pw-swap-s0 closed_loop after A40-v21-ar2_pw-smoke
  A40-v21-ar2_pw-swap-s1 closed_loop after A40-v21-ar2_pw-smoke
  A40-v21-ar2_pw-swap-s2 closed_loop after A40-v21-ar2_pw-smoke
  A40-v21-ar2_pw-swap-s3 closed_loop after A40-v21-ar2_pw-smoke
  A40-v21-ar2_pw-swap-s4 closed_loop after A40-v21-ar2_pw-smoke
  A40-v21-ar2_pw-swap-s5 closed_loop after A40-v21-ar2_pw-smoke
  A40-v21-ar2_pw-swap-s6 closed_loop after A40-v21-ar2_pw-smoke
  A40-v21-ar2_pw-swap-s7 closed_loop after A40-v21-ar2_pw-smoke
  A40-v21-ar2_pw-swap-s8 closed_loop after A40-v21-ar2_pw-smoke
  A40-v21-ar2_pw-swap-s9 closed_loop after A40-v21-ar2_pw-smoke
  A40-v21-ar2_pw-put-s0 closed_loop after A40-v21-ar2_pw-smoke
  A40-v21-ar2_pw-put-s1 closed_loop after A40-v21-ar2_pw-smoke
  A40-v21-ar2_pw-put-s2 closed_loop after A40-v21-ar2_pw-smoke
  A40-v21-ar2_pw-put-s3 closed_loop after A40-v21-ar2_pw-smoke
  A40-v21-ar2_pw-put-s4 closed_loop after A40-v21-ar2_pw-smoke
  A40-v21-ar2_pw-put-s5 closed_loop after A40-v21-ar2_pw-smoke
  A40-v21-ar2_pw-put-s6 closed_loop after A40-v21-ar2_pw-smoke
  A40-v21-ar2_pw-put-s7 closed_loop after A40-v21-ar2_pw-smoke
  A40-v21-ar2_pw-put-s8 closed_loop after A40-v21-ar2_pw-smoke
  A40-v21-ar2_pw-put-s9 closed_loop after A40-v21-ar2_pw-smoke
  A40-V21-C23-verdict shell       after A40-v21-ar2_pw-swap-s0, A40-v21-ar2_pw-swap-s1, A40-v21-ar2_pw-swap-s2, A40-v21-ar2_pw-swap-s3, A40-v21-ar2_pw-swap-s4, A40-v21-ar2_pw-swap-s5, A40-v21-ar2_pw-swap-s6, A40-v21-ar2_pw-swap-s7, A40-v21-ar2_pw-swap-s8, A40-v21-ar2_pw-swap-s9, A40-v21-ar2_pw-put-s0, A40-v21-ar2_pw-put-s1, A40-v21-ar2_pw-put-s2, A40-v21-ar2_pw-put-s3, A40-v21-ar2_pw-put-s4, A40-v21-ar2_pw-put-s5, A40-v21-ar2_pw-put-s6, A40-v21-ar2_pw-put-s7, A40-v21-ar2_pw-put-s8, A40-v21-ar2_pw-put-s9
  A40-V21-C23-gate-r2 shell       after A40-V21-C23-verdict
  A40-v21-ar2_pw-r2-swap-s0 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_pw-r2-swap-s1 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_pw-r2-swap-s2 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_pw-r2-swap-s3 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_pw-r2-swap-s4 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_pw-r2-swap-s5 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_pw-r2-swap-s6 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_pw-r2-swap-s7 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_pw-r2-swap-s8 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_pw-r2-swap-s9 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_v3c-r2-swap-s0 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_v3c-r2-swap-s1 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_v3c-r2-swap-s2 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_v3c-r2-swap-s3 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_v3c-r2-swap-s4 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_v3c-r2-swap-s5 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_v3c-r2-swap-s6 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_v3c-r2-swap-s7 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_v3c-r2-swap-s8 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_v3c-r2-swap-s9 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_pw-r2-put-s0 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_pw-r2-put-s1 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_pw-r2-put-s2 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_pw-r2-put-s3 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_pw-r2-put-s4 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_pw-r2-put-s5 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_pw-r2-put-s6 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_pw-r2-put-s7 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_pw-r2-put-s8 closed_loop after A40-V21-C23-gate-r2
  A40-v21-ar2_pw-r2-put-s9 closed_loop after A40-V21-C23-gate-r2
  A40-V21-C23-ext-verdict shell       after A40-v21-ar2_pw-r2-swap-s0, A40-v21-ar2_pw-r2-swap-s1, A40-v21-ar2_pw-r2-swap-s2, A40-v21-ar2_pw-r2-swap-s3, A40-v21-ar2_pw-r2-swap-s4, A40-v21-ar2_pw-r2-swap-s5, A40-v21-ar2_pw-r2-swap-s6, A40-v21-ar2_pw-r2-swap-s7, A40-v21-ar2_pw-r2-swap-s8, A40-v21-ar2_pw-r2-swap-s9, A40-v21-ar2_v3c-r2-swap-s0, A40-v21-ar2_v3c-r2-swap-s1, A40-v21-ar2_v3c-r2-swap-s2, A40-v21-ar2_v3c-r2-swap-s3, A40-v21-ar2_v3c-r2-swap-s4, A40-v21-ar2_v3c-r2-swap-s5, A40-v21-ar2_v3c-r2-swap-s6, A40-v21-ar2_v3c-r2-swap-s7, A40-v21-ar2_v3c-r2-swap-s8, A40-v21-ar2_v3c-r2-swap-s9, A40-v21-ar2_pw-r2-put-s0, A40-v21-ar2_pw-r2-put-s1, A40-v21-ar2_pw-r2-put-s2, A40-v21-ar2_pw-r2-put-s3, A40-v21-ar2_pw-r2-put-s4, A40-v21-ar2_pw-r2-put-s5, A40-v21-ar2_pw-r2-put-s6, A40-v21-ar2_pw-r2-put-s7, A40-v21-ar2_pw-r2-put-s8, A40-v21-ar2_pw-r2-put-s9
  A40-v21-ranking_drop-smoke closed_loop on hold
  A40-v21-ranking_drop-s0 closed_loop on hold
  A40-v21-ranking_drop-s1 closed_loop on hold
  A40-v21-ranking_drop-s2 closed_loop on hold
  A40-v21-ranking_drop-s3 closed_loop on hold
  A40-v21-ranking_drop-s4 closed_loop on hold
  A40-v21-ranking_drop-s5 closed_loop on hold
  A40-v21-ranking_drop-s6 closed_loop on hold
  A40-v21-ranking_drop-s7 closed_loop on hold
  A40-v21-ranking_drop-s8 closed_loop on hold
  A40-v21-ranking_drop-s9 closed_loop on hold
  A40-V21-C24B-verdict shell       on hold
  A40-v22-rearr_pw_long_s18-e60-smoke closed_loop after A40-fetch-rearr_pw_long_s18-e60
  A40-v22-rearr_pw_long_s18-e60-rearr-s0 closed_loop after A40-v22-rearr_pw_long_s18-e60-smoke
  A40-v22-rearr_pw_long_s18-e60-rearr-s1 closed_loop after A40-v22-rearr_pw_long_s18-e60-smoke
  A40-v22-rearr_pw_long_s18-e60-rearr-s2 closed_loop after A40-v22-rearr_pw_long_s18-e60-smoke
  A40-v22-rearr_pw_long_s18-e60-rearr-s3 closed_loop after A40-v22-rearr_pw_long_s18-e60-smoke
  A40-v22-rearr_pw_long_s18-e60-rearr-s4 closed_loop after A40-v22-rearr_pw_long_s18-e60-smoke
  A40-v22-rearr_pw_long_s18-e60-rearr-s5 closed_loop after A40-v22-rearr_pw_long_s18-e60-smoke
  A40-v22-rearr_pw_long_s18-e60-rearr-s6 closed_loop after A40-v22-rearr_pw_long_s18-e60-smoke
  A40-v22-rearr_pw_long_s18-e60-rearr-s7 closed_loop after A40-v22-rearr_pw_long_s18-e60-smoke
  A40-v22-rearr_pw_long_s18-e60-rearr-s8 closed_loop after A40-v22-rearr_pw_long_s18-e60-smoke
  A40-v22-rearr_pw_long_s18-e60-rearr-s9 closed_loop after A40-v22-rearr_pw_long_s18-e60-smoke
  A40-V22-C27-s18    shell       after A40-v22-rearr_pw_long_s18-e60-rearr-s0, A40-v22-rearr_pw_long_s18-e60-rearr-s1, A40-v22-rearr_pw_long_s18-e60-rearr-s2, A40-v22-rearr_pw_long_s18-e60-rearr-s3, A40-v22-rearr_pw_long_s18-e60-rearr-s4, A40-v22-rearr_pw_long_s18-e60-rearr-s5, A40-v22-rearr_pw_long_s18-e60-rearr-s6, A40-v22-rearr_pw_long_s18-e60-rearr-s7, A40-v22-rearr_pw_long_s18-e60-rearr-s8, A40-v22-rearr_pw_long_s18-e60-rearr-s9
  A40-v22-rearr_pw_long-e60-smoke closed_loop after A40-fetch-rearr_pw_long-e60
  A40-v22-rearr_pw_long-e60-rearr-s0 closed_loop after A40-v22-rearr_pw_long-e60-smoke
  A40-v22-rearr_pw_long-e60-rearr-s1 closed_loop after A40-v22-rearr_pw_long-e60-smoke
  A40-v22-rearr_pw_long-e60-rearr-s2 closed_loop after A40-v22-rearr_pw_long-e60-smoke
  A40-v22-rearr_pw_long-e60-rearr-s3 closed_loop after A40-v22-rearr_pw_long-e60-smoke
  A40-v22-rearr_pw_long-e60-rearr-s4 closed_loop after A40-v22-rearr_pw_long-e60-smoke
  A40-v22-rearr_pw_long-e60-rearr-s5 closed_loop after A40-v22-rearr_pw_long-e60-smoke
  A40-v22-rearr_pw_long-e60-rearr-s6 closed_loop after A40-v22-rearr_pw_long-e60-smoke
  A40-v22-rearr_pw_long-e60-rearr-s7 closed_loop after A40-v22-rearr_pw_long-e60-smoke
  A40-v22-rearr_pw_long-e60-rearr-s8 closed_loop after A40-v22-rearr_pw_long-e60-smoke
  A40-v22-rearr_pw_long-e60-rearr-s9 closed_loop after A40-v22-rearr_pw_long-e60-smoke
  A40-V22-C27-verdict shell       after A40-v22-rearr_pw_long-e60-rearr-s0, A40-v22-rearr_pw_long-e60-rearr-s1, A40-v22-rearr_pw_long-e60-rearr-s2, A40-v22-rearr_pw_long-e60-rearr-s3, A40-v22-rearr_pw_long-e60-rearr-s4, A40-v22-rearr_pw_long-e60-rearr-s5, A40-v22-rearr_pw_long-e60-rearr-s6, A40-v22-rearr_pw_long-e60-rearr-s7, A40-v22-rearr_pw_long-e60-rearr-s8, A40-v22-rearr_pw_long-e60-rearr-s9, A40-v22-rearr_pw_long_s18-e60-rearr-s0, A40-v22-rearr_pw_long_s18-e60-rearr-s1, A40-v22-rearr_pw_long_s18-e60-rearr-s2, A40-v22-rearr_pw_long_s18-e60-rearr-s3, A40-v22-rearr_pw_long_s18-e60-rearr-s4, A40-v22-rearr_pw_long_s18-e60-rearr-s5, A40-v22-rearr_pw_long_s18-e60-rearr-s6, A40-v22-rearr_pw_long_s18-e60-rearr-s7, A40-v22-rearr_pw_long_s18-e60-rearr-s8, A40-v22-rearr_pw_long_s18-e60-rearr-s9
  A40-V22-C27-gate-r2 shell       after A40-V22-C27-verdict
  A40-v22r2-rearr_pw_long_s18-e60-rearr-s0 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_long_s18-e60-rearr-s1 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_long_s18-e60-rearr-s2 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_long_s18-e60-rearr-s3 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_long_s18-e60-rearr-s4 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_long_s18-e60-rearr-s5 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_long_s18-e60-rearr-s6 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_long_s18-e60-rearr-s7 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_long_s18-e60-rearr-s8 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_long_s18-e60-rearr-s9 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_long-e60-rearr-s0 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_long-e60-rearr-s1 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_long-e60-rearr-s2 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_long-e60-rearr-s3 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_long-e60-rearr-s4 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_long-e60-rearr-s5 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_long-e60-rearr-s6 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_long-e60-rearr-s7 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_long-e60-rearr-s8 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_long-e60-rearr-s9 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_s18-e30-rearr-s0 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_s18-e30-rearr-s1 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_s18-e30-rearr-s2 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_s18-e30-rearr-s3 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_s18-e30-rearr-s4 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_s18-e30-rearr-s5 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_s18-e30-rearr-s6 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_s18-e30-rearr-s7 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_s18-e30-rearr-s8 closed_loop after A40-V22-C27-gate-r2
  A40-v22r2-rearr_pw_s18-e30-rearr-s9 closed_loop after A40-V22-C27-gate-r2
  A40-V22-C27-ext-verdict shell       after A40-v22r2-rearr_pw_long_s18-e60-rearr-s0, A40-v22r2-rearr_pw_long_s18-e60-rearr-s1, A40-v22r2-rearr_pw_long_s18-e60-rearr-s2, A40-v22r2-rearr_pw_long_s18-e60-rearr-s3, A40-v22r2-rearr_pw_long_s18-e60-rearr-s4, A40-v22r2-rearr_pw_long_s18-e60-rearr-s5, A40-v22r2-rearr_pw_long_s18-e60-rearr-s6, A40-v22r2-rearr_pw_long_s18-e60-rearr-s7, A40-v22r2-rearr_pw_long_s18-e60-rearr-s8, A40-v22r2-rearr_pw_long_s18-e60-rearr-s9, A40-v22r2-rearr_pw_long-e60-rearr-s0, A40-v22r2-rearr_pw_long-e60-rearr-s1, A40-v22r2-rearr_pw_long-e60-rearr-s2, A40-v22r2-rearr_pw_long-e60-rearr-s3, A40-v22r2-rearr_pw_long-e60-rearr-s4, A40-v22r2-rearr_pw_long-e60-rearr-s5, A40-v22r2-rearr_pw_long-e60-rearr-s6, A40-v22r2-rearr_pw_long-e60-rearr-s7, A40-v22r2-rearr_pw_long-e60-rearr-s8, A40-v22r2-rearr_pw_long-e60-rearr-s9, A40-v22r2-rearr_pw_s18-e30-rearr-s0, A40-v22r2-rearr_pw_s18-e30-rearr-s1, A40-v22r2-rearr_pw_s18-e30-rearr-s2, A40-v22r2-rearr_pw_s18-e30-rearr-s3, A40-v22r2-rearr_pw_s18-e30-rearr-s4, A40-v22r2-rearr_pw_s18-e30-rearr-s5, A40-v22r2-rearr_pw_s18-e30-rearr-s6, A40-v22r2-rearr_pw_s18-e30-rearr-s7, A40-v22r2-rearr_pw_s18-e30-rearr-s8, A40-v22r2-rearr_pw_s18-e30-rearr-s9
  A40-v22-rearr_pw_h100_s18-e30-smoke closed_loop after A40-fetch-rearr_pw_h100_s18-e30
  A40-v22-rearr_pw_h100_s18-e30-rearr-s0 closed_loop after A40-v22-rearr_pw_h100_s18-e30-smoke
  A40-v22-rearr_pw_h100_s18-e30-rearr-s1 closed_loop after A40-v22-rearr_pw_h100_s18-e30-smoke
  A40-v22-rearr_pw_h100_s18-e30-rearr-s2 closed_loop after A40-v22-rearr_pw_h100_s18-e30-smoke
  A40-v22-rearr_pw_h100_s18-e30-rearr-s3 closed_loop after A40-v22-rearr_pw_h100_s18-e30-smoke
  A40-v22-rearr_pw_h100_s18-e30-rearr-s4 closed_loop after A40-v22-rearr_pw_h100_s18-e30-smoke
  A40-v22-rearr_pw_h100_s18-e30-rearr-s5 closed_loop after A40-v22-rearr_pw_h100_s18-e30-smoke
  A40-v22-rearr_pw_h100_s18-e30-rearr-s6 closed_loop after A40-v22-rearr_pw_h100_s18-e30-smoke
  A40-v22-rearr_pw_h100_s18-e30-rearr-s7 closed_loop after A40-v22-rearr_pw_h100_s18-e30-smoke
  A40-v22-rearr_pw_h100_s18-e30-rearr-s8 closed_loop after A40-v22-rearr_pw_h100_s18-e30-smoke
  A40-v22-rearr_pw_h100_s18-e30-rearr-s9 closed_loop after A40-v22-rearr_pw_h100_s18-e30-smoke
  A40-v22-rearr_pw_h100-e30-smoke closed_loop after A40-fetch-rearr_pw_h100-e30
  A40-v22-rearr_pw_h100-e30-rearr-s0 closed_loop after A40-v22-rearr_pw_h100-e30-smoke
  A40-v22-rearr_pw_h100-e30-rearr-s1 closed_loop after A40-v22-rearr_pw_h100-e30-smoke
  A40-v22-rearr_pw_h100-e30-rearr-s2 closed_loop after A40-v22-rearr_pw_h100-e30-smoke
  A40-v22-rearr_pw_h100-e30-rearr-s3 closed_loop after A40-v22-rearr_pw_h100-e30-smoke
  A40-v22-rearr_pw_h100-e30-rearr-s4 closed_loop after A40-v22-rearr_pw_h100-e30-smoke
  A40-v22-rearr_pw_h100-e30-rearr-s5 closed_loop after A40-v22-rearr_pw_h100-e30-smoke
  A40-v22-rearr_pw_h100-e30-rearr-s6 closed_loop after A40-v22-rearr_pw_h100-e30-smoke
  A40-v22-rearr_pw_h100-e30-rearr-s7 closed_loop after A40-v22-rearr_pw_h100-e30-smoke
  A40-v22-rearr_pw_h100-e30-rearr-s8 closed_loop after A40-v22-rearr_pw_h100-e30-smoke
  A40-v22-rearr_pw_h100-e30-rearr-s9 closed_loop after A40-v22-rearr_pw_h100-e30-smoke
  A40-v22-rearr_pw_h100_long_s18-e60-smoke closed_loop after A40-fetch-rearr_pw_h100_long_s18-e60
  A40-v22-rearr_pw_h100_long_s18-e60-rearr-s0 closed_loop after A40-v22-rearr_pw_h100_long_s18-e60-smoke
  A40-v22-rearr_pw_h100_long_s18-e60-rearr-s1 closed_loop after A40-v22-rearr_pw_h100_long_s18-e60-smoke
  A40-v22-rearr_pw_h100_long_s18-e60-rearr-s2 closed_loop after A40-v22-rearr_pw_h100_long_s18-e60-smoke
  A40-v22-rearr_pw_h100_long_s18-e60-rearr-s3 closed_loop after A40-v22-rearr_pw_h100_long_s18-e60-smoke
  A40-v22-rearr_pw_h100_long_s18-e60-rearr-s4 closed_loop after A40-v22-rearr_pw_h100_long_s18-e60-smoke
  A40-v22-rearr_pw_h100_long_s18-e60-rearr-s5 closed_loop after A40-v22-rearr_pw_h100_long_s18-e60-smoke
  A40-v22-rearr_pw_h100_long_s18-e60-rearr-s6 closed_loop after A40-v22-rearr_pw_h100_long_s18-e60-smoke
  A40-v22-rearr_pw_h100_long_s18-e60-rearr-s7 closed_loop after A40-v22-rearr_pw_h100_long_s18-e60-smoke
  A40-v22-rearr_pw_h100_long_s18-e60-rearr-s8 closed_loop after A40-v22-rearr_pw_h100_long_s18-e60-smoke
  A40-v22-rearr_pw_h100_long_s18-e60-rearr-s9 closed_loop after A40-v22-rearr_pw_h100_long_s18-e60-smoke
  A40-V22-C27B-s18   shell       after A40-v22-rearr_pw_h100_long_s18-e60-rearr-s0, A40-v22-rearr_pw_h100_long_s18-e60-rearr-s1, A40-v22-rearr_pw_h100_long_s18-e60-rearr-s2, A40-v22-rearr_pw_h100_long_s18-e60-rearr-s3, A40-v22-rearr_pw_h100_long_s18-e60-rearr-s4, A40-v22-rearr_pw_h100_long_s18-e60-rearr-s5, A40-v22-rearr_pw_h100_long_s18-e60-rearr-s6, A40-v22-rearr_pw_h100_long_s18-e60-rearr-s7, A40-v22-rearr_pw_h100_long_s18-e60-rearr-s8, A40-v22-rearr_pw_h100_long_s18-e60-rearr-s9, A40-v22-rearr_pw_h100_s18-e30-rearr-s0, A40-v22-rearr_pw_h100_s18-e30-rearr-s1, A40-v22-rearr_pw_h100_s18-e30-rearr-s2, A40-v22-rearr_pw_h100_s18-e30-rearr-s3, A40-v22-rearr_pw_h100_s18-e30-rearr-s4, A40-v22-rearr_pw_h100_s18-e30-rearr-s5, A40-v22-rearr_pw_h100_s18-e30-rearr-s6, A40-v22-rearr_pw_h100_s18-e30-rearr-s7, A40-v22-rearr_pw_h100_s18-e30-rearr-s8, A40-v22-rearr_pw_h100_s18-e30-rearr-s9
  A40-v22-rearr_pw_h100_long-e60-smoke closed_loop after A40-fetch-rearr_pw_h100_long-e60
  A40-v22-rearr_pw_h100_long-e60-rearr-s0 closed_loop after A40-v22-rearr_pw_h100_long-e60-smoke
  A40-v22-rearr_pw_h100_long-e60-rearr-s1 closed_loop after A40-v22-rearr_pw_h100_long-e60-smoke
  A40-v22-rearr_pw_h100_long-e60-rearr-s2 closed_loop after A40-v22-rearr_pw_h100_long-e60-smoke
  A40-v22-rearr_pw_h100_long-e60-rearr-s3 closed_loop after A40-v22-rearr_pw_h100_long-e60-smoke
  A40-v22-rearr_pw_h100_long-e60-rearr-s4 closed_loop after A40-v22-rearr_pw_h100_long-e60-smoke
  A40-v22-rearr_pw_h100_long-e60-rearr-s5 closed_loop after A40-v22-rearr_pw_h100_long-e60-smoke
  A40-v22-rearr_pw_h100_long-e60-rearr-s6 closed_loop after A40-v22-rearr_pw_h100_long-e60-smoke
  A40-v22-rearr_pw_h100_long-e60-rearr-s7 closed_loop after A40-v22-rearr_pw_h100_long-e60-smoke
  A40-v22-rearr_pw_h100_long-e60-rearr-s8 closed_loop after A40-v22-rearr_pw_h100_long-e60-smoke
  A40-v22-rearr_pw_h100_long-e60-rearr-s9 closed_loop after A40-v22-rearr_pw_h100_long-e60-smoke
  A40-V22-C27B-verdict shell       after A40-v22-rearr_pw_h100_long-e60-rearr-s0, A40-v22-rearr_pw_h100_long-e60-rearr-s1, A40-v22-rearr_pw_h100_long-e60-rearr-s2, A40-v22-rearr_pw_h100_long-e60-rearr-s3, A40-v22-rearr_pw_h100_long-e60-rearr-s4, A40-v22-rearr_pw_h100_long-e60-rearr-s5, A40-v22-rearr_pw_h100_long-e60-rearr-s6, A40-v22-rearr_pw_h100_long-e60-rearr-s7, A40-v22-rearr_pw_h100_long-e60-rearr-s8, A40-v22-rearr_pw_h100_long-e60-rearr-s9, A40-v22-rearr_pw_h100_long_s18-e60-rearr-s0, A40-v22-rearr_pw_h100_long_s18-e60-rearr-s1, A40-v22-rearr_pw_h100_long_s18-e60-rearr-s2, A40-v22-rearr_pw_h100_long_s18-e60-rearr-s3, A40-v22-rearr_pw_h100_long_s18-e60-rearr-s4, A40-v22-rearr_pw_h100_long_s18-e60-rearr-s5, A40-v22-rearr_pw_h100_long_s18-e60-rearr-s6, A40-v22-rearr_pw_h100_long_s18-e60-rearr-s7, A40-v22-rearr_pw_h100_long_s18-e60-rearr-s8, A40-v22-rearr_pw_h100_long_s18-e60-rearr-s9, A40-v22-rearr_pw_h100_s18-e30-rearr-s0, A40-v22-rearr_pw_h100_s18-e30-rearr-s1, A40-v22-rearr_pw_h100_s18-e30-rearr-s2, A40-v22-rearr_pw_h100_s18-e30-rearr-s3, A40-v22-rearr_pw_h100_s18-e30-rearr-s4, A40-v22-rearr_pw_h100_s18-e30-rearr-s5, A40-v22-rearr_pw_h100_s18-e30-rearr-s6, A40-v22-rearr_pw_h100_s18-e30-rearr-s7, A40-v22-rearr_pw_h100_s18-e30-rearr-s8, A40-v22-rearr_pw_h100_s18-e30-rearr-s9, A40-v22-rearr_pw_h100-e30-rearr-s0, A40-v22-rearr_pw_h100-e30-rearr-s1, A40-v22-rearr_pw_h100-e30-rearr-s2, A40-v22-rearr_pw_h100-e30-rearr-s3, A40-v22-rearr_pw_h100-e30-rearr-s4, A40-v22-rearr_pw_h100-e30-rearr-s5, A40-v22-rearr_pw_h100-e30-rearr-s6, A40-v22-rearr_pw_h100-e30-rearr-s7, A40-v22-rearr_pw_h100-e30-rearr-s8, A40-v22-rearr_pw_h100-e30-rearr-s9
  A40-v22-obs_cf800-e10-smoke closed_loop after A40-fetch-obs_cf800-e10
  A40-v22-obs_cf800-e10-obs-s0 closed_loop after A40-v22-obs_cf800-e10-smoke
  A40-v22-obs_cf800-e10-obs-s1 closed_loop after A40-v22-obs_cf800-e10-smoke
  A40-v22-obs_cf800-e10-obs-s2 closed_loop after A40-v22-obs_cf800-e10-smoke
  A40-v22-obs_cf800-e10-obs-s3 closed_loop after A40-v22-obs_cf800-e10-smoke
  A40-v22-obs_cf800-e10-obs-s4 closed_loop after A40-v22-obs_cf800-e10-smoke
  A40-v22-obs_cf800-e10-obs-s5 closed_loop after A40-v22-obs_cf800-e10-smoke
  A40-v22-obs_cf800-e10-obs-s6 closed_loop after A40-v22-obs_cf800-e10-smoke
  A40-v22-obs_cf800-e10-obs-s7 closed_loop after A40-v22-obs_cf800-e10-smoke
  A40-v22-obs_cf800-e10-obs-s8 closed_loop after A40-v22-obs_cf800-e10-smoke
  A40-v22-obs_cf800-e10-obs-s9 closed_loop after A40-v22-obs_cf800-e10-smoke
  A40-V22-C30-verdict shell       after A40-v22-obs_cf800-e10-obs-s0, A40-v22-obs_cf800-e10-obs-s1, A40-v22-obs_cf800-e10-obs-s2, A40-v22-obs_cf800-e10-obs-s3, A40-v22-obs_cf800-e10-obs-s4, A40-v22-obs_cf800-e10-obs-s5, A40-v22-obs_cf800-e10-obs-s6, A40-v22-obs_cf800-e10-obs-s7, A40-v22-obs_cf800-e10-obs-s8, A40-v22-obs_cf800-e10-obs-s9
  A40-V22-C30-gate-r2 shell       after A40-V22-C30-verdict
  A40-v22r2-obs_cf800-e10-obs-s0 closed_loop after A40-V22-C30-gate-r2
  A40-v22r2-obs_cf800-e10-obs-s1 closed_loop after A40-V22-C30-gate-r2
  A40-v22r2-obs_cf800-e10-obs-s2 closed_loop after A40-V22-C30-gate-r2
  A40-v22r2-obs_cf800-e10-obs-s3 closed_loop after A40-V22-C30-gate-r2
  A40-v22r2-obs_cf800-e10-obs-s4 closed_loop after A40-V22-C30-gate-r2
  A40-v22r2-obs_cf800-e10-obs-s5 closed_loop after A40-V22-C30-gate-r2
  A40-v22r2-obs_cf800-e10-obs-s6 closed_loop after A40-V22-C30-gate-r2
  A40-v22r2-obs_cf800-e10-obs-s7 closed_loop after A40-V22-C30-gate-r2
  A40-v22r2-obs_cf800-e10-obs-s8 closed_loop after A40-V22-C30-gate-r2
  A40-v22r2-obs_cf800-e10-obs-s9 closed_loop after A40-V22-C30-gate-r2
  A40-v22r2-obs_s800-e10-obs-s0 closed_loop after A40-V22-C30-gate-r2
  A40-v22r2-obs_s800-e10-obs-s1 closed_loop after A40-V22-C30-gate-r2
  A40-v22r2-obs_s800-e10-obs-s2 closed_loop after A40-V22-C30-gate-r2
  A40-v22r2-obs_s800-e10-obs-s3 closed_loop after A40-V22-C30-gate-r2
  A40-v22r2-obs_s800-e10-obs-s4 closed_loop after A40-V22-C30-gate-r2
  A40-v22r2-obs_s800-e10-obs-s5 closed_loop after A40-V22-C30-gate-r2
  A40-v22r2-obs_s800-e10-obs-s6 closed_loop after A40-V22-C30-gate-r2
  A40-v22r2-obs_s800-e10-obs-s7 closed_loop after A40-V22-C30-gate-r2
  A40-v22r2-obs_s800-e10-obs-s8 closed_loop after A40-V22-C30-gate-r2
  A40-v22r2-obs_s800-e10-obs-s9 closed_loop after A40-V22-C30-gate-r2
  A40-V22-C30-ext-verdict shell       after A40-v22r2-obs_cf800-e10-obs-s0, A40-v22r2-obs_cf800-e10-obs-s1, A40-v22r2-obs_cf800-e10-obs-s2, A40-v22r2-obs_cf800-e10-obs-s3, A40-v22r2-obs_cf800-e10-obs-s4, A40-v22r2-obs_cf800-e10-obs-s5, A40-v22r2-obs_cf800-e10-obs-s6, A40-v22r2-obs_cf800-e10-obs-s7, A40-v22r2-obs_cf800-e10-obs-s8, A40-v22r2-obs_cf800-e10-obs-s9, A40-v22r2-obs_s800-e10-obs-s0, A40-v22r2-obs_s800-e10-obs-s1, A40-v22r2-obs_s800-e10-obs-s2, A40-v22r2-obs_s800-e10-obs-s3, A40-v22r2-obs_s800-e10-obs-s4, A40-v22r2-obs_s800-e10-obs-s5, A40-v22r2-obs_s800-e10-obs-s6, A40-v22r2-obs_s800-e10-obs-s7, A40-v22r2-obs_s800-e10-obs-s8, A40-v22r2-obs_s800-e10-obs-s9
  A40-v22-rearr_joint3-e30-smoke closed_loop after A40-fetch-rearr_joint3-e30
  A40-v22-rearr_joint3-e30-rearr-s0 closed_loop after A40-v22-rearr_joint3-e30-smoke
  A40-v22-rearr_joint3-e30-rearr-s1 closed_loop after A40-v22-rearr_joint3-e30-smoke
  A40-v22-rearr_joint3-e30-rearr-s2 closed_loop after A40-v22-rearr_joint3-e30-smoke
  A40-v22-rearr_joint3-e30-rearr-s3 closed_loop after A40-v22-rearr_joint3-e30-smoke
  A40-v22-rearr_joint3-e30-rearr-s4 closed_loop after A40-v22-rearr_joint3-e30-smoke
  A40-v22-rearr_joint3-e30-rearr-s5 closed_loop after A40-v22-rearr_joint3-e30-smoke
  A40-v22-rearr_joint3-e30-rearr-s6 closed_loop after A40-v22-rearr_joint3-e30-smoke
  A40-v22-rearr_joint3-e30-rearr-s7 closed_loop after A40-v22-rearr_joint3-e30-smoke
  A40-v22-rearr_joint3-e30-rearr-s8 closed_loop after A40-v22-rearr_joint3-e30-smoke
  A40-v22-rearr_joint3-e30-rearr-s9 closed_loop after A40-v22-rearr_joint3-e30-smoke
  A40-v22-rearr_joint3-e30-put-s0 closed_loop after A40-fetch-rearr_joint3-e30
  A40-v22-rearr_joint3-e30-put-s1 closed_loop after A40-fetch-rearr_joint3-e30
  A40-v22-rearr_joint3-e30-put-s2 closed_loop after A40-fetch-rearr_joint3-e30
  A40-v22-rearr_joint3-e30-put-s3 closed_loop after A40-fetch-rearr_joint3-e30
  A40-v22-rearr_joint3-e30-put-s4 closed_loop after A40-fetch-rearr_joint3-e30
  A40-v22-rearr_joint3-e30-put-s5 closed_loop after A40-fetch-rearr_joint3-e30
  A40-v22-rearr_joint3-e30-put-s6 closed_loop after A40-fetch-rearr_joint3-e30
  A40-v22-rearr_joint3-e30-put-s7 closed_loop after A40-fetch-rearr_joint3-e30
  A40-v22-rearr_joint3-e30-put-s8 closed_loop after A40-fetch-rearr_joint3-e30
  A40-v22-rearr_joint3-e30-put-s9 closed_loop after A40-fetch-rearr_joint3-e30
  A40-v22-rearr_joint3-e30-swap-s0 closed_loop after A40-fetch-rearr_joint3-e30
  A40-v22-rearr_joint3-e30-swap-s1 closed_loop after A40-fetch-rearr_joint3-e30
  A40-v22-rearr_joint3-e30-swap-s2 closed_loop after A40-fetch-rearr_joint3-e30
  A40-v22-rearr_joint3-e30-swap-s3 closed_loop after A40-fetch-rearr_joint3-e30
  A40-v22-rearr_joint3-e30-swap-s4 closed_loop after A40-fetch-rearr_joint3-e30
  A40-v22-rearr_joint3-e30-swap-s5 closed_loop after A40-fetch-rearr_joint3-e30
  A40-v22-rearr_joint3-e30-swap-s6 closed_loop after A40-fetch-rearr_joint3-e30
  A40-v22-rearr_joint3-e30-swap-s7 closed_loop after A40-fetch-rearr_joint3-e30
  A40-v22-rearr_joint3-e30-swap-s8 closed_loop after A40-fetch-rearr_joint3-e30
  A40-v22-rearr_joint3-e30-swap-s9 closed_loop after A40-fetch-rearr_joint3-e30
  A40-V22-C32-verdict shell       after A40-v22-rearr_joint3-e30-rearr-s0, A40-v22-rearr_joint3-e30-rearr-s1, A40-v22-rearr_joint3-e30-rearr-s2, A40-v22-rearr_joint3-e30-rearr-s3, A40-v22-rearr_joint3-e30-rearr-s4, A40-v22-rearr_joint3-e30-rearr-s5, A40-v22-rearr_joint3-e30-rearr-s6, A40-v22-rearr_joint3-e30-rearr-s7, A40-v22-rearr_joint3-e30-rearr-s8, A40-v22-rearr_joint3-e30-rearr-s9, A40-v22-rearr_joint3-e30-put-s0, A40-v22-rearr_joint3-e30-put-s1, A40-v22-rearr_joint3-e30-put-s2, A40-v22-rearr_joint3-e30-put-s3, A40-v22-rearr_joint3-e30-put-s4, A40-v22-rearr_joint3-e30-put-s5, A40-v22-rearr_joint3-e30-put-s6, A40-v22-rearr_joint3-e30-put-s7, A40-v22-rearr_joint3-e30-put-s8, A40-v22-rearr_joint3-e30-put-s9, A40-v22-rearr_joint3-e30-swap-s0, A40-v22-rearr_joint3-e30-swap-s1, A40-v22-rearr_joint3-e30-swap-s2, A40-v22-rearr_joint3-e30-swap-s3, A40-v22-rearr_joint3-e30-swap-s4, A40-v22-rearr_joint3-e30-swap-s5, A40-v22-rearr_joint3-e30-swap-s6, A40-v22-rearr_joint3-e30-swap-s7, A40-v22-rearr_joint3-e30-swap-s8, A40-v22-rearr_joint3-e30-swap-s9
  A40-V22-C32-gate-r2 shell       after A40-V22-C32-verdict
  A40-v22r2-rearr_joint3-e30-rearr-s0 closed_loop after A40-V22-C32-gate-r2
  A40-v22r2-rearr_joint3-e30-rearr-s1 closed_loop after A40-V22-C32-gate-r2
  A40-v22r2-rearr_joint3-e30-rearr-s2 closed_loop after A40-V22-C32-gate-r2
  A40-v22r2-rearr_joint3-e30-rearr-s3 closed_loop after A40-V22-C32-gate-r2
  A40-v22r2-rearr_joint3-e30-rearr-s4 closed_loop after A40-V22-C32-gate-r2
  A40-v22r2-rearr_joint3-e30-rearr-s5 closed_loop after A40-V22-C32-gate-r2
  A40-v22r2-rearr_joint3-e30-rearr-s6 closed_loop after A40-V22-C32-gate-r2
  A40-v22r2-rearr_joint3-e30-rearr-s7 closed_loop after A40-V22-C32-gate-r2
  A40-v22r2-rearr_joint3-e30-rearr-s8 closed_loop after A40-V22-C32-gate-r2
  A40-v22r2-rearr_joint3-e30-rearr-s9 closed_loop after A40-V22-C32-gate-r2
  A40-v22r2-rearr_v3c_h2-e30-rearr-s0 closed_loop after A40-V22-C32-gate-r2
  A40-v22r2-rearr_v3c_h2-e30-rearr-s1 closed_loop after A40-V22-C32-gate-r2
  A40-v22r2-rearr_v3c_h2-e30-rearr-s2 closed_loop after A40-V22-C32-gate-r2
  A40-v22r2-rearr_v3c_h2-e30-rearr-s3 closed_loop after A40-V22-C32-gate-r2
  A40-v22r2-rearr_v3c_h2-e30-rearr-s4 closed_loop after A40-V22-C32-gate-r2
  A40-v22r2-rearr_v3c_h2-e30-rearr-s5 closed_loop after A40-V22-C32-gate-r2
  A40-v22r2-rearr_v3c_h2-e30-rearr-s6 closed_loop after A40-V22-C32-gate-r2
  A40-v22r2-rearr_v3c_h2-e30-rearr-s7 closed_loop after A40-V22-C32-gate-r2
  A40-v22r2-rearr_v3c_h2-e30-rearr-s8 closed_loop after A40-V22-C32-gate-r2
  A40-v22r2-rearr_v3c_h2-e30-rearr-s9 closed_loop after A40-V22-C32-gate-r2
  A40-V22-C32-ext-verdict shell       after A40-v22r2-rearr_joint3-e30-rearr-s0, A40-v22r2-rearr_joint3-e30-rearr-s1, A40-v22r2-rearr_joint3-e30-rearr-s2, A40-v22r2-rearr_joint3-e30-rearr-s3, A40-v22r2-rearr_joint3-e30-rearr-s4, A40-v22r2-rearr_joint3-e30-rearr-s5, A40-v22r2-rearr_joint3-e30-rearr-s6, A40-v22r2-rearr_joint3-e30-rearr-s7, A40-v22r2-rearr_joint3-e30-rearr-s8, A40-v22r2-rearr_joint3-e30-rearr-s9, A40-v22r2-rearr_v3c_h2-e30-rearr-s0, A40-v22r2-rearr_v3c_h2-e30-rearr-s1, A40-v22r2-rearr_v3c_h2-e30-rearr-s2, A40-v22r2-rearr_v3c_h2-e30-rearr-s3, A40-v22r2-rearr_v3c_h2-e30-rearr-s4, A40-v22r2-rearr_v3c_h2-e30-rearr-s5, A40-v22r2-rearr_v3c_h2-e30-rearr-s6, A40-v22r2-rearr_v3c_h2-e30-rearr-s7, A40-v22r2-rearr_v3c_h2-e30-rearr-s8, A40-v22r2-rearr_v3c_h2-e30-rearr-s9
  A40-v22-swapT_joint3_ow-e30-smoke closed_loop after A40-fetch-swapT_joint3_ow-e30
  A40-v22-swapT_joint3_ow-e30-swapT-s0 closed_loop after A40-v22-swapT_joint3_ow-e30-smoke
  A40-v22-swapT_joint3_ow-e30-swapT-s1 closed_loop after A40-v22-swapT_joint3_ow-e30-smoke
  A40-v22-swapT_joint3_ow-e30-swapT-s2 closed_loop after A40-v22-swapT_joint3_ow-e30-smoke
  A40-v22-swapT_joint3_ow-e30-swapT-s3 closed_loop after A40-v22-swapT_joint3_ow-e30-smoke
  A40-v22-swapT_joint3_ow-e30-swapT-s4 closed_loop after A40-v22-swapT_joint3_ow-e30-smoke
  A40-v22-swapT_joint3_ow-e30-swapT-s5 closed_loop after A40-v22-swapT_joint3_ow-e30-smoke
  A40-v22-swapT_joint3_ow-e30-swapT-s6 closed_loop after A40-v22-swapT_joint3_ow-e30-smoke
  A40-v22-swapT_joint3_ow-e30-swapT-s7 closed_loop after A40-v22-swapT_joint3_ow-e30-smoke
  A40-v22-swapT_joint3_ow-e30-swapT-s8 closed_loop after A40-v22-swapT_joint3_ow-e30-smoke
  A40-v22-swapT_joint3_ow-e30-swapT-s9 closed_loop after A40-v22-swapT_joint3_ow-e30-smoke
  A40-v22-swapT_joint3_ow-e30-put-s0 closed_loop after A40-fetch-swapT_joint3_ow-e30
  A40-v22-swapT_joint3_ow-e30-put-s1 closed_loop after A40-fetch-swapT_joint3_ow-e30
  A40-v22-swapT_joint3_ow-e30-put-s2 closed_loop after A40-fetch-swapT_joint3_ow-e30
  A40-v22-swapT_joint3_ow-e30-put-s3 closed_loop after A40-fetch-swapT_joint3_ow-e30
  A40-v22-swapT_joint3_ow-e30-put-s4 closed_loop after A40-fetch-swapT_joint3_ow-e30
  A40-v22-swapT_joint3_ow-e30-put-s5 closed_loop after A40-fetch-swapT_joint3_ow-e30
  A40-v22-swapT_joint3_ow-e30-put-s6 closed_loop after A40-fetch-swapT_joint3_ow-e30
  A40-v22-swapT_joint3_ow-e30-put-s7 closed_loop after A40-fetch-swapT_joint3_ow-e30
  A40-v22-swapT_joint3_ow-e30-put-s8 closed_loop after A40-fetch-swapT_joint3_ow-e30
  A40-v22-swapT_joint3_ow-e30-put-s9 closed_loop after A40-fetch-swapT_joint3_ow-e30
  A40-v22-swapT_joint3_ow-e30-swap-s0 closed_loop after A40-fetch-swapT_joint3_ow-e30
  A40-v22-swapT_joint3_ow-e30-swap-s1 closed_loop after A40-fetch-swapT_joint3_ow-e30
  A40-v22-swapT_joint3_ow-e30-swap-s2 closed_loop after A40-fetch-swapT_joint3_ow-e30
  A40-v22-swapT_joint3_ow-e30-swap-s3 closed_loop after A40-fetch-swapT_joint3_ow-e30
  A40-v22-swapT_joint3_ow-e30-swap-s4 closed_loop after A40-fetch-swapT_joint3_ow-e30
  A40-v22-swapT_joint3_ow-e30-swap-s5 closed_loop after A40-fetch-swapT_joint3_ow-e30
  A40-v22-swapT_joint3_ow-e30-swap-s6 closed_loop after A40-fetch-swapT_joint3_ow-e30
  A40-v22-swapT_joint3_ow-e30-swap-s7 closed_loop after A40-fetch-swapT_joint3_ow-e30
  A40-v22-swapT_joint3_ow-e30-swap-s8 closed_loop after A40-fetch-swapT_joint3_ow-e30
  A40-v22-swapT_joint3_ow-e30-swap-s9 closed_loop after A40-fetch-swapT_joint3_ow-e30
  A40-V22-C37-verdict shell       after A40-v22-swapT_joint3_ow-e30-swapT-s0, A40-v22-swapT_joint3_ow-e30-swapT-s1, A40-v22-swapT_joint3_ow-e30-swapT-s2, A40-v22-swapT_joint3_ow-e30-swapT-s3, A40-v22-swapT_joint3_ow-e30-swapT-s4, A40-v22-swapT_joint3_ow-e30-swapT-s5, A40-v22-swapT_joint3_ow-e30-swapT-s6, A40-v22-swapT_joint3_ow-e30-swapT-s7, A40-v22-swapT_joint3_ow-e30-swapT-s8, A40-v22-swapT_joint3_ow-e30-swapT-s9, A40-v22-swapT_joint3_ow-e30-put-s0, A40-v22-swapT_joint3_ow-e30-put-s1, A40-v22-swapT_joint3_ow-e30-put-s2, A40-v22-swapT_joint3_ow-e30-put-s3, A40-v22-swapT_joint3_ow-e30-put-s4, A40-v22-swapT_joint3_ow-e30-put-s5, A40-v22-swapT_joint3_ow-e30-put-s6, A40-v22-swapT_joint3_ow-e30-put-s7, A40-v22-swapT_joint3_ow-e30-put-s8, A40-v22-swapT_joint3_ow-e30-put-s9, A40-v22-swapT_joint3_ow-e30-swap-s0, A40-v22-swapT_joint3_ow-e30-swap-s1, A40-v22-swapT_joint3_ow-e30-swap-s2, A40-v22-swapT_joint3_ow-e30-swap-s3, A40-v22-swapT_joint3_ow-e30-swap-s4, A40-v22-swapT_joint3_ow-e30-swap-s5, A40-v22-swapT_joint3_ow-e30-swap-s6, A40-v22-swapT_joint3_ow-e30-swap-s7, A40-v22-swapT_joint3_ow-e30-swap-s8, A40-v22-swapT_joint3_ow-e30-swap-s9
  A40-V22-C37-gate-r2 shell       after A40-V22-C37-verdict
  A40-v22r2-swapT_joint3_ow-e30-swapT-s0 closed_loop after A40-V22-C37-gate-r2
  A40-v22r2-swapT_joint3_ow-e30-swapT-s1 closed_loop after A40-V22-C37-gate-r2
  A40-v22r2-swapT_joint3_ow-e30-swapT-s2 closed_loop after A40-V22-C37-gate-r2
  A40-v22r2-swapT_joint3_ow-e30-swapT-s3 closed_loop after A40-V22-C37-gate-r2
  A40-v22r2-swapT_joint3_ow-e30-swapT-s4 closed_loop after A40-V22-C37-gate-r2
  A40-v22r2-swapT_joint3_ow-e30-swapT-s5 closed_loop after A40-V22-C37-gate-r2
  A40-v22r2-swapT_joint3_ow-e30-swapT-s6 closed_loop after A40-V22-C37-gate-r2
  A40-v22r2-swapT_joint3_ow-e30-swapT-s7 closed_loop after A40-V22-C37-gate-r2
  A40-v22r2-swapT_joint3_ow-e30-swapT-s8 closed_loop after A40-V22-C37-gate-r2
  A40-v22r2-swapT_joint3_ow-e30-swapT-s9 closed_loop after A40-V22-C37-gate-r2
  A40-v22r2-swapT_joint3-e30-swapT-s0 closed_loop after A40-V22-C37-gate-r2
  A40-v22r2-swapT_joint3-e30-swapT-s1 closed_loop after A40-V22-C37-gate-r2
  A40-v22r2-swapT_joint3-e30-swapT-s2 closed_loop after A40-V22-C37-gate-r2
  A40-v22r2-swapT_joint3-e30-swapT-s3 closed_loop after A40-V22-C37-gate-r2
  A40-v22r2-swapT_joint3-e30-swapT-s4 closed_loop after A40-V22-C37-gate-r2
  A40-v22r2-swapT_joint3-e30-swapT-s5 closed_loop after A40-V22-C37-gate-r2
  A40-v22r2-swapT_joint3-e30-swapT-s6 closed_loop after A40-V22-C37-gate-r2
  A40-v22r2-swapT_joint3-e30-swapT-s7 closed_loop after A40-V22-C37-gate-r2
  A40-v22r2-swapT_joint3-e30-swapT-s8 closed_loop after A40-V22-C37-gate-r2
  A40-v22r2-swapT_joint3-e30-swapT-s9 closed_loop after A40-V22-C37-gate-r2
  A40-V22-C37-ext-verdict shell       after A40-v22r2-swapT_joint3_ow-e30-swapT-s0, A40-v22r2-swapT_joint3_ow-e30-swapT-s1, A40-v22r2-swapT_joint3_ow-e30-swapT-s2, A40-v22r2-swapT_joint3_ow-e30-swapT-s3, A40-v22r2-swapT_joint3_ow-e30-swapT-s4, A40-v22r2-swapT_joint3_ow-e30-swapT-s5, A40-v22r2-swapT_joint3_ow-e30-swapT-s6, A40-v22r2-swapT_joint3_ow-e30-swapT-s7, A40-v22r2-swapT_joint3_ow-e30-swapT-s8, A40-v22r2-swapT_joint3_ow-e30-swapT-s9, A40-v22r2-swapT_joint3-e30-swapT-s0, A40-v22r2-swapT_joint3-e30-swapT-s1, A40-v22r2-swapT_joint3-e30-swapT-s2, A40-v22r2-swapT_joint3-e30-swapT-s3, A40-v22r2-swapT_joint3-e30-swapT-s4, A40-v22r2-swapT_joint3-e30-swapT-s5, A40-v22r2-swapT_joint3-e30-swapT-s6, A40-v22r2-swapT_joint3-e30-swapT-s7, A40-v22r2-swapT_joint3-e30-swapT-s8, A40-v22r2-swapT_joint3-e30-swapT-s9
  A40-v22-press_cd-smoke closed_loop after A40-fetch-press_cd-e30
  A40-v22-press_cd-s0 closed_loop after A40-v22-press_cd-smoke
  A40-v22-press_cd-s1 closed_loop after A40-v22-press_cd-smoke
  A40-v22-press_cd-s2 closed_loop after A40-v22-press_cd-smoke
  A40-v22-press_cd-s3 closed_loop after A40-v22-press_cd-smoke
  A40-v22-press_cd-s4 closed_loop after A40-v22-press_cd-smoke
  A40-v22-press_cd-s5 closed_loop after A40-v22-press_cd-smoke
  A40-v22-press_cd-s6 closed_loop after A40-v22-press_cd-smoke
  A40-v22-press_cd-s7 closed_loop after A40-v22-press_cd-smoke
  A40-v22-press_cd-s8 closed_loop after A40-v22-press_cd-smoke
  A40-v22-press_cd-s9 closed_loop after A40-v22-press_cd-smoke
  A40-V22-C31-verdict shell       after A40-v22-press_cd-s0, A40-v22-press_cd-s1, A40-v22-press_cd-s2, A40-v22-press_cd-s3, A40-v22-press_cd-s4, A40-v22-press_cd-s5, A40-v22-press_cd-s6, A40-v22-press_cd-s7, A40-v22-press_cd-s8, A40-v22-press_cd-s9
  A40-V22-C31-gate-r2 shell       after A40-V22-C31-verdict
  A40-v22-c31r2-press_cd_e30-s0 closed_loop after A40-V22-C31-gate-r2
  A40-v22-c31r2-press_cd_e30-s1 closed_loop after A40-V22-C31-gate-r2
  A40-v22-c31r2-press_cd_e30-s2 closed_loop after A40-V22-C31-gate-r2
  A40-v22-c31r2-press_cd_e30-s3 closed_loop after A40-V22-C31-gate-r2
  A40-v22-c31r2-press_cd_e30-s4 closed_loop after A40-V22-C31-gate-r2
  A40-v22-c31r2-press_cd_e30-s5 closed_loop after A40-V22-C31-gate-r2
  A40-v22-c31r2-press_cd_e30-s6 closed_loop after A40-V22-C31-gate-r2
  A40-v22-c31r2-press_cd_e30-s7 closed_loop after A40-V22-C31-gate-r2
  A40-v22-c31r2-press_cd_e30-s8 closed_loop after A40-V22-C31-gate-r2
  A40-v22-c31r2-press_cd_e30-s9 closed_loop after A40-V22-C31-gate-r2
  A40-v22-c31r2-press_told_e30-s0 closed_loop after A40-V22-C31-gate-r2
  A40-v22-c31r2-press_told_e30-s1 closed_loop after A40-V22-C31-gate-r2
  A40-v22-c31r2-press_told_e30-s2 closed_loop after A40-V22-C31-gate-r2
  A40-v22-c31r2-press_told_e30-s3 closed_loop after A40-V22-C31-gate-r2
  A40-v22-c31r2-press_told_e30-s4 closed_loop after A40-V22-C31-gate-r2
  A40-v22-c31r2-press_told_e30-s5 closed_loop after A40-V22-C31-gate-r2
  A40-v22-c31r2-press_told_e30-s6 closed_loop after A40-V22-C31-gate-r2
  A40-v22-c31r2-press_told_e30-s7 closed_loop after A40-V22-C31-gate-r2
  A40-v22-c31r2-press_told_e30-s8 closed_loop after A40-V22-C31-gate-r2
  A40-v22-c31r2-press_told_e30-s9 closed_loop after A40-V22-C31-gate-r2
  A40-V22-C31-ext-verdict shell       after A40-v22-c31r2-press_cd_e30-s0, A40-v22-c31r2-press_cd_e30-s1, A40-v22-c31r2-press_cd_e30-s2, A40-v22-c31r2-press_cd_e30-s3, A40-v22-c31r2-press_cd_e30-s4, A40-v22-c31r2-press_cd_e30-s5, A40-v22-c31r2-press_cd_e30-s6, A40-v22-c31r2-press_cd_e30-s7, A40-v22-c31r2-press_cd_e30-s8, A40-v22-c31r2-press_cd_e30-s9, A40-v22-c31r2-press_told_e30-s0, A40-v22-c31r2-press_told_e30-s1, A40-v22-c31r2-press_told_e30-s2, A40-v22-c31r2-press_told_e30-s3, A40-v22-c31r2-press_told_e30-s4, A40-v22-c31r2-press_told_e30-s5, A40-v22-c31r2-press_told_e30-s6, A40-v22-c31r2-press_told_e30-s7, A40-v22-c31r2-press_told_e30-s8, A40-v22-c31r2-press_told_e30-s9
  A40-v22-swapT_ow-smoke closed_loop after A40-fetch-swapT_ow-e30
  A40-v22-swapT_ow-s0 closed_loop after A40-v22-swapT_ow-smoke
  A40-v22-swapT_ow-s1 closed_loop after A40-v22-swapT_ow-smoke
  A40-v22-swapT_ow-s2 closed_loop after A40-v22-swapT_ow-smoke
  A40-v22-swapT_ow-s3 closed_loop after A40-v22-swapT_ow-smoke
  A40-v22-swapT_ow-s4 closed_loop after A40-v22-swapT_ow-smoke
  A40-v22-swapT_ow-s5 closed_loop after A40-v22-swapT_ow-smoke
  A40-v22-swapT_ow-s6 closed_loop after A40-v22-swapT_ow-smoke
  A40-v22-swapT_ow-s7 closed_loop after A40-v22-swapT_ow-smoke
  A40-v22-swapT_ow-s8 closed_loop after A40-v22-swapT_ow-smoke
  A40-v22-swapT_ow-s9 closed_loop after A40-v22-swapT_ow-smoke
  A40-V22-C36-verdict shell       after A40-v22-swapT_ow-s0, A40-v22-swapT_ow-s1, A40-v22-swapT_ow-s2, A40-v22-swapT_ow-s3, A40-v22-swapT_ow-s4, A40-v22-swapT_ow-s5, A40-v22-swapT_ow-s6, A40-v22-swapT_ow-s7, A40-v22-swapT_ow-s8, A40-v22-swapT_ow-s9
  A40-V22-C36-gate-r2 shell       after A40-V22-C36-verdict
  A40-v22-swapT_ow-r2-s0 closed_loop after A40-V22-C36-gate-r2
  A40-v22-swapT_ow-r2-s1 closed_loop after A40-V22-C36-gate-r2
  A40-v22-swapT_ow-r2-s2 closed_loop after A40-V22-C36-gate-r2
  A40-v22-swapT_ow-r2-s3 closed_loop after A40-V22-C36-gate-r2
  A40-v22-swapT_ow-r2-s4 closed_loop after A40-V22-C36-gate-r2
  A40-v22-swapT_ow-r2-s5 closed_loop after A40-V22-C36-gate-r2
  A40-v22-swapT_ow-r2-s6 closed_loop after A40-V22-C36-gate-r2
  A40-v22-swapT_ow-r2-s7 closed_loop after A40-V22-C36-gate-r2
  A40-v22-swapT_ow-r2-s8 closed_loop after A40-V22-C36-gate-r2
  A40-v22-swapT_ow-r2-s9 closed_loop after A40-V22-C36-gate-r2
  A40-v22-swapT_arprop_h2-r2-s0 closed_loop after A40-V22-C36-gate-r2
  A40-v22-swapT_arprop_h2-r2-s1 closed_loop after A40-V22-C36-gate-r2
  A40-v22-swapT_arprop_h2-r2-s2 closed_loop after A40-V22-C36-gate-r2
  A40-v22-swapT_arprop_h2-r2-s3 closed_loop after A40-V22-C36-gate-r2
  A40-v22-swapT_arprop_h2-r2-s4 closed_loop after A40-V22-C36-gate-r2
  A40-v22-swapT_arprop_h2-r2-s5 closed_loop after A40-V22-C36-gate-r2
  A40-v22-swapT_arprop_h2-r2-s6 closed_loop after A40-V22-C36-gate-r2
  A40-v22-swapT_arprop_h2-r2-s7 closed_loop after A40-V22-C36-gate-r2
  A40-v22-swapT_arprop_h2-r2-s8 closed_loop after A40-V22-C36-gate-r2
  A40-v22-swapT_arprop_h2-r2-s9 closed_loop after A40-V22-C36-gate-r2
  A40-V22-C36-ext-verdict shell       after A40-v22-swapT_ow-r2-s0, A40-v22-swapT_ow-r2-s1, A40-v22-swapT_ow-r2-s2, A40-v22-swapT_ow-r2-s3, A40-v22-swapT_ow-r2-s4, A40-v22-swapT_ow-r2-s5, A40-v22-swapT_ow-r2-s6, A40-v22-swapT_ow-r2-s7, A40-v22-swapT_ow-r2-s8, A40-v22-swapT_ow-r2-s9, A40-v22-swapT_arprop_h2-r2-s0, A40-v22-swapT_arprop_h2-r2-s1, A40-v22-swapT_arprop_h2-r2-s2, A40-v22-swapT_arprop_h2-r2-s3, A40-v22-swapT_arprop_h2-r2-s4, A40-v22-swapT_arprop_h2-r2-s5, A40-v22-swapT_arprop_h2-r2-s6, A40-v22-swapT_arprop_h2-r2-s7, A40-v22-swapT_arprop_h2-r2-s8, A40-v22-swapT_arprop_h2-r2-s9
  A40-v22-swapT_ow_s18-s0 closed_loop after A40-fetch-swapT_ow_s18-e30
  A40-v22-swapT_ow_s18-s1 closed_loop after A40-fetch-swapT_ow_s18-e30
  A40-v22-swapT_ow_s18-s2 closed_loop after A40-fetch-swapT_ow_s18-e30
  A40-v22-swapT_ow_s18-s3 closed_loop after A40-fetch-swapT_ow_s18-e30
  A40-v22-swapT_ow_s18-s4 closed_loop after A40-fetch-swapT_ow_s18-e30
  A40-v22-swapT_ow_s18-s5 closed_loop after A40-fetch-swapT_ow_s18-e30
  A40-v22-swapT_ow_s18-s6 closed_loop after A40-fetch-swapT_ow_s18-e30
  A40-v22-swapT_ow_s18-s7 closed_loop after A40-fetch-swapT_ow_s18-e30
  A40-v22-swapT_ow_s18-s8 closed_loop after A40-fetch-swapT_ow_s18-e30
  A40-v22-swapT_ow_s18-s9 closed_loop after A40-fetch-swapT_ow_s18-e30
  A40-V22-C36-s18-report shell       after A40-v22-swapT_ow_s18-s0, A40-v22-swapT_ow_s18-s1, A40-v22-swapT_ow_s18-s2, A40-v22-swapT_ow_s18-s3, A40-v22-swapT_ow_s18-s4, A40-v22-swapT_ow_s18-s5, A40-v22-swapT_ow_s18-s6, A40-v22-swapT_ow_s18-s7, A40-v22-swapT_ow_s18-s8, A40-v22-swapT_ow_s18-s9, A40-V22-C36-verdict
  A40-v22-swapT_ar_ow-smoke closed_loop after A40-fetch-swapT_ar_ow-e30
  A40-v22-swapT_ar_ow-s0 closed_loop after A40-v22-swapT_ar_ow-smoke
  A40-v22-swapT_ar_ow-s1 closed_loop after A40-v22-swapT_ar_ow-smoke
  A40-v22-swapT_ar_ow-s2 closed_loop after A40-v22-swapT_ar_ow-smoke
  A40-v22-swapT_ar_ow-s3 closed_loop after A40-v22-swapT_ar_ow-smoke
  A40-v22-swapT_ar_ow-s4 closed_loop after A40-v22-swapT_ar_ow-smoke
  A40-v22-swapT_ar_ow-s5 closed_loop after A40-v22-swapT_ar_ow-smoke
  A40-v22-swapT_ar_ow-s6 closed_loop after A40-v22-swapT_ar_ow-smoke
  A40-v22-swapT_ar_ow-s7 closed_loop after A40-v22-swapT_ar_ow-smoke
  A40-v22-swapT_ar_ow-s8 closed_loop after A40-v22-swapT_ar_ow-smoke
  A40-v22-swapT_ar_ow-s9 closed_loop after A40-v22-swapT_ar_ow-smoke
  A40-V22-C36B-verdict shell       after A40-v22-swapT_ar_ow-s0, A40-v22-swapT_ar_ow-s1, A40-v22-swapT_ar_ow-s2, A40-v22-swapT_ar_ow-s3, A40-v22-swapT_ar_ow-s4, A40-v22-swapT_ar_ow-s5, A40-v22-swapT_ar_ow-s6, A40-v22-swapT_ar_ow-s7, A40-v22-swapT_ar_ow-s8, A40-v22-swapT_ar_ow-s9
  A40-V22-C36B-gate-r2 shell       after A40-V22-C36B-verdict
  A40-v22-swapT_ar_ow-r2-s0 closed_loop after A40-V22-C36B-gate-r2
  A40-v22-swapT_ar_ow-r2-s1 closed_loop after A40-V22-C36B-gate-r2
  A40-v22-swapT_ar_ow-r2-s2 closed_loop after A40-V22-C36B-gate-r2
  A40-v22-swapT_ar_ow-r2-s3 closed_loop after A40-V22-C36B-gate-r2
  A40-v22-swapT_ar_ow-r2-s4 closed_loop after A40-V22-C36B-gate-r2
  A40-v22-swapT_ar_ow-r2-s5 closed_loop after A40-V22-C36B-gate-r2
  A40-v22-swapT_ar_ow-r2-s6 closed_loop after A40-V22-C36B-gate-r2
  A40-v22-swapT_ar_ow-r2-s7 closed_loop after A40-V22-C36B-gate-r2
  A40-v22-swapT_ar_ow-r2-s8 closed_loop after A40-V22-C36B-gate-r2
  A40-v22-swapT_ar_ow-r2-s9 closed_loop after A40-V22-C36B-gate-r2
  A40-V22-C36B-ext-verdict shell       after A40-v22-swapT_ar_ow-r2-s0, A40-v22-swapT_ar_ow-r2-s1, A40-v22-swapT_ar_ow-r2-s2, A40-v22-swapT_ar_ow-r2-s3, A40-v22-swapT_ar_ow-r2-s4, A40-v22-swapT_ar_ow-r2-s5, A40-v22-swapT_ar_ow-r2-s6, A40-v22-swapT_ar_ow-r2-s7, A40-v22-swapT_ar_ow-r2-s8, A40-v22-swapT_ar_ow-r2-s9
  A40-v22-swapT_ar_ow_s18-s0 closed_loop after A40-fetch-swapT_ar_ow_s18-e30
  A40-v22-swapT_ar_ow_s18-s1 closed_loop after A40-fetch-swapT_ar_ow_s18-e30
  A40-v22-swapT_ar_ow_s18-s2 closed_loop after A40-fetch-swapT_ar_ow_s18-e30
  A40-v22-swapT_ar_ow_s18-s3 closed_loop after A40-fetch-swapT_ar_ow_s18-e30
  A40-v22-swapT_ar_ow_s18-s4 closed_loop after A40-fetch-swapT_ar_ow_s18-e30
  A40-v22-swapT_ar_ow_s18-s5 closed_loop after A40-fetch-swapT_ar_ow_s18-e30
  A40-v22-swapT_ar_ow_s18-s6 closed_loop after A40-fetch-swapT_ar_ow_s18-e30
  A40-v22-swapT_ar_ow_s18-s7 closed_loop after A40-fetch-swapT_ar_ow_s18-e30
  A40-v22-swapT_ar_ow_s18-s8 closed_loop after A40-fetch-swapT_ar_ow_s18-e30
  A40-v22-swapT_ar_ow_s18-s9 closed_loop after A40-fetch-swapT_ar_ow_s18-e30
  A40-V22-C36B-s18-report shell       after A40-v22-swapT_ar_ow_s18-s0, A40-v22-swapT_ar_ow_s18-s1, A40-v22-swapT_ar_ow_s18-s2, A40-v22-swapT_ar_ow_s18-s3, A40-v22-swapT_ar_ow_s18-s4, A40-v22-swapT_ar_ow_s18-s5, A40-v22-swapT_ar_ow_s18-s6, A40-v22-swapT_ar_ow_s18-s7, A40-v22-swapT_ar_ow_s18-s8, A40-v22-swapT_ar_ow_s18-s9, A40-V22-C36B-verdict
  A40-d8r-press_x16-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])  [6/10 episodes already done]
  A40-d8r-press_x32-s0 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])  [5/10 episodes already done]
  A40-d8r-press_x32-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])  [5/10 episodes already done]
  A40-d8r-press_x32-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d8r-press_x32-s3 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d8r-press_x32-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d8r-press_s50-s0 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d8r-press_s50-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d8r-press_s50-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d8r-press_s50-s3 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d8r-press_s50-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d8r-press-report shell       after A40-d8r-press_x16-s4, A40-d8r-press_x32-s0, A40-d8r-press_x32-s1, A40-d8r-press_x32-s2, A40-d8r-press_x32-s3, A40-d8r-press_x32-s4, A40-d8r-press_s50-s0, A40-d8r-press_s50-s1, A40-d8r-press_s50-s2, A40-d8r-press_s50-s3, A40-d8r-press_s50-s4
  A40-d8r-press_x16-gate shell       after A40-d8r-press-report
  A40-d8r-press_x16-b0 closed_loop after A40-d8r-press_x16-gate
  A40-d8r-press_x16-b1 closed_loop after A40-d8r-press_x16-gate
  A40-d8r-press_x16-b2 closed_loop after A40-d8r-press_x16-gate
  A40-d8r-press_x16-b3 closed_loop after A40-d8r-press_x16-gate
  A40-d8r-press_x16-b4 closed_loop after A40-d8r-press_x16-gate
  A40-d8r-press_x32-gate shell       after A40-d8r-press-report
  A40-d8r-press_x32-b0 closed_loop after A40-d8r-press_x32-gate
  A40-d8r-press_x32-b1 closed_loop after A40-d8r-press_x32-gate
  A40-d8r-press_x32-b2 closed_loop after A40-d8r-press_x32-gate
  A40-d8r-press_x32-b3 closed_loop after A40-d8r-press_x32-gate
  A40-d8r-press_x32-b4 closed_loop after A40-d8r-press_x32-gate
  A40-d8r-press_s50-gate shell       after A40-d8r-press-report
  A40-d8r-press_s50-b0 closed_loop after A40-d8r-press_s50-gate
  A40-d8r-press_s50-b1 closed_loop after A40-d8r-press_s50-gate
  A40-d8r-press_s50-b2 closed_loop after A40-d8r-press_s50-gate
  A40-d8r-press_s50-b3 closed_loop after A40-d8r-press_s50-gate
  A40-d8r-press_s50-b4 closed_loop after A40-d8r-press_s50-gate
  A40-d8r-press-report100 shell       after A40-d8r-press_x16-b0, A40-d8r-press_x16-b1, A40-d8r-press_x16-b2, A40-d8r-press_x16-b3, A40-d8r-press_x16-b4, A40-d8r-press_x32-b0, A40-d8r-press_x32-b1, A40-d8r-press_x32-b2, A40-d8r-press_x32-b3, A40-d8r-press_x32-b4, A40-d8r-press_s50-b0, A40-d8r-press_s50-b1, A40-d8r-press_s50-b2, A40-d8r-press_s50-b3, A40-d8r-press_s50-b4
  A40-d8r-rearr18_x16-s0 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d8r-rearr18_x16-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d8r-rearr18_x16-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d8r-rearr18_x16-s3 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d8r-rearr18_x16-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d8r-rearr18-report shell       after A40-d8r-rearr18_x16-s0, A40-d8r-rearr18_x16-s1, A40-d8r-rearr18_x16-s2, A40-d8r-rearr18_x16-s3, A40-d8r-rearr18_x16-s4
  A40-d8r-rearr18_x16-gate shell       after A40-d8r-rearr18-report
  A40-d8r-rearr18_x16-b0 closed_loop after A40-d8r-rearr18_x16-gate
  A40-d8r-rearr18_x16-b1 closed_loop after A40-d8r-rearr18_x16-gate
  A40-d8r-rearr18_x16-b2 closed_loop after A40-d8r-rearr18_x16-gate
  A40-d8r-rearr18_x16-b3 closed_loop after A40-d8r-rearr18_x16-gate
  A40-d8r-rearr18_x16-b4 closed_loop after A40-d8r-rearr18_x16-gate
  A40-d8r-rearr18-report100 shell       after A40-d8r-rearr18_x16-b0, A40-d8r-rearr18_x16-b1, A40-d8r-rearr18_x16-b2, A40-d8r-rearr18_x16-b3, A40-d8r-rearr18_x16-b4
  A40-d9-rearr_pw_e30-off-s3 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d9-rearr_pw_e30-off-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d9-rearr_pw_s18_e30-off-s0 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d9-rearr_pw_s18_e30-off-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d9-rearr_pw_s18_e30-off-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d9-rearr_pw_s18_e30-off-s3 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d9-rearr_pw_s18_e30-off-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d9r-rearr_pw_e30-off-s0 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d9r-rearr_pw_e30-off-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d9r-rearr_pw_e30-off-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d9-report      shell       after A40-d9r-rearr_pw_e30-off-s0, A40-d9r-rearr_pw_e30-off-s1, A40-d9r-rearr_pw_e30-off-s2, A40-d9-rearr_pw_e30-off-s3, A40-d9-rearr_pw_e30-off-s4, A40-d9-rearr_pw_s18_e30-off-s0, A40-d9-rearr_pw_s18_e30-off-s1, A40-d9-rearr_pw_s18_e30-off-s2, A40-d9-rearr_pw_s18_e30-off-s3, A40-d9-rearr_pw_s18_e30-off-s4
  A40-v22-press_cd-e10-s0 closed_loop after A40-fetch-press_cd-e10, A40-v22-press_cd-smoke
  A40-v22-press_cd-e10-s1 closed_loop after A40-fetch-press_cd-e10, A40-v22-press_cd-smoke
  A40-v22-press_cd-e10-s2 closed_loop after A40-fetch-press_cd-e10, A40-v22-press_cd-smoke
  A40-v22-press_cd-e10-s3 closed_loop after A40-fetch-press_cd-e10, A40-v22-press_cd-smoke
  A40-v22-press_cd-e10-s4 closed_loop after A40-fetch-press_cd-e10, A40-v22-press_cd-smoke
  A40-v22-press_cd-e10-s5 closed_loop after A40-fetch-press_cd-e10, A40-v22-press_cd-smoke
  A40-v22-press_cd-e10-s6 closed_loop after A40-fetch-press_cd-e10, A40-v22-press_cd-smoke
  A40-v22-press_cd-e10-s7 closed_loop after A40-fetch-press_cd-e10, A40-v22-press_cd-smoke
  A40-v22-press_cd-e10-s8 closed_loop after A40-fetch-press_cd-e10, A40-v22-press_cd-smoke
  A40-v22-press_cd-e10-s9 closed_loop after A40-fetch-press_cd-e10, A40-v22-press_cd-smoke
  A40-v22-press_cd-e20-s0 closed_loop after A40-fetch-press_cd-e20, A40-v22-press_cd-smoke
  A40-v22-press_cd-e20-s1 closed_loop after A40-fetch-press_cd-e20, A40-v22-press_cd-smoke
  A40-v22-press_cd-e20-s2 closed_loop after A40-fetch-press_cd-e20, A40-v22-press_cd-smoke
  A40-v22-press_cd-e20-s3 closed_loop after A40-fetch-press_cd-e20, A40-v22-press_cd-smoke
  A40-v22-press_cd-e20-s4 closed_loop after A40-fetch-press_cd-e20, A40-v22-press_cd-smoke
  A40-v22-press_cd-e20-s5 closed_loop after A40-fetch-press_cd-e20, A40-v22-press_cd-smoke
  A40-v22-press_cd-e20-s6 closed_loop after A40-fetch-press_cd-e20, A40-v22-press_cd-smoke
  A40-v22-press_cd-e20-s7 closed_loop after A40-fetch-press_cd-e20, A40-v22-press_cd-smoke
  A40-v22-press_cd-e20-s8 closed_loop after A40-fetch-press_cd-e20, A40-v22-press_cd-smoke
  A40-v22-press_cd-e20-s9 closed_loop after A40-fetch-press_cd-e20, A40-v22-press_cd-smoke
  A40-v22-rearr_pw_long_s18-e45-smoke closed_loop after A40-fetch-rearr_pw_long_s18-e45
  A40-v22-rearr_pw_long_s18-e45-rearr-s0 closed_loop after A40-v22-rearr_pw_long_s18-e45-smoke
  A40-v22-rearr_pw_long_s18-e45-rearr-s1 closed_loop after A40-v22-rearr_pw_long_s18-e45-smoke
  A40-v22-rearr_pw_long_s18-e45-rearr-s2 closed_loop after A40-v22-rearr_pw_long_s18-e45-smoke
  A40-v22-rearr_pw_long_s18-e45-rearr-s3 closed_loop after A40-v22-rearr_pw_long_s18-e45-smoke
  A40-v22-rearr_pw_long_s18-e45-rearr-s4 closed_loop after A40-v22-rearr_pw_long_s18-e45-smoke
  A40-v22-rearr_pw_long_s18-e45-rearr-s5 closed_loop after A40-v22-rearr_pw_long_s18-e45-smoke
  A40-v22-rearr_pw_long_s18-e45-rearr-s6 closed_loop after A40-v22-rearr_pw_long_s18-e45-smoke
  A40-v22-rearr_pw_long_s18-e45-rearr-s7 closed_loop after A40-v22-rearr_pw_long_s18-e45-smoke
  A40-v22-rearr_pw_long_s18-e45-rearr-s8 closed_loop after A40-v22-rearr_pw_long_s18-e45-smoke
  A40-v22-rearr_pw_long_s18-e45-rearr-s9 closed_loop after A40-v22-rearr_pw_long_s18-e45-smoke
  A40-v22-rearr_pw_long-e45-smoke closed_loop after A40-fetch-rearr_pw_long-e45
  A40-v22-rearr_pw_long-e45-rearr-s0 closed_loop after A40-v22-rearr_pw_long-e45-smoke
  A40-v22-rearr_pw_long-e45-rearr-s1 closed_loop after A40-v22-rearr_pw_long-e45-smoke
  A40-v22-rearr_pw_long-e45-rearr-s2 closed_loop after A40-v22-rearr_pw_long-e45-smoke
  A40-v22-rearr_pw_long-e45-rearr-s3 closed_loop after A40-v22-rearr_pw_long-e45-smoke
  A40-v22-rearr_pw_long-e45-rearr-s4 closed_loop after A40-v22-rearr_pw_long-e45-smoke
  A40-v22-rearr_pw_long-e45-rearr-s5 closed_loop after A40-v22-rearr_pw_long-e45-smoke
  A40-v22-rearr_pw_long-e45-rearr-s6 closed_loop after A40-v22-rearr_pw_long-e45-smoke
  A40-v22-rearr_pw_long-e45-rearr-s7 closed_loop after A40-v22-rearr_pw_long-e45-smoke
  A40-v22-rearr_pw_long-e45-rearr-s8 closed_loop after A40-v22-rearr_pw_long-e45-smoke
  A40-v22-rearr_pw_long-e45-rearr-s9 closed_loop after A40-v22-rearr_pw_long-e45-smoke
  A40-V22-DESC-c27_e45 shell       after A40-v22-rearr_pw_long_s18-e45-rearr-s0, A40-v22-rearr_pw_long_s18-e45-rearr-s1, A40-v22-rearr_pw_long_s18-e45-rearr-s2, A40-v22-rearr_pw_long_s18-e45-rearr-s3, A40-v22-rearr_pw_long_s18-e45-rearr-s4, A40-v22-rearr_pw_long_s18-e45-rearr-s5, A40-v22-rearr_pw_long_s18-e45-rearr-s6, A40-v22-rearr_pw_long_s18-e45-rearr-s7, A40-v22-rearr_pw_long_s18-e45-rearr-s8, A40-v22-rearr_pw_long_s18-e45-rearr-s9, A40-v22-rearr_pw_long-e45-rearr-s0, A40-v22-rearr_pw_long-e45-rearr-s1, A40-v22-rearr_pw_long-e45-rearr-s2, A40-v22-rearr_pw_long-e45-rearr-s3, A40-v22-rearr_pw_long-e45-rearr-s4, A40-v22-rearr_pw_long-e45-rearr-s5, A40-v22-rearr_pw_long-e45-rearr-s6, A40-v22-rearr_pw_long-e45-rearr-s7, A40-v22-rearr_pw_long-e45-rearr-s8, A40-v22-rearr_pw_long-e45-rearr-s9
  A40-v22-rearr_pw_h100_long_s18-e45-smoke closed_loop after A40-fetch-rearr_pw_h100_long_s18-e45
  A40-v22-rearr_pw_h100_long_s18-e45-rearr-s0 closed_loop after A40-v22-rearr_pw_h100_long_s18-e45-smoke
  A40-v22-rearr_pw_h100_long_s18-e45-rearr-s1 closed_loop after A40-v22-rearr_pw_h100_long_s18-e45-smoke
  A40-v22-rearr_pw_h100_long_s18-e45-rearr-s2 closed_loop after A40-v22-rearr_pw_h100_long_s18-e45-smoke
  A40-v22-rearr_pw_h100_long_s18-e45-rearr-s3 closed_loop after A40-v22-rearr_pw_h100_long_s18-e45-smoke
  A40-v22-rearr_pw_h100_long_s18-e45-rearr-s4 closed_loop after A40-v22-rearr_pw_h100_long_s18-e45-smoke
  A40-v22-rearr_pw_h100_long_s18-e45-rearr-s5 closed_loop after A40-v22-rearr_pw_h100_long_s18-e45-smoke
  A40-v22-rearr_pw_h100_long_s18-e45-rearr-s6 closed_loop after A40-v22-rearr_pw_h100_long_s18-e45-smoke
  A40-v22-rearr_pw_h100_long_s18-e45-rearr-s7 closed_loop after A40-v22-rearr_pw_h100_long_s18-e45-smoke
  A40-v22-rearr_pw_h100_long_s18-e45-rearr-s8 closed_loop after A40-v22-rearr_pw_h100_long_s18-e45-smoke
  A40-v22-rearr_pw_h100_long_s18-e45-rearr-s9 closed_loop after A40-v22-rearr_pw_h100_long_s18-e45-smoke
  A40-v22-rearr_pw_h100_long-e45-smoke closed_loop after A40-fetch-rearr_pw_h100_long-e45
  A40-v22-rearr_pw_h100_long-e45-rearr-s0 closed_loop after A40-v22-rearr_pw_h100_long-e45-smoke
  A40-v22-rearr_pw_h100_long-e45-rearr-s1 closed_loop after A40-v22-rearr_pw_h100_long-e45-smoke
  A40-v22-rearr_pw_h100_long-e45-rearr-s2 closed_loop after A40-v22-rearr_pw_h100_long-e45-smoke
  A40-v22-rearr_pw_h100_long-e45-rearr-s3 closed_loop after A40-v22-rearr_pw_h100_long-e45-smoke
  A40-v22-rearr_pw_h100_long-e45-rearr-s4 closed_loop after A40-v22-rearr_pw_h100_long-e45-smoke
  A40-v22-rearr_pw_h100_long-e45-rearr-s5 closed_loop after A40-v22-rearr_pw_h100_long-e45-smoke
  A40-v22-rearr_pw_h100_long-e45-rearr-s6 closed_loop after A40-v22-rearr_pw_h100_long-e45-smoke
  A40-v22-rearr_pw_h100_long-e45-rearr-s7 closed_loop after A40-v22-rearr_pw_h100_long-e45-smoke
  A40-v22-rearr_pw_h100_long-e45-rearr-s8 closed_loop after A40-v22-rearr_pw_h100_long-e45-smoke
  A40-v22-rearr_pw_h100_long-e45-rearr-s9 closed_loop after A40-v22-rearr_pw_h100_long-e45-smoke
  A40-V22-DESC-c27b_e45 shell       after A40-v22-rearr_pw_h100_long_s18-e45-rearr-s0, A40-v22-rearr_pw_h100_long_s18-e45-rearr-s1, A40-v22-rearr_pw_h100_long_s18-e45-rearr-s2, A40-v22-rearr_pw_h100_long_s18-e45-rearr-s3, A40-v22-rearr_pw_h100_long_s18-e45-rearr-s4, A40-v22-rearr_pw_h100_long_s18-e45-rearr-s5, A40-v22-rearr_pw_h100_long_s18-e45-rearr-s6, A40-v22-rearr_pw_h100_long_s18-e45-rearr-s7, A40-v22-rearr_pw_h100_long_s18-e45-rearr-s8, A40-v22-rearr_pw_h100_long_s18-e45-rearr-s9, A40-v22-rearr_pw_h100_long-e45-rearr-s0, A40-v22-rearr_pw_h100_long-e45-rearr-s1, A40-v22-rearr_pw_h100_long-e45-rearr-s2, A40-v22-rearr_pw_h100_long-e45-rearr-s3, A40-v22-rearr_pw_h100_long-e45-rearr-s4, A40-v22-rearr_pw_h100_long-e45-rearr-s5, A40-v22-rearr_pw_h100_long-e45-rearr-s6, A40-v22-rearr_pw_h100_long-e45-rearr-s7, A40-v22-rearr_pw_h100_long-e45-rearr-s8, A40-v22-rearr_pw_h100_long-e45-rearr-s9
  A40-v22-rearr_ar_pw_s18-e30-smoke closed_loop after A40-fetch-rearr_ar_pw_s18-e30
  A40-v22-rearr_ar_pw_s18-e30-rearr-s0 closed_loop after A40-v22-rearr_ar_pw_s18-e30-smoke
  A40-v22-rearr_ar_pw_s18-e30-rearr-s1 closed_loop after A40-v22-rearr_ar_pw_s18-e30-smoke
  A40-v22-rearr_ar_pw_s18-e30-rearr-s2 closed_loop after A40-v22-rearr_ar_pw_s18-e30-smoke
  A40-v22-rearr_ar_pw_s18-e30-rearr-s3 closed_loop after A40-v22-rearr_ar_pw_s18-e30-smoke
  A40-v22-rearr_ar_pw_s18-e30-rearr-s4 closed_loop after A40-v22-rearr_ar_pw_s18-e30-smoke
  A40-v22-rearr_ar_pw_s18-e30-rearr-s5 closed_loop after A40-v22-rearr_ar_pw_s18-e30-smoke
  A40-v22-rearr_ar_pw_s18-e30-rearr-s6 closed_loop after A40-v22-rearr_ar_pw_s18-e30-smoke
  A40-v22-rearr_ar_pw_s18-e30-rearr-s7 closed_loop after A40-v22-rearr_ar_pw_s18-e30-smoke
  A40-v22-rearr_ar_pw_s18-e30-rearr-s8 closed_loop after A40-v22-rearr_ar_pw_s18-e30-smoke
  A40-v22-rearr_ar_pw_s18-e30-rearr-s9 closed_loop after A40-v22-rearr_ar_pw_s18-e30-smoke
  A40-v22-rearr_arprop_pw_s18-e30-smoke closed_loop after A40-fetch-rearr_arprop_pw_s18-e30
  A40-v22-rearr_arprop_pw_s18-e30-rearr-s0 closed_loop after A40-v22-rearr_arprop_pw_s18-e30-smoke
  A40-v22-rearr_arprop_pw_s18-e30-rearr-s1 closed_loop after A40-v22-rearr_arprop_pw_s18-e30-smoke
  A40-v22-rearr_arprop_pw_s18-e30-rearr-s2 closed_loop after A40-v22-rearr_arprop_pw_s18-e30-smoke
  A40-v22-rearr_arprop_pw_s18-e30-rearr-s3 closed_loop after A40-v22-rearr_arprop_pw_s18-e30-smoke
  A40-v22-rearr_arprop_pw_s18-e30-rearr-s4 closed_loop after A40-v22-rearr_arprop_pw_s18-e30-smoke
  A40-v22-rearr_arprop_pw_s18-e30-rearr-s5 closed_loop after A40-v22-rearr_arprop_pw_s18-e30-smoke
  A40-v22-rearr_arprop_pw_s18-e30-rearr-s6 closed_loop after A40-v22-rearr_arprop_pw_s18-e30-smoke
  A40-v22-rearr_arprop_pw_s18-e30-rearr-s7 closed_loop after A40-v22-rearr_arprop_pw_s18-e30-smoke
  A40-v22-rearr_arprop_pw_s18-e30-rearr-s8 closed_loop after A40-v22-rearr_arprop_pw_s18-e30-smoke
  A40-v22-rearr_arprop_pw_s18-e30-rearr-s9 closed_loop after A40-v22-rearr_arprop_pw_s18-e30-smoke
  A40-V22-DESC-c28   shell       after A40-v22-rearr_ar_pw_s18-e30-rearr-s0, A40-v22-rearr_ar_pw_s18-e30-rearr-s1, A40-v22-rearr_ar_pw_s18-e30-rearr-s2, A40-v22-rearr_ar_pw_s18-e30-rearr-s3, A40-v22-rearr_ar_pw_s18-e30-rearr-s4, A40-v22-rearr_ar_pw_s18-e30-rearr-s5, A40-v22-rearr_ar_pw_s18-e30-rearr-s6, A40-v22-rearr_ar_pw_s18-e30-rearr-s7, A40-v22-rearr_ar_pw_s18-e30-rearr-s8, A40-v22-rearr_ar_pw_s18-e30-rearr-s9, A40-v22-rearr_arprop_pw_s18-e30-rearr-s0, A40-v22-rearr_arprop_pw_s18-e30-rearr-s1, A40-v22-rearr_arprop_pw_s18-e30-rearr-s2, A40-v22-rearr_arprop_pw_s18-e30-rearr-s3, A40-v22-rearr_arprop_pw_s18-e30-rearr-s4, A40-v22-rearr_arprop_pw_s18-e30-rearr-s5, A40-v22-rearr_arprop_pw_s18-e30-rearr-s6, A40-v22-rearr_arprop_pw_s18-e30-rearr-s7, A40-v22-rearr_arprop_pw_s18-e30-rearr-s8, A40-v22-rearr_arprop_pw_s18-e30-rearr-s9
  A40-v22-rearrange_ar_s18-e30-smoke closed_loop after A40-fetch-rearrange_ar_s18-e30
  A40-v22-rearrange_ar_s18-e30-rearr-s0 closed_loop after A40-v22-rearrange_ar_s18-e30-smoke
  A40-v22-rearrange_ar_s18-e30-rearr-s1 closed_loop after A40-v22-rearrange_ar_s18-e30-smoke
  A40-v22-rearrange_ar_s18-e30-rearr-s2 closed_loop after A40-v22-rearrange_ar_s18-e30-smoke
  A40-v22-rearrange_ar_s18-e30-rearr-s3 closed_loop after A40-v22-rearrange_ar_s18-e30-smoke
  A40-v22-rearrange_ar_s18-e30-rearr-s4 closed_loop after A40-v22-rearrange_ar_s18-e30-smoke
  A40-v22-rearrange_ar_s18-e30-rearr-s5 closed_loop after A40-v22-rearrange_ar_s18-e30-smoke
  A40-v22-rearrange_ar_s18-e30-rearr-s6 closed_loop after A40-v22-rearrange_ar_s18-e30-smoke
  A40-v22-rearrange_ar_s18-e30-rearr-s7 closed_loop after A40-v22-rearrange_ar_s18-e30-smoke
  A40-v22-rearrange_ar_s18-e30-rearr-s8 closed_loop after A40-v22-rearrange_ar_s18-e30-smoke
  A40-v22-rearrange_ar_s18-e30-rearr-s9 closed_loop after A40-v22-rearrange_ar_s18-e30-smoke
  A40-v22-rearrange_arprop_s18-e30-smoke closed_loop after A40-fetch-rearrange_arprop_s18-e30
  A40-v22-rearrange_arprop_s18-e30-rearr-s0 closed_loop after A40-v22-rearrange_arprop_s18-e30-smoke
  A40-v22-rearrange_arprop_s18-e30-rearr-s1 closed_loop after A40-v22-rearrange_arprop_s18-e30-smoke
  A40-v22-rearrange_arprop_s18-e30-rearr-s2 closed_loop after A40-v22-rearrange_arprop_s18-e30-smoke
  A40-v22-rearrange_arprop_s18-e30-rearr-s3 closed_loop after A40-v22-rearrange_arprop_s18-e30-smoke
  A40-v22-rearrange_arprop_s18-e30-rearr-s4 closed_loop after A40-v22-rearrange_arprop_s18-e30-smoke
  A40-v22-rearrange_arprop_s18-e30-rearr-s5 closed_loop after A40-v22-rearrange_arprop_s18-e30-smoke
  A40-v22-rearrange_arprop_s18-e30-rearr-s6 closed_loop after A40-v22-rearrange_arprop_s18-e30-smoke
  A40-v22-rearrange_arprop_s18-e30-rearr-s7 closed_loop after A40-v22-rearrange_arprop_s18-e30-smoke
  A40-v22-rearrange_arprop_s18-e30-rearr-s8 closed_loop after A40-v22-rearrange_arprop_s18-e30-smoke
  A40-v22-rearrange_arprop_s18-e30-rearr-s9 closed_loop after A40-v22-rearrange_arprop_s18-e30-smoke
  A40-V22-DESC-c33   shell       after A40-v22-rearrange_ar_s18-e30-rearr-s0, A40-v22-rearrange_ar_s18-e30-rearr-s1, A40-v22-rearrange_ar_s18-e30-rearr-s2, A40-v22-rearrange_ar_s18-e30-rearr-s3, A40-v22-rearrange_ar_s18-e30-rearr-s4, A40-v22-rearrange_ar_s18-e30-rearr-s5, A40-v22-rearrange_ar_s18-e30-rearr-s6, A40-v22-rearrange_ar_s18-e30-rearr-s7, A40-v22-rearrange_ar_s18-e30-rearr-s8, A40-v22-rearrange_ar_s18-e30-rearr-s9, A40-v22-rearrange_arprop_s18-e30-rearr-s0, A40-v22-rearrange_arprop_s18-e30-rearr-s1, A40-v22-rearrange_arprop_s18-e30-rearr-s2, A40-v22-rearrange_arprop_s18-e30-rearr-s3, A40-v22-rearrange_arprop_s18-e30-rearr-s4, A40-v22-rearrange_arprop_s18-e30-rearr-s5, A40-v22-rearrange_arprop_s18-e30-rearr-s6, A40-v22-rearrange_arprop_s18-e30-rearr-s7, A40-v22-rearrange_arprop_s18-e30-rearr-s8, A40-v22-rearrange_arprop_s18-e30-rearr-s9
  A40-v22-ranking_v3a_s18-e30-smoke closed_loop after A40-fetch-ranking_v3a_s18-e30
  A40-v22-ranking_v3a_s18-e30-rank-s0 closed_loop after A40-v22-ranking_v3a_s18-e30-smoke
  A40-v22-ranking_v3a_s18-e30-rank-s1 closed_loop after A40-v22-ranking_v3a_s18-e30-smoke
  A40-v22-ranking_v3a_s18-e30-rank-s2 closed_loop after A40-v22-ranking_v3a_s18-e30-smoke
  A40-v22-ranking_v3a_s18-e30-rank-s3 closed_loop after A40-v22-ranking_v3a_s18-e30-smoke
  A40-v22-ranking_v3a_s18-e30-rank-s4 closed_loop after A40-v22-ranking_v3a_s18-e30-smoke
  A40-v22-ranking_v3a_s18-e30-rank-s5 closed_loop after A40-v22-ranking_v3a_s18-e30-smoke
  A40-v22-ranking_v3a_s18-e30-rank-s6 closed_loop after A40-v22-ranking_v3a_s18-e30-smoke
  A40-v22-ranking_v3a_s18-e30-rank-s7 closed_loop after A40-v22-ranking_v3a_s18-e30-smoke
  A40-v22-ranking_v3a_s18-e30-rank-s8 closed_loop after A40-v22-ranking_v3a_s18-e30-smoke
  A40-v22-ranking_v3a_s18-e30-rank-s9 closed_loop after A40-v22-ranking_v3a_s18-e30-smoke
  A40-v22-ranking_v3a_s18-e20-smoke closed_loop after A40-fetch-ranking_v3a_s18-e20
  A40-v22-ranking_v3a_s18-e20-rank-s0 closed_loop after A40-v22-ranking_v3a_s18-e20-smoke
  A40-v22-ranking_v3a_s18-e20-rank-s1 closed_loop after A40-v22-ranking_v3a_s18-e20-smoke
  A40-v22-ranking_v3a_s18-e20-rank-s2 closed_loop after A40-v22-ranking_v3a_s18-e20-smoke
  A40-v22-ranking_v3a_s18-e20-rank-s3 closed_loop after A40-v22-ranking_v3a_s18-e20-smoke
  A40-v22-ranking_v3a_s18-e20-rank-s4 closed_loop after A40-v22-ranking_v3a_s18-e20-smoke
  A40-v22-ranking_v3a_s18-e20-rank-s5 closed_loop after A40-v22-ranking_v3a_s18-e20-smoke
  A40-v22-ranking_v3a_s18-e20-rank-s6 closed_loop after A40-v22-ranking_v3a_s18-e20-smoke
  A40-v22-ranking_v3a_s18-e20-rank-s7 closed_loop after A40-v22-ranking_v3a_s18-e20-smoke
  A40-v22-ranking_v3a_s18-e20-rank-s8 closed_loop after A40-v22-ranking_v3a_s18-e20-smoke
  A40-v22-ranking_v3a_s18-e20-rank-s9 closed_loop after A40-v22-ranking_v3a_s18-e20-smoke
  A40-V22-DESC-c29   shell       after A40-v22-ranking_v3a_s18-e30-rank-s0, A40-v22-ranking_v3a_s18-e30-rank-s1, A40-v22-ranking_v3a_s18-e30-rank-s2, A40-v22-ranking_v3a_s18-e30-rank-s3, A40-v22-ranking_v3a_s18-e30-rank-s4, A40-v22-ranking_v3a_s18-e30-rank-s5, A40-v22-ranking_v3a_s18-e30-rank-s6, A40-v22-ranking_v3a_s18-e30-rank-s7, A40-v22-ranking_v3a_s18-e30-rank-s8, A40-v22-ranking_v3a_s18-e30-rank-s9, A40-v22-ranking_v3a_s18-e20-rank-s0, A40-v22-ranking_v3a_s18-e20-rank-s1, A40-v22-ranking_v3a_s18-e20-rank-s2, A40-v22-ranking_v3a_s18-e20-rank-s3, A40-v22-ranking_v3a_s18-e20-rank-s4, A40-v22-ranking_v3a_s18-e20-rank-s5, A40-v22-ranking_v3a_s18-e20-rank-s6, A40-v22-ranking_v3a_s18-e20-rank-s7, A40-v22-ranking_v3a_s18-e20-rank-s8, A40-v22-ranking_v3a_s18-e20-rank-s9
  A40-v22-swapT_joint3_s18-e30-smoke closed_loop after A40-fetch-swapT_joint3_s18-e30
  A40-v22-swapT_joint3_s18-e30-swapT-s0 closed_loop after A40-v22-swapT_joint3_s18-e30-smoke
  A40-v22-swapT_joint3_s18-e30-swapT-s1 closed_loop after A40-v22-swapT_joint3_s18-e30-smoke
  A40-v22-swapT_joint3_s18-e30-swapT-s2 closed_loop after A40-v22-swapT_joint3_s18-e30-smoke
  A40-v22-swapT_joint3_s18-e30-swapT-s3 closed_loop after A40-v22-swapT_joint3_s18-e30-smoke
  A40-v22-swapT_joint3_s18-e30-swapT-s4 closed_loop after A40-v22-swapT_joint3_s18-e30-smoke
  A40-v22-swapT_joint3_s18-e30-swapT-s5 closed_loop after A40-v22-swapT_joint3_s18-e30-smoke
  A40-v22-swapT_joint3_s18-e30-swapT-s6 closed_loop after A40-v22-swapT_joint3_s18-e30-smoke
  A40-v22-swapT_joint3_s18-e30-swapT-s7 closed_loop after A40-v22-swapT_joint3_s18-e30-smoke
  A40-v22-swapT_joint3_s18-e30-swapT-s8 closed_loop after A40-v22-swapT_joint3_s18-e30-smoke
  A40-v22-swapT_joint3_s18-e30-swapT-s9 closed_loop after A40-v22-swapT_joint3_s18-e30-smoke
  A40-v22-swapT_joint3_s18-e30-put-s0 closed_loop after A40-fetch-swapT_joint3_s18-e30
  A40-v22-swapT_joint3_s18-e30-put-s1 closed_loop after A40-fetch-swapT_joint3_s18-e30
  A40-v22-swapT_joint3_s18-e30-put-s2 closed_loop after A40-fetch-swapT_joint3_s18-e30
  A40-v22-swapT_joint3_s18-e30-put-s3 closed_loop after A40-fetch-swapT_joint3_s18-e30
  A40-v22-swapT_joint3_s18-e30-put-s4 closed_loop after A40-fetch-swapT_joint3_s18-e30
  A40-v22-swapT_joint3_s18-e30-put-s5 closed_loop after A40-fetch-swapT_joint3_s18-e30
  A40-v22-swapT_joint3_s18-e30-put-s6 closed_loop after A40-fetch-swapT_joint3_s18-e30
  A40-v22-swapT_joint3_s18-e30-put-s7 closed_loop after A40-fetch-swapT_joint3_s18-e30
  A40-v22-swapT_joint3_s18-e30-put-s8 closed_loop after A40-fetch-swapT_joint3_s18-e30
  A40-v22-swapT_joint3_s18-e30-put-s9 closed_loop after A40-fetch-swapT_joint3_s18-e30
  A40-v22-swapT_joint3_s18-e30-swap-s0 closed_loop after A40-fetch-swapT_joint3_s18-e30
  A40-v22-swapT_joint3_s18-e30-swap-s1 closed_loop after A40-fetch-swapT_joint3_s18-e30
  A40-v22-swapT_joint3_s18-e30-swap-s2 closed_loop after A40-fetch-swapT_joint3_s18-e30
  A40-v22-swapT_joint3_s18-e30-swap-s3 closed_loop after A40-fetch-swapT_joint3_s18-e30
  A40-v22-swapT_joint3_s18-e30-swap-s4 closed_loop after A40-fetch-swapT_joint3_s18-e30
  A40-v22-swapT_joint3_s18-e30-swap-s5 closed_loop after A40-fetch-swapT_joint3_s18-e30
  A40-v22-swapT_joint3_s18-e30-swap-s6 closed_loop after A40-fetch-swapT_joint3_s18-e30
  A40-v22-swapT_joint3_s18-e30-swap-s7 closed_loop after A40-fetch-swapT_joint3_s18-e30
  A40-v22-swapT_joint3_s18-e30-swap-s8 closed_loop after A40-fetch-swapT_joint3_s18-e30
  A40-v22-swapT_joint3_s18-e30-swap-s9 closed_loop after A40-fetch-swapT_joint3_s18-e30
  A40-V22-DESC-c35   shell       after A40-v22-swapT_joint3_s18-e30-swapT-s0, A40-v22-swapT_joint3_s18-e30-swapT-s1, A40-v22-swapT_joint3_s18-e30-swapT-s2, A40-v22-swapT_joint3_s18-e30-swapT-s3, A40-v22-swapT_joint3_s18-e30-swapT-s4, A40-v22-swapT_joint3_s18-e30-swapT-s5, A40-v22-swapT_joint3_s18-e30-swapT-s6, A40-v22-swapT_joint3_s18-e30-swapT-s7, A40-v22-swapT_joint3_s18-e30-swapT-s8, A40-v22-swapT_joint3_s18-e30-swapT-s9, A40-v22-swapT_joint3_s18-e30-put-s0, A40-v22-swapT_joint3_s18-e30-put-s1, A40-v22-swapT_joint3_s18-e30-put-s2, A40-v22-swapT_joint3_s18-e30-put-s3, A40-v22-swapT_joint3_s18-e30-put-s4, A40-v22-swapT_joint3_s18-e30-put-s5, A40-v22-swapT_joint3_s18-e30-put-s6, A40-v22-swapT_joint3_s18-e30-put-s7, A40-v22-swapT_joint3_s18-e30-put-s8, A40-v22-swapT_joint3_s18-e30-put-s9, A40-v22-swapT_joint3_s18-e30-swap-s0, A40-v22-swapT_joint3_s18-e30-swap-s1, A40-v22-swapT_joint3_s18-e30-swap-s2, A40-v22-swapT_joint3_s18-e30-swap-s3, A40-v22-swapT_joint3_s18-e30-swap-s4, A40-v22-swapT_joint3_s18-e30-swap-s5, A40-v22-swapT_joint3_s18-e30-swap-s6, A40-v22-swapT_joint3_s18-e30-swap-s7, A40-v22-swapT_joint3_s18-e30-swap-s8, A40-v22-swapT_joint3_s18-e30-swap-s9
  A40-v22-rearr_joint3-e10-smoke closed_loop after A40-fetch-rearr_joint3-e10
  A40-v22-rearr_joint3-e10-rearr-s0 closed_loop after A40-v22-rearr_joint3-e10-smoke
  A40-v22-rearr_joint3-e10-rearr-s1 closed_loop after A40-v22-rearr_joint3-e10-smoke
  A40-v22-rearr_joint3-e10-rearr-s2 closed_loop after A40-v22-rearr_joint3-e10-smoke
  A40-v22-rearr_joint3-e10-rearr-s3 closed_loop after A40-v22-rearr_joint3-e10-smoke
  A40-v22-rearr_joint3-e10-rearr-s4 closed_loop after A40-v22-rearr_joint3-e10-smoke
  A40-v22-rearr_joint3-e10-rearr-s5 closed_loop after A40-v22-rearr_joint3-e10-smoke
  A40-v22-rearr_joint3-e10-rearr-s6 closed_loop after A40-v22-rearr_joint3-e10-smoke
  A40-v22-rearr_joint3-e10-rearr-s7 closed_loop after A40-v22-rearr_joint3-e10-smoke
  A40-v22-rearr_joint3-e10-rearr-s8 closed_loop after A40-v22-rearr_joint3-e10-smoke
  A40-v22-rearr_joint3-e10-rearr-s9 closed_loop after A40-v22-rearr_joint3-e10-smoke
  A40-v22-rearr_joint3-e20-smoke closed_loop after A40-fetch-rearr_joint3-e20
  A40-v22-rearr_joint3-e20-rearr-s0 closed_loop after A40-v22-rearr_joint3-e20-smoke
  A40-v22-rearr_joint3-e20-rearr-s1 closed_loop after A40-v22-rearr_joint3-e20-smoke
  A40-v22-rearr_joint3-e20-rearr-s2 closed_loop after A40-v22-rearr_joint3-e20-smoke
  A40-v22-rearr_joint3-e20-rearr-s3 closed_loop after A40-v22-rearr_joint3-e20-smoke
  A40-v22-rearr_joint3-e20-rearr-s4 closed_loop after A40-v22-rearr_joint3-e20-smoke
  A40-v22-rearr_joint3-e20-rearr-s5 closed_loop after A40-v22-rearr_joint3-e20-smoke
  A40-v22-rearr_joint3-e20-rearr-s6 closed_loop after A40-v22-rearr_joint3-e20-smoke
  A40-v22-rearr_joint3-e20-rearr-s7 closed_loop after A40-v22-rearr_joint3-e20-smoke
  A40-v22-rearr_joint3-e20-rearr-s8 closed_loop after A40-v22-rearr_joint3-e20-smoke
  A40-v22-rearr_joint3-e20-rearr-s9 closed_loop after A40-v22-rearr_joint3-e20-smoke
  A40-V22-DESC-c32_e10e20 shell       after A40-v22-rearr_joint3-e10-rearr-s0, A40-v22-rearr_joint3-e10-rearr-s1, A40-v22-rearr_joint3-e10-rearr-s2, A40-v22-rearr_joint3-e10-rearr-s3, A40-v22-rearr_joint3-e10-rearr-s4, A40-v22-rearr_joint3-e10-rearr-s5, A40-v22-rearr_joint3-e10-rearr-s6, A40-v22-rearr_joint3-e10-rearr-s7, A40-v22-rearr_joint3-e10-rearr-s8, A40-v22-rearr_joint3-e10-rearr-s9, A40-v22-rearr_joint3-e20-rearr-s0, A40-v22-rearr_joint3-e20-rearr-s1, A40-v22-rearr_joint3-e20-rearr-s2, A40-v22-rearr_joint3-e20-rearr-s3, A40-v22-rearr_joint3-e20-rearr-s4, A40-v22-rearr_joint3-e20-rearr-s5, A40-v22-rearr_joint3-e20-rearr-s6, A40-v22-rearr_joint3-e20-rearr-s7, A40-v22-rearr_joint3-e20-rearr-s8, A40-v22-rearr_joint3-e20-rearr-s9
  A40-v22-swapT_joint3_ow-e10-smoke closed_loop after A40-fetch-swapT_joint3_ow-e10
  A40-v22-swapT_joint3_ow-e10-swapT-s0 closed_loop after A40-v22-swapT_joint3_ow-e10-smoke
  A40-v22-swapT_joint3_ow-e10-swapT-s1 closed_loop after A40-v22-swapT_joint3_ow-e10-smoke
  A40-v22-swapT_joint3_ow-e10-swapT-s2 closed_loop after A40-v22-swapT_joint3_ow-e10-smoke
  A40-v22-swapT_joint3_ow-e10-swapT-s3 closed_loop after A40-v22-swapT_joint3_ow-e10-smoke
  A40-v22-swapT_joint3_ow-e10-swapT-s4 closed_loop after A40-v22-swapT_joint3_ow-e10-smoke
  A40-v22-swapT_joint3_ow-e10-swapT-s5 closed_loop after A40-v22-swapT_joint3_ow-e10-smoke
  A40-v22-swapT_joint3_ow-e10-swapT-s6 closed_loop after A40-v22-swapT_joint3_ow-e10-smoke
  A40-v22-swapT_joint3_ow-e10-swapT-s7 closed_loop after A40-v22-swapT_joint3_ow-e10-smoke
  A40-v22-swapT_joint3_ow-e10-swapT-s8 closed_loop after A40-v22-swapT_joint3_ow-e10-smoke
  A40-v22-swapT_joint3_ow-e10-swapT-s9 closed_loop after A40-v22-swapT_joint3_ow-e10-smoke
  A40-v22-swapT_joint3_ow-e20-smoke closed_loop after A40-fetch-swapT_joint3_ow-e20
  A40-v22-swapT_joint3_ow-e20-swapT-s0 closed_loop after A40-v22-swapT_joint3_ow-e20-smoke
  A40-v22-swapT_joint3_ow-e20-swapT-s1 closed_loop after A40-v22-swapT_joint3_ow-e20-smoke
  A40-v22-swapT_joint3_ow-e20-swapT-s2 closed_loop after A40-v22-swapT_joint3_ow-e20-smoke
  A40-v22-swapT_joint3_ow-e20-swapT-s3 closed_loop after A40-v22-swapT_joint3_ow-e20-smoke
  A40-v22-swapT_joint3_ow-e20-swapT-s4 closed_loop after A40-v22-swapT_joint3_ow-e20-smoke
  A40-v22-swapT_joint3_ow-e20-swapT-s5 closed_loop after A40-v22-swapT_joint3_ow-e20-smoke
  A40-v22-swapT_joint3_ow-e20-swapT-s6 closed_loop after A40-v22-swapT_joint3_ow-e20-smoke
  A40-v22-swapT_joint3_ow-e20-swapT-s7 closed_loop after A40-v22-swapT_joint3_ow-e20-smoke
  A40-v22-swapT_joint3_ow-e20-swapT-s8 closed_loop after A40-v22-swapT_joint3_ow-e20-smoke
  A40-v22-swapT_joint3_ow-e20-swapT-s9 closed_loop after A40-v22-swapT_joint3_ow-e20-smoke
  A40-V22-DESC-c37_e10e20 shell       after A40-v22-swapT_joint3_ow-e10-swapT-s0, A40-v22-swapT_joint3_ow-e10-swapT-s1, A40-v22-swapT_joint3_ow-e10-swapT-s2, A40-v22-swapT_joint3_ow-e10-swapT-s3, A40-v22-swapT_joint3_ow-e10-swapT-s4, A40-v22-swapT_joint3_ow-e10-swapT-s5, A40-v22-swapT_joint3_ow-e10-swapT-s6, A40-v22-swapT_joint3_ow-e10-swapT-s7, A40-v22-swapT_joint3_ow-e10-swapT-s8, A40-v22-swapT_joint3_ow-e10-swapT-s9, A40-v22-swapT_joint3_ow-e20-swapT-s0, A40-v22-swapT_joint3_ow-e20-swapT-s1, A40-v22-swapT_joint3_ow-e20-swapT-s2, A40-v22-swapT_joint3_ow-e20-swapT-s3, A40-v22-swapT_joint3_ow-e20-swapT-s4, A40-v22-swapT_joint3_ow-e20-swapT-s5, A40-v22-swapT_joint3_ow-e20-swapT-s6, A40-v22-swapT_joint3_ow-e20-swapT-s7, A40-v22-swapT_joint3_ow-e20-swapT-s8, A40-v22-swapT_joint3_ow-e20-swapT-s9
  A40-v22-obs_cf800-e5-smoke closed_loop after A40-fetch-obs_cf800-e5
  A40-v22-obs_cf800-e5-obs-s0 closed_loop after A40-v22-obs_cf800-e5-smoke
  A40-v22-obs_cf800-e5-obs-s1 closed_loop after A40-v22-obs_cf800-e5-smoke
  A40-v22-obs_cf800-e5-obs-s2 closed_loop after A40-v22-obs_cf800-e5-smoke
  A40-v22-obs_cf800-e5-obs-s3 closed_loop after A40-v22-obs_cf800-e5-smoke
  A40-v22-obs_cf800-e5-obs-s4 closed_loop after A40-v22-obs_cf800-e5-smoke
  A40-v22-obs_cf800-e5-obs-s5 closed_loop after A40-v22-obs_cf800-e5-smoke
  A40-v22-obs_cf800-e5-obs-s6 closed_loop after A40-v22-obs_cf800-e5-smoke
  A40-v22-obs_cf800-e5-obs-s7 closed_loop after A40-v22-obs_cf800-e5-smoke
  A40-v22-obs_cf800-e5-obs-s8 closed_loop after A40-v22-obs_cf800-e5-smoke
  A40-v22-obs_cf800-e5-obs-s9 closed_loop after A40-v22-obs_cf800-e5-smoke
  A40-V22-DESC-c30_e5 shell       after A40-v22-obs_cf800-e5-obs-s0, A40-v22-obs_cf800-e5-obs-s1, A40-v22-obs_cf800-e5-obs-s2, A40-v22-obs_cf800-e5-obs-s3, A40-v22-obs_cf800-e5-obs-s4, A40-v22-obs_cf800-e5-obs-s5, A40-v22-obs_cf800-e5-obs-s6, A40-v22-obs_cf800-e5-obs-s7, A40-v22-obs_cf800-e5-obs-s8, A40-v22-obs_cf800-e5-obs-s9
  A40-v22-rearr_pw_s19-e30-smoke closed_loop after A40-fetch-rearr_pw_s19-e30
  A40-v22-rearr_pw_s19-e30-rearr-s0 closed_loop after A40-v22-rearr_pw_s19-e30-smoke
  A40-v22-rearr_pw_s19-e30-rearr-s1 closed_loop after A40-v22-rearr_pw_s19-e30-smoke
  A40-v22-rearr_pw_s19-e30-rearr-s2 closed_loop after A40-v22-rearr_pw_s19-e30-smoke
  A40-v22-rearr_pw_s19-e30-rearr-s3 closed_loop after A40-v22-rearr_pw_s19-e30-smoke
  A40-v22-rearr_pw_s19-e30-rearr-s4 closed_loop after A40-v22-rearr_pw_s19-e30-smoke
  A40-v22-rearr_pw_s19-e30-rearr-s5 closed_loop after A40-v22-rearr_pw_s19-e30-smoke
  A40-v22-rearr_pw_s19-e30-rearr-s6 closed_loop after A40-v22-rearr_pw_s19-e30-smoke
  A40-v22-rearr_pw_s19-e30-rearr-s7 closed_loop after A40-v22-rearr_pw_s19-e30-smoke
  A40-v22-rearr_pw_s19-e30-rearr-s8 closed_loop after A40-v22-rearr_pw_s19-e30-smoke
  A40-v22-rearr_pw_s19-e30-rearr-s9 closed_loop after A40-v22-rearr_pw_s19-e30-smoke
  A40-v22-rearr_pw_h100_s19-e30-smoke closed_loop after A40-fetch-rearr_pw_h100_s19-e30
  A40-v22-rearr_pw_h100_s19-e30-rearr-s0 closed_loop after A40-v22-rearr_pw_h100_s19-e30-smoke
  A40-v22-rearr_pw_h100_s19-e30-rearr-s1 closed_loop after A40-v22-rearr_pw_h100_s19-e30-smoke
  A40-v22-rearr_pw_h100_s19-e30-rearr-s2 closed_loop after A40-v22-rearr_pw_h100_s19-e30-smoke
  A40-v22-rearr_pw_h100_s19-e30-rearr-s3 closed_loop after A40-v22-rearr_pw_h100_s19-e30-smoke
  A40-v22-rearr_pw_h100_s19-e30-rearr-s4 closed_loop after A40-v22-rearr_pw_h100_s19-e30-smoke
  A40-v22-rearr_pw_h100_s19-e30-rearr-s5 closed_loop after A40-v22-rearr_pw_h100_s19-e30-smoke
  A40-v22-rearr_pw_h100_s19-e30-rearr-s6 closed_loop after A40-v22-rearr_pw_h100_s19-e30-smoke
  A40-v22-rearr_pw_h100_s19-e30-rearr-s7 closed_loop after A40-v22-rearr_pw_h100_s19-e30-smoke
  A40-v22-rearr_pw_h100_s19-e30-rearr-s8 closed_loop after A40-v22-rearr_pw_h100_s19-e30-smoke
  A40-v22-rearr_pw_h100_s19-e30-rearr-s9 closed_loop after A40-v22-rearr_pw_h100_s19-e30-smoke
  A40-v22-rearr_pw_h100_s20-e30-smoke closed_loop after A40-fetch-rearr_pw_h100_s20-e30
  A40-v22-rearr_pw_h100_s20-e30-rearr-s0 closed_loop after A40-v22-rearr_pw_h100_s20-e30-smoke
  A40-v22-rearr_pw_h100_s20-e30-rearr-s1 closed_loop after A40-v22-rearr_pw_h100_s20-e30-smoke
  A40-v22-rearr_pw_h100_s20-e30-rearr-s2 closed_loop after A40-v22-rearr_pw_h100_s20-e30-smoke
  A40-v22-rearr_pw_h100_s20-e30-rearr-s3 closed_loop after A40-v22-rearr_pw_h100_s20-e30-smoke
  A40-v22-rearr_pw_h100_s20-e30-rearr-s4 closed_loop after A40-v22-rearr_pw_h100_s20-e30-smoke
  A40-v22-rearr_pw_h100_s20-e30-rearr-s5 closed_loop after A40-v22-rearr_pw_h100_s20-e30-smoke
  A40-v22-rearr_pw_h100_s20-e30-rearr-s6 closed_loop after A40-v22-rearr_pw_h100_s20-e30-smoke
  A40-v22-rearr_pw_h100_s20-e30-rearr-s7 closed_loop after A40-v22-rearr_pw_h100_s20-e30-smoke
  A40-v22-rearr_pw_h100_s20-e30-rearr-s8 closed_loop after A40-v22-rearr_pw_h100_s20-e30-smoke
  A40-v22-rearr_pw_h100_s20-e30-rearr-s9 closed_loop after A40-v22-rearr_pw_h100_s20-e30-smoke
  A40-V22-DESC-fill_rearr shell       after A40-v22-rearr_pw_s19-e30-rearr-s0, A40-v22-rearr_pw_s19-e30-rearr-s1, A40-v22-rearr_pw_s19-e30-rearr-s2, A40-v22-rearr_pw_s19-e30-rearr-s3, A40-v22-rearr_pw_s19-e30-rearr-s4, A40-v22-rearr_pw_s19-e30-rearr-s5, A40-v22-rearr_pw_s19-e30-rearr-s6, A40-v22-rearr_pw_s19-e30-rearr-s7, A40-v22-rearr_pw_s19-e30-rearr-s8, A40-v22-rearr_pw_s19-e30-rearr-s9, A40-v22-rearr_pw_h100_s19-e30-rearr-s0, A40-v22-rearr_pw_h100_s19-e30-rearr-s1, A40-v22-rearr_pw_h100_s19-e30-rearr-s2, A40-v22-rearr_pw_h100_s19-e30-rearr-s3, A40-v22-rearr_pw_h100_s19-e30-rearr-s4, A40-v22-rearr_pw_h100_s19-e30-rearr-s5, A40-v22-rearr_pw_h100_s19-e30-rearr-s6, A40-v22-rearr_pw_h100_s19-e30-rearr-s7, A40-v22-rearr_pw_h100_s19-e30-rearr-s8, A40-v22-rearr_pw_h100_s19-e30-rearr-s9, A40-v22-rearr_pw_h100_s20-e30-rearr-s0, A40-v22-rearr_pw_h100_s20-e30-rearr-s1, A40-v22-rearr_pw_h100_s20-e30-rearr-s2, A40-v22-rearr_pw_h100_s20-e30-rearr-s3, A40-v22-rearr_pw_h100_s20-e30-rearr-s4, A40-v22-rearr_pw_h100_s20-e30-rearr-s5, A40-v22-rearr_pw_h100_s20-e30-rearr-s6, A40-v22-rearr_pw_h100_s20-e30-rearr-s7, A40-v22-rearr_pw_h100_s20-e30-rearr-s8, A40-v22-rearr_pw_h100_s20-e30-rearr-s9
  A40-v22-swapT_ar_s18-e30-smoke closed_loop after A40-fetch-swapT_ar_s18-e30
  A40-v22-swapT_ar_s18-e30-swapT-s0 closed_loop after A40-v22-swapT_ar_s18-e30-smoke
  A40-v22-swapT_ar_s18-e30-swapT-s1 closed_loop after A40-v22-swapT_ar_s18-e30-smoke
  A40-v22-swapT_ar_s18-e30-swapT-s2 closed_loop after A40-v22-swapT_ar_s18-e30-smoke
  A40-v22-swapT_ar_s18-e30-swapT-s3 closed_loop after A40-v22-swapT_ar_s18-e30-smoke
  A40-v22-swapT_ar_s18-e30-swapT-s4 closed_loop after A40-v22-swapT_ar_s18-e30-smoke
  A40-v22-swapT_ar_s18-e30-swapT-s5 closed_loop after A40-v22-swapT_ar_s18-e30-smoke
  A40-v22-swapT_ar_s18-e30-swapT-s6 closed_loop after A40-v22-swapT_ar_s18-e30-smoke
  A40-v22-swapT_ar_s18-e30-swapT-s7 closed_loop after A40-v22-swapT_ar_s18-e30-smoke
  A40-v22-swapT_ar_s18-e30-swapT-s8 closed_loop after A40-v22-swapT_ar_s18-e30-smoke
  A40-v22-swapT_ar_s18-e30-swapT-s9 closed_loop after A40-v22-swapT_ar_s18-e30-smoke
  A40-V22-DESC-fill_swapT shell       after A40-v22-swapT_ar_s18-e30-swapT-s0, A40-v22-swapT_ar_s18-e30-swapT-s1, A40-v22-swapT_ar_s18-e30-swapT-s2, A40-v22-swapT_ar_s18-e30-swapT-s3, A40-v22-swapT_ar_s18-e30-swapT-s4, A40-v22-swapT_ar_s18-e30-swapT-s5, A40-v22-swapT_ar_s18-e30-swapT-s6, A40-v22-swapT_ar_s18-e30-swapT-s7, A40-v22-swapT_ar_s18-e30-swapT-s8, A40-v22-swapT_ar_s18-e30-swapT-s9
  A40-v22-ranking_arprop_s18-e30-smoke closed_loop after A40-fetch-ranking_arprop_s18-e30
  A40-v22-ranking_arprop_s18-e30-rank-s0 closed_loop after A40-v22-ranking_arprop_s18-e30-smoke
  A40-v22-ranking_arprop_s18-e30-rank-s1 closed_loop after A40-v22-ranking_arprop_s18-e30-smoke
  A40-v22-ranking_arprop_s18-e30-rank-s2 closed_loop after A40-v22-ranking_arprop_s18-e30-smoke
  A40-v22-ranking_arprop_s18-e30-rank-s3 closed_loop after A40-v22-ranking_arprop_s18-e30-smoke
  A40-v22-ranking_arprop_s18-e30-rank-s4 closed_loop after A40-v22-ranking_arprop_s18-e30-smoke
  A40-v22-ranking_arprop_s18-e30-rank-s5 closed_loop after A40-v22-ranking_arprop_s18-e30-smoke
  A40-v22-ranking_arprop_s18-e30-rank-s6 closed_loop after A40-v22-ranking_arprop_s18-e30-smoke
  A40-v22-ranking_arprop_s18-e30-rank-s7 closed_loop after A40-v22-ranking_arprop_s18-e30-smoke
  A40-v22-ranking_arprop_s18-e30-rank-s8 closed_loop after A40-v22-ranking_arprop_s18-e30-smoke
  A40-v22-ranking_arprop_s18-e30-rank-s9 closed_loop after A40-v22-ranking_arprop_s18-e30-smoke
  A40-V22-DESC-fill_rank shell       after A40-v22-ranking_arprop_s18-e30-rank-s0, A40-v22-ranking_arprop_s18-e30-rank-s1, A40-v22-ranking_arprop_s18-e30-rank-s2, A40-v22-ranking_arprop_s18-e30-rank-s3, A40-v22-ranking_arprop_s18-e30-rank-s4, A40-v22-ranking_arprop_s18-e30-rank-s5, A40-v22-ranking_arprop_s18-e30-rank-s6, A40-v22-ranking_arprop_s18-e30-rank-s7, A40-v22-ranking_arprop_s18-e30-rank-s8, A40-v22-ranking_arprop_s18-e30-rank-s9
  A40-covnone30-smoke closed_loop after A40-fetch-cover_none-e30
  A40-covnone30-s0   closed_loop after A40-covnone30-smoke
  A40-covnone30-s1   closed_loop after A40-covnone30-smoke
  A40-covnone30-s2   closed_loop after A40-covnone30-smoke
  A40-covnone30-s3   closed_loop after A40-covnone30-smoke
  A40-covnone30-s4   closed_loop after A40-covnone30-smoke
  A40-covnone30-s5   closed_loop after A40-covnone30-smoke
  A40-covnone30-s6   closed_loop after A40-covnone30-smoke
  A40-covnone30-s7   closed_loop after A40-covnone30-smoke
  A40-covnone30-s8   closed_loop after A40-covnone30-smoke
  A40-covnone30-s9   closed_loop after A40-covnone30-smoke
  A40-COVNONE-report shell       after A40-covnone30-s0, A40-covnone30-s1, A40-covnone30-s2, A40-covnone30-s3, A40-covnone30-s4, A40-covnone30-s5, A40-covnone30-s6, A40-covnone30-s7, A40-covnone30-s8, A40-covnone30-s9
  A40-E22-clock-p256-vis-swap-s0 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p256-vis-swap-s1 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p256-vis-swap-s2 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p256-vis-swap-s3 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p256-vis-swap-s4 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p256-hid-swap-s0 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p256-hid-swap-s1 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p256-hid-swap-s2 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p256-hid-swap-s3 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p256-hid-swap-s4 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p256-vis-put-s0 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p256-vis-put-s1 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p256-vis-put-s2 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p256-vis-put-s3 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p256-vis-put-s4 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p256-hid-put-s0 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p256-hid-put-s1 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p256-hid-put-s2 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p256-hid-put-s3 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p256-hid-put-s4 closed_loop on hold  [10/10 episodes already done]
  A40-E22-ledger-p256-vis-put-s0 closed_loop on hold  [10/10 episodes already done]
  A40-E22-ledger-p256-vis-put-s1 closed_loop on hold  [10/10 episodes already done]
  A40-E22-ledger-p256-vis-put-s2 closed_loop on hold  [10/10 episodes already done]
  A40-E22-ledger-p256-vis-put-s3 closed_loop on hold  [10/10 episodes already done]
  A40-E22-ledger-p256-vis-put-s4 closed_loop on hold  [10/10 episodes already done]
  A40-E22-ledger-p256-hid-put-s0 closed_loop on hold  [10/10 episodes already done]
  A40-E22-ledger-p256-hid-put-s1 closed_loop on hold  [10/10 episodes already done]
  A40-E22-ledger-p256-hid-put-s2 closed_loop on hold  [10/10 episodes already done]
  A40-E22-ledger-p256-hid-put-s3 closed_loop on hold  [10/10 episodes already done]
  A40-E22-ledger-p256-hid-put-s4 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p1024-vis-swap-s0 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p1024-vis-swap-s1 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p1024-vis-swap-s2 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p1024-vis-swap-s3 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p1024-vis-swap-s4 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p1024-hid-swap-s0 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p1024-hid-swap-s1 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p1024-hid-swap-s2 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p1024-hid-swap-s3 closed_loop on hold  [10/10 episodes already done]
  A40-E22-clock-p1024-hid-swap-s4 closed_loop on hold  [10/10 episodes already done]
  A40-E22-ledger-p1024-vis-swap-s0 closed_loop on hold  [10/10 episodes already done]
  A40-E22-ledger-p1024-vis-swap-s1 closed_loop on hold  [10/10 episodes already done]
  A40-E22-ledger-p1024-vis-swap-s2 closed_loop on hold  [10/10 episodes already done]
  A40-E22-ledger-p1024-vis-swap-s3 closed_loop on hold  [10/10 episodes already done]
  A40-E22-ledger-p1024-vis-swap-s4 closed_loop on hold  [10/10 episodes already done]
  A40-E22-ledger-p1024-hid-swap-s0 closed_loop on hold  [10/10 episodes already done]
  A40-E22-ledger-p1024-hid-swap-s1 closed_loop on hold  [10/10 episodes already done]
  A40-E22-ledger-p1024-hid-swap-s2 closed_loop on hold  [10/10 episodes already done]
  A40-E22-ledger-p1024-hid-swap-s3 closed_loop on hold  [10/10 episodes already done]
  A40-E22-ledger-p1024-hid-swap-s4 closed_loop on hold  [10/10 episodes already done]
  A40-battery_count-smoke closed_loop after A40-fetch-battery_count-e30
  A40-E15-battery_count-s0 closed_loop after A40-battery_count-smoke
  A40-E15-battery_count-s1 closed_loop after A40-battery_count-smoke
  A40-E15-battery_count-s2 closed_loop after A40-battery_count-smoke
  A40-E15-battery_count-s3 closed_loop after A40-battery_count-smoke
  A40-E15-battery_count-s4 closed_loop after A40-battery_count-smoke
  A40-E15-battery_count-s5 closed_loop after A40-battery_count-smoke
  A40-E15-battery_count-s6 closed_loop after A40-battery_count-smoke
  A40-E15-battery_count-s7 closed_loop after A40-battery_count-smoke
  A40-E15-battery_count-s8 closed_loop after A40-battery_count-smoke
  A40-E15-battery_count-s9 closed_loop after A40-battery_count-smoke
  A40-E15-verdict    shell       after A40-E15-battery_count-s0, A40-E15-battery_count-s1, A40-E15-battery_count-s2, A40-E15-battery_count-s3, A40-E15-battery_count-s4, A40-E15-battery_count-s5, A40-E15-battery_count-s6, A40-E15-battery_count-s7, A40-E15-battery_count-s8, A40-E15-battery_count-s9
  A40-MAIN2-rearrange_ar-rearr-s0 closed_loop on hold
  A40-MAIN2-rearrange_ar-rearr-s1 closed_loop on hold
  A40-MAIN2-rearrange_ar-rearr-s2 closed_loop on hold
  A40-MAIN2-rearrange_ar-rearr-s3 closed_loop on hold
  A40-MAIN2-rearrange_ar-rearr-s4 closed_loop on hold
  A40-MAIN2-rearrange_ar-rearr-s5 closed_loop on hold
  A40-MAIN2-rearrange_ar-rearr-s6 closed_loop on hold
  A40-MAIN2-rearrange_ar-rearr-s7 closed_loop on hold
  A40-MAIN2-rearrange_ar-rearr-s8 closed_loop on hold
  A40-MAIN2-rearrange_ar-rearr-s9 closed_loop on hold
  A40-MAIN2-swapT_ar-swapT-s0 closed_loop on hold
  A40-MAIN2-swapT_ar-swapT-s1 closed_loop on hold
  A40-MAIN2-swapT_ar-swapT-s2 closed_loop on hold
  A40-MAIN2-swapT_ar-swapT-s3 closed_loop on hold
  A40-MAIN2-swapT_ar-swapT-s4 closed_loop on hold
  A40-MAIN2-swapT_ar-swapT-s5 closed_loop on hold
  A40-MAIN2-swapT_ar-swapT-s6 closed_loop on hold
  A40-MAIN2-swapT_ar-swapT-s7 closed_loop on hold
  A40-MAIN2-swapT_ar-swapT-s8 closed_loop on hold
  A40-MAIN2-swapT_ar-swapT-s9 closed_loop on hold
  A40-c24b-audit-off-s0 closed_loop on hold
  A40-c24b-audit-off-s1 closed_loop on hold
  A40-c24b-audit-off-s2 closed_loop on hold
  A40-c24b-audit-mfirst-s0 closed_loop on hold
  A40-c24b-audit-mfirst-s1 closed_loop on hold
  A40-c24b-audit-mfirst-s2 closed_loop on hold
  A40-c24b-audit-mnear-s0 closed_loop on hold
  A40-c24b-audit-mnear-s1 closed_loop on hold
  A40-c24b-audit-mnear-s2 closed_loop on hold
  A40-V21-C24B-report shell       on hold
  A40-v21-obs_cf200-e20-s7 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])  [9/10 episodes already done]
  A40-v21-obs_cf200-e20-s9 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-V21-C25-report shell       after A40-v21-obs_cf200-e20-s7, A40-v21-obs_cf200-e20-s9
  A40-fs-obs_s800_20-e10-s0 closed_loop after A40-fetch-obs_s800_20-e10
  A40-fs-obs_s800_20-e10-s1 closed_loop after A40-fetch-obs_s800_20-e10
  A40-fs-obs_s800_20-e10-s2 closed_loop after A40-fetch-obs_s800_20-e10
  A40-fs-obs_s800_20-e10-s3 closed_loop after A40-fetch-obs_s800_20-e10
  A40-fs-obs_s800_20-e10-s4 closed_loop after A40-fetch-obs_s800_20-e10
  A40-fs-obs_s800_20-e10-s5 closed_loop after A40-fetch-obs_s800_20-e10
  A40-fs-obs_s800_20-e10-s6 closed_loop after A40-fetch-obs_s800_20-e10
  A40-fs-obs_s800_20-e10-s7 closed_loop after A40-fetch-obs_s800_20-e10
  A40-fs-obs_s800_20-e10-s8 closed_loop after A40-fetch-obs_s800_20-e10
  A40-fs-obs_s800_20-e10-s9 closed_loop after A40-fetch-obs_s800_20-e10
  A40-FS-report-obs_s800_20-e10 shell       after A40-fs-obs_s800_20-e10-s0, A40-fs-obs_s800_20-e10-s1, A40-fs-obs_s800_20-e10-s2, A40-fs-obs_s800_20-e10-s3, A40-fs-obs_s800_20-e10-s4, A40-fs-obs_s800_20-e10-s5, A40-fs-obs_s800_20-e10-s6, A40-fs-obs_s800_20-e10-s7, A40-fs-obs_s800_20-e10-s8, A40-fs-obs_s800_20-e10-s9
  A40-fs-obs_s800_20-e20-s0 closed_loop after A40-fetch-obs_s800_20-e20
  A40-fs-obs_s800_20-e20-s1 closed_loop after A40-fetch-obs_s800_20-e20
  A40-fs-obs_s800_20-e20-s2 closed_loop after A40-fetch-obs_s800_20-e20
  A40-fs-obs_s800_20-e20-s3 closed_loop after A40-fetch-obs_s800_20-e20
  A40-fs-obs_s800_20-e20-s4 closed_loop after A40-fetch-obs_s800_20-e20
  A40-fs-obs_s800_20-e20-s5 closed_loop after A40-fetch-obs_s800_20-e20
  A40-fs-obs_s800_20-e20-s6 closed_loop after A40-fetch-obs_s800_20-e20
  A40-fs-obs_s800_20-e20-s7 closed_loop after A40-fetch-obs_s800_20-e20
  A40-fs-obs_s800_20-e20-s8 closed_loop after A40-fetch-obs_s800_20-e20
  A40-fs-obs_s800_20-e20-s9 closed_loop after A40-fetch-obs_s800_20-e20
  A40-FS-report-obs_s800_20-e20 shell       after A40-fs-obs_s800_20-e20-s0, A40-fs-obs_s800_20-e20-s1, A40-fs-obs_s800_20-e20-s2, A40-fs-obs_s800_20-e20-s3, A40-fs-obs_s800_20-e20-s4, A40-fs-obs_s800_20-e20-s5, A40-fs-obs_s800_20-e20-s6, A40-fs-obs_s800_20-e20-s7, A40-fs-obs_s800_20-e20-s8, A40-fs-obs_s800_20-e20-s9
  A40-fs-obs_s800_s18-e10-s0 closed_loop after A40-fetch-obs_s800_s18-e10
  A40-fs-obs_s800_s18-e10-s1 closed_loop after A40-fetch-obs_s800_s18-e10
  A40-fs-obs_s800_s18-e10-s2 closed_loop after A40-fetch-obs_s800_s18-e10
  A40-fs-obs_s800_s18-e10-s3 closed_loop after A40-fetch-obs_s800_s18-e10
  A40-fs-obs_s800_s18-e10-s4 closed_loop after A40-fetch-obs_s800_s18-e10
  A40-fs-obs_s800_s18-e10-s5 closed_loop after A40-fetch-obs_s800_s18-e10
  A40-fs-obs_s800_s18-e10-s6 closed_loop after A40-fetch-obs_s800_s18-e10
  A40-fs-obs_s800_s18-e10-s7 closed_loop after A40-fetch-obs_s800_s18-e10
  A40-fs-obs_s800_s18-e10-s8 closed_loop after A40-fetch-obs_s800_s18-e10
  A40-fs-obs_s800_s18-e10-s9 closed_loop after A40-fetch-obs_s800_s18-e10
  A40-FS-report-obs_s800_s18-e10 shell       after A40-fs-obs_s800_s18-e10-s0, A40-fs-obs_s800_s18-e10-s1, A40-fs-obs_s800_s18-e10-s2, A40-fs-obs_s800_s18-e10-s3, A40-fs-obs_s800_s18-e10-s4, A40-fs-obs_s800_s18-e10-s5, A40-fs-obs_s800_s18-e10-s6, A40-fs-obs_s800_s18-e10-s7, A40-fs-obs_s800_s18-e10-s8, A40-fs-obs_s800_s18-e10-s9
  A40-fs-obs_s1600-e5-s0 closed_loop after A40-fetch-obs_s1600-e5
  A40-fs-obs_s1600-e5-s1 closed_loop after A40-fetch-obs_s1600-e5
  A40-fs-obs_s1600-e5-s2 closed_loop after A40-fetch-obs_s1600-e5
  A40-fs-obs_s1600-e5-s3 closed_loop after A40-fetch-obs_s1600-e5
  A40-fs-obs_s1600-e5-s4 closed_loop after A40-fetch-obs_s1600-e5
  A40-fs-obs_s1600-e5-s5 closed_loop after A40-fetch-obs_s1600-e5
  A40-fs-obs_s1600-e5-s6 closed_loop after A40-fetch-obs_s1600-e5
  A40-fs-obs_s1600-e5-s7 closed_loop after A40-fetch-obs_s1600-e5
  A40-fs-obs_s1600-e5-s8 closed_loop after A40-fetch-obs_s1600-e5
  A40-fs-obs_s1600-e5-s9 closed_loop after A40-fetch-obs_s1600-e5
  A40-FS-report-obs_s1600-e5 shell       after A40-fs-obs_s1600-e5-s0, A40-fs-obs_s1600-e5-s1, A40-fs-obs_s1600-e5-s2, A40-fs-obs_s1600-e5-s3, A40-fs-obs_s1600-e5-s4, A40-fs-obs_s1600-e5-s5, A40-fs-obs_s1600-e5-s6, A40-fs-obs_s1600-e5-s7, A40-fs-obs_s1600-e5-s8, A40-fs-obs_s1600-e5-s9
  A40-fs-obs_s1600-e10-s0 closed_loop after A40-fetch-obs_s1600-e10
  A40-fs-obs_s1600-e10-s1 closed_loop after A40-fetch-obs_s1600-e10
  A40-fs-obs_s1600-e10-s2 closed_loop after A40-fetch-obs_s1600-e10
  A40-fs-obs_s1600-e10-s3 closed_loop after A40-fetch-obs_s1600-e10
  A40-fs-obs_s1600-e10-s4 closed_loop after A40-fetch-obs_s1600-e10
  A40-fs-obs_s1600-e10-s5 closed_loop after A40-fetch-obs_s1600-e10
  A40-fs-obs_s1600-e10-s6 closed_loop after A40-fetch-obs_s1600-e10
  A40-fs-obs_s1600-e10-s7 closed_loop after A40-fetch-obs_s1600-e10
  A40-fs-obs_s1600-e10-s8 closed_loop after A40-fetch-obs_s1600-e10
  A40-fs-obs_s1600-e10-s9 closed_loop after A40-fetch-obs_s1600-e10
  A40-FS-report-obs_s1600-e10 shell       after A40-fs-obs_s1600-e10-s0, A40-fs-obs_s1600-e10-s1, A40-fs-obs_s1600-e10-s2, A40-fs-obs_s1600-e10-s3, A40-fs-obs_s1600-e10-s4, A40-fs-obs_s1600-e10-s5, A40-fs-obs_s1600-e10-s6, A40-fs-obs_s1600-e10-s7, A40-fs-obs_s1600-e10-s8, A40-fs-obs_s1600-e10-s9
  A40-d11-ar2s18-e30-put-s0 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d11-ar2s18-e30-put-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d11-ar2s18-e30-put-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d11-ar2s18-e30-put-s3 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d11-ar2s18-e30-put-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d11-ar2s18-e30-put-s5 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d11-ar2s18-e30-put-s6 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d11-ar2s18-e30-put-s7 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3])
  A40-d11-ar2s18-e30-put-s8 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d11-ar2s18-e30-put-s9 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d11-ar2s18-e30-swap-s0 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d11-ar2s18-e30-swap-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d11-ar2s18-e30-swap-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d11-ar2s18-e30-swap-s3 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d11-ar2s18-e30-swap-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d11-ar2s18-e30-swap-s5 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d11-ar2s18-e30-swap-s6 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d11-ar2s18-e30-swap-s7 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d11-ar2s18-e30-swap-s8 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d11-ar2s18-e30-swap-s9 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d11-ar2s18-e10-swap-s0 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d11-ar2s18-e10-swap-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d11-ar2s18-e10-swap-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d11-ar2s18-e10-swap-s3 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d11-ar2s18-e10-swap-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d11-ar2s18-e10-swap-s5 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d11-ar2s18-e10-swap-s6 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d11-ar2s18-e10-swap-s7 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d11-ar2s18-e10-swap-s8 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d11-ar2s18-e10-swap-s9 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d11-report     shell       after A40-d11-ar2s18-e30-put-s0, A40-d11-ar2s18-e30-put-s1, A40-d11-ar2s18-e30-put-s2, A40-d11-ar2s18-e30-put-s3, A40-d11-ar2s18-e30-put-s4, A40-d11-ar2s18-e30-put-s5, A40-d11-ar2s18-e30-put-s6, A40-d11-ar2s18-e30-put-s7, A40-d11-ar2s18-e30-put-s8, A40-d11-ar2s18-e30-put-s9, A40-d11-ar2s18-e30-swap-s0, A40-d11-ar2s18-e30-swap-s1, A40-d11-ar2s18-e30-swap-s2, A40-d11-ar2s18-e30-swap-s3, A40-d11-ar2s18-e30-swap-s4, A40-d11-ar2s18-e30-swap-s5, A40-d11-ar2s18-e30-swap-s6, A40-d11-ar2s18-e30-swap-s7, A40-d11-ar2s18-e30-swap-s8, A40-d11-ar2s18-e30-swap-s9, A40-d11-ar2s18-e10-swap-s0, A40-d11-ar2s18-e10-swap-s1, A40-d11-ar2s18-e10-swap-s2, A40-d11-ar2s18-e10-swap-s3, A40-d11-ar2s18-e10-swap-s4, A40-d11-ar2s18-e10-swap-s5, A40-d11-ar2s18-e10-swap-s6, A40-d11-ar2s18-e10-swap-s7, A40-d11-ar2s18-e10-swap-s8, A40-d11-ar2s18-e10-swap-s9
  A40-d10-ranking_v3a-off-s0 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d10-ranking_v3a-off-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d10-ranking_v3a-off-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d10-ranking_v3a-mfirst-s0 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d10-ranking_v3a-mfirst-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d10-ranking_v3a-mfirst-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d10-ranking_v3a-mnear-s0 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d10-ranking_v3a-mnear-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d10-ranking_v3a-mnear-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-d10-report     shell       after A40-d10-ranking_v3a-off-s0, A40-d10-ranking_v3a-off-s1, A40-d10-ranking_v3a-off-s2, A40-d10-ranking_v3a-mfirst-s0, A40-d10-ranking_v3a-mfirst-s1, A40-d10-ranking_v3a-mfirst-s2, A40-d10-ranking_v3a-mnear-s0, A40-d10-ranking_v3a-mnear-s1, A40-d10-ranking_v3a-mnear-s2
  A40-v21-ar2_pw-e10-s0 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-v21-ar2_pw-e10-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-v21-ar2_pw-e10-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-v21-ar2_pw-e10-s3 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-v21-ar2_pw-e10-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-v21-ar2_pw-e10-s5 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-v21-ar2_pw-e10-s6 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-v21-ar2_pw-e10-s7 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-v21-ar2_pw-e10-s8 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-v21-ar2_pw-e10-s9 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-V21-C23-report shell       after A40-v21-ar2_pw-e10-s0, A40-v21-ar2_pw-e10-s1, A40-v21-ar2_pw-e10-s2, A40-v21-ar2_pw-e10-s3, A40-v21-ar2_pw-e10-s4, A40-v21-ar2_pw-e10-s5, A40-v21-ar2_pw-e10-s6, A40-v21-ar2_pw-e10-s7, A40-v21-ar2_pw-e10-s8, A40-v21-ar2_pw-e10-s9, A40-V21-C23-verdict
  A40-stepa-ar_2task_e20-s6 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-ar_2task_e20-s7 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-ar_2task_e20-s8 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-ar_2task_e20-s9 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-cover_arprop_e10-s0 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-cover_arprop_e10-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-cover_arprop_e10-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-cover_arprop_e10-s3 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-cover_arprop_e10-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-cover_arprop_e10-s5 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-cover_arprop_e10-s6 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-cover_arprop_e10-s7 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-cover_arprop_e10-s8 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-cover_arprop_e10-s9 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-cover_arprop_e20-s0 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-cover_arprop_e20-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-cover_arprop_e20-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-cover_arprop_e20-s3 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-cover_arprop_e20-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-cover_arprop_e20-s5 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-cover_arprop_e20-s6 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-cover_arprop_e20-s7 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-cover_arprop_e20-s8 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-cover_arprop_e20-s9 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-rearrange_arprop_e20-s0 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-rearrange_arprop_e20-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-rearrange_arprop_e20-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-rearrange_arprop_e20-s3 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-rearrange_arprop_e20-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-rearrange_arprop_e20-s5 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-rearrange_arprop_e20-s6 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-rearrange_arprop_e20-s7 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-rearrange_arprop_e20-s8 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-stepa-rearrange_arprop_e20-s9 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E22h-verdict   shell       after A40-E22h-fetch-hid2

FAILURES SEEN (latest per task)
  A40-HF-autoprune-loop attempt 3: stalled: nothing written for 120 min  -> now done ERROR
  A40-v20joint3-put-s0 attempt 2: 2 episodes ended with ERROR.json (re-run retries only those)  -> now done DONE
  A40-d8-swapT_x16-s0 attempt 2: 6 episodes ended with ERROR.json (re-run retries only those)  -> now done DONE
  A40-d8-swapT-report attempt 3: rc=1: Python exception  -> now done ERROR
  A40-d8-swapT_x16-gate attempt 3: rc=3: non-zero exit  -> now done ERROR
  A40-d8-swapT_x32-gate attempt 3: rc=3: non-zero exit  -> now done ERROR
  A40-d8-swapT_s50-gate attempt 3: rc=3: non-zero exit  -> now done ERROR
  A40-d8-swapT-report100 attempt 3: rc=1: Python exception  -> now done ERROR
  A40-d8-press_x16-s1 attempt 3: rc=1: Python exception  -> now done ERROR
  A40-d8-press_x16-s4 attempt 3: rc=1: Python exception  -> now done ERROR
  A40-d8-press_x32-s0 attempt 3: rc=1: Python exception  -> now done ERROR
  A40-d8-press_x32-s1 attempt 3: rc=1: Python exception  -> now done ERROR
  A40-d8-press_x32-s2 attempt 3: rc=1: Python exception  -> now done ERROR
  A40-d8-press_x32-s3 attempt 3: rc=1: Python exception  -> now done ERROR
  A40-d8-press_x32-s4 attempt 3: rc=1: Python exception  -> now done ERROR
  A40-d8-press_s50-s0 attempt 3: rc=1: Python exception  -> now done ERROR
  A40-d8-press_s50-s1 attempt 3: rc=1: Python exception  -> now done ERROR
  A40-d8-press_s50-s2 attempt 3: rc=1: Python exception  -> now done ERROR
  A40-d8-press_s50-s3 attempt 3: rc=1: Python exception  -> now done ERROR
  A40-d8-press_s50-s4 attempt 3: rc=1: Python exception  -> now done ERROR
  A40-d8-press_x16-gate attempt 3: rc=3: non-zero exit  -> now done ERROR
  A40-d8-press_x32-gate attempt 3: rc=3: non-zero exit  -> now done ERROR
  A40-d8-press_s50-gate attempt 3: rc=3: non-zero exit  -> now done ERROR
  A40-d8-rearr18_x16-s0 attempt 3: rc=1: Python exception  -> now done ERROR
  A40-d8-rearr18_x16-s1 attempt 3: rc=1: Python exception  -> now done ERROR
  A40-d8-rearr18_x16-s2 attempt 3: rc=1: Python exception  -> now done ERROR
  A40-d8-rearr18_x16-s3 attempt 3: rc=1: Python exception  -> now done ERROR
  A40-d8-rearr18_x16-s4 attempt 3: rc=1: Python exception  -> now done ERROR
  A40-d8-rearr18_x16-gate attempt 3: rc=3: non-zero exit  -> now done ERROR
  A40-d9-rearr_pw_e30-off-s0 attempt 3: rc=1: Python exception  -> now done ERROR
  A40-d9-rearr_pw_e30-off-s1 attempt 3: rc=1: Python exception  -> now done ERROR
  A40-d9-rearr_pw_e30-off-s2 attempt 3: rc=1: Python exception  -> now done ERROR
  A40-d9-rearr_pw_e30-off-s3 attempt 2: rc=1: Python exception  -> now pending
  A40-d9-rearr_pw_e30-off-s4 attempt 2: rc=1: Python exception  -> now pending
  A40-d9-rearr_pw_s18_e30-off-s0 attempt 2: rc=1: Python exception  -> now pending
  A40-d9-rearr_pw_s18_e30-off-s1 attempt 2: rc=1: Python exception  -> now pending
  A40-d9-rearr_pw_s18_e30-off-s2 attempt 2: rc=1: Python exception  -> now pending
  A40-d9-rearr_pw_s18_e30-off-s3 attempt 2: rc=1: Python exception  -> now pending
  A40-d9-rearr_pw_s18_e30-off-s4 attempt 2: rc=1: Python exception  -> now pending
  A40-v20told10-s0   attempt 3: 10 episodes ended with ERROR.json (re-run retries only those)  -> now done INCONCLUSIVE
  A40-v20told10-s1   attempt 3: 10 episodes ended with ERROR.json (re-run retries only those)  -> now done INCONCLUSIVE
  A40-v20told10-s2   attempt 3: 10 episodes ended with ERROR.json (re-run retries only those)  -> now done INCONCLUSIVE
  A40-v20told10-s3   attempt 3: 10 episodes ended with ERROR.json (re-run retries only those)  -> now done INCONCLUSIVE
  A40-v20told10-s4   attempt 3: 10 episodes ended with ERROR.json (re-run retries only those)  -> now done INCONCLUSIVE
  A40-v20told10-s5   attempt 3: 10 episodes ended with ERROR.json (re-run retries only those)  -> now done INCONCLUSIVE
  A40-v20told10-s6   attempt 3: 10 episodes ended with ERROR.json (re-run retries only those)  -> now done INCONCLUSIVE
  A40-v20told10-s7   attempt 3: 10 episodes ended with ERROR.json (re-run retries only those)  -> now done INCONCLUSIVE
  A40-v20told10-s8   attempt 3: 10 episodes ended with ERROR.json (re-run retries only those)  -> now done INCONCLUSIVE
  A40-v20told10-s9   attempt 3: 10 episodes ended with ERROR.json (re-run retries only those)  -> now done INCONCLUSIVE
  A40-v20told20-s0   attempt 3: 10 episodes ended with ERROR.json (re-run retries only those)  -> now done INCONCLUSIVE
  A40-v20told20-s1   attempt 3: 10 episodes ended with ERROR.json (re-run retries only those)  -> now done INCONCLUSIVE
  A40-v20told20-s2   attempt 3: 10 episodes ended with ERROR.json (re-run retries only those)  -> now done INCONCLUSIVE
  A40-v20told20-s3   attempt 3: 10 episodes ended with ERROR.json (re-run retries only those)  -> now done INCONCLUSIVE
  A40-v20told20-s4   attempt 3: 10 episodes ended with ERROR.json (re-run retries only those)  -> now done INCONCLUSIVE
  A40-v20told20-s5   attempt 3: 10 episodes ended with ERROR.json (re-run retries only those)  -> now done INCONCLUSIVE
  A40-v20told20-s6   attempt 3: 10 episodes ended with ERROR.json (re-run retries only those)  -> now done INCONCLUSIVE
  A40-v20told20-s7   attempt 3: 10 episodes ended with ERROR.json (re-run retries only those)  -> now done INCONCLUSIVE
  A40-v20told20-s8   attempt 3: 10 episodes ended with ERROR.json (re-run retries only those)  -> now done INCONCLUSIVE
  A40-v20told20-s9   attempt 3: 10 episodes ended with ERROR.json (re-run retries only those)  -> now done INCONCLUSIVE
  T2                 attempt 2: rc=1: non-zero exit  -> now done PASS
  PB-events2         attempt 3: rc=1: non-zero exit  -> now done ERROR
  PB-parity          attempt 3: rc=1: non-zero exit  -> now done ERROR
  PB-parity2         attempt 3: rc=1: non-zero exit  -> now done ERROR
  PB-plan            attempt 3: rc=2: non-zero exit  -> now done PASS
  PB-s1-A            attempt 2: rc=1: non-zero exit  -> now done PASS
  A40-MAIN-cover_ar30-s9 attempt 2: 1 episodes ended with ERROR.json (re-run retries only those)  -> now done DONE
  A40-MAIN-obs_ar30-s5 attempt 2: 2 episodes ended with ERROR.json (re-run retries only those)  -> now done DONE
  A40-MAIN-obs_ar30-s6 attempt 2: 2 episodes ended with ERROR.json (re-run retries only those)  -> now done DONE
  A40-MAIN-obs_ar30-s7 attempt 2: 4 episodes ended with ERROR.json (re-run retries only those)  -> now done DONE
  A40-MAIN-obs_ar30-s8 attempt 2: 5 episodes ended with ERROR.json (re-run retries only those)  -> now done DONE
  A40-MAIN-obs_ar30-s9 attempt 2: 7 episodes ended with ERROR.json (re-run retries only those)  -> now done DONE
  A40-MAIN-obs_arprop30-s2 attempt 2: 9 episodes ended with ERROR.json (re-run retries only those)  -> now done DONE
  A40-fetch-prop10   attempt 2: stalled: nothing written for 120 min  -> now done PASS
  A40-fetch-prop20   attempt 2: stalled: nothing written for 120 min  -> now done PASS
  A40-fetch-ar10     attempt 2: stalled: nothing written for 120 min  -> now done PASS
  A40-fetch-ar20     attempt 2: stalled: nothing written for 120 min  -> now done PASS
  A40-E5-index-matters attempt 3: rc=1: non-zero exit  -> now done ERROR
  A40-E5b-clock-put  attempt 3: rc=1: non-zero exit  -> now done ERROR
  A40-fetch-rearrange_arprop-e30 attempt 2: exec process died without a verdict (killed / crash / container restart)  -> now done PASS
  A40-fetch-ar2_arev-e30 attempt 2: exec process died without a verdict (killed / crash / container restart)  -> now done PASS
  A40-fetch-ar2_tw-e30 attempt 2: exec process died without a verdict (killed / crash / container restart)  -> now done PASS
  A40-Z6-occupancy   attempt 3: rc=2: non-zero exit  -> now done ERROR
  A40-E22a-fetch-all attempt 2: exec process died without a verdict (killed / crash / container restart)  -> now done PASS
  A40-fetch-battery_count-e30 attempt 2: exec process died without a verdict (killed / crash / container restart)  -> now running
  A40-v21-rearr_arprop_pw-e10-s4 attempt 3: rc=1: Python exception  -> now done DONE
  A40-v21-obs_cf200-e20-s7 attempt 2: rc=1: Python exception  -> now pending
  A40-v21-obs_cf200-e20-s9 attempt 1: rc=1: Python exception  -> now pending
  A40-fs-obs_s800-e5-s2 attempt 2: 10 episodes ended with ERROR.json (re-run retries only those)  -> now done DONE
  A40-d11-ar2s18-e30-put-s0 attempt 1: rc=1: Python exception  -> now pending
  A40-d11-ar2s18-e30-put-s1 attempt 1: rc=1: Python exception  -> now pending
  A40-d11-ar2s18-e30-put-s2 attempt 1: rc=1: Python exception  -> now pending
  A40-d11-ar2s18-e30-put-s3 attempt 1: rc=1: Python exception  -> now pending
  A40-d11-ar2s18-e30-put-s4 attempt 1: rc=1: Python exception  -> now pending
  A40-d11-ar2s18-e30-put-s5 attempt 1: rc=1: Python exception  -> now pending
  A40-d11-ar2s18-e30-put-s6 attempt 1: rc=1: Python exception  -> now pending
  A40-d11-ar2s18-e30-put-s7 attempt 1: rc=1: Python exception  -> now pending

LATEST VERDICTS
  11-29 00:46  A40-d8-rearr18_x16-b0 SKIPPED       
  11-29 00:46  A40-d8-rearr18_x16-b1 SKIPPED       
  11-29 00:46  A40-d8-rearr18_x16-b2 SKIPPED       
  11-29 00:46  A40-d8-rearr18_x16-b3 SKIPPED       
  11-29 00:46  A40-d8-rearr18_x16-b4 SKIPPED       
  11-29 00:46  A40-d8-rearr18-report100 PASS          rc=0
  11-29 01:09  A40-C36FB-bank-put PASS          rc=0
  11-29 01:39  A40-d8r-press_x16-s1 DONE          press_button/on n=46 pressed=46 n1_correct=18 n2_correct=19 confirmed=46 count_correct=8 success=8 prog=0.38; errors=4
```

## A40-fetch-ar2_pw-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-ar2_pw-e30.log):
```
[fetch] 2026-11-28 15:50:04 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 15:55:04 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 16:00:05 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 16:05:05 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 16:10:06 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 16:15:06 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 16:20:07 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 16:25:07 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 16:30:08 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 16:35:08 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 16:40:09 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 16:45:10 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 16:50:10 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 16:55:11 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 17:00:11 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 17:05:12 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 17:10:12 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 17:15:13 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 17:20:13 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 17:25:14 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 17:30:14 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 17:35:15 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 17:40:16 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 17:45:16 waiting for exports/ar2_pw_e30 on the relay
[fetch] 2026-11-28 17:50:17 waiting for exports/ar2_pw_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-ar2_pw-e30.log):
```

[pool] 2026-11-28 03:37:39 exec A40-fetch-ar2_pw-e30 GPU None 
[pool] 2026-11-28 03:37:43 A40-fetch-ar2_pw-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-ar2_pw-e30.log
```

## A40-V21-C25-e10look (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-V21-C25-e10look.log):
```

[queue5] 2026-11-28 08:47:50 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/v21_verdict.py c25
{"run": "card 25 obs_cf200 (same table, every target) against obs_s200", "sesoi": 0.15, "finished": {"obs_cf200_e30": 0, "obs_s200_e30": 100}, "verdict": "WAIT (0 / 100 of 100)", "described": {"obs_cf200_e10": {"success": 30, "against_obs_s200_e30": {"scenes": 100, "new": 30, "ref": 15, "D": 0.15, "ci95": [0.04, 0.26], "only_new": 25, "only_ref": 10}, "against_obs_ar_e30": {"scenes": 100, "new": 30, "ref": 13, "D": 0.17, "ci95": [0.06, 0.29], "only_new": 27, "only_ref": 10}, "against_obs_s800_e10": {"scenes": 100, "new": 30, "ref": 49, "D": -0.19, "ci95": [-0.32, -0.06], "only_new": 14, "only_ref": 33}}}}
V21 C25: WAIT (0 / 100 of 100)
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-V21-C25-e10look.log):
```

[pool] 2026-11-28 08:47:46 exec A40-V21-C25-e10look GPU None 
[pool] 2026-11-28 08:47:50 A40-V21-C25-e10look: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-V21-C25-e10look.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-V21-C25-e10look.md
[queue5] 2026-11-28 08:47:55 A40-V21-C25-e10look: PASS  rc=0
```

## A40-HF-autoprune-loop2 (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-HF-autoprune-loop2.log):
```
HF PRUNE AUTO: deleted []; projected 93.9%
[autoprune-loop] 2026-11-28 08:12:43 next check in 60 min
[autoprune-loop] 2026-11-28 09:12:43 usage refresh + check
[autoprune-loop] 2026-11-28 09:12:48 usage refreshed; prune check
HF PRUNE AUTO: deleted []; projected 93.9%
[autoprune-loop] 2026-11-28 09:13:03 next check in 60 min
[autoprune-loop] 2026-11-28 10:13:03 usage refresh + check
[autoprune-loop] 2026-11-28 10:13:08 usage refreshed; prune check
HF PRUNE AUTO: deleted []; projected 95.1%
[autoprune-loop] 2026-11-28 10:13:25 next check in 60 min
[autoprune-loop] 2026-11-28 11:13:25 usage refresh + check
[autoprune-loop] 2026-11-28 11:13:30 usage refreshed; prune check
HF PRUNE AUTO: deleted []; projected 95.1%
[autoprune-loop] 2026-11-28 11:13:42 next check in 60 min
[autoprune-loop] 2026-11-28 12:13:42 usage refresh + check
[autoprune-loop] 2026-11-28 12:13:47 usage refreshed; prune check
HF PRUNE AUTO: deleted []; projected 96.4%
[autoprune-loop] 2026-11-28 12:14:00 next check in 60 min
[autoprune-loop] 2026-11-28 13:14:00 usage refresh + check
[autoprune-loop] 2026-11-28 13:14:04 usage refreshed; prune check
[autoprune] rearr_ar_pw_e10: A40 copy verified (9a68dbff30635c66), 12.0 GB
[autoprune] rearr_arprop_pw_e10: A40 copy verified (c8636f76d12059b0), 12.0 GB
HF PRUNE AUTO: deleted ['rearr_ar_pw_e10', 'rearr_arprop_pw_e10']; projected 95.1%
[autoprune-loop] 2026-11-28 13:16:20 next check in 60 min
[autoprune-loop] 2026-11-28 14:16:20 window over (11-28 14:00)
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-HF-autoprune-loop2.log):
```

[pool] 2026-11-27 22:07:32 exec A40-HF-autoprune-loop2 GPU None 
[pool] 2026-11-27 22:07:36 A40-HF-autoprune-loop2: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-HF-autoprune-loop2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-HF-autoprune-loop2.md
[queue5] 2026-11-28 14:16:25 A40-HF-autoprune-loop2: PASS  rc=0
```

## A40-fetch-obs_cf200-e30 (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-obs_cf200-e30.log):
```
[fetch] 2026-11-28 10:25:00 waiting for exports/obs_cf200_e30 on the relay
[fetch] 2026-11-28 10:30:00 waiting for exports/obs_cf200_e30 on the relay
[fetch] 2026-11-28 10:35:01 waiting for exports/obs_cf200_e30 on the relay
[fetch] 2026-11-28 10:40:02 waiting for exports/obs_cf200_e30 on the relay
[fetch] 2026-11-28 10:45:02 waiting for exports/obs_cf200_e30 on the relay
[fetch] 2026-11-28 10:50:03 waiting for exports/obs_cf200_e30 on the relay
[fetch] 2026-11-28 10:55:03 waiting for exports/obs_cf200_e30 on the relay
[fetch] 2026-11-28 11:00:04 waiting for exports/obs_cf200_e30 on the relay
[fetch] 2026-11-28 11:05:04 waiting for exports/obs_cf200_e30 on the relay
[fetch] 2026-11-28 11:10:05 waiting for exports/obs_cf200_e30 on the relay
[fetch] 2026-11-28 11:15:05 waiting for exports/obs_cf200_e30 on the relay
[fetch] 2026-11-28 11:20:06 waiting for exports/obs_cf200_e30 on the relay
[fetch] 2026-11-28 11:25:06 waiting for exports/obs_cf200_e30 on the relay
[fetch] 2026-11-28 11:30:07 waiting for exports/obs_cf200_e30 on the relay
[fetch] 2026-11-28 11:35:07 waiting for exports/obs_cf200_e30 on the relay
[fetch] disk before: /dev/sdb         19T   11T  6.6T  62% /workspace/FastWAM-memory2
[fetch] 2026-11-28 11:40:08 fetching obs_cf200_e30 (attempt 1)
[relay] get hhyfred/memwam-fullft/exports/obs_cf200_e30/export_e30.pt -> /workspace/FastWAM-memory2/outputs/fullft/exports/obs_cf200_e30/export_e30.pt (12042063395 bytes)
[relay] get hhyfred/memwam-fullft/exports/obs_cf200_e30/export_e30.pt.sha256 -> /workspace/FastWAM-memory2/outputs/fullft/exports/obs_cf200_e30/export_e30.pt.sha256 (80 bytes)
export_e30.pt: OK
total 11759844
drwxr-xr-x   2 root root        4096 Nov 28 11:48 .
drwxr-xr-x 106 root root        4096 Nov 28 11:40 ..
-rw-r--r--   1 root root 12042063395 Nov 28 11:48 export_e30.pt
-rw-r--r--   1 root root          80 Nov 28 11:48 export_e30.pt.sha256
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-obs_cf200-e30.log):
```

[pool] 2026-11-27 12:46:30 exec A40-fetch-obs_cf200-e30 GPU None 
[pool] 2026-11-27 12:46:34 A40-fetch-obs_cf200-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-obs_cf200-e30.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-obs_cf200-e30.md
[queue5] 2026-11-28 19:49:07 A40-fetch-obs_cf200-e30: PASS  rc=0
```

## A40-v21-obs_cf200-smoke (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-smoke.log):
```
[fullft] text from the training cache (observe_and_pickup/episode_0000000, 50 episodes share it; fingerprint 2579ac7058fe)
/restore-tmp/dense_joint_v1/data_path.py:16: UserWarning: The given NumPy array is not writable, and PyTorch does not support non-writable tensors. This means writing to this tensor will result in undefined behavior. You may want to copy the array to protect its data or make it writable before converting it to a tensor. This type of warning will be suppressed for the rest of this program. (Triggered internally at /opt/pytorch/pytorch/torch/csrc/utils/tensor_numpy.cpp:206.)
  return torch.stack([TF.resize(torch.from_numpy(np.ascontiguousarray(a)).permute(2,0,1).float()/255.,
[decide] 2026-11-28 11:52:04 obs_cf200_e30_smoke/on observe_and_pickup seed=4300000 frame=0/250 hist=0 policy=0.6s elapsed=7s
[decide] 2026-11-28 11:52:16 obs_cf200_e30_smoke/on observe_and_pickup seed=4300000 frame=32/250 hist=2 policy=0.5s elapsed=19s
[decide] 2026-11-28 11:52:33 obs_cf200_e30_smoke/on observe_and_pickup seed=4300000 frame=64/250 hist=3 policy=0.5s elapsed=36s
[decide] 2026-11-28 11:52:44 obs_cf200_e30_smoke/on observe_and_pickup seed=4300000 frame=96/250 hist=3 policy=0.5s elapsed=46s
[decide] 2026-11-28 11:53:01 obs_cf200_e30_smoke/on observe_and_pickup seed=4300000 frame=128/250 hist=3 policy=0.5s elapsed=63s
[decide] 2026-11-28 11:53:11 obs_cf200_e30_smoke/on observe_and_pickup seed=4300000 frame=160/250 hist=3 policy=0.5s elapsed=74s
[decide] 2026-11-28 11:53:21 obs_cf200_e30_smoke/on observe_and_pickup seed=4300000 frame=192/250 hist=3 policy=0.5s elapsed=84s
[decide] 2026-11-28 11:53:31 obs_cf200_e30_smoke/on observe_and_pickup seed=4300000 frame=224/250 hist=3 policy=0.6s elapsed=94s
[closed-loop] 2026-11-28 11:53:44 done  obs_cf200_e30_smoke/on observe_and_pickup seed=4300000 success=False targets=250/250 reward=0.0 lift=None  155s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
obs_cf200_e30_smoke/on  observe_and_pickup   1     0.00  [0.00,0.79]         -    0.00      250        -        -        -    0.5
rearr_ar_pw_e30_smoke/onrearrange_blocks   1     1.00  [0.21,1.00]      1.00    1.00      392        -        -        -    0.6
rearr_arprop_pw_e30_smoke/onrearrange_blocks   1     0.00  [0.00,0.79]      1.00    0.00      700        -        -        -    0.6
rearr_pw_s18_e30_smoke/onrearrange_blocks   1     0.00  [0.00,0.79]      1.00    0.00      700        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearr_ar_pw_e30_smoke/on vs rearr_arprop_pw_e30_smoke/on   1     0       1       0        0  1.000
  rearr_ar_pw_e30_smoke/on vs rearr_pw_s18_e30_smoke/on   1     0       1       0        0  1.000
  rearr_arprop_pw_e30_smoke/on vs rearr_pw_s18_e30_smoke/on   1     0       0       0        1  1.000

[summary] 4 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21smoke/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-smoke.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 19:53:50 A40-v21-obs_cf200-smoke: PASS  observe_and_pickup/on n=1  prog=0.00
```

## A40-v21-obs_cf200-s0 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-s0.log):
```
  obs_cf200_e20/on         vs obs_cf200_e30/on          23     8       2       0       13  0.500
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 912 episodes, 1 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/obs_cf200_e20/on/observe_and_pickup/seed_4300099/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-s0.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 20:18:33 A40-v21-obs_cf200-s0: DONE  observe_and_pickup/on n=23  prog=0.00
```

## A40-v21-obs_cf200-s1 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-s1.log):
```
  obs_cf200_e20/on         vs obs_cf200_e30/on          40    14       2       4       20  0.688
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 929 episodes, 1 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/obs_cf200_e20/on/observe_and_pickup/seed_4300099/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-s1.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 20:28:36 A40-v21-obs_cf200-s1: DONE  observe_and_pickup/on n=40  prog=0.00
```

## A40-v21-obs_cf200-s2 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-s2.log):
```
  obs_cf200_e20/on         vs obs_cf200_e30/on          43    14       2       5       22  0.453
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 932 episodes, 1 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/obs_cf200_e20/on/observe_and_pickup/seed_4300099/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-s2.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 20:29:56 A40-v21-obs_cf200-s2: DONE  observe_and_pickup/on n=44  prog=0.00
```

## A40-v21-obs_cf200-s3 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-s3.log):
```
  obs_cf200_e20/on         vs obs_cf200_e30/on          46    17       2       5       22  0.453
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 935 episodes, 1 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/obs_cf200_e20/on/observe_and_pickup/seed_4300099/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-s3.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 20:30:49 A40-v21-obs_cf200-s3: DONE  observe_and_pickup/on n=46  prog=0.00
```

## A40-v21-obs_cf200-s4 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-s4.log):
```
  obs_cf200_e20/on         vs obs_cf200_e30/on          73    26       6       9       32  0.607
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 966 episodes, 1 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/obs_cf200_e20/on/observe_and_pickup/seed_4300099/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-s4.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 20:43:54 A40-v21-obs_cf200-s4: DONE  observe_and_pickup/on n=77  prog=0.00
```

## A40-v21-obs_cf200-s5 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-s5.log):
```
  obs_cf200_e20/on         vs obs_cf200_e30/on          87    32       8      10       37  0.815
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 984 episodes, 1 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/obs_cf200_e20/on/observe_and_pickup/seed_4300099/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-s5.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 20:51:44 A40-v21-obs_cf200-s5: DONE  observe_and_pickup/on n=95  prog=0.00
```

## A40-v21-obs_cf200-s6 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-s6.log):
```
  obs_cf200_e20/on         vs obs_cf200_e30/on          85    32       8      10       35  0.815
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 980 episodes, 1 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/obs_cf200_e20/on/observe_and_pickup/seed_4300099/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-s6.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 20:50:06 A40-v21-obs_cf200-s6: DONE  observe_and_pickup/on n=91  prog=0.00
```

## A40-v21-obs_cf200-s7 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-s7.log):
```
  obs_cf200_e20/on         vs obs_cf200_e30/on          86    32       8      10       36  0.815
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 983 episodes, 1 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/obs_cf200_e20/on/observe_and_pickup/seed_4300099/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-s7.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 20:51:22 A40-v21-obs_cf200-s7: DONE  observe_and_pickup/on n=94  prog=0.00
```

## A40-v21-obs_cf200-s8 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-s8.log):
```
  obs_cf200_e20/on         vs obs_cf200_e30/on          89    32       8      10       39  0.815
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 988 episodes, 1 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/obs_cf200_e20/on/observe_and_pickup/seed_4300099/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-s8.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 20:56:22 A40-v21-obs_cf200-s8: DONE  observe_and_pickup/on n=99  prog=0.00
```

## A40-v21-obs_cf200-s9 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-s9.log):
```
  obs_cf200_e20/on         vs obs_cf200_e30/on          89    32       8      10       39  0.815
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 989 episodes, 1 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/obs_cf200_e20/on/observe_and_pickup/seed_4300099/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-s9.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 20:56:34 A40-v21-obs_cf200-s9: DONE  observe_and_pickup/on n=100  prog=0.00
```

## A40-V21-C25-verdict (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-V21-C25-verdict.log):
```

[queue5] 2026-11-28 20:56:39 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/v21_verdict.py c25
{"run": "card 25 obs_cf200 (same table, every target) against obs_s200", "sesoi": 0.15, "finished": {"obs_cf200_e30": 100, "obs_s200_e30": 100}, "main": {"scenes": 100, "new": 46, "ref": 15, "D": 0.31, "ci95": [0.19, 0.42], "only_new": 37, "only_ref": 6}, "verdict": "BREAKING THE SHORTCUT HELPS", "described": {"against_obs_ar_e30": {"scenes": 100, "new": 46, "ref": 13, "D": 0.33, "ci95": [0.23, 0.44], "only_new": 37, "only_ref": 4}, "success_vs_bars": "46 vs 13 (obs_ar e30), 20 (blind pick), 28 (pure-WAM best, self-reported)", "against_obs_s800_e10": {"scenes": 100, "new": 46, "ref": 49, "D": -0.03, "ci95": [-0.15, 0.08], "only_new": 16, "only_ref": 19}, "obs_cf200_e10": {"scenes": 100, "new": 30, "ref": 15, "D": 0.15, "ci95": [0.04, 0.26], "only_new": 25, "only_ref": 10}, "obs_cf200_e20": {"scenes": 89, "new": 40, "ref": 15, "D": 0.2809, "ci95": [0.1685, 0.3933], "only_new": 29, "only_ref": 4}}, "seed_extension_v21_5_5_6": "not due (|D| >= 0.30)"}
V21 C25: BREAKING THE SHORTCUT HELPS
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-V21-C25-verdict.log):
```

[pool] 2026-11-28 20:56:34 exec A40-V21-C25-verdict GPU None 
[pool] 2026-11-28 20:56:39 A40-V21-C25-verdict: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-V21-C25-verdict.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-V21-C25-verdict.md
[queue5] 2026-11-28 20:56:48 A40-V21-C25-verdict: PASS  rc=0
```

## A40-fetch-ranking_drop-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-ranking_drop-e30.log):
```
[fetch] 2026-11-28 15:50:57 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 15:55:58 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 16:00:58 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 16:05:59 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 16:10:59 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 16:16:00 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 16:21:00 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 16:26:01 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 16:31:02 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 16:36:02 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 16:41:03 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 16:46:03 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 16:51:04 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 16:56:04 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 17:01:05 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 17:06:06 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 17:11:06 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 17:16:07 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 17:21:07 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 17:26:08 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 17:31:08 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 17:36:09 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 17:41:09 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 17:46:10 waiting for exports/ranking_drop_e30 on the relay
[fetch] 2026-11-28 17:51:11 waiting for exports/ranking_drop_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-ranking_drop-e30.log):
```

[pool] 2026-11-27 11:26:44 exec A40-fetch-ranking_drop-e30 GPU None 
[pool] 2026-11-27 11:26:47 A40-fetch-ranking_drop-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-ranking_drop-e30.log
```

## A40-fetch-rearr_pw_s18-e30 (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_s18-e30.log):
```
[fetch] 2026-11-27 18:48:48 waiting for exports/rearr_pw_s18_e30 on the relay
[fetch] 2026-11-27 18:53:48 waiting for exports/rearr_pw_s18_e30 on the relay
[fetch] 2026-11-27 18:58:49 waiting for exports/rearr_pw_s18_e30 on the relay
[fetch] 2026-11-27 19:03:49 waiting for exports/rearr_pw_s18_e30 on the relay
[fetch] 2026-11-27 19:08:50 waiting for exports/rearr_pw_s18_e30 on the relay
[fetch] 2026-11-27 19:13:50 waiting for exports/rearr_pw_s18_e30 on the relay
[fetch] 2026-11-27 19:18:51 waiting for exports/rearr_pw_s18_e30 on the relay
[fetch] 2026-11-27 19:23:51 waiting for exports/rearr_pw_s18_e30 on the relay
[fetch] 2026-11-27 19:28:52 waiting for exports/rearr_pw_s18_e30 on the relay
[fetch] 2026-11-27 19:33:53 waiting for exports/rearr_pw_s18_e30 on the relay
[fetch] 2026-11-27 19:38:53 waiting for exports/rearr_pw_s18_e30 on the relay
[fetch] 2026-11-27 19:43:54 waiting for exports/rearr_pw_s18_e30 on the relay
[fetch] 2026-11-27 19:48:54 waiting for exports/rearr_pw_s18_e30 on the relay
[fetch] 2026-11-27 19:53:55 waiting for exports/rearr_pw_s18_e30 on the relay
[fetch] 2026-11-27 19:58:55 waiting for exports/rearr_pw_s18_e30 on the relay
[fetch] disk before: /dev/sdb         19T   11T  6.7T  62% /workspace/FastWAM-memory2
[fetch] 2026-11-27 20:03:56 fetching rearr_pw_s18_e30 (attempt 1)
[relay] get hhyfred/memwam-fullft/exports/rearr_pw_s18_e30/export_e30.pt -> /workspace/FastWAM-memory2/outputs/fullft/exports/rearr_pw_s18_e30/export_e30.pt (12042506501 bytes)
[relay] get hhyfred/memwam-fullft/exports/rearr_pw_s18_e30/export_e30.pt.sha256 -> /workspace/FastWAM-memory2/outputs/fullft/exports/rearr_pw_s18_e30/export_e30.pt.sha256 (80 bytes)
export_e30.pt: OK
total 11760280
drwxr-xr-x  2 root root        4096 Nov 27 20:12 .
drwxr-xr-x 97 root root        4096 Nov 27 20:03 ..
-rw-r--r--  1 root root 12042506501 Nov 27 20:12 export_e30.pt
-rw-r--r--  1 root root          80 Nov 27 20:12 export_e30.pt.sha256
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearr_pw_s18-e30.log):
```

[pool] 2026-11-27 01:35:52 exec A40-fetch-rearr_pw_s18-e30 GPU None 
[pool] 2026-11-27 01:35:56 A40-fetch-rearr_pw_s18-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_s18-e30.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-rearr_pw_s18-e30.md
[queue5] 2026-11-28 04:12:50 A40-fetch-rearr_pw_s18-e30: PASS  rc=0
```

## A40-v21-rearr_pw_s18-smoke (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-rearr_pw_s18-smoke.log):
```
[decide] 2026-11-27 20:25:31 rearr_pw_s18_e30_smoke/on rearrange_blocks seed=4300000 frame=320/700 hist=3 policy=0.6s elapsed=119s
[decide] 2026-11-27 20:25:41 rearr_pw_s18_e30_smoke/on rearrange_blocks seed=4300000 frame=352/700 hist=3 policy=0.6s elapsed=129s
[decide] 2026-11-27 20:25:51 rearr_pw_s18_e30_smoke/on rearrange_blocks seed=4300000 frame=384/700 hist=3 policy=0.6s elapsed=139s
[decide] 2026-11-27 20:26:01 rearr_pw_s18_e30_smoke/on rearrange_blocks seed=4300000 frame=416/700 hist=3 policy=0.6s elapsed=149s
[decide] 2026-11-27 20:26:11 rearr_pw_s18_e30_smoke/on rearrange_blocks seed=4300000 frame=448/700 hist=3 policy=0.6s elapsed=159s
[decide] 2026-11-27 20:26:26 rearr_pw_s18_e30_smoke/on rearrange_blocks seed=4300000 frame=480/700 hist=3 policy=0.6s elapsed=175s
[decide] 2026-11-27 20:26:44 rearr_pw_s18_e30_smoke/on rearrange_blocks seed=4300000 frame=512/700 hist=3 policy=0.6s elapsed=192s
[decide] 2026-11-27 20:26:54 rearr_pw_s18_e30_smoke/on rearrange_blocks seed=4300000 frame=544/700 hist=3 policy=0.6s elapsed=203s
[decide] 2026-11-27 20:27:04 rearr_pw_s18_e30_smoke/on rearrange_blocks seed=4300000 frame=576/700 hist=3 policy=0.6s elapsed=212s
[decide] 2026-11-27 20:27:14 rearr_pw_s18_e30_smoke/on rearrange_blocks seed=4300000 frame=608/700 hist=3 policy=0.6s elapsed=222s
[decide] 2026-11-27 20:27:24 rearr_pw_s18_e30_smoke/on rearrange_blocks seed=4300000 frame=640/700 hist=3 policy=0.6s elapsed=232s
[decide] 2026-11-27 20:27:35 rearr_pw_s18_e30_smoke/on rearrange_blocks seed=4300000 frame=672/700 hist=3 policy=0.6s elapsed=243s
[closed-loop] 2026-11-27 20:27:51 done  rearr_pw_s18_e30_smoke/on rearrange_blocks seed=4300000 success=False targets=700/700 reward=0.0 lift=0.12096530199050903  299s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
rearr_ar_pw_e30_smoke/onrearrange_blocks   1     1.00  [0.21,1.00]      1.00    1.00      392        -        -        -    0.6
rearr_arprop_pw_e30_smoke/onrearrange_blocks   1     0.00  [0.00,0.79]      1.00    0.00      700        -        -        -    0.6
rearr_pw_s18_e30_smoke/onrearrange_blocks   1     0.00  [0.00,0.79]      1.00    0.00      700        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearr_ar_pw_e30_smoke/on vs rearr_arprop_pw_e30_smoke/on   1     0       1       0        0  1.000
  rearr_ar_pw_e30_smoke/on vs rearr_pw_s18_e30_smoke/on   1     0       1       0        0  1.000
  rearr_arprop_pw_e30_smoke/on vs rearr_pw_s18_e30_smoke/on   1     0       0       0        1  1.000

[summary] 3 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21smoke/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-rearr_pw_s18-smoke.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 04:27:56 A40-v21-rearr_pw_s18-smoke: PASS  rearrange_blocks/on n=1  prog=0.00
```

## A40-v21-rearr_pw_s18-s0 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-rearr_pw_s18-s0.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on       36    10       2      15        9  0.002
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on       36    11       0      14       11  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on       36    14       3      11        8  0.057
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on       36     9       3      16        8  0.004
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on       36    18       5       7        6  0.774
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on       36    11       6      14        5  0.115

[summary] 636 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-rearr_pw_s18-s0.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 05:15:12 A40-v21-rearr_pw_s18-s0: DONE  rearrange_blocks/on n=36  prog=0.00
```

## A40-v21-rearr_pw_s18-s1 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-rearr_pw_s18-s1.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on       30     9       2      12        7  0.013
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on       30     8       0      13        9  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on       30    10       3      11        6  0.057
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on       30     7       3      14        6  0.013
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on       30    15       4       6        5  0.754
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on       30     9       5      12        4  0.143

[summary] 630 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-rearr_pw_s18-s1.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 05:07:49 A40-v21-rearr_pw_s18-s1: DONE  rearrange_blocks/on n=30  prog=0.00
```

## A40-v21-rearr_pw_s18-s2 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-rearr_pw_s18-s2.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on       43    11       4      17       11  0.007
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on       43    12       2      16       13  0.001
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on       43    15       5      13       10  0.096
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on       43     9       4      19       11  0.003
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on       43    21       8       7        7  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on       43    12       9      16        6  0.230

[summary] 643 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-rearr_pw_s18-s2.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 05:21:51 A40-v21-rearr_pw_s18-s2: DONE  rearrange_blocks/on n=43  prog=0.00
```

## A40-v21-rearr_pw_s18-s3 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-rearr_pw_s18-s3.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on       42    11       3      17       11  0.003
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on       42    12       1      16       13  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on       42    15       5      13        9  0.096
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on       42     9       3      19       11  0.001
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on       42    21       7       7        7  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on       42    12       8      16        6  0.152

[summary] 642 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-rearr_pw_s18-s3.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 05:21:27 A40-v21-rearr_pw_s18-s3: DONE  rearrange_blocks/on n=42  prog=0.00
```

## A40-v21-rearr_pw_s18-s4 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-rearr_pw_s18-s4.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on       88    20       9      36       23  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on       88    22       8      34       24  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on       88    35      14      21       18  0.311
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on       88    14       4      42       28  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on       88    40      14      16       18  0.856
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on       88    22      17      34       15  0.024

[summary] 698 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-rearr_pw_s18-s4.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 05:52:29 A40-v21-rearr_pw_s18-s4: DONE  rearrange_blocks/on n=88  prog=0.00
```

## A40-v21-rearr_pw_s18-s5 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-rearr_pw_s18-s5.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on       86    19       9      35       23  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on       86    21       8      33       24  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on       86    34      14      20       18  0.392
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on       86    13       4      41       28  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on       86    39      14      15       18  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on       86    21      17      33       15  0.033

[summary] 696 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-rearr_pw_s18-s5.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 05:51:53 A40-v21-rearr_pw_s18-s5: DONE  rearrange_blocks/on n=86  prog=0.00
```

## A40-v21-rearr_pw_s18-s6 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-rearr_pw_s18-s6.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on       94    21      10      38       25  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on       94    24       8      35       27  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on       94    37      16      22       19  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on       94    14       4      45       31  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on       94    42      16      17       19  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on       94    24      19      35       16  0.040

[summary] 708 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-rearr_pw_s18-s6.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 05:58:51 A40-v21-rearr_pw_s18-s6: DONE  rearrange_blocks/on n=94  prog=0.00
```

## A40-v21-rearr_pw_s18-s7 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-rearr_pw_s18-s7.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 728 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-rearr_pw_s18-s7.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 06:08:00 A40-v21-rearr_pw_s18-s7: DONE  rearrange_blocks/on n=100  prog=0.00
```

## A40-v21-rearr_pw_s18-s8 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-rearr_pw_s18-s8.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on       98    21      10      39       28  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on       98    25       9      35       29  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on       98    38      16      22       22  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on       98    14       4      46       34  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on       98    43      17      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on       98    24      20      36       18  0.044

[summary] 718 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-rearr_pw_s18-s8.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 06:03:47 A40-v21-rearr_pw_s18-s8: DONE  rearrange_blocks/on n=98  prog=0.00
```

## A40-v21-rearr_pw_s18-s9 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-rearr_pw_s18-s9.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on       99    21      10      40       28  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on       99    25       9      36       29  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on       99    39      16      22       22  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on       99    14       4      47       34  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on       99    44      17      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on       99    24      20      37       18  0.033

[summary] 724 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-rearr_pw_s18-s9.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 06:06:46 A40-v21-rearr_pw_s18-s9: DONE  rearrange_blocks/on n=99  prog=0.00
```

## A40-V21-C22-report (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-V21-C22-report.log):
```

[queue5] 2026-11-28 06:08:34 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/v21_verdict.py c22
{"run": "card 22 rearr_pw_s18 (seed 18), described only", "finished": {"rearr_pw_s18_e30": 100, "rearr_pw_e30": 100}, "success_1_100": {"seed18": 61, "seed17": 93, "mean_of_two_seeds": 77.0}, "paired_counts": {"scenes": 100, "new": 61, "ref": 93, "D": -0.32, "ci95": [-0.43, -0.21], "only_new": 4, "only_ref": 36}, "classes": {"rearr_pw_s18_e30": {"never pressed: block1 placed on the empty mat": 17, "success": 61, "pressed twice or more (after step 1 was complete)": 22}, "rearr_pw_e30": {"success": 93, "never pressed: block1 placed on the empty mat": 4, "stage 1, then moved block1 again (which-block error)": 2, "pressed too early (block1 not on the empty mat at the press)": 1}}, "verdict": "DESCRIBED"}
V21 C22: DESCRIBED
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-V21-C22-report.log):
```

[pool] 2026-11-28 06:08:30 exec A40-V21-C22-report GPU None 
[pool] 2026-11-28 06:08:34 A40-V21-C22-report: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-V21-C22-report.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-V21-C22-report.md
[queue5] 2026-11-28 06:10:05 A40-V21-C22-report: PASS  rc=0
```

## A40-fetch-swapT_joint3-e30 (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_joint3-e30.log):
```
[fetch] 2026-11-28 09:06:13 waiting for exports/swapT_joint3_e30 on the relay
[fetch] 2026-11-28 09:11:14 waiting for exports/swapT_joint3_e30 on the relay
[fetch] 2026-11-28 09:16:14 waiting for exports/swapT_joint3_e30 on the relay
[fetch] 2026-11-28 09:21:15 waiting for exports/swapT_joint3_e30 on the relay
[fetch] 2026-11-28 09:26:16 waiting for exports/swapT_joint3_e30 on the relay
[fetch] 2026-11-28 09:31:16 waiting for exports/swapT_joint3_e30 on the relay
[fetch] 2026-11-28 09:36:17 waiting for exports/swapT_joint3_e30 on the relay
[fetch] 2026-11-28 09:41:17 waiting for exports/swapT_joint3_e30 on the relay
[fetch] 2026-11-28 09:46:18 waiting for exports/swapT_joint3_e30 on the relay
[fetch] 2026-11-28 09:51:18 waiting for exports/swapT_joint3_e30 on the relay
[fetch] 2026-11-28 09:56:19 waiting for exports/swapT_joint3_e30 on the relay
[fetch] 2026-11-28 10:01:20 waiting for exports/swapT_joint3_e30 on the relay
[fetch] 2026-11-28 10:06:20 waiting for exports/swapT_joint3_e30 on the relay
[fetch] 2026-11-28 10:11:21 waiting for exports/swapT_joint3_e30 on the relay
[fetch] 2026-11-28 10:16:21 waiting for exports/swapT_joint3_e30 on the relay
[fetch] disk before: /dev/sdb         19T   11T  6.6T  62% /workspace/FastWAM-memory2
[fetch] 2026-11-28 10:21:22 fetching swapT_joint3_e30 (attempt 1)
[relay] get hhyfred/memwam-fullft/exports/swapT_joint3_e30/export_e30.pt -> /workspace/FastWAM-memory2/outputs/fullft/exports/swapT_joint3_e30/export_e30.pt (12042506693 bytes)
[relay] get hhyfred/memwam-fullft/exports/swapT_joint3_e30/export_e30.pt.sha256 -> /workspace/FastWAM-memory2/outputs/fullft/exports/swapT_joint3_e30/export_e30.pt.sha256 (80 bytes)
export_e30.pt: OK
total 11760280
drwxr-xr-x   2 root root        4096 Nov 28 10:30 .
drwxr-xr-x 105 root root        4096 Nov 28 10:21 ..
-rw-r--r--   1 root root 12042506693 Nov 28 10:30 export_e30.pt
-rw-r--r--   1 root root          80 Nov 28 10:30 export_e30.pt.sha256
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-swapT_joint3-e30.log):
```

[pool] 2026-11-26 18:05:47 exec A40-fetch-swapT_joint3-e30 GPU None 
[pool] 2026-11-26 18:05:50 A40-fetch-swapT_joint3-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_joint3-e30.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-swapT_joint3-e30.md
[queue5] 2026-11-28 18:30:21 A40-fetch-swapT_joint3-e30: PASS  rc=0
```

## A40-v20joint3-smoke (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-smoke.log):
```
[decide] 2026-11-28 10:53:05 swapT_joint3_e30_smoke/on swap_T seed=4300000 frame=288/600 hist=3 policy=0.6s elapsed=110s
[closed-loop] 2026-11-28 10:53:08 done  swapT_joint3_e30_smoke/on swap_T seed=4300000 success=True targets=293/600 reward=1.0 lift=None  151s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_v3c_e30_smoke/on    swap_blocks        1     1.00  [0.21,1.00]      1.00    1.00      589        -        -        -    0.6
obs_match_e30_smoke/on  observe_and_pickup   1     0.00  [0.00,0.79]         -    0.00      250        -        -        -    0.7
obs_s200_e30_smoke/on   observe_and_pickup   1     0.00  [0.00,0.79]         -    0.00      250        -        -        -    0.6
press_told_e30_smoke/on press_button       1     0.00  [0.00,0.79]         -    0.00     1500        -        -        -    0.6
ranking_v3a_e30_smoke/onblocks_ranking_try   1     1.00  [0.21,1.00]      1.00    0.00     1859        -        -        -    0.6
rearr_pw_e30_smoke/on   rearrange_blocks   1     1.00  [0.21,1.00]      1.00    1.00      384        -        -        -    0.6
swapT_arprop_h2_e30_smoke/onswap_T             1     0.00  [0.00,0.79]         -    0.00      600        -        -        -    0.6
swapT_joint3_e30_smoke/onswap_T             1     1.00  [0.21,1.00]         -    1.00      293        -        -        -    0.6
swapT_long_e60_smoke/on swap_T             1     0.00  [0.00,0.79]         -    0.00      600        -        -        -    0.6
swapT_long_h100_e60_smoke/onswap_T             1     0.00  [0.00,0.79]         -    0.00      600        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  obs_match_e30_smoke/on   vs obs_s200_e30_smoke/on      1     0       0       0        1  1.000
  swapT_arprop_h2_e30_smoke/on vs swapT_joint3_e30_smoke/on   1     0       0       1        0  1.000
  swapT_arprop_h2_e30_smoke/on vs swapT_long_e60_smoke/on    1     0       0       0        1  1.000
  swapT_arprop_h2_e30_smoke/on vs swapT_long_h100_e60_smoke/on   1     0       0       0        1  1.000
  swapT_joint3_e30_smoke/on vs swapT_long_e60_smoke/on    1     0       1       0        0  1.000
  swapT_joint3_e30_smoke/on vs swapT_long_h100_e60_smoke/on   1     0       1       0        0  1.000
  swapT_long_e60_smoke/on  vs swapT_long_h100_e60_smoke/on   1     0       0       0        1  1.000

[summary] 10 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20smoke/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-smoke.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 18:53:15 A40-v20joint3-smoke: PASS  swap_T/on n=1  prog=0.00
```

## A40-v20joint3-s0 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-s0.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on       56    19       2      30        5  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on         56    22      27       2        5  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on         56    19      30       2        5  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on    56    26      23       3        4  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on    56    23      26       2        5  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2356 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-s0.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 19:28:56 A40-v20joint3-s0: DONE  swap_T/on n=56  prog=0.00
```

## A40-v20joint3-s1 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-s1.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on       57    19       2      31        5  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on         57    22      28       2        5  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on         57    19      31       2        5  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on    57    26      24       3        4  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on    57    23      27       2        5  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2357 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-s1.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 19:29:20 A40-v20joint3-s1: DONE  swap_T/on n=57  prog=0.00
```

## A40-v20joint3-s2 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-s2.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on       54    18       2      30        4  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on         54    21      27       2        4  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on         54    18      30       2        4  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on    54    25      23       3        3  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on    54    22      26       2        4  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2354 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-s2.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 19:28:14 A40-v20joint3-s2: DONE  swap_T/on n=55  prog=0.00
```

## A40-v20joint3-s3 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-s3.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on       64    22       2      34        6  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on         64    24      32       2        6  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on         64    21      35       2        6  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on    64    29      27       3        5  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on    64    25      31       2        6  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2364 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-s3.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 19:33:50 A40-v20joint3-s3: DONE  swap_T/on n=64  prog=0.00
```

## A40-v20joint3-s4 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-s4.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on       69    25       2      36        6  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on         69    26      35       2        6  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on         69    25      36       2        6  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on    69    32      29       3        5  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on    69    27      34       2        6  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2369 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-s4.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 19:35:57 A40-v20joint3-s4: DONE  swap_T/on n=69  prog=0.00
```

## A40-v20joint3-s5 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-s5.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on       65    23       2      34        6  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on         65    24      33       2        6  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on         65    22      35       2        6  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on    65    30      27       3        5  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on    65    25      32       2        6  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2365 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-s5.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 19:33:52 A40-v20joint3-s5: DONE  swap_T/on n=65  prog=0.00
```

## A40-v20joint3-s6 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-s6.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on       84    30       3      43        8  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on         84    28      45       2        9  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on         84    28      45       2        9  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on    84    37      36       5        6  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on    84    31      42       2        9  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2389 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-s6.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 19:48:14 A40-v20joint3-s6: DONE  swap_T/on n=84  prog=0.00
```

## A40-v20joint3-s7 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-s7.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on       98    35       4      49       10  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on         98    35      49       3       11  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on         98    33      51       3       11  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on    98    43      41       6        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on    98    36      48       2       12  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2413 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-s7.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 20:02:40 A40-v20joint3-s7: DONE  swap_T/on n=98  prog=0.00
```

## A40-v20joint3-s8 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-s8.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on      100    35       4      50       11  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on        100    35      50       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on        100    33      52       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on   100    43      42       7        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on   100    36      49       2       13  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2416 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-s8.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 20:05:27 A40-v20joint3-s8: DONE  swap_T/on n=100  prog=0.00
```

## A40-v20joint3-s9 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-s9.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on       99    35       4      50       10  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on         99    35      50       3       11  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on         99    33      52       3       11  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on    99    43      42       6        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on    99    36      49       2       12  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2414 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-s9.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 20:04:43 A40-v20joint3-s9: DONE  swap_T/on n=99  prog=0.00
```

## A40-v20joint3-swap-s0 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-swap-s0.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on      100    35       4      50       11  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on        100    35      50       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on        100    33      52       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on   100    43      42       7        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on   100    36      49       2       13  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2428 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-swap-s0.log):
```

[pool] 2026-11-28 19:34:57 exec A40-v20joint3-swap-s0 GPU 4 
[pool] 2026-11-28 19:35:02 A40-v20joint3-swap-s0: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-swap-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-swap-s0.md
[queue5] 2026-11-28 20:24:50 A40-v20joint3-swap-s0: DONE  swap_blocks/on n=28 lifted=28 s1=28 s2=28 s3=28 pressed=28 success=28 prog=1.00
```

## A40-v20joint3-swap-s1 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-swap-s1.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on      100    35       4      50       11  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on        100    35      50       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on        100    33      52       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on   100    43      42       7        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on   100    36      49       2       13  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2429 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-swap-s1.log):
```

[pool] 2026-11-28 19:35:33 exec A40-v20joint3-swap-s1 GPU 1 
[pool] 2026-11-28 19:35:37 A40-v20joint3-swap-s1: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-swap-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-swap-s1.md
[queue5] 2026-11-28 20:25:43 A40-v20joint3-swap-s1: DONE  swap_blocks/on n=29 lifted=29 s1=29 s2=29 s3=29 pressed=29 success=29 prog=1.00
```

## A40-v20joint3-swap-s2 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-swap-s2.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on      100    35       4      50       11  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on        100    35      50       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on        100    33      52       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on   100    43      42       7        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on   100    36      49       2       13  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2430 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-swap-s2.log):
```

[pool] 2026-11-28 19:37:19 exec A40-v20joint3-swap-s2 GPU 0 
[pool] 2026-11-28 19:37:24 A40-v20joint3-swap-s2: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-swap-s2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-swap-s2.md
[queue5] 2026-11-28 20:27:09 A40-v20joint3-swap-s2: DONE  swap_blocks/on n=30 lifted=30 s1=30 s2=30 s3=30 pressed=30 success=30 prog=1.00
```

## A40-v20joint3-swap-s3 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-swap-s3.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on      100    35       4      50       11  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on        100    35      50       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on        100    33      52       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on   100    43      42       7        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on   100    36      49       2       13  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2472 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-swap-s3.log):
```

[pool] 2026-11-28 20:32:05 exec A40-v20joint3-swap-s3 GPU 5 
[pool] 2026-11-28 20:32:10 A40-v20joint3-swap-s3: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-swap-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-swap-s3.md
[queue5] 2026-11-28 21:22:40 A40-v20joint3-swap-s3: DONE  swap_blocks/on n=72 lifted=72 s1=72 s2=72 s3=72 pressed=72 success=72 prog=1.00
```

## A40-v20joint3-swap-s4 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-swap-s4.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on      100    35       4      50       11  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on        100    35      50       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on        100    33      52       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on   100    43      42       7        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on   100    36      49       2       13  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2490 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-swap-s4.log):
```

[pool] 2026-11-28 20:45:11 exec A40-v20joint3-swap-s4 GPU 6 
[pool] 2026-11-28 20:45:16 A40-v20joint3-swap-s4: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-swap-s4.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-swap-s4.md
[queue5] 2026-11-28 21:33:53 A40-v20joint3-swap-s4: DONE  swap_blocks/on n=88 lifted=88 s1=88 s2=88 s3=88 pressed=88 success=88 prog=1.00
```

## A40-v20joint3-swap-s5 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-swap-s5.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on      100    35       4      50       11  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on        100    35      50       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on        100    33      52       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on   100    43      42       7        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on   100    36      49       2       13  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2498 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-swap-s5.log):
```

[pool] 2026-11-28 20:51:12 exec A40-v20joint3-swap-s5 GPU 1 
[pool] 2026-11-28 20:51:17 A40-v20joint3-swap-s5: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-swap-s5.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-swap-s5.md
[queue5] 2026-11-28 21:39:01 A40-v20joint3-swap-s5: DONE  swap_blocks/on n=94 lifted=94 s1=94 s2=94 s3=94 pressed=94 success=94 prog=1.00
```

## A40-v20joint3-swap-s6 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-swap-s6.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on      100    35       4      50       11  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on        100    35      50       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on        100    33      52       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on   100    43      42       7        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on   100    36      49       2       13  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2501 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-swap-s6.log):
```

[pool] 2026-11-28 20:52:58 exec A40-v20joint3-swap-s6 GPU 0 
[pool] 2026-11-28 20:53:03 A40-v20joint3-swap-s6: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-swap-s6.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-swap-s6.md
[queue5] 2026-11-28 21:40:52 A40-v20joint3-swap-s6: DONE  swap_blocks/on n=95 lifted=95 s1=95 s2=95 s3=95 pressed=95 success=95 prog=1.00
```

## A40-v20joint3-swap-s7 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-swap-s7.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on      100    35       4      50       11  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on        100    35      50       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on        100    33      52       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on   100    43      42       7        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on   100    36      49       2       13  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2504 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-swap-s7.log):
```

[pool] 2026-11-28 20:52:58 exec A40-v20joint3-swap-s7 GPU 4 
[pool] 2026-11-28 20:53:03 A40-v20joint3-swap-s7: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-swap-s7.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-swap-s7.md
[queue5] 2026-11-28 21:42:37 A40-v20joint3-swap-s7: DONE  swap_blocks/on n=98 lifted=98 s1=98 s2=98 s3=98 pressed=98 success=98 prog=1.00
```

## A40-v20joint3-swap-s8 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-swap-s8.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on      100    35       4      50       11  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on        100    35      50       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on        100    33      52       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on   100    43      42       7        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on   100    36      49       2       13  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2510 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-swap-s8.log):
```

[pool] 2026-11-28 20:57:45 exec A40-v20joint3-swap-s8 GPU 3 
[pool] 2026-11-28 20:57:50 A40-v20joint3-swap-s8: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-swap-s8.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-swap-s8.md
[queue5] 2026-11-28 21:46:45 A40-v20joint3-swap-s8: DONE  swap_blocks/on n=100 lifted=100 s1=100 s2=100 s3=100 pressed=100 success=100 prog=1.00
```

## A40-v20joint3-swap-s9 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-swap-s9.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on      100    35       4      50       11  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on        100    35      50       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on        100    33      52       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on   100    43      42       7        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on   100    36      49       2       13  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2507 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-swap-s9.log):
```

[pool] 2026-11-28 20:57:45 exec A40-v20joint3-swap-s9 GPU 7 
[pool] 2026-11-28 20:57:50 A40-v20joint3-swap-s9: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-swap-s9.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-swap-s9.md
[queue5] 2026-11-28 21:45:15 A40-v20joint3-swap-s9: DONE  swap_blocks/on n=99 lifted=99 s1=99 s2=99 s3=99 pressed=99 success=99 prog=1.00
```

## A40-v20joint3-put-s0 (done, attempt 2, GPU 6)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 5,
  "time": "2026-11-28 21:49:13",
  "why": "2 episodes ended with ERROR.json (re-run retries only those)"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-put-s0.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on      100    35       4      50       11  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on        100    35      50       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on        100    33      52       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on   100    43      42       7        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on   100    36      49       2       13  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2539 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-put-s0.log):
```
[pool] 2026-11-28 21:23:51 exec A40-v20joint3-put-s0 GPU 5 
[pool] 2026-11-28 21:23:56 A40-v20joint3-put-s0: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-put-s0.log
[pool] 2026-11-28 21:49:13 A40-v20joint3-put-s0: attempt 1 failed (2 episodes ended with ERROR.json (re-run retries only those)); retry after 21:59 on any empty GPU

[pool] 2026-11-28 22:10:47 exec A40-v20joint3-put-s0 GPU 6 
[pool] 2026-11-28 22:10:53 A40-v20joint3-put-s0: start (attempt 2/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-put-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-put-s0.md
[queue5] 2026-11-28 22:18:53 A40-v20joint3-put-s0: DONE  put_back_block/on n=39 lifted=39 centre=39 pressed=39 stage1=39 regrasp=39 returned=39 success=39 prog=1.00
```

## A40-v20joint3-put-s1 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-put-s1.log):
```
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on      100    35       4      50       11  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on        100    35      50       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on        100    33      52       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on   100    43      42       7        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on   100    36      49       2       13  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2526 episodes, 2 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/swapT_joint3_e30/on/put_back_block/seed_4300080/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/swapT_joint3_e30/on/put_back_block/seed_4300090/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-put-s1.log):
```

[pool] 2026-11-28 21:34:30 exec A40-v20joint3-put-s1 GPU 6 
[pool] 2026-11-28 21:34:35 A40-v20joint3-put-s1: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-put-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-put-s1.md
[queue5] 2026-11-28 22:07:03 A40-v20joint3-put-s1: DONE  put_back_block/on n=26 lifted=26 centre=26 pressed=26 stage1=26 regrasp=26 returned=26 success=26 prog=1.00; errors=2
```

## A40-v20joint3-put-s2 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-put-s2.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on      100    35       4      50       11  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on        100    35      50       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on        100    33      52       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on   100    43      42       7        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on   100    36      49       2       13  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2554 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-put-s2.log):
```

[pool] 2026-11-28 21:50:31 exec A40-v20joint3-put-s2 GPU 0 
[pool] 2026-11-28 21:50:36 A40-v20joint3-put-s2: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-put-s2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-put-s2.md
[queue5] 2026-11-28 22:25:46 A40-v20joint3-put-s2: DONE  put_back_block/on n=54 lifted=54 centre=54 pressed=54 stage1=54 regrasp=54 returned=54 success=54 prog=1.00
```

## A40-v20joint3-put-s3 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-put-s3.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on      100    35       4      50       11  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on        100    35      50       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on        100    33      52       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on   100    43      42       7        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on   100    36      49       2       13  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2551 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-put-s3.log):
```

[pool] 2026-11-28 21:50:31 exec A40-v20joint3-put-s3 GPU 7 
[pool] 2026-11-28 21:50:36 A40-v20joint3-put-s3: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-put-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-put-s3.md
[queue5] 2026-11-28 22:24:59 A40-v20joint3-put-s3: DONE  put_back_block/on n=51 lifted=51 centre=51 pressed=51 stage1=51 regrasp=51 returned=51 success=51 prog=1.00
```

## A40-v20joint3-put-s4 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-put-s4.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on      100    35       4      50       11  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on        100    35      50       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on        100    33      52       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on   100    43      42       7        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on   100    36      49       2       13  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2589 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-put-s4.log):
```

[pool] 2026-11-28 22:11:22 exec A40-v20joint3-put-s4 GPU 5 
[pool] 2026-11-28 22:11:28 A40-v20joint3-put-s4: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-put-s4.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-put-s4.md
[queue5] 2026-11-28 22:44:14 A40-v20joint3-put-s4: DONE  put_back_block/on n=89 lifted=89 centre=89 pressed=89 stage1=89 regrasp=89 returned=89 success=89 prog=1.00
```

## A40-v20joint3-put-s5 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-put-s5.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on      100    35       4      50       11  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on        100    35      50       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on        100    33      52       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on   100    43      42       7        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on   100    36      49       2       13  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2590 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-put-s5.log):
```

[pool] 2026-11-28 22:11:58 exec A40-v20joint3-put-s5 GPU 1 
[pool] 2026-11-28 22:12:03 A40-v20joint3-put-s5: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-put-s5.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-put-s5.md
[queue5] 2026-11-28 22:44:32 A40-v20joint3-put-s5: DONE  put_back_block/on n=90 lifted=90 centre=90 pressed=90 stage1=90 regrasp=90 returned=90 success=90 prog=1.00
```

## A40-v20joint3-put-s6 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-put-s6.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on      100    35       4      50       11  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on        100    35      50       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on        100    33      52       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on   100    43      42       7        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on   100    36      49       2       13  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2591 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-put-s6.log):
```

[pool] 2026-11-28 22:11:58 exec A40-v20joint3-put-s6 GPU 3 
[pool] 2026-11-28 22:12:03 A40-v20joint3-put-s6: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-put-s6.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-put-s6.md
[queue5] 2026-11-28 22:44:49 A40-v20joint3-put-s6: DONE  put_back_block/on n=91 lifted=91 centre=91 pressed=91 stage1=91 regrasp=91 returned=91 success=91 prog=1.00
```

## A40-v20joint3-put-s7 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-put-s7.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on      100    35       4      50       11  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on        100    35      50       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on        100    33      52       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on   100    43      42       7        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on   100    36      49       2       13  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2592 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-put-s7.log):
```

[pool] 2026-11-28 22:12:34 exec A40-v20joint3-put-s7 GPU 4 
[pool] 2026-11-28 22:12:39 A40-v20joint3-put-s7: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-put-s7.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-put-s7.md
[queue5] 2026-11-28 22:46:01 A40-v20joint3-put-s7: DONE  put_back_block/on n=92 lifted=92 centre=92 pressed=92 stage1=92 regrasp=92 returned=92 success=92 prog=1.00
```

## A40-v20joint3-put-s8 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-put-s8.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on      100    35       4      50       11  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on        100    35      50       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on        100    33      52       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on   100    43      42       7        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on   100    36      49       2       13  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2597 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-put-s8.log):
```

[pool] 2026-11-28 22:20:20 exec A40-v20joint3-put-s8 GPU 6 
[pool] 2026-11-28 22:20:25 A40-v20joint3-put-s8: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-put-s8.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-put-s8.md
[queue5] 2026-11-28 22:52:05 A40-v20joint3-put-s8: DONE  put_back_block/on n=97 lifted=97 centre=97 pressed=97 stage1=97 regrasp=97 returned=97 success=97 prog=1.00
```

## A40-v20joint3-put-s9 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-put-s9.log):
```
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_joint3_e30/on      100    35       4      50       11  0.000
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_joint3_e30/on      vs swapT_long_e45/on        100    35      50       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_e60/on        100    33      52       3       12  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e45/on   100    43      42       7        8  0.000
  swapT_joint3_e30/on      vs swapT_long_h100_e60/on   100    36      49       2       13  0.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2600 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v20joint3-put-s9.log):
```

[pool] 2026-11-28 22:26:18 exec A40-v20joint3-put-s9 GPU 7 
[pool] 2026-11-28 22:26:23 A40-v20joint3-put-s9: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v20joint3-put-s9.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-put-s9.md
[queue5] 2026-11-28 22:57:47 A40-v20joint3-put-s9: DONE  put_back_block/on n=100 lifted=100 centre=100 pressed=100 stage1=100 regrasp=100 returned=100 success=100 prog=1.00
```

## A40-joint3-verdict (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-joint3-verdict.log):
```

[queue5] 2026-11-28 22:57:46 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/v20_verdict.py joint3
{"run": "card 9b swap_T trained together with put / swap (swapT_joint3)", "sesoi": 0.15, "finished": {"swapT_joint3_e30": 100, "swapT_arprop_h2_e30": 100}, "main": {"scenes": 100, "new": 85, "ref": 39, "D": 0.46, "ci95": [0.34, 0.57], "only_new": 50, "only_ref": 4}, "verdict": "swap_T: CO-TRAINING HELPS; swap_blocks: NO HARM; put_back_block: NO HARM", "non_inferiority_swap_blocks": {"finished": {"swapT_joint3_e30": 100, "ar2_prop_e30": 100}, "main": {"scenes": 100, "new": 100, "ref": 100, "D": 0.0, "ci95": [0.0, 0.0], "only_new": 0, "only_ref": 0}, "verdict": "NO HARM"}, "non_inferiority_put_back_block": {"finished": {"swapT_joint3_e30": 100, "ar2_prop_e30": 100}, "main": {"scenes": 100, "new": 100, "ref": 100, "D": 0.0, "ci95": [0.0, 0.0], "only_new": 0, "only_ref": 0}, "verdict": "NO HARM"}}
V20 JOINT3: swap_T: CO-TRAINING HELPS; swap_blocks: NO HARM; put_back_block: NO HARM
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-joint3-verdict.log):
```

[pool] 2026-11-28 22:57:41 exec A40-joint3-verdict GPU None 
[pool] 2026-11-28 22:57:46 A40-joint3-verdict: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-joint3-verdict.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-joint3-verdict.md
[queue5] 2026-11-28 22:57:54 A40-joint3-verdict: PASS  rc=0
```

## A40-fetch-rearr_pw_long_s18-e60 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_long_s18-e60.log):
```
[fetch] 2026-11-28 15:49:06 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 15:54:07 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 15:59:07 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 16:04:08 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 16:09:08 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 16:14:09 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 16:19:09 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 16:24:10 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 16:29:10 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 16:34:11 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 16:39:11 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 16:44:12 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 16:49:13 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 16:54:13 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 16:59:14 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 17:04:14 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 17:09:15 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 17:14:15 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 17:19:16 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 17:24:16 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 17:29:17 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 17:34:18 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 17:39:18 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 17:44:19 waiting for exports/rearr_pw_long_s18_e60 on the relay
[fetch] 2026-11-28 17:49:19 waiting for exports/rearr_pw_long_s18_e60 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearr_pw_long_s18-e60.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-rearr_pw_long_s18-e60 GPU None 
[pool] 2026-11-28 17:08:21 A40-fetch-rearr_pw_long_s18-e60: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_long_s18-e60.log
```

## A40-fetch-rearr_pw_long-e60 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_long-e60.log):
```
[fetch] 2026-11-28 15:49:06 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 15:54:07 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 15:59:08 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 16:04:08 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 16:09:09 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 16:14:09 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 16:19:10 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 16:24:10 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 16:29:11 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 16:34:11 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 16:39:12 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 16:44:13 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 16:49:13 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 16:54:14 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 16:59:14 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 17:04:15 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 17:09:15 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 17:14:16 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 17:19:17 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 17:24:17 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 17:29:18 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 17:34:18 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 17:39:19 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 17:44:19 waiting for exports/rearr_pw_long_e60 on the relay
[fetch] 2026-11-28 17:49:20 waiting for exports/rearr_pw_long_e60 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearr_pw_long-e60.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-rearr_pw_long-e60 GPU None 
[pool] 2026-11-28 17:08:22 A40-fetch-rearr_pw_long-e60: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_long-e60.log
```

## A40-fetch-rearr_pw_h100_s18-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_h100_s18-e30.log):
```
[fetch] 2026-11-28 15:49:06 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 15:54:06 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 15:59:07 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 16:04:07 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 16:09:08 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 16:14:09 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 16:19:09 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 16:24:10 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 16:29:10 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 16:34:11 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 16:39:11 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 16:44:12 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 16:49:12 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 16:54:13 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 16:59:13 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 17:04:14 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 17:09:15 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 17:14:15 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 17:19:16 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 17:24:16 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 17:29:17 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 17:34:17 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 17:39:18 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 17:44:18 waiting for exports/rearr_pw_h100_s18_e30 on the relay
[fetch] 2026-11-28 17:49:19 waiting for exports/rearr_pw_h100_s18_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearr_pw_h100_s18-e30.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-rearr_pw_h100_s18-e30 GPU None 
[pool] 2026-11-28 17:08:21 A40-fetch-rearr_pw_h100_s18-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_h100_s18-e30.log
```

## A40-fetch-rearr_pw_h100-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_h100-e30.log):
```
[fetch] 2026-11-28 15:49:08 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 15:54:08 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 15:59:09 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 16:04:09 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 16:09:10 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 16:14:10 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 16:19:11 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 16:24:12 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 16:29:12 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 16:34:13 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 16:39:13 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 16:44:14 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 16:49:14 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 16:54:15 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 16:59:15 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 17:04:16 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 17:09:17 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 17:14:17 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 17:19:18 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 17:24:18 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 17:29:19 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 17:34:19 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 17:39:20 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 17:44:20 waiting for exports/rearr_pw_h100_e30 on the relay
[fetch] 2026-11-28 17:49:21 waiting for exports/rearr_pw_h100_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearr_pw_h100-e30.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-rearr_pw_h100-e30 GPU None 
[pool] 2026-11-28 17:08:22 A40-fetch-rearr_pw_h100-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_h100-e30.log
```

## A40-fetch-rearr_pw_h100_long_s18-e60 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_h100_long_s18-e60.log):
```
[fetch] 2026-11-28 15:49:07 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 15:54:08 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 15:59:09 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 16:04:09 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 16:09:10 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 16:14:10 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 16:19:11 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 16:24:11 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 16:29:12 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 16:34:12 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 16:39:13 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 16:44:13 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 16:49:14 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 16:54:15 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 16:59:15 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 17:04:16 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 17:09:16 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 17:14:17 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 17:19:17 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 17:24:18 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 17:29:18 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 17:34:19 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 17:39:19 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 17:44:20 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
[fetch] 2026-11-28 17:49:21 waiting for exports/rearr_pw_h100_long_s18_e60 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearr_pw_h100_long_s18-e60.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-rearr_pw_h100_long_s18-e60 GPU None 
[pool] 2026-11-28 17:08:22 A40-fetch-rearr_pw_h100_long_s18-e60: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_h100_long_s18-e60.log
```

## A40-fetch-rearr_pw_h100_long-e60 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_h100_long-e60.log):
```
[fetch] 2026-11-28 15:49:06 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 15:54:07 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 15:59:08 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 16:04:08 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 16:09:09 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 16:14:09 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 16:19:10 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 16:24:10 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 16:29:11 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 16:34:11 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 16:39:12 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 16:44:13 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 16:49:13 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 16:54:14 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 16:59:14 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 17:04:15 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 17:09:15 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 17:14:16 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 17:19:16 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 17:24:17 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 17:29:18 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 17:34:18 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 17:39:19 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 17:44:19 waiting for exports/rearr_pw_h100_long_e60 on the relay
[fetch] 2026-11-28 17:49:20 waiting for exports/rearr_pw_h100_long_e60 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearr_pw_h100_long-e60.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-rearr_pw_h100_long-e60 GPU None 
[pool] 2026-11-28 17:08:22 A40-fetch-rearr_pw_h100_long-e60: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_h100_long-e60.log
```

## A40-fetch-obs_cf800-e10 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-obs_cf800-e10.log):
```
[fetch] 2026-11-28 15:49:07 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 15:54:08 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 15:59:09 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 16:04:09 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 16:09:10 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 16:14:10 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 16:19:11 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 16:24:11 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 16:29:12 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 16:34:13 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 16:39:13 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 16:44:14 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 16:49:14 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 16:54:15 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 16:59:15 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 17:04:16 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 17:09:17 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 17:14:17 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 17:19:18 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 17:24:18 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 17:29:19 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 17:34:19 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 17:39:20 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 17:44:20 waiting for exports/obs_cf800_e10 on the relay
[fetch] 2026-11-28 17:49:21 waiting for exports/obs_cf800_e10 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-obs_cf800-e10.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-obs_cf800-e10 GPU None 
[pool] 2026-11-28 17:08:22 A40-fetch-obs_cf800-e10: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-obs_cf800-e10.log
```

## A40-fetch-rearr_joint3-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_joint3-e30.log):
```
[fetch] 2026-11-28 15:49:08 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 15:54:08 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 15:59:09 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 16:04:09 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 16:09:10 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 16:14:10 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 16:19:11 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 16:24:11 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 16:29:12 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 16:34:13 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 16:39:13 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 16:44:14 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 16:49:14 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 16:54:15 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 16:59:15 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 17:04:16 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 17:09:17 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 17:14:17 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 17:19:18 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 17:24:18 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 17:29:19 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 17:34:19 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 17:39:20 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 17:44:20 waiting for exports/rearr_joint3_e30 on the relay
[fetch] 2026-11-28 17:49:21 waiting for exports/rearr_joint3_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearr_joint3-e30.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-rearr_joint3-e30 GPU None 
[pool] 2026-11-28 17:08:22 A40-fetch-rearr_joint3-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_joint3-e30.log
```

## A40-fetch-swapT_joint3_ow-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_joint3_ow-e30.log):
```
[fetch] 2026-11-28 15:49:07 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 15:54:08 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 15:59:08 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 16:04:09 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 16:09:09 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 16:14:10 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 16:19:10 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 16:24:11 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 16:29:11 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 16:34:12 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 16:39:13 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 16:44:13 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 16:49:14 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 16:54:14 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 16:59:15 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 17:04:15 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 17:09:16 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 17:14:17 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 17:19:17 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 17:24:18 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 17:29:18 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 17:34:19 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 17:39:19 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 17:44:20 waiting for exports/swapT_joint3_ow_e30 on the relay
[fetch] 2026-11-28 17:49:20 waiting for exports/swapT_joint3_ow_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-swapT_joint3_ow-e30.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-swapT_joint3_ow-e30 GPU None 
[pool] 2026-11-28 17:08:22 A40-fetch-swapT_joint3_ow-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_joint3_ow-e30.log
```

## A40-fetch-press_cd-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-press_cd-e30.log):
```
[fetch] 2026-11-28 15:49:14 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 15:54:15 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 15:59:15 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 16:04:16 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 16:09:16 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 16:14:17 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 16:19:17 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 16:24:18 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 16:29:18 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 16:34:19 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 16:39:20 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 16:44:20 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 16:49:21 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 16:54:21 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 16:59:22 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 17:04:22 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 17:09:23 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 17:14:24 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 17:19:24 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 17:24:25 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 17:29:25 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 17:34:26 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 17:39:26 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 17:44:27 waiting for exports/press_cd_e30 on the relay
[fetch] 2026-11-28 17:49:27 waiting for exports/press_cd_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-press_cd-e30.log):
```

[pool] 2026-11-28 16:58:25 exec A40-fetch-press_cd-e30 GPU None 
[pool] 2026-11-28 16:58:29 A40-fetch-press_cd-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-press_cd-e30.log
```

## A40-C36FB-bank-put (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-C36FB-bank-put.log):
```


  ...ullft/bank_swap_T_a40.tgz: 100%|██████████| 17.1kB / 17.1kB            [A[A


  ...ullft/bank_swap_T_a40.tgz: 100%|██████████| 17.1kB / 17.1kB            [A[A


  ...ullft/bank_swap_T_a40.tgz: 100%|██████████| 17.1kB / 17.1kB            [A[A


  ...ullft/bank_swap_T_a40.tgz: 100%|██████████| 17.1kB / 17.1kB            [A[A


  ...ullft/bank_swap_T_a40.tgz: 100%|██████████| 17.1kB / 17.1kB            [A[A


  ...ullft/bank_swap_T_a40.tgz: 100%|██████████| 17.1kB / 17.1kB            [A[A
Processing Files (1 / 1)      : 100%|██████████| 17.1kB / 17.1kB, 1.38kB/s  

New Data Upload               : 100%|██████████| 17.1kB / 17.1kB, 1.38kB/s  

  ...ullft/bank_swap_T_a40.tgz: 100%|██████████| 17.1kB / 17.1kB            
[relay] put bank_swap_T_a40.tgz (17125 bytes) -> hhyfred/memwam-diag-v1/diag/bank_swap_T_a40/bank_swap_T_a40.tgz
[relay] put bank_swap_T_a40.tgz.sha256 (86 bytes) -> hhyfred/memwam-diag-v1/diag/bank_swap_T_a40/bank_swap_T_a40.tgz.sha256
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-C36FB-bank-put.log):
```

[pool] 2026-11-29 01:08:56 exec A40-C36FB-bank-put GPU None 
[pool] 2026-11-29 01:09:01 A40-C36FB-bank-put: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-C36FB-bank-put.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-C36FB-bank-put.md
[queue5] 2026-11-29 01:09:18 A40-C36FB-bank-put: PASS  rc=0
```

## A40-fetch-swapT_ow-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_ow-e30.log):
```
[fetch] 2026-11-28 15:49:24 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 15:54:24 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 15:59:25 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 16:04:25 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 16:09:26 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 16:14:26 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 16:19:27 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 16:24:27 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 16:29:28 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 16:34:28 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 16:39:29 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 16:44:30 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 16:49:30 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 16:54:31 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 16:59:31 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 17:04:32 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 17:09:33 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 17:14:33 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 17:19:34 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 17:24:34 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 17:29:35 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 17:34:35 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 17:39:36 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 17:44:37 waiting for exports/swapT_ow_e30 on the relay
[fetch] 2026-11-28 17:49:37 waiting for exports/swapT_ow_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-swapT_ow-e30.log):
```

[pool] 2026-11-28 16:28:29 exec A40-fetch-swapT_ow-e30 GPU None 
[pool] 2026-11-28 16:28:33 A40-fetch-swapT_ow-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_ow-e30.log
```

## A40-fetch-swapT_ow_s18-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_ow_s18-e30.log):
```
[fetch] 2026-11-28 15:49:31 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 15:54:31 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 15:59:32 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:04:32 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:09:33 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:14:34 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:19:34 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:24:35 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:29:35 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:34:36 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:39:36 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:44:37 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:49:38 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:54:38 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:59:39 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 17:04:39 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 17:09:40 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 17:14:40 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 17:19:41 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 17:24:41 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 17:29:42 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 17:34:43 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 17:39:43 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 17:44:44 waiting for exports/swapT_ow_s18_e30 on the relay
[fetch] 2026-11-28 17:49:44 waiting for exports/swapT_ow_s18_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-swapT_ow_s18-e30.log):
```

[pool] 2026-11-28 16:28:29 exec A40-fetch-swapT_ow_s18-e30 GPU None 
[pool] 2026-11-28 16:28:32 A40-fetch-swapT_ow_s18-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_ow_s18-e30.log
```

## A40-fetch-swapT_ar_ow-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_ar_ow-e30.log):
```
[fetch] 2026-11-28 15:49:22 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 15:54:22 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 15:59:23 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 16:04:23 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 16:09:24 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 16:14:25 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 16:19:25 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 16:24:26 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 16:29:26 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 16:34:27 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 16:39:27 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 16:44:28 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 16:49:28 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 16:54:29 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 16:59:30 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 17:04:30 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 17:09:31 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 17:14:31 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 17:19:32 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 17:24:32 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 17:29:33 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 17:34:34 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 17:39:34 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 17:44:35 waiting for exports/swapT_ar_ow_e30 on the relay
[fetch] 2026-11-28 17:49:35 waiting for exports/swapT_ar_ow_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-swapT_ar_ow-e30.log):
```

[pool] 2026-11-28 16:28:29 exec A40-fetch-swapT_ar_ow-e30 GPU None 
[pool] 2026-11-28 16:28:33 A40-fetch-swapT_ar_ow-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_ar_ow-e30.log
```

## A40-fetch-swapT_ar_ow_s18-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_ar_ow_s18-e30.log):
```
[fetch] 2026-11-28 15:49:24 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 15:54:25 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 15:59:25 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:04:26 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:09:26 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:14:27 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:19:28 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:24:28 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:29:29 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:34:29 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:39:30 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:44:30 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:49:31 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:54:31 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 16:59:32 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 17:04:33 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 17:09:33 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 17:14:34 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 17:19:34 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 17:24:35 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 17:29:35 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 17:34:36 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 17:39:37 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 17:44:37 waiting for exports/swapT_ar_ow_s18_e30 on the relay
[fetch] 2026-11-28 17:49:38 waiting for exports/swapT_ar_ow_s18_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-swapT_ar_ow_s18-e30.log):
```

[pool] 2026-11-28 16:28:29 exec A40-fetch-swapT_ar_ow_s18-e30 GPU None 
[pool] 2026-11-28 16:28:33 A40-fetch-swapT_ar_ow_s18-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_ar_ow_s18-e30.log
```

## A40-d8-swapT_x16-s0 (done, attempt 2, GPU 4)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 6,
  "time": "2026-11-28 16:52:48",
  "why": "6 episodes ended with ERROR.json (re-run retries only those)"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_x16-s0.log):
```
[decide] 2026-11-28 09:25:42 swapT_ar_e30_x16/on swap_T seed=4300044 frame=128/600 hist=3 policy=0.6s elapsed=50s
[decide] 2026-11-28 09:26:01 swapT_ar_e30_x16/on swap_T seed=4300044 frame=192/600 hist=3 policy=0.6s elapsed=69s
[decide] 2026-11-28 09:26:20 swapT_ar_e30_x16/on swap_T seed=4300044 frame=256/600 hist=3 policy=0.6s elapsed=88s
[decide] 2026-11-28 09:26:38 swapT_ar_e30_x16/on swap_T seed=4300044 frame=320/600 hist=3 policy=0.5s elapsed=106s
[decide] 2026-11-28 09:26:57 swapT_ar_e30_x16/on swap_T seed=4300044 frame=384/600 hist=3 policy=0.6s elapsed=125s
[decide] 2026-11-28 09:27:24 swapT_ar_e30_x16/on swap_T seed=4300044 frame=448/600 hist=3 policy=0.5s elapsed=152s
[decide] 2026-11-28 09:27:44 swapT_ar_e30_x16/on swap_T seed=4300044 frame=512/600 hist=3 policy=0.5s elapsed=172s
[decide] 2026-11-28 09:28:09 swapT_ar_e30_x16/on swap_T seed=4300044 frame=576/600 hist=3 policy=0.5s elapsed=197s
[closed-loop] 2026-11-28 09:28:18 done  swapT_ar_e30_x16/on swap_T seed=4300044 success=False targets=600/600 reward=0.0 lift=None  251s
[closed-loop] 2026-11-28 09:28:18 start swapT_ar_e30_x16/on swap_T seed=4300049 target_limit=600 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x16/on/swap_T/seed_4300049
[decide] 2026-11-28 09:29:08 swapT_ar_e30_x16/on swap_T seed=4300049 frame=0/600 hist=0 policy=0.5s elapsed=6s
[decide] 2026-11-28 09:29:28 swapT_ar_e30_x16/on swap_T seed=4300049 frame=64/600 hist=3 policy=0.6s elapsed=26s
[decide] 2026-11-28 09:29:55 swapT_ar_e30_x16/on swap_T seed=4300049 frame=128/600 hist=3 policy=0.5s elapsed=52s
[decide] 2026-11-28 09:30:14 swapT_ar_e30_x16/on swap_T seed=4300049 frame=192/600 hist=3 policy=0.5s elapsed=71s
[decide] 2026-11-28 09:30:39 swapT_ar_e30_x16/on swap_T seed=4300049 frame=256/600 hist=3 policy=0.5s elapsed=96s
[closed-loop] 2026-11-28 09:30:51 done  swapT_ar_e30_x16/on swap_T seed=4300049 success=True targets=293/600 reward=1.0 lift=None  153s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
swapT_ar_e30_x16/on     swap_T            49     0.53  [0.39,0.66]         -    0.53      436        -        -        -    0.6
swapT_ar_e30_x32/on     swap_T             7     0.57  [0.25,0.84]         -    0.57      425        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  swapT_ar_e30_x16/on      vs swapT_ar_e30_x32/on        7     2       1       2        2  1.000

[summary] 56 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-swapT_x16-s0.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 17:31:08 A40-d8-swapT_x16-s0: DONE  swap_T/on n=49  prog=0.00
```

## A40-d8-swapT_x16-s1 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_x16-s1.log):
```
[decide] 2026-11-28 09:11:17 swapT_ar_e30_x16/on swap_T seed=4300045 frame=128/600 hist=3 policy=0.6s elapsed=47s
[decide] 2026-11-28 09:11:45 swapT_ar_e30_x16/on swap_T seed=4300045 frame=192/600 hist=3 policy=0.6s elapsed=75s
[decide] 2026-11-28 09:12:11 swapT_ar_e30_x16/on swap_T seed=4300045 frame=256/600 hist=3 policy=0.6s elapsed=101s
[closed-loop] 2026-11-28 09:12:28 done  swapT_ar_e30_x16/on swap_T seed=4300045 success=True targets=293/600 reward=1.0 lift=None  159s
[closed-loop] 2026-11-28 09:12:28 start swapT_ar_e30_x16/on swap_T seed=4300050 target_limit=600 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x16/on/swap_T/seed_4300050
[decide] 2026-11-28 09:13:14 swapT_ar_e30_x16/on swap_T seed=4300050 frame=0/600 hist=0 policy=0.5s elapsed=6s
[decide] 2026-11-28 09:13:37 swapT_ar_e30_x16/on swap_T seed=4300050 frame=64/600 hist=3 policy=0.6s elapsed=29s
[decide] 2026-11-28 09:14:02 swapT_ar_e30_x16/on swap_T seed=4300050 frame=128/600 hist=3 policy=0.6s elapsed=54s
[decide] 2026-11-28 09:14:29 swapT_ar_e30_x16/on swap_T seed=4300050 frame=192/600 hist=3 policy=0.6s elapsed=81s
[decide] 2026-11-28 09:14:49 swapT_ar_e30_x16/on swap_T seed=4300050 frame=256/600 hist=3 policy=0.6s elapsed=100s
[decide] 2026-11-28 09:15:07 swapT_ar_e30_x16/on swap_T seed=4300050 frame=320/600 hist=3 policy=0.6s elapsed=119s
[decide] 2026-11-28 09:15:25 swapT_ar_e30_x16/on swap_T seed=4300050 frame=384/600 hist=3 policy=0.6s elapsed=137s
[decide] 2026-11-28 09:15:46 swapT_ar_e30_x16/on swap_T seed=4300050 frame=448/600 hist=3 policy=0.6s elapsed=158s
[decide] 2026-11-28 09:16:07 swapT_ar_e30_x16/on swap_T seed=4300050 frame=512/600 hist=3 policy=0.6s elapsed=178s
[decide] 2026-11-28 09:16:26 swapT_ar_e30_x16/on swap_T seed=4300050 frame=576/600 hist=3 policy=0.6s elapsed=198s
[closed-loop] 2026-11-28 09:16:44 done  swapT_ar_e30_x16/on swap_T seed=4300050 success=False targets=600/600 reward=0.0 lift=None  255s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
swapT_ar_e30_x16/on     swap_T            40     0.55  [0.40,0.69]         -    0.55      430        -        -        -    0.6

[summary] 40 episodes, 4 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/SUMMARY.json
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x16/on/swap_T/seed_4300034/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x16/on/swap_T/seed_4300039/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x16/on/swap_T/seed_4300044/ERROR.json: nv/lib/python3.10/multiprocessing/connection.py", line 414, in _recv_bytes\n    buf = self._recv(4)\n  File "/opt/rmbench-fused-env/lib/python3.10/multiprocessing/connection.py", line 379, in _recv\n    chunk = read(handle, remaining)\nConnectionResetError: [Errno 104] Connection reset by peer\n\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x16/on/swap_T/seed_4300049/ERROR.json: nv/lib/python3.10/multiprocessing/connection.py", line 414, in _recv_bytes\n    buf = self._recv(4)\n  File "/opt/rmbench-fused-env/lib/python3.10/multiprocessing/connection.py", line 379, in _recv\n    chunk = read(handle, remaining)\nConnectionResetError: [Errno 104] Connection reset by peer\n\n')
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-swapT_x16-s1.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 17:16:58 A40-d8-swapT_x16-s1: DONE  swap_T/on n=40  prog=0.00; errors=4
```

## A40-d8-swapT_x16-s2 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_x16-s2.log):
```
[decide] 2026-11-28 09:01:45 swapT_ar_e30_x16/on swap_T seed=4300046 frame=256/600 hist=3 policy=0.6s elapsed=104s
[closed-loop] 2026-11-28 09:01:55 done  swapT_ar_e30_x16/on swap_T seed=4300046 success=True targets=284/600 reward=1.0 lift=None  157s
[closed-loop] 2026-11-28 09:01:55 start swapT_ar_e30_x16/on swap_T seed=4300051 target_limit=600 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x16/on/swap_T/seed_4300051
[decide] 2026-11-28 09:02:39 swapT_ar_e30_x16/on swap_T seed=4300051 frame=0/600 hist=0 policy=0.5s elapsed=6s
[decide] 2026-11-28 09:02:59 swapT_ar_e30_x16/on swap_T seed=4300051 frame=64/600 hist=3 policy=0.5s elapsed=26s
[decide] 2026-11-28 09:03:19 swapT_ar_e30_x16/on swap_T seed=4300051 frame=128/600 hist=3 policy=0.5s elapsed=46s
[decide] 2026-11-28 09:03:41 swapT_ar_e30_x16/on swap_T seed=4300051 frame=192/600 hist=3 policy=0.6s elapsed=68s
[decide] 2026-11-28 09:04:06 swapT_ar_e30_x16/on swap_T seed=4300051 frame=256/600 hist=3 policy=0.6s elapsed=93s
[decide] 2026-11-28 09:04:28 swapT_ar_e30_x16/on swap_T seed=4300051 frame=320/600 hist=3 policy=0.6s elapsed=115s
[decide] 2026-11-28 09:04:45 swapT_ar_e30_x16/on swap_T seed=4300051 frame=384/600 hist=3 policy=0.6s elapsed=132s
[decide] 2026-11-28 09:05:09 swapT_ar_e30_x16/on swap_T seed=4300051 frame=448/600 hist=3 policy=0.6s elapsed=156s
[decide] 2026-11-28 09:05:25 swapT_ar_e30_x16/on swap_T seed=4300051 frame=512/600 hist=3 policy=0.6s elapsed=172s
[decide] 2026-11-28 09:05:49 swapT_ar_e30_x16/on swap_T seed=4300051 frame=576/600 hist=3 policy=0.6s elapsed=196s
[closed-loop] 2026-11-28 09:05:57 done  swapT_ar_e30_x16/on swap_T seed=4300051 success=False targets=600/600 reward=0.0 lift=None  242s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
swapT_ar_e30_x16/on     swap_T            28     0.50  [0.33,0.67]         -    0.50      446        -        -        -    0.7

[summary] 28 episodes, 6 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/SUMMARY.json
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x16/on/swap_T/seed_4300021/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x16/on/swap_T/seed_4300028/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x16/on/swap_T/seed_4300034/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x16/on/swap_T/seed_4300039/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x16/on/swap_T/seed_4300044/ERROR.json: nv/lib/python3.10/multiprocessing/connection.py", line 414, in _recv_bytes\n    buf = self._recv(4)\n  File "/opt/rmbench-fused-env/lib/python3.10/multiprocessing/connection.py", line 379, in _recv\n    chunk = read(handle, remaining)\nConnectionResetError: [Errno 104] Connection reset by peer\n\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x16/on/swap_T/seed_4300049/ERROR.json: nv/lib/python3.10/multiprocessing/connection.py", line 414, in _recv_bytes\n    buf = self._recv(4)\n  File "/opt/rmbench-fused-env/lib/python3.10/multiprocessing/connection.py", line 379, in _recv\n    chunk = read(handle, remaining)\nConnectionResetError: [Errno 104] Connection reset by peer\n\n')
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-swapT_x16-s2.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 17:06:08 A40-d8-swapT_x16-s2: DONE  swap_T/on n=28  prog=0.00; errors=6
```

## A40-d8-swapT_x16-s3 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_x16-s3.log):
```
[decide] 2026-11-28 09:08:38 swapT_ar_e30_x16/on swap_T seed=4300042 frame=256/600 hist=3 policy=0.6s elapsed=93s
[closed-loop] 2026-11-28 09:08:48 done  swapT_ar_e30_x16/on swap_T seed=4300042 success=True targets=285/600 reward=1.0 lift=None  143s
[closed-loop] 2026-11-28 09:08:48 start swapT_ar_e30_x16/on swap_T seed=4300047 target_limit=600 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x16/on/swap_T/seed_4300047
[decide] 2026-11-28 09:09:43 swapT_ar_e30_x16/on swap_T seed=4300047 frame=0/600 hist=0 policy=0.5s elapsed=6s
[decide] 2026-11-28 09:10:10 swapT_ar_e30_x16/on swap_T seed=4300047 frame=64/600 hist=3 policy=0.6s elapsed=34s
[decide] 2026-11-28 09:10:30 swapT_ar_e30_x16/on swap_T seed=4300047 frame=128/600 hist=3 policy=0.6s elapsed=54s
[decide] 2026-11-28 09:10:50 swapT_ar_e30_x16/on swap_T seed=4300047 frame=192/600 hist=3 policy=0.6s elapsed=74s
[decide] 2026-11-28 09:11:10 swapT_ar_e30_x16/on swap_T seed=4300047 frame=256/600 hist=3 policy=0.6s elapsed=93s
[closed-loop] 2026-11-28 09:11:20 done  swapT_ar_e30_x16/on swap_T seed=4300047 success=True targets=285/600 reward=1.0 lift=None  151s
[closed-loop] 2026-11-28 09:11:20 start swapT_ar_e30_x16/on swap_T seed=4300052 target_limit=600 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x16/on/swap_T/seed_4300052
[decide] 2026-11-28 09:12:18 swapT_ar_e30_x16/on swap_T seed=4300052 frame=0/600 hist=0 policy=0.5s elapsed=11s
[decide] 2026-11-28 09:12:41 swapT_ar_e30_x16/on swap_T seed=4300052 frame=64/600 hist=3 policy=0.6s elapsed=34s
[decide] 2026-11-28 09:13:06 swapT_ar_e30_x16/on swap_T seed=4300052 frame=128/600 hist=3 policy=0.6s elapsed=58s
[decide] 2026-11-28 09:13:25 swapT_ar_e30_x16/on swap_T seed=4300052 frame=192/600 hist=3 policy=0.6s elapsed=78s
[decide] 2026-11-28 09:13:51 swapT_ar_e30_x16/on swap_T seed=4300052 frame=256/600 hist=3 policy=0.6s elapsed=104s
[closed-loop] 2026-11-28 09:14:04 done  swapT_ar_e30_x16/on swap_T seed=4300052 success=True targets=293/600 reward=1.0 lift=None  165s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
swapT_ar_e30_x16/on     swap_T            37     0.54  [0.38,0.69]         -    0.54      433        -        -        -    0.6

[summary] 37 episodes, 4 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/SUMMARY.json
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x16/on/swap_T/seed_4300034/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x16/on/swap_T/seed_4300039/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x16/on/swap_T/seed_4300044/ERROR.json: nv/lib/python3.10/multiprocessing/connection.py", line 414, in _recv_bytes\n    buf = self._recv(4)\n  File "/opt/rmbench-fused-env/lib/python3.10/multiprocessing/connection.py", line 379, in _recv\n    chunk = read(handle, remaining)\nConnectionResetError: [Errno 104] Connection reset by peer\n\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x16/on/swap_T/seed_4300049/ERROR.json: nv/lib/python3.10/multiprocessing/connection.py", line 414, in _recv_bytes\n    buf = self._recv(4)\n  File "/opt/rmbench-fused-env/lib/python3.10/multiprocessing/connection.py", line 379, in _recv\n    chunk = read(handle, remaining)\nConnectionResetError: [Errno 104] Connection reset by peer\n\n')
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-swapT_x16-s3.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 17:14:18 A40-d8-swapT_x16-s3: DONE  swap_T/on n=37  prog=0.00; errors=4
```

## A40-d8-swapT_x16-s4 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_x16-s4.log):
```
[decide] 2026-11-28 09:28:28 swapT_ar_e30_x16/on swap_T seed=4300048 frame=128/600 hist=3 policy=0.5s elapsed=56s
[decide] 2026-11-28 09:28:59 swapT_ar_e30_x16/on swap_T seed=4300048 frame=192/600 hist=3 policy=0.6s elapsed=86s
[decide] 2026-11-28 09:29:18 swapT_ar_e30_x16/on swap_T seed=4300048 frame=256/600 hist=3 policy=0.6s elapsed=105s
[closed-loop] 2026-11-28 09:29:28 done  swapT_ar_e30_x16/on swap_T seed=4300048 success=True targets=284/600 reward=1.0 lift=None  154s
[closed-loop] 2026-11-28 09:29:28 start swapT_ar_e30_x16/on swap_T seed=4300053 target_limit=600 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x16/on/swap_T/seed_4300053
[decide] 2026-11-28 09:30:12 swapT_ar_e30_x16/on swap_T seed=4300053 frame=0/600 hist=0 policy=0.5s elapsed=6s
[decide] 2026-11-28 09:30:38 swapT_ar_e30_x16/on swap_T seed=4300053 frame=64/600 hist=3 policy=0.6s elapsed=33s
[decide] 2026-11-28 09:30:58 swapT_ar_e30_x16/on swap_T seed=4300053 frame=128/600 hist=3 policy=0.5s elapsed=52s
[decide] 2026-11-28 09:31:24 swapT_ar_e30_x16/on swap_T seed=4300053 frame=192/600 hist=3 policy=0.5s elapsed=78s
[decide] 2026-11-28 09:31:50 swapT_ar_e30_x16/on swap_T seed=4300053 frame=256/600 hist=3 policy=0.5s elapsed=104s
[decide] 2026-11-28 09:32:08 swapT_ar_e30_x16/on swap_T seed=4300053 frame=320/600 hist=3 policy=0.6s elapsed=123s
[decide] 2026-11-28 09:32:24 swapT_ar_e30_x16/on swap_T seed=4300053 frame=384/600 hist=3 policy=0.5s elapsed=139s
[decide] 2026-11-28 09:32:51 swapT_ar_e30_x16/on swap_T seed=4300053 frame=448/600 hist=3 policy=0.5s elapsed=166s
[decide] 2026-11-28 09:33:12 swapT_ar_e30_x16/on swap_T seed=4300053 frame=512/600 hist=3 policy=0.6s elapsed=186s
[decide] 2026-11-28 09:33:36 swapT_ar_e30_x16/on swap_T seed=4300053 frame=576/600 hist=3 policy=0.6s elapsed=211s
[closed-loop] 2026-11-28 09:33:46 done  swapT_ar_e30_x16/on swap_T seed=4300053 success=False targets=600/600 reward=0.0 lift=None  259s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
swapT_ar_e30_x16/on     swap_T            50     0.52  [0.39,0.65]         -    0.52      439        -        -        -    0.6
swapT_ar_e30_x32/on     swap_T             8     0.50  [0.22,0.78]         -    0.50      446        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  swapT_ar_e30_x16/on      vs swapT_ar_e30_x32/on        8     2       1       2        3  1.000

[summary] 58 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-swapT_x16-s4.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 17:34:03 A40-d8-swapT_x16-s4: DONE  swap_T/on n=50  prog=0.00
```

## A40-d8-swapT_x32-s0 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_x32-s0.log):
```
[decide] 2026-11-28 09:43:09 swapT_ar_e30_x32/on swap_T seed=4300039 frame=256/600 hist=3 policy=0.6s elapsed=93s
[decide] 2026-11-28 09:43:49 swapT_ar_e30_x32/on swap_T seed=4300039 frame=384/600 hist=3 policy=0.6s elapsed=133s
[decide] 2026-11-28 09:44:27 swapT_ar_e30_x32/on swap_T seed=4300039 frame=512/600 hist=3 policy=0.6s elapsed=171s
[closed-loop] 2026-11-28 09:44:53 done  swapT_ar_e30_x32/on swap_T seed=4300039 success=False targets=600/600 reward=0.0 lift=None  247s
[closed-loop] 2026-11-28 09:44:53 start swapT_ar_e30_x32/on swap_T seed=4300044 target_limit=600 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x32/on/swap_T/seed_4300044
[decide] 2026-11-28 09:45:44 swapT_ar_e30_x32/on swap_T seed=4300044 frame=0/600 hist=0 policy=0.4s elapsed=6s
[decide] 2026-11-28 09:46:41 swapT_ar_e30_x32/on swap_T seed=4300044 frame=128/600 hist=3 policy=0.6s elapsed=64s
[decide] 2026-11-28 09:47:17 swapT_ar_e30_x32/on swap_T seed=4300044 frame=256/600 hist=3 policy=0.6s elapsed=100s
[decide] 2026-11-28 09:47:54 swapT_ar_e30_x32/on swap_T seed=4300044 frame=384/600 hist=3 policy=0.6s elapsed=136s
[decide] 2026-11-28 09:48:50 swapT_ar_e30_x32/on swap_T seed=4300044 frame=512/600 hist=3 policy=0.6s elapsed=193s
[closed-loop] 2026-11-28 09:49:15 done  swapT_ar_e30_x32/on swap_T seed=4300044 success=False targets=600/600 reward=0.0 lift=None  263s
[closed-loop] 2026-11-28 09:49:15 start swapT_ar_e30_x32/on swap_T seed=4300049 target_limit=600 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x32/on/swap_T/seed_4300049
[decide] 2026-11-28 09:49:59 swapT_ar_e30_x32/on swap_T seed=4300049 frame=0/600 hist=0 policy=0.4s elapsed=6s
[decide] 2026-11-28 09:50:46 swapT_ar_e30_x32/on swap_T seed=4300049 frame=128/600 hist=3 policy=0.6s elapsed=53s
[decide] 2026-11-28 09:51:26 swapT_ar_e30_x32/on swap_T seed=4300049 frame=256/600 hist=3 policy=0.6s elapsed=93s
[closed-loop] 2026-11-28 09:51:38 done  swapT_ar_e30_x32/on swap_T seed=4300049 success=True targets=291/600 reward=1.0 lift=None  142s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
swapT_ar_e30_x16/on     swap_T            50     0.52  [0.39,0.65]         -    0.52      439        -        -        -    0.6
swapT_ar_e30_x32/on     swap_T            34     0.53  [0.37,0.69]         -    0.53      437        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  swapT_ar_e30_x16/on      vs swapT_ar_e30_x32/on       34    12       3       6       13  0.508

[summary] 84 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-swapT_x32-s0.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 17:51:51 A40-d8-swapT_x32-s0: DONE  swap_T/on n=34  prog=0.00
```

## A40-d8-swapT_x32-s1 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_x32-s1.log):
```
[decide] 2026-11-28 09:43:52 swapT_ar_e30_x32/on swap_T seed=4300040 frame=256/600 hist=3 policy=0.6s elapsed=86s
[decide] 2026-11-28 09:44:25 swapT_ar_e30_x32/on swap_T seed=4300040 frame=384/600 hist=3 policy=0.6s elapsed=119s
[decide] 2026-11-28 09:45:06 swapT_ar_e30_x32/on swap_T seed=4300040 frame=512/600 hist=3 policy=0.6s elapsed=159s
[closed-loop] 2026-11-28 09:45:42 done  swapT_ar_e30_x32/on swap_T seed=4300040 success=False targets=600/600 reward=0.0 lift=None  241s
[closed-loop] 2026-11-28 09:45:42 start swapT_ar_e30_x32/on swap_T seed=4300045 target_limit=600 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x32/on/swap_T/seed_4300045
[decide] 2026-11-28 09:46:39 swapT_ar_e30_x32/on swap_T seed=4300045 frame=0/600 hist=0 policy=0.4s elapsed=11s
[decide] 2026-11-28 09:47:17 swapT_ar_e30_x32/on swap_T seed=4300045 frame=128/600 hist=3 policy=0.6s elapsed=48s
[decide] 2026-11-28 09:47:55 swapT_ar_e30_x32/on swap_T seed=4300045 frame=256/600 hist=3 policy=0.6s elapsed=86s
[closed-loop] 2026-11-28 09:48:11 done  swapT_ar_e30_x32/on swap_T seed=4300045 success=True targets=291/600 reward=1.0 lift=None  148s
[closed-loop] 2026-11-28 09:48:11 start swapT_ar_e30_x32/on swap_T seed=4300050 target_limit=600 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x32/on/swap_T/seed_4300050
[decide] 2026-11-28 09:49:00 swapT_ar_e30_x32/on swap_T seed=4300050 frame=0/600 hist=0 policy=0.4s elapsed=6s
[decide] 2026-11-28 09:49:44 swapT_ar_e30_x32/on swap_T seed=4300050 frame=128/600 hist=3 policy=0.6s elapsed=50s
[decide] 2026-11-28 09:50:22 swapT_ar_e30_x32/on swap_T seed=4300050 frame=256/600 hist=3 policy=0.6s elapsed=88s
[decide] 2026-11-28 09:51:07 swapT_ar_e30_x32/on swap_T seed=4300050 frame=384/600 hist=3 policy=0.6s elapsed=133s
[decide] 2026-11-28 09:51:45 swapT_ar_e30_x32/on swap_T seed=4300050 frame=512/600 hist=3 policy=0.6s elapsed=171s
[closed-loop] 2026-11-28 09:52:10 done  swapT_ar_e30_x32/on swap_T seed=4300050 success=False targets=600/600 reward=0.0 lift=None  240s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
swapT_ar_e30_x16/on     swap_T            50     0.52  [0.39,0.65]         -    0.52      439        -        -        -    0.6
swapT_ar_e30_x32/on     swap_T            35     0.51  [0.36,0.67]         -    0.51      441        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  swapT_ar_e30_x16/on      vs swapT_ar_e30_x32/on       35    12       3       6       14  0.508

[summary] 85 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-swapT_x32-s1.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 17:52:23 A40-d8-swapT_x32-s1: DONE  swap_T/on n=35  prog=0.00
```

## A40-d8-swapT_x32-s2 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_x32-s2.log):
```
[decide] 2026-11-28 09:57:11 swapT_ar_e30_x32/on swap_T seed=4300041 frame=128/600 hist=3 policy=0.6s elapsed=52s
[decide] 2026-11-28 09:57:55 swapT_ar_e30_x32/on swap_T seed=4300041 frame=256/600 hist=3 policy=0.6s elapsed=96s
[closed-loop] 2026-11-28 09:58:09 done  swapT_ar_e30_x32/on swap_T seed=4300041 success=True targets=295/600 reward=1.0 lift=None  153s
[closed-loop] 2026-11-28 09:58:09 start swapT_ar_e30_x32/on swap_T seed=4300046 target_limit=600 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x32/on/swap_T/seed_4300046
[decide] 2026-11-28 09:58:52 swapT_ar_e30_x32/on swap_T seed=4300046 frame=0/600 hist=0 policy=0.5s elapsed=6s
[decide] 2026-11-28 09:59:38 swapT_ar_e30_x32/on swap_T seed=4300046 frame=128/600 hist=3 policy=0.6s elapsed=52s
[decide] 2026-11-28 10:00:16 swapT_ar_e30_x32/on swap_T seed=4300046 frame=256/600 hist=3 policy=0.6s elapsed=90s
[closed-loop] 2026-11-28 10:00:26 done  swapT_ar_e30_x32/on swap_T seed=4300046 success=True targets=288/600 reward=1.0 lift=None  138s
[closed-loop] 2026-11-28 10:00:26 start swapT_ar_e30_x32/on swap_T seed=4300051 target_limit=600 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x32/on/swap_T/seed_4300051
[decide] 2026-11-28 10:01:17 swapT_ar_e30_x32/on swap_T seed=4300051 frame=0/600 hist=0 policy=0.5s elapsed=6s
[decide] 2026-11-28 10:02:04 swapT_ar_e30_x32/on swap_T seed=4300051 frame=128/600 hist=3 policy=0.6s elapsed=53s
[decide] 2026-11-28 10:02:40 swapT_ar_e30_x32/on swap_T seed=4300051 frame=256/600 hist=3 policy=0.6s elapsed=89s
[closed-loop] 2026-11-28 10:02:55 done  swapT_ar_e30_x32/on swap_T seed=4300051 success=True targets=296/600 reward=1.0 lift=None  149s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
swapT_ar_e30_s50/on     swap_T             3     0.67  [0.21,0.94]         -    0.67      394        -        -        -    2.4
swapT_ar_e30_x16/on     swap_T            50     0.52  [0.39,0.65]         -    0.52      439        -        -        -    0.6
swapT_ar_e30_x32/on     swap_T            47     0.57  [0.43,0.70]         -    0.57      423        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x16/on        3     0       2       0        1  0.500
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x32/on        3     2       0       0        1  1.000
  swapT_ar_e30_x16/on      vs swapT_ar_e30_x32/on       47    20       4       7       16  0.549

[summary] 100 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-swapT_x32-s2.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 18:03:11 A40-d8-swapT_x32-s2: DONE  swap_T/on n=47  prog=0.00
```

## A40-d8-swapT_x32-s3 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_x32-s3.log):
```
[decide] 2026-11-28 09:54:08 swapT_ar_e30_x32/on swap_T seed=4300042 frame=128/600 hist=3 policy=0.6s elapsed=50s
[decide] 2026-11-28 09:54:51 swapT_ar_e30_x32/on swap_T seed=4300042 frame=256/600 hist=3 policy=0.6s elapsed=92s
[closed-loop] 2026-11-28 09:55:00 done  swapT_ar_e30_x32/on swap_T seed=4300042 success=True targets=286/600 reward=1.0 lift=None  149s
[closed-loop] 2026-11-28 09:55:00 start swapT_ar_e30_x32/on swap_T seed=4300047 target_limit=600 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x32/on/swap_T/seed_4300047
[decide] 2026-11-28 09:55:59 swapT_ar_e30_x32/on swap_T seed=4300047 frame=0/600 hist=0 policy=0.4s elapsed=13s
[decide] 2026-11-28 09:56:41 swapT_ar_e30_x32/on swap_T seed=4300047 frame=128/600 hist=3 policy=0.6s elapsed=55s
[decide] 2026-11-28 09:57:24 swapT_ar_e30_x32/on swap_T seed=4300047 frame=256/600 hist=3 policy=0.6s elapsed=98s
[closed-loop] 2026-11-28 09:57:33 done  swapT_ar_e30_x32/on swap_T seed=4300047 success=True targets=284/600 reward=1.0 lift=None  153s
[closed-loop] 2026-11-28 09:57:33 start swapT_ar_e30_x32/on swap_T seed=4300052 target_limit=600 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x32/on/swap_T/seed_4300052
[decide] 2026-11-28 09:58:18 swapT_ar_e30_x32/on swap_T seed=4300052 frame=0/600 hist=0 policy=0.4s elapsed=7s
[decide] 2026-11-28 09:59:00 swapT_ar_e30_x32/on swap_T seed=4300052 frame=128/600 hist=3 policy=0.6s elapsed=49s
[decide] 2026-11-28 09:59:43 swapT_ar_e30_x32/on swap_T seed=4300052 frame=256/600 hist=3 policy=0.6s elapsed=92s
[closed-loop] 2026-11-28 09:59:55 done  swapT_ar_e30_x32/on swap_T seed=4300052 success=True targets=293/600 reward=1.0 lift=None  142s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
swapT_ar_e30_s50/on     swap_T             1     1.00  [0.21,1.00]         -    1.00      289        -        -        -    2.3
swapT_ar_e30_x16/on     swap_T            50     0.52  [0.39,0.65]         -    0.52      439        -        -        -    0.6
swapT_ar_e30_x32/on     swap_T            44     0.57  [0.42,0.70]         -    0.57      424        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x16/on        1     0       1       0        0  1.000
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x32/on        1     1       0       0        0  1.000
  swapT_ar_e30_x16/on      vs swapT_ar_e30_x32/on       44    19       4       6       15  0.754

[summary] 95 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-swapT_x32-s3.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 18:00:10 A40-d8-swapT_x32-s3: DONE  swap_T/on n=44  prog=0.00
```

## A40-d8-swapT_x32-s4 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_x32-s4.log):
```
[closed-loop] 2026-11-28 10:03:13 done  swapT_ar_e30_x32/on swap_T seed=4300043 success=True targets=291/600 reward=1.0 lift=None  146s
[closed-loop] 2026-11-28 10:03:13 start swapT_ar_e30_x32/on swap_T seed=4300048 target_limit=600 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x32/on/swap_T/seed_4300048
[decide] 2026-11-28 10:03:59 swapT_ar_e30_x32/on swap_T seed=4300048 frame=0/600 hist=0 policy=0.4s elapsed=6s
[decide] 2026-11-28 10:04:36 swapT_ar_e30_x32/on swap_T seed=4300048 frame=128/600 hist=3 policy=0.6s elapsed=44s
[decide] 2026-11-28 10:05:12 swapT_ar_e30_x32/on swap_T seed=4300048 frame=256/600 hist=3 policy=0.6s elapsed=79s
[closed-loop] 2026-11-28 10:05:23 done  swapT_ar_e30_x32/on swap_T seed=4300048 success=True targets=289/600 reward=1.0 lift=None  130s
[closed-loop] 2026-11-28 10:05:23 start swapT_ar_e30_x32/on swap_T seed=4300053 target_limit=600 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_x32/on/swap_T/seed_4300053
[decide] 2026-11-28 10:06:20 swapT_ar_e30_x32/on swap_T seed=4300053 frame=0/600 hist=0 policy=0.4s elapsed=6s
[decide] 2026-11-28 10:06:57 swapT_ar_e30_x32/on swap_T seed=4300053 frame=128/600 hist=3 policy=0.6s elapsed=44s
[decide] 2026-11-28 10:07:40 swapT_ar_e30_x32/on swap_T seed=4300053 frame=256/600 hist=3 policy=0.6s elapsed=86s
[decide] 2026-11-28 10:08:13 swapT_ar_e30_x32/on swap_T seed=4300053 frame=384/600 hist=3 policy=0.6s elapsed=119s
[decide] 2026-11-28 10:08:51 swapT_ar_e30_x32/on swap_T seed=4300053 frame=512/600 hist=3 policy=0.6s elapsed=158s
[closed-loop] 2026-11-28 10:09:16 done  swapT_ar_e30_x32/on swap_T seed=4300053 success=False targets=600/600 reward=0.0 lift=None  233s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
swapT_ar_e30_s50/on     swap_T             5     0.80  [0.38,0.96]         -    0.80      353        -        -        -    2.4
swapT_ar_e30_x16/on     swap_T            50     0.52  [0.39,0.65]         -    0.52      439        -        -        -    0.6
swapT_ar_e30_x32/on     swap_T            50     0.58  [0.44,0.71]         -    0.58      421        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x16/on        5     2       2       0        1  0.500
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x32/on        5     3       1       0        1  1.000
  swapT_ar_e30_x16/on      vs swapT_ar_e30_x32/on       50    22       4       7       17  0.549

[summary] 105 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-swapT_x32-s4.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 18:09:34 A40-d8-swapT_x32-s4: DONE  swap_T/on n=50  prog=0.00
```

## A40-d8-swapT_s50-s0 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_s50-s0.log):
```
[closed-loop] 2026-11-28 10:44:12 done  swapT_ar_e30_s50/on swap_T seed=4300044 success=False targets=600/600 reward=0.0 lift=None  421s
[closed-loop] 2026-11-28 10:44:12 start swapT_ar_e30_s50/on swap_T seed=4300049 target_limit=600 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_s50/on/swap_T/seed_4300049
[decide] 2026-11-28 10:45:06 swapT_ar_e30_s50/on swap_T seed=4300049 frame=0/600 hist=0 policy=1.9s elapsed=10s
[decide] 2026-11-28 10:45:26 swapT_ar_e30_s50/on swap_T seed=4300049 frame=32/600 hist=2 policy=2.3s elapsed=31s
[decide] 2026-11-28 10:45:44 swapT_ar_e30_s50/on swap_T seed=4300049 frame=64/600 hist=3 policy=2.3s elapsed=49s
[decide] 2026-11-28 10:46:03 swapT_ar_e30_s50/on swap_T seed=4300049 frame=96/600 hist=3 policy=2.3s elapsed=67s
[decide] 2026-11-28 10:46:20 swapT_ar_e30_s50/on swap_T seed=4300049 frame=128/600 hist=3 policy=2.4s elapsed=85s
[decide] 2026-11-28 10:46:39 swapT_ar_e30_s50/on swap_T seed=4300049 frame=160/600 hist=3 policy=2.3s elapsed=103s
[decide] 2026-11-28 10:46:56 swapT_ar_e30_s50/on swap_T seed=4300049 frame=192/600 hist=3 policy=2.4s elapsed=120s
[decide] 2026-11-28 10:47:14 swapT_ar_e30_s50/on swap_T seed=4300049 frame=224/600 hist=3 policy=2.3s elapsed=138s
[decide] 2026-11-28 10:47:31 swapT_ar_e30_s50/on swap_T seed=4300049 frame=256/600 hist=3 policy=2.3s elapsed=156s
[decide] 2026-11-28 10:47:48 swapT_ar_e30_s50/on swap_T seed=4300049 frame=288/600 hist=3 policy=2.3s elapsed=173s
[closed-loop] 2026-11-28 10:47:51 done  swapT_ar_e30_s50/on swap_T seed=4300049 success=True targets=290/600 reward=1.0 lift=None  219s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
swapT_ar_e30_s50/on     swap_T            39     0.46  [0.32,0.61]         -    0.46      457        -        -        -    2.3
swapT_ar_e30_x16/on     swap_T            50     0.52  [0.39,0.65]         -    0.52      439        -        -        -    0.6
swapT_ar_e30_x32/on     swap_T            50     0.58  [0.44,0.71]         -    0.58      421        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x16/on       39    15       3       5       16  0.727
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x32/on       39    14       4       8       13  0.388
  swapT_ar_e30_x16/on      vs swapT_ar_e30_x32/on       50    22       4       7       17  0.549

[summary] 139 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-swapT_s50-s0.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 18:48:05 A40-d8-swapT_s50-s0: DONE  swap_T/on n=39  prog=0.00
```

## A40-d8-swapT_s50-s1 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_s50-s1.log):
```
[decide] 2026-11-28 10:47:47 swapT_ar_e30_s50/on swap_T seed=4300050 frame=224/600 hist=3 policy=2.3s elapsed=133s
[decide] 2026-11-28 10:48:04 swapT_ar_e30_s50/on swap_T seed=4300050 frame=256/600 hist=3 policy=2.3s elapsed=150s
[decide] 2026-11-28 10:48:28 swapT_ar_e30_s50/on swap_T seed=4300050 frame=288/600 hist=3 policy=2.3s elapsed=174s
[decide] 2026-11-28 10:48:46 swapT_ar_e30_s50/on swap_T seed=4300050 frame=320/600 hist=3 policy=2.5s elapsed=192s
[decide] 2026-11-28 10:49:03 swapT_ar_e30_s50/on swap_T seed=4300050 frame=352/600 hist=3 policy=2.3s elapsed=208s
[decide] 2026-11-28 10:49:20 swapT_ar_e30_s50/on swap_T seed=4300050 frame=384/600 hist=3 policy=2.3s elapsed=226s
[decide] 2026-11-28 10:49:43 swapT_ar_e30_s50/on swap_T seed=4300050 frame=416/600 hist=3 policy=2.3s elapsed=249s
[decide] 2026-11-28 10:50:05 swapT_ar_e30_s50/on swap_T seed=4300050 frame=448/600 hist=3 policy=2.4s elapsed=271s
[decide] 2026-11-28 10:50:24 swapT_ar_e30_s50/on swap_T seed=4300050 frame=480/600 hist=3 policy=2.3s elapsed=290s
[decide] 2026-11-28 10:50:42 swapT_ar_e30_s50/on swap_T seed=4300050 frame=512/600 hist=3 policy=2.5s elapsed=308s
[decide] 2026-11-28 10:51:04 swapT_ar_e30_s50/on swap_T seed=4300050 frame=544/600 hist=3 policy=2.3s elapsed=330s
[decide] 2026-11-28 10:51:22 swapT_ar_e30_s50/on swap_T seed=4300050 frame=576/600 hist=3 policy=2.3s elapsed=348s
[closed-loop] 2026-11-28 10:51:36 done  swapT_ar_e30_s50/on swap_T seed=4300050 success=False targets=600/600 reward=0.0 lift=None  399s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
swapT_ar_e30_s50/on     swap_T            43     0.44  [0.30,0.59]         -    0.44      463        -        -        -    2.4
swapT_ar_e30_x16/on     swap_T            50     0.52  [0.39,0.65]         -    0.52      439        -        -        -    0.6
swapT_ar_e30_x32/on     swap_T            50     0.58  [0.44,0.71]         -    0.58      421        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x16/on       43    16       3       6       18  0.508
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x32/on       43    15       4       9       15  0.267
  swapT_ar_e30_x16/on      vs swapT_ar_e30_x32/on       50    22       4       7       17  0.549

[summary] 143 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-swapT_s50-s1.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 18:51:52 A40-d8-swapT_s50-s1: DONE  swap_T/on n=43  prog=0.00
```

## A40-d8-swapT_s50-s2 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_s50-s2.log):
```
[decide] 2026-11-28 10:54:40 swapT_ar_e30_s50/on swap_T seed=4300051 frame=224/600 hist=3 policy=2.3s elapsed=134s
[decide] 2026-11-28 10:55:04 swapT_ar_e30_s50/on swap_T seed=4300051 frame=256/600 hist=3 policy=2.3s elapsed=158s
[decide] 2026-11-28 10:55:22 swapT_ar_e30_s50/on swap_T seed=4300051 frame=288/600 hist=3 policy=2.5s elapsed=175s
[decide] 2026-11-28 10:55:39 swapT_ar_e30_s50/on swap_T seed=4300051 frame=320/600 hist=3 policy=2.2s elapsed=193s
[decide] 2026-11-28 10:55:57 swapT_ar_e30_s50/on swap_T seed=4300051 frame=352/600 hist=3 policy=2.4s elapsed=211s
[decide] 2026-11-28 10:56:17 swapT_ar_e30_s50/on swap_T seed=4300051 frame=384/600 hist=3 policy=2.5s elapsed=231s
[decide] 2026-11-28 10:56:41 swapT_ar_e30_s50/on swap_T seed=4300051 frame=416/600 hist=3 policy=2.3s elapsed=255s
[decide] 2026-11-28 10:57:00 swapT_ar_e30_s50/on swap_T seed=4300051 frame=448/600 hist=3 policy=2.2s elapsed=274s
[decide] 2026-11-28 10:57:16 swapT_ar_e30_s50/on swap_T seed=4300051 frame=480/600 hist=3 policy=2.2s elapsed=290s
[decide] 2026-11-28 10:57:32 swapT_ar_e30_s50/on swap_T seed=4300051 frame=512/600 hist=3 policy=2.4s elapsed=306s
[decide] 2026-11-28 10:57:53 swapT_ar_e30_s50/on swap_T seed=4300051 frame=544/600 hist=3 policy=2.4s elapsed=327s
[decide] 2026-11-28 10:58:11 swapT_ar_e30_s50/on swap_T seed=4300051 frame=576/600 hist=3 policy=2.5s elapsed=344s
[closed-loop] 2026-11-28 10:58:25 done  swapT_ar_e30_s50/on swap_T seed=4300051 success=False targets=600/600 reward=0.0 lift=None  398s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
swapT_ar_e30_s50/on     swap_T            47     0.45  [0.31,0.59]         -    0.45      462        -        -        -    2.3
swapT_ar_e30_x16/on     swap_T            50     0.52  [0.39,0.65]         -    0.52      439        -        -        -    0.6
swapT_ar_e30_x32/on     swap_T            50     0.58  [0.44,0.71]         -    0.58      421        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x16/on       47    18       3       6       20  0.508
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x32/on       47    17       4      10       16  0.180
  swapT_ar_e30_x16/on      vs swapT_ar_e30_x32/on       50    22       4       7       17  0.549

[summary] 147 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-swapT_s50-s2.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 18:58:42 A40-d8-swapT_s50-s2: DONE  swap_T/on n=47  prog=0.00
```

## A40-d8-swapT_s50-s3 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_s50-s3.log):
```
[closed-loop] 2026-11-28 10:49:20 done  swapT_ar_e30_s50/on swap_T seed=4300047 success=False targets=600/600 reward=0.0 lift=None  415s
[closed-loop] 2026-11-28 10:49:20 start swapT_ar_e30_s50/on swap_T seed=4300052 target_limit=600 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_s50/on/swap_T/seed_4300052
[decide] 2026-11-28 10:50:14 swapT_ar_e30_s50/on swap_T seed=4300052 frame=0/600 hist=0 policy=2.2s elapsed=8s
[decide] 2026-11-28 10:50:32 swapT_ar_e30_s50/on swap_T seed=4300052 frame=32/600 hist=2 policy=2.5s elapsed=26s
[decide] 2026-11-28 10:50:54 swapT_ar_e30_s50/on swap_T seed=4300052 frame=64/600 hist=3 policy=2.5s elapsed=48s
[decide] 2026-11-28 10:51:15 swapT_ar_e30_s50/on swap_T seed=4300052 frame=96/600 hist=3 policy=2.5s elapsed=69s
[decide] 2026-11-28 10:51:33 swapT_ar_e30_s50/on swap_T seed=4300052 frame=128/600 hist=3 policy=2.5s elapsed=87s
[decide] 2026-11-28 10:51:52 swapT_ar_e30_s50/on swap_T seed=4300052 frame=160/600 hist=3 policy=2.5s elapsed=106s
[decide] 2026-11-28 10:52:14 swapT_ar_e30_s50/on swap_T seed=4300052 frame=192/600 hist=3 policy=2.4s elapsed=128s
[decide] 2026-11-28 10:52:32 swapT_ar_e30_s50/on swap_T seed=4300052 frame=224/600 hist=3 policy=2.4s elapsed=146s
[decide] 2026-11-28 10:52:50 swapT_ar_e30_s50/on swap_T seed=4300052 frame=256/600 hist=3 policy=2.4s elapsed=164s
[decide] 2026-11-28 10:53:07 swapT_ar_e30_s50/on swap_T seed=4300052 frame=288/600 hist=3 policy=2.4s elapsed=181s
[closed-loop] 2026-11-28 10:53:11 done  swapT_ar_e30_s50/on swap_T seed=4300052 success=True targets=293/600 reward=1.0 lift=None  231s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
swapT_ar_e30_s50/on     swap_T            45     0.47  [0.33,0.61]         -    0.47      456        -        -        -    2.4
swapT_ar_e30_x16/on     swap_T            50     0.52  [0.39,0.65]         -    0.52      439        -        -        -    0.6
swapT_ar_e30_x32/on     swap_T            50     0.58  [0.44,0.71]         -    0.58      421        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x16/on       45    18       3       6       18  0.508
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x32/on       45    17       4       9       15  0.267
  swapT_ar_e30_x16/on      vs swapT_ar_e30_x32/on       50    22       4       7       17  0.549

[summary] 145 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-swapT_s50-s3.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 18:53:27 A40-d8-swapT_s50-s3: DONE  swap_T/on n=45  prog=0.00
```

## A40-d8-swapT_s50-s4 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_s50-s4.log):
```
[closed-loop] 2026-11-28 11:07:37 done  swapT_ar_e30_s50/on swap_T seed=4300048 success=False targets=600/600 reward=0.0 lift=None  455s
[closed-loop] 2026-11-28 11:07:37 start swapT_ar_e30_s50/on swap_T seed=4300053 target_limit=600 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/swapT_ar_e30_s50/on/swap_T/seed_4300053
[decide] 2026-11-28 11:08:24 swapT_ar_e30_s50/on swap_T seed=4300053 frame=0/600 hist=0 policy=2.0s elapsed=10s
[decide] 2026-11-28 11:08:45 swapT_ar_e30_s50/on swap_T seed=4300053 frame=32/600 hist=2 policy=2.3s elapsed=31s
[decide] 2026-11-28 11:09:04 swapT_ar_e30_s50/on swap_T seed=4300053 frame=64/600 hist=3 policy=2.3s elapsed=50s
[decide] 2026-11-28 11:09:23 swapT_ar_e30_s50/on swap_T seed=4300053 frame=96/600 hist=3 policy=2.3s elapsed=70s
[decide] 2026-11-28 11:09:44 swapT_ar_e30_s50/on swap_T seed=4300053 frame=128/600 hist=3 policy=2.3s elapsed=91s
[decide] 2026-11-28 11:10:08 swapT_ar_e30_s50/on swap_T seed=4300053 frame=160/600 hist=3 policy=2.3s elapsed=114s
[decide] 2026-11-28 11:10:32 swapT_ar_e30_s50/on swap_T seed=4300053 frame=192/600 hist=3 policy=2.4s elapsed=138s
[decide] 2026-11-28 11:10:55 swapT_ar_e30_s50/on swap_T seed=4300053 frame=224/600 hist=3 policy=2.3s elapsed=161s
[decide] 2026-11-28 11:11:12 swapT_ar_e30_s50/on swap_T seed=4300053 frame=256/600 hist=3 policy=2.3s elapsed=179s
[decide] 2026-11-28 11:11:34 swapT_ar_e30_s50/on swap_T seed=4300053 frame=288/600 hist=3 policy=2.3s elapsed=201s
[closed-loop] 2026-11-28 11:11:41 done  swapT_ar_e30_s50/on swap_T seed=4300053 success=True targets=297/600 reward=1.0 lift=None  244s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
swapT_ar_e30_s50/on     swap_T            50     0.46  [0.33,0.60]         -    0.46      458        -        -        -    2.3
swapT_ar_e30_x16/on     swap_T            50     0.52  [0.39,0.65]         -    0.52      439        -        -        -    0.6
swapT_ar_e30_x32/on     swap_T            50     0.58  [0.44,0.71]         -    0.58      421        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x16/on       50    19       4       7       20  0.549
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x32/on       50    18       5      11       16  0.210
  swapT_ar_e30_x16/on      vs swapT_ar_e30_x32/on       50    22       4       7       17  0.549

[summary] 150 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-swapT_s50-s4.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'swap_T'
[queue5] 2026-11-28 19:11:58 A40-d8-swapT_s50-s4: DONE  swap_T/on n=50  prog=0.00
```

## A40-d8-swapT-report (done, attempt 3, GPU None)

failures:
```
[
 {
  "attempt": 1,
  "gpu": null,
  "time": "2026-11-28 19:12:27",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": null,
  "time": "2026-11-28 19:23:07",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 3,
  "gpu": null,
  "time": "2026-11-28 19:33:17",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT-report.log):
```
  File "/workspace/FastWAM-memory2/scripts/fullft/deed_verdict.py", line 63, in compare
    d, lo, hi = a1.paired_ci(a, b)
                ^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/fullft/a1_verdict.py", line 46, in paired_ci
    d = sum(a) / k - sum(b) / k
        ~~~~~~~^~~
ZeroDivisionError: division by zero

[queue5] 2026-11-28 19:33:16 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py report
Traceback (most recent call last):
  File "/workspace/FastWAM-memory2/scripts/fullft/diag8.py", line 90, in <module>
    main()
  File "/workspace/FastWAM-memory2/scripts/fullft/diag8.py", line 80, in main
    "settings": {k: one(k) for k in SETTINGS}, "verdict": "DESCRIBED"}
                    ^^^^^^
  File "/workspace/FastWAM-memory2/scripts/fullft/diag8.py", line 62, in one
    c50 = compare(new, ref, first)
          ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/fullft/deed_verdict.py", line 63, in compare
    d, lo, hi = a1.paired_ci(a, b)
                ^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/fullft/a1_verdict.py", line 46, in paired_ci
    d = sum(a) / k - sum(b) / k
        ~~~~~~~^~~
ZeroDivisionError: division by zero
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-swapT-report.log):
```
[pool] 2026-11-28 19:23:06 A40-d8-swapT-report: start (attempt 2/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT-report.log
[pool] 2026-11-28 19:23:07 A40-d8-swapT-report: attempt 2 failed (rc=1: Python exception); retry after 19:33 on any empty GPU

[pool] 2026-11-28 19:33:12 exec A40-d8-swapT-report GPU None 
[pool] 2026-11-28 19:33:16 A40-d8-swapT-report: start (attempt 3/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT-report.log
[pool] 2026-11-28 19:33:17 A40-d8-swapT-report: attempt 3 failed (rc=1: Python exception); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-swapT-report.md
[queue5] 2026-11-28 19:33:22 A40-d8-swapT-report: ERROR  rc=1
```

## A40-d8-swapT_x16-gate (done, attempt 3, GPU None)

failures:
```
[
 {
  "attempt": 1,
  "gpu": null,
  "time": "2026-11-28 19:33:52",
  "why": "rc=3: non-zero exit"
 },
 {
  "attempt": 2,
  "gpu": null,
  "time": "2026-11-28 19:43:57",
  "why": "rc=3: non-zero exit"
 },
 {
  "attempt": 3,
  "gpu": null,
  "time": "2026-11-28 19:54:03",
  "why": "rc=3: non-zero exit"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_x16-gate.log):
```

[queue5] 2026-11-28 19:33:52 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py gate swapT_x16
DIAG8 GATE swapT_x16: gain on 1-50 = -1 ({'scenes': 50, 'new': 26, 'ref': 27, 'D': -0.02, 'ci95': [-0.12, 0.08], 'only_new': 3, 'only_ref': 4}), below the line: no re-evaluation

[queue5] 2026-11-28 19:43:57 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py gate swapT_x16
DIAG8 GATE swapT_x16: gain on 1-50 = -1 ({'scenes': 50, 'new': 26, 'ref': 27, 'D': -0.02, 'ci95': [-0.12, 0.08], 'only_new': 3, 'only_ref': 4}), below the line: no re-evaluation

[queue5] 2026-11-28 19:54:03 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py gate swapT_x16
DIAG8 GATE swapT_x16: gain on 1-50 = -1 ({'scenes': 50, 'new': 26, 'ref': 27, 'D': -0.02, 'ci95': [-0.12, 0.08], 'only_new': 3, 'only_ref': 4}), below the line: no re-evaluation
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-swapT_x16-gate.log):
```
[pool] 2026-11-28 19:43:57 A40-d8-swapT_x16-gate: start (attempt 2/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_x16-gate.log
[pool] 2026-11-28 19:43:57 A40-d8-swapT_x16-gate: attempt 2 failed (rc=3: non-zero exit); retry after 19:53 on any empty GPU

[pool] 2026-11-28 19:53:58 exec A40-d8-swapT_x16-gate GPU None 
[pool] 2026-11-28 19:54:03 A40-d8-swapT_x16-gate: start (attempt 3/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_x16-gate.log
[pool] 2026-11-28 19:54:03 A40-d8-swapT_x16-gate: attempt 3 failed (rc=3: non-zero exit); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-swapT_x16-gate.md
[queue5] 2026-11-28 19:54:08 A40-d8-swapT_x16-gate: ERROR  rc=3
```

## A40-d8-swapT_x32-gate (done, attempt 3, GPU None)

failures:
```
[
 {
  "attempt": 1,
  "gpu": null,
  "time": "2026-11-28 19:33:52",
  "why": "rc=3: non-zero exit"
 },
 {
  "attempt": 2,
  "gpu": null,
  "time": "2026-11-28 19:43:57",
  "why": "rc=3: non-zero exit"
 },
 {
  "attempt": 3,
  "gpu": null,
  "time": "2026-11-28 19:54:03",
  "why": "rc=3: non-zero exit"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_x32-gate.log):
```

[queue5] 2026-11-28 19:33:52 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py gate swapT_x32
DIAG8 GATE swapT_x32: gain on 1-50 = 2 ({'scenes': 50, 'new': 29, 'ref': 27, 'D': 0.04, 'ci95': [-0.1, 0.18], 'only_new': 7, 'only_ref': 5}), below the line: no re-evaluation

[queue5] 2026-11-28 19:43:57 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py gate swapT_x32
DIAG8 GATE swapT_x32: gain on 1-50 = 2 ({'scenes': 50, 'new': 29, 'ref': 27, 'D': 0.04, 'ci95': [-0.1, 0.18], 'only_new': 7, 'only_ref': 5}), below the line: no re-evaluation

[queue5] 2026-11-28 19:54:03 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py gate swapT_x32
DIAG8 GATE swapT_x32: gain on 1-50 = 2 ({'scenes': 50, 'new': 29, 'ref': 27, 'D': 0.04, 'ci95': [-0.1, 0.18], 'only_new': 7, 'only_ref': 5}), below the line: no re-evaluation
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-swapT_x32-gate.log):
```
[pool] 2026-11-28 19:43:57 A40-d8-swapT_x32-gate: start (attempt 2/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_x32-gate.log
[pool] 2026-11-28 19:43:57 A40-d8-swapT_x32-gate: attempt 2 failed (rc=3: non-zero exit); retry after 19:53 on any empty GPU

[pool] 2026-11-28 19:53:58 exec A40-d8-swapT_x32-gate GPU None 
[pool] 2026-11-28 19:54:03 A40-d8-swapT_x32-gate: start (attempt 3/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_x32-gate.log
[pool] 2026-11-28 19:54:03 A40-d8-swapT_x32-gate: attempt 3 failed (rc=3: non-zero exit); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-swapT_x32-gate.md
[queue5] 2026-11-28 19:54:08 A40-d8-swapT_x32-gate: ERROR  rc=3
```

## A40-d8-swapT_s50-gate (done, attempt 3, GPU None)

failures:
```
[
 {
  "attempt": 1,
  "gpu": null,
  "time": "2026-11-28 19:33:52",
  "why": "rc=3: non-zero exit"
 },
 {
  "attempt": 2,
  "gpu": null,
  "time": "2026-11-28 19:43:57",
  "why": "rc=3: non-zero exit"
 },
 {
  "attempt": 3,
  "gpu": null,
  "time": "2026-11-28 19:54:03",
  "why": "rc=3: non-zero exit"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_s50-gate.log):
```

[queue5] 2026-11-28 19:33:52 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py gate swapT_s50
DIAG8 GATE swapT_s50: gain on 1-50 = -4 ({'scenes': 50, 'new': 23, 'ref': 27, 'D': -0.08, 'ci95': [-0.22, 0.06], 'only_new': 4, 'only_ref': 8}), below the line: no re-evaluation

[queue5] 2026-11-28 19:43:57 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py gate swapT_s50
DIAG8 GATE swapT_s50: gain on 1-50 = -4 ({'scenes': 50, 'new': 23, 'ref': 27, 'D': -0.08, 'ci95': [-0.22, 0.06], 'only_new': 4, 'only_ref': 8}), below the line: no re-evaluation

[queue5] 2026-11-28 19:54:03 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py gate swapT_s50
DIAG8 GATE swapT_s50: gain on 1-50 = -4 ({'scenes': 50, 'new': 23, 'ref': 27, 'D': -0.08, 'ci95': [-0.22, 0.06], 'only_new': 4, 'only_ref': 8}), below the line: no re-evaluation
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-swapT_s50-gate.log):
```
[pool] 2026-11-28 19:43:57 A40-d8-swapT_s50-gate: start (attempt 2/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_s50-gate.log
[pool] 2026-11-28 19:43:57 A40-d8-swapT_s50-gate: attempt 2 failed (rc=3: non-zero exit); retry after 19:53 on any empty GPU

[pool] 2026-11-28 19:53:58 exec A40-d8-swapT_s50-gate GPU None 
[pool] 2026-11-28 19:54:03 A40-d8-swapT_s50-gate: start (attempt 3/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT_s50-gate.log
[pool] 2026-11-28 19:54:03 A40-d8-swapT_s50-gate: attempt 3 failed (rc=3: non-zero exit); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-swapT_s50-gate.md
[queue5] 2026-11-28 19:54:08 A40-d8-swapT_s50-gate: ERROR  rc=3
```

## A40-d8-swapT-report100 (done, attempt 3, GPU None)

failures:
```
[
 {
  "attempt": 1,
  "gpu": null,
  "time": "2026-11-28 19:54:41",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": null,
  "time": "2026-11-28 20:05:21",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 3,
  "gpu": null,
  "time": "2026-11-28 20:16:03",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT-report100.log):
```
  File "/workspace/FastWAM-memory2/scripts/fullft/deed_verdict.py", line 63, in compare
    d, lo, hi = a1.paired_ci(a, b)
                ^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/fullft/a1_verdict.py", line 46, in paired_ci
    d = sum(a) / k - sum(b) / k
        ~~~~~~~^~~
ZeroDivisionError: division by zero

[queue5] 2026-11-28 20:16:02 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py report
Traceback (most recent call last):
  File "/workspace/FastWAM-memory2/scripts/fullft/diag8.py", line 90, in <module>
    main()
  File "/workspace/FastWAM-memory2/scripts/fullft/diag8.py", line 80, in main
    "settings": {k: one(k) for k in SETTINGS}, "verdict": "DESCRIBED"}
                    ^^^^^^
  File "/workspace/FastWAM-memory2/scripts/fullft/diag8.py", line 62, in one
    c50 = compare(new, ref, first)
          ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/fullft/deed_verdict.py", line 63, in compare
    d, lo, hi = a1.paired_ci(a, b)
                ^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/fullft/a1_verdict.py", line 46, in paired_ci
    d = sum(a) / k - sum(b) / k
        ~~~~~~~^~~
ZeroDivisionError: division by zero
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-swapT-report100.log):
```
[pool] 2026-11-28 20:05:20 A40-d8-swapT-report100: start (attempt 2/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT-report100.log
[pool] 2026-11-28 20:05:21 A40-d8-swapT-report100: attempt 2 failed (rc=1: Python exception); retry after 20:15 on any empty GPU

[pool] 2026-11-28 20:15:57 exec A40-d8-swapT-report100 GPU None 
[pool] 2026-11-28 20:16:02 A40-d8-swapT-report100: start (attempt 3/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT-report100.log
[pool] 2026-11-28 20:16:03 A40-d8-swapT-report100: attempt 3 failed (rc=1: Python exception); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-swapT-report100.md
[queue5] 2026-11-28 20:16:07 A40-d8-swapT-report100: ERROR  rc=1
```

## A40-d7c-rearr-split (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d7c-rearr-split.log):
```
v21:rearr_arprop_pw_e10: 100 episodes
   50  never pressed: block1 placed on the empty mat   e.g. seeds [4300000, 4300002, 4300004, 4300006]
   18  success   e.g. seeds [4300001, 4300011, 4300012, 4300013]
   15  stage 1, then moved block1 again (which-block error)   e.g. seeds [4300008, 4300010, 4300015, 4300025]
   13  pressed twice or more (after step 1 was complete)   e.g. seeds [4300003, 4300005, 4300022, 4300023]
    4  stage 1, second step never started (block2 never lifted)   e.g. seeds [4300018, 4300021, 4300059, 4300083]

v21:rearr_arprop_pw_e20: 100 episodes
   62  success   e.g. seeds [4300000, 4300001, 4300003, 4300004]
   24  never pressed: block1 placed on the empty mat   e.g. seeds [4300002, 4300007, 4300016, 4300017]
   13  pressed twice or more (after step 1 was complete)   e.g. seeds [4300019, 4300023, 4300034, 4300038]
    1  stage 1, then moved block1 again (which-block error)   e.g. seeds [4300010]

v21:rearr_arprop_pw_e30: 100 episodes
   45  success   e.g. seeds [4300003, 4300004, 4300006, 4300007]
   26  pressed twice or more (after step 1 was complete)   e.g. seeds [4300000, 4300002, 4300005, 4300010]
   19  stage 1, then moved block1 again (which-block error)   e.g. seeds [4300001, 4300015, 4300016, 4300019]
   10  never pressed: block1 placed on the empty mat   e.g. seeds [4300036, 4300039, 4300045, 4300049]

v21:rearr_pw_s18_e30: 100 episodes
   61  success   e.g. seeds [4300001, 4300002, 4300003, 4300005]
   22  pressed twice or more (after step 1 was complete)   e.g. seeds [4300004, 4300009, 4300012, 4300020]
   17  never pressed: block1 placed on the empty mat   e.g. seeds [4300000, 4300006, 4300007, 4300014]

REARR SPLIT REPORT: written outputs/fullft/REARR_SPLIT_D7C.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d7c-rearr-split.log):
```

[pool] 2026-11-28 20:38:40 exec A40-d7c-rearr-split GPU None 
[pool] 2026-11-28 20:38:44 A40-d7c-rearr-split: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d7c-rearr-split.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d7c-rearr-split.md
[queue5] 2026-11-28 20:50:58 A40-d7c-rearr-split: PASS  rc=0
```

## A40-d8-swapT-report2 (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT-report2.log):
```

[queue5] 2026-11-28 20:38:44 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py report
swapT_x16    1-50: 26 vs 27 of 50 (gain -1; line reached False)
swapT_x32    1-50: 29 vs 27 of 50 (gain 2; line reached False)
swapT_s50    1-50: 23 vs 27 of 50 (gain -4; line reached False)
press_x16    no paired episodes yet
press_x32    no paired episodes yet
press_s50    no paired episodes yet
rearr18_x16  no paired episodes yet
DIAG8 REPORT written /workspace/FastWAM-memory2/outputs/fullft/DIAG_V22_DIAG8.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-swapT-report2.log):
```

[pool] 2026-11-28 20:38:40 exec A40-d8-swapT-report2 GPU None 
[pool] 2026-11-28 20:38:44 A40-d8-swapT-report2: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-swapT-report2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-swapT-report2.md
[queue5] 2026-11-28 20:38:51 A40-d8-swapT-report2: PASS  rc=0
```

## A40-d8-press_x16-s0 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x16-s0.log):
```

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
press_fast_e30_x16/on   press_button      35     0.17  [0.08,0.33]         -    0.00     1318        -        -        -    0.7
press_fast_e30_x32/on   press_button      10     0.10  [0.02,0.40]         -    0.00     1419        -        -        -    0.7
swapT_ar_e30_s50/on     swap_T            50     0.46  [0.33,0.60]         -    0.46      458        -        -        -    2.3
swapT_ar_e30_x16/on     swap_T            50     0.52  [0.39,0.65]         -    0.52      439        -        -        -    0.6
swapT_ar_e30_x32/on     swap_T            50     0.58  [0.44,0.71]         -    0.58      421        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  press_fast_e30_x16/on    vs press_fast_e30_x32/on     10     0       3       1        6  0.625
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x16/on       50    19       4       7       20  0.549
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x32/on       50    18       5      11       16  0.210
  swapT_ar_e30_x16/on      vs swapT_ar_e30_x32/on       50    22       4       7       17  0.549

[summary] 195 episodes, 17 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/SUMMARY.json
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300034/ERROR.json: ace/FastWAM/resources/RMBench/envs/camera/camera.py", line 371, in _get_rgb\n    camera_rgba = camera.get_picture("Color")\nRuntimeError: vk::Queue::submit: ErrorDeviceLost\n\nterminate called after throwing an instance of \'vk::DeviceLostError\'\n  what():  vk::Device::waitIdle: ErrorDeviceLost\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300036/ERROR.json: apter.py", line 439, in main\n    official = sim_eval.load_official()\n  File "/workspace/FastWAM/scripts/memory_s1/sim_eval.py", line 67, in load_official\n    selected_render_system = sapien.render.RenderSystem(device="cuda:0")\nRuntimeError: Failed to find a supported physical device "cuda:0"\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300039/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300041/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300044/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300046/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300049/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x32/on/press_button/seed_4300025/ERROR.json: ce/FastWAM/resources/RMBench/envs/camera/camera.py", line 336, in _get_rgba\n    camera_rgba = camera.get_picture("Color")\nRuntimeError: vk::Queue::submit: ErrorDeviceLost\n\nterminate called after throwing an instance of \'vk::DeviceLostError\'\n  what():  vk::Device::waitIdle: ErrorDeviceLost\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x32/on/press_button/seed_4300026/ERROR.json: rkspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: vk::Queue::submit: ErrorDeviceLost\n\nterminate called after throwing an instance of \'vk::DeviceLostError\'\n  what():  vk::Device::waitIdle: ErrorDeviceLost\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x32/on/press_button/seed_4300030/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-press_x16-s0.log):
```

[pool] 2026-11-28 22:26:53 exec A40-d8-press_x16-s0 GPU 0 
[pool] 2026-11-28 22:26:58 A40-d8-press_x16-s0: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x16-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x16-s0.md
[queue5] 2026-11-28 23:53:26 A40-d8-press_x16-s0: DONE  press_button/on n=35 pressed=35 n1_correct=14 n2_correct=14 confirmed=35 count_correct=6 success=6 prog=0.38; errors=7
```

## A40-d8-press_x16-s1 (done, attempt 3, GPU 5)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 5,
  "time": "2026-11-28 23:51:22",
  "why": "3 episodes ended with ERROR.json (re-run retries only those)"
 },
 {
  "attempt": 2,
  "gpu": 5,
  "time": "2026-11-29 00:02:32",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 3,
  "gpu": 5,
  "time": "2026-11-29 00:14:21",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x16-s1.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-press_x16-s1.log):
```
[pool] 2026-11-29 00:01:56 A40-d8-press_x16-s1: start (attempt 2/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x16-s1.log
[pool] 2026-11-29 00:02:32 A40-d8-press_x16-s1: attempt 2 failed (rc=1: Python exception); retry after 00:12 on any empty GPU

[pool] 2026-11-29 00:13:40 exec A40-d8-press_x16-s1 GPU 5 
[pool] 2026-11-29 00:13:45 A40-d8-press_x16-s1: start (attempt 3/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x16-s1.log
[pool] 2026-11-29 00:14:21 A40-d8-press_x16-s1: attempt 3 failed (rc=1: Python exception); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x16-s1.md
[queue5] 2026-11-29 00:16:20 A40-d8-press_x16-s1: ERROR  press_button/on n=41 pressed=41 n1_correct=17 n2_correct=18 confirmed=41 count_correct=8 success=8 prog=0.40; errors=7
```

## A40-d8-press_x16-s2 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x16-s2.log):
```

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
press_fast_e30_x16/on   press_button      42     0.19  [0.10,0.33]         -    0.00     1289        -        -        -    0.7
press_fast_e30_x32/on   press_button      10     0.10  [0.02,0.40]         -    0.00     1419        -        -        -    0.7
swapT_ar_e30_s50/on     swap_T            50     0.46  [0.33,0.60]         -    0.46      458        -        -        -    2.3
swapT_ar_e30_x16/on     swap_T            50     0.52  [0.39,0.65]         -    0.52      439        -        -        -    0.6
swapT_ar_e30_x32/on     swap_T            50     0.58  [0.44,0.71]         -    0.58      421        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  press_fast_e30_x16/on    vs press_fast_e30_x32/on     10     0       3       1        6  0.625
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x16/on       50    19       4       7       20  0.549
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x32/on       50    18       5      11       16  0.210
  swapT_ar_e30_x16/on      vs swapT_ar_e30_x32/on       50    22       4       7       17  0.549

[summary] 202 episodes, 17 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/SUMMARY.json
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300034/ERROR.json: ace/FastWAM/resources/RMBench/envs/camera/camera.py", line 371, in _get_rgb\n    camera_rgba = camera.get_picture("Color")\nRuntimeError: vk::Queue::submit: ErrorDeviceLost\n\nterminate called after throwing an instance of \'vk::DeviceLostError\'\n  what():  vk::Device::waitIdle: ErrorDeviceLost\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300036/ERROR.json: apter.py", line 439, in main\n    official = sim_eval.load_official()\n  File "/workspace/FastWAM/scripts/memory_s1/sim_eval.py", line 67, in load_official\n    selected_render_system = sapien.render.RenderSystem(device="cuda:0")\nRuntimeError: Failed to find a supported physical device "cuda:0"\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300039/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300041/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300044/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300046/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300049/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x32/on/press_button/seed_4300025/ERROR.json: ce/FastWAM/resources/RMBench/envs/camera/camera.py", line 336, in _get_rgba\n    camera_rgba = camera.get_picture("Color")\nRuntimeError: vk::Queue::submit: ErrorDeviceLost\n\nterminate called after throwing an instance of \'vk::DeviceLostError\'\n  what():  vk::Device::waitIdle: ErrorDeviceLost\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x32/on/press_button/seed_4300026/ERROR.json: rkspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: vk::Queue::submit: ErrorDeviceLost\n\nterminate called after throwing an instance of \'vk::DeviceLostError\'\n  what():  vk::Device::waitIdle: ErrorDeviceLost\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x32/on/press_button/seed_4300030/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-press_x16-s2.log):
```

[pool] 2026-11-28 22:45:50 exec A40-d8-press_x16-s2 GPU 1 
[pool] 2026-11-28 22:45:55 A40-d8-press_x16-s2: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x16-s2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x16-s2.md
[queue5] 2026-11-29 00:17:28 A40-d8-press_x16-s2: DONE  press_button/on n=42 pressed=42 n1_correct=17 n2_correct=19 confirmed=42 count_correct=8 success=8 prog=0.40; errors=7
```

## A40-d8-press_x16-s3 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x16-s3.log):
```

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
press_fast_e30_x16/on   press_button      43     0.19  [0.10,0.33]         -    0.00     1294        -        -        -    0.7
press_fast_e30_x32/on   press_button      10     0.10  [0.02,0.40]         -    0.00     1419        -        -        -    0.7
swapT_ar_e30_s50/on     swap_T            50     0.46  [0.33,0.60]         -    0.46      458        -        -        -    2.3
swapT_ar_e30_x16/on     swap_T            50     0.52  [0.39,0.65]         -    0.52      439        -        -        -    0.6
swapT_ar_e30_x32/on     swap_T            50     0.58  [0.44,0.71]         -    0.58      421        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  press_fast_e30_x16/on    vs press_fast_e30_x32/on     10     0       3       1        6  0.625
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x16/on       50    19       4       7       20  0.549
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x32/on       50    18       5      11       16  0.210
  swapT_ar_e30_x16/on      vs swapT_ar_e30_x32/on       50    22       4       7       17  0.549

[summary] 203 episodes, 17 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/SUMMARY.json
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300034/ERROR.json: ace/FastWAM/resources/RMBench/envs/camera/camera.py", line 371, in _get_rgb\n    camera_rgba = camera.get_picture("Color")\nRuntimeError: vk::Queue::submit: ErrorDeviceLost\n\nterminate called after throwing an instance of \'vk::DeviceLostError\'\n  what():  vk::Device::waitIdle: ErrorDeviceLost\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300036/ERROR.json: apter.py", line 439, in main\n    official = sim_eval.load_official()\n  File "/workspace/FastWAM/scripts/memory_s1/sim_eval.py", line 67, in load_official\n    selected_render_system = sapien.render.RenderSystem(device="cuda:0")\nRuntimeError: Failed to find a supported physical device "cuda:0"\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300039/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300041/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300044/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300046/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300049/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x32/on/press_button/seed_4300025/ERROR.json: ce/FastWAM/resources/RMBench/envs/camera/camera.py", line 336, in _get_rgba\n    camera_rgba = camera.get_picture("Color")\nRuntimeError: vk::Queue::submit: ErrorDeviceLost\n\nterminate called after throwing an instance of \'vk::DeviceLostError\'\n  what():  vk::Device::waitIdle: ErrorDeviceLost\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x32/on/press_button/seed_4300026/ERROR.json: rkspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: vk::Queue::submit: ErrorDeviceLost\n\nterminate called after throwing an instance of \'vk::DeviceLostError\'\n  what():  vk::Device::waitIdle: ErrorDeviceLost\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x32/on/press_button/seed_4300030/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-press_x16-s3.log):
```

[pool] 2026-11-28 22:45:50 exec A40-d8-press_x16-s3 GPU 3 
[pool] 2026-11-28 22:45:55 A40-d8-press_x16-s3: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x16-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x16-s3.md
[queue5] 2026-11-29 00:23:24 A40-d8-press_x16-s3: DONE  press_button/on n=43 pressed=43 n1_correct=17 n2_correct=19 confirmed=43 count_correct=8 success=8 prog=0.39; errors=7
```

## A40-d8-press_x16-s4 (done, attempt 3, GPU 6)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 4,
  "time": "2026-11-28 23:51:25",
  "why": "4 episodes ended with ERROR.json (re-run retries only those)"
 },
 {
  "attempt": 2,
  "gpu": 6,
  "time": "2026-11-29 00:02:32",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 3,
  "gpu": 6,
  "time": "2026-11-29 00:14:20",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x16-s4.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-press_x16-s4.log):
```
[pool] 2026-11-29 00:01:56 A40-d8-press_x16-s4: start (attempt 2/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x16-s4.log
[pool] 2026-11-29 00:02:32 A40-d8-press_x16-s4: attempt 2 failed (rc=1: Python exception); retry after 00:12 on any empty GPU

[pool] 2026-11-29 00:13:40 exec A40-d8-press_x16-s4 GPU 6 
[pool] 2026-11-29 00:13:45 A40-d8-press_x16-s4: start (attempt 3/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x16-s4.log
[pool] 2026-11-29 00:14:20 A40-d8-press_x16-s4: attempt 3 failed (rc=1: Python exception); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x16-s4.md
[queue5] 2026-11-29 00:16:20 A40-d8-press_x16-s4: ERROR  press_button/on n=41 pressed=41 n1_correct=17 n2_correct=18 confirmed=41 count_correct=8 success=8 prog=0.40; errors=7
```

## A40-d8-press_x32-s0 (done, attempt 3, GPU 5)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 6,
  "time": "2026-11-28 23:48:02",
  "why": "5 episodes ended with ERROR.json (re-run retries only those)"
 },
 {
  "attempt": 2,
  "gpu": 5,
  "time": "2026-11-29 00:00:09",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 3,
  "gpu": 5,
  "time": "2026-11-29 00:11:57",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x32-s0.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-press_x32-s0.log):
```
[pool] 2026-11-28 23:59:34 A40-d8-press_x32-s0: start (attempt 2/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x32-s0.log
[pool] 2026-11-29 00:00:09 A40-d8-press_x32-s0: attempt 2 failed (rc=1: Python exception); retry after 00:10 on any empty GPU

[pool] 2026-11-29 00:11:18 exec A40-d8-press_x32-s0 GPU 5 
[pool] 2026-11-29 00:11:23 A40-d8-press_x32-s0: start (attempt 3/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x32-s0.log
[pool] 2026-11-29 00:11:57 A40-d8-press_x32-s0: attempt 3 failed (rc=1: Python exception); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x32-s0.md
[queue5] 2026-11-29 00:12:34 A40-d8-press_x32-s0: ERROR  press_button/on n=10 pressed=10 n1_correct=5 n2_correct=5 confirmed=10 count_correct=1 success=1 prog=0.36; errors=10
```

## A40-d8-press_x32-s1 (done, attempt 3, GPU 5)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 7,
  "time": "2026-11-28 23:42:51",
  "why": "5 episodes ended with ERROR.json (re-run retries only those)"
 },
 {
  "attempt": 2,
  "gpu": 4,
  "time": "2026-11-28 23:53:40",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 3,
  "gpu": 5,
  "time": "2026-11-29 00:04:54",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x32-s1.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-press_x32-s1.log):
```
[pool] 2026-11-28 23:53:04 A40-d8-press_x32-s1: start (attempt 2/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x32-s1.log
[pool] 2026-11-28 23:53:40 A40-d8-press_x32-s1: attempt 2 failed (rc=1: Python exception); retry after 00:03 on any empty GPU

[pool] 2026-11-29 00:04:13 exec A40-d8-press_x32-s1 GPU 5 
[pool] 2026-11-29 00:04:18 A40-d8-press_x32-s1: start (attempt 3/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x32-s1.log
[pool] 2026-11-29 00:04:54 A40-d8-press_x32-s1: attempt 3 failed (rc=1: Python exception); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x32-s1.md
[queue5] 2026-11-29 00:05:34 A40-d8-press_x32-s1: ERROR  press_button/on n=10 pressed=10 n1_correct=5 n2_correct=5 confirmed=10 count_correct=1 success=1 prog=0.36; errors=10
```

## A40-d8-press_x32-s2 (done, attempt 3, GPU 5)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 7,
  "time": "2026-11-28 23:45:06",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 4,
  "time": "2026-11-28 23:56:03",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 3,
  "gpu": 5,
  "time": "2026-11-29 00:07:17",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x32-s2.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-press_x32-s2.log):
```
[pool] 2026-11-28 23:55:25 A40-d8-press_x32-s2: start (attempt 2/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x32-s2.log
[pool] 2026-11-28 23:56:03 A40-d8-press_x32-s2: attempt 2 failed (rc=1: Python exception); retry after 00:06 on any empty GPU

[pool] 2026-11-29 00:06:35 exec A40-d8-press_x32-s2 GPU 5 
[pool] 2026-11-29 00:06:40 A40-d8-press_x32-s2: start (attempt 3/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x32-s2.log
[pool] 2026-11-29 00:07:17 A40-d8-press_x32-s2: attempt 3 failed (rc=1: Python exception); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x32-s2.md
[queue5] 2026-11-29 00:07:53 A40-d8-press_x32-s2: ERROR  press_button/on n=10 pressed=10 n1_correct=5 n2_correct=5 confirmed=10 count_correct=1 success=1 prog=0.36; errors=10
```

## A40-d8-press_x32-s3 (done, attempt 3, GPU 6)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 7,
  "time": "2026-11-28 23:47:43",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 6,
  "time": "2026-11-29 00:00:10",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 3,
  "gpu": 6,
  "time": "2026-11-29 00:11:57",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x32-s3.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-press_x32-s3.log):
```
[pool] 2026-11-28 23:59:34 A40-d8-press_x32-s3: start (attempt 2/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x32-s3.log
[pool] 2026-11-29 00:00:10 A40-d8-press_x32-s3: attempt 2 failed (rc=1: Python exception); retry after 00:10 on any empty GPU

[pool] 2026-11-29 00:11:18 exec A40-d8-press_x32-s3 GPU 6 
[pool] 2026-11-29 00:11:23 A40-d8-press_x32-s3: start (attempt 3/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x32-s3.log
[pool] 2026-11-29 00:11:57 A40-d8-press_x32-s3: attempt 3 failed (rc=1: Python exception); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x32-s3.md
[queue5] 2026-11-29 00:12:35 A40-d8-press_x32-s3: ERROR  press_button/on n=10 pressed=10 n1_correct=5 n2_correct=5 confirmed=10 count_correct=1 success=1 prog=0.36; errors=10
```

## A40-d8-press_x32-s4 (done, attempt 3, GPU 7)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 6,
  "time": "2026-11-28 23:50:36",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 7,
  "time": "2026-11-29 00:02:32",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 3,
  "gpu": 7,
  "time": "2026-11-29 00:14:21",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x32-s4.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-press_x32-s4.log):
```
[pool] 2026-11-29 00:01:56 A40-d8-press_x32-s4: start (attempt 2/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x32-s4.log
[pool] 2026-11-29 00:02:32 A40-d8-press_x32-s4: attempt 2 failed (rc=1: Python exception); retry after 00:12 on any empty GPU

[pool] 2026-11-29 00:13:40 exec A40-d8-press_x32-s4 GPU 7 
[pool] 2026-11-29 00:13:45 A40-d8-press_x32-s4: start (attempt 3/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x32-s4.log
[pool] 2026-11-29 00:14:21 A40-d8-press_x32-s4: attempt 3 failed (rc=1: Python exception); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x32-s4.md
[queue5] 2026-11-29 00:14:58 A40-d8-press_x32-s4: ERROR  press_button/on n=10 pressed=10 n1_correct=5 n2_correct=5 confirmed=10 count_correct=1 success=1 prog=0.36; errors=10
```

## A40-d8-press_s50-s0 (done, attempt 3, GPU 5)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 7,
  "time": "2026-11-28 23:50:36",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 6,
  "time": "2026-11-29 00:04:55",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 3,
  "gpu": 5,
  "time": "2026-11-29 00:16:43",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_s50-s0.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-press_s50-s0.log):
```
[pool] 2026-11-29 00:04:18 A40-d8-press_s50-s0: start (attempt 2/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_s50-s0.log
[pool] 2026-11-29 00:04:55 A40-d8-press_s50-s0: attempt 2 failed (rc=1: Python exception); retry after 00:14 on any empty GPU

[pool] 2026-11-29 00:16:03 exec A40-d8-press_s50-s0 GPU 5 
[pool] 2026-11-29 00:16:08 A40-d8-press_s50-s0: start (attempt 3/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_s50-s0.log
[pool] 2026-11-29 00:16:43 A40-d8-press_s50-s0: attempt 3 failed (rc=1: Python exception); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_s50-s0.md
[queue5] 2026-11-29 00:16:48 A40-d8-press_s50-s0: ERROR  
```

## A40-d8-press_s50-s1 (done, attempt 3, GPU 6)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 6,
  "time": "2026-11-28 23:53:04",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 7,
  "time": "2026-11-29 00:04:54",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 3,
  "gpu": 6,
  "time": "2026-11-29 00:16:43",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_s50-s1.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-press_s50-s1.log):
```
[pool] 2026-11-29 00:04:18 A40-d8-press_s50-s1: start (attempt 2/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_s50-s1.log
[pool] 2026-11-29 00:04:54 A40-d8-press_s50-s1: attempt 2 failed (rc=1: Python exception); retry after 00:14 on any empty GPU

[pool] 2026-11-29 00:16:03 exec A40-d8-press_s50-s1 GPU 6 
[pool] 2026-11-29 00:16:08 A40-d8-press_s50-s1: start (attempt 3/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_s50-s1.log
[pool] 2026-11-29 00:16:43 A40-d8-press_s50-s1: attempt 3 failed (rc=1: Python exception); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_s50-s1.md
[queue5] 2026-11-29 00:16:48 A40-d8-press_s50-s1: ERROR  
```

## A40-d8-press_s50-s2 (done, attempt 3, GPU 7)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 7,
  "time": "2026-11-28 23:53:04",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 4,
  "time": "2026-11-29 00:05:30",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 3,
  "gpu": 7,
  "time": "2026-11-29 00:16:42",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_s50-s2.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-press_s50-s2.log):
```
[pool] 2026-11-29 00:04:55 A40-d8-press_s50-s2: start (attempt 2/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_s50-s2.log
[pool] 2026-11-29 00:05:30 A40-d8-press_s50-s2: attempt 2 failed (rc=1: Python exception); retry after 00:15 on any empty GPU

[pool] 2026-11-29 00:16:03 exec A40-d8-press_s50-s2 GPU 7 
[pool] 2026-11-29 00:16:08 A40-d8-press_s50-s2: start (attempt 3/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_s50-s2.log
[pool] 2026-11-29 00:16:42 A40-d8-press_s50-s2: attempt 3 failed (rc=1: Python exception); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_s50-s2.md
[queue5] 2026-11-29 00:16:48 A40-d8-press_s50-s2: ERROR  
```

## A40-d8-press_s50-s3 (done, attempt 3, GPU 5)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 5,
  "time": "2026-11-28 23:53:41",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 6,
  "time": "2026-11-29 00:07:14",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 3,
  "gpu": 5,
  "time": "2026-11-29 00:19:07",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_s50-s3.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-press_s50-s3.log):
```
[pool] 2026-11-29 00:06:40 A40-d8-press_s50-s3: start (attempt 2/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_s50-s3.log
[pool] 2026-11-29 00:07:14 A40-d8-press_s50-s3: attempt 2 failed (rc=1: Python exception); retry after 00:17 on any empty GPU

[pool] 2026-11-29 00:18:26 exec A40-d8-press_s50-s3 GPU 5 
[pool] 2026-11-29 00:18:31 A40-d8-press_s50-s3: start (attempt 3/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_s50-s3.log
[pool] 2026-11-29 00:19:07 A40-d8-press_s50-s3: attempt 3 failed (rc=1: Python exception); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_s50-s3.md
[queue5] 2026-11-29 00:19:13 A40-d8-press_s50-s3: ERROR  
```

## A40-d8-press_s50-s4 (done, attempt 3, GPU 6)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 6,
  "time": "2026-11-28 23:55:29",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 7,
  "time": "2026-11-29 00:07:15",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 3,
  "gpu": 6,
  "time": "2026-11-29 00:19:06",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_s50-s4.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-press_s50-s4.log):
```
[pool] 2026-11-29 00:06:40 A40-d8-press_s50-s4: start (attempt 2/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_s50-s4.log
[pool] 2026-11-29 00:07:15 A40-d8-press_s50-s4: attempt 2 failed (rc=1: Python exception); retry after 00:17 on any empty GPU

[pool] 2026-11-29 00:18:26 exec A40-d8-press_s50-s4 GPU 6 
[pool] 2026-11-29 00:18:31 A40-d8-press_s50-s4: start (attempt 3/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_s50-s4.log
[pool] 2026-11-29 00:19:06 A40-d8-press_s50-s4: attempt 3 failed (rc=1: Python exception); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_s50-s4.md
[queue5] 2026-11-29 00:19:12 A40-d8-press_s50-s4: ERROR  
```

## A40-d8-press-report (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press-report.log):
```

[queue5] 2026-11-29 00:22:04 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py report
swapT_x16    1-50: 26 vs 27 of 50 (gain -1; line reached False)
swapT_x32    1-50: 29 vs 27 of 50 (gain 2; line reached False)
swapT_s50    1-50: 23 vs 27 of 50 (gain -4; line reached False)
press_x16    1-50: 8 vs 13 of 43 (gain -5; line reached False)
press_x32    1-50: 1 vs 3 of 10 (gain -2; line reached False)
press_s50    no paired episodes yet
rearr18_x16  no paired episodes yet
DIAG8 REPORT written /workspace/FastWAM-memory2/outputs/fullft/DIAG_V22_DIAG8.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-press-report.log):
```

[pool] 2026-11-29 00:21:59 exec A40-d8-press-report GPU None 
[pool] 2026-11-29 00:22:04 A40-d8-press-report: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press-report.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press-report.md
[queue5] 2026-11-29 00:22:11 A40-d8-press-report: PASS  rc=0
```

## A40-d8-press_x16-gate (done, attempt 3, GPU None)

failures:
```
[
 {
  "attempt": 1,
  "gpu": null,
  "time": "2026-11-29 00:22:40",
  "why": "rc=3: non-zero exit"
 },
 {
  "attempt": 2,
  "gpu": null,
  "time": "2026-11-29 00:33:19",
  "why": "rc=3: non-zero exit"
 },
 {
  "attempt": 3,
  "gpu": null,
  "time": "2026-11-29 00:43:58",
  "why": "rc=3: non-zero exit"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x16-gate.log):
```

[queue5] 2026-11-29 00:22:40 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py gate press_x16
DIAG8 GATE press_x16: gain on 1-50 = -5 ({'scenes': 43, 'new': 8, 'ref': 13, 'D': -0.1163, 'ci95': [-0.2791, 0.0465], 'only_new': 4, 'only_ref': 9}), below the line: no re-evaluation

[queue5] 2026-11-29 00:33:19 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py gate press_x16
DIAG8 GATE press_x16: gain on 1-50 = -5 ({'scenes': 43, 'new': 8, 'ref': 13, 'D': -0.1163, 'ci95': [-0.2791, 0.0465], 'only_new': 4, 'only_ref': 9}), below the line: no re-evaluation

[queue5] 2026-11-29 00:43:58 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py gate press_x16
DIAG8 GATE press_x16: gain on 1-50 = -5 ({'scenes': 43, 'new': 8, 'ref': 13, 'D': -0.1163, 'ci95': [-0.2791, 0.0465], 'only_new': 4, 'only_ref': 9}), below the line: no re-evaluation
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-press_x16-gate.log):
```
[pool] 2026-11-29 00:33:19 A40-d8-press_x16-gate: start (attempt 2/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x16-gate.log
[pool] 2026-11-29 00:33:19 A40-d8-press_x16-gate: attempt 2 failed (rc=3: non-zero exit); retry after 00:43 on any empty GPU

[pool] 2026-11-29 00:43:53 exec A40-d8-press_x16-gate GPU None 
[pool] 2026-11-29 00:43:58 A40-d8-press_x16-gate: start (attempt 3/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x16-gate.log
[pool] 2026-11-29 00:43:58 A40-d8-press_x16-gate: attempt 3 failed (rc=3: non-zero exit); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x16-gate.md
[queue5] 2026-11-29 00:44:04 A40-d8-press_x16-gate: ERROR  rc=3
```

## A40-d8-press_x32-gate (done, attempt 3, GPU None)

failures:
```
[
 {
  "attempt": 1,
  "gpu": null,
  "time": "2026-11-29 00:22:40",
  "why": "rc=3: non-zero exit"
 },
 {
  "attempt": 2,
  "gpu": null,
  "time": "2026-11-29 00:33:19",
  "why": "rc=3: non-zero exit"
 },
 {
  "attempt": 3,
  "gpu": null,
  "time": "2026-11-29 00:43:58",
  "why": "rc=3: non-zero exit"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x32-gate.log):
```

[queue5] 2026-11-29 00:22:40 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py gate press_x32
DIAG8 GATE press_x32: gain on 1-50 = -2 ({'scenes': 10, 'new': 1, 'ref': 3, 'D': -0.2, 'ci95': [-0.6, 0.2], 'only_new': 1, 'only_ref': 3}), below the line: no re-evaluation

[queue5] 2026-11-29 00:33:19 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py gate press_x32
DIAG8 GATE press_x32: gain on 1-50 = -2 ({'scenes': 10, 'new': 1, 'ref': 3, 'D': -0.2, 'ci95': [-0.6, 0.2], 'only_new': 1, 'only_ref': 3}), below the line: no re-evaluation

[queue5] 2026-11-29 00:43:58 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py gate press_x32
DIAG8 GATE press_x32: gain on 1-50 = -2 ({'scenes': 10, 'new': 1, 'ref': 3, 'D': -0.2, 'ci95': [-0.6, 0.2], 'only_new': 1, 'only_ref': 3}), below the line: no re-evaluation
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-press_x32-gate.log):
```
[pool] 2026-11-29 00:33:19 A40-d8-press_x32-gate: start (attempt 2/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x32-gate.log
[pool] 2026-11-29 00:33:19 A40-d8-press_x32-gate: attempt 2 failed (rc=3: non-zero exit); retry after 00:43 on any empty GPU

[pool] 2026-11-29 00:43:53 exec A40-d8-press_x32-gate GPU None 
[pool] 2026-11-29 00:43:58 A40-d8-press_x32-gate: start (attempt 3/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_x32-gate.log
[pool] 2026-11-29 00:43:58 A40-d8-press_x32-gate: attempt 3 failed (rc=3: non-zero exit); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x32-gate.md
[queue5] 2026-11-29 00:44:03 A40-d8-press_x32-gate: ERROR  rc=3
```

## A40-d8-press_s50-gate (done, attempt 3, GPU None)

failures:
```
[
 {
  "attempt": 1,
  "gpu": null,
  "time": "2026-11-29 00:22:40",
  "why": "rc=3: non-zero exit"
 },
 {
  "attempt": 2,
  "gpu": null,
  "time": "2026-11-29 00:33:19",
  "why": "rc=3: non-zero exit"
 },
 {
  "attempt": 3,
  "gpu": null,
  "time": "2026-11-29 00:43:58",
  "why": "rc=3: non-zero exit"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_s50-gate.log):
```

[queue5] 2026-11-29 00:22:40 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py gate press_s50
DIAG8 GATE press_s50: gain on 1-50 = None (None), below the line: no re-evaluation

[queue5] 2026-11-29 00:33:19 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py gate press_s50
DIAG8 GATE press_s50: gain on 1-50 = None (None), below the line: no re-evaluation

[queue5] 2026-11-29 00:43:58 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py gate press_s50
DIAG8 GATE press_s50: gain on 1-50 = None (None), below the line: no re-evaluation
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-press_s50-gate.log):
```
[pool] 2026-11-29 00:33:19 A40-d8-press_s50-gate: start (attempt 2/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_s50-gate.log
[pool] 2026-11-29 00:33:19 A40-d8-press_s50-gate: attempt 2 failed (rc=3: non-zero exit); retry after 00:43 on any empty GPU

[pool] 2026-11-29 00:43:53 exec A40-d8-press_s50-gate GPU None 
[pool] 2026-11-29 00:43:58 A40-d8-press_s50-gate: start (attempt 3/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press_s50-gate.log
[pool] 2026-11-29 00:43:58 A40-d8-press_s50-gate: attempt 3 failed (rc=3: non-zero exit); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_s50-gate.md
[queue5] 2026-11-29 00:44:03 A40-d8-press_s50-gate: ERROR  rc=3
```

## A40-d8-press-report100 (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press-report100.log):
```

[queue5] 2026-11-29 00:44:35 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py report
swapT_x16    1-50: 26 vs 27 of 50 (gain -1; line reached False)
swapT_x32    1-50: 29 vs 27 of 50 (gain 2; line reached False)
swapT_s50    1-50: 23 vs 27 of 50 (gain -4; line reached False)
press_x16    1-50: 8 vs 13 of 43 (gain -5; line reached False)
press_x32    1-50: 1 vs 3 of 10 (gain -2; line reached False)
press_s50    no paired episodes yet
rearr18_x16  no paired episodes yet
DIAG8 REPORT written /workspace/FastWAM-memory2/outputs/fullft/DIAG_V22_DIAG8.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-press-report100.log):
```

[pool] 2026-11-29 00:44:29 exec A40-d8-press-report100 GPU None 
[pool] 2026-11-29 00:44:35 A40-d8-press-report100: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-press-report100.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press-report100.md
[queue5] 2026-11-29 00:44:42 A40-d8-press-report100: PASS  rc=0
```

## A40-d8r-press_x16-s1 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8r-press_x16-s1.log):
```

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
press_fast_e30_x16/on   press_button      46     0.17  [0.09,0.31]         -    0.00     1307        -        -        -    0.7
press_fast_e30_x32/on   press_button      10     0.10  [0.02,0.40]         -    0.00     1419        -        -        -    0.7
swapT_ar_e30_s50/on     swap_T            50     0.46  [0.33,0.60]         -    0.46      458        -        -        -    2.3
swapT_ar_e30_x16/on     swap_T            50     0.52  [0.39,0.65]         -    0.52      439        -        -        -    0.6
swapT_ar_e30_x32/on     swap_T            50     0.58  [0.44,0.71]         -    0.58      421        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  press_fast_e30_x16/on    vs press_fast_e30_x32/on     10     0       3       1        6  0.625
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x16/on       50    19       4       7       20  0.549
  swapT_ar_e30_s50/on      vs swapT_ar_e30_x32/on       50    18       5      11       16  0.210
  swapT_ar_e30_x16/on      vs swapT_ar_e30_x32/on       50    22       4       7       17  0.549

[summary] 206 episodes, 14 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/SUMMARY.json
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300034/ERROR.json: ace/FastWAM/resources/RMBench/envs/camera/camera.py", line 371, in _get_rgb\n    camera_rgba = camera.get_picture("Color")\nRuntimeError: vk::Queue::submit: ErrorDeviceLost\n\nterminate called after throwing an instance of \'vk::DeviceLostError\'\n  what():  vk::Device::waitIdle: ErrorDeviceLost\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300039/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300044/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x16/on/press_button/seed_4300049/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x32/on/press_button/seed_4300025/ERROR.json: ce/FastWAM/resources/RMBench/envs/camera/camera.py", line 336, in _get_rgba\n    camera_rgba = camera.get_picture("Color")\nRuntimeError: vk::Queue::submit: ErrorDeviceLost\n\nterminate called after throwing an instance of \'vk::DeviceLostError\'\n  what():  vk::Device::waitIdle: ErrorDeviceLost\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x32/on/press_button/seed_4300026/ERROR.json: rkspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: vk::Queue::submit: ErrorDeviceLost\n\nterminate called after throwing an instance of \'vk::DeviceLostError\'\n  what():  vk::Device::waitIdle: ErrorDeviceLost\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x32/on/press_button/seed_4300030/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x32/on/press_button/seed_4300031/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x32/on/press_button/seed_4300035/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/d8/press_fast_e30_x32/on/press_button/seed_4300036/ERROR.json: fused-env/lib/python3.10/site-packages/curobo/types/math.py", line 215, in from_list\n    position = torch.as_tensor(\n  File "/opt/rmbench-fused-env/lib/python3.10/site-packages/torch/cuda/__init__.py", line 319, in _lazy_init\n    torch._C._cuda_init()\nRuntimeError: No CUDA GPUs are available\n')
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8r-press_x16-s1.log):
```

[pool] 2026-11-29 01:07:44 exec A40-d8r-press_x16-s1 GPU 0 
[pool] 2026-11-29 01:08:09 A40-d8r-press_x16-s1: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8r-press_x16-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8r-press_x16-s1.md
[queue5] 2026-11-29 01:41:01 A40-d8r-press_x16-s1: DONE  press_button/on n=46 pressed=46 n1_correct=18 n2_correct=19 confirmed=46 count_correct=8 success=8 prog=0.38; errors=4
```

## A40-d8-rearr18_x16-s0 (done, attempt 3, GPU 5)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 7,
  "time": "2026-11-28 23:57:52",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 5,
  "time": "2026-11-29 00:09:35",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 3,
  "gpu": 5,
  "time": "2026-11-29 00:21:30",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-rearr18_x16-s0.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-rearr18_x16-s0.log):
```
[pool] 2026-11-29 00:09:01 A40-d8-rearr18_x16-s0: start (attempt 2/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-rearr18_x16-s0.log
[pool] 2026-11-29 00:09:35 A40-d8-rearr18_x16-s0: attempt 2 failed (rc=1: Python exception); retry after 00:19 on any empty GPU

[pool] 2026-11-29 00:20:48 exec A40-d8-rearr18_x16-s0 GPU 5 
[pool] 2026-11-29 00:20:54 A40-d8-rearr18_x16-s0: start (attempt 3/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-rearr18_x16-s0.log
[pool] 2026-11-29 00:21:30 A40-d8-rearr18_x16-s0: attempt 3 failed (rc=1: Python exception); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-rearr18_x16-s0.md
[queue5] 2026-11-29 00:21:35 A40-d8-rearr18_x16-s0: ERROR  
```

## A40-d8-rearr18_x16-s1 (done, attempt 3, GPU 6)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 5,
  "time": "2026-11-28 23:57:53",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 6,
  "time": "2026-11-29 00:09:36",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 3,
  "gpu": 6,
  "time": "2026-11-29 00:21:29",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-rearr18_x16-s1.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-rearr18_x16-s1.log):
```
[pool] 2026-11-29 00:09:01 A40-d8-rearr18_x16-s1: start (attempt 2/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-rearr18_x16-s1.log
[pool] 2026-11-29 00:09:36 A40-d8-rearr18_x16-s1: attempt 2 failed (rc=1: Python exception); retry after 00:19 on any empty GPU

[pool] 2026-11-29 00:20:48 exec A40-d8-rearr18_x16-s1 GPU 6 
[pool] 2026-11-29 00:20:54 A40-d8-rearr18_x16-s1: start (attempt 3/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-rearr18_x16-s1.log
[pool] 2026-11-29 00:21:29 A40-d8-rearr18_x16-s1: attempt 3 failed (rc=1: Python exception); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-rearr18_x16-s1.md
[queue5] 2026-11-29 00:21:34 A40-d8-rearr18_x16-s1: ERROR  
```

## A40-d8-rearr18_x16-s2 (done, attempt 3, GPU 7)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 6,
  "time": "2026-11-28 23:57:52",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 7,
  "time": "2026-11-29 00:09:36",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 3,
  "gpu": 7,
  "time": "2026-11-29 00:21:28",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-rearr18_x16-s2.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-rearr18_x16-s2.log):
```
[pool] 2026-11-29 00:09:01 A40-d8-rearr18_x16-s2: start (attempt 2/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-rearr18_x16-s2.log
[pool] 2026-11-29 00:09:36 A40-d8-rearr18_x16-s2: attempt 2 failed (rc=1: Python exception); retry after 00:19 on any empty GPU

[pool] 2026-11-29 00:20:48 exec A40-d8-rearr18_x16-s2 GPU 7 
[pool] 2026-11-29 00:20:54 A40-d8-rearr18_x16-s2: start (attempt 3/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-rearr18_x16-s2.log
[pool] 2026-11-29 00:21:28 A40-d8-rearr18_x16-s2: attempt 3 failed (rc=1: Python exception); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-rearr18_x16-s2.md
[queue5] 2026-11-29 00:21:33 A40-d8-rearr18_x16-s2: ERROR  
```

## A40-d8-rearr18_x16-s3 (done, attempt 3, GPU 4)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 4,
  "time": "2026-11-28 23:58:23",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 4,
  "time": "2026-11-29 00:10:10",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 3,
  "gpu": 4,
  "time": "2026-11-29 00:22:03",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-rearr18_x16-s3.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-rearr18_x16-s3.log):
```
[pool] 2026-11-29 00:09:37 A40-d8-rearr18_x16-s3: start (attempt 2/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-rearr18_x16-s3.log
[pool] 2026-11-29 00:10:10 A40-d8-rearr18_x16-s3: attempt 2 failed (rc=1: Python exception); retry after 00:20 on any empty GPU

[pool] 2026-11-29 00:21:24 exec A40-d8-rearr18_x16-s3 GPU 4 
[pool] 2026-11-29 00:21:29 A40-d8-rearr18_x16-s3: start (attempt 3/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-rearr18_x16-s3.log
[pool] 2026-11-29 00:22:03 A40-d8-rearr18_x16-s3: attempt 3 failed (rc=1: Python exception); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-rearr18_x16-s3.md
[queue5] 2026-11-29 00:22:09 A40-d8-rearr18_x16-s3: ERROR  
```

## A40-d8-rearr18_x16-s4 (done, attempt 3, GPU 5)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 7,
  "time": "2026-11-29 00:00:11",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 7,
  "time": "2026-11-29 00:11:58",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 3,
  "gpu": 5,
  "time": "2026-11-29 00:23:50",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-rearr18_x16-s4.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-rearr18_x16-s4.log):
```
[pool] 2026-11-29 00:11:23 A40-d8-rearr18_x16-s4: start (attempt 2/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-rearr18_x16-s4.log
[pool] 2026-11-29 00:11:58 A40-d8-rearr18_x16-s4: attempt 2 failed (rc=1: Python exception); retry after 00:21 on any empty GPU

[pool] 2026-11-29 00:23:10 exec A40-d8-rearr18_x16-s4 GPU 5 
[pool] 2026-11-29 00:23:15 A40-d8-rearr18_x16-s4: start (attempt 3/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-rearr18_x16-s4.log
[pool] 2026-11-29 00:23:50 A40-d8-rearr18_x16-s4: attempt 3 failed (rc=1: Python exception); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-rearr18_x16-s4.md
[queue5] 2026-11-29 00:23:55 A40-d8-rearr18_x16-s4: ERROR  
```

## A40-d8-rearr18-report (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-rearr18-report.log):
```

[queue5] 2026-11-29 00:24:27 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py report
swapT_x16    1-50: 26 vs 27 of 50 (gain -1; line reached False)
swapT_x32    1-50: 29 vs 27 of 50 (gain 2; line reached False)
swapT_s50    1-50: 23 vs 27 of 50 (gain -4; line reached False)
press_x16    1-50: 8 vs 13 of 43 (gain -5; line reached False)
press_x32    1-50: 1 vs 3 of 10 (gain -2; line reached False)
press_s50    no paired episodes yet
rearr18_x16  no paired episodes yet
DIAG8 REPORT written /workspace/FastWAM-memory2/outputs/fullft/DIAG_V22_DIAG8.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-rearr18-report.log):
```

[pool] 2026-11-29 00:24:22 exec A40-d8-rearr18-report GPU None 
[pool] 2026-11-29 00:24:27 A40-d8-rearr18-report: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-rearr18-report.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-rearr18-report.md
[queue5] 2026-11-29 00:24:33 A40-d8-rearr18-report: PASS  rc=0
```

## A40-d8-rearr18_x16-gate (done, attempt 3, GPU None)

failures:
```
[
 {
  "attempt": 1,
  "gpu": null,
  "time": "2026-11-29 00:25:02",
  "why": "rc=3: non-zero exit"
 },
 {
  "attempt": 2,
  "gpu": null,
  "time": "2026-11-29 00:35:42",
  "why": "rc=3: non-zero exit"
 },
 {
  "attempt": 3,
  "gpu": null,
  "time": "2026-11-29 00:46:22",
  "why": "rc=3: non-zero exit"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-rearr18_x16-gate.log):
```

[queue5] 2026-11-29 00:25:02 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py gate rearr18_x16
DIAG8 GATE rearr18_x16: gain on 1-50 = None (None), below the line: no re-evaluation

[queue5] 2026-11-29 00:35:42 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py gate rearr18_x16
DIAG8 GATE rearr18_x16: gain on 1-50 = None (None), below the line: no re-evaluation

[queue5] 2026-11-29 00:46:22 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py gate rearr18_x16
DIAG8 GATE rearr18_x16: gain on 1-50 = None (None), below the line: no re-evaluation
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-rearr18_x16-gate.log):
```
[pool] 2026-11-29 00:35:42 A40-d8-rearr18_x16-gate: start (attempt 2/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-rearr18_x16-gate.log
[pool] 2026-11-29 00:35:42 A40-d8-rearr18_x16-gate: attempt 2 failed (rc=3: non-zero exit); retry after 00:45 on any empty GPU

[pool] 2026-11-29 00:46:16 exec A40-d8-rearr18_x16-gate GPU None 
[pool] 2026-11-29 00:46:22 A40-d8-rearr18_x16-gate: start (attempt 3/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-rearr18_x16-gate.log
[pool] 2026-11-29 00:46:22 A40-d8-rearr18_x16-gate: attempt 3 failed (rc=3: non-zero exit); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-rearr18_x16-gate.md
[queue5] 2026-11-29 00:46:27 A40-d8-rearr18_x16-gate: ERROR  rc=3
```

## A40-d8-rearr18-report100 (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-rearr18-report100.log):
```

[queue5] 2026-11-29 00:46:58 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag8.py report
swapT_x16    1-50: 26 vs 27 of 50 (gain -1; line reached False)
swapT_x32    1-50: 29 vs 27 of 50 (gain 2; line reached False)
swapT_s50    1-50: 23 vs 27 of 50 (gain -4; line reached False)
press_x16    1-50: 8 vs 13 of 43 (gain -5; line reached False)
press_x32    1-50: 1 vs 3 of 10 (gain -2; line reached False)
press_s50    no paired episodes yet
rearr18_x16  no paired episodes yet
DIAG8 REPORT written /workspace/FastWAM-memory2/outputs/fullft/DIAG_V22_DIAG8.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d8-rearr18-report100.log):
```

[pool] 2026-11-29 00:46:52 exec A40-d8-rearr18-report100 GPU None 
[pool] 2026-11-29 00:46:58 A40-d8-rearr18-report100: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d8-rearr18-report100.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-rearr18-report100.md
[queue5] 2026-11-29 00:47:04 A40-d8-rearr18-report100: PASS  rc=0
```

## A40-d7a-report (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d7a-report.log):
```

[queue5] 2026-11-28 16:48:24 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag7a.py

== seed18 v21:rearr_pw_s18_e30: 100 episodes; classes {'never pressed: block1 placed on the empty mat': 17, 'success': 61, 'pressed twice or more (after step 1 was complete)': 22}
   pressed twice, first press in the record between the presses: {'always in the record': 4, 'sometimes in the record': 18}
   never pressed, depth: {'ABOVE': 15, 'AT DEPTH': 2}; lowest heights [0.191, 0.191, 0.2019, 0.2048, 0.2056, 0.2059, 0.2065, 0.2082, 0.2163, 0.2208, 0.2217, 0.2223, 0.2224, 0.2224, 0.2224, 0.2226, 0.2227]
   write delay: {'median': 9, 'min': 5, 'max': 13, 'n': 83}

== seed17 v20:rearr_pw_e30: 100 episodes; classes {'success': 93, 'never pressed: block1 placed on the empty mat': 4, 'stage 1, then moved block1 again (which-block error)': 2, 'pressed too early (block1 not on the empty mat at the press)': 1}
   pressed twice, first press in the record between the presses: {}
   never pressed, depth: {'ABOVE': 4}; lowest heights [0.1975, 0.2025, 0.2043, 0.2217]
   write delay: {'median': 9.5, 'min': 5, 'max': 14, 'n': 96}

DIAG 7A: majority_above True (ABOVE 15 of 17 never-pressed episodes of seed 18 (> half -> true)); written outputs/fullft/DIAG_V22_DIAG7A.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d7a-report.log):
```

[pool] 2026-11-28 16:48:20 exec A40-d7a-report GPU None 
[pool] 2026-11-28 16:48:24 A40-d7a-report: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d7a-report.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d7a-report.md
[queue5] 2026-11-28 16:52:47 A40-d7a-report: PASS  rc=0
```

## A40-d9-rearr_pw_e30-off-s0 (done, attempt 3, GPU 5)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 4,
  "time": "2026-11-29 00:03:13",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 4,
  "time": "2026-11-29 00:14:56",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 3,
  "gpu": 5,
  "time": "2026-11-29 00:26:13",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_e30-off-s0.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d9-rearr_pw_e30-off-s0.log):
```
[pool] 2026-11-29 00:14:22 A40-d9-rearr_pw_e30-off-s0: start (attempt 2/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_e30-off-s0.log
[pool] 2026-11-29 00:14:56 A40-d9-rearr_pw_e30-off-s0: attempt 2 failed (rc=1: Python exception); retry after 00:24 on any empty GPU

[pool] 2026-11-29 00:25:32 exec A40-d9-rearr_pw_e30-off-s0 GPU 5 
[pool] 2026-11-29 00:25:38 A40-d9-rearr_pw_e30-off-s0: start (attempt 3/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_e30-off-s0.log
[pool] 2026-11-29 00:26:13 A40-d9-rearr_pw_e30-off-s0: attempt 3 failed (rc=1: Python exception); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d9-rearr_pw_e30-off-s0.md
[queue5] 2026-11-29 00:26:18 A40-d9-rearr_pw_e30-off-s0: ERROR  
```

## A40-d9-rearr_pw_e30-off-s1 (done, attempt 3, GPU 5)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 4,
  "time": "2026-11-29 00:07:50",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 7,
  "time": "2026-11-29 00:19:07",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 3,
  "gpu": 5,
  "time": "2026-11-29 00:30:57",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_e30-off-s1.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d9-rearr_pw_e30-off-s1.log):
```
[pool] 2026-11-29 00:18:31 A40-d9-rearr_pw_e30-off-s1: start (attempt 2/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_e30-off-s1.log
[pool] 2026-11-29 00:19:07 A40-d9-rearr_pw_e30-off-s1: attempt 2 failed (rc=1: Python exception); retry after 00:29 on any empty GPU

[pool] 2026-11-29 00:30:15 exec A40-d9-rearr_pw_e30-off-s1 GPU 5 
[pool] 2026-11-29 00:30:20 A40-d9-rearr_pw_e30-off-s1: start (attempt 3/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_e30-off-s1.log
[pool] 2026-11-29 00:30:57 A40-d9-rearr_pw_e30-off-s1: attempt 3 failed (rc=1: Python exception); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d9-rearr_pw_e30-off-s1.md
[queue5] 2026-11-29 00:31:02 A40-d9-rearr_pw_e30-off-s1: ERROR  
```

## A40-d9-rearr_pw_e30-off-s2 (done, attempt 3, GPU 4)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 4,
  "time": "2026-11-29 00:12:32",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 6,
  "time": "2026-11-29 00:23:50",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 3,
  "gpu": 4,
  "time": "2026-11-29 00:35:03",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_e30-off-s2.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d9-rearr_pw_e30-off-s2.log):
```
[pool] 2026-11-29 00:23:15 A40-d9-rearr_pw_e30-off-s2: start (attempt 2/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_e30-off-s2.log
[pool] 2026-11-29 00:23:50 A40-d9-rearr_pw_e30-off-s2: attempt 2 failed (rc=1: Python exception); retry after 00:33 on any empty GPU

[pool] 2026-11-29 00:34:24 exec A40-d9-rearr_pw_e30-off-s2 GPU 4 
[pool] 2026-11-29 00:34:29 A40-d9-rearr_pw_e30-off-s2: start (attempt 3/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_e30-off-s2.log
[pool] 2026-11-29 00:35:03 A40-d9-rearr_pw_e30-off-s2: attempt 3 failed (rc=1: Python exception); attempts used up: judging what exists
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d9-rearr_pw_e30-off-s2.md
[queue5] 2026-11-29 00:35:09 A40-d9-rearr_pw_e30-off-s2: ERROR  
```

## A40-d9-rearr_pw_e30-off-s3 (pending, attempt 2, GPU 4)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 4,
  "time": "2026-11-29 00:17:19",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 5,
  "time": "2026-11-29 00:28:34",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_e30-off-s3.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d9-rearr_pw_e30-off-s3.log):
```
[pool] 2026-11-29 00:17:19 A40-d9-rearr_pw_e30-off-s3: attempt 1 failed (rc=1: Python exception); retry after 00:27 on any empty GPU

[pool] 2026-11-29 00:27:54 exec A40-d9-rearr_pw_e30-off-s3 GPU 5 
[pool] 2026-11-29 00:27:59 A40-d9-rearr_pw_e30-off-s3: start (attempt 2/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_e30-off-s3.log
[pool] 2026-11-29 00:28:34 A40-d9-rearr_pw_e30-off-s3: attempt 2 failed (rc=1: Python exception); retry after 00:38 on any empty GPU

[pool] 2026-11-29 00:39:09 exec A40-d9-rearr_pw_e30-off-s3 GPU 4 
[pool] 2026-11-29 00:39:14 A40-d9-rearr_pw_e30-off-s3: GPU 4 is unhealthy ({4: '[N/A]', 5: '[N/A]', 6: '[N/A]', 7: '[N/A]'}); dropped [4, 5, 6, 7] from the allowed GPUs (now [0, 1, 2, 3]); back in the queue, attempt counter unchanged
```

## A40-d9-rearr_pw_e30-off-s4 (pending, attempt 2, GPU 6)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 4,
  "time": "2026-11-29 00:19:42",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 6,
  "time": "2026-11-29 00:30:56",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_e30-off-s4.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d9-rearr_pw_e30-off-s4.log):
```

[pool] 2026-11-29 00:19:02 exec A40-d9-rearr_pw_e30-off-s4 GPU 4 
[pool] 2026-11-29 00:19:07 A40-d9-rearr_pw_e30-off-s4: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_e30-off-s4.log
[pool] 2026-11-29 00:19:42 A40-d9-rearr_pw_e30-off-s4: attempt 1 failed (rc=1: Python exception); retry after 00:29 on any empty GPU

[pool] 2026-11-29 00:30:15 exec A40-d9-rearr_pw_e30-off-s4 GPU 6 
[pool] 2026-11-29 00:30:20 A40-d9-rearr_pw_e30-off-s4: start (attempt 2/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_e30-off-s4.log
[pool] 2026-11-29 00:30:56 A40-d9-rearr_pw_e30-off-s4: attempt 2 failed (rc=1: Python exception); retry after 00:40 on any empty GPU
```

## A40-d9-rearr_pw_s18_e30-off-s0 (pending, attempt 2, GPU 5)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 7,
  "time": "2026-11-29 00:23:50",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 5,
  "time": "2026-11-29 00:35:41",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_s18_e30-off-s0.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d9-rearr_pw_s18_e30-off-s0.log):
```

[pool] 2026-11-29 00:23:10 exec A40-d9-rearr_pw_s18_e30-off-s0 GPU 7 
[pool] 2026-11-29 00:23:15 A40-d9-rearr_pw_s18_e30-off-s0: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_s18_e30-off-s0.log
[pool] 2026-11-29 00:23:50 A40-d9-rearr_pw_s18_e30-off-s0: attempt 1 failed (rc=1: Python exception); retry after 00:33 on any empty GPU

[pool] 2026-11-29 00:35:00 exec A40-d9-rearr_pw_s18_e30-off-s0 GPU 5 
[pool] 2026-11-29 00:35:05 A40-d9-rearr_pw_s18_e30-off-s0: start (attempt 2/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_s18_e30-off-s0.log
[pool] 2026-11-29 00:35:41 A40-d9-rearr_pw_s18_e30-off-s0: attempt 2 failed (rc=1: Python exception); retry after 00:45 on any empty GPU
```

## A40-d9-rearr_pw_s18_e30-off-s1 (pending, attempt 2, GPU 6)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 4,
  "time": "2026-11-29 00:24:26",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 6,
  "time": "2026-11-29 00:35:41",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_s18_e30-off-s1.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d9-rearr_pw_s18_e30-off-s1.log):
```

[pool] 2026-11-29 00:23:46 exec A40-d9-rearr_pw_s18_e30-off-s1 GPU 4 
[pool] 2026-11-29 00:23:52 A40-d9-rearr_pw_s18_e30-off-s1: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_s18_e30-off-s1.log
[pool] 2026-11-29 00:24:26 A40-d9-rearr_pw_s18_e30-off-s1: attempt 1 failed (rc=1: Python exception); retry after 00:34 on any empty GPU

[pool] 2026-11-29 00:35:00 exec A40-d9-rearr_pw_s18_e30-off-s1 GPU 6 
[pool] 2026-11-29 00:35:05 A40-d9-rearr_pw_s18_e30-off-s1: start (attempt 2/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_s18_e30-off-s1.log
[pool] 2026-11-29 00:35:41 A40-d9-rearr_pw_s18_e30-off-s1: attempt 2 failed (rc=1: Python exception); retry after 00:45 on any empty GPU
```

## A40-d9-rearr_pw_s18_e30-off-s2 (pending, attempt 2, GPU 4)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 6,
  "time": "2026-11-29 00:26:12",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 4,
  "time": "2026-11-29 00:37:26",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_s18_e30-off-s2.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d9-rearr_pw_s18_e30-off-s2.log):
```

[pool] 2026-11-29 00:25:32 exec A40-d9-rearr_pw_s18_e30-off-s2 GPU 6 
[pool] 2026-11-29 00:25:38 A40-d9-rearr_pw_s18_e30-off-s2: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_s18_e30-off-s2.log
[pool] 2026-11-29 00:26:12 A40-d9-rearr_pw_s18_e30-off-s2: attempt 1 failed (rc=1: Python exception); retry after 00:36 on any empty GPU

[pool] 2026-11-29 00:36:47 exec A40-d9-rearr_pw_s18_e30-off-s2 GPU 4 
[pool] 2026-11-29 00:36:52 A40-d9-rearr_pw_s18_e30-off-s2: start (attempt 2/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_s18_e30-off-s2.log
[pool] 2026-11-29 00:37:26 A40-d9-rearr_pw_s18_e30-off-s2: attempt 2 failed (rc=1: Python exception); retry after 00:47 on any empty GPU
```

## A40-d9-rearr_pw_s18_e30-off-s3 (pending, attempt 2, GPU 5)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 7,
  "time": "2026-11-29 00:26:12",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 5,
  "time": "2026-11-29 00:38:02",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_s18_e30-off-s3.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d9-rearr_pw_s18_e30-off-s3.log):
```

[pool] 2026-11-29 00:25:32 exec A40-d9-rearr_pw_s18_e30-off-s3 GPU 7 
[pool] 2026-11-29 00:25:38 A40-d9-rearr_pw_s18_e30-off-s3: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_s18_e30-off-s3.log
[pool] 2026-11-29 00:26:12 A40-d9-rearr_pw_s18_e30-off-s3: attempt 1 failed (rc=1: Python exception); retry after 00:36 on any empty GPU

[pool] 2026-11-29 00:37:22 exec A40-d9-rearr_pw_s18_e30-off-s3 GPU 5 
[pool] 2026-11-29 00:37:27 A40-d9-rearr_pw_s18_e30-off-s3: start (attempt 2/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_s18_e30-off-s3.log
[pool] 2026-11-29 00:38:02 A40-d9-rearr_pw_s18_e30-off-s3: attempt 2 failed (rc=1: Python exception); retry after 00:48 on any empty GPU
```

## A40-d9-rearr_pw_s18_e30-off-s4 (pending, attempt 2, GPU 6)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 4,
  "time": "2026-11-29 00:26:48",
  "why": "rc=1: Python exception"
 },
 {
  "attempt": 2,
  "gpu": 6,
  "time": "2026-11-29 00:38:05",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_s18_e30-off-s4.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d9-rearr_pw_s18_e30-off-s4.log):
```

[pool] 2026-11-29 00:26:08 exec A40-d9-rearr_pw_s18_e30-off-s4 GPU 4 
[pool] 2026-11-29 00:26:14 A40-d9-rearr_pw_s18_e30-off-s4: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_s18_e30-off-s4.log
[pool] 2026-11-29 00:26:48 A40-d9-rearr_pw_s18_e30-off-s4: attempt 1 failed (rc=1: Python exception); retry after 00:36 on any empty GPU

[pool] 2026-11-29 00:37:22 exec A40-d9-rearr_pw_s18_e30-off-s4 GPU 6 
[pool] 2026-11-29 00:37:28 A40-d9-rearr_pw_s18_e30-off-s4: start (attempt 2/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d9-rearr_pw_s18_e30-off-s4.log
[pool] 2026-11-29 00:38:05 A40-d9-rearr_pw_s18_e30-off-s4: attempt 2 failed (rc=1: Python exception); retry after 00:48 on any empty GPU
```

## A40-fetch-press_cd-e10 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-press_cd-e10.log):
```
[fetch] 2026-11-28 15:49:14 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 15:54:15 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 15:59:15 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 16:04:16 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 16:09:17 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 16:14:17 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 16:19:18 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 16:24:18 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 16:29:19 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 16:34:19 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 16:39:20 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 16:44:20 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 16:49:21 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 16:54:22 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 16:59:22 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 17:04:23 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 17:09:23 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 17:14:24 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 17:19:25 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 17:24:25 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 17:29:26 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 17:34:26 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 17:39:27 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 17:44:27 waiting for exports/press_cd_e10 on the relay
[fetch] 2026-11-28 17:49:28 waiting for exports/press_cd_e10 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-press_cd-e10.log):
```

[pool] 2026-11-28 16:58:25 exec A40-fetch-press_cd-e10 GPU None 
[pool] 2026-11-28 16:58:29 A40-fetch-press_cd-e10: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-press_cd-e10.log
```

## A40-fetch-press_cd-e20 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-press_cd-e20.log):
```
[fetch] 2026-11-28 15:49:14 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 15:54:15 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 15:59:15 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 16:04:16 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 16:09:16 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 16:14:17 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 16:19:18 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 16:24:18 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 16:29:19 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 16:34:19 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 16:39:20 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 16:44:20 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 16:49:21 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 16:54:21 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 16:59:22 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 17:04:22 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 17:09:23 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 17:14:24 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 17:19:24 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 17:24:25 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 17:29:25 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 17:34:26 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 17:39:27 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 17:44:27 waiting for exports/press_cd_e20 on the relay
[fetch] 2026-11-28 17:49:28 waiting for exports/press_cd_e20 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-press_cd-e20.log):
```

[pool] 2026-11-28 16:58:25 exec A40-fetch-press_cd-e20 GPU None 
[pool] 2026-11-28 16:58:29 A40-fetch-press_cd-e20: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-press_cd-e20.log
```

## A40-fetch-rearr_pw_long_s18-e45 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_long_s18-e45.log):
```
[fetch] 2026-11-28 15:49:07 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 15:54:07 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 15:59:08 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 16:04:08 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 16:09:09 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 16:14:09 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 16:19:10 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 16:24:10 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 16:29:11 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 16:34:12 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 16:39:12 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 16:44:13 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 16:49:13 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 16:54:14 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 16:59:14 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 17:04:15 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 17:09:15 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 17:14:16 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 17:19:17 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 17:24:17 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 17:29:18 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 17:34:18 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 17:39:19 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 17:44:19 waiting for exports/rearr_pw_long_s18_e45 on the relay
[fetch] 2026-11-28 17:49:20 waiting for exports/rearr_pw_long_s18_e45 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearr_pw_long_s18-e45.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-rearr_pw_long_s18-e45 GPU None 
[pool] 2026-11-28 17:08:22 A40-fetch-rearr_pw_long_s18-e45: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_long_s18-e45.log
```

## A40-fetch-rearr_pw_long-e45 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_long-e45.log):
```
[fetch] 2026-11-28 15:49:06 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 15:54:07 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 15:59:07 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 16:04:08 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 16:09:08 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 16:14:09 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 16:19:09 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 16:24:10 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 16:29:10 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 16:34:11 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 16:39:12 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 16:44:12 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 16:49:13 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 16:54:13 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 16:59:14 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 17:04:14 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 17:09:15 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 17:14:15 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 17:19:16 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 17:24:17 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 17:29:17 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 17:34:18 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 17:39:18 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 17:44:19 waiting for exports/rearr_pw_long_e45 on the relay
[fetch] 2026-11-28 17:49:19 waiting for exports/rearr_pw_long_e45 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearr_pw_long-e45.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-rearr_pw_long-e45 GPU None 
[pool] 2026-11-28 17:08:21 A40-fetch-rearr_pw_long-e45: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_long-e45.log
```

## A40-fetch-rearr_pw_h100_long_s18-e45 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_h100_long_s18-e45.log):
```
[fetch] 2026-11-28 15:49:06 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 15:54:06 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 15:59:07 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 16:04:07 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 16:09:08 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 16:14:08 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 16:19:09 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 16:24:10 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 16:29:10 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 16:34:11 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 16:39:11 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 16:44:12 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 16:49:12 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 16:54:13 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 16:59:13 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 17:04:14 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 17:09:14 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 17:14:15 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 17:19:15 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 17:24:16 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 17:29:16 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 17:34:17 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 17:39:18 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 17:44:18 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
[fetch] 2026-11-28 17:49:19 waiting for exports/rearr_pw_h100_long_s18_e45 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearr_pw_h100_long_s18-e45.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-rearr_pw_h100_long_s18-e45 GPU None 
[pool] 2026-11-28 17:08:21 A40-fetch-rearr_pw_h100_long_s18-e45: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_h100_long_s18-e45.log
```

## A40-fetch-rearr_pw_h100_long-e45 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_h100_long-e45.log):
```
[fetch] 2026-11-28 15:49:08 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 15:54:08 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 15:59:09 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 16:04:09 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 16:09:10 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 16:14:10 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 16:19:11 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 16:24:11 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 16:29:12 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 16:34:13 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 16:39:13 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 16:44:14 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 16:49:14 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 16:54:15 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 16:59:15 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 17:04:16 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 17:09:17 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 17:14:17 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 17:19:18 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 17:24:18 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 17:29:19 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 17:34:19 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 17:39:20 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 17:44:20 waiting for exports/rearr_pw_h100_long_e45 on the relay
[fetch] 2026-11-28 17:49:21 waiting for exports/rearr_pw_h100_long_e45 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearr_pw_h100_long-e45.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-rearr_pw_h100_long-e45 GPU None 
[pool] 2026-11-28 17:08:22 A40-fetch-rearr_pw_h100_long-e45: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_h100_long-e45.log
```

## A40-fetch-rearr_ar_pw_s18-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_ar_pw_s18-e30.log):
```
[fetch] 2026-11-28 15:49:06 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 15:54:06 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 15:59:07 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:04:08 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:09:08 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:14:09 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:19:09 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:24:10 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:29:10 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:34:11 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:39:12 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:44:12 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:49:13 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:54:13 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:59:14 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 17:04:14 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 17:09:15 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 17:14:15 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 17:19:16 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 17:24:16 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 17:29:17 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 17:34:18 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 17:39:18 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 17:44:19 waiting for exports/rearr_ar_pw_s18_e30 on the relay
[fetch] 2026-11-28 17:49:19 waiting for exports/rearr_ar_pw_s18_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearr_ar_pw_s18-e30.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-rearr_ar_pw_s18-e30 GPU None 
[pool] 2026-11-28 17:08:21 A40-fetch-rearr_ar_pw_s18-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_ar_pw_s18-e30.log
```

## A40-fetch-rearr_arprop_pw_s18-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_arprop_pw_s18-e30.log):
```
[fetch] 2026-11-28 15:49:07 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 15:54:07 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 15:59:08 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:04:08 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:09:09 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:14:09 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:19:10 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:24:11 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:29:11 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:34:12 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:39:12 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:44:13 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:49:13 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:54:14 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 16:59:14 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 17:04:15 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 17:09:15 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 17:14:16 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 17:19:17 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 17:24:17 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 17:29:18 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 17:34:18 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 17:39:19 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 17:44:19 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
[fetch] 2026-11-28 17:49:20 waiting for exports/rearr_arprop_pw_s18_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearr_arprop_pw_s18-e30.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-rearr_arprop_pw_s18-e30 GPU None 
[pool] 2026-11-28 17:08:22 A40-fetch-rearr_arprop_pw_s18-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_arprop_pw_s18-e30.log
```

## A40-fetch-rearrange_ar_s18-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearrange_ar_s18-e30.log):
```
[fetch] 2026-11-28 15:49:07 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 15:54:08 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 15:59:08 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:04:09 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:09:09 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:14:10 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:19:10 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:24:11 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:29:11 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:34:12 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:39:13 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:44:13 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:49:14 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:54:14 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:59:15 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 17:04:15 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 17:09:16 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 17:14:16 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 17:19:17 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 17:24:18 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 17:29:18 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 17:34:19 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 17:39:19 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 17:44:20 waiting for exports/rearrange_ar_s18_e30 on the relay
[fetch] 2026-11-28 17:49:20 waiting for exports/rearrange_ar_s18_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearrange_ar_s18-e30.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-rearrange_ar_s18-e30 GPU None 
[pool] 2026-11-28 17:08:22 A40-fetch-rearrange_ar_s18-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearrange_ar_s18-e30.log
```

## A40-fetch-rearrange_arprop_s18-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearrange_arprop_s18-e30.log):
```
[fetch] 2026-11-28 15:49:07 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 15:54:08 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 15:59:08 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:04:09 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:09:09 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:14:10 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:19:10 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:24:11 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:29:11 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:34:12 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:39:12 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:44:13 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:49:14 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:54:14 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:59:15 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 17:04:15 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 17:09:16 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 17:14:16 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 17:19:17 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 17:24:18 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 17:29:18 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 17:34:19 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 17:39:19 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 17:44:20 waiting for exports/rearrange_arprop_s18_e30 on the relay
[fetch] 2026-11-28 17:49:20 waiting for exports/rearrange_arprop_s18_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearrange_arprop_s18-e30.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-rearrange_arprop_s18-e30 GPU None 
[pool] 2026-11-28 17:08:22 A40-fetch-rearrange_arprop_s18-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearrange_arprop_s18-e30.log
```

## A40-fetch-ranking_v3a_s18-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-ranking_v3a_s18-e30.log):
```
[fetch] 2026-11-28 15:49:07 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 15:54:08 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 15:59:08 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 16:04:09 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 16:09:09 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 16:14:10 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 16:19:10 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 16:24:11 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 16:29:11 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 16:34:12 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 16:39:12 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 16:44:13 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 16:49:13 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 16:54:14 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 16:59:15 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 17:04:15 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 17:09:16 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 17:14:16 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 17:19:17 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 17:24:17 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 17:29:18 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 17:34:18 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 17:39:19 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 17:44:19 waiting for exports/ranking_v3a_s18_e30 on the relay
[fetch] 2026-11-28 17:49:20 waiting for exports/ranking_v3a_s18_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-ranking_v3a_s18-e30.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-ranking_v3a_s18-e30 GPU None 
[pool] 2026-11-28 17:08:22 A40-fetch-ranking_v3a_s18-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-ranking_v3a_s18-e30.log
```

## A40-fetch-ranking_v3a_s18-e20 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-ranking_v3a_s18-e20.log):
```
[fetch] 2026-11-28 15:49:07 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 15:54:08 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 15:59:08 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 16:04:09 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 16:09:09 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 16:14:10 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 16:19:10 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 16:24:11 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 16:29:11 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 16:34:12 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 16:39:13 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 16:44:13 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 16:49:14 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 16:54:14 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 16:59:15 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 17:04:15 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 17:09:16 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 17:14:17 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 17:19:17 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 17:24:18 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 17:29:18 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 17:34:19 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 17:39:19 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 17:44:20 waiting for exports/ranking_v3a_s18_e20 on the relay
[fetch] 2026-11-28 17:49:20 waiting for exports/ranking_v3a_s18_e20 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-ranking_v3a_s18-e20.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-ranking_v3a_s18-e20 GPU None 
[pool] 2026-11-28 17:08:22 A40-fetch-ranking_v3a_s18-e20: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-ranking_v3a_s18-e20.log
```

## A40-fetch-swapT_joint3_s18-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_joint3_s18-e30.log):
```
[fetch] 2026-11-28 15:49:08 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 15:54:08 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 15:59:09 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 16:04:09 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 16:09:10 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 16:14:10 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 16:19:11 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 16:24:11 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 16:29:12 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 16:34:13 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 16:39:13 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 16:44:14 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 16:49:14 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 16:54:15 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 16:59:15 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 17:04:16 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 17:09:17 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 17:14:17 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 17:19:18 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 17:24:18 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 17:29:19 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 17:34:19 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 17:39:20 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 17:44:20 waiting for exports/swapT_joint3_s18_e30 on the relay
[fetch] 2026-11-28 17:49:21 waiting for exports/swapT_joint3_s18_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-swapT_joint3_s18-e30.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-swapT_joint3_s18-e30 GPU None 
[pool] 2026-11-28 17:08:23 A40-fetch-swapT_joint3_s18-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_joint3_s18-e30.log
```

## A40-fetch-rearr_joint3-e10 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_joint3-e10.log):
```
[fetch] 2026-11-28 15:49:08 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 15:54:08 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 15:59:09 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 16:04:09 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 16:09:10 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 16:14:10 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 16:19:11 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 16:24:12 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 16:29:12 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 16:34:13 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 16:39:13 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 16:44:14 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 16:49:14 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 16:54:15 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 16:59:15 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 17:04:16 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 17:09:17 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 17:14:17 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 17:19:18 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 17:24:18 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 17:29:19 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 17:34:19 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 17:39:20 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 17:44:21 waiting for exports/rearr_joint3_e10 on the relay
[fetch] 2026-11-28 17:49:21 waiting for exports/rearr_joint3_e10 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearr_joint3-e10.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-rearr_joint3-e10 GPU None 
[pool] 2026-11-28 17:08:23 A40-fetch-rearr_joint3-e10: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_joint3-e10.log
```

## A40-fetch-rearr_joint3-e20 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_joint3-e20.log):
```
[fetch] 2026-11-28 15:49:07 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 15:54:08 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 15:59:09 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 16:04:09 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 16:09:10 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 16:14:10 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 16:19:11 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 16:24:11 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 16:29:12 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 16:34:12 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 16:39:13 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 16:44:13 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 16:49:14 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 16:54:15 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 16:59:15 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 17:04:16 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 17:09:16 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 17:14:17 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 17:19:18 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 17:24:18 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 17:29:19 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 17:34:19 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 17:39:20 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 17:44:20 waiting for exports/rearr_joint3_e20 on the relay
[fetch] 2026-11-28 17:49:21 waiting for exports/rearr_joint3_e20 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearr_joint3-e20.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-rearr_joint3-e20 GPU None 
[pool] 2026-11-28 17:08:22 A40-fetch-rearr_joint3-e20: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_joint3-e20.log
```

## A40-fetch-swapT_joint3_ow-e10 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_joint3_ow-e10.log):
```
[fetch] 2026-11-28 15:49:06 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 15:54:06 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 15:59:07 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 16:04:08 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 16:09:08 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 16:14:09 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 16:19:09 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 16:24:10 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 16:29:10 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 16:34:11 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 16:39:11 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 16:44:12 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 16:49:13 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 16:54:13 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 16:59:14 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 17:04:14 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 17:09:15 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 17:14:15 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 17:19:16 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 17:24:16 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 17:29:17 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 17:34:18 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 17:39:18 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 17:44:19 waiting for exports/swapT_joint3_ow_e10 on the relay
[fetch] 2026-11-28 17:49:19 waiting for exports/swapT_joint3_ow_e10 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-swapT_joint3_ow-e10.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-swapT_joint3_ow-e10 GPU None 
[pool] 2026-11-28 17:08:22 A40-fetch-swapT_joint3_ow-e10: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_joint3_ow-e10.log
```

## A40-fetch-swapT_joint3_ow-e20 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_joint3_ow-e20.log):
```
[fetch] 2026-11-28 15:49:07 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 15:54:08 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 15:59:08 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 16:04:09 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 16:09:09 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 16:14:10 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 16:19:10 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 16:24:11 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 16:29:11 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 16:34:12 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 16:39:13 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 16:44:13 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 16:49:14 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 16:54:14 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 16:59:15 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 17:04:15 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 17:09:16 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 17:14:17 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 17:19:17 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 17:24:18 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 17:29:18 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 17:34:19 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 17:39:19 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 17:44:20 waiting for exports/swapT_joint3_ow_e20 on the relay
[fetch] 2026-11-28 17:49:20 waiting for exports/swapT_joint3_ow_e20 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-swapT_joint3_ow-e20.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-swapT_joint3_ow-e20 GPU None 
[pool] 2026-11-28 17:08:22 A40-fetch-swapT_joint3_ow-e20: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_joint3_ow-e20.log
```

## A40-fetch-obs_cf800-e5 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-obs_cf800-e5.log):
```
[fetch] 2026-11-28 15:49:07 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 15:54:08 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 15:59:08 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 16:04:09 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 16:09:09 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 16:14:10 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 16:19:10 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 16:24:11 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 16:29:11 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 16:34:12 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 16:39:13 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 16:44:13 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 16:49:14 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 16:54:14 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 16:59:15 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 17:04:15 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 17:09:16 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 17:14:16 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 17:19:17 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 17:24:17 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 17:29:18 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 17:34:19 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 17:39:19 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 17:44:20 waiting for exports/obs_cf800_e5 on the relay
[fetch] 2026-11-28 17:49:20 waiting for exports/obs_cf800_e5 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-obs_cf800-e5.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-obs_cf800-e5 GPU None 
[pool] 2026-11-28 17:08:22 A40-fetch-obs_cf800-e5: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-obs_cf800-e5.log
```

## A40-fetch-rearr_pw_s19-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_s19-e30.log):
```
[fetch] 2026-11-28 15:49:07 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 15:54:08 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 15:59:09 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 16:04:09 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 16:09:10 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 16:14:10 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 16:19:11 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 16:24:11 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 16:29:12 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 16:34:12 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 16:39:13 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 16:44:13 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 16:49:14 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 16:54:14 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 16:59:15 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 17:04:16 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 17:09:16 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 17:14:17 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 17:19:17 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 17:24:18 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 17:29:18 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 17:34:19 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 17:39:19 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 17:44:20 waiting for exports/rearr_pw_s19_e30 on the relay
[fetch] 2026-11-28 17:49:21 waiting for exports/rearr_pw_s19_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearr_pw_s19-e30.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-rearr_pw_s19-e30 GPU None 
[pool] 2026-11-28 17:08:23 A40-fetch-rearr_pw_s19-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_s19-e30.log
```

## A40-fetch-rearr_pw_h100_s19-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_h100_s19-e30.log):
```
[fetch] 2026-11-28 15:49:07 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 15:54:07 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 15:59:08 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 16:04:08 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 16:09:09 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 16:14:09 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 16:19:10 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 16:24:10 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 16:29:11 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 16:34:11 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 16:39:12 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 16:44:13 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 16:49:13 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 16:54:14 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 16:59:14 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 17:04:15 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 17:09:15 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 17:14:16 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 17:19:16 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 17:24:17 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 17:29:18 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 17:34:18 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 17:39:19 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 17:44:19 waiting for exports/rearr_pw_h100_s19_e30 on the relay
[fetch] 2026-11-28 17:49:20 waiting for exports/rearr_pw_h100_s19_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearr_pw_h100_s19-e30.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-rearr_pw_h100_s19-e30 GPU None 
[pool] 2026-11-28 17:08:22 A40-fetch-rearr_pw_h100_s19-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_h100_s19-e30.log
```

## A40-fetch-rearr_pw_h100_s20-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_h100_s20-e30.log):
```
[fetch] 2026-11-28 15:49:05 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 15:54:06 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 15:59:06 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 16:04:07 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 16:09:07 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 16:14:08 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 16:19:08 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 16:24:09 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 16:29:09 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 16:34:10 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 16:39:10 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 16:44:11 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 16:49:11 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 16:54:12 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 16:59:13 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 17:04:13 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 17:09:14 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 17:14:14 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 17:19:15 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 17:24:15 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 17:29:16 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 17:34:16 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 17:39:17 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 17:44:17 waiting for exports/rearr_pw_h100_s20_e30 on the relay
[fetch] 2026-11-28 17:49:18 waiting for exports/rearr_pw_h100_s20_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearr_pw_h100_s20-e30.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-rearr_pw_h100_s20-e30 GPU None 
[pool] 2026-11-28 17:08:21 A40-fetch-rearr_pw_h100_s20-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearr_pw_h100_s20-e30.log
```

## A40-fetch-swapT_ar_s18-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_ar_s18-e30.log):
```
[fetch] 2026-11-28 15:49:07 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 15:54:08 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 15:59:08 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:04:09 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:09:09 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:14:10 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:19:10 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:24:11 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:29:12 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:34:12 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:39:13 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:44:13 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:49:14 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:54:14 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 16:59:15 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 17:04:15 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 17:09:16 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 17:14:17 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 17:19:17 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 17:24:18 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 17:29:18 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 17:34:19 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 17:39:20 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 17:44:20 waiting for exports/swapT_ar_s18_e30 on the relay
[fetch] 2026-11-28 17:49:21 waiting for exports/swapT_ar_s18_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-swapT_ar_s18-e30.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-swapT_ar_s18-e30 GPU None 
[pool] 2026-11-28 17:08:22 A40-fetch-swapT_ar_s18-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_ar_s18-e30.log
```

## A40-fetch-ranking_arprop_s18-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-ranking_arprop_s18-e30.log):
```
[fetch] 2026-11-28 15:49:08 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 15:54:08 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 15:59:09 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:04:09 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:09:10 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:14:10 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:19:11 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:24:11 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:29:12 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:34:13 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:39:13 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:44:14 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:49:14 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:54:15 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 16:59:15 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 17:04:16 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 17:09:17 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 17:14:17 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 17:19:18 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 17:24:18 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 17:29:19 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 17:34:19 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 17:39:20 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 17:44:20 waiting for exports/ranking_arprop_s18_e30 on the relay
[fetch] 2026-11-28 17:49:21 waiting for exports/ranking_arprop_s18_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-ranking_arprop_s18-e30.log):
```

[pool] 2026-11-28 17:08:16 exec A40-fetch-ranking_arprop_s18-e30 GPU None 
[pool] 2026-11-28 17:08:22 A40-fetch-ranking_arprop_s18-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-ranking_arprop_s18-e30.log
```

## A40-fetch-cover_none-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-cover_none-e30.log):
```
[fetch] 2026-11-28 15:50:13 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 15:55:14 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 16:00:14 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 16:05:15 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 16:10:16 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 16:15:16 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 16:20:17 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 16:25:17 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 16:30:18 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 16:35:18 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 16:40:19 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 16:45:19 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 16:50:20 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 16:55:21 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 17:00:21 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 17:05:22 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 17:10:22 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 17:15:23 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 17:20:23 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 17:25:24 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 17:30:24 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 17:35:25 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 17:40:25 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 17:45:26 waiting for exports/cover_none_e30 on the relay
[fetch] 2026-11-28 17:50:26 waiting for exports/cover_none_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-cover_none-e30.log):
```

[pool] 2026-11-24 18:22:55 exec A40-fetch-cover_none-e30 GPU None 
[pool] 2026-11-24 18:22:58 A40-fetch-cover_none-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-cover_none-e30.log
```

## A40-fetch-battery_clock-e30 (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-battery_clock-e30.log):
```
[fetch] 2026-11-28 02:43:14 waiting for exports/battery_clock_e30 on the relay
[fetch] 2026-11-28 02:48:15 waiting for exports/battery_clock_e30 on the relay
[fetch] 2026-11-28 02:53:15 waiting for exports/battery_clock_e30 on the relay
[fetch] 2026-11-28 02:58:16 waiting for exports/battery_clock_e30 on the relay
[fetch] 2026-11-28 03:03:16 waiting for exports/battery_clock_e30 on the relay
[fetch] 2026-11-28 03:08:17 waiting for exports/battery_clock_e30 on the relay
[fetch] 2026-11-28 03:13:17 waiting for exports/battery_clock_e30 on the relay
[fetch] 2026-11-28 03:18:18 waiting for exports/battery_clock_e30 on the relay
[fetch] 2026-11-28 03:23:18 waiting for exports/battery_clock_e30 on the relay
[fetch] 2026-11-28 03:28:19 waiting for exports/battery_clock_e30 on the relay
[fetch] 2026-11-28 03:33:19 waiting for exports/battery_clock_e30 on the relay
[fetch] 2026-11-28 03:38:20 waiting for exports/battery_clock_e30 on the relay
[fetch] 2026-11-28 03:43:21 waiting for exports/battery_clock_e30 on the relay
[fetch] 2026-11-28 03:48:21 waiting for exports/battery_clock_e30 on the relay
[fetch] 2026-11-28 03:53:22 waiting for exports/battery_clock_e30 on the relay
[fetch] disk before: /dev/sdb         19T   11T  6.7T  62% /workspace/FastWAM-memory2
[fetch] 2026-11-28 03:58:22 fetching battery_clock_e30 (attempt 1)
[relay] get hhyfred/memwam-fullft/exports/battery_clock_e30/export_e30.pt -> /workspace/FastWAM-memory2/outputs/fullft/exports/battery_clock_e30/export_e30.pt (12042326085 bytes)
[relay] get hhyfred/memwam-fullft/exports/battery_clock_e30/export_e30.pt.sha256 -> /workspace/FastWAM-memory2/outputs/fullft/exports/battery_clock_e30/export_e30.pt.sha256 (80 bytes)
export_e30.pt: OK
total 11760104
drwxr-xr-x   2 root root        4096 Nov 28 04:06 .
drwxr-xr-x 100 root root        4096 Nov 28 03:58 ..
-rw-r--r--   1 root root 12042326085 Nov 28 04:05 export_e30.pt
-rw-r--r--   1 root root          80 Nov 28 04:06 export_e30.pt.sha256
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-battery_clock-e30.log):
```

[pool] 2026-11-24 18:32:57 exec A40-fetch-battery_clock-e30 GPU None 
[pool] 2026-11-24 18:33:00 A40-fetch-battery_clock-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-battery_clock-e30.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-battery_clock-e30.md
[queue5] 2026-11-28 12:06:24 A40-fetch-battery_clock-e30: PASS  rc=0
```

## A40-batclk30-smoke (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-batclk30-smoke.log):
```
rearrange_none_e30_smoke/onrearrange_blocks   1     0.00  [0.00,0.79]      1.00    0.00      700        -        -        -    0.5
swapT_ar_e30_smoke/on   swap_T             1     0.00  [0.00,0.79]         -    0.00      600        -        -        -    0.5
swapT_arprop_e30_smoke/onswap_T             1     0.00  [0.00,0.79]         -    0.00      600        -        -        -    0.6
swapT_none_e30_smoke/on swap_T             1     0.00  [0.00,0.79]         -    0.00      600        -        -        -    0.5

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  battery_ar_e30_smoke/on  vs battery_arprop_e30_smoke/on   1     1       0       0        0  1.000
  battery_ar_e30_smoke/on  vs battery_clock_e30_smoke/on   1     1       0       0        0  1.000
  battery_ar_e30_smoke/on  vs battery_none_e30_smoke/on   1     1       0       0        0  1.000
  battery_arprop_e30_smoke/on vs battery_clock_e30_smoke/on   1     1       0       0        0  1.000
  battery_arprop_e30_smoke/on vs battery_none_e30_smoke/on   1     1       0       0        0  1.000
  battery_clock_e30_smoke/on vs battery_none_e30_smoke/on   1     1       0       0        0  1.000
  cover_ar_e30_smoke/on    vs cover_arprop_e30_smoke/on   1     1       0       0        0  1.000
  obs_ar_e30_smoke/on      vs obs_arprop_e30_smoke/on    1     0       0       0        1  1.000
  ranking_ar_e30_smoke/on  vs ranking_arprop_e30_smoke/on   1     0       0       1        0  1.000
  ranking_ar_e30_smoke/on  vs ranking_none_e30_smoke/on   1     0       0       1        0  1.000
  ranking_arprop_e30_smoke/on vs ranking_none_e30_smoke/on   1     1       0       0        0  1.000
  rearrange_ar_e30_smoke/on vs rearrange_arprop_e30_smoke/on   1     0       0       1        0  1.000
  rearrange_ar_e30_smoke/on vs rearrange_none_e30_smoke/on   1     0       0       0        1  1.000
  rearrange_arprop_e30_smoke/on vs rearrange_none_e30_smoke/on   1     0       1       0        0  1.000
  swapT_ar_e30_smoke/on    vs swapT_arprop_e30_smoke/on   1     0       0       0        1  1.000
  swapT_ar_e30_smoke/on    vs swapT_none_e30_smoke/on    1     0       0       0        1  1.000
  swapT_arprop_e30_smoke/on vs swapT_none_e30_smoke/on    1     0       0       0        1  1.000

[summary] 17 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e6smoke/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-batclk30-smoke.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'battery_try'
[queue5] 2026-11-28 13:35:48 A40-batclk30-smoke: PASS  battery_try/on n=1  prog=0.00
```

## A40-batclk30-s0 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-batclk30-s0.log):
```
rearrange_none_e30/on   rearrange_blocks 100     0.04  [0.02,0.10]      1.00    0.04      687        -        -        -    0.5
swapT_ar_e30/on         swap_T           100     0.51  [0.41,0.61]         -    0.51      442        -        -        -    0.6
swapT_arprop_e30/on     swap_T           100     0.49  [0.39,0.59]         -    0.49      448        -        -        -    0.6
swapT_none_e30/on       swap_T           100     0.05  [0.02,0.11]         -    0.05      585        -        -        -    0.5

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  battery_ar_e30/on        vs battery_arprop_e30/on    100    88       3       3        6  1.000
  battery_ar_e30/on        vs battery_clock_e30/on      35    33       0       1        1  1.000
  battery_ar_e30/on        vs battery_none_e30/on      100    50      41       4        5  0.000
  battery_arprop_e30/on    vs battery_clock_e30/on      35    32       0       2        1  0.500
  battery_arprop_e30/on    vs battery_none_e30/on      100    51      40       3        6  0.000
  battery_clock_e30/on     vs battery_none_e30/on       35    18      16       1        0  0.000
  cover_ar_e30/on          vs cover_arprop_e30/on      100    71       1      28        0  0.000
  obs_ar_e30/on            vs obs_arprop_e30/on        100     8       5       8       79  0.581
  ranking_ar_e30/on        vs ranking_arprop_e30/on    100    46      31      19        4  0.119
  ranking_ar_e30/on        vs ranking_none_e30/on       71     4      50       2       15  0.000
  ranking_arprop_e30/on    vs ranking_none_e30/on       71     6      38       0       27  0.000
  rearrange_ar_e30/on      vs rearrange_arprop_e30/on  100    26       3      36       35  0.000
  rearrange_ar_e30/on      vs rearrange_none_e30/on    100     1      28       3       68  0.000
  rearrange_arprop_e30/on  vs rearrange_none_e30/on    100     2      60       2       36  0.000
  swapT_ar_e30/on          vs swapT_arprop_e30/on      100    40      11       9       40  0.824
  swapT_ar_e30/on          vs swapT_none_e30/on        100     1      50       4       45  0.000
  swapT_arprop_e30/on      vs swapT_none_e30/on        100     2      47       3       48  0.000

[summary] 1606 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e6/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-batclk30-s0.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'battery_try'
[queue5] 2026-11-28 14:19:42 A40-batclk30-s0: DONE  battery_try/on n=35  prog=0.00
```

## A40-batclk30-s1 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-batclk30-s1.log):
```
rearrange_none_e30/on   rearrange_blocks 100     0.04  [0.02,0.10]      1.00    0.04      687        -        -        -    0.5
swapT_ar_e30/on         swap_T           100     0.51  [0.41,0.61]         -    0.51      442        -        -        -    0.6
swapT_arprop_e30/on     swap_T           100     0.49  [0.39,0.59]         -    0.49      448        -        -        -    0.6
swapT_none_e30/on       swap_T           100     0.05  [0.02,0.11]         -    0.05      585        -        -        -    0.5

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  battery_ar_e30/on        vs battery_arprop_e30/on    100    88       3       3        6  1.000
  battery_ar_e30/on        vs battery_clock_e30/on      38    35       0       2        1  0.500
  battery_ar_e30/on        vs battery_none_e30/on      100    50      41       4        5  0.000
  battery_arprop_e30/on    vs battery_clock_e30/on      38    35       0       2        1  0.500
  battery_arprop_e30/on    vs battery_none_e30/on      100    51      40       3        6  0.000
  battery_clock_e30/on     vs battery_none_e30/on       38    20      17       1        0  0.000
  cover_ar_e30/on          vs cover_arprop_e30/on      100    71       1      28        0  0.000
  obs_ar_e30/on            vs obs_arprop_e30/on        100     8       5       8       79  0.581
  ranking_ar_e30/on        vs ranking_arprop_e30/on    100    46      31      19        4  0.119
  ranking_ar_e30/on        vs ranking_none_e30/on       71     4      50       2       15  0.000
  ranking_arprop_e30/on    vs ranking_none_e30/on       71     6      38       0       27  0.000
  rearrange_ar_e30/on      vs rearrange_arprop_e30/on  100    26       3      36       35  0.000
  rearrange_ar_e30/on      vs rearrange_none_e30/on    100     1      28       3       68  0.000
  rearrange_arprop_e30/on  vs rearrange_none_e30/on    100     2      60       2       36  0.000
  swapT_ar_e30/on          vs swapT_arprop_e30/on      100    40      11       9       40  0.824
  swapT_ar_e30/on          vs swapT_none_e30/on        100     1      50       4       45  0.000
  swapT_arprop_e30/on      vs swapT_none_e30/on        100     2      47       3       48  0.000

[summary] 1609 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e6/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-batclk30-s1.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'battery_try'
[queue5] 2026-11-28 14:21:20 A40-batclk30-s1: DONE  battery_try/on n=38  prog=0.00
```

## A40-batclk30-s2 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-batclk30-s2.log):
```
rearrange_none_e30/on   rearrange_blocks 100     0.04  [0.02,0.10]      1.00    0.04      687        -        -        -    0.5
swapT_ar_e30/on         swap_T           100     0.51  [0.41,0.61]         -    0.51      442        -        -        -    0.6
swapT_arprop_e30/on     swap_T           100     0.49  [0.39,0.59]         -    0.49      448        -        -        -    0.6
swapT_none_e30/on       swap_T           100     0.05  [0.02,0.11]         -    0.05      585        -        -        -    0.5

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  battery_ar_e30/on        vs battery_arprop_e30/on    100    88       3       3        6  1.000
  battery_ar_e30/on        vs battery_clock_e30/on      40    37       0       2        1  0.500
  battery_ar_e30/on        vs battery_none_e30/on      100    50      41       4        5  0.000
  battery_arprop_e30/on    vs battery_clock_e30/on      40    37       0       2        1  0.500
  battery_arprop_e30/on    vs battery_none_e30/on      100    51      40       3        6  0.000
  battery_clock_e30/on     vs battery_none_e30/on       40    22      17       1        0  0.000
  cover_ar_e30/on          vs cover_arprop_e30/on      100    71       1      28        0  0.000
  obs_ar_e30/on            vs obs_arprop_e30/on        100     8       5       8       79  0.581
  ranking_ar_e30/on        vs ranking_arprop_e30/on    100    46      31      19        4  0.119
  ranking_ar_e30/on        vs ranking_none_e30/on       71     4      50       2       15  0.000
  ranking_arprop_e30/on    vs ranking_none_e30/on       71     6      38       0       27  0.000
  rearrange_ar_e30/on      vs rearrange_arprop_e30/on  100    26       3      36       35  0.000
  rearrange_ar_e30/on      vs rearrange_none_e30/on    100     1      28       3       68  0.000
  rearrange_arprop_e30/on  vs rearrange_none_e30/on    100     2      60       2       36  0.000
  swapT_ar_e30/on          vs swapT_arprop_e30/on      100    40      11       9       40  0.824
  swapT_ar_e30/on          vs swapT_none_e30/on        100     1      50       4       45  0.000
  swapT_arprop_e30/on      vs swapT_none_e30/on        100     2      47       3       48  0.000

[summary] 1611 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e6/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-batclk30-s2.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'battery_try'
[queue5] 2026-11-28 14:24:26 A40-batclk30-s2: DONE  battery_try/on n=40  prog=0.00
```

## A40-batclk30-s3 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-batclk30-s3.log):
```
rearrange_none_e30/on   rearrange_blocks 100     0.04  [0.02,0.10]      1.00    0.04      687        -        -        -    0.5
swapT_ar_e30/on         swap_T           100     0.51  [0.41,0.61]         -    0.51      442        -        -        -    0.6
swapT_arprop_e30/on     swap_T           100     0.49  [0.39,0.59]         -    0.49      448        -        -        -    0.6
swapT_none_e30/on       swap_T           100     0.05  [0.02,0.11]         -    0.05      585        -        -        -    0.5

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  battery_ar_e30/on        vs battery_arprop_e30/on    100    88       3       3        6  1.000
  battery_ar_e30/on        vs battery_clock_e30/on      41    38       0       2        1  0.500
  battery_ar_e30/on        vs battery_none_e30/on      100    50      41       4        5  0.000
  battery_arprop_e30/on    vs battery_clock_e30/on      41    38       0       2        1  0.500
  battery_arprop_e30/on    vs battery_none_e30/on      100    51      40       3        6  0.000
  battery_clock_e30/on     vs battery_none_e30/on       41    23      17       1        0  0.000
  cover_ar_e30/on          vs cover_arprop_e30/on      100    71       1      28        0  0.000
  obs_ar_e30/on            vs obs_arprop_e30/on        100     8       5       8       79  0.581
  ranking_ar_e30/on        vs ranking_arprop_e30/on    100    46      31      19        4  0.119
  ranking_ar_e30/on        vs ranking_none_e30/on       71     4      50       2       15  0.000
  ranking_arprop_e30/on    vs ranking_none_e30/on       71     6      38       0       27  0.000
  rearrange_ar_e30/on      vs rearrange_arprop_e30/on  100    26       3      36       35  0.000
  rearrange_ar_e30/on      vs rearrange_none_e30/on    100     1      28       3       68  0.000
  rearrange_arprop_e30/on  vs rearrange_none_e30/on    100     2      60       2       36  0.000
  swapT_ar_e30/on          vs swapT_arprop_e30/on      100    40      11       9       40  0.824
  swapT_ar_e30/on          vs swapT_none_e30/on        100     1      50       4       45  0.000
  swapT_arprop_e30/on      vs swapT_none_e30/on        100     2      47       3       48  0.000

[summary] 1612 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e6/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-batclk30-s3.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'battery_try'
[queue5] 2026-11-28 14:26:30 A40-batclk30-s3: DONE  battery_try/on n=41  prog=0.00
```

## A40-batclk30-s4 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-batclk30-s4.log):
```
rearrange_none_e30/on   rearrange_blocks 100     0.04  [0.02,0.10]      1.00    0.04      687        -        -        -    0.5
swapT_ar_e30/on         swap_T           100     0.51  [0.41,0.61]         -    0.51      442        -        -        -    0.6
swapT_arprop_e30/on     swap_T           100     0.49  [0.39,0.59]         -    0.49      448        -        -        -    0.6
swapT_none_e30/on       swap_T           100     0.05  [0.02,0.11]         -    0.05      585        -        -        -    0.5

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  battery_ar_e30/on        vs battery_arprop_e30/on    100    88       3       3        6  1.000
  battery_ar_e30/on        vs battery_clock_e30/on      87    80       0       5        2  0.062
  battery_ar_e30/on        vs battery_none_e30/on      100    50      41       4        5  0.000
  battery_arprop_e30/on    vs battery_clock_e30/on      87    80       0       5        2  0.062
  battery_arprop_e30/on    vs battery_none_e30/on      100    51      40       3        6  0.000
  battery_clock_e30/on     vs battery_none_e30/on       87    46      39       1        1  0.000
  cover_ar_e30/on          vs cover_arprop_e30/on      100    71       1      28        0  0.000
  obs_ar_e30/on            vs obs_arprop_e30/on        100     8       5       8       79  0.581
  ranking_ar_e30/on        vs ranking_arprop_e30/on    100    46      31      19        4  0.119
  ranking_ar_e30/on        vs ranking_none_e30/on       74     4      53       2       15  0.000
  ranking_arprop_e30/on    vs ranking_none_e30/on       74     6      39       0       29  0.000
  rearrange_ar_e30/on      vs rearrange_arprop_e30/on  100    26       3      36       35  0.000
  rearrange_ar_e30/on      vs rearrange_none_e30/on    100     1      28       3       68  0.000
  rearrange_arprop_e30/on  vs rearrange_none_e30/on    100     2      60       2       36  0.000
  swapT_ar_e30/on          vs swapT_arprop_e30/on      100    40      11       9       40  0.824
  swapT_ar_e30/on          vs swapT_none_e30/on        100     1      50       4       45  0.000
  swapT_arprop_e30/on      vs swapT_none_e30/on        100     2      47       3       48  0.000

[summary] 1661 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e6/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-batclk30-s4.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'battery_try'
[queue5] 2026-11-28 15:07:35 A40-batclk30-s4: DONE  battery_try/on n=87  prog=0.00
```

## A40-batclk30-s5 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-batclk30-s5.log):
```
rearrange_none_e30/on   rearrange_blocks 100     0.04  [0.02,0.10]      1.00    0.04      687        -        -        -    0.5
swapT_ar_e30/on         swap_T           100     0.51  [0.41,0.61]         -    0.51      442        -        -        -    0.6
swapT_arprop_e30/on     swap_T           100     0.49  [0.39,0.59]         -    0.49      448        -        -        -    0.6
swapT_none_e30/on       swap_T           100     0.05  [0.02,0.11]         -    0.05      585        -        -        -    0.5

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  battery_ar_e30/on        vs battery_arprop_e30/on    100    88       3       3        6  1.000
  battery_ar_e30/on        vs battery_clock_e30/on      83    76       0       5        2  0.062
  battery_ar_e30/on        vs battery_none_e30/on      100    50      41       4        5  0.000
  battery_arprop_e30/on    vs battery_clock_e30/on      83    76       0       5        2  0.062
  battery_arprop_e30/on    vs battery_none_e30/on      100    51      40       3        6  0.000
  battery_clock_e30/on     vs battery_none_e30/on       83    43      38       1        1  0.000
  cover_ar_e30/on          vs cover_arprop_e30/on      100    71       1      28        0  0.000
  obs_ar_e30/on            vs obs_arprop_e30/on        100     8       5       8       79  0.581
  ranking_ar_e30/on        vs ranking_arprop_e30/on    100    46      31      19        4  0.119
  ranking_ar_e30/on        vs ranking_none_e30/on       74     4      53       2       15  0.000
  ranking_arprop_e30/on    vs ranking_none_e30/on       74     6      39       0       29  0.000
  rearrange_ar_e30/on      vs rearrange_arprop_e30/on  100    26       3      36       35  0.000
  rearrange_ar_e30/on      vs rearrange_none_e30/on    100     1      28       3       68  0.000
  rearrange_arprop_e30/on  vs rearrange_none_e30/on    100     2      60       2       36  0.000
  swapT_ar_e30/on          vs swapT_arprop_e30/on      100    40      11       9       40  0.824
  swapT_ar_e30/on          vs swapT_none_e30/on        100     1      50       4       45  0.000
  swapT_arprop_e30/on      vs swapT_none_e30/on        100     2      47       3       48  0.000

[summary] 1657 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e6/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-batclk30-s5.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'battery_try'
[queue5] 2026-11-28 15:03:33 A40-batclk30-s5: DONE  battery_try/on n=83  prog=0.00
```

## A40-batclk30-s6 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-batclk30-s6.log):
```
rearrange_none_e30/on   rearrange_blocks 100     0.04  [0.02,0.10]      1.00    0.04      687        -        -        -    0.5
swapT_ar_e30/on         swap_T           100     0.51  [0.41,0.61]         -    0.51      442        -        -        -    0.6
swapT_arprop_e30/on     swap_T           100     0.49  [0.39,0.59]         -    0.49      448        -        -        -    0.6
swapT_none_e30/on       swap_T           100     0.05  [0.02,0.11]         -    0.05      585        -        -        -    0.5

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  battery_ar_e30/on        vs battery_arprop_e30/on    100    88       3       3        6  1.000
  battery_ar_e30/on        vs battery_clock_e30/on      92    84       0       5        3  0.062
  battery_ar_e30/on        vs battery_none_e30/on      100    50      41       4        5  0.000
  battery_arprop_e30/on    vs battery_clock_e30/on      92    84       0       5        3  0.062
  battery_arprop_e30/on    vs battery_none_e30/on      100    51      40       3        6  0.000
  battery_clock_e30/on     vs battery_none_e30/on       92    47      42       1        2  0.000
  cover_ar_e30/on          vs cover_arprop_e30/on      100    71       1      28        0  0.000
  obs_ar_e30/on            vs obs_arprop_e30/on        100     8       5       8       79  0.581
  ranking_ar_e30/on        vs ranking_arprop_e30/on    100    46      31      19        4  0.119
  ranking_ar_e30/on        vs ranking_none_e30/on       74     4      53       2       15  0.000
  ranking_arprop_e30/on    vs ranking_none_e30/on       74     6      39       0       29  0.000
  rearrange_ar_e30/on      vs rearrange_arprop_e30/on  100    26       3      36       35  0.000
  rearrange_ar_e30/on      vs rearrange_none_e30/on    100     1      28       3       68  0.000
  rearrange_arprop_e30/on  vs rearrange_none_e30/on    100     2      60       2       36  0.000
  swapT_ar_e30/on          vs swapT_arprop_e30/on      100    40      11       9       40  0.824
  swapT_ar_e30/on          vs swapT_none_e30/on        100     1      50       4       45  0.000
  swapT_arprop_e30/on      vs swapT_none_e30/on        100     2      47       3       48  0.000

[summary] 1666 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e6/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-batclk30-s6.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'battery_try'
[queue5] 2026-11-28 15:12:17 A40-batclk30-s6: DONE  battery_try/on n=92  prog=0.00
```

## A40-batclk30-s7 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-batclk30-s7.log):
```
rearrange_none_e30/on   rearrange_blocks 100     0.04  [0.02,0.10]      1.00    0.04      687        -        -        -    0.5
swapT_ar_e30/on         swap_T           100     0.51  [0.41,0.61]         -    0.51      442        -        -        -    0.6
swapT_arprop_e30/on     swap_T           100     0.49  [0.39,0.59]         -    0.49      448        -        -        -    0.6
swapT_none_e30/on       swap_T           100     0.05  [0.02,0.11]         -    0.05      585        -        -        -    0.5

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  battery_ar_e30/on        vs battery_arprop_e30/on    100    88       3       3        6  1.000
  battery_ar_e30/on        vs battery_clock_e30/on      96    88       0       5        3  0.062
  battery_ar_e30/on        vs battery_none_e30/on      100    50      41       4        5  0.000
  battery_arprop_e30/on    vs battery_clock_e30/on      96    88       0       5        3  0.062
  battery_arprop_e30/on    vs battery_none_e30/on      100    51      40       3        6  0.000
  battery_clock_e30/on     vs battery_none_e30/on       96    49      44       1        2  0.000
  cover_ar_e30/on          vs cover_arprop_e30/on      100    71       1      28        0  0.000
  obs_ar_e30/on            vs obs_arprop_e30/on        100     8       5       8       79  0.581
  ranking_ar_e30/on        vs ranking_arprop_e30/on    100    46      31      19        4  0.119
  ranking_ar_e30/on        vs ranking_none_e30/on       74     4      53       2       15  0.000
  ranking_arprop_e30/on    vs ranking_none_e30/on       74     6      39       0       29  0.000
  rearrange_ar_e30/on      vs rearrange_arprop_e30/on  100    26       3      36       35  0.000
  rearrange_ar_e30/on      vs rearrange_none_e30/on    100     1      28       3       68  0.000
  rearrange_arprop_e30/on  vs rearrange_none_e30/on    100     2      60       2       36  0.000
  swapT_ar_e30/on          vs swapT_arprop_e30/on      100    40      11       9       40  0.824
  swapT_ar_e30/on          vs swapT_none_e30/on        100     1      50       4       45  0.000
  swapT_arprop_e30/on      vs swapT_none_e30/on        100     2      47       3       48  0.000

[summary] 1670 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e6/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-batclk30-s7.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'battery_try'
[queue5] 2026-11-28 15:17:25 A40-batclk30-s7: DONE  battery_try/on n=96  prog=0.00
```

## A40-batclk30-s8 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-batclk30-s8.log):
```
rearrange_none_e30/on   rearrange_blocks 100     0.04  [0.02,0.10]      1.00    0.04      687        -        -        -    0.5
swapT_ar_e30/on         swap_T           100     0.51  [0.41,0.61]         -    0.51      442        -        -        -    0.6
swapT_arprop_e30/on     swap_T           100     0.49  [0.39,0.59]         -    0.49      448        -        -        -    0.6
swapT_none_e30/on       swap_T           100     0.05  [0.02,0.11]         -    0.05      585        -        -        -    0.5

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  battery_ar_e30/on        vs battery_arprop_e30/on    100    88       3       3        6  1.000
  battery_ar_e30/on        vs battery_clock_e30/on     100    91       0       5        4  0.062
  battery_ar_e30/on        vs battery_none_e30/on      100    50      41       4        5  0.000
  battery_arprop_e30/on    vs battery_clock_e30/on     100    91       0       5        4  0.062
  battery_arprop_e30/on    vs battery_none_e30/on      100    51      40       3        6  0.000
  battery_clock_e30/on     vs battery_none_e30/on      100    52      44       2        2  0.000
  cover_ar_e30/on          vs cover_arprop_e30/on      100    71       1      28        0  0.000
  obs_ar_e30/on            vs obs_arprop_e30/on        100     8       5       8       79  0.581
  ranking_ar_e30/on        vs ranking_arprop_e30/on    100    46      31      19        4  0.119
  ranking_ar_e30/on        vs ranking_none_e30/on       75     4      54       2       15  0.000
  ranking_arprop_e30/on    vs ranking_none_e30/on       75     6      40       0       29  0.000
  rearrange_ar_e30/on      vs rearrange_arprop_e30/on  100    26       3      36       35  0.000
  rearrange_ar_e30/on      vs rearrange_none_e30/on    100     1      28       3       68  0.000
  rearrange_arprop_e30/on  vs rearrange_none_e30/on    100     2      60       2       36  0.000
  swapT_ar_e30/on          vs swapT_arprop_e30/on      100    40      11       9       40  0.824
  swapT_ar_e30/on          vs swapT_none_e30/on        100     1      50       4       45  0.000
  swapT_arprop_e30/on      vs swapT_none_e30/on        100     2      47       3       48  0.000

[summary] 1675 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e6/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-batclk30-s8.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'battery_try'
[queue5] 2026-11-28 15:23:50 A40-batclk30-s8: DONE  battery_try/on n=100  prog=0.00
```

## A40-batclk30-s9 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-batclk30-s9.log):
```
rearrange_none_e30/on   rearrange_blocks 100     0.04  [0.02,0.10]      1.00    0.04      687        -        -        -    0.5
swapT_ar_e30/on         swap_T           100     0.51  [0.41,0.61]         -    0.51      442        -        -        -    0.6
swapT_arprop_e30/on     swap_T           100     0.49  [0.39,0.59]         -    0.49      448        -        -        -    0.6
swapT_none_e30/on       swap_T           100     0.05  [0.02,0.11]         -    0.05      585        -        -        -    0.5

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  battery_ar_e30/on        vs battery_arprop_e30/on    100    88       3       3        6  1.000
  battery_ar_e30/on        vs battery_clock_e30/on      99    90       0       5        4  0.062
  battery_ar_e30/on        vs battery_none_e30/on      100    50      41       4        5  0.000
  battery_arprop_e30/on    vs battery_clock_e30/on      99    90       0       5        4  0.062
  battery_arprop_e30/on    vs battery_none_e30/on      100    51      40       3        6  0.000
  battery_clock_e30/on     vs battery_none_e30/on       99    51      44       2        2  0.000
  cover_ar_e30/on          vs cover_arprop_e30/on      100    71       1      28        0  0.000
  obs_ar_e30/on            vs obs_arprop_e30/on        100     8       5       8       79  0.581
  ranking_ar_e30/on        vs ranking_arprop_e30/on    100    46      31      19        4  0.119
  ranking_ar_e30/on        vs ranking_none_e30/on       75     4      54       2       15  0.000
  ranking_arprop_e30/on    vs ranking_none_e30/on       75     6      40       0       29  0.000
  rearrange_ar_e30/on      vs rearrange_arprop_e30/on  100    26       3      36       35  0.000
  rearrange_ar_e30/on      vs rearrange_none_e30/on    100     1      28       3       68  0.000
  rearrange_arprop_e30/on  vs rearrange_none_e30/on    100     2      60       2       36  0.000
  swapT_ar_e30/on          vs swapT_arprop_e30/on      100    40      11       9       40  0.824
  swapT_ar_e30/on          vs swapT_none_e30/on        100     1      50       4       45  0.000
  swapT_arprop_e30/on      vs swapT_none_e30/on        100     2      47       3       48  0.000

[summary] 1674 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e6/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-batclk30-s9.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'battery_try'
[queue5] 2026-11-28 15:23:41 A40-batclk30-s9: DONE  battery_try/on n=99  prog=0.00
```

## A40-BATCLK-report (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-BATCLK-report.log):
```

[queue5] 2026-11-28 15:24:07 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/v20_verdict.py batclk
{"run": "main-table cell battery clock (described)", "finished": {"battery_clock_e30": 100}, "success_1_100": 96, "against_battery_ar_e30": {"scenes": 100, "new": 96, "ref": 91, "D": 0.05, "ci95": [0.01, 0.1], "only_new": 5, "only_ref": 0}, "against_battery_arprop_e30": {"scenes": 100, "new": 96, "ref": 91, "D": 0.05, "ci95": [0.01, 0.1], "only_new": 5, "only_ref": 0}, "verdict": "DESCRIBED"}
V20 BATCLK: DESCRIBED
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-BATCLK-report.log):
```

[pool] 2026-11-28 15:24:04 exec A40-BATCLK-report GPU None 
[pool] 2026-11-28 15:24:07 A40-BATCLK-report: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-BATCLK-report.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-BATCLK-report.md
[queue5] 2026-11-28 15:24:12 A40-BATCLK-report: PASS  rc=0
```

## A40-fetch-ranking_none-e30 (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-ranking_none-e30.log):
```
[fetch] 2026-11-28 00:43:13 waiting for exports/ranking_none_e30 on the relay
[fetch] 2026-11-28 00:48:14 waiting for exports/ranking_none_e30 on the relay
[fetch] 2026-11-28 00:53:14 waiting for exports/ranking_none_e30 on the relay
[fetch] 2026-11-28 00:58:15 waiting for exports/ranking_none_e30 on the relay
[fetch] 2026-11-28 01:03:15 waiting for exports/ranking_none_e30 on the relay
[fetch] 2026-11-28 01:08:16 waiting for exports/ranking_none_e30 on the relay
[fetch] 2026-11-28 01:13:17 waiting for exports/ranking_none_e30 on the relay
[fetch] 2026-11-28 01:18:17 waiting for exports/ranking_none_e30 on the relay
[fetch] 2026-11-28 01:23:18 waiting for exports/ranking_none_e30 on the relay
[fetch] 2026-11-28 01:28:18 waiting for exports/ranking_none_e30 on the relay
[fetch] 2026-11-28 01:33:19 waiting for exports/ranking_none_e30 on the relay
[fetch] 2026-11-28 01:38:20 waiting for exports/ranking_none_e30 on the relay
[fetch] 2026-11-28 01:43:20 waiting for exports/ranking_none_e30 on the relay
[fetch] 2026-11-28 01:48:21 waiting for exports/ranking_none_e30 on the relay
[fetch] 2026-11-28 01:53:21 waiting for exports/ranking_none_e30 on the relay
[fetch] disk before: /dev/sdb         19T   11T  6.7T  62% /workspace/FastWAM-memory2
[fetch] 2026-11-28 01:58:22 fetching ranking_none_e30 (attempt 1)
[relay] get hhyfred/memwam-fullft/exports/ranking_none_e30/export_e30.pt -> /workspace/FastWAM-memory2/outputs/fullft/exports/ranking_none_e30/export_e30.pt (12042063331 bytes)
[relay] get hhyfred/memwam-fullft/exports/ranking_none_e30/export_e30.pt.sha256 -> /workspace/FastWAM-memory2/outputs/fullft/exports/ranking_none_e30/export_e30.pt.sha256 (80 bytes)
export_e30.pt: OK
total 11759844
drwxr-xr-x  2 root root        4096 Nov 28 02:06 .
drwxr-xr-x 99 root root        4096 Nov 28 01:58 ..
-rw-r--r--  1 root root 12042063331 Nov 28 02:05 export_e30.pt
-rw-r--r--  1 root root          80 Nov 28 02:06 export_e30.pt.sha256
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-ranking_none-e30.log):
```

[pool] 2026-11-24 18:52:56 exec A40-fetch-ranking_none-e30 GPU None 
[pool] 2026-11-24 18:52:59 A40-fetch-ranking_none-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-ranking_none-e30.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-ranking_none-e30.md
[queue5] 2026-11-28 10:06:18 A40-fetch-ranking_none-e30: PASS  rc=0
```

## A40-ranknone30-smoke (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-ranknone30-smoke.log):
```
ranking_none_e30_smoke/onblocks_ranking_try   1     1.00  [0.21,1.00]      1.00    0.00     1672        -        -        -    0.5
rearrange_ar_e30_smoke/onrearrange_blocks   1     0.00  [0.00,0.79]      1.00    0.00      700        -        -        -    0.6
rearrange_arprop_e30_smoke/onrearrange_blocks   1     1.00  [0.21,1.00]      1.00    1.00      389        -        -        -    0.6
rearrange_none_e30_smoke/onrearrange_blocks   1     0.00  [0.00,0.79]      1.00    0.00      700        -        -        -    0.5
swapT_ar_e30_smoke/on   swap_T             1     0.00  [0.00,0.79]         -    0.00      600        -        -        -    0.5
swapT_arprop_e30_smoke/onswap_T             1     0.00  [0.00,0.79]         -    0.00      600        -        -        -    0.6
swapT_none_e30_smoke/on swap_T             1     0.00  [0.00,0.79]         -    0.00      600        -        -        -    0.5

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  battery_ar_e30_smoke/on  vs battery_arprop_e30_smoke/on   1     1       0       0        0  1.000
  battery_ar_e30_smoke/on  vs battery_none_e30_smoke/on   1     1       0       0        0  1.000
  battery_arprop_e30_smoke/on vs battery_none_e30_smoke/on   1     1       0       0        0  1.000
  cover_ar_e30_smoke/on    vs cover_arprop_e30_smoke/on   1     1       0       0        0  1.000
  obs_ar_e30_smoke/on      vs obs_arprop_e30_smoke/on    1     0       0       0        1  1.000
  ranking_ar_e30_smoke/on  vs ranking_arprop_e30_smoke/on   1     0       0       1        0  1.000
  ranking_ar_e30_smoke/on  vs ranking_none_e30_smoke/on   1     0       0       1        0  1.000
  ranking_arprop_e30_smoke/on vs ranking_none_e30_smoke/on   1     1       0       0        0  1.000
  rearrange_ar_e30_smoke/on vs rearrange_arprop_e30_smoke/on   1     0       0       1        0  1.000
  rearrange_ar_e30_smoke/on vs rearrange_none_e30_smoke/on   1     0       0       0        1  1.000
  rearrange_arprop_e30_smoke/on vs rearrange_none_e30_smoke/on   1     0       1       0        0  1.000
  swapT_ar_e30_smoke/on    vs swapT_arprop_e30_smoke/on   1     0       0       0        1  1.000
  swapT_ar_e30_smoke/on    vs swapT_none_e30_smoke/on    1     0       0       0        1  1.000
  swapT_arprop_e30_smoke/on vs swapT_none_e30_smoke/on    1     0       0       0        1  1.000

[summary] 16 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e6smoke/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-ranknone30-smoke.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'blocks_ranking_try'
[queue5] 2026-11-28 10:18:32 A40-ranknone30-smoke: PASS  blocks_ranking_try/on n=1  prog=0.00
```

## A40-ranknone30-s0 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-ranknone30-s0.log):
```
ranking_none_e30/on     blocks_ranking_try  60     0.08  [0.04,0.18]      1.00    0.00     3374        -        -        -    0.5
rearrange_ar_e30/on     rearrange_blocks 100     0.29  [0.21,0.39]      1.00    0.29      611        -        -        -    0.6
rearrange_arprop_e30/on rearrange_blocks 100     0.62  [0.52,0.71]      1.00    0.62      509        -        -        -    0.6
rearrange_none_e30/on   rearrange_blocks 100     0.04  [0.02,0.10]      1.00    0.04      687        -        -        -    0.5
swapT_ar_e30/on         swap_T           100     0.51  [0.41,0.61]         -    0.51      442        -        -        -    0.6
swapT_arprop_e30/on     swap_T           100     0.49  [0.39,0.59]         -    0.49      448        -        -        -    0.6
swapT_none_e30/on       swap_T           100     0.05  [0.02,0.11]         -    0.05      585        -        -        -    0.5

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  battery_ar_e30/on        vs battery_arprop_e30/on    100    88       3       3        6  1.000
  battery_ar_e30/on        vs battery_none_e30/on      100    50      41       4        5  0.000
  battery_arprop_e30/on    vs battery_none_e30/on      100    51      40       3        6  0.000
  cover_ar_e30/on          vs cover_arprop_e30/on      100    71       1      28        0  0.000
  obs_ar_e30/on            vs obs_arprop_e30/on        100     8       5       8       79  0.581
  ranking_ar_e30/on        vs ranking_arprop_e30/on    100    46      31      19        4  0.119
  ranking_ar_e30/on        vs ranking_none_e30/on       60     4      42       1       13  0.000
  ranking_arprop_e30/on    vs ranking_none_e30/on       60     5      33       0       22  0.000
  rearrange_ar_e30/on      vs rearrange_arprop_e30/on  100    26       3      36       35  0.000
  rearrange_ar_e30/on      vs rearrange_none_e30/on    100     1      28       3       68  0.000
  rearrange_arprop_e30/on  vs rearrange_none_e30/on    100     2      60       2       36  0.000
  swapT_ar_e30/on          vs swapT_arprop_e30/on      100    40      11       9       40  0.824
  swapT_ar_e30/on          vs swapT_none_e30/on        100     1      50       4       45  0.000
  swapT_arprop_e30/on      vs swapT_none_e30/on        100     2      47       3       48  0.000

[summary] 1560 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e6/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-ranknone30-s0.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'blocks_ranking_try'
[queue5] 2026-11-28 13:28:11 A40-ranknone30-s0: DONE  blocks_ranking_try/on n=60  prog=0.00
```

## A40-ranknone30-s1 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-ranknone30-s1.log):
```
ranking_none_e30/on     blocks_ranking_try  59     0.08  [0.04,0.18]      1.00    0.00     3372        -        -        -    0.5
rearrange_ar_e30/on     rearrange_blocks 100     0.29  [0.21,0.39]      1.00    0.29      611        -        -        -    0.6
rearrange_arprop_e30/on rearrange_blocks 100     0.62  [0.52,0.71]      1.00    0.62      509        -        -        -    0.6
rearrange_none_e30/on   rearrange_blocks 100     0.04  [0.02,0.10]      1.00    0.04      687        -        -        -    0.5
swapT_ar_e30/on         swap_T           100     0.51  [0.41,0.61]         -    0.51      442        -        -        -    0.6
swapT_arprop_e30/on     swap_T           100     0.49  [0.39,0.59]         -    0.49      448        -        -        -    0.6
swapT_none_e30/on       swap_T           100     0.05  [0.02,0.11]         -    0.05      585        -        -        -    0.5

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  battery_ar_e30/on        vs battery_arprop_e30/on    100    88       3       3        6  1.000
  battery_ar_e30/on        vs battery_none_e30/on      100    50      41       4        5  0.000
  battery_arprop_e30/on    vs battery_none_e30/on      100    51      40       3        6  0.000
  cover_ar_e30/on          vs cover_arprop_e30/on      100    71       1      28        0  0.000
  obs_ar_e30/on            vs obs_arprop_e30/on        100     8       5       8       79  0.581
  ranking_ar_e30/on        vs ranking_arprop_e30/on    100    46      31      19        4  0.119
  ranking_ar_e30/on        vs ranking_none_e30/on       59     4      41       1       13  0.000
  ranking_arprop_e30/on    vs ranking_none_e30/on       59     5      32       0       22  0.000
  rearrange_ar_e30/on      vs rearrange_arprop_e30/on  100    26       3      36       35  0.000
  rearrange_ar_e30/on      vs rearrange_none_e30/on    100     1      28       3       68  0.000
  rearrange_arprop_e30/on  vs rearrange_none_e30/on    100     2      60       2       36  0.000
  swapT_ar_e30/on          vs swapT_arprop_e30/on      100    40      11       9       40  0.824
  swapT_ar_e30/on          vs swapT_none_e30/on        100     1      50       4       45  0.000
  swapT_arprop_e30/on      vs swapT_none_e30/on        100     2      47       3       48  0.000

[summary] 1559 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e6/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-ranknone30-s1.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'blocks_ranking_try'
[queue5] 2026-11-28 13:26:39 A40-ranknone30-s1: DONE  blocks_ranking_try/on n=59  prog=0.00
```

## A40-ranknone30-s2 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-ranknone30-s2.log):
```
ranking_none_e30/on     blocks_ranking_try  64     0.08  [0.03,0.17]      1.00    0.00     3382        -        -        -    0.5
rearrange_ar_e30/on     rearrange_blocks 100     0.29  [0.21,0.39]      1.00    0.29      611        -        -        -    0.6
rearrange_arprop_e30/on rearrange_blocks 100     0.62  [0.52,0.71]      1.00    0.62      509        -        -        -    0.6
rearrange_none_e30/on   rearrange_blocks 100     0.04  [0.02,0.10]      1.00    0.04      687        -        -        -    0.5
swapT_ar_e30/on         swap_T           100     0.51  [0.41,0.61]         -    0.51      442        -        -        -    0.6
swapT_arprop_e30/on     swap_T           100     0.49  [0.39,0.59]         -    0.49      448        -        -        -    0.6
swapT_none_e30/on       swap_T           100     0.05  [0.02,0.11]         -    0.05      585        -        -        -    0.5

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  battery_ar_e30/on        vs battery_arprop_e30/on    100    88       3       3        6  1.000
  battery_ar_e30/on        vs battery_none_e30/on      100    50      41       4        5  0.000
  battery_arprop_e30/on    vs battery_none_e30/on      100    51      40       3        6  0.000
  cover_ar_e30/on          vs cover_arprop_e30/on      100    71       1      28        0  0.000
  obs_ar_e30/on            vs obs_arprop_e30/on        100     8       5       8       79  0.581
  ranking_ar_e30/on        vs ranking_arprop_e30/on    100    46      31      19        4  0.119
  ranking_ar_e30/on        vs ranking_none_e30/on       64     4      45       1       14  0.000
  ranking_arprop_e30/on    vs ranking_none_e30/on       64     5      35       0       24  0.000
  rearrange_ar_e30/on      vs rearrange_arprop_e30/on  100    26       3      36       35  0.000
  rearrange_ar_e30/on      vs rearrange_none_e30/on    100     1      28       3       68  0.000
  rearrange_arprop_e30/on  vs rearrange_none_e30/on    100     2      60       2       36  0.000
  swapT_ar_e30/on          vs swapT_arprop_e30/on      100    40      11       9       40  0.824
  swapT_ar_e30/on          vs swapT_none_e30/on        100     1      50       4       45  0.000
  swapT_arprop_e30/on      vs swapT_none_e30/on        100     2      47       3       48  0.000

[summary] 1564 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e6/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-ranknone30-s2.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'blocks_ranking_try'
[queue5] 2026-11-28 13:37:57 A40-ranknone30-s2: DONE  blocks_ranking_try/on n=64  prog=0.00
```

## A40-ranknone30-s3 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-ranknone30-s3.log):
```
ranking_none_e30/on     blocks_ranking_try  65     0.08  [0.03,0.17]      1.00    0.00     3384        -        -        -    0.5
rearrange_ar_e30/on     rearrange_blocks 100     0.29  [0.21,0.39]      1.00    0.29      611        -        -        -    0.6
rearrange_arprop_e30/on rearrange_blocks 100     0.62  [0.52,0.71]      1.00    0.62      509        -        -        -    0.6
rearrange_none_e30/on   rearrange_blocks 100     0.04  [0.02,0.10]      1.00    0.04      687        -        -        -    0.5
swapT_ar_e30/on         swap_T           100     0.51  [0.41,0.61]         -    0.51      442        -        -        -    0.6
swapT_arprop_e30/on     swap_T           100     0.49  [0.39,0.59]         -    0.49      448        -        -        -    0.6
swapT_none_e30/on       swap_T           100     0.05  [0.02,0.11]         -    0.05      585        -        -        -    0.5

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  battery_ar_e30/on        vs battery_arprop_e30/on    100    88       3       3        6  1.000
  battery_ar_e30/on        vs battery_none_e30/on      100    50      41       4        5  0.000
  battery_arprop_e30/on    vs battery_none_e30/on      100    51      40       3        6  0.000
  cover_ar_e30/on          vs cover_arprop_e30/on      100    71       1      28        0  0.000
  obs_ar_e30/on            vs obs_arprop_e30/on        100     8       5       8       79  0.581
  ranking_ar_e30/on        vs ranking_arprop_e30/on    100    46      31      19        4  0.119
  ranking_ar_e30/on        vs ranking_none_e30/on       65     4      46       1       14  0.000
  ranking_arprop_e30/on    vs ranking_none_e30/on       65     5      36       0       24  0.000
  rearrange_ar_e30/on      vs rearrange_arprop_e30/on  100    26       3      36       35  0.000
  rearrange_ar_e30/on      vs rearrange_none_e30/on    100     1      28       3       68  0.000
  rearrange_arprop_e30/on  vs rearrange_none_e30/on    100     2      60       2       36  0.000
  swapT_ar_e30/on          vs swapT_arprop_e30/on      100    40      11       9       40  0.824
  swapT_ar_e30/on          vs swapT_none_e30/on        100     1      50       4       45  0.000
  swapT_arprop_e30/on      vs swapT_none_e30/on        100     2      47       3       48  0.000

[summary] 1565 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e6/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-ranknone30-s3.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'blocks_ranking_try'
[queue5] 2026-11-28 13:38:42 A40-ranknone30-s3: DONE  blocks_ranking_try/on n=65  prog=0.00
```

## A40-ranknone30-s4 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-ranknone30-s4.log):
```
ranking_none_e30/on     blocks_ranking_try  63     0.08  [0.03,0.17]      1.00    0.00     3380        -        -        -    0.5
rearrange_ar_e30/on     rearrange_blocks 100     0.29  [0.21,0.39]      1.00    0.29      611        -        -        -    0.6
rearrange_arprop_e30/on rearrange_blocks 100     0.62  [0.52,0.71]      1.00    0.62      509        -        -        -    0.6
rearrange_none_e30/on   rearrange_blocks 100     0.04  [0.02,0.10]      1.00    0.04      687        -        -        -    0.5
swapT_ar_e30/on         swap_T           100     0.51  [0.41,0.61]         -    0.51      442        -        -        -    0.6
swapT_arprop_e30/on     swap_T           100     0.49  [0.39,0.59]         -    0.49      448        -        -        -    0.6
swapT_none_e30/on       swap_T           100     0.05  [0.02,0.11]         -    0.05      585        -        -        -    0.5

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  battery_ar_e30/on        vs battery_arprop_e30/on    100    88       3       3        6  1.000
  battery_ar_e30/on        vs battery_none_e30/on      100    50      41       4        5  0.000
  battery_arprop_e30/on    vs battery_none_e30/on      100    51      40       3        6  0.000
  cover_ar_e30/on          vs cover_arprop_e30/on      100    71       1      28        0  0.000
  obs_ar_e30/on            vs obs_arprop_e30/on        100     8       5       8       79  0.581
  ranking_ar_e30/on        vs ranking_arprop_e30/on    100    46      31      19        4  0.119
  ranking_ar_e30/on        vs ranking_none_e30/on       63     4      45       1       13  0.000
  ranking_arprop_e30/on    vs ranking_none_e30/on       63     5      35       0       23  0.000
  rearrange_ar_e30/on      vs rearrange_arprop_e30/on  100    26       3      36       35  0.000
  rearrange_ar_e30/on      vs rearrange_none_e30/on    100     1      28       3       68  0.000
  rearrange_arprop_e30/on  vs rearrange_none_e30/on    100     2      60       2       36  0.000
  swapT_ar_e30/on          vs swapT_arprop_e30/on      100    40      11       9       40  0.824
  swapT_ar_e30/on          vs swapT_none_e30/on        100     1      50       4       45  0.000
  swapT_arprop_e30/on      vs swapT_none_e30/on        100     2      47       3       48  0.000

[summary] 1563 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e6/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-ranknone30-s4.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'blocks_ranking_try'
[queue5] 2026-11-28 13:37:23 A40-ranknone30-s4: DONE  blocks_ranking_try/on n=63  prog=0.00
```

## A40-ranknone30-s5 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-ranknone30-s5.log):
```
rearrange_none_e30/on   rearrange_blocks 100     0.04  [0.02,0.10]      1.00    0.04      687        -        -        -    0.5
swapT_ar_e30/on         swap_T           100     0.51  [0.41,0.61]         -    0.51      442        -        -        -    0.6
swapT_arprop_e30/on     swap_T           100     0.49  [0.39,0.59]         -    0.49      448        -        -        -    0.6
swapT_none_e30/on       swap_T           100     0.05  [0.02,0.11]         -    0.05      585        -        -        -    0.5

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  battery_ar_e30/on        vs battery_arprop_e30/on    100    88       3       3        6  1.000
  battery_ar_e30/on        vs battery_clock_e30/on      30    28       0       1        1  1.000
  battery_ar_e30/on        vs battery_none_e30/on      100    50      41       4        5  0.000
  battery_arprop_e30/on    vs battery_clock_e30/on      30    28       0       1        1  1.000
  battery_arprop_e30/on    vs battery_none_e30/on      100    51      40       3        6  0.000
  battery_clock_e30/on     vs battery_none_e30/on       30    16      13       1        0  0.002
  cover_ar_e30/on          vs cover_arprop_e30/on      100    71       1      28        0  0.000
  obs_ar_e30/on            vs obs_arprop_e30/on        100     8       5       8       79  0.581
  ranking_ar_e30/on        vs ranking_arprop_e30/on    100    46      31      19        4  0.119
  ranking_ar_e30/on        vs ranking_none_e30/on       69     4      48       2       15  0.000
  ranking_arprop_e30/on    vs ranking_none_e30/on       69     6      37       0       26  0.000
  rearrange_ar_e30/on      vs rearrange_arprop_e30/on  100    26       3      36       35  0.000
  rearrange_ar_e30/on      vs rearrange_none_e30/on    100     1      28       3       68  0.000
  rearrange_arprop_e30/on  vs rearrange_none_e30/on    100     2      60       2       36  0.000
  swapT_ar_e30/on          vs swapT_arprop_e30/on      100    40      11       9       40  0.824
  swapT_ar_e30/on          vs swapT_none_e30/on        100     1      50       4       45  0.000
  swapT_arprop_e30/on      vs swapT_none_e30/on        100     2      47       3       48  0.000

[summary] 1599 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e6/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-ranknone30-s5.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'blocks_ranking_try'
[queue5] 2026-11-28 14:15:29 A40-ranknone30-s5: DONE  blocks_ranking_try/on n=69  prog=0.00
```

## A40-ranknone30-s6 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-ranknone30-s6.log):
```
rearrange_none_e30/on   rearrange_blocks 100     0.04  [0.02,0.10]      1.00    0.04      687        -        -        -    0.5
swapT_ar_e30/on         swap_T           100     0.51  [0.41,0.61]         -    0.51      442        -        -        -    0.6
swapT_arprop_e30/on     swap_T           100     0.49  [0.39,0.59]         -    0.49      448        -        -        -    0.6
swapT_none_e30/on       swap_T           100     0.05  [0.02,0.11]         -    0.05      585        -        -        -    0.5

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  battery_ar_e30/on        vs battery_arprop_e30/on    100    88       3       3        6  1.000
  battery_ar_e30/on        vs battery_clock_e30/on      53    47       0       4        2  0.125
  battery_ar_e30/on        vs battery_none_e30/on      100    50      41       4        5  0.000
  battery_arprop_e30/on    vs battery_clock_e30/on      53    47       0       4        2  0.125
  battery_arprop_e30/on    vs battery_none_e30/on      100    51      40       3        6  0.000
  battery_clock_e30/on     vs battery_none_e30/on       53    29      22       1        1  0.000
  cover_ar_e30/on          vs cover_arprop_e30/on      100    71       1      28        0  0.000
  obs_ar_e30/on            vs obs_arprop_e30/on        100     8       5       8       79  0.581
  ranking_ar_e30/on        vs ranking_arprop_e30/on    100    46      31      19        4  0.119
  ranking_ar_e30/on        vs ranking_none_e30/on       73     4      52       2       15  0.000
  ranking_arprop_e30/on    vs ranking_none_e30/on       73     6      38       0       29  0.000
  rearrange_ar_e30/on      vs rearrange_arprop_e30/on  100    26       3      36       35  0.000
  rearrange_ar_e30/on      vs rearrange_none_e30/on    100     1      28       3       68  0.000
  rearrange_arprop_e30/on  vs rearrange_none_e30/on    100     2      60       2       36  0.000
  swapT_ar_e30/on          vs swapT_arprop_e30/on      100    40      11       9       40  0.824
  swapT_ar_e30/on          vs swapT_none_e30/on        100     1      50       4       45  0.000
  swapT_arprop_e30/on      vs swapT_none_e30/on        100     2      47       3       48  0.000

[summary] 1626 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e6/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-ranknone30-s6.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'blocks_ranking_try'
[queue5] 2026-11-28 14:41:12 A40-ranknone30-s6: DONE  blocks_ranking_try/on n=73  prog=0.00
```

## A40-ranknone30-s7 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-ranknone30-s7.log):
```
rearrange_none_e30/on   rearrange_blocks 100     0.04  [0.02,0.10]      1.00    0.04      687        -        -        -    0.5
swapT_ar_e30/on         swap_T           100     0.51  [0.41,0.61]         -    0.51      442        -        -        -    0.6
swapT_arprop_e30/on     swap_T           100     0.49  [0.39,0.59]         -    0.49      448        -        -        -    0.6
swapT_none_e30/on       swap_T           100     0.05  [0.02,0.11]         -    0.05      585        -        -        -    0.5

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  battery_ar_e30/on        vs battery_arprop_e30/on    100    88       3       3        6  1.000
  battery_ar_e30/on        vs battery_clock_e30/on     100    91       0       5        4  0.062
  battery_ar_e30/on        vs battery_none_e30/on      100    50      41       4        5  0.000
  battery_arprop_e30/on    vs battery_clock_e30/on     100    91       0       5        4  0.062
  battery_arprop_e30/on    vs battery_none_e30/on      100    51      40       3        6  0.000
  battery_clock_e30/on     vs battery_none_e30/on      100    52      44       2        2  0.000
  cover_ar_e30/on          vs cover_arprop_e30/on      100    71       1      28        0  0.000
  obs_ar_e30/on            vs obs_arprop_e30/on        100     8       5       8       79  0.581
  ranking_ar_e30/on        vs ranking_arprop_e30/on    100    46      31      19        4  0.119
  ranking_ar_e30/on        vs ranking_none_e30/on       90     4      65       2       19  0.000
  ranking_arprop_e30/on    vs ranking_none_e30/on       90     6      51       0       33  0.000
  rearrange_ar_e30/on      vs rearrange_arprop_e30/on  100    26       3      36       35  0.000
  rearrange_ar_e30/on      vs rearrange_none_e30/on    100     1      28       3       68  0.000
  rearrange_arprop_e30/on  vs rearrange_none_e30/on    100     2      60       2       36  0.000
  swapT_ar_e30/on          vs swapT_arprop_e30/on      100    40      11       9       40  0.824
  swapT_ar_e30/on          vs swapT_none_e30/on        100     1      50       4       45  0.000
  swapT_arprop_e30/on      vs swapT_none_e30/on        100     2      47       3       48  0.000

[summary] 1690 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e6/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-ranknone30-s7.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'blocks_ranking_try'
[queue5] 2026-11-28 17:28:00 A40-ranknone30-s7: DONE  blocks_ranking_try/on n=90  prog=0.00
```

## A40-ranknone30-s8 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-ranknone30-s8.log):
```
rearrange_none_e30/on   rearrange_blocks 100     0.04  [0.02,0.10]      1.00    0.04      687        -        -        -    0.5
swapT_ar_e30/on         swap_T           100     0.51  [0.41,0.61]         -    0.51      442        -        -        -    0.6
swapT_arprop_e30/on     swap_T           100     0.49  [0.39,0.59]         -    0.49      448        -        -        -    0.6
swapT_none_e30/on       swap_T           100     0.05  [0.02,0.11]         -    0.05      585        -        -        -    0.5

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  battery_ar_e30/on        vs battery_arprop_e30/on    100    88       3       3        6  1.000
  battery_ar_e30/on        vs battery_clock_e30/on     100    91       0       5        4  0.062
  battery_ar_e30/on        vs battery_none_e30/on      100    50      41       4        5  0.000
  battery_arprop_e30/on    vs battery_clock_e30/on     100    91       0       5        4  0.062
  battery_arprop_e30/on    vs battery_none_e30/on      100    51      40       3        6  0.000
  battery_clock_e30/on     vs battery_none_e30/on      100    52      44       2        2  0.000
  cover_ar_e30/on          vs cover_arprop_e30/on      100    71       1      28        0  0.000
  obs_ar_e30/on            vs obs_arprop_e30/on        100     8       5       8       79  0.581
  ranking_ar_e30/on        vs ranking_arprop_e30/on    100    46      31      19        4  0.119
  ranking_ar_e30/on        vs ranking_none_e30/on       99     4      72       2       21  0.000
  ranking_arprop_e30/on    vs ranking_none_e30/on       99     6      58       0       35  0.000
  rearrange_ar_e30/on      vs rearrange_arprop_e30/on  100    26       3      36       35  0.000
  rearrange_ar_e30/on      vs rearrange_none_e30/on    100     1      28       3       68  0.000
  rearrange_arprop_e30/on  vs rearrange_none_e30/on    100     2      60       2       36  0.000
  swapT_ar_e30/on          vs swapT_arprop_e30/on      100    40      11       9       40  0.824
  swapT_ar_e30/on          vs swapT_none_e30/on        100     1      50       4       45  0.000
  swapT_arprop_e30/on      vs swapT_none_e30/on        100     2      47       3       48  0.000

[summary] 1699 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e6/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-ranknone30-s8.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'blocks_ranking_try'
[queue5] 2026-11-28 18:59:52 A40-ranknone30-s8: DONE  blocks_ranking_try/on n=99  prog=0.00
```

## A40-ranknone30-s9 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-ranknone30-s9.log):
```
rearrange_none_e30/on   rearrange_blocks 100     0.04  [0.02,0.10]      1.00    0.04      687        -        -        -    0.5
swapT_ar_e30/on         swap_T           100     0.51  [0.41,0.61]         -    0.51      442        -        -        -    0.6
swapT_arprop_e30/on     swap_T           100     0.49  [0.39,0.59]         -    0.49      448        -        -        -    0.6
swapT_none_e30/on       swap_T           100     0.05  [0.02,0.11]         -    0.05      585        -        -        -    0.5

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  battery_ar_e30/on        vs battery_arprop_e30/on    100    88       3       3        6  1.000
  battery_ar_e30/on        vs battery_clock_e30/on     100    91       0       5        4  0.062
  battery_ar_e30/on        vs battery_none_e30/on      100    50      41       4        5  0.000
  battery_arprop_e30/on    vs battery_clock_e30/on     100    91       0       5        4  0.062
  battery_arprop_e30/on    vs battery_none_e30/on      100    51      40       3        6  0.000
  battery_clock_e30/on     vs battery_none_e30/on      100    52      44       2        2  0.000
  cover_ar_e30/on          vs cover_arprop_e30/on      100    71       1      28        0  0.000
  obs_ar_e30/on            vs obs_arprop_e30/on        100     8       5       8       79  0.581
  ranking_ar_e30/on        vs ranking_arprop_e30/on    100    46      31      19        4  0.119
  ranking_ar_e30/on        vs ranking_none_e30/on      100     4      73       2       21  0.000
  ranking_arprop_e30/on    vs ranking_none_e30/on      100     6      59       0       35  0.000
  rearrange_ar_e30/on      vs rearrange_arprop_e30/on  100    26       3      36       35  0.000
  rearrange_ar_e30/on      vs rearrange_none_e30/on    100     1      28       3       68  0.000
  rearrange_arprop_e30/on  vs rearrange_none_e30/on    100     2      60       2       36  0.000
  swapT_ar_e30/on          vs swapT_arprop_e30/on      100    40      11       9       40  0.824
  swapT_ar_e30/on          vs swapT_none_e30/on        100     1      50       4       45  0.000
  swapT_arprop_e30/on      vs swapT_none_e30/on        100     2      47       3       48  0.000

[summary] 1700 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e6/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-ranknone30-s9.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'blocks_ranking_try'
[queue5] 2026-11-28 19:01:28 A40-ranknone30-s9: DONE  blocks_ranking_try/on n=100  prog=0.00
```

## A40-RANKNONE-report (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-RANKNONE-report.log):
```

[queue5] 2026-11-28 19:01:43 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/v20_verdict.py ranknone
{"run": "main-table cell ranking without history (described)", "finished": {"ranking_none_e30": 100}, "success_1_100": 6, "against_ranking_ar_e30": {"scenes": 100, "new": 6, "ref": 77, "D": -0.71, "ci95": [-0.8, -0.61], "only_new": 2, "only_ref": 73}, "against_ranking_arprop_e30": {"scenes": 100, "new": 6, "ref": 65, "D": -0.59, "ci95": [-0.68, -0.49], "only_new": 0, "only_ref": 59}, "verdict": "DESCRIBED"}
V20 RANKNONE: DESCRIBED
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-RANKNONE-report.log):
```

[pool] 2026-11-28 19:01:38 exec A40-RANKNONE-report GPU None 
[pool] 2026-11-28 19:01:43 A40-RANKNONE-report: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-RANKNONE-report.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-RANKNONE-report.md
[queue5] 2026-11-28 19:01:48 A40-RANKNONE-report: PASS  rc=0
```

## A40-fetch-battery_count-e30 (running, attempt 2, GPU None)

failures:
```
[
 {
  "attempt": 1,
  "gpu": null,
  "time": "2026-11-22 12:44:30",
  "why": "exec process died without a verdict (killed / crash / container restart)"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-battery_count-e30.log):
```
[fetch] 2026-11-28 15:48:58 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 15:53:59 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 15:59:00 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 16:04:00 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 16:09:01 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 16:14:01 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 16:19:02 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 16:24:02 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 16:29:03 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 16:34:03 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 16:39:04 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 16:44:04 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 16:49:05 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 16:54:06 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 16:59:06 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 17:04:07 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 17:09:07 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 17:14:08 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 17:19:08 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 17:24:09 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 17:29:09 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 17:34:10 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 17:39:11 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 17:44:11 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-28 17:49:12 waiting for exports/battery_count_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-battery_count-e30.log):
```

[pool] 2026-11-19 19:17:58 exec A40-fetch-battery_count-e30 GPU None 
[pool] 2026-11-19 19:18:00 A40-fetch-battery_count-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-battery_count-e30.log

[pool] 2026-11-22 12:45:35 exec A40-fetch-battery_count-e30 GPU None 
[pool] 2026-11-22 12:45:37 A40-fetch-battery_count-e30: start (attempt 2/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-battery_count-e30.log
```

## A40-fetch-obs_cf200-e10 (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-obs_cf200-e10.log):
```
[fetch] 2026-11-27 19:38:17 waiting for exports/obs_cf200_e10 on the relay
[fetch] 2026-11-27 19:43:17 waiting for exports/obs_cf200_e10 on the relay
[fetch] 2026-11-27 19:48:18 waiting for exports/obs_cf200_e10 on the relay
[fetch] 2026-11-27 19:53:18 waiting for exports/obs_cf200_e10 on the relay
[fetch] 2026-11-27 19:58:19 waiting for exports/obs_cf200_e10 on the relay
[fetch] 2026-11-27 20:03:19 waiting for exports/obs_cf200_e10 on the relay
[fetch] 2026-11-27 20:08:20 waiting for exports/obs_cf200_e10 on the relay
[fetch] 2026-11-27 20:13:20 waiting for exports/obs_cf200_e10 on the relay
[fetch] 2026-11-27 20:18:21 waiting for exports/obs_cf200_e10 on the relay
[fetch] 2026-11-27 20:23:21 waiting for exports/obs_cf200_e10 on the relay
[fetch] 2026-11-27 20:28:22 waiting for exports/obs_cf200_e10 on the relay
[fetch] 2026-11-27 20:33:22 waiting for exports/obs_cf200_e10 on the relay
[fetch] 2026-11-27 20:38:23 waiting for exports/obs_cf200_e10 on the relay
[fetch] 2026-11-27 20:43:24 waiting for exports/obs_cf200_e10 on the relay
[fetch] 2026-11-27 20:48:24 waiting for exports/obs_cf200_e10 on the relay
[fetch] disk before: /dev/sdb         19T   11T  6.7T  62% /workspace/FastWAM-memory2
[fetch] 2026-11-27 20:53:25 fetching obs_cf200_e10 (attempt 1)
[relay] get hhyfred/memwam-fullft/exports/obs_cf200_e10/export_e10.pt -> /workspace/FastWAM-memory2/outputs/fullft/exports/obs_cf200_e10/export_e10.pt (12042063331 bytes)
[relay] get hhyfred/memwam-fullft/exports/obs_cf200_e10/export_e10.pt.sha256 -> /workspace/FastWAM-memory2/outputs/fullft/exports/obs_cf200_e10/export_e10.pt.sha256 (80 bytes)
export_e10.pt: OK
total 11759844
drwxr-xr-x  2 root root        4096 Nov 27 21:02 .
drwxr-xr-x 98 root root        4096 Nov 27 20:53 ..
-rw-r--r--  1 root root 12042063331 Nov 27 21:02 export_e10.pt
-rw-r--r--  1 root root          80 Nov 27 21:02 export_e10.pt.sha256
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-obs_cf200-e10.log):
```

[pool] 2026-11-27 12:46:30 exec A40-fetch-obs_cf200-e10 GPU None 
[pool] 2026-11-27 12:46:34 A40-fetch-obs_cf200-e10: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-obs_cf200-e10.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-obs_cf200-e10.md
[queue5] 2026-11-28 05:02:21 A40-fetch-obs_cf200-e10: PASS  rc=0
```

## A40-v21-obs_cf200-e10-s0 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e10-s0.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on       84    18       9      34       23  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on       84    21       8      31       24  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on       84    33      14      19       18  0.487
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on       84    13       4      39       28  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on       84    38      14      14       18  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on       84    21      17      31       15  0.059

[summary] 694 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-e10-s0.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 05:49:46 A40-v21-obs_cf200-e10-s0: DONE  observe_and_pickup/on n=10  prog=0.00
```

## A40-v21-obs_cf200-e10-s1 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e10-s1.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 746 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-e10-s1.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 06:15:27 A40-v21-obs_cf200-e10-s1: DONE  observe_and_pickup/on n=46  prog=0.00
```

## A40-v21-obs_cf200-e10-s2 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e10-s2.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 759 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-e10-s2.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 06:20:44 A40-v21-obs_cf200-e10-s2: DONE  observe_and_pickup/on n=59  prog=0.00
```

## A40-v21-obs_cf200-e10-s3 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e10-s3.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 755 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-e10-s3.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 06:19:14 A40-v21-obs_cf200-e10-s3: DONE  observe_and_pickup/on n=55  prog=0.00
```

## A40-v21-obs_cf200-e10-s4 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e10-s4.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 776 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-e10-s4.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 06:28:02 A40-v21-obs_cf200-e10-s4: DONE  observe_and_pickup/on n=76  prog=0.00
```

## A40-v21-obs_cf200-e10-s5 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e10-s5.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 782 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-e10-s5.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 06:30:22 A40-v21-obs_cf200-e10-s5: DONE  observe_and_pickup/on n=82  prog=0.00
```

## A40-v21-obs_cf200-e10-s6 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e10-s6.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 789 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-e10-s6.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 06:34:02 A40-v21-obs_cf200-e10-s6: DONE  observe_and_pickup/on n=89  prog=0.00
```

## A40-v21-obs_cf200-e10-s7 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e10-s7.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 792 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-e10-s7.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 06:35:46 A40-v21-obs_cf200-e10-s7: DONE  observe_and_pickup/on n=92  prog=0.00
```

## A40-v21-obs_cf200-e10-s8 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e10-s8.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 799 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-e10-s8.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 06:43:02 A40-v21-obs_cf200-e10-s8: DONE  observe_and_pickup/on n=99  prog=0.00
```

## A40-v21-obs_cf200-e10-s9 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e10-s9.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 800 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-e10-s9.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 06:44:32 A40-v21-obs_cf200-e10-s9: DONE  observe_and_pickup/on n=100  prog=0.00
```

## A40-fetch-obs_cf200-e20 (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-obs_cf200-e20.log):
```
[fetch] 2026-11-28 03:04:10 waiting for exports/obs_cf200_e20 on the relay
[fetch] 2026-11-28 03:09:10 waiting for exports/obs_cf200_e20 on the relay
[fetch] 2026-11-28 03:14:11 waiting for exports/obs_cf200_e20 on the relay
[fetch] 2026-11-28 03:19:12 waiting for exports/obs_cf200_e20 on the relay
[fetch] 2026-11-28 03:24:12 waiting for exports/obs_cf200_e20 on the relay
[fetch] 2026-11-28 03:29:13 waiting for exports/obs_cf200_e20 on the relay
[fetch] 2026-11-28 03:34:13 waiting for exports/obs_cf200_e20 on the relay
[fetch] 2026-11-28 03:39:14 waiting for exports/obs_cf200_e20 on the relay
[fetch] 2026-11-28 03:44:14 waiting for exports/obs_cf200_e20 on the relay
[fetch] 2026-11-28 03:49:15 waiting for exports/obs_cf200_e20 on the relay
[fetch] 2026-11-28 03:54:15 waiting for exports/obs_cf200_e20 on the relay
[fetch] 2026-11-28 03:59:16 waiting for exports/obs_cf200_e20 on the relay
[fetch] 2026-11-28 04:04:16 waiting for exports/obs_cf200_e20 on the relay
[fetch] 2026-11-28 04:09:17 waiting for exports/obs_cf200_e20 on the relay
[fetch] 2026-11-28 04:14:18 waiting for exports/obs_cf200_e20 on the relay
[fetch] disk before: /dev/sdb         19T   11T  6.7T  62% /workspace/FastWAM-memory2
[fetch] 2026-11-28 04:19:18 fetching obs_cf200_e20 (attempt 1)
[relay] get hhyfred/memwam-fullft/exports/obs_cf200_e20/export_e20.pt -> /workspace/FastWAM-memory2/outputs/fullft/exports/obs_cf200_e20/export_e20.pt (12042063395 bytes)
[relay] get hhyfred/memwam-fullft/exports/obs_cf200_e20/export_e20.pt.sha256 -> /workspace/FastWAM-memory2/outputs/fullft/exports/obs_cf200_e20/export_e20.pt.sha256 (80 bytes)
export_e20.pt: OK
total 11759844
drwxr-xr-x   2 root root        4096 Nov 28 04:27 .
drwxr-xr-x 101 root root        4096 Nov 28 04:19 ..
-rw-r--r--   1 root root 12042063395 Nov 28 04:26 export_e20.pt
-rw-r--r--   1 root root          80 Nov 28 04:27 export_e20.pt.sha256
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-obs_cf200-e20.log):
```

[pool] 2026-11-27 12:46:30 exec A40-fetch-obs_cf200-e20 GPU None 
[pool] 2026-11-27 12:46:34 A40-fetch-obs_cf200-e20: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-obs_cf200-e20.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-obs_cf200-e20.md
[queue5] 2026-11-28 12:27:14 A40-fetch-obs_cf200-e20: PASS  rc=0
```

## A40-v21-obs_cf200-e20-s0 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e20-s0.log):
```
paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  obs_cf200_e10/on         vs obs_cf200_e20/on          24     2       3       9       10  0.146
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 824 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-e20-s0.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 15:36:01 A40-v21-obs_cf200-e20-s0: DONE  observe_and_pickup/on n=24  prog=0.00
```

## A40-v21-obs_cf200-e20-s1 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e20-s1.log):
```
paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  obs_cf200_e10/on         vs obs_cf200_e20/on          35     2       8      13       12  0.383
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 835 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-e20-s1.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 15:43:35 A40-v21-obs_cf200-e20-s1: DONE  observe_and_pickup/on n=35  prog=0.00
```

## A40-v21-obs_cf200-e20-s2 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e20-s2.log):
```
paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  obs_cf200_e10/on         vs obs_cf200_e20/on          44     2      10      16       16  0.327
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 844 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-e20-s2.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 15:49:59 A40-v21-obs_cf200-e20-s2: DONE  observe_and_pickup/on n=44  prog=0.00
```

## A40-v21-obs_cf200-e20-s3 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e20-s3.log):
```
paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  obs_cf200_e10/on         vs obs_cf200_e20/on          44     2      10      16       16  0.327
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 844 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-e20-s3.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 15:49:58 A40-v21-obs_cf200-e20-s3: DONE  observe_and_pickup/on n=44  prog=0.00
```

## A40-v21-obs_cf200-e20-s4 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e20-s4.log):
```
paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  obs_cf200_e10/on         vs obs_cf200_e20/on          50     2      11      20       17  0.150
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 850 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-e20-s4.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 16:00:41 A40-v21-obs_cf200-e20-s4: DONE  observe_and_pickup/on n=50  prog=0.00
```

## A40-v21-obs_cf200-e20-s5 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e20-s5.log):
```
  obs_cf200_e10/on         vs obs_cf200_e20/on          85     9      14      31       31  0.016
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 885 episodes, 1 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/obs_cf200_e20/on/observe_and_pickup/seed_4300099/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-e20-s5.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 16:26:35 A40-v21-obs_cf200-e20-s5: DONE  observe_and_pickup/on n=85  prog=0.00; errors=1
```

## A40-v21-obs_cf200-e20-s6 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e20-s6.log):
```
  obs_cf200_e10/on         vs obs_cf200_e20/on          87     9      14      31       33  0.016
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 887 episodes, 1 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/obs_cf200_e20/on/observe_and_pickup/seed_4300099/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-e20-s6.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 16:28:19 A40-v21-obs_cf200-e20-s6: DONE  observe_and_pickup/on n=87  prog=0.00; errors=1
```

## A40-v21-obs_cf200-e20-s7 (pending, attempt 2, GPU 6)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 6,
  "time": "2026-11-28 16:24:50",
  "why": "1 episodes ended with ERROR.json (re-run retries only those)"
 },
 {
  "attempt": 2,
  "gpu": 6,
  "time": "2026-11-29 00:28:35",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e20-s7.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-e20-s7.log):
```

[pool] 2026-11-28 16:03:37 exec A40-v21-obs_cf200-e20-s7 GPU 6 
[pool] 2026-11-28 16:03:41 A40-v21-obs_cf200-e20-s7: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e20-s7.log
[pool] 2026-11-28 16:24:50 A40-v21-obs_cf200-e20-s7: attempt 1 failed (1 episodes ended with ERROR.json (re-run retries only those)); retry after 16:34 on any empty GPU

[pool] 2026-11-29 00:27:54 exec A40-v21-obs_cf200-e20-s7 GPU 6 
[pool] 2026-11-29 00:27:59 A40-v21-obs_cf200-e20-s7: start (attempt 2/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e20-s7.log
[pool] 2026-11-29 00:28:35 A40-v21-obs_cf200-e20-s7: attempt 2 failed (rc=1: Python exception); retry after 00:38 on any empty GPU
```

## A40-v21-obs_cf200-e20-s8 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e20-s8.log):
```
  obs_cf200_e10/on         vs obs_cf200_e20/on          89     9      15      31       34  0.026
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e20/on       100     8      23      26       43  0.775
  rearr_ar_pw_e10/on       vs rearr_ar_pw_e30/on       100    18      13      37       32  0.001
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e10/on   100    11      20       7       62  0.019
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e20/on   100    26       5      36       33  0.000
  rearr_ar_pw_e10/on       vs rearr_arprop_pw_e30/on   100    16      15      29       40  0.049
  rearr_ar_pw_e10/on       vs rearr_pw_s18_e30/on      100    21      10      40       29  0.000
  rearr_ar_pw_e20/on       vs rearr_ar_pw_e30/on       100    22      12      33       33  0.002
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e10/on   100     7      27      11       55  0.014
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e20/on   100    26       8      36       30  0.000
  rearr_ar_pw_e20/on       vs rearr_arprop_pw_e30/on   100    20      14      25       41  0.108
  rearr_ar_pw_e20/on       vs rearr_pw_s18_e30/on      100    25       9      36       30  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e10/on   100     7      48      11       34  0.000
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e20/on   100    38      17      24       21  0.349
  rearr_ar_pw_e30/on       vs rearr_arprop_pw_e30/on   100    24      31      21       24  0.212
  rearr_ar_pw_e30/on       vs rearr_pw_s18_e30/on      100    39      16      22       23  0.418
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e20/on   100    14       4      48       34  0.000
  rearr_arprop_pw_e10/on   vs rearr_arprop_pw_e30/on   100     8      10      37       45  0.000
  rearr_arprop_pw_e10/on   vs rearr_pw_s18_e30/on      100    14       4      47       35  0.000
  rearr_arprop_pw_e20/on   vs rearr_arprop_pw_e30/on   100    35      27      10       28  0.008
  rearr_arprop_pw_e20/on   vs rearr_pw_s18_e30/on      100    44      18      17       21  1.000
  rearr_arprop_pw_e30/on   vs rearr_pw_s18_e30/on      100    24      21      37       18  0.048

[summary] 889 episodes, 1 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/SUMMARY.json
   ERROR /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v21/obs_cf200_e20/on/observe_and_pickup/seed_4300099/ERROR.json: \n  File "/workspace/FastWAM/resources/RMBench/envs/_base_task.py", line 451, in get_obs\n    self.cameras.update_picture()\n  File "/workspace/FastWAM/resources/RMBench/envs/camera/camera.py", line 276, in update_picture\n    self.left_camera.take_picture()\nRuntimeError: cannot create buffer\n\n')
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-e20-s8.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 16:33:19 A40-v21-obs_cf200-e20-s8: DONE  observe_and_pickup/on n=89  prog=0.00; errors=1
```

## A40-v21-obs_cf200-e20-s9 (pending, attempt 1, GPU 7)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 7,
  "time": "2026-11-29 00:28:36",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e20-s9.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-v21-obs_cf200-e20-s9.log):
```

[pool] 2026-11-29 00:27:54 exec A40-v21-obs_cf200-e20-s9 GPU 7 
[pool] 2026-11-29 00:27:59 A40-v21-obs_cf200-e20-s9: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-v21-obs_cf200-e20-s9.log
[pool] 2026-11-29 00:28:36 A40-v21-obs_cf200-e20-s9: attempt 1 failed (rc=1: Python exception); retry after 00:38 on any empty GPU
```

## A40-fs-obs_s800-e5-s7 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fs-obs_s800-e5-s7.log):
```
  obs_s200_e10/on          vs obs_s800_e5/on            89     7       6      34       42  0.000
  obs_s200_e20/on          vs obs_s200_e30/on          100    10       3       5       82  0.727
  obs_s200_e20/on          vs obs_s800_e10/on          100    10       3      39       48  0.000
  obs_s200_e20/on          vs obs_s800_e5/on            89     8       5      33       43  0.000
  obs_s200_e30/on          vs obs_s800_e10/on          100    12       3      37       48  0.000
  obs_s200_e30/on          vs obs_s800_e5/on            89    11       4      30       44  0.000
  obs_s800_e10/on          vs obs_s800_e5/on            89    28      16      13       32  0.711
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2289 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fs-obs_s800-e5-s7.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 01:56:08 A40-fs-obs_s800-e5-s7: DONE  observe_and_pickup/on n=89  prog=0.00
```

## A40-fs-obs_s800-e5-s8 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fs-obs_s800-e5-s8.log):
```
  obs_s200_e10/on          vs obs_s800_e5/on            99     7       7      39       46  0.000
  obs_s200_e20/on          vs obs_s200_e30/on          100    10       3       5       82  0.727
  obs_s200_e20/on          vs obs_s800_e10/on          100    10       3      39       48  0.000
  obs_s200_e20/on          vs obs_s800_e5/on            99     8       5      38       48  0.000
  obs_s200_e30/on          vs obs_s800_e10/on          100    12       3      37       48  0.000
  obs_s200_e30/on          vs obs_s800_e5/on            99    11       4      35       49  0.000
  obs_s800_e10/on          vs obs_s800_e5/on            99    31      17      15       36  0.860
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2299 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fs-obs_s800-e5-s8.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 02:06:15 A40-fs-obs_s800-e5-s8: DONE  observe_and_pickup/on n=99  prog=0.00
```

## A40-fs-obs_s800-e5-s9 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fs-obs_s800-e5-s9.log):
```
  obs_s200_e10/on          vs obs_s800_e5/on           100     7       7      39       47  0.000
  obs_s200_e20/on          vs obs_s200_e30/on          100    10       3       5       82  0.727
  obs_s200_e20/on          vs obs_s800_e10/on          100    10       3      39       48  0.000
  obs_s200_e20/on          vs obs_s800_e5/on           100     8       5      38       49  0.000
  obs_s200_e30/on          vs obs_s800_e10/on          100    12       3      37       48  0.000
  obs_s200_e30/on          vs obs_s800_e5/on           100    11       4      35       50  0.000
  obs_s800_e10/on          vs obs_s800_e5/on           100    31      18      15       36  0.728
  press_told_e10/on        vs press_told_e20/on        100     0       0      12       88  0.000
  press_told_e10/on        vs press_told_e30/on        100     0       0      22       78  0.000
  press_told_e20/on        vs press_told_e30/on        100     2      10      20       68  0.099
  rearr_pw_e10/on          vs rearr_pw_e20/on          100    11       3      67       19  0.000
  rearr_pw_e10/on          vs rearr_pw_e30/on          100    14       0      79        7  0.000
  rearr_pw_e20/on          vs rearr_pw_e30/on          100    74       4      19        3  0.003
  swapT_arprop_h2_e30/on   vs swapT_long_e45/on        100    24      15      14       47  1.000
  swapT_arprop_h2_e30/on   vs swapT_long_e60/on        100    27      12       9       52  0.664
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e45/on   100    30       9      20       41  0.061
  swapT_arprop_h2_e30/on   vs swapT_long_h100_e60/on   100    25      14      13       48  1.000
  swapT_long_e45/on        vs swapT_long_e60/on        100    25      13      11       51  0.839
  swapT_long_e45/on        vs swapT_long_h100_e45/on   100    31       7      19       43  0.029
  swapT_long_e45/on        vs swapT_long_h100_e60/on   100    28      10      10       52  1.000
  swapT_long_e60/on        vs swapT_long_h100_e45/on   100    27       9      23       41  0.020
  swapT_long_e60/on        vs swapT_long_h100_e60/on   100    25      11      13       51  0.839
  swapT_long_h100_e45/on   vs swapT_long_h100_e60/on   100    31      19       7       43  0.029

[summary] 2300 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/v20/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fs-obs_s800-e5-s9.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'observe_and_pickup'
[queue5] 2026-11-28 02:08:00 A40-fs-obs_s800-e5-s9: DONE  observe_and_pickup/on n=100  prog=0.00
```

## A40-FS-report-obs_s800-e5 (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-FS-report-obs_s800-e5.log):
```

[queue5] 2026-11-28 02:08:22 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/v21_verdict.py fs
{"run": "find-same push (described)", "reference_obs_s800_e10": "49/100", "runs": {"obs_s200_e30": {"finished": 100, "success": 15, "against_obs_s800_e10": {"scenes": 100, "new": 15, "ref": 49, "D": -0.34, "ci95": [-0.45, -0.24], "only_new": 3, "only_ref": 37}, "against_obs_ar_e30": {"scenes": 100, "new": 15, "ref": 13, "D": 0.02, "ci95": [-0.07, 0.11], "only_new": 12, "only_ref": 10}}, "obs_s800_e5": {"finished": 100, "success": 46, "against_obs_s800_e10": {"scenes": 100, "new": 46, "ref": 49, "D": -0.03, "ci95": [-0.14, 0.08], "only_new": 15, "only_ref": 18}, "against_obs_ar_e30": {"scenes": 100, "new": 46, "ref": 13, "D": 0.33, "ci95": [0.21, 0.45], "only_new": 41, "only_ref": 8}}, "obs_s800_e10": {"finished": 100, "success": 49, "against_obs_s800_e10": null, "against_obs_ar_e30": {"scenes": 100, "new": 49, "ref": 13, "D": 0.36, "ci95": [0.24, 0.47], "only_new": 41, "only_ref": 5}}}, "verdict": "DESCRIBED"}
V21 FS: DESCRIBED
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-FS-report-obs_s800-e5.log):
```

[pool] 2026-11-28 02:08:18 exec A40-FS-report-obs_s800-e5 GPU None 
[pool] 2026-11-28 02:08:22 A40-FS-report-obs_s800-e5: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-FS-report-obs_s800-e5.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-FS-report-obs_s800-e5.md
[queue5] 2026-11-28 02:08:28 A40-FS-report-obs_s800-e5: PASS  rc=0
```

## A40-fetch-obs_s800_20-e10 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-obs_s800_20-e10.log):
```
[fetch] 2026-11-28 15:50:44 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 15:55:47 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 16:00:48 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 16:05:48 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 16:10:49 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 16:15:49 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 16:20:50 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 16:25:50 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 16:30:51 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 16:35:51 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 16:40:52 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 16:45:53 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 16:50:53 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 16:55:54 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 17:00:54 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 17:05:55 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 17:10:55 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 17:15:56 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 17:20:56 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 17:25:57 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 17:30:57 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 17:35:58 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 17:40:58 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 17:45:59 waiting for exports/obs_s800_20_e10 on the relay
[fetch] 2026-11-28 17:50:59 waiting for exports/obs_s800_20_e10 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-obs_s800_20-e10.log):
```

[pool] 2026-11-27 13:16:45 exec A40-fetch-obs_s800_20-e10 GPU None 
[pool] 2026-11-27 13:16:49 A40-fetch-obs_s800_20-e10: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-obs_s800_20-e10.log
```

## A40-fetch-obs_s800_20-e20 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-obs_s800_20-e20.log):
```
[fetch] 2026-11-28 15:50:49 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 15:55:50 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 16:00:50 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 16:05:51 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 16:10:51 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 16:15:52 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 16:20:52 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 16:25:53 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 16:30:53 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 16:35:54 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 16:40:54 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 16:45:55 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 16:50:56 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 16:55:56 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 17:00:57 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 17:05:57 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 17:10:58 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 17:15:59 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 17:20:59 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 17:26:00 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 17:31:00 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 17:36:01 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 17:41:01 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 17:46:02 waiting for exports/obs_s800_20_e20 on the relay
[fetch] 2026-11-28 17:51:02 waiting for exports/obs_s800_20_e20 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-obs_s800_20-e20.log):
```

[pool] 2026-11-27 13:16:45 exec A40-fetch-obs_s800_20-e20 GPU None 
[pool] 2026-11-27 13:16:49 A40-fetch-obs_s800_20-e20: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-obs_s800_20-e20.log
```

## A40-fetch-obs_s800_s18-e10 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-obs_s800_s18-e10.log):
```
[fetch] 2026-11-28 15:50:43 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 15:55:43 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 16:00:44 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 16:05:44 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 16:10:45 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 16:15:45 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 16:20:46 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 16:25:47 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 16:30:47 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 16:35:48 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 16:40:48 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 16:45:49 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 16:50:49 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 16:55:50 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 17:00:50 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 17:05:51 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 17:10:52 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 17:15:52 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 17:20:53 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 17:25:53 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 17:30:54 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 17:35:54 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 17:40:55 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 17:45:56 waiting for exports/obs_s800_s18_e10 on the relay
[fetch] 2026-11-28 17:50:56 waiting for exports/obs_s800_s18_e10 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-obs_s800_s18-e10.log):
```

[pool] 2026-11-27 13:16:45 exec A40-fetch-obs_s800_s18-e10 GPU None 
[pool] 2026-11-27 13:16:49 A40-fetch-obs_s800_s18-e10: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-obs_s800_s18-e10.log
```

## A40-fetch-obs_s1600-e5 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-obs_s1600-e5.log):
```
[fetch] 2026-11-28 15:50:42 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 15:55:43 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 16:00:44 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 16:05:44 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 16:10:45 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 16:15:45 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 16:20:46 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 16:25:46 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 16:30:47 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 16:35:47 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 16:40:48 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 16:45:49 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 16:50:49 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 16:55:50 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 17:00:50 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 17:05:51 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 17:10:51 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 17:15:52 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 17:20:53 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 17:25:53 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 17:30:54 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 17:35:54 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 17:40:55 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 17:45:55 waiting for exports/obs_s1600_e5 on the relay
[fetch] 2026-11-28 17:50:56 waiting for exports/obs_s1600_e5 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-obs_s1600-e5.log):
```

[pool] 2026-11-27 13:16:45 exec A40-fetch-obs_s1600-e5 GPU None 
[pool] 2026-11-27 13:16:49 A40-fetch-obs_s1600-e5: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-obs_s1600-e5.log
```

## A40-fetch-obs_s1600-e10 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-obs_s1600-e10.log):
```
[fetch] 2026-11-28 15:50:43 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 15:55:43 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 16:00:44 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 16:05:44 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 16:10:45 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 16:15:46 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 16:20:46 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 16:25:47 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 16:30:47 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 16:35:48 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 16:40:48 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 16:45:49 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 16:50:49 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 16:55:50 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 17:00:50 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 17:05:51 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 17:10:52 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 17:15:52 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 17:20:53 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 17:25:53 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 17:30:54 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 17:35:54 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 17:40:55 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 17:45:56 waiting for exports/obs_s1600_e10 on the relay
[fetch] 2026-11-28 17:50:56 waiting for exports/obs_s1600_e10 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-obs_s1600-e10.log):
```

[pool] 2026-11-27 13:16:45 exec A40-fetch-obs_s1600-e10 GPU None 
[pool] 2026-11-27 13:16:49 A40-fetch-obs_s1600-e10: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-obs_s1600-e10.log
```

## A40-fetch-ar2_prop_s18-e30 (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-ar2_prop_s18-e30.log):
```

[queue5] 2026-11-28 16:48:24 $ bash -c RUN=ar2_prop_s18 TAG=e30 bash /workspace/FastWAM-memory2/scripts/fullft/export_fetch.sh
[fetch] disk before: /dev/sdb         19T   11T  6.6T  62% /workspace/FastWAM-memory2
[fetch] 2026-11-28 08:48:25 fetching ar2_prop_s18_e30 (attempt 1)
[relay] get hhyfred/memwam-fullft/exports/ar2_prop_s18_e30/export_e30.pt -> /workspace/FastWAM-memory2/outputs/fullft/exports/ar2_prop_s18_e30/export_e30.pt (12042506501 bytes)
[relay] get hhyfred/memwam-fullft/exports/ar2_prop_s18_e30/export_e30.pt.sha256 -> /workspace/FastWAM-memory2/outputs/fullft/exports/ar2_prop_s18_e30/export_e30.pt.sha256 (80 bytes)
export_e30.pt: OK
total 11760280
drwxr-xr-x   2 root root        4096 Nov 28 08:58 .
drwxr-xr-x 104 root root        4096 Nov 28 08:53 ..
-rw-r--r--   1 root root 12042506501 Nov 28 08:58 export_e30.pt
-rw-r--r--   1 root root          80 Nov 28 08:58 export_e30.pt.sha256
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-ar2_prop_s18-e30.log):
```

[pool] 2026-11-28 16:48:20 exec A40-fetch-ar2_prop_s18-e30 GPU None 
[pool] 2026-11-28 16:48:24 A40-fetch-ar2_prop_s18-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-ar2_prop_s18-e30.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-ar2_prop_s18-e30.md
[queue5] 2026-11-28 16:58:58 A40-fetch-ar2_prop_s18-e30: PASS  rc=0
```

## A40-fetch-ar2_prop_s18-e10 (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-ar2_prop_s18-e10.log):
```

[queue5] 2026-11-28 16:48:24 $ bash -c RUN=ar2_prop_s18 TAG=e10 bash /workspace/FastWAM-memory2/scripts/fullft/export_fetch.sh
[fetch] 2026-11-28 08:48:25 waiting for exports/ar2_prop_s18_e10 on the relay
[fetch] disk before: /dev/sdb         19T   11T  6.6T  62% /workspace/FastWAM-memory2
[fetch] 2026-11-28 08:53:25 fetching ar2_prop_s18_e10 (attempt 1)
[relay] get hhyfred/memwam-fullft/exports/ar2_prop_s18_e10/export_e10.pt -> /workspace/FastWAM-memory2/outputs/fullft/exports/ar2_prop_s18_e10/export_e10.pt (12042506309 bytes)
[relay] get hhyfred/memwam-fullft/exports/ar2_prop_s18_e10/export_e10.pt.sha256 -> /workspace/FastWAM-memory2/outputs/fullft/exports/ar2_prop_s18_e10/export_e10.pt.sha256 (80 bytes)
export_e10.pt: OK
total 11760280
drwxr-xr-x   2 root root        4096 Nov 28 09:03 .
drwxr-xr-x 104 root root        4096 Nov 28 08:53 ..
-rw-r--r--   1 root root 12042506309 Nov 28 09:03 export_e10.pt
-rw-r--r--   1 root root          80 Nov 28 09:03 export_e10.pt.sha256
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-ar2_prop_s18-e10.log):
```

[pool] 2026-11-28 16:48:20 exec A40-fetch-ar2_prop_s18-e10 GPU None 
[pool] 2026-11-28 16:48:24 A40-fetch-ar2_prop_s18-e10: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-ar2_prop_s18-e10.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-ar2_prop_s18-e10.md
[queue5] 2026-11-28 17:03:42 A40-fetch-ar2_prop_s18-e10: PASS  rc=0
```

## A40-d11-ar2s18-e30-put-s0 (pending, attempt 1, GPU 4)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 4,
  "time": "2026-11-29 00:30:41",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d11-ar2s18-e30-put-s0.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d11-ar2s18-e30-put-s0.log):
```

[pool] 2026-11-29 00:28:29 exec A40-d11-ar2s18-e30-put-s0 GPU 4 
[pool] 2026-11-29 00:28:35 A40-d11-ar2s18-e30-put-s0: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d11-ar2s18-e30-put-s0.log
[pool] 2026-11-29 00:30:41 A40-d11-ar2s18-e30-put-s0: attempt 1 failed (rc=1: Python exception); retry after 00:40 on any empty GPU
```

## A40-d11-ar2s18-e30-put-s1 (pending, attempt 1, GPU 7)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 7,
  "time": "2026-11-29 00:30:56",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d11-ar2s18-e30-put-s1.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d11-ar2s18-e30-put-s1.log):
```

[pool] 2026-11-29 00:30:15 exec A40-d11-ar2s18-e30-put-s1 GPU 7 
[pool] 2026-11-29 00:30:20 A40-d11-ar2s18-e30-put-s1: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d11-ar2s18-e30-put-s1.log
[pool] 2026-11-29 00:30:56 A40-d11-ar2s18-e30-put-s1: attempt 1 failed (rc=1: Python exception); retry after 00:40 on any empty GPU
```

## A40-d11-ar2s18-e30-put-s2 (pending, attempt 1, GPU 4)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 4,
  "time": "2026-11-29 00:32:42",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d11-ar2s18-e30-put-s2.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d11-ar2s18-e30-put-s2.log):
```

[pool] 2026-11-29 00:32:02 exec A40-d11-ar2s18-e30-put-s2 GPU 4 
[pool] 2026-11-29 00:32:07 A40-d11-ar2s18-e30-put-s2: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d11-ar2s18-e30-put-s2.log
[pool] 2026-11-29 00:32:42 A40-d11-ar2s18-e30-put-s2: attempt 1 failed (rc=1: Python exception); retry after 00:42 on any empty GPU
```

## A40-d11-ar2s18-e30-put-s3 (pending, attempt 1, GPU 5)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 5,
  "time": "2026-11-29 00:33:18",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d11-ar2s18-e30-put-s3.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d11-ar2s18-e30-put-s3.log):
```

[pool] 2026-11-29 00:32:38 exec A40-d11-ar2s18-e30-put-s3 GPU 5 
[pool] 2026-11-29 00:32:43 A40-d11-ar2s18-e30-put-s3: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d11-ar2s18-e30-put-s3.log
[pool] 2026-11-29 00:33:18 A40-d11-ar2s18-e30-put-s3: attempt 1 failed (rc=1: Python exception); retry after 00:43 on any empty GPU
```

## A40-d11-ar2s18-e30-put-s4 (pending, attempt 1, GPU 6)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 6,
  "time": "2026-11-29 00:33:18",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d11-ar2s18-e30-put-s4.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d11-ar2s18-e30-put-s4.log):
```

[pool] 2026-11-29 00:32:38 exec A40-d11-ar2s18-e30-put-s4 GPU 6 
[pool] 2026-11-29 00:32:43 A40-d11-ar2s18-e30-put-s4: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d11-ar2s18-e30-put-s4.log
[pool] 2026-11-29 00:33:18 A40-d11-ar2s18-e30-put-s4: attempt 1 failed (rc=1: Python exception); retry after 00:43 on any empty GPU
```

## A40-d11-ar2s18-e30-put-s5 (pending, attempt 1, GPU 7)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 7,
  "time": "2026-11-29 00:33:19",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d11-ar2s18-e30-put-s5.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d11-ar2s18-e30-put-s5.log):
```

[pool] 2026-11-29 00:32:38 exec A40-d11-ar2s18-e30-put-s5 GPU 7 
[pool] 2026-11-29 00:32:43 A40-d11-ar2s18-e30-put-s5: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d11-ar2s18-e30-put-s5.log
[pool] 2026-11-29 00:33:19 A40-d11-ar2s18-e30-put-s5: attempt 1 failed (rc=1: Python exception); retry after 00:43 on any empty GPU
```

## A40-d11-ar2s18-e30-put-s6 (pending, attempt 1, GPU 7)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 7,
  "time": "2026-11-29 00:35:41",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d11-ar2s18-e30-put-s6.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d11-ar2s18-e30-put-s6.log):
```

[pool] 2026-11-29 00:35:00 exec A40-d11-ar2s18-e30-put-s6 GPU 7 
[pool] 2026-11-29 00:35:05 A40-d11-ar2s18-e30-put-s6: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d11-ar2s18-e30-put-s6.log
[pool] 2026-11-29 00:35:41 A40-d11-ar2s18-e30-put-s6: attempt 1 failed (rc=1: Python exception); retry after 00:45 on any empty GPU
```

## A40-d11-ar2s18-e30-put-s7 (pending, attempt 1, GPU 7)

failures:
```
[
 {
  "attempt": 1,
  "gpu": 7,
  "time": "2026-11-29 00:38:04",
  "why": "rc=1: Python exception"
 }
]
```
job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d11-ar2s18-e30-put-s7.log):
```
    model.to(device=device, dtype=torch.bfloat16).eval()
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1340, in to
    return self._apply(convert)
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/workspace/FastWAM-memory2/src/fastwam/models/wan22/wan_video_dit.py", line 401, in _apply
    result = super()._apply(fn)
             ^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 900, in _apply
    module._apply(fn)
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 927, in _apply
    param_applied = fn(param)
                    ^^^^^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/nn/modules/module.py", line 1326, in convert
    return t.to(
           ^^^^^
  File "/usr/local/lib/python3.12/dist-packages/torch/cuda/__init__.py", line 319, in _lazy_init
    torch._C._cuda_init()
RuntimeError: No CUDA GPUs are available
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-d11-ar2s18-e30-put-s7.log):
```

[pool] 2026-11-29 00:37:22 exec A40-d11-ar2s18-e30-put-s7 GPU 7 
[pool] 2026-11-29 00:37:28 A40-d11-ar2s18-e30-put-s7: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-d11-ar2s18-e30-put-s7.log
[pool] 2026-11-29 00:38:04 A40-d11-ar2s18-e30-put-s7: attempt 1 failed (rc=1: Python exception); retry after 00:48 on any empty GPU
```

## A40-fetch-ar2_pw-e10 (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-ar2_pw-e10.log):
```
[fetch] 2026-11-28 05:38:51 waiting for exports/ar2_pw_e10 on the relay
[fetch] 2026-11-28 05:43:52 waiting for exports/ar2_pw_e10 on the relay
[fetch] 2026-11-28 05:48:52 waiting for exports/ar2_pw_e10 on the relay
[fetch] 2026-11-28 05:53:53 waiting for exports/ar2_pw_e10 on the relay
[fetch] 2026-11-28 05:58:53 waiting for exports/ar2_pw_e10 on the relay
[fetch] 2026-11-28 06:03:54 waiting for exports/ar2_pw_e10 on the relay
[fetch] 2026-11-28 06:08:54 waiting for exports/ar2_pw_e10 on the relay
[fetch] 2026-11-28 06:13:55 waiting for exports/ar2_pw_e10 on the relay
[fetch] 2026-11-28 06:18:55 waiting for exports/ar2_pw_e10 on the relay
[fetch] 2026-11-28 06:23:56 waiting for exports/ar2_pw_e10 on the relay
[fetch] 2026-11-28 06:28:56 waiting for exports/ar2_pw_e10 on the relay
[fetch] 2026-11-28 06:33:57 waiting for exports/ar2_pw_e10 on the relay
[fetch] 2026-11-28 06:38:57 waiting for exports/ar2_pw_e10 on the relay
[fetch] 2026-11-28 06:43:58 waiting for exports/ar2_pw_e10 on the relay
[fetch] 2026-11-28 06:48:58 waiting for exports/ar2_pw_e10 on the relay
[fetch] disk before: /dev/sdb         19T   11T  6.6T  62% /workspace/FastWAM-memory2
[fetch] 2026-11-28 06:53:59 fetching ar2_pw_e10 (attempt 1)
[relay] get hhyfred/memwam-fullft/exports/ar2_pw_e10/export_e10.pt -> /workspace/FastWAM-memory2/outputs/fullft/exports/ar2_pw_e10/export_e10.pt (12042506565 bytes)
[relay] get hhyfred/memwam-fullft/exports/ar2_pw_e10/export_e10.pt.sha256 -> /workspace/FastWAM-memory2/outputs/fullft/exports/ar2_pw_e10/export_e10.pt.sha256 (80 bytes)
export_e10.pt: OK
total 11760280
drwxr-xr-x   2 root root        4096 Nov 28 07:02 .
drwxr-xr-x 102 root root        4096 Nov 28 06:53 ..
-rw-r--r--   1 root root 12042506565 Nov 28 07:02 export_e10.pt
-rw-r--r--   1 root root          80 Nov 28 07:02 export_e10.pt.sha256
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-ar2_pw-e10.log):
```

[pool] 2026-11-28 03:37:39 exec A40-fetch-ar2_pw-e10 GPU None 
[pool] 2026-11-28 03:37:43 A40-fetch-ar2_pw-e10: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-ar2_pw-e10.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-ar2_pw-e10.md
[queue5] 2026-11-28 15:02:56 A40-fetch-ar2_pw-e10: PASS  rc=0
```

## A40-c18-cover-freeze1-s1 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-cover-freeze1-s1.log):
```
[decide] 2026-11-27 19:31:13 cover_arprop_e30_freeze1/on cover_blocks seed=4300046 frame=1312/1500 hist=3 policy=0.6s elapsed=444s
[decide] 2026-11-27 19:31:23 cover_arprop_e30_freeze1/on cover_blocks seed=4300046 frame=1344/1500 hist=3 policy=0.5s elapsed=454s
[decide] 2026-11-27 19:31:32 cover_arprop_e30_freeze1/on cover_blocks seed=4300046 frame=1376/1500 hist=3 policy=0.6s elapsed=464s
[decide] 2026-11-27 19:31:42 cover_arprop_e30_freeze1/on cover_blocks seed=4300046 frame=1408/1500 hist=3 policy=0.5s elapsed=473s
[decide] 2026-11-27 19:31:52 cover_arprop_e30_freeze1/on cover_blocks seed=4300046 frame=1440/1500 hist=3 policy=0.6s elapsed=483s
[decide] 2026-11-27 19:32:02 cover_arprop_e30_freeze1/on cover_blocks seed=4300046 frame=1472/1500 hist=3 policy=0.5s elapsed=493s
[closed-loop] 2026-11-27 19:32:15 done  cover_arprop_e30_freeze1/on cover_blocks seed=4300046 success=False targets=1500/1500 reward=0.15 lift=None  547s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
cover_arprop_e30_addmove/oncover_blocks      28     0.96  [0.82,0.99]         -    0.97      972        -        -        -    0.6
cover_arprop_e30_freeze1/oncover_blocks      47     0.00  [0.00,0.08]         -    0.16     1500        -        -        -    0.6
cover_arprop_e30_off/on cover_blocks      50     0.00  [0.00,0.07]         -    0.18     1500        -        -        -    0.6
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  28     0      27       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   28     0      27       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   47     0       0       0       47  1.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 275 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-cover-freeze1-s1.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'cover_blocks'
[queue5] 2026-11-28 03:33:26 A40-c18-cover-freeze1-s1: DONE  cover_blocks/on n=47  prog=0.00
```

## A40-c18-cover-freeze1-s2 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-cover-freeze1-s2.log):
```
[decide] 2026-11-27 19:29:05 cover_arprop_e30_freeze1/on cover_blocks seed=4300047 frame=1312/1500 hist=3 policy=0.6s elapsed=456s
[decide] 2026-11-27 19:29:15 cover_arprop_e30_freeze1/on cover_blocks seed=4300047 frame=1344/1500 hist=3 policy=0.6s elapsed=467s
[decide] 2026-11-27 19:29:25 cover_arprop_e30_freeze1/on cover_blocks seed=4300047 frame=1376/1500 hist=3 policy=0.6s elapsed=477s
[decide] 2026-11-27 19:29:35 cover_arprop_e30_freeze1/on cover_blocks seed=4300047 frame=1408/1500 hist=3 policy=0.6s elapsed=487s
[decide] 2026-11-27 19:29:45 cover_arprop_e30_freeze1/on cover_blocks seed=4300047 frame=1440/1500 hist=3 policy=0.6s elapsed=497s
[decide] 2026-11-27 19:29:55 cover_arprop_e30_freeze1/on cover_blocks seed=4300047 frame=1472/1500 hist=3 policy=0.6s elapsed=507s
[closed-loop] 2026-11-27 19:30:09 done  cover_arprop_e30_freeze1/on cover_blocks seed=4300047 success=False targets=1500/1500 reward=0.15 lift=None  565s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
cover_arprop_e30_addmove/oncover_blocks      28     0.96  [0.82,0.99]         -    0.97      972        -        -        -    0.6
cover_arprop_e30_freeze1/oncover_blocks      46     0.00  [0.00,0.08]         -    0.16     1500        -        -        -    0.6
cover_arprop_e30_off/on cover_blocks      50     0.00  [0.00,0.07]         -    0.18     1500        -        -        -    0.6
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  27     0      26       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   28     0      27       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   46     0       0       0       46  1.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 274 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-cover-freeze1-s2.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'cover_blocks'
[queue5] 2026-11-28 03:31:18 A40-c18-cover-freeze1-s2: DONE  cover_blocks/on n=46  prog=0.00
```

## A40-c18-cover-freeze1-s3 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-cover-freeze1-s3.log):
```
[decide] 2026-11-27 19:31:46 cover_arprop_e30_freeze1/on cover_blocks seed=4300048 frame=1312/1500 hist=3 policy=0.5s elapsed=432s
[decide] 2026-11-27 19:31:56 cover_arprop_e30_freeze1/on cover_blocks seed=4300048 frame=1344/1500 hist=3 policy=0.5s elapsed=441s
[decide] 2026-11-27 19:32:05 cover_arprop_e30_freeze1/on cover_blocks seed=4300048 frame=1376/1500 hist=3 policy=0.5s elapsed=451s
[decide] 2026-11-27 19:32:15 cover_arprop_e30_freeze1/on cover_blocks seed=4300048 frame=1408/1500 hist=3 policy=0.5s elapsed=461s
[decide] 2026-11-27 19:32:25 cover_arprop_e30_freeze1/on cover_blocks seed=4300048 frame=1440/1500 hist=3 policy=0.6s elapsed=471s
[decide] 2026-11-27 19:32:35 cover_arprop_e30_freeze1/on cover_blocks seed=4300048 frame=1472/1500 hist=3 policy=0.5s elapsed=480s
[closed-loop] 2026-11-27 19:32:55 done  cover_arprop_e30_freeze1/on cover_blocks seed=4300048 success=False targets=1500/1500 reward=0.15 lift=None  548s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
cover_arprop_e30_addmove/oncover_blocks      29     0.97  [0.83,0.99]         -    0.98      972        -        -        -    0.6
cover_arprop_e30_freeze1/oncover_blocks      49     0.00  [0.00,0.07]         -    0.16     1500        -        -        -    0.6
cover_arprop_e30_off/on cover_blocks      50     0.00  [0.00,0.07]         -    0.18     1500        -        -        -    0.6
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  29     0      28       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   29     0      28       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   49     0       0       0       49  1.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 278 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-cover-freeze1-s3.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'cover_blocks'
[queue5] 2026-11-28 03:34:08 A40-c18-cover-freeze1-s3: DONE  cover_blocks/on n=49  prog=0.00
```

## A40-c18-cover-freeze1-s4 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-cover-freeze1-s4.log):
```
[decide] 2026-11-27 19:42:28 cover_arprop_e30_freeze1/on cover_blocks seed=4300049 frame=1440/1500 hist=3 policy=0.6s elapsed=530s
[decide] 2026-11-27 19:42:38 cover_arprop_e30_freeze1/on cover_blocks seed=4300049 frame=1472/1500 hist=3 policy=0.6s elapsed=540s
[closed-loop] 2026-11-27 19:42:52 done  cover_arprop_e30_freeze1/on cover_blocks seed=4300049 success=False targets=1500/1500 reward=0.15 lift=None  596s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
cover_arprop_e30_addmove/oncover_blocks      34     0.97  [0.85,0.99]         -    0.98      969        -        -        -    0.6
cover_arprop_e30_freeze1/oncover_blocks      50     0.00  [0.00,0.07]         -    0.16     1500        -        -        -    0.6
cover_arprop_e30_off/on cover_blocks      50     0.00  [0.00,0.07]         -    0.18     1500        -        -        -    0.6
rearr_pw_e30_off/on     rearrange_blocks   3     0.00  [0.00,0.56]      1.00    0.00      700        -        -        -    0.6
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  34     0      33       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   34     0      33       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   50     0       0       0       50  1.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_addmove/on   3     0       0       1        2  1.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_freeze1/on   3     0       0       0        3  1.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_off/on   3     0       0       1        2  1.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 287 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-cover-freeze1-s4.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'cover_blocks'
[queue5] 2026-11-28 03:44:07 A40-c18-cover-freeze1-s4: DONE  cover_blocks/on n=50  prog=0.00
```

## A40-c18-cover-addmove-s0 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-cover-addmove-s0.log):
```
[decide] 2026-11-27 19:10:59 cover_arprop_e30_addmove/on cover_blocks seed=4300045 frame=800/1500 hist=3 policy=0.5s elapsed=263s
[decide] 2026-11-27 19:11:09 cover_arprop_e30_addmove/on cover_blocks seed=4300045 frame=832/1500 hist=3 policy=0.5s elapsed=272s
[decide] 2026-11-27 19:11:19 cover_arprop_e30_addmove/on cover_blocks seed=4300045 frame=864/1500 hist=3 policy=0.5s elapsed=282s
[decide] 2026-11-27 19:11:36 cover_arprop_e30_addmove/on cover_blocks seed=4300045 frame=896/1500 hist=3 policy=0.5s elapsed=299s
[decide] 2026-11-27 19:11:45 cover_arprop_e30_addmove/on cover_blocks seed=4300045 frame=928/1500 hist=3 policy=0.5s elapsed=309s
[decide] 2026-11-27 19:11:55 cover_arprop_e30_addmove/on cover_blocks seed=4300045 frame=960/1500 hist=3 policy=0.5s elapsed=319s
[closed-loop] 2026-11-27 19:12:05 done  cover_arprop_e30_addmove/on cover_blocks seed=4300045 success=True targets=979/1500 reward=1.0 lift=None  372s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
cover_arprop_e30_addmove/oncover_blocks      20     0.95  [0.76,0.99]         -    0.97      977        -        -        -    0.6
cover_arprop_e30_freeze1/oncover_blocks      38     0.00  [0.00,0.09]         -    0.17     1500        -        -        -    0.6
cover_arprop_e30_off/on cover_blocks      50     0.00  [0.00,0.07]         -    0.18     1500        -        -        -    0.6
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  20     0      19       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   20     0      19       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   38     0       0       0       38  1.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 258 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-cover-addmove-s0.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'cover_blocks'
[queue5] 2026-11-28 03:12:29 A40-c18-cover-addmove-s0: DONE  cover_blocks/on n=20  prog=0.00
```

## A40-c18-cover-addmove-s1 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-cover-addmove-s1.log):
```
[decide] 2026-11-27 19:23:44 cover_arprop_e30_addmove/on cover_blocks seed=4300046 frame=800/1500 hist=3 policy=0.5s elapsed=282s
[decide] 2026-11-27 19:23:57 cover_arprop_e30_addmove/on cover_blocks seed=4300046 frame=832/1500 hist=3 policy=0.6s elapsed=296s
[decide] 2026-11-27 19:24:16 cover_arprop_e30_addmove/on cover_blocks seed=4300046 frame=864/1500 hist=3 policy=0.6s elapsed=314s
[decide] 2026-11-27 19:24:26 cover_arprop_e30_addmove/on cover_blocks seed=4300046 frame=896/1500 hist=3 policy=0.5s elapsed=324s
[decide] 2026-11-27 19:24:36 cover_arprop_e30_addmove/on cover_blocks seed=4300046 frame=928/1500 hist=3 policy=0.6s elapsed=334s
[decide] 2026-11-27 19:24:47 cover_arprop_e30_addmove/on cover_blocks seed=4300046 frame=960/1500 hist=3 policy=0.6s elapsed=345s
[closed-loop] 2026-11-27 19:24:54 done  cover_arprop_e30_addmove/on cover_blocks seed=4300046 success=True targets=974/1500 reward=1.0 lift=None  390s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
cover_arprop_e30_addmove/oncover_blocks      26     0.96  [0.81,0.99]         -    0.97      972        -        -        -    0.6
cover_arprop_e30_freeze1/oncover_blocks      45     0.00  [0.00,0.08]         -    0.16     1500        -        -        -    0.6
cover_arprop_e30_off/on cover_blocks      50     0.00  [0.00,0.07]         -    0.18     1500        -        -        -    0.6
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  25     0      24       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   26     0      25       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   45     0       0       0       45  1.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 271 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-cover-addmove-s1.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'cover_blocks'
[queue5] 2026-11-28 03:25:22 A40-c18-cover-addmove-s1: DONE  cover_blocks/on n=26  prog=0.00
```

## A40-c18-cover-addmove-s2 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-cover-addmove-s2.log):
```
[decide] 2026-11-27 19:52:10 cover_arprop_e30_addmove/on cover_blocks seed=4300047 frame=928/1500 hist=3 policy=0.6s elapsed=348s
[decide] 2026-11-27 19:52:21 cover_arprop_e30_addmove/on cover_blocks seed=4300047 frame=960/1500 hist=3 policy=0.6s elapsed=359s
[closed-loop] 2026-11-27 19:52:30 done  cover_arprop_e30_addmove/on cover_blocks seed=4300047 success=True targets=975/1500 reward=1.0 lift=None  415s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
cover_arprop_e30_addmove/oncover_blocks      38     0.97  [0.87,1.00]         -    0.98      967        -        -        -    0.6
cover_arprop_e30_freeze1/oncover_blocks      50     0.00  [0.00,0.07]         -    0.16     1500        -        -        -    0.6
cover_arprop_e30_off/on cover_blocks      50     0.00  [0.00,0.07]         -    0.18     1500        -        -        -    0.6
rearr_pw_e30_off/on     rearrange_blocks  10     0.00  [0.00,0.28]      1.00    0.00      700        -        -        -    0.6
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  38     0      37       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   38     0      37       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   50     0       0       0       50  1.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_addmove/on  10     0       0       6        4  0.031
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_freeze1/on  10     0       0       1        9  1.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_off/on  10     0       0       2        8  0.500
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 298 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-cover-addmove-s2.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'cover_blocks'
[queue5] 2026-11-28 03:53:09 A40-c18-cover-addmove-s2: DONE  cover_blocks/on n=38  prog=0.00
```

## A40-c18-cover-addmove-s3 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-cover-addmove-s3.log):
```
[decide] 2026-11-27 20:19:12 cover_arprop_e30_addmove/on cover_blocks seed=4300048 frame=928/1500 hist=3 policy=0.5s elapsed=328s
[decide] 2026-11-27 20:19:23 cover_arprop_e30_addmove/on cover_blocks seed=4300048 frame=960/1500 hist=3 policy=0.6s elapsed=339s
[closed-loop] 2026-11-27 20:19:30 done  cover_arprop_e30_addmove/on cover_blocks seed=4300048 success=True targets=972/1500 reward=1.0 lift=None  395s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
cover_arprop_e30_addmove/oncover_blocks      47     0.98  [0.89,1.00]         -    0.99      966        -        -        -    0.6
cover_arprop_e30_freeze1/oncover_blocks      50     0.00  [0.00,0.07]         -    0.16     1500        -        -        -    0.6
cover_arprop_e30_off/on cover_blocks      50     0.00  [0.00,0.07]         -    0.18     1500        -        -        -    0.6
rearr_pw_e30_off/on     rearrange_blocks  35     0.00  [0.00,0.10]      1.00    0.00      700        -        -        -    0.6
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  47     0      46       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   47     0      46       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   50     0       0       0       50  1.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_addmove/on  35     0       0      22       13  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_freeze1/on  35     0       0      10       25  0.002
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_off/on  35     0       0       5       30  0.062
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 332 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-cover-addmove-s3.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'cover_blocks'
[queue5] 2026-11-28 04:20:17 A40-c18-cover-addmove-s3: DONE  cover_blocks/on n=47  prog=0.00
```

## A40-c18-cover-addmove-s4 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-cover-addmove-s4.log):
```
cover_arprop_e30_addmove/oncover_blocks      50     0.98  [0.90,1.00]         -    0.99      966        -        -        -    0.6
cover_arprop_e30_freeze1/oncover_blocks      50     0.00  [0.00,0.07]         -    0.16     1500        -        -        -    0.6
cover_arprop_e30_off/on cover_blocks      50     0.00  [0.00,0.07]         -    0.18     1500        -        -        -    0.6
rearr_pw_e30_freeze1/on rearrange_blocks   3     0.00  [0.00,0.56]      1.00    0.00      700        -        -        -    0.6
rearr_pw_e30_off/on     rearrange_blocks  46     0.00  [0.00,0.08]      1.00    0.00      700        -        -        -    0.6
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  50     0      49       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   50     0      49       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   50     0       0       0       50  1.000
  rearr_pw_e30_freeze1/on  vs rearr_pw_e30_off/on        3     0       0       0        3  1.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_addmove/on   3     0       0       1        2  1.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_freeze1/on   3     0       0       0        3  1.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_off/on   3     0       0       1        2  1.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_addmove/on  46     0       0      30       16  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_freeze1/on  46     0       0      15       31  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_off/on  46     0       0       8       38  0.008
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 349 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-cover-addmove-s4.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'cover_blocks'
[queue5] 2026-11-28 04:33:45 A40-c18-cover-addmove-s4: DONE  cover_blocks/on n=50  prog=0.00
```

## A40-c18-rearrpw-off-s0 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-rearrpw-off-s0.log):
```
[decide] 2026-11-27 20:22:03 rearr_pw_e30_off/on rearrange_blocks seed=4300045 frame=640/700 hist=3 policy=0.6s elapsed=227s
[decide] 2026-11-27 20:22:13 rearr_pw_e30_off/on rearrange_blocks seed=4300045 frame=672/700 hist=3 policy=0.5s elapsed=236s
[closed-loop] 2026-11-27 20:22:24 done  rearr_pw_e30_off/on rearrange_blocks seed=4300045 success=False targets=700/700 reward=0.0 lift=0.12509852647781372  286s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
cover_arprop_e30_addmove/oncover_blocks      48     0.98  [0.89,1.00]         -    0.99      966        -        -        -    0.6
cover_arprop_e30_freeze1/oncover_blocks      50     0.00  [0.00,0.07]         -    0.16     1500        -        -        -    0.6
cover_arprop_e30_off/on cover_blocks      50     0.00  [0.00,0.07]         -    0.18     1500        -        -        -    0.6
rearr_pw_e30_off/on     rearrange_blocks  40     0.00  [0.00,0.09]      1.00    0.00      700        -        -        -    0.6
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  48     0      47       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   48     0      47       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   50     0       0       0       50  1.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_addmove/on  40     0       0      24       16  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_freeze1/on  40     0       0      11       29  0.001
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_off/on  40     0       0       6       34  0.031
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 338 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-rearrpw-off-s0.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 04:22:44 A40-c18-rearrpw-off-s0: DONE  rearrange_blocks/on n=40  prog=0.00
```

## A40-c18-rearrpw-off-s1 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-rearrpw-off-s1.log):
```
[decide] 2026-11-27 20:24:03 rearr_pw_e30_off/on rearrange_blocks seed=4300046 frame=640/700 hist=3 policy=0.6s elapsed=216s
[decide] 2026-11-27 20:24:13 rearr_pw_e30_off/on rearrange_blocks seed=4300046 frame=672/700 hist=3 policy=0.6s elapsed=226s
[closed-loop] 2026-11-27 20:24:24 done  rearr_pw_e30_off/on rearrange_blocks seed=4300046 success=False targets=700/700 reward=0.0 lift=0.12101197242736816  289s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
cover_arprop_e30_addmove/oncover_blocks      48     0.98  [0.89,1.00]         -    0.99      966        -        -        -    0.6
cover_arprop_e30_freeze1/oncover_blocks      50     0.00  [0.00,0.07]         -    0.16     1500        -        -        -    0.6
cover_arprop_e30_off/on cover_blocks      50     0.00  [0.00,0.07]         -    0.18     1500        -        -        -    0.6
rearr_pw_e30_off/on     rearrange_blocks  41     0.00  [0.00,0.09]      1.00    0.00      700        -        -        -    0.6
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  48     0      47       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   48     0      47       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   50     0       0       0       50  1.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_addmove/on  41     0       0      25       16  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_freeze1/on  41     0       0      12       29  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_off/on  41     0       0       6       35  0.031
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 339 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-rearrpw-off-s1.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 04:24:44 A40-c18-rearrpw-off-s1: DONE  rearrange_blocks/on n=41  prog=0.00
```

## A40-c18-rearrpw-off-s2 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-rearrpw-off-s2.log):
```
[decide] 2026-11-27 20:24:55 rearr_pw_e30_off/on rearrange_blocks seed=4300047 frame=640/700 hist=3 policy=0.6s elapsed=220s
[decide] 2026-11-27 20:25:05 rearr_pw_e30_off/on rearrange_blocks seed=4300047 frame=672/700 hist=3 policy=0.5s elapsed=230s
[closed-loop] 2026-11-27 20:25:17 done  rearr_pw_e30_off/on rearrange_blocks seed=4300047 success=False targets=700/700 reward=0.0 lift=0.11974769830703735  281s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
cover_arprop_e30_addmove/oncover_blocks      48     0.98  [0.89,1.00]         -    0.99      966        -        -        -    0.6
cover_arprop_e30_freeze1/oncover_blocks      50     0.00  [0.00,0.07]         -    0.16     1500        -        -        -    0.6
cover_arprop_e30_off/on cover_blocks      50     0.00  [0.00,0.07]         -    0.18     1500        -        -        -    0.6
rearr_pw_e30_off/on     rearrange_blocks  43     0.00  [0.00,0.08]      1.00    0.00      700        -        -        -    0.6
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  48     0      47       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   48     0      47       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   50     0       0       0       50  1.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_addmove/on  43     0       0      27       16  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_freeze1/on  43     0       0      13       30  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_off/on  43     0       0       7       36  0.016
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 341 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-rearrpw-off-s2.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 04:25:38 A40-c18-rearrpw-off-s2: DONE  rearrange_blocks/on n=43  prog=0.00
```

## A40-c18-rearrpw-off-s3 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-rearrpw-off-s3.log):
```
cover_arprop_e30_addmove/oncover_blocks      50     0.98  [0.90,1.00]         -    0.99      966        -        -        -    0.6
cover_arprop_e30_freeze1/oncover_blocks      50     0.00  [0.00,0.07]         -    0.16     1500        -        -        -    0.6
cover_arprop_e30_off/on cover_blocks      50     0.00  [0.00,0.07]         -    0.18     1500        -        -        -    0.6
rearr_pw_e30_freeze1/on rearrange_blocks   4     0.00  [0.00,0.49]      1.00    0.00      700        -        -        -    0.6
rearr_pw_e30_off/on     rearrange_blocks  48     0.00  [0.00,0.07]      1.00    0.00      700        -        -        -    0.6
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  50     0      49       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   50     0      49       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   50     0       0       0       50  1.000
  rearr_pw_e30_freeze1/on  vs rearr_pw_e30_off/on        4     0       0       0        4  1.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_addmove/on   4     0       0       1        3  1.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_freeze1/on   4     0       0       0        4  1.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_off/on   4     0       0       1        3  1.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_addmove/on  48     0       0      31       17  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_freeze1/on  48     0       0      15       33  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_off/on  48     0       0       8       40  0.008
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 352 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-rearrpw-off-s3.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 04:36:28 A40-c18-rearrpw-off-s3: DONE  rearrange_blocks/on n=48  prog=0.00
```

## A40-c18-rearrpw-off-s4 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-rearrpw-off-s4.log):
```
cover_arprop_e30_addmove/oncover_blocks      50     0.98  [0.90,1.00]         -    0.99      966        -        -        -    0.6
cover_arprop_e30_freeze1/oncover_blocks      50     0.00  [0.00,0.07]         -    0.16     1500        -        -        -    0.6
cover_arprop_e30_off/on cover_blocks      50     0.00  [0.00,0.07]         -    0.18     1500        -        -        -    0.6
rearr_pw_e30_freeze1/on rearrange_blocks   9     0.00  [0.00,0.30]      1.00    0.00      700        -        -        -    0.6
rearr_pw_e30_off/on     rearrange_blocks  50     0.00  [0.00,0.07]      1.00    0.00      700        -        -        -    0.6
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  50     0      49       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   50     0      49       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   50     0       0       0       50  1.000
  rearr_pw_e30_freeze1/on  vs rearr_pw_e30_off/on        9     0       0       0        9  1.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_addmove/on   9     0       0       5        4  0.062
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_freeze1/on   9     0       0       1        8  1.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_off/on   9     0       0       2        7  0.500
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_addmove/on  50     0       0      33       17  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_freeze1/on  50     0       0      16       34  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_off/on  50     0       0      10       40  0.002
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 359 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-rearrpw-off-s4.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 04:44:33 A40-c18-rearrpw-off-s4: DONE  rearrange_blocks/on n=50  prog=0.00
```

## A40-c18-rearrpw-freeze1-s0 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-rearrpw-freeze1-s0.log):
```
cover_arprop_e30_addmove/oncover_blocks      50     0.98  [0.90,1.00]         -    0.99      966        -        -        -    0.6
cover_arprop_e30_freeze1/oncover_blocks      50     0.00  [0.00,0.07]         -    0.16     1500        -        -        -    0.6
cover_arprop_e30_off/on cover_blocks      50     0.00  [0.00,0.07]         -    0.18     1500        -        -        -    0.6
rearr_pw_e30_freeze1/on rearrange_blocks  28     0.00  [0.00,0.12]      1.00    0.00      700        -        -        -    0.6
rearr_pw_e30_off/on     rearrange_blocks  50     0.00  [0.00,0.07]      1.00    0.00      700        -        -        -    0.6
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  50     0      49       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   50     0      49       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   50     0       0       0       50  1.000
  rearr_pw_e30_freeze1/on  vs rearr_pw_e30_off/on       28     0       0       0       28  1.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_addmove/on  28     0       0      16       12  0.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_freeze1/on  28     0       0       8       20  0.008
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_off/on  28     0       0       4       24  0.125
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_addmove/on  50     0       0      33       17  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_freeze1/on  50     0       0      16       34  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_off/on  50     0       0      10       40  0.002
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 378 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-rearrpw-freeze1-s0.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 05:16:00 A40-c18-rearrpw-freeze1-s0: DONE  rearrange_blocks/on n=28  prog=0.00
```

## A40-c18-rearrpw-freeze1-s1 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-rearrpw-freeze1-s1.log):
```
cover_arprop_e30_addmove/oncover_blocks      50     0.98  [0.90,1.00]         -    0.99      966        -        -        -    0.6
cover_arprop_e30_freeze1/oncover_blocks      50     0.00  [0.00,0.07]         -    0.16     1500        -        -        -    0.6
cover_arprop_e30_off/on cover_blocks      50     0.00  [0.00,0.07]         -    0.18     1500        -        -        -    0.6
rearr_pw_e30_freeze1/on rearrange_blocks  29     0.00  [0.00,0.12]      1.00    0.00      700        -        -        -    0.6
rearr_pw_e30_off/on     rearrange_blocks  50     0.00  [0.00,0.07]      1.00    0.00      700        -        -        -    0.6
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  50     0      49       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   50     0      49       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   50     0       0       0       50  1.000
  rearr_pw_e30_freeze1/on  vs rearr_pw_e30_off/on       29     0       0       0       29  1.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_addmove/on  29     0       0      17       12  0.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_freeze1/on  29     0       0       9       20  0.004
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_off/on  29     0       0       4       25  0.125
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_addmove/on  50     0       0      33       17  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_freeze1/on  50     0       0      16       34  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_off/on  50     0       0      10       40  0.002
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 379 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-rearrpw-freeze1-s1.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 05:17:32 A40-c18-rearrpw-freeze1-s1: DONE  rearrange_blocks/on n=29  prog=0.00
```

## A40-c18-rearrpw-freeze1-s2 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-rearrpw-freeze1-s2.log):
```
cover_arprop_e30_addmove/oncover_blocks      50     0.98  [0.90,1.00]         -    0.99      966        -        -        -    0.6
cover_arprop_e30_freeze1/oncover_blocks      50     0.00  [0.00,0.07]         -    0.16     1500        -        -        -    0.6
cover_arprop_e30_off/on cover_blocks      50     0.00  [0.00,0.07]         -    0.18     1500        -        -        -    0.6
rearr_pw_e30_freeze1/on rearrange_blocks  30     0.00  [0.00,0.11]      1.00    0.00      700        -        -        -    0.6
rearr_pw_e30_off/on     rearrange_blocks  50     0.00  [0.00,0.07]      1.00    0.00      700        -        -        -    0.6
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  50     0      49       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   50     0      49       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   50     0       0       0       50  1.000
  rearr_pw_e30_freeze1/on  vs rearr_pw_e30_off/on       30     0       0       0       30  1.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_addmove/on  30     0       0      18       12  0.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_freeze1/on  30     0       0       9       21  0.004
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_off/on  30     0       0       4       26  0.125
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_addmove/on  50     0       0      33       17  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_freeze1/on  50     0       0      16       34  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_off/on  50     0       0      10       40  0.002
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 380 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-rearrpw-freeze1-s2.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 05:18:45 A40-c18-rearrpw-freeze1-s2: DONE  rearrange_blocks/on n=30  prog=0.00
```

## A40-c18-rearrpw-freeze1-s3 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-rearrpw-freeze1-s3.log):
```
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  50     0      49       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   50     0      49       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   50     0       0       0       50  1.000
  rearr_pw_e30_addmove/on  vs rearr_pw_e30_freeze1/on   46     0      45       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearr_pw_e30_off/on       46     0      45       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearrange_arprop_e30_addmove/on  46    29      16       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearrange_arprop_e30_freeze1/on  46    14      31       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearrange_arprop_e30_off/on  46     7      38       0        1  0.000
  rearr_pw_e30_freeze1/on  vs rearr_pw_e30_off/on       48     0       0       0       48  1.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_addmove/on  48     0       0      31       17  0.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_freeze1/on  48     0       0      15       33  0.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_off/on  48     0       0       8       40  0.008
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_addmove/on  50     0       0      33       17  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_freeze1/on  50     0       0      16       34  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_off/on  50     0       0      10       40  0.002
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 444 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-rearrpw-freeze1-s3.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 07:15:24 A40-c18-rearrpw-freeze1-s3: DONE  rearrange_blocks/on n=48  prog=0.00
```

## A40-c18-rearrpw-freeze1-s4 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-rearrpw-freeze1-s4.log):
```
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  50     0      49       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   50     0      49       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   50     0       0       0       50  1.000
  rearr_pw_e30_addmove/on  vs rearr_pw_e30_freeze1/on   50     0      49       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearr_pw_e30_off/on       50     0      49       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearrange_arprop_e30_addmove/on  50    33      16       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearrange_arprop_e30_freeze1/on  50    16      33       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearrange_arprop_e30_off/on  50    10      39       0        1  0.000
  rearr_pw_e30_freeze1/on  vs rearr_pw_e30_off/on       50     0       0       0       50  1.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_addmove/on  50     0       0      33       17  0.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_freeze1/on  50     0       0      16       34  0.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_off/on  50     0       0      10       40  0.002
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_addmove/on  50     0       0      33       17  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_freeze1/on  50     0       0      16       34  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_off/on  50     0       0      10       40  0.002
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 450 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-rearrpw-freeze1-s4.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 07:21:06 A40-c18-rearrpw-freeze1-s4: DONE  rearrange_blocks/on n=50  prog=0.00
```

## A40-c18-rearrpw-addmove-s0 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-rearrpw-addmove-s0.log):
```
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  50     0      49       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   50     0      49       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   50     0       0       0       50  1.000
  rearr_pw_e30_addmove/on  vs rearr_pw_e30_freeze1/on   37     0      36       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearr_pw_e30_off/on       37     0      36       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearrange_arprop_e30_addmove/on  37    23      13       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearrange_arprop_e30_freeze1/on  37    10      26       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearrange_arprop_e30_off/on  37     5      31       0        1  0.000
  rearr_pw_e30_freeze1/on  vs rearr_pw_e30_off/on       45     0       0       0       45  1.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_addmove/on  45     0       0      29       16  0.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_freeze1/on  45     0       0      14       31  0.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_off/on  45     0       0       7       38  0.016
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_addmove/on  50     0       0      33       17  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_freeze1/on  50     0       0      16       34  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_off/on  50     0       0      10       40  0.002
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 432 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-rearrpw-addmove-s0.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 07:06:59 A40-c18-rearrpw-addmove-s0: DONE  rearrange_blocks/on n=37  prog=0.00
```

## A40-c18-rearrpw-addmove-s1 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-rearrpw-addmove-s1.log):
```
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  50     0      49       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   50     0      49       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   50     0       0       0       50  1.000
  rearr_pw_e30_addmove/on  vs rearr_pw_e30_freeze1/on   44     0      43       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearr_pw_e30_off/on       44     0      43       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearrange_arprop_e30_addmove/on  44    28      15       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearrange_arprop_e30_freeze1/on  44    13      30       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearrange_arprop_e30_off/on  44     7      36       0        1  0.000
  rearr_pw_e30_freeze1/on  vs rearr_pw_e30_off/on       47     0       0       0       47  1.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_addmove/on  47     0       0      30       17  0.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_freeze1/on  47     0       0      15       32  0.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_off/on  47     0       0       8       39  0.008
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_addmove/on  50     0       0      33       17  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_freeze1/on  50     0       0      16       34  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_off/on  50     0       0      10       40  0.002
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 441 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-rearrpw-addmove-s1.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 07:12:16 A40-c18-rearrpw-addmove-s1: DONE  rearrange_blocks/on n=44  prog=0.00
```

## A40-c18-rearrpw-addmove-s2 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-rearrpw-addmove-s2.log):
```
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  50     0      49       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   50     0      49       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   50     0       0       0       50  1.000
  rearr_pw_e30_addmove/on  vs rearr_pw_e30_freeze1/on   43     0      42       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearr_pw_e30_off/on       43     0      42       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearrange_arprop_e30_addmove/on  43    27      15       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearrange_arprop_e30_freeze1/on  43    12      30       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearrange_arprop_e30_off/on  43     7      35       0        1  0.000
  rearr_pw_e30_freeze1/on  vs rearr_pw_e30_off/on       47     0       0       0       47  1.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_addmove/on  47     0       0      30       17  0.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_freeze1/on  47     0       0      15       32  0.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_off/on  47     0       0       8       39  0.008
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_addmove/on  50     0       0      33       17  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_freeze1/on  50     0       0      16       34  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_off/on  50     0       0      10       40  0.002
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 440 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-rearrpw-addmove-s2.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 07:12:01 A40-c18-rearrpw-addmove-s2: DONE  rearrange_blocks/on n=43  prog=0.00
```

## A40-c18-rearrpw-addmove-s3 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-rearrpw-addmove-s3.log):
```
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  50     0      49       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   50     0      49       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   50     0       0       0       50  1.000
  rearr_pw_e30_addmove/on  vs rearr_pw_e30_freeze1/on   49     0      48       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearr_pw_e30_off/on       49     0      48       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearrange_arprop_e30_addmove/on  49    32      16       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearrange_arprop_e30_freeze1/on  49    16      32       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearrange_arprop_e30_off/on  49     9      39       0        1  0.000
  rearr_pw_e30_freeze1/on  vs rearr_pw_e30_off/on       49     0       0       0       49  1.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_addmove/on  49     0       0      32       17  0.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_freeze1/on  49     0       0      16       33  0.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_off/on  49     0       0       9       40  0.004
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_addmove/on  50     0       0      33       17  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_freeze1/on  50     0       0      16       34  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_off/on  50     0       0      10       40  0.002
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 448 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-rearrpw-addmove-s3.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 07:19:15 A40-c18-rearrpw-addmove-s3: DONE  rearrange_blocks/on n=49  prog=0.00
```

## A40-c18-rearrpw-addmove-s4 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-c18-rearrpw-addmove-s4.log):
```
rearrange_arprop_e30_addmove/onrearrange_blocks  50     0.66  [0.52,0.78]      1.00    0.66      497        -        -        -    0.6
rearrange_arprop_e30_freeze1/onrearrange_blocks  50     0.32  [0.21,0.46]      1.00    0.32      605        -        -        -    0.6
rearrange_arprop_e30_off/onrearrange_blocks  50     0.20  [0.11,0.33]      1.00    0.20      641        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  cover_arprop_e30_addmove/on vs cover_arprop_e30_freeze1/on  50     0      49       0        1  0.000
  cover_arprop_e30_addmove/on vs cover_arprop_e30_off/on   50     0      49       0        1  0.000
  cover_arprop_e30_freeze1/on vs cover_arprop_e30_off/on   50     0       0       0       50  1.000
  rearr_pw_e30_addmove/on  vs rearr_pw_e30_freeze1/on   49     0      48       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearr_pw_e30_off/on       50     0      49       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearrange_arprop_e30_addmove/on  50    33      16       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearrange_arprop_e30_freeze1/on  50    16      33       0        1  0.000
  rearr_pw_e30_addmove/on  vs rearrange_arprop_e30_off/on  50    10      39       0        1  0.000
  rearr_pw_e30_freeze1/on  vs rearr_pw_e30_off/on       49     0       0       0       49  1.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_addmove/on  49     0       0      32       17  0.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_freeze1/on  49     0       0      16       33  0.000
  rearr_pw_e30_freeze1/on  vs rearrange_arprop_e30_off/on  49     0       0       9       40  0.004
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_addmove/on  50     0       0      33       17  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_freeze1/on  50     0       0      16       34  0.000
  rearr_pw_e30_off/on      vs rearrange_arprop_e30_off/on  50     0       0      10       40  0.002
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_freeze1/on  50    16      17       0       17  0.000
  rearrange_arprop_e30_addmove/on vs rearrange_arprop_e30_off/on  50     8      25       2       15  0.000
  rearrange_arprop_e30_freeze1/on vs rearrange_arprop_e30_off/on  50     7       9       3       31  0.146

[summary] 449 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/c18/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-c18-rearrpw-addmove-s4.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-28 07:20:13 A40-c18-rearrpw-addmove-s4: DONE  rearrange_blocks/on n=50  prog=0.00
```

## A40-C18-report (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-C18-report.log):
```
    8  pressed twice or more (after step 1 was complete)   e.g. seeds [4300000, 4300005, 4300019, 4300021]

c18:rearr_pw_e30_off: 50 episodes
   50  pressed twice or more (after step 1 was complete)   e.g. seeds [4300000, 4300001, 4300002, 4300003]

c18:rearr_pw_e30_freeze1: 50 episodes
   50  pressed twice or more (after step 1 was complete)   e.g. seeds [4300000, 4300001, 4300002, 4300003]

c18:rearr_pw_e30_addmove: 50 episodes
   49  success   e.g. seeds [4300000, 4300001, 4300002, 4300003]
    1  never pressed: block1 placed on the empty mat   e.g. seeds [4300016]

e6:rearrange_arprop_e30: 100 episodes
   62  success   e.g. seeds [4300000, 4300001, 4300002, 4300003]
   18  pressed twice or more (after step 1 was complete)   e.g. seeds [4300006, 4300008, 4300018, 4300024]
   17  never pressed: block1 placed on the empty mat   e.g. seeds [4300007, 4300014, 4300016, 4300017]
    3  stage 1, then moved block1 again (which-block error)   e.g. seeds [4300021, 4300040, 4300098]

v20:rearr_pw_e30: 100 episodes
   93  success   e.g. seeds [4300000, 4300001, 4300002, 4300003]
    4  never pressed: block1 placed on the empty mat   e.g. seeds [4300029, 4300054, 4300087, 4300091]
    2  stage 1, then moved block1 again (which-block error)   e.g. seeds [4300059, 4300093]
    1  pressed too early (block1 not on the empty mat at the press)   e.g. seeds [4300097]

REARR SPLIT REPORT: written outputs/fullft/REARR_SPLIT.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-C18-report.log):
```

[pool] 2026-11-28 07:21:15 exec A40-C18-report GPU None 
[pool] 2026-11-28 07:21:19 A40-C18-report: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-C18-report.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-C18-report.md
[queue5] 2026-11-28 07:26:17 A40-C18-report: PASS  rc=0
```

## A40-stepa-ar_2task_e10-s0 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e10-s0.log):
```
[decide] 2026-11-28 00:14:10 ar_2task_e10/on swap_blocks seed=4300202 frame=416/1000 hist=3 policy=0.5s elapsed=147s
[decide] 2026-11-28 00:14:20 ar_2task_e10/on swap_blocks seed=4300202 frame=448/1000 hist=3 policy=0.5s elapsed=157s
[decide] 2026-11-28 00:14:30 ar_2task_e10/on swap_blocks seed=4300202 frame=480/1000 hist=3 policy=0.5s elapsed=167s
[decide] 2026-11-28 00:14:40 ar_2task_e10/on swap_blocks seed=4300202 frame=512/1000 hist=3 policy=0.6s elapsed=177s
[decide] 2026-11-28 00:14:50 ar_2task_e10/on swap_blocks seed=4300202 frame=544/1000 hist=3 policy=0.5s elapsed=187s
[decide] 2026-11-28 00:15:00 ar_2task_e10/on swap_blocks seed=4300202 frame=576/1000 hist=3 policy=0.5s elapsed=197s
[decide] 2026-11-28 00:15:10 ar_2task_e10/on swap_blocks seed=4300202 frame=608/1000 hist=3 policy=0.6s elapsed=207s
[decide] 2026-11-28 00:15:20 ar_2task_e10/on swap_blocks seed=4300202 frame=640/1000 hist=3 policy=0.5s elapsed=217s
[decide] 2026-11-28 00:15:30 ar_2task_e10/on swap_blocks seed=4300202 frame=672/1000 hist=3 policy=0.5s elapsed=227s
[decide] 2026-11-28 00:15:40 ar_2task_e10/on swap_blocks seed=4300202 frame=704/1000 hist=3 policy=0.6s elapsed=237s
[decide] 2026-11-28 00:15:52 ar_2task_e10/on swap_blocks seed=4300202 frame=736/1000 hist=3 policy=0.6s elapsed=250s
[decide] 2026-11-28 00:16:07 ar_2task_e10/on swap_blocks seed=4300202 frame=768/1000 hist=3 policy=0.5s elapsed=264s
[decide] 2026-11-28 00:16:21 ar_2task_e10/on swap_blocks seed=4300202 frame=800/1000 hist=3 policy=0.6s elapsed=279s
[decide] 2026-11-28 00:16:40 ar_2task_e10/on swap_blocks seed=4300202 frame=832/1000 hist=3 policy=0.6s elapsed=297s
[decide] 2026-11-28 00:16:50 ar_2task_e10/on swap_blocks seed=4300202 frame=864/1000 hist=3 policy=0.6s elapsed=307s
[decide] 2026-11-28 00:17:03 ar_2task_e10/on swap_blocks seed=4300202 frame=896/1000 hist=3 policy=0.6s elapsed=321s
[decide] 2026-11-28 00:17:16 ar_2task_e10/on swap_blocks seed=4300202 frame=928/1000 hist=3 policy=0.5s elapsed=333s
[decide] 2026-11-28 00:17:26 ar_2task_e10/on swap_blocks seed=4300202 frame=960/1000 hist=3 policy=0.6s elapsed=344s
[decide] 2026-11-28 00:17:36 ar_2task_e10/on swap_blocks seed=4300202 frame=992/1000 hist=3 policy=0.5s elapsed=354s
[closed-loop] 2026-11-28 00:17:42 done  ar_2task_e10/on swap_blocks seed=4300202 success=False targets=1000/1000 reward=0.0 lift=0.0  400s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar_2task_e10/on         swap_blocks       60     0.07  [0.03,0.16]      0.83    0.07      984        -        -        -    0.6

[summary] 60 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/stepa/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-stepa-ar_2task_e10-s0.log):
```

[pool] 2026-11-28 07:08:07 exec A40-stepa-ar_2task_e10-s0 GPU 3 
[pool] 2026-11-28 07:08:11 A40-stepa-ar_2task_e10-s0: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e10-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e10-s0.md
[queue5] 2026-11-28 08:20:16 A40-stepa-ar_2task_e10-s0: DONE  swap_blocks/on n=60 lifted=50 s1=50 s2=39 s3=34 pressed=11 success=4 prog=0.51
```

## A40-stepa-ar_2task_e10-s1 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e10-s1.log):
```
[decide] 2026-11-28 00:19:30 ar_2task_e10/on swap_blocks seed=4300204 frame=416/1000 hist=3 policy=0.6s elapsed=152s
[decide] 2026-11-28 00:19:41 ar_2task_e10/on swap_blocks seed=4300204 frame=448/1000 hist=3 policy=0.6s elapsed=163s
[decide] 2026-11-28 00:19:51 ar_2task_e10/on swap_blocks seed=4300204 frame=480/1000 hist=3 policy=0.6s elapsed=173s
[decide] 2026-11-28 00:20:02 ar_2task_e10/on swap_blocks seed=4300204 frame=512/1000 hist=3 policy=0.6s elapsed=184s
[decide] 2026-11-28 00:20:12 ar_2task_e10/on swap_blocks seed=4300204 frame=544/1000 hist=3 policy=0.6s elapsed=194s
[decide] 2026-11-28 00:20:22 ar_2task_e10/on swap_blocks seed=4300204 frame=576/1000 hist=3 policy=0.6s elapsed=204s
[decide] 2026-11-28 00:20:33 ar_2task_e10/on swap_blocks seed=4300204 frame=608/1000 hist=3 policy=0.6s elapsed=215s
[decide] 2026-11-28 00:20:43 ar_2task_e10/on swap_blocks seed=4300204 frame=640/1000 hist=3 policy=0.6s elapsed=225s
[decide] 2026-11-28 00:20:53 ar_2task_e10/on swap_blocks seed=4300204 frame=672/1000 hist=3 policy=0.6s elapsed=235s
[decide] 2026-11-28 00:21:03 ar_2task_e10/on swap_blocks seed=4300204 frame=704/1000 hist=3 policy=0.6s elapsed=245s
[decide] 2026-11-28 00:21:14 ar_2task_e10/on swap_blocks seed=4300204 frame=736/1000 hist=3 policy=0.6s elapsed=255s
[decide] 2026-11-28 00:21:26 ar_2task_e10/on swap_blocks seed=4300204 frame=768/1000 hist=3 policy=0.6s elapsed=268s
[decide] 2026-11-28 00:21:42 ar_2task_e10/on swap_blocks seed=4300204 frame=800/1000 hist=3 policy=0.6s elapsed=283s
[decide] 2026-11-28 00:21:52 ar_2task_e10/on swap_blocks seed=4300204 frame=832/1000 hist=3 policy=0.6s elapsed=294s
[decide] 2026-11-28 00:22:02 ar_2task_e10/on swap_blocks seed=4300204 frame=864/1000 hist=3 policy=0.6s elapsed=304s
[decide] 2026-11-28 00:22:13 ar_2task_e10/on swap_blocks seed=4300204 frame=896/1000 hist=3 policy=0.6s elapsed=315s
[decide] 2026-11-28 00:22:23 ar_2task_e10/on swap_blocks seed=4300204 frame=928/1000 hist=3 policy=0.6s elapsed=325s
[decide] 2026-11-28 00:22:42 ar_2task_e10/on swap_blocks seed=4300204 frame=960/1000 hist=3 policy=0.6s elapsed=343s
[decide] 2026-11-28 00:22:57 ar_2task_e10/on swap_blocks seed=4300204 frame=992/1000 hist=3 policy=0.6s elapsed=359s
[closed-loop] 2026-11-28 00:23:02 done  ar_2task_e10/on swap_blocks seed=4300204 success=False targets=1000/1000 reward=0.0 lift=0.08589684963226318  410s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar_2task_e10/on         swap_blocks       65     0.06  [0.02,0.15]      0.83    0.06      985        -        -        -    0.6

[summary] 65 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/stepa/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-stepa-ar_2task_e10-s1.log):
```

[pool] 2026-11-28 07:13:18 exec A40-stepa-ar_2task_e10-s1 GPU 0 
[pool] 2026-11-28 07:13:22 A40-stepa-ar_2task_e10-s1: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e10-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e10-s1.md
[queue5] 2026-11-28 08:25:50 A40-stepa-ar_2task_e10-s1: DONE  swap_blocks/on n=65 lifted=54 s1=54 s2=43 s3=38 pressed=12 success=4 prog=0.51
```

## A40-stepa-ar_2task_e10-s2 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e10-s2.log):
```
[decide] 2026-11-28 00:16:30 ar_2task_e10/on swap_blocks seed=4300206 frame=416/1000 hist=3 policy=0.6s elapsed=155s
[decide] 2026-11-28 00:16:45 ar_2task_e10/on swap_blocks seed=4300206 frame=448/1000 hist=3 policy=0.6s elapsed=169s
[decide] 2026-11-28 00:16:57 ar_2task_e10/on swap_blocks seed=4300206 frame=480/1000 hist=3 policy=0.6s elapsed=181s
[decide] 2026-11-28 00:17:11 ar_2task_e10/on swap_blocks seed=4300206 frame=512/1000 hist=3 policy=0.6s elapsed=195s
[decide] 2026-11-28 00:17:21 ar_2task_e10/on swap_blocks seed=4300206 frame=544/1000 hist=3 policy=0.6s elapsed=206s
[decide] 2026-11-28 00:17:31 ar_2task_e10/on swap_blocks seed=4300206 frame=576/1000 hist=3 policy=0.6s elapsed=216s
[decide] 2026-11-28 00:17:42 ar_2task_e10/on swap_blocks seed=4300206 frame=608/1000 hist=3 policy=0.6s elapsed=226s
[decide] 2026-11-28 00:17:52 ar_2task_e10/on swap_blocks seed=4300206 frame=640/1000 hist=3 policy=0.6s elapsed=236s
[decide] 2026-11-28 00:18:03 ar_2task_e10/on swap_blocks seed=4300206 frame=672/1000 hist=3 policy=0.6s elapsed=247s
[decide] 2026-11-28 00:18:13 ar_2task_e10/on swap_blocks seed=4300206 frame=704/1000 hist=3 policy=0.6s elapsed=257s
[decide] 2026-11-28 00:18:30 ar_2task_e10/on swap_blocks seed=4300206 frame=736/1000 hist=3 policy=0.6s elapsed=274s
[decide] 2026-11-28 00:18:40 ar_2task_e10/on swap_blocks seed=4300206 frame=768/1000 hist=3 policy=0.6s elapsed=284s
[decide] 2026-11-28 00:18:50 ar_2task_e10/on swap_blocks seed=4300206 frame=800/1000 hist=3 policy=0.6s elapsed=294s
[decide] 2026-11-28 00:19:00 ar_2task_e10/on swap_blocks seed=4300206 frame=832/1000 hist=3 policy=0.6s elapsed=305s
[decide] 2026-11-28 00:19:10 ar_2task_e10/on swap_blocks seed=4300206 frame=864/1000 hist=3 policy=0.6s elapsed=315s
[decide] 2026-11-28 00:19:21 ar_2task_e10/on swap_blocks seed=4300206 frame=896/1000 hist=3 policy=0.6s elapsed=325s
[decide] 2026-11-28 00:19:31 ar_2task_e10/on swap_blocks seed=4300206 frame=928/1000 hist=3 policy=0.6s elapsed=336s
[decide] 2026-11-28 00:19:41 ar_2task_e10/on swap_blocks seed=4300206 frame=960/1000 hist=3 policy=0.6s elapsed=346s
[decide] 2026-11-28 00:19:52 ar_2task_e10/on swap_blocks seed=4300206 frame=992/1000 hist=3 policy=0.6s elapsed=356s
[closed-loop] 2026-11-28 00:19:57 done  ar_2task_e10/on swap_blocks seed=4300206 success=False targets=1000/1000 reward=0.0 lift=0.0773358941078186  401s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar_2task_e10/on         swap_blocks       62     0.06  [0.03,0.15]      0.84    0.06      985        -        -        -    0.6

[summary] 62 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/stepa/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-stepa-ar_2task_e10-s2.log):
```

[pool] 2026-11-28 07:13:53 exec A40-stepa-ar_2task_e10-s2 GPU 1 
[pool] 2026-11-28 07:13:56 A40-stepa-ar_2task_e10-s2: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e10-s2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e10-s2.md
[queue5] 2026-11-28 08:22:35 A40-stepa-ar_2task_e10-s2: DONE  swap_blocks/on n=62 lifted=52 s1=52 s2=41 s3=36 pressed=11 success=4 prog=0.51
```

## A40-stepa-ar_2task_e10-s3 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e10-s3.log):
```
[decide] 2026-11-28 00:21:06 ar_2task_e10/on swap_blocks seed=4300208 frame=416/1000 hist=3 policy=0.6s elapsed=139s
[decide] 2026-11-28 00:21:17 ar_2task_e10/on swap_blocks seed=4300208 frame=448/1000 hist=3 policy=0.5s elapsed=149s
[decide] 2026-11-28 00:21:34 ar_2task_e10/on swap_blocks seed=4300208 frame=480/1000 hist=3 policy=0.5s elapsed=166s
[decide] 2026-11-28 00:21:44 ar_2task_e10/on swap_blocks seed=4300208 frame=512/1000 hist=3 policy=0.5s elapsed=176s
[decide] 2026-11-28 00:21:54 ar_2task_e10/on swap_blocks seed=4300208 frame=544/1000 hist=3 policy=0.5s elapsed=186s
[decide] 2026-11-28 00:22:04 ar_2task_e10/on swap_blocks seed=4300208 frame=576/1000 hist=3 policy=0.5s elapsed=196s
[decide] 2026-11-28 00:22:14 ar_2task_e10/on swap_blocks seed=4300208 frame=608/1000 hist=3 policy=0.5s elapsed=207s
[decide] 2026-11-28 00:22:25 ar_2task_e10/on swap_blocks seed=4300208 frame=640/1000 hist=3 policy=0.5s elapsed=217s
[decide] 2026-11-28 00:22:44 ar_2task_e10/on swap_blocks seed=4300208 frame=672/1000 hist=3 policy=0.5s elapsed=236s
[decide] 2026-11-28 00:22:58 ar_2task_e10/on swap_blocks seed=4300208 frame=704/1000 hist=3 policy=0.5s elapsed=251s
[decide] 2026-11-28 00:23:09 ar_2task_e10/on swap_blocks seed=4300208 frame=736/1000 hist=3 policy=0.5s elapsed=261s
[decide] 2026-11-28 00:23:19 ar_2task_e10/on swap_blocks seed=4300208 frame=768/1000 hist=3 policy=0.5s elapsed=272s
[decide] 2026-11-28 00:23:33 ar_2task_e10/on swap_blocks seed=4300208 frame=800/1000 hist=3 policy=0.6s elapsed=285s
[decide] 2026-11-28 00:23:49 ar_2task_e10/on swap_blocks seed=4300208 frame=832/1000 hist=3 policy=0.6s elapsed=301s
[decide] 2026-11-28 00:24:03 ar_2task_e10/on swap_blocks seed=4300208 frame=864/1000 hist=3 policy=0.6s elapsed=315s
[decide] 2026-11-28 00:24:13 ar_2task_e10/on swap_blocks seed=4300208 frame=896/1000 hist=3 policy=0.6s elapsed=325s
[decide] 2026-11-28 00:24:23 ar_2task_e10/on swap_blocks seed=4300208 frame=928/1000 hist=3 policy=0.5s elapsed=336s
[decide] 2026-11-28 00:24:33 ar_2task_e10/on swap_blocks seed=4300208 frame=960/1000 hist=3 policy=0.5s elapsed=346s
[decide] 2026-11-28 00:24:43 ar_2task_e10/on swap_blocks seed=4300208 frame=992/1000 hist=3 policy=0.5s elapsed=356s
[closed-loop] 2026-11-28 00:24:49 done  ar_2task_e10/on swap_blocks seed=4300208 success=False targets=1000/1000 reward=0.0 lift=0.07520079612731934  399s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar_2task_e10/on         swap_blocks       67     0.06  [0.02,0.14]      0.84    0.06      986        -        -        -    0.6

[summary] 67 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/stepa/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-stepa-ar_2task_e10-s3.log):
```

[pool] 2026-11-28 07:16:43 exec A40-stepa-ar_2task_e10-s3 GPU 6 
[pool] 2026-11-28 07:16:46 A40-stepa-ar_2task_e10-s3: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e10-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e10-s3.md
[queue5] 2026-11-28 08:27:39 A40-stepa-ar_2task_e10-s3: DONE  swap_blocks/on n=67 lifted=56 s1=56 s2=45 s3=40 pressed=12 success=4 prog=0.51
```

## A40-stepa-ar_2task_e10-s4 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e10-s4.log):
```
[decide] 2026-11-28 00:25:34 ar_2task_e10/on swap_blocks seed=4300209 frame=416/1000 hist=3 policy=0.5s elapsed=149s
[decide] 2026-11-28 00:25:44 ar_2task_e10/on swap_blocks seed=4300209 frame=448/1000 hist=3 policy=0.5s elapsed=160s
[decide] 2026-11-28 00:25:55 ar_2task_e10/on swap_blocks seed=4300209 frame=480/1000 hist=3 policy=0.5s elapsed=170s
[decide] 2026-11-28 00:26:05 ar_2task_e10/on swap_blocks seed=4300209 frame=512/1000 hist=3 policy=0.5s elapsed=180s
[decide] 2026-11-28 00:26:15 ar_2task_e10/on swap_blocks seed=4300209 frame=544/1000 hist=3 policy=0.5s elapsed=190s
[decide] 2026-11-28 00:26:28 ar_2task_e10/on swap_blocks seed=4300209 frame=576/1000 hist=3 policy=0.5s elapsed=203s
[decide] 2026-11-28 00:26:43 ar_2task_e10/on swap_blocks seed=4300209 frame=608/1000 hist=3 policy=0.5s elapsed=218s
[decide] 2026-11-28 00:26:53 ar_2task_e10/on swap_blocks seed=4300209 frame=640/1000 hist=3 policy=0.5s elapsed=228s
[decide] 2026-11-28 00:27:03 ar_2task_e10/on swap_blocks seed=4300209 frame=672/1000 hist=3 policy=0.5s elapsed=238s
[decide] 2026-11-28 00:27:13 ar_2task_e10/on swap_blocks seed=4300209 frame=704/1000 hist=3 policy=0.5s elapsed=248s
[decide] 2026-11-28 00:27:23 ar_2task_e10/on swap_blocks seed=4300209 frame=736/1000 hist=3 policy=0.5s elapsed=258s
[decide] 2026-11-28 00:27:33 ar_2task_e10/on swap_blocks seed=4300209 frame=768/1000 hist=3 policy=0.5s elapsed=268s
[decide] 2026-11-28 00:27:44 ar_2task_e10/on swap_blocks seed=4300209 frame=800/1000 hist=3 policy=0.5s elapsed=279s
[decide] 2026-11-28 00:27:54 ar_2task_e10/on swap_blocks seed=4300209 frame=832/1000 hist=3 policy=0.5s elapsed=289s
[decide] 2026-11-28 00:28:08 ar_2task_e10/on swap_blocks seed=4300209 frame=864/1000 hist=3 policy=0.5s elapsed=303s
[decide] 2026-11-28 00:28:23 ar_2task_e10/on swap_blocks seed=4300209 frame=896/1000 hist=3 policy=0.5s elapsed=318s
[decide] 2026-11-28 00:28:33 ar_2task_e10/on swap_blocks seed=4300209 frame=928/1000 hist=3 policy=0.5s elapsed=328s
[decide] 2026-11-28 00:28:43 ar_2task_e10/on swap_blocks seed=4300209 frame=960/1000 hist=3 policy=0.5s elapsed=338s
[decide] 2026-11-28 00:28:54 ar_2task_e10/on swap_blocks seed=4300209 frame=992/1000 hist=3 policy=0.5s elapsed=349s
[closed-loop] 2026-11-28 00:29:00 done  ar_2task_e10/on swap_blocks seed=4300209 success=False targets=1000/1000 reward=0.0 lift=0.08195817470550537  399s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar_2task_e10/on         swap_blocks       69     0.06  [0.02,0.14]      0.83    0.06      986        -        -        -    0.6

[summary] 69 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/stepa/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-stepa-ar_2task_e10-s4.log):
```

[pool] 2026-11-28 07:20:41 exec A40-stepa-ar_2task_e10-s4 GPU 4 
[pool] 2026-11-28 07:20:45 A40-stepa-ar_2task_e10-s4: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e10-s4.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e10-s4.md
[queue5] 2026-11-28 08:31:56 A40-stepa-ar_2task_e10-s4: DONE  swap_blocks/on n=69 lifted=57 s1=57 s2=46 s3=41 pressed=12 success=4 prog=0.51
```

## A40-stepa-ar_2task_e10-s5 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e10-s5.log):
```
[decide] 2026-11-28 00:26:23 ar_2task_e10/on swap_blocks seed=4300215 frame=416/1000 hist=3 policy=0.5s elapsed=139s
[decide] 2026-11-28 00:26:40 ar_2task_e10/on swap_blocks seed=4300215 frame=448/1000 hist=3 policy=0.6s elapsed=156s
[decide] 2026-11-28 00:26:51 ar_2task_e10/on swap_blocks seed=4300215 frame=480/1000 hist=3 policy=0.5s elapsed=167s
[decide] 2026-11-28 00:27:01 ar_2task_e10/on swap_blocks seed=4300215 frame=512/1000 hist=3 policy=0.6s elapsed=177s
[decide] 2026-11-28 00:27:11 ar_2task_e10/on swap_blocks seed=4300215 frame=544/1000 hist=3 policy=0.5s elapsed=187s
[decide] 2026-11-28 00:27:21 ar_2task_e10/on swap_blocks seed=4300215 frame=576/1000 hist=3 policy=0.6s elapsed=197s
[decide] 2026-11-28 00:27:31 ar_2task_e10/on swap_blocks seed=4300215 frame=608/1000 hist=3 policy=0.6s elapsed=207s
[decide] 2026-11-28 00:27:42 ar_2task_e10/on swap_blocks seed=4300215 frame=640/1000 hist=3 policy=0.6s elapsed=218s
[decide] 2026-11-28 00:27:53 ar_2task_e10/on swap_blocks seed=4300215 frame=672/1000 hist=3 policy=0.5s elapsed=229s
[decide] 2026-11-28 00:28:06 ar_2task_e10/on swap_blocks seed=4300215 frame=704/1000 hist=3 policy=0.5s elapsed=242s
[decide] 2026-11-28 00:28:21 ar_2task_e10/on swap_blocks seed=4300215 frame=736/1000 hist=3 policy=0.6s elapsed=257s
[decide] 2026-11-28 00:28:31 ar_2task_e10/on swap_blocks seed=4300215 frame=768/1000 hist=3 policy=0.5s elapsed=267s
[decide] 2026-11-28 00:28:42 ar_2task_e10/on swap_blocks seed=4300215 frame=800/1000 hist=3 policy=0.6s elapsed=278s
[decide] 2026-11-28 00:28:52 ar_2task_e10/on swap_blocks seed=4300215 frame=832/1000 hist=3 policy=0.6s elapsed=288s
[decide] 2026-11-28 00:29:02 ar_2task_e10/on swap_blocks seed=4300215 frame=864/1000 hist=3 policy=0.5s elapsed=298s
[decide] 2026-11-28 00:29:12 ar_2task_e10/on swap_blocks seed=4300215 frame=896/1000 hist=3 policy=0.5s elapsed=308s
[decide] 2026-11-28 00:29:23 ar_2task_e10/on swap_blocks seed=4300215 frame=928/1000 hist=3 policy=0.5s elapsed=319s
[decide] 2026-11-28 00:29:33 ar_2task_e10/on swap_blocks seed=4300215 frame=960/1000 hist=3 policy=0.6s elapsed=329s
[decide] 2026-11-28 00:29:44 ar_2task_e10/on swap_blocks seed=4300215 frame=992/1000 hist=3 policy=0.5s elapsed=340s
[closed-loop] 2026-11-28 00:29:49 done  ar_2task_e10/on swap_blocks seed=4300215 success=False targets=1000/1000 reward=0.0 lift=0.08218586444854736  390s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar_2task_e10/on         swap_blocks       71     0.06  [0.02,0.14]      0.83    0.06      987        -        -        -    0.6

[summary] 71 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/stepa/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-stepa-ar_2task_e10-s5.log):
```

[pool] 2026-11-28 07:21:50 exec A40-stepa-ar_2task_e10-s5 GPU 5 
[pool] 2026-11-28 07:21:54 A40-stepa-ar_2task_e10-s5: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e10-s5.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e10-s5.md
[queue5] 2026-11-28 08:32:51 A40-stepa-ar_2task_e10-s5: DONE  swap_blocks/on n=71 lifted=59 s1=59 s2=48 s3=42 pressed=12 success=4 prog=0.51
```

## A40-stepa-ar_2task_e10-s6 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e10-s6.log):
```
[decide] 2026-11-28 00:25:47 ar_2task_e10/on swap_blocks seed=4300220 frame=416/1000 hist=3 policy=0.5s elapsed=152s
[decide] 2026-11-28 00:25:58 ar_2task_e10/on swap_blocks seed=4300220 frame=448/1000 hist=3 policy=0.6s elapsed=163s
[decide] 2026-11-28 00:26:08 ar_2task_e10/on swap_blocks seed=4300220 frame=480/1000 hist=3 policy=0.5s elapsed=173s
[decide] 2026-11-28 00:26:18 ar_2task_e10/on swap_blocks seed=4300220 frame=512/1000 hist=3 policy=0.6s elapsed=183s
[decide] 2026-11-28 00:26:30 ar_2task_e10/on swap_blocks seed=4300220 frame=544/1000 hist=3 policy=0.5s elapsed=196s
[decide] 2026-11-28 00:26:45 ar_2task_e10/on swap_blocks seed=4300220 frame=576/1000 hist=3 policy=0.6s elapsed=211s
[decide] 2026-11-28 00:26:56 ar_2task_e10/on swap_blocks seed=4300220 frame=608/1000 hist=3 policy=0.6s elapsed=221s
[decide] 2026-11-28 00:27:06 ar_2task_e10/on swap_blocks seed=4300220 frame=640/1000 hist=3 policy=0.5s elapsed=231s
[decide] 2026-11-28 00:27:16 ar_2task_e10/on swap_blocks seed=4300220 frame=672/1000 hist=3 policy=0.6s elapsed=241s
[decide] 2026-11-28 00:27:26 ar_2task_e10/on swap_blocks seed=4300220 frame=704/1000 hist=3 policy=0.5s elapsed=251s
[decide] 2026-11-28 00:27:36 ar_2task_e10/on swap_blocks seed=4300220 frame=736/1000 hist=3 policy=0.5s elapsed=262s
[decide] 2026-11-28 00:27:47 ar_2task_e10/on swap_blocks seed=4300220 frame=768/1000 hist=3 policy=0.6s elapsed=273s
[decide] 2026-11-28 00:27:59 ar_2task_e10/on swap_blocks seed=4300220 frame=800/1000 hist=3 policy=0.5s elapsed=284s
[decide] 2026-11-28 00:28:17 ar_2task_e10/on swap_blocks seed=4300220 frame=832/1000 hist=3 policy=0.6s elapsed=302s
[decide] 2026-11-28 00:28:27 ar_2task_e10/on swap_blocks seed=4300220 frame=864/1000 hist=3 policy=0.5s elapsed=313s
[decide] 2026-11-28 00:28:38 ar_2task_e10/on swap_blocks seed=4300220 frame=896/1000 hist=3 policy=0.5s elapsed=323s
[decide] 2026-11-28 00:28:49 ar_2task_e10/on swap_blocks seed=4300220 frame=928/1000 hist=3 policy=0.5s elapsed=334s
[decide] 2026-11-28 00:28:59 ar_2task_e10/on swap_blocks seed=4300220 frame=960/1000 hist=3 policy=0.5s elapsed=344s
[decide] 2026-11-28 00:29:11 ar_2task_e10/on swap_blocks seed=4300220 frame=992/1000 hist=3 policy=0.5s elapsed=356s
[closed-loop] 2026-11-28 00:29:16 done  ar_2task_e10/on swap_blocks seed=4300220 success=False targets=1000/1000 reward=0.0 lift=0.08841311931610107  403s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar_2task_e10/on         swap_blocks       70     0.06  [0.02,0.14]      0.83    0.06      986        -        -        -    0.6

[summary] 70 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/stepa/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-stepa-ar_2task_e10-s6.log):
```

[pool] 2026-11-28 07:22:27 exec A40-stepa-ar_2task_e10-s6 GPU 7 
[pool] 2026-11-28 07:22:30 A40-stepa-ar_2task_e10-s6: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e10-s6.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e10-s6.md
[queue5] 2026-11-28 08:32:16 A40-stepa-ar_2task_e10-s6: DONE  swap_blocks/on n=70 lifted=58 s1=58 s2=47 s3=42 pressed=12 success=4 prog=0.51
```

## A40-stepa-ar_2task_e10-s7 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e10-s7.log):
```
[decide] 2026-11-28 01:27:16 ar_2task_e10/on swap_blocks seed=4300223 frame=544/1000 hist=3 policy=0.6s elapsed=194s
[decide] 2026-11-28 01:27:36 ar_2task_e10/on swap_blocks seed=4300223 frame=576/1000 hist=3 policy=0.6s elapsed=214s
[decide] 2026-11-28 01:27:47 ar_2task_e10/on swap_blocks seed=4300223 frame=608/1000 hist=3 policy=0.7s elapsed=225s
[decide] 2026-11-28 01:27:57 ar_2task_e10/on swap_blocks seed=4300223 frame=640/1000 hist=3 policy=0.6s elapsed=235s
[decide] 2026-11-28 01:28:07 ar_2task_e10/on swap_blocks seed=4300223 frame=672/1000 hist=3 policy=0.6s elapsed=245s
[decide] 2026-11-28 01:28:19 ar_2task_e10/on swap_blocks seed=4300223 frame=704/1000 hist=3 policy=0.6s elapsed=257s
[decide] 2026-11-28 01:28:36 ar_2task_e10/on swap_blocks seed=4300223 frame=736/1000 hist=3 policy=0.8s elapsed=274s
[decide] 2026-11-28 01:28:49 ar_2task_e10/on swap_blocks seed=4300223 frame=768/1000 hist=3 policy=0.8s elapsed=288s
[decide] 2026-11-28 01:29:03 ar_2task_e10/on swap_blocks seed=4300223 frame=800/1000 hist=3 policy=0.7s elapsed=301s
[decide] 2026-11-28 01:29:20 ar_2task_e10/on swap_blocks seed=4300223 frame=832/1000 hist=3 policy=0.8s elapsed=318s
[decide] 2026-11-28 01:29:39 ar_2task_e10/on swap_blocks seed=4300223 frame=864/1000 hist=3 policy=0.8s elapsed=338s
[decide] 2026-11-28 01:29:52 ar_2task_e10/on swap_blocks seed=4300223 frame=896/1000 hist=3 policy=0.9s elapsed=350s
[decide] 2026-11-28 01:30:03 ar_2task_e10/on swap_blocks seed=4300223 frame=928/1000 hist=3 policy=0.8s elapsed=362s
[decide] 2026-11-28 01:30:15 ar_2task_e10/on swap_blocks seed=4300223 frame=960/1000 hist=3 policy=0.8s elapsed=373s
[decide] 2026-11-28 01:30:27 ar_2task_e10/on swap_blocks seed=4300223 frame=992/1000 hist=3 policy=0.8s elapsed=385s
[closed-loop] 2026-11-28 01:30:33 done  ar_2task_e10/on swap_blocks seed=4300223 success=False targets=1000/1000 reward=0.0 lift=0.07164174318313599  431s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar_2task_e10/on         swap_blocks       98     0.06  [0.03,0.13]      0.84    0.06      985        -        -        -    0.6
ar_2task_e20/on         swap_blocks       32     0.31  [0.18,0.49]      1.00    0.31      867        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar_2task_e10/on          vs ar_2task_e20/on           32     1       2       9       20  0.065

[summary] 130 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/stepa/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-stepa-ar_2task_e10-s7.log):
```

[pool] 2026-11-28 08:19:58 exec A40-stepa-ar_2task_e10-s7 GPU 3 
[pool] 2026-11-28 08:20:02 A40-stepa-ar_2task_e10-s7: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e10-s7.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e10-s7.md
[queue5] 2026-11-28 09:36:13 A40-stepa-ar_2task_e10-s7: DONE  swap_blocks/on n=98 lifted=82 s1=82 s2=69 s3=56 pressed=19 success=6 prog=0.52
```

## A40-stepa-ar_2task_e10-s8 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e10-s8.log):
```
[decide] 2026-11-28 01:33:02 ar_2task_e10/on swap_blocks seed=4300224 frame=544/1000 hist=3 policy=0.8s elapsed=251s
[decide] 2026-11-28 01:33:14 ar_2task_e10/on swap_blocks seed=4300224 frame=576/1000 hist=3 policy=0.7s elapsed=263s
[decide] 2026-11-28 01:33:26 ar_2task_e10/on swap_blocks seed=4300224 frame=608/1000 hist=3 policy=0.8s elapsed=275s
[decide] 2026-11-28 01:33:38 ar_2task_e10/on swap_blocks seed=4300224 frame=640/1000 hist=3 policy=0.8s elapsed=287s
[decide] 2026-11-28 01:33:52 ar_2task_e10/on swap_blocks seed=4300224 frame=672/1000 hist=3 policy=0.9s elapsed=300s
[decide] 2026-11-28 01:34:06 ar_2task_e10/on swap_blocks seed=4300224 frame=704/1000 hist=3 policy=0.7s elapsed=315s
[decide] 2026-11-28 01:34:18 ar_2task_e10/on swap_blocks seed=4300224 frame=736/1000 hist=3 policy=0.8s elapsed=327s
[decide] 2026-11-28 01:34:31 ar_2task_e10/on swap_blocks seed=4300224 frame=768/1000 hist=3 policy=0.8s elapsed=340s
[decide] 2026-11-28 01:34:43 ar_2task_e10/on swap_blocks seed=4300224 frame=800/1000 hist=3 policy=0.8s elapsed=352s
[decide] 2026-11-28 01:34:58 ar_2task_e10/on swap_blocks seed=4300224 frame=832/1000 hist=3 policy=0.7s elapsed=367s
[decide] 2026-11-28 01:35:17 ar_2task_e10/on swap_blocks seed=4300224 frame=864/1000 hist=3 policy=0.8s elapsed=386s
[decide] 2026-11-28 01:35:34 ar_2task_e10/on swap_blocks seed=4300224 frame=896/1000 hist=3 policy=0.7s elapsed=403s
[decide] 2026-11-28 01:35:51 ar_2task_e10/on swap_blocks seed=4300224 frame=928/1000 hist=3 policy=0.8s elapsed=420s
[decide] 2026-11-28 01:36:04 ar_2task_e10/on swap_blocks seed=4300224 frame=960/1000 hist=3 policy=0.7s elapsed=433s
[decide] 2026-11-28 01:36:16 ar_2task_e10/on swap_blocks seed=4300224 frame=992/1000 hist=3 policy=0.8s elapsed=445s
[closed-loop] 2026-11-28 01:36:23 done  ar_2task_e10/on swap_blocks seed=4300224 success=False targets=1000/1000 reward=0.0 lift=0.08008831739425659  496s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar_2task_e10/on         swap_blocks      100     0.06  [0.03,0.12]      0.84    0.06      985        -        -        -    0.6
ar_2task_e20/on         swap_blocks       35     0.34  [0.21,0.51]      1.00    0.34      854        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar_2task_e10/on          vs ar_2task_e20/on           35     1       2      11       21  0.022

[summary] 135 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/stepa/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-stepa-ar_2task_e10-s8.log):
```

[pool] 2026-11-28 08:22:15 exec A40-stepa-ar_2task_e10-s8 GPU 1 
[pool] 2026-11-28 08:22:18 A40-stepa-ar_2task_e10-s8: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e10-s8.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e10-s8.md
[queue5] 2026-11-28 09:42:06 A40-stepa-ar_2task_e10-s8: DONE  swap_blocks/on n=100 lifted=84 s1=84 s2=70 s3=57 pressed=19 success=6 prog=0.52
```

## A40-stepa-ar_2task_e10-s9 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e10-s9.log):
```
[decide] 2026-11-28 01:32:02 ar_2task_e10/on swap_blocks seed=4300226 frame=544/1000 hist=3 policy=0.8s elapsed=251s
[decide] 2026-11-28 01:32:15 ar_2task_e10/on swap_blocks seed=4300226 frame=576/1000 hist=3 policy=0.8s elapsed=265s
[decide] 2026-11-28 01:32:27 ar_2task_e10/on swap_blocks seed=4300226 frame=608/1000 hist=3 policy=0.8s elapsed=277s
[decide] 2026-11-28 01:32:39 ar_2task_e10/on swap_blocks seed=4300226 frame=640/1000 hist=3 policy=0.7s elapsed=289s
[decide] 2026-11-28 01:32:51 ar_2task_e10/on swap_blocks seed=4300226 frame=672/1000 hist=3 policy=0.8s elapsed=301s
[decide] 2026-11-28 01:33:03 ar_2task_e10/on swap_blocks seed=4300226 frame=704/1000 hist=3 policy=0.9s elapsed=313s
[decide] 2026-11-28 01:33:16 ar_2task_e10/on swap_blocks seed=4300226 frame=736/1000 hist=3 policy=0.8s elapsed=325s
[decide] 2026-11-28 01:33:28 ar_2task_e10/on swap_blocks seed=4300226 frame=768/1000 hist=3 policy=0.8s elapsed=338s
[decide] 2026-11-28 01:33:42 ar_2task_e10/on swap_blocks seed=4300226 frame=800/1000 hist=3 policy=0.9s elapsed=351s
[decide] 2026-11-28 01:33:54 ar_2task_e10/on swap_blocks seed=4300226 frame=832/1000 hist=3 policy=0.8s elapsed=364s
[decide] 2026-11-28 01:34:07 ar_2task_e10/on swap_blocks seed=4300226 frame=864/1000 hist=3 policy=0.8s elapsed=376s
[decide] 2026-11-28 01:34:19 ar_2task_e10/on swap_blocks seed=4300226 frame=896/1000 hist=3 policy=0.8s elapsed=389s
[decide] 2026-11-28 01:34:31 ar_2task_e10/on swap_blocks seed=4300226 frame=928/1000 hist=3 policy=0.7s elapsed=401s
[decide] 2026-11-28 01:34:43 ar_2task_e10/on swap_blocks seed=4300226 frame=960/1000 hist=3 policy=0.8s elapsed=413s
[decide] 2026-11-28 01:34:59 ar_2task_e10/on swap_blocks seed=4300226 frame=992/1000 hist=3 policy=0.8s elapsed=428s
[closed-loop] 2026-11-28 01:35:10 done  ar_2task_e10/on swap_blocks seed=4300226 success=False targets=1000/1000 reward=0.0 lift=0.08541858196258545  486s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar_2task_e10/on         swap_blocks       99     0.06  [0.03,0.13]      0.84    0.06      985        -        -        -    0.6
ar_2task_e20/on         swap_blocks       34     0.35  [0.21,0.52]      1.00    0.35      850        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar_2task_e10/on          vs ar_2task_e20/on           34     1       2      11       20  0.022

[summary] 133 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/stepa/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-stepa-ar_2task_e10-s9.log):
```

[pool] 2026-11-28 08:25:06 exec A40-stepa-ar_2task_e10-s9 GPU 0 
[pool] 2026-11-28 08:25:10 A40-stepa-ar_2task_e10-s9: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e10-s9.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e10-s9.md
[queue5] 2026-11-28 09:40:54 A40-stepa-ar_2task_e10-s9: DONE  swap_blocks/on n=99 lifted=83 s1=83 s2=69 s3=56 pressed=19 success=6 prog=0.52
```

## A40-stepa-ar_2task_e20-s0 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e20-s0.log):
```
[decide] 2026-11-28 01:40:01 ar_2task_e20/on swap_blocks seed=4300202 frame=544/1000 hist=3 policy=0.8s elapsed=232s
[decide] 2026-11-28 01:40:13 ar_2task_e20/on swap_blocks seed=4300202 frame=576/1000 hist=3 policy=0.7s elapsed=245s
[decide] 2026-11-28 01:40:26 ar_2task_e20/on swap_blocks seed=4300202 frame=608/1000 hist=3 policy=0.8s elapsed=257s
[decide] 2026-11-28 01:40:38 ar_2task_e20/on swap_blocks seed=4300202 frame=640/1000 hist=3 policy=0.7s elapsed=269s
[decide] 2026-11-28 01:40:51 ar_2task_e20/on swap_blocks seed=4300202 frame=672/1000 hist=3 policy=0.9s elapsed=282s
[decide] 2026-11-28 01:41:04 ar_2task_e20/on swap_blocks seed=4300202 frame=704/1000 hist=3 policy=0.7s elapsed=295s
[decide] 2026-11-28 01:41:17 ar_2task_e20/on swap_blocks seed=4300202 frame=736/1000 hist=3 policy=0.9s elapsed=308s
[decide] 2026-11-28 01:41:29 ar_2task_e20/on swap_blocks seed=4300202 frame=768/1000 hist=3 policy=0.7s elapsed=320s
[decide] 2026-11-28 01:41:42 ar_2task_e20/on swap_blocks seed=4300202 frame=800/1000 hist=3 policy=0.7s elapsed=333s
[decide] 2026-11-28 01:41:54 ar_2task_e20/on swap_blocks seed=4300202 frame=832/1000 hist=3 policy=0.8s elapsed=346s
[decide] 2026-11-28 01:42:08 ar_2task_e20/on swap_blocks seed=4300202 frame=864/1000 hist=3 policy=0.8s elapsed=359s
[decide] 2026-11-28 01:42:22 ar_2task_e20/on swap_blocks seed=4300202 frame=896/1000 hist=3 policy=0.9s elapsed=374s
[decide] 2026-11-28 01:42:35 ar_2task_e20/on swap_blocks seed=4300202 frame=928/1000 hist=3 policy=0.8s elapsed=386s
[decide] 2026-11-28 01:42:48 ar_2task_e20/on swap_blocks seed=4300202 frame=960/1000 hist=3 policy=0.8s elapsed=399s
[decide] 2026-11-28 01:43:00 ar_2task_e20/on swap_blocks seed=4300202 frame=992/1000 hist=3 policy=0.8s elapsed=411s
[closed-loop] 2026-11-28 01:43:06 done  ar_2task_e20/on swap_blocks seed=4300202 success=False targets=1000/1000 reward=0.0 lift=0.09513092041015625  468s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar_2task_e10/on         swap_blocks      100     0.06  [0.03,0.12]      0.84    0.06      985        -        -        -    0.6
ar_2task_e20/on         swap_blocks       39     0.33  [0.21,0.49]      1.00    0.33      858        -        -        -    0.7

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar_2task_e10/on          vs ar_2task_e20/on           39     1       2      12       24  0.013

[summary] 139 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/stepa/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-stepa-ar_2task_e20-s0.log):
```

[pool] 2026-11-28 08:26:48 exec A40-stepa-ar_2task_e20-s0 GPU 6 
[pool] 2026-11-28 08:26:52 A40-stepa-ar_2task_e20-s0: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e20-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e20-s0.md
[queue5] 2026-11-28 09:44:55 A40-stepa-ar_2task_e20-s0: DONE  swap_blocks/on n=39 lifted=39 s1=39 s2=35 s3=33 pressed=20 success=13 prog=0.74
```

## A40-stepa-ar_2task_e20-s1 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e20-s1.log):
```
[decide] 2026-11-28 01:42:35 ar_2task_e20/on swap_blocks seed=4300204 frame=544/1000 hist=3 policy=0.8s elapsed=238s
[decide] 2026-11-28 01:42:48 ar_2task_e20/on swap_blocks seed=4300204 frame=576/1000 hist=3 policy=0.8s elapsed=251s
[decide] 2026-11-28 01:43:00 ar_2task_e20/on swap_blocks seed=4300204 frame=608/1000 hist=3 policy=0.7s elapsed=262s
[decide] 2026-11-28 01:43:15 ar_2task_e20/on swap_blocks seed=4300204 frame=640/1000 hist=3 policy=0.9s elapsed=277s
[decide] 2026-11-28 01:43:28 ar_2task_e20/on swap_blocks seed=4300204 frame=672/1000 hist=3 policy=0.8s elapsed=291s
[decide] 2026-11-28 01:43:42 ar_2task_e20/on swap_blocks seed=4300204 frame=704/1000 hist=3 policy=0.9s elapsed=305s
[decide] 2026-11-28 01:43:56 ar_2task_e20/on swap_blocks seed=4300204 frame=736/1000 hist=3 policy=0.7s elapsed=318s
[decide] 2026-11-28 01:44:10 ar_2task_e20/on swap_blocks seed=4300204 frame=768/1000 hist=3 policy=0.9s elapsed=333s
[decide] 2026-11-28 01:44:24 ar_2task_e20/on swap_blocks seed=4300204 frame=800/1000 hist=3 policy=0.7s elapsed=346s
[decide] 2026-11-28 01:44:38 ar_2task_e20/on swap_blocks seed=4300204 frame=832/1000 hist=3 policy=0.9s elapsed=361s
[decide] 2026-11-28 01:44:51 ar_2task_e20/on swap_blocks seed=4300204 frame=864/1000 hist=3 policy=0.8s elapsed=374s
[decide] 2026-11-28 01:45:06 ar_2task_e20/on swap_blocks seed=4300204 frame=896/1000 hist=3 policy=0.9s elapsed=388s
[decide] 2026-11-28 01:45:19 ar_2task_e20/on swap_blocks seed=4300204 frame=928/1000 hist=3 policy=0.7s elapsed=401s
[decide] 2026-11-28 01:45:33 ar_2task_e20/on swap_blocks seed=4300204 frame=960/1000 hist=3 policy=0.8s elapsed=416s
[decide] 2026-11-28 01:45:47 ar_2task_e20/on swap_blocks seed=4300204 frame=992/1000 hist=3 policy=0.7s elapsed=430s
[closed-loop] 2026-11-28 01:45:53 done  ar_2task_e20/on swap_blocks seed=4300204 success=False targets=1000/1000 reward=0.0 lift=0.103626549243927  487s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar_2task_e10/on         swap_blocks      100     0.06  [0.03,0.12]      0.84    0.06      985        -        -        -    0.6
ar_2task_e20/on         swap_blocks       40     0.33  [0.20,0.48]      1.00    0.33      862        -        -        -    0.7

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar_2task_e10/on          vs ar_2task_e20/on           40     1       2      12       25  0.013

[summary] 140 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/stepa/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-stepa-ar_2task_e20-s1.log):
```

[pool] 2026-11-28 08:31:20 exec A40-stepa-ar_2task_e20-s1 GPU 4 
[pool] 2026-11-28 08:31:24 A40-stepa-ar_2task_e20-s1: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e20-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e20-s1.md
[queue5] 2026-11-28 09:47:48 A40-stepa-ar_2task_e20-s1: DONE  swap_blocks/on n=40 lifted=40 s1=40 s2=36 s3=34 pressed=20 success=13 prog=0.74
```

## A40-stepa-ar_2task_e20-s2 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e20-s2.log):
```
[decide] 2026-11-28 01:35:42 ar_2task_e20/on swap_blocks seed=4300206 frame=544/1000 hist=3 policy=0.9s elapsed=242s
[decide] 2026-11-28 01:35:56 ar_2task_e20/on swap_blocks seed=4300206 frame=576/1000 hist=3 policy=0.9s elapsed=256s
[decide] 2026-11-28 01:36:09 ar_2task_e20/on swap_blocks seed=4300206 frame=608/1000 hist=3 policy=0.8s elapsed=269s
[decide] 2026-11-28 01:36:23 ar_2task_e20/on swap_blocks seed=4300206 frame=640/1000 hist=3 policy=0.9s elapsed=283s
[decide] 2026-11-28 01:36:36 ar_2task_e20/on swap_blocks seed=4300206 frame=672/1000 hist=3 policy=0.8s elapsed=296s
[decide] 2026-11-28 01:36:49 ar_2task_e20/on swap_blocks seed=4300206 frame=704/1000 hist=3 policy=0.9s elapsed=309s
[decide] 2026-11-28 01:37:03 ar_2task_e20/on swap_blocks seed=4300206 frame=736/1000 hist=3 policy=0.8s elapsed=323s
[decide] 2026-11-28 01:37:16 ar_2task_e20/on swap_blocks seed=4300206 frame=768/1000 hist=3 policy=0.8s elapsed=336s
[decide] 2026-11-28 01:37:30 ar_2task_e20/on swap_blocks seed=4300206 frame=800/1000 hist=3 policy=0.8s elapsed=350s
[decide] 2026-11-28 01:37:43 ar_2task_e20/on swap_blocks seed=4300206 frame=832/1000 hist=3 policy=0.8s elapsed=363s
[decide] 2026-11-28 01:37:59 ar_2task_e20/on swap_blocks seed=4300206 frame=864/1000 hist=3 policy=0.7s elapsed=379s
[decide] 2026-11-28 01:38:18 ar_2task_e20/on swap_blocks seed=4300206 frame=896/1000 hist=3 policy=0.9s elapsed=398s
[decide] 2026-11-28 01:38:30 ar_2task_e20/on swap_blocks seed=4300206 frame=928/1000 hist=3 policy=0.9s elapsed=410s
[decide] 2026-11-28 01:38:45 ar_2task_e20/on swap_blocks seed=4300206 frame=960/1000 hist=3 policy=1.0s elapsed=425s
[decide] 2026-11-28 01:38:57 ar_2task_e20/on swap_blocks seed=4300206 frame=992/1000 hist=3 policy=0.8s elapsed=437s
[closed-loop] 2026-11-28 01:39:03 done  ar_2task_e20/on swap_blocks seed=4300206 success=False targets=1000/1000 reward=0.0 lift=0.07788282632827759  498s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar_2task_e10/on         swap_blocks      100     0.06  [0.03,0.12]      0.84    0.06      985        -        -        -    0.6
ar_2task_e20/on         swap_blocks       37     0.32  [0.20,0.49]      1.00    0.32      862        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar_2task_e10/on          vs ar_2task_e20/on           37     1       2      11       23  0.022

[summary] 137 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/stepa/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-stepa-ar_2task_e20-s2.log):
```

[pool] 2026-11-28 08:31:20 exec A40-stepa-ar_2task_e20-s2 GPU 7 
[pool] 2026-11-28 08:31:24 A40-stepa-ar_2task_e20-s2: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e20-s2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e20-s2.md
[queue5] 2026-11-28 09:40:51 A40-stepa-ar_2task_e20-s2: DONE  swap_blocks/on n=37 lifted=37 s1=37 s2=33 s3=31 pressed=19 success=12 prog=0.73
```

## A40-stepa-ar_2task_e20-s3 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e20-s3.log):
```
[decide] 2026-11-28 01:36:39 ar_2task_e20/on swap_blocks seed=4300208 frame=96/1000 hist=3 policy=0.8s elapsed=52s
[decide] 2026-11-28 01:36:53 ar_2task_e20/on swap_blocks seed=4300208 frame=128/1000 hist=3 policy=0.9s elapsed=66s
[decide] 2026-11-28 01:37:08 ar_2task_e20/on swap_blocks seed=4300208 frame=160/1000 hist=3 policy=0.9s elapsed=81s
[decide] 2026-11-28 01:37:22 ar_2task_e20/on swap_blocks seed=4300208 frame=192/1000 hist=3 policy=0.9s elapsed=95s
[decide] 2026-11-28 01:37:37 ar_2task_e20/on swap_blocks seed=4300208 frame=224/1000 hist=3 policy=0.9s elapsed=110s
[decide] 2026-11-28 01:37:51 ar_2task_e20/on swap_blocks seed=4300208 frame=256/1000 hist=3 policy=0.9s elapsed=125s
[decide] 2026-11-28 01:38:14 ar_2task_e20/on swap_blocks seed=4300208 frame=288/1000 hist=3 policy=0.9s elapsed=147s
[decide] 2026-11-28 01:38:28 ar_2task_e20/on swap_blocks seed=4300208 frame=320/1000 hist=3 policy=0.9s elapsed=161s
[decide] 2026-11-28 01:38:42 ar_2task_e20/on swap_blocks seed=4300208 frame=352/1000 hist=3 policy=0.9s elapsed=176s
[decide] 2026-11-28 01:38:57 ar_2task_e20/on swap_blocks seed=4300208 frame=384/1000 hist=3 policy=0.9s elapsed=191s
[decide] 2026-11-28 01:39:12 ar_2task_e20/on swap_blocks seed=4300208 frame=416/1000 hist=3 policy=0.9s elapsed=206s
[decide] 2026-11-28 01:39:27 ar_2task_e20/on swap_blocks seed=4300208 frame=448/1000 hist=3 policy=0.9s elapsed=220s
[decide] 2026-11-28 01:39:41 ar_2task_e20/on swap_blocks seed=4300208 frame=480/1000 hist=3 policy=0.9s elapsed=235s
[decide] 2026-11-28 01:39:56 ar_2task_e20/on swap_blocks seed=4300208 frame=512/1000 hist=3 policy=0.9s elapsed=249s
[decide] 2026-11-28 01:40:11 ar_2task_e20/on swap_blocks seed=4300208 frame=544/1000 hist=3 policy=0.9s elapsed=264s
[closed-loop] 2026-11-28 01:40:27 done  ar_2task_e20/on swap_blocks seed=4300208 success=True targets=574/1000 reward=1.0 lift=0.09958875179290771  345s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar_2task_e10/on         swap_blocks      100     0.06  [0.03,0.12]      0.84    0.06      985        -        -        -    0.6
ar_2task_e20/on         swap_blocks       38     0.34  [0.21,0.50]      1.00    0.34      854        -        -        -    0.7

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar_2task_e10/on          vs ar_2task_e20/on           38     1       2      12       23  0.013

[summary] 138 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/stepa/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-stepa-ar_2task_e20-s3.log):
```

[pool] 2026-11-28 08:32:18 exec A40-stepa-ar_2task_e20-s3 GPU 5 
[pool] 2026-11-28 08:32:22 A40-stepa-ar_2task_e20-s3: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e20-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e20-s3.md
[queue5] 2026-11-28 09:42:12 A40-stepa-ar_2task_e20-s3: DONE  swap_blocks/on n=38 lifted=38 s1=38 s2=34 s3=32 pressed=20 success=13 prog=0.74
```

## A40-stepa-ar_2task_e20-s4 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e20-s4.log):
```
[decide] 2026-11-28 02:53:25 ar_2task_e20/on swap_blocks seed=4300209 frame=96/1000 hist=3 policy=0.6s elapsed=37s
[decide] 2026-11-28 02:53:36 ar_2task_e20/on swap_blocks seed=4300209 frame=128/1000 hist=3 policy=0.6s elapsed=48s
[decide] 2026-11-28 02:53:46 ar_2task_e20/on swap_blocks seed=4300209 frame=160/1000 hist=3 policy=0.6s elapsed=59s
[decide] 2026-11-28 02:53:57 ar_2task_e20/on swap_blocks seed=4300209 frame=192/1000 hist=3 policy=0.6s elapsed=69s
[decide] 2026-11-28 02:54:08 ar_2task_e20/on swap_blocks seed=4300209 frame=224/1000 hist=3 policy=0.6s elapsed=80s
[decide] 2026-11-28 02:54:18 ar_2task_e20/on swap_blocks seed=4300209 frame=256/1000 hist=3 policy=0.6s elapsed=90s
[decide] 2026-11-28 02:54:29 ar_2task_e20/on swap_blocks seed=4300209 frame=288/1000 hist=3 policy=0.6s elapsed=101s
[decide] 2026-11-28 02:54:42 ar_2task_e20/on swap_blocks seed=4300209 frame=320/1000 hist=3 policy=0.6s elapsed=114s
[decide] 2026-11-28 02:54:57 ar_2task_e20/on swap_blocks seed=4300209 frame=352/1000 hist=3 policy=0.6s elapsed=129s
[decide] 2026-11-28 02:55:08 ar_2task_e20/on swap_blocks seed=4300209 frame=384/1000 hist=3 policy=0.6s elapsed=140s
[decide] 2026-11-28 02:55:18 ar_2task_e20/on swap_blocks seed=4300209 frame=416/1000 hist=3 policy=0.6s elapsed=150s
[decide] 2026-11-28 02:55:29 ar_2task_e20/on swap_blocks seed=4300209 frame=448/1000 hist=3 policy=0.6s elapsed=161s
[decide] 2026-11-28 02:55:39 ar_2task_e20/on swap_blocks seed=4300209 frame=480/1000 hist=3 policy=0.6s elapsed=171s
[decide] 2026-11-28 02:55:49 ar_2task_e20/on swap_blocks seed=4300209 frame=512/1000 hist=3 policy=0.6s elapsed=181s
[decide] 2026-11-28 02:56:00 ar_2task_e20/on swap_blocks seed=4300209 frame=544/1000 hist=3 policy=0.6s elapsed=192s
[closed-loop] 2026-11-28 02:56:09 done  ar_2task_e20/on swap_blocks seed=4300209 success=True targets=565/1000 reward=1.0 lift=0.0988854169845581  239s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar_2task_e10/on         swap_blocks      100     0.06  [0.03,0.12]      0.84    0.06      985        -        -        -    0.6
ar_2task_e20/on         swap_blocks       57     0.40  [0.29,0.53]      0.98    0.40      828        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar_2task_e10/on          vs ar_2task_e20/on           57     1       2      22       32  0.000

[summary] 157 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/stepa/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-stepa-ar_2task_e20-s4.log):
```

[pool] 2026-11-28 10:01:45 exec A40-stepa-ar_2task_e20-s4 GPU 1 
[pool] 2026-11-28 10:01:49 A40-stepa-ar_2task_e20-s4: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e20-s4.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e20-s4.md
[queue5] 2026-11-28 10:57:58 A40-stepa-ar_2task_e20-s4: DONE  swap_blocks/on n=57 lifted=56 s1=56 s2=50 s3=48 pressed=33 success=23 prog=0.75
```

## A40-stepa-ar_2task_e20-s5 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e20-s5.log):
```
[decide] 2026-11-28 03:08:57 ar_2task_e20/on swap_blocks seed=4300215 frame=544/1000 hist=3 policy=0.6s elapsed=184s
[decide] 2026-11-28 03:09:08 ar_2task_e20/on swap_blocks seed=4300215 frame=576/1000 hist=3 policy=0.6s elapsed=195s
[decide] 2026-11-28 03:09:19 ar_2task_e20/on swap_blocks seed=4300215 frame=608/1000 hist=3 policy=0.6s elapsed=205s
[decide] 2026-11-28 03:09:29 ar_2task_e20/on swap_blocks seed=4300215 frame=640/1000 hist=3 policy=0.6s elapsed=215s
[decide] 2026-11-28 03:09:39 ar_2task_e20/on swap_blocks seed=4300215 frame=672/1000 hist=3 policy=0.6s elapsed=226s
[decide] 2026-11-28 03:09:49 ar_2task_e20/on swap_blocks seed=4300215 frame=704/1000 hist=3 policy=0.6s elapsed=236s
[decide] 2026-11-28 03:10:00 ar_2task_e20/on swap_blocks seed=4300215 frame=736/1000 hist=3 policy=0.6s elapsed=247s
[decide] 2026-11-28 03:10:10 ar_2task_e20/on swap_blocks seed=4300215 frame=768/1000 hist=3 policy=0.6s elapsed=257s
[decide] 2026-11-28 03:10:21 ar_2task_e20/on swap_blocks seed=4300215 frame=800/1000 hist=3 policy=0.6s elapsed=268s
[decide] 2026-11-28 03:10:32 ar_2task_e20/on swap_blocks seed=4300215 frame=832/1000 hist=3 policy=0.6s elapsed=279s
[decide] 2026-11-28 03:10:42 ar_2task_e20/on swap_blocks seed=4300215 frame=864/1000 hist=3 policy=0.6s elapsed=289s
[decide] 2026-11-28 03:10:53 ar_2task_e20/on swap_blocks seed=4300215 frame=896/1000 hist=3 policy=0.6s elapsed=300s
[decide] 2026-11-28 03:11:03 ar_2task_e20/on swap_blocks seed=4300215 frame=928/1000 hist=3 policy=0.6s elapsed=310s
[decide] 2026-11-28 03:11:17 ar_2task_e20/on swap_blocks seed=4300215 frame=960/1000 hist=3 policy=0.6s elapsed=323s
[decide] 2026-11-28 03:11:31 ar_2task_e20/on swap_blocks seed=4300215 frame=992/1000 hist=3 policy=0.6s elapsed=338s
[closed-loop] 2026-11-28 03:11:37 done  ar_2task_e20/on swap_blocks seed=4300215 success=False targets=1000/1000 reward=0.0 lift=0.1035916805267334  388s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar_2task_e10/on         swap_blocks      100     0.06  [0.03,0.12]      0.84    0.06      985        -        -        -    0.6
ar_2task_e20/on         swap_blocks       60     0.40  [0.29,0.53]      0.98    0.40      830        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar_2task_e10/on          vs ar_2task_e20/on           60     1       2      23       34  0.000

[summary] 160 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/stepa/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-stepa-ar_2task_e20-s5.log):
```

[pool] 2026-11-28 10:16:25 exec A40-stepa-ar_2task_e20-s5 GPU 5 
[pool] 2026-11-28 10:16:30 A40-stepa-ar_2task_e20-s5: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-stepa-ar_2task_e20-s5.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e20-s5.md
[queue5] 2026-11-28 11:13:32 A40-stepa-ar_2task_e20-s5: DONE  swap_blocks/on n=60 lifted=59 s1=59 s2=53 s3=51 pressed=34 success=24 prog=0.75
```

## A40-E22h-fetch-hid2 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22h-fetch-hid2.log):
```
[e22a100] 2026-11-28 23:49:15 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-28 23:54:16 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-28 23:59:16 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-29 00:04:17 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-29 00:09:17 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-29 00:14:18 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-29 00:19:18 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-29 00:24:19 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-29 00:29:20 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-29 00:34:20 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-29 00:39:21 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-29 00:44:21 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-29 00:49:22 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-29 00:54:22 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-29 00:59:23 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-29 01:04:23 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-29 01:09:24 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-29 01:14:25 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-29 01:19:25 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-29 01:24:26 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-29 01:29:26 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-29 01:34:27 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-29 01:39:27 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-29 01:44:28 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-29 01:49:28 waiting for diag/e22_a100/E22_A100_hid2.tar.gz (the A100 uploads it after its E22a cards)
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22h-fetch-hid2.log):
```

[pool] 2026-11-28 16:58:25 exec A40-E22h-fetch-hid2 GPU None 
[pool] 2026-11-28 16:58:29 A40-E22h-fetch-hid2: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22h-fetch-hid2.log
```

## verdicts in the last 24.0 h

- A40-V21-C25-e10look: **PASS** (2026-11-28 08:47:51) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-V21-C25-e10look.md
- A40-HF-autoprune-loop2: **PASS** (2026-11-28 14:16:21) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-HF-autoprune-loop2.md
- A40-fetch-obs_cf200-e30: **PASS** (2026-11-28 19:49:02) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-obs_cf200-e30.md
- A40-v21-obs_cf200-smoke: **PASS** (2026-11-28 19:53:45) observe_and_pickup/on n=1  prog=0.00
- A40-v21-obs_cf200-s0: **DONE** (2026-11-28 20:18:28) observe_and_pickup/on n=23  prog=0.00
- A40-v21-obs_cf200-s1: **DONE** (2026-11-28 20:28:31) observe_and_pickup/on n=40  prog=0.00
- A40-v21-obs_cf200-s2: **DONE** (2026-11-28 20:29:51) observe_and_pickup/on n=44  prog=0.00
- A40-v21-obs_cf200-s3: **DONE** (2026-11-28 20:30:44) observe_and_pickup/on n=46  prog=0.00
- A40-v21-obs_cf200-s4: **DONE** (2026-11-28 20:43:49) observe_and_pickup/on n=77  prog=0.00
- A40-v21-obs_cf200-s5: **DONE** (2026-11-28 20:51:39) observe_and_pickup/on n=95  prog=0.00
- A40-v21-obs_cf200-s6: **DONE** (2026-11-28 20:50:01) observe_and_pickup/on n=91  prog=0.00
- A40-v21-obs_cf200-s7: **DONE** (2026-11-28 20:51:18) observe_and_pickup/on n=94  prog=0.00
- A40-v21-obs_cf200-s8: **DONE** (2026-11-28 20:56:17) observe_and_pickup/on n=99  prog=0.00
- A40-v21-obs_cf200-s9: **DONE** (2026-11-28 20:56:29) observe_and_pickup/on n=100  prog=0.00
- A40-V21-C25-verdict: **PASS** (2026-11-28 20:56:43) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-V21-C25-verdict.md
- A40-fetch-rearr_pw_s18-e30: **PASS** (2026-11-28 04:12:46) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-rearr_pw_s18-e30.md
- A40-v21-rearr_pw_s18-smoke: **PASS** (2026-11-28 04:27:52) rearrange_blocks/on n=1  prog=0.00
- A40-v21-rearr_pw_s18-s0: **DONE** (2026-11-28 05:15:07) rearrange_blocks/on n=36  prog=0.00
- A40-v21-rearr_pw_s18-s1: **DONE** (2026-11-28 05:07:46) rearrange_blocks/on n=30  prog=0.00
- A40-v21-rearr_pw_s18-s2: **DONE** (2026-11-28 05:21:47) rearrange_blocks/on n=43  prog=0.00
- A40-v21-rearr_pw_s18-s3: **DONE** (2026-11-28 05:21:23) rearrange_blocks/on n=42  prog=0.00
- A40-v21-rearr_pw_s18-s4: **DONE** (2026-11-28 05:52:25) rearrange_blocks/on n=88  prog=0.00
- A40-v21-rearr_pw_s18-s5: **DONE** (2026-11-28 05:51:49) rearrange_blocks/on n=86  prog=0.00
- A40-v21-rearr_pw_s18-s6: **DONE** (2026-11-28 05:58:47) rearrange_blocks/on n=94  prog=0.00
- A40-v21-rearr_pw_s18-s7: **DONE** (2026-11-28 06:07:57) rearrange_blocks/on n=100  prog=0.00
- A40-v21-rearr_pw_s18-s8: **DONE** (2026-11-28 06:03:43) rearrange_blocks/on n=98  prog=0.00
- A40-v21-rearr_pw_s18-s9: **DONE** (2026-11-28 06:06:42) rearrange_blocks/on n=99  prog=0.00
- A40-V21-C22-report: **PASS** (2026-11-28 06:10:01) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-V21-C22-report.md
- A40-fetch-swapT_joint3-e30: **PASS** (2026-11-28 18:30:16) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-swapT_joint3-e30.md
- A40-v20joint3-smoke: **PASS** (2026-11-28 18:53:10) swap_T/on n=1  prog=0.00
- A40-v20joint3-s0: **DONE** (2026-11-28 19:28:51) swap_T/on n=56  prog=0.00
- A40-v20joint3-s1: **DONE** (2026-11-28 19:29:15) swap_T/on n=57  prog=0.00
- A40-v20joint3-s2: **DONE** (2026-11-28 19:28:10) swap_T/on n=55  prog=0.00
- A40-v20joint3-s3: **DONE** (2026-11-28 19:33:45) swap_T/on n=64  prog=0.00
- A40-v20joint3-s4: **DONE** (2026-11-28 19:35:52) swap_T/on n=69  prog=0.00
- A40-v20joint3-s5: **DONE** (2026-11-28 19:33:47) swap_T/on n=65  prog=0.00
- A40-v20joint3-s6: **DONE** (2026-11-28 19:48:09) swap_T/on n=84  prog=0.00
- A40-v20joint3-s7: **DONE** (2026-11-28 20:02:35) swap_T/on n=98  prog=0.00
- A40-v20joint3-s8: **DONE** (2026-11-28 20:05:22) swap_T/on n=100  prog=0.00
- A40-v20joint3-s9: **DONE** (2026-11-28 20:04:38) swap_T/on n=99  prog=0.00
- A40-v20joint3-swap-s0: **DONE** (2026-11-28 20:24:35) swap_blocks/on n=28 lifted=28 s1=28 s2=28 s3=28 pressed=28 success=28 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-swap-s0.md
- A40-v20joint3-swap-s1: **DONE** (2026-11-28 20:25:27) swap_blocks/on n=29 lifted=29 s1=29 s2=29 s3=29 pressed=29 success=29 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-swap-s1.md
- A40-v20joint3-swap-s2: **DONE** (2026-11-28 20:26:54) swap_blocks/on n=30 lifted=30 s1=30 s2=30 s3=30 pressed=30 success=30 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-swap-s2.md
- A40-v20joint3-swap-s3: **DONE** (2026-11-28 21:22:09) swap_blocks/on n=72 lifted=72 s1=72 s2=72 s3=72 pressed=72 success=72 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-swap-s3.md
- A40-v20joint3-swap-s4: **DONE** (2026-11-28 21:33:17) swap_blocks/on n=88 lifted=88 s1=88 s2=88 s3=88 pressed=88 success=88 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-swap-s4.md
- A40-v20joint3-swap-s5: **DONE** (2026-11-28 21:38:23) swap_blocks/on n=94 lifted=94 s1=94 s2=94 s3=94 pressed=94 success=94 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-swap-s5.md
- A40-v20joint3-swap-s6: **DONE** (2026-11-28 21:40:13) swap_blocks/on n=95 lifted=95 s1=95 s2=95 s3=95 pressed=95 success=95 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-swap-s6.md
- A40-v20joint3-swap-s7: **DONE** (2026-11-28 21:41:57) swap_blocks/on n=98 lifted=98 s1=98 s2=98 s3=98 pressed=98 success=98 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-swap-s7.md
- A40-v20joint3-swap-s8: **DONE** (2026-11-28 21:46:04) swap_blocks/on n=100 lifted=100 s1=100 s2=100 s3=100 pressed=100 success=100 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-swap-s8.md
- A40-v20joint3-swap-s9: **DONE** (2026-11-28 21:44:34) swap_blocks/on n=99 lifted=99 s1=99 s2=99 s3=99 pressed=99 success=99 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-swap-s9.md
- A40-v20joint3-put-s0: **DONE** (2026-11-28 22:18:42) put_back_block/on n=39 lifted=39 centre=39 pressed=39 stage1=39 regrasp=39 returned=39 success=39 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-put-s0.md
- A40-v20joint3-put-s1: **DONE** (2026-11-28 22:06:51) put_back_block/on n=26 lifted=26 centre=26 pressed=26 stage1=26 regrasp=26 returned=26 success=26 prog=1.00; errors=2
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-put-s1.md
- A40-v20joint3-put-s2: **DONE** (2026-11-28 22:25:32) put_back_block/on n=54 lifted=54 centre=54 pressed=54 stage1=54 regrasp=54 returned=54 success=54 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-put-s2.md
- A40-v20joint3-put-s3: **DONE** (2026-11-28 22:24:45) put_back_block/on n=51 lifted=51 centre=51 pressed=51 stage1=51 regrasp=51 returned=51 success=51 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-put-s3.md
- A40-v20joint3-put-s4: **DONE** (2026-11-28 22:43:54) put_back_block/on n=89 lifted=89 centre=89 pressed=89 stage1=89 regrasp=89 returned=89 success=89 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-put-s4.md
- A40-v20joint3-put-s5: **DONE** (2026-11-28 22:44:12) put_back_block/on n=90 lifted=90 centre=90 pressed=90 stage1=90 regrasp=90 returned=90 success=90 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-put-s5.md
- A40-v20joint3-put-s6: **DONE** (2026-11-28 22:44:30) put_back_block/on n=91 lifted=91 centre=91 pressed=91 stage1=91 regrasp=91 returned=91 success=91 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-put-s6.md
- A40-v20joint3-put-s7: **DONE** (2026-11-28 22:45:41) put_back_block/on n=92 lifted=92 centre=92 pressed=92 stage1=92 regrasp=92 returned=92 success=92 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-put-s7.md
- A40-v20joint3-put-s8: **DONE** (2026-11-28 22:51:44) put_back_block/on n=97 lifted=97 centre=97 pressed=97 stage1=97 regrasp=97 returned=97 success=97 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-put-s8.md
- A40-v20joint3-put-s9: **DONE** (2026-11-28 22:57:26) put_back_block/on n=100 lifted=100 centre=100 pressed=100 stage1=100 regrasp=100 returned=100 success=100 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-v20joint3-put-s9.md
- A40-joint3-verdict: **PASS** (2026-11-28 22:57:49) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-joint3-verdict.md
- A40-C36FB-bank-put: **PASS** (2026-11-29 01:09:12) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-C36FB-bank-put.md
- A40-d8-swapT_x16-s0: **DONE** (2026-11-28 17:31:03) swap_T/on n=49  prog=0.00
- A40-d8-swapT_x16-s1: **DONE** (2026-11-28 17:16:53) swap_T/on n=40  prog=0.00; errors=4
- A40-d8-swapT_x16-s2: **DONE** (2026-11-28 17:06:04) swap_T/on n=28  prog=0.00; errors=6
- A40-d8-swapT_x16-s3: **DONE** (2026-11-28 17:14:13) swap_T/on n=37  prog=0.00; errors=4
- A40-d8-swapT_x16-s4: **DONE** (2026-11-28 17:33:58) swap_T/on n=50  prog=0.00
- A40-d8-swapT_x32-s0: **DONE** (2026-11-28 17:51:46) swap_T/on n=34  prog=0.00
- A40-d8-swapT_x32-s1: **DONE** (2026-11-28 17:52:19) swap_T/on n=35  prog=0.00
- A40-d8-swapT_x32-s2: **DONE** (2026-11-28 18:03:06) swap_T/on n=47  prog=0.00
- A40-d8-swapT_x32-s3: **DONE** (2026-11-28 18:00:05) swap_T/on n=44  prog=0.00
- A40-d8-swapT_x32-s4: **DONE** (2026-11-28 18:09:29) swap_T/on n=50  prog=0.00
- A40-d8-swapT_s50-s0: **DONE** (2026-11-28 18:48:00) swap_T/on n=39  prog=0.00
- A40-d8-swapT_s50-s1: **DONE** (2026-11-28 18:51:47) swap_T/on n=43  prog=0.00
- A40-d8-swapT_s50-s2: **DONE** (2026-11-28 18:58:37) swap_T/on n=47  prog=0.00
- A40-d8-swapT_s50-s3: **DONE** (2026-11-28 18:53:22) swap_T/on n=45  prog=0.00
- A40-d8-swapT_s50-s4: **DONE** (2026-11-28 19:11:53) swap_T/on n=50  prog=0.00
- A40-d8-swapT-report: **ERROR** (2026-11-28 19:33:17) rc=1
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-swapT-report.md
- A40-d8-swapT_x16-gate: **ERROR** (2026-11-28 19:54:03) rc=3
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-swapT_x16-gate.md
- A40-d8-swapT_x16-b0: **SKIPPED** (2026-11-28 19:54:34) 
- A40-d8-swapT_x16-b1: **SKIPPED** (2026-11-28 19:54:35) 
- A40-d8-swapT_x16-b2: **SKIPPED** (2026-11-28 19:54:35) 
- A40-d8-swapT_x16-b3: **SKIPPED** (2026-11-28 19:54:35) 
- A40-d8-swapT_x16-b4: **SKIPPED** (2026-11-28 19:54:35) 
- A40-d8-swapT_x32-gate: **ERROR** (2026-11-28 19:54:03) rc=3
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-swapT_x32-gate.md
- A40-d8-swapT_x32-b0: **SKIPPED** (2026-11-28 19:54:35) 
- A40-d8-swapT_x32-b1: **SKIPPED** (2026-11-28 19:54:35) 
- A40-d8-swapT_x32-b2: **SKIPPED** (2026-11-28 19:54:35) 
- A40-d8-swapT_x32-b3: **SKIPPED** (2026-11-28 19:54:35) 
- A40-d8-swapT_x32-b4: **SKIPPED** (2026-11-28 19:54:35) 
- A40-d8-swapT_s50-gate: **ERROR** (2026-11-28 19:54:03) rc=3
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-swapT_s50-gate.md
- A40-d8-swapT_s50-b0: **SKIPPED** (2026-11-28 19:54:35) 
- A40-d8-swapT_s50-b1: **SKIPPED** (2026-11-28 19:54:35) 
- A40-d8-swapT_s50-b2: **SKIPPED** (2026-11-28 19:54:35) 
- A40-d8-swapT_s50-b3: **SKIPPED** (2026-11-28 19:54:35) 
- A40-d8-swapT_s50-b4: **SKIPPED** (2026-11-28 19:54:35) 
- A40-d8-swapT-report100: **ERROR** (2026-11-28 20:16:03) rc=1
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-swapT-report100.md
- A40-d7c-rearr-split: **PASS** (2026-11-28 20:50:53) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d7c-rearr-split.md
- A40-d8-swapT-report2: **PASS** (2026-11-28 20:38:46) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-swapT-report2.md
- A40-d8-press_x16-s0: **DONE** (2026-11-28 23:51:59) press_button/on n=35 pressed=35 n1_correct=14 n2_correct=14 confirmed=35 count_correct=6 success=6 prog=0.38; errors=7
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x16-s0.md
- A40-d8-press_x16-s1: **ERROR** (2026-11-29 00:14:48) press_button/on n=41 pressed=41 n1_correct=17 n2_correct=18 confirmed=41 count_correct=8 success=8 prog=0.40; errors=7
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x16-s1.md
- A40-d8-press_x16-s2: **DONE** (2026-11-29 00:15:53) press_button/on n=42 pressed=42 n1_correct=17 n2_correct=19 confirmed=42 count_correct=8 success=8 prog=0.40; errors=7
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x16-s2.md
- A40-d8-press_x16-s3: **DONE** (2026-11-29 00:21:46) press_button/on n=43 pressed=43 n1_correct=17 n2_correct=19 confirmed=43 count_correct=8 success=8 prog=0.39; errors=7
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x16-s3.md
- A40-d8-press_x16-s4: **ERROR** (2026-11-29 00:14:48) press_button/on n=41 pressed=41 n1_correct=17 n2_correct=18 confirmed=41 count_correct=8 success=8 prog=0.40; errors=7
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x16-s4.md
- A40-d8-press_x32-s0: **ERROR** (2026-11-29 00:12:04) press_button/on n=10 pressed=10 n1_correct=5 n2_correct=5 confirmed=10 count_correct=1 success=1 prog=0.36; errors=10
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x32-s0.md
- A40-d8-press_x32-s1: **ERROR** (2026-11-29 00:05:03) press_button/on n=10 pressed=10 n1_correct=5 n2_correct=5 confirmed=10 count_correct=1 success=1 prog=0.36; errors=10
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x32-s1.md
- A40-d8-press_x32-s2: **ERROR** (2026-11-29 00:07:24) press_button/on n=10 pressed=10 n1_correct=5 n2_correct=5 confirmed=10 count_correct=1 success=1 prog=0.36; errors=10
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x32-s2.md
- A40-d8-press_x32-s3: **ERROR** (2026-11-29 00:12:05) press_button/on n=10 pressed=10 n1_correct=5 n2_correct=5 confirmed=10 count_correct=1 success=1 prog=0.36; errors=10
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x32-s3.md
- A40-d8-press_x32-s4: **ERROR** (2026-11-29 00:14:28) press_button/on n=10 pressed=10 n1_correct=5 n2_correct=5 confirmed=10 count_correct=1 success=1 prog=0.36; errors=10
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x32-s4.md
- A40-d8-press_s50-s0: **ERROR** (2026-11-29 00:16:43) 
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_s50-s0.md
- A40-d8-press_s50-s1: **ERROR** (2026-11-29 00:16:43) 
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_s50-s1.md
- A40-d8-press_s50-s2: **ERROR** (2026-11-29 00:16:42) 
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_s50-s2.md
- A40-d8-press_s50-s3: **ERROR** (2026-11-29 00:19:07) 
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_s50-s3.md
- A40-d8-press_s50-s4: **ERROR** (2026-11-29 00:19:06) 
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_s50-s4.md
- A40-d8-press-report: **PASS** (2026-11-29 00:22:05) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press-report.md
- A40-d8-press_x16-gate: **ERROR** (2026-11-29 00:43:58) rc=3
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x16-gate.md
- A40-d8-press_x16-b0: **SKIPPED** (2026-11-29 00:44:28) 
- A40-d8-press_x16-b1: **SKIPPED** (2026-11-29 00:44:28) 
- A40-d8-press_x16-b2: **SKIPPED** (2026-11-29 00:44:28) 
- A40-d8-press_x16-b3: **SKIPPED** (2026-11-29 00:44:28) 
- A40-d8-press_x16-b4: **SKIPPED** (2026-11-29 00:44:28) 
- A40-d8-press_x32-gate: **ERROR** (2026-11-29 00:43:58) rc=3
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_x32-gate.md
- A40-d8-press_x32-b0: **SKIPPED** (2026-11-29 00:44:29) 
- A40-d8-press_x32-b1: **SKIPPED** (2026-11-29 00:44:29) 
- A40-d8-press_x32-b2: **SKIPPED** (2026-11-29 00:44:29) 
- A40-d8-press_x32-b3: **SKIPPED** (2026-11-29 00:44:29) 
- A40-d8-press_x32-b4: **SKIPPED** (2026-11-29 00:44:29) 
- A40-d8-press_s50-gate: **ERROR** (2026-11-29 00:43:58) rc=3
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press_s50-gate.md
- A40-d8-press_s50-b0: **SKIPPED** (2026-11-29 00:44:29) 
- A40-d8-press_s50-b1: **SKIPPED** (2026-11-29 00:44:29) 
- A40-d8-press_s50-b2: **SKIPPED** (2026-11-29 00:44:29) 
- A40-d8-press_s50-b3: **SKIPPED** (2026-11-29 00:44:29) 
- A40-d8-press_s50-b4: **SKIPPED** (2026-11-29 00:44:29) 
- A40-d8-press-report100: **PASS** (2026-11-29 00:44:35) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-press-report100.md
- A40-d8r-press_x16-s1: **DONE** (2026-11-29 01:39:14) press_button/on n=46 pressed=46 n1_correct=18 n2_correct=19 confirmed=46 count_correct=8 success=8 prog=0.38; errors=4
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8r-press_x16-s1.md
- A40-d8-rearr18_x16-s0: **ERROR** (2026-11-29 00:21:30) 
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-rearr18_x16-s0.md
- A40-d8-rearr18_x16-s1: **ERROR** (2026-11-29 00:21:29) 
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-rearr18_x16-s1.md
- A40-d8-rearr18_x16-s2: **ERROR** (2026-11-29 00:21:28) 
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-rearr18_x16-s2.md
- A40-d8-rearr18_x16-s3: **ERROR** (2026-11-29 00:22:03) 
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-rearr18_x16-s3.md
- A40-d8-rearr18_x16-s4: **ERROR** (2026-11-29 00:23:50) 
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-rearr18_x16-s4.md
- A40-d8-rearr18-report: **PASS** (2026-11-29 00:24:28) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-rearr18-report.md
- A40-d8-rearr18_x16-gate: **ERROR** (2026-11-29 00:46:22) rc=3
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-rearr18_x16-gate.md
- A40-d8-rearr18_x16-b0: **SKIPPED** (2026-11-29 00:46:52) 
- A40-d8-rearr18_x16-b1: **SKIPPED** (2026-11-29 00:46:52) 
- A40-d8-rearr18_x16-b2: **SKIPPED** (2026-11-29 00:46:52) 
- A40-d8-rearr18_x16-b3: **SKIPPED** (2026-11-29 00:46:52) 
- A40-d8-rearr18_x16-b4: **SKIPPED** (2026-11-29 00:46:52) 
- A40-d8-rearr18-report100: **PASS** (2026-11-29 00:46:59) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d8-rearr18-report100.md
- A40-d7a-report: **PASS** (2026-11-28 16:52:43) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d7a-report.md
- A40-d9-rearr_pw_e30-off-s0: **ERROR** (2026-11-29 00:26:13) 
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d9-rearr_pw_e30-off-s0.md
- A40-d9-rearr_pw_e30-off-s1: **ERROR** (2026-11-29 00:30:57) 
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d9-rearr_pw_e30-off-s1.md
- A40-d9-rearr_pw_e30-off-s2: **ERROR** (2026-11-29 00:35:03) 
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-d9-rearr_pw_e30-off-s2.md
- A40-fetch-battery_clock-e30: **PASS** (2026-11-28 12:06:19) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-battery_clock-e30.md
- A40-batclk30-smoke: **PASS** (2026-11-28 13:35:45) battery_try/on n=1  prog=0.00
- A40-batclk30-s0: **DONE** (2026-11-28 14:19:38) battery_try/on n=35  prog=0.00
- A40-batclk30-s1: **DONE** (2026-11-28 14:21:16) battery_try/on n=38  prog=0.00
- A40-batclk30-s2: **DONE** (2026-11-28 14:24:23) battery_try/on n=40  prog=0.00
- A40-batclk30-s3: **DONE** (2026-11-28 14:26:26) battery_try/on n=41  prog=0.00
- A40-batclk30-s4: **DONE** (2026-11-28 15:07:31) battery_try/on n=87  prog=0.00
- A40-batclk30-s5: **DONE** (2026-11-28 15:03:29) battery_try/on n=83  prog=0.00
- A40-batclk30-s6: **DONE** (2026-11-28 15:12:13) battery_try/on n=92  prog=0.00
- A40-batclk30-s7: **DONE** (2026-11-28 15:17:22) battery_try/on n=96  prog=0.00
- A40-batclk30-s8: **DONE** (2026-11-28 15:23:46) battery_try/on n=100  prog=0.00
- A40-batclk30-s9: **DONE** (2026-11-28 15:23:37) battery_try/on n=99  prog=0.00
- A40-BATCLK-report: **PASS** (2026-11-28 15:24:08) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-BATCLK-report.md
- A40-fetch-ranking_none-e30: **PASS** (2026-11-28 10:06:13) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-ranking_none-e30.md
- A40-ranknone30-smoke: **PASS** (2026-11-28 10:18:27) blocks_ranking_try/on n=1  prog=0.00
- A40-ranknone30-s0: **DONE** (2026-11-28 13:28:07) blocks_ranking_try/on n=60  prog=0.00
- A40-ranknone30-s1: **DONE** (2026-11-28 13:26:35) blocks_ranking_try/on n=59  prog=0.00
- A40-ranknone30-s2: **DONE** (2026-11-28 13:37:54) blocks_ranking_try/on n=64  prog=0.00
- A40-ranknone30-s3: **DONE** (2026-11-28 13:38:38) blocks_ranking_try/on n=65  prog=0.00
- A40-ranknone30-s4: **DONE** (2026-11-28 13:37:19) blocks_ranking_try/on n=63  prog=0.00
- A40-ranknone30-s5: **DONE** (2026-11-28 14:15:25) blocks_ranking_try/on n=69  prog=0.00
- A40-ranknone30-s6: **DONE** (2026-11-28 14:41:07) blocks_ranking_try/on n=73  prog=0.00
- A40-ranknone30-s7: **DONE** (2026-11-28 17:27:55) blocks_ranking_try/on n=90  prog=0.00
- A40-ranknone30-s8: **DONE** (2026-11-28 18:59:47) blocks_ranking_try/on n=99  prog=0.00
- A40-ranknone30-s9: **DONE** (2026-11-28 19:01:23) blocks_ranking_try/on n=100  prog=0.00
- A40-RANKNONE-report: **PASS** (2026-11-28 19:01:43) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-RANKNONE-report.md
- A40-fetch-obs_cf200-e10: **PASS** (2026-11-28 05:02:16) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-obs_cf200-e10.md
- A40-v21-obs_cf200-e10-s0: **DONE** (2026-11-28 05:49:42) observe_and_pickup/on n=10  prog=0.00
- A40-v21-obs_cf200-e10-s1: **DONE** (2026-11-28 06:15:23) observe_and_pickup/on n=46  prog=0.00
- A40-v21-obs_cf200-e10-s2: **DONE** (2026-11-28 06:20:41) observe_and_pickup/on n=59  prog=0.00
- A40-v21-obs_cf200-e10-s3: **DONE** (2026-11-28 06:19:10) observe_and_pickup/on n=55  prog=0.00
- A40-v21-obs_cf200-e10-s4: **DONE** (2026-11-28 06:27:58) observe_and_pickup/on n=76  prog=0.00
- A40-v21-obs_cf200-e10-s5: **DONE** (2026-11-28 06:30:18) observe_and_pickup/on n=82  prog=0.00
- A40-v21-obs_cf200-e10-s6: **DONE** (2026-11-28 06:33:58) observe_and_pickup/on n=89  prog=0.00
- A40-v21-obs_cf200-e10-s7: **DONE** (2026-11-28 06:35:42) observe_and_pickup/on n=92  prog=0.00
- A40-v21-obs_cf200-e10-s8: **DONE** (2026-11-28 06:42:58) observe_and_pickup/on n=99  prog=0.00
- A40-v21-obs_cf200-e10-s9: **DONE** (2026-11-28 06:44:28) observe_and_pickup/on n=100  prog=0.00
- A40-fetch-obs_cf200-e20: **PASS** (2026-11-28 12:27:10) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-obs_cf200-e20.md
- A40-v21-obs_cf200-e20-s0: **DONE** (2026-11-28 15:35:58) observe_and_pickup/on n=24  prog=0.00
- A40-v21-obs_cf200-e20-s1: **DONE** (2026-11-28 15:43:31) observe_and_pickup/on n=35  prog=0.00
- A40-v21-obs_cf200-e20-s2: **DONE** (2026-11-28 15:49:54) observe_and_pickup/on n=44  prog=0.00
- A40-v21-obs_cf200-e20-s3: **DONE** (2026-11-28 15:49:53) observe_and_pickup/on n=44  prog=0.00
- A40-v21-obs_cf200-e20-s4: **DONE** (2026-11-28 16:00:36) observe_and_pickup/on n=50  prog=0.00
- A40-v21-obs_cf200-e20-s5: **DONE** (2026-11-28 16:26:31) observe_and_pickup/on n=85  prog=0.00; errors=1
- A40-v21-obs_cf200-e20-s6: **DONE** (2026-11-28 16:28:15) observe_and_pickup/on n=87  prog=0.00; errors=1
- A40-v21-obs_cf200-e20-s8: **DONE** (2026-11-28 16:33:15) observe_and_pickup/on n=89  prog=0.00; errors=1
- A40-fs-obs_s800-e5-s7: **DONE** (2026-11-28 01:56:04) observe_and_pickup/on n=89  prog=0.00
- A40-fs-obs_s800-e5-s8: **DONE** (2026-11-28 02:06:11) observe_and_pickup/on n=99  prog=0.00
- A40-fs-obs_s800-e5-s9: **DONE** (2026-11-28 02:07:57) observe_and_pickup/on n=100  prog=0.00
- A40-FS-report-obs_s800-e5: **PASS** (2026-11-28 02:08:24) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-FS-report-obs_s800-e5.md
- A40-fetch-ar2_prop_s18-e30: **PASS** (2026-11-28 16:58:53) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-ar2_prop_s18-e30.md
- A40-fetch-ar2_prop_s18-e10: **PASS** (2026-11-28 17:03:38) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-ar2_prop_s18-e10.md
- A40-fetch-ar2_pw-e10: **PASS** (2026-11-28 15:02:52) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-ar2_pw-e10.md
- A40-c18-cover-freeze1-s1: **DONE** (2026-11-28 03:33:22) cover_blocks/on n=47  prog=0.00
- A40-c18-cover-freeze1-s2: **DONE** (2026-11-28 03:31:14) cover_blocks/on n=46  prog=0.00
- A40-c18-cover-freeze1-s3: **DONE** (2026-11-28 03:34:05) cover_blocks/on n=49  prog=0.00
- A40-c18-cover-freeze1-s4: **DONE** (2026-11-28 03:44:03) cover_blocks/on n=50  prog=0.00
- A40-c18-cover-addmove-s0: **DONE** (2026-11-28 03:12:25) cover_blocks/on n=20  prog=0.00
- A40-c18-cover-addmove-s1: **DONE** (2026-11-28 03:25:19) cover_blocks/on n=26  prog=0.00
- A40-c18-cover-addmove-s2: **DONE** (2026-11-28 03:53:05) cover_blocks/on n=38  prog=0.00
- A40-c18-cover-addmove-s3: **DONE** (2026-11-28 04:20:13) cover_blocks/on n=47  prog=0.00
- A40-c18-cover-addmove-s4: **DONE** (2026-11-28 04:33:41) cover_blocks/on n=50  prog=0.00
- A40-c18-rearrpw-off-s0: **DONE** (2026-11-28 04:22:40) rearrange_blocks/on n=40  prog=0.00
- A40-c18-rearrpw-off-s1: **DONE** (2026-11-28 04:24:40) rearrange_blocks/on n=41  prog=0.00
- A40-c18-rearrpw-off-s2: **DONE** (2026-11-28 04:25:34) rearrange_blocks/on n=43  prog=0.00
- A40-c18-rearrpw-off-s3: **DONE** (2026-11-28 04:36:24) rearrange_blocks/on n=48  prog=0.00
- A40-c18-rearrpw-off-s4: **DONE** (2026-11-28 04:44:29) rearrange_blocks/on n=50  prog=0.00
- A40-c18-rearrpw-freeze1-s0: **DONE** (2026-11-28 05:15:56) rearrange_blocks/on n=28  prog=0.00
- A40-c18-rearrpw-freeze1-s1: **DONE** (2026-11-28 05:17:28) rearrange_blocks/on n=29  prog=0.00
- A40-c18-rearrpw-freeze1-s2: **DONE** (2026-11-28 05:18:42) rearrange_blocks/on n=30  prog=0.00
- A40-c18-rearrpw-freeze1-s3: **DONE** (2026-11-28 07:15:20) rearrange_blocks/on n=48  prog=0.00
- A40-c18-rearrpw-freeze1-s4: **DONE** (2026-11-28 07:21:02) rearrange_blocks/on n=50  prog=0.00
- A40-c18-rearrpw-addmove-s0: **DONE** (2026-11-28 07:06:56) rearrange_blocks/on n=37  prog=0.00
- A40-c18-rearrpw-addmove-s1: **DONE** (2026-11-28 07:12:12) rearrange_blocks/on n=44  prog=0.00
- A40-c18-rearrpw-addmove-s2: **DONE** (2026-11-28 07:11:57) rearrange_blocks/on n=43  prog=0.00
- A40-c18-rearrpw-addmove-s3: **DONE** (2026-11-28 07:19:11) rearrange_blocks/on n=49  prog=0.00
- A40-c18-rearrpw-addmove-s4: **DONE** (2026-11-28 07:20:09) rearrange_blocks/on n=50  prog=0.00
- A40-C18-report: **PASS** (2026-11-28 07:26:13) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-C18-report.md
- A40-stepa-ar_2task_e10-s0: **DONE** (2026-11-28 08:18:20) swap_blocks/on n=60 lifted=50 s1=50 s2=39 s3=34 pressed=11 success=4 prog=0.51
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e10-s0.md
- A40-stepa-ar_2task_e10-s1: **DONE** (2026-11-28 08:23:43) swap_blocks/on n=65 lifted=54 s1=54 s2=43 s3=38 pressed=12 success=4 prog=0.51
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e10-s1.md
- A40-stepa-ar_2task_e10-s2: **DONE** (2026-11-28 08:20:36) swap_blocks/on n=62 lifted=52 s1=52 s2=41 s3=36 pressed=11 success=4 prog=0.51
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e10-s2.md
- A40-stepa-ar_2task_e10-s3: **DONE** (2026-11-28 08:25:31) swap_blocks/on n=67 lifted=56 s1=56 s2=45 s3=40 pressed=12 success=4 prog=0.51
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e10-s3.md
- A40-stepa-ar_2task_e10-s4: **DONE** (2026-11-28 08:29:43) swap_blocks/on n=69 lifted=57 s1=57 s2=46 s3=41 pressed=12 success=4 prog=0.51
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e10-s4.md
- A40-stepa-ar_2task_e10-s5: **DONE** (2026-11-28 08:30:34) swap_blocks/on n=71 lifted=59 s1=59 s2=48 s3=42 pressed=12 success=4 prog=0.51
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e10-s5.md
- A40-stepa-ar_2task_e10-s6: **DONE** (2026-11-28 08:30:00) swap_blocks/on n=70 lifted=58 s1=58 s2=47 s3=42 pressed=12 success=4 prog=0.51
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e10-s6.md
- A40-stepa-ar_2task_e10-s7: **DONE** (2026-11-28 09:32:04) swap_blocks/on n=98 lifted=82 s1=82 s2=69 s3=56 pressed=19 success=6 prog=0.52
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e10-s7.md
- A40-stepa-ar_2task_e10-s8: **DONE** (2026-11-28 09:37:47) swap_blocks/on n=100 lifted=84 s1=84 s2=70 s3=57 pressed=19 success=6 prog=0.52
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e10-s8.md
- A40-stepa-ar_2task_e10-s9: **DONE** (2026-11-28 09:36:40) swap_blocks/on n=99 lifted=83 s1=83 s2=69 s3=56 pressed=19 success=6 prog=0.52
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e10-s9.md
- A40-stepa-ar_2task_e20-s0: **DONE** (2026-11-28 09:43:36) swap_blocks/on n=39 lifted=39 s1=39 s2=35 s3=33 pressed=20 success=13 prog=0.74
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e20-s0.md
- A40-stepa-ar_2task_e20-s1: **DONE** (2026-11-28 09:46:24) swap_blocks/on n=40 lifted=40 s1=40 s2=36 s3=34 pressed=20 success=13 prog=0.74
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e20-s1.md
- A40-stepa-ar_2task_e20-s2: **DONE** (2026-11-28 09:39:36) swap_blocks/on n=37 lifted=37 s1=37 s2=33 s3=31 pressed=19 success=12 prog=0.73
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e20-s2.md
- A40-stepa-ar_2task_e20-s3: **DONE** (2026-11-28 09:40:55) swap_blocks/on n=38 lifted=38 s1=38 s2=34 s3=32 pressed=20 success=13 prog=0.74
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e20-s3.md
- A40-stepa-ar_2task_e20-s4: **DONE** (2026-11-28 10:56:40) swap_blocks/on n=57 lifted=56 s1=56 s2=50 s3=48 pressed=33 success=23 prog=0.75
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e20-s4.md
- A40-stepa-ar_2task_e20-s5: **DONE** (2026-11-28 11:12:10) swap_blocks/on n=60 lifted=59 s1=59 s2=53 s3=51 pressed=34 success=24 prog=0.75
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-stepa-ar_2task_e20-s5.md

## dispatcher log (pool.log, last 40 lines)
```
[queue5] 2026-11-29 00:44:28 A40-d8-press_x16-b0: SKIPPED  
[pool] 2026-11-29 00:44:28 A40-d8-press_x16-b1: skipped (requires PASS of ['A40-d8-press_x16-gate'])
[queue5] 2026-11-29 00:44:28 A40-d8-press_x16-b1: SKIPPED  
[pool] 2026-11-29 00:44:28 A40-d8-press_x16-b2: skipped (requires PASS of ['A40-d8-press_x16-gate'])
[queue5] 2026-11-29 00:44:28 A40-d8-press_x16-b2: SKIPPED  
[pool] 2026-11-29 00:44:28 A40-d8-press_x16-b3: skipped (requires PASS of ['A40-d8-press_x16-gate'])
[queue5] 2026-11-29 00:44:28 A40-d8-press_x16-b3: SKIPPED  
[pool] 2026-11-29 00:44:28 A40-d8-press_x16-b4: skipped (requires PASS of ['A40-d8-press_x16-gate'])
[queue5] 2026-11-29 00:44:29 A40-d8-press_x16-b4: SKIPPED  
[pool] 2026-11-29 00:44:29 A40-d8-press_x32-b0: skipped (requires PASS of ['A40-d8-press_x32-gate'])
[queue5] 2026-11-29 00:44:29 A40-d8-press_x32-b0: SKIPPED  
[pool] 2026-11-29 00:44:29 A40-d8-press_x32-b1: skipped (requires PASS of ['A40-d8-press_x32-gate'])
[queue5] 2026-11-29 00:44:29 A40-d8-press_x32-b1: SKIPPED  
[pool] 2026-11-29 00:44:29 A40-d8-press_x32-b2: skipped (requires PASS of ['A40-d8-press_x32-gate'])
[queue5] 2026-11-29 00:44:29 A40-d8-press_x32-b2: SKIPPED  
[pool] 2026-11-29 00:44:29 A40-d8-press_x32-b3: skipped (requires PASS of ['A40-d8-press_x32-gate'])
[queue5] 2026-11-29 00:44:29 A40-d8-press_x32-b3: SKIPPED  
[pool] 2026-11-29 00:44:29 A40-d8-press_x32-b4: skipped (requires PASS of ['A40-d8-press_x32-gate'])
[queue5] 2026-11-29 00:44:29 A40-d8-press_x32-b4: SKIPPED  
[pool] 2026-11-29 00:44:29 A40-d8-press_s50-b0: skipped (requires PASS of ['A40-d8-press_s50-gate'])
[queue5] 2026-11-29 00:44:29 A40-d8-press_s50-b0: SKIPPED  
[pool] 2026-11-29 00:44:29 A40-d8-press_s50-b1: skipped (requires PASS of ['A40-d8-press_s50-gate'])
[queue5] 2026-11-29 00:44:29 A40-d8-press_s50-b1: SKIPPED  
[pool] 2026-11-29 00:44:29 A40-d8-press_s50-b2: skipped (requires PASS of ['A40-d8-press_s50-gate'])
[queue5] 2026-11-29 00:44:29 A40-d8-press_s50-b2: SKIPPED  
[pool] 2026-11-29 00:44:29 A40-d8-press_s50-b3: skipped (requires PASS of ['A40-d8-press_s50-gate'])
[queue5] 2026-11-29 00:44:29 A40-d8-press_s50-b3: SKIPPED  
[pool] 2026-11-29 00:44:29 A40-d8-press_s50-b4: skipped (requires PASS of ['A40-d8-press_s50-gate'])
[queue5] 2026-11-29 00:44:29 A40-d8-press_s50-b4: SKIPPED  
[pool] 2026-11-29 00:46:52 A40-d8-rearr18_x16-b0: skipped (requires PASS of ['A40-d8-rearr18_x16-gate'])
[queue5] 2026-11-29 00:46:52 A40-d8-rearr18_x16-b0: SKIPPED  
[pool] 2026-11-29 00:46:52 A40-d8-rearr18_x16-b1: skipped (requires PASS of ['A40-d8-rearr18_x16-gate'])
[queue5] 2026-11-29 00:46:52 A40-d8-rearr18_x16-b1: SKIPPED  
[pool] 2026-11-29 00:46:52 A40-d8-rearr18_x16-b2: skipped (requires PASS of ['A40-d8-rearr18_x16-gate'])
[queue5] 2026-11-29 00:46:52 A40-d8-rearr18_x16-b2: SKIPPED  
[pool] 2026-11-29 00:46:52 A40-d8-rearr18_x16-b3: skipped (requires PASS of ['A40-d8-rearr18_x16-gate'])
[queue5] 2026-11-29 00:46:52 A40-d8-rearr18_x16-b3: SKIPPED  
[pool] 2026-11-29 00:46:52 A40-d8-rearr18_x16-b4: skipped (requires PASS of ['A40-d8-rearr18_x16-gate'])
[queue5] 2026-11-29 00:46:52 A40-d8-rearr18_x16-b4: SKIPPED  
[pool] 2026-11-29 01:07:44 A40-d8r-press_x16-s1: started on GPU 0 (attempt 1, exec pid 3962036)
```
## lane cpu log (last 10 lines)
```
```

disk free: 6684G

# pool5 report 2026-11-21 20:44:55 (GPU18)

```
== pool5 2026-11-21 20:44:55 on GPU18: dispatcher pid 25178 ALIVE (last beat 2026-11-21 20:44:30); allowed GPUs [0, 1, 2, 3, 4, 5, 6, 7]; lanes ['a40', 'a40cpu']; nothing new starts after 01-05 23:59
   GPU 0:  15465/46068 MiB,   1% busy  -> A40-E16-rearrange-clock-s1
   GPU 1:  16593/46068 MiB,   2% busy  -> A40-E16-rearrange-clock-s0
   GPU 2:  32725/46068 MiB,   0% busy  -> BUSY, not a queue task (another user, or ours started outside the queue)
   GPU 3:  19255/46068 MiB,  37% busy  -> A40-E22b-ledger-b4-swap-s4
   GPU 4:  15009/46068 MiB,   0% busy  -> A40-E16-rearrange-clock-s2
   GPU 5:  19161/46068 MiB,  38% busy  -> A40-E22b-ledger-b4-swap-s2
   GPU 6:  19161/46068 MiB,  36% busy  -> A40-E22b-ledger-b4-swap-s3
   GPU 7:  19159/46068 MiB,  60% busy  -> A40-E16-rearrange-clock-s3
   queue5 lane processes: 
   tasks: 806 done, 16 running, 581 pending, 58 on hold

RUNNING
  A40-fetch-rearrange_arprop-e30 shell       GPU None  attempt 1  since 11-19 19:18  [pool]    last write 1 min ago
  A40-fetch-swapT_arprop-e30 shell       GPU None  attempt 1  since 11-19 19:18  [pool]    last write 1 min ago
  A40-fetch-ar2_arev-e30 shell       GPU None  attempt 1  since 11-19 19:18  [pool]    last write 1 min ago
  A40-fetch-ar2_tw-e30 shell       GPU None  attempt 1  since 11-19 19:18  [pool]    last write 1 min ago
  A40-fetch-press_clock-e10 shell       GPU None  attempt 1  since 11-19 19:18  [pool]    last write 1 min ago
  A40-fetch-press_clock-e20 shell       GPU None  attempt 1  since 11-19 19:18  [pool]    last write 1 min ago
  A40-fetch-press_clock-e30 shell       GPU None  attempt 1  since 11-19 19:18  [pool]    last write 1 min ago
  A40-E22b-ledger-b4-swap-s2 closed_loop GPU 5  attempt 1  since 11-21 19:47  [pool]  7/10 episodes  ETA 11-21 21:06 (0.4 h)    last write 0 min ago
  A40-E22b-ledger-b4-swap-s3 closed_loop GPU 6  attempt 1  since 11-21 19:47  [pool]  8/10 episodes  ETA 11-21 20:58 (0.2 h)    last write 0 min ago
  A40-E22b-ledger-b4-swap-s4 closed_loop GPU 3  attempt 1  since 11-21 19:48  [pool]  7/10 episodes  ETA 11-21 21:05 (0.3 h)    last write 0 min ago
  A40-E22a-fetch-all shell       GPU None  attempt 1  since 11-20 17:18  [pool]    last write 3 min ago
  A40-E16-rearrange-clock-s0 closed_loop GPU 1  attempt 1  since 11-21 20:12  [pool]  8/10 episodes  ETA 11-21 20:52 (0.1 h)    last write 0 min ago
  A40-E16-rearrange-clock-s1 closed_loop GPU 0  attempt 1  since 11-21 20:18  [pool]  6/10 episodes  ETA 11-21 21:00 (0.3 h)    last write 0 min ago
  A40-E16-rearrange-clock-s2 closed_loop GPU 4  attempt 1  since 11-21 20:28  [pool]  4/10 episodes  ETA 11-21 21:07 (0.4 h)    last write 0 min ago
  A40-E16-rearrange-clock-s3 closed_loop GPU 7  attempt 1  since 11-21 20:40  [pool]  0/10 episodes  ETA ?    last write 0 min ago
  A40-fetch-battery_count-e30 shell       GPU None  attempt 1  since 11-19 19:18  [pool]    last write 1 min ago

QUEUE (pool lanes, in start order)
  A40-rearrLED30-smoke closed_loop after A40-fetch-rearrange_arprop-e30
  A40-E6-rearrLED30-s0 closed_loop after A40-rearrLED30-smoke
  A40-E6-rearrLED30-s1 closed_loop after A40-rearrLED30-smoke
  A40-E6-rearrLED30-s2 closed_loop after A40-rearrLED30-smoke
  A40-E6-rearrLED30-s3 closed_loop after A40-rearrLED30-smoke
  A40-E6-rearrLED30-s4 closed_loop after A40-rearrLED30-smoke
  A40-E6-rearrLED30-s5 closed_loop after A40-rearrLED30-smoke
  A40-E6-rearrLED30-s6 closed_loop after A40-rearrLED30-smoke
  A40-E6-rearrLED30-s7 closed_loop after A40-rearrLED30-smoke
  A40-E6-rearrLED30-s8 closed_loop after A40-rearrLED30-smoke
  A40-E6-rearrLED30-s9 closed_loop after A40-rearrLED30-smoke
  A40-swapTLED30-smoke closed_loop after A40-fetch-swapT_arprop-e30
  A40-E6-swapTLED30-s0 closed_loop after A40-swapTLED30-smoke
  A40-E6-swapTLED30-s1 closed_loop after A40-swapTLED30-smoke
  A40-E6-swapTLED30-s2 closed_loop after A40-swapTLED30-smoke
  A40-E6-swapTLED30-s3 closed_loop after A40-swapTLED30-smoke
  A40-E6-swapTLED30-s4 closed_loop after A40-swapTLED30-smoke
  A40-E6-swapTLED30-s5 closed_loop after A40-swapTLED30-smoke
  A40-E6-swapTLED30-s6 closed_loop after A40-swapTLED30-smoke
  A40-E6-swapTLED30-s7 closed_loop after A40-swapTLED30-smoke
  A40-E6-swapTLED30-s8 closed_loop after A40-swapTLED30-smoke
  A40-E6-swapTLED30-s9 closed_loop after A40-swapTLED30-smoke
  A40-E6-ledger-report shell       after A40-E6-rearrLED30-s0, A40-E6-rearrLED30-s1, A40-E6-rearrLED30-s2, A40-E6-rearrLED30-s3, A40-E6-rearrLED30-s4, A40-E6-rearrLED30-s5, A40-E6-rearrLED30-s6, A40-E6-rearrLED30-s7, A40-E6-rearrLED30-s8, A40-E6-rearrLED30-s9, A40-E6-swapTLED30-s0, A40-E6-swapTLED30-s1, A40-E6-swapTLED30-s2, A40-E6-swapTLED30-s3, A40-E6-swapTLED30-s4, A40-E6-swapTLED30-s5, A40-E6-swapTLED30-s6, A40-E6-swapTLED30-s7, A40-E6-swapTLED30-s8, A40-E6-swapTLED30-s9
  A40-ar2_arev-smoke closed_loop after A40-fetch-ar2_arev-e30
  A40-ar2_arev-swap-s0 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-swap-s1 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-swap-s2 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-swap-s3 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-swap-s4 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-swap-s5 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-swap-s6 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-swap-s7 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-swap-s8 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-swap-s9 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-put-s0 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-put-s1 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-put-s2 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-put-s3 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-put-s4 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-put-s5 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-put-s6 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-put-s7 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-put-s8 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-put-s9 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-p64-vis-s0 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-p64-vis-s1 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-p64-vis-s2 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-p64-vis-s3 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-p64-vis-s4 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-p64-hid-s0 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-p64-hid-s1 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-p64-hid-s2 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-p64-hid-s3 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-p64-hid-s4 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-p256-vis-s0 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-p256-vis-s1 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-p256-vis-s2 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-p256-vis-s3 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-p256-vis-s4 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-p256-hid-s0 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-p256-hid-s1 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-p256-hid-s2 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-p256-hid-s3 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-p256-hid-s4 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-evoff-s0 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-evoff-s1 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-evoff-s2 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-evoff-s3 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-evoff-s4 closed_loop after A40-ar2_arev-smoke
  A40-ar2_arev-verdict shell       after A40-ar2_arev-swap-s0, A40-ar2_arev-swap-s1, A40-ar2_arev-swap-s2, A40-ar2_arev-swap-s3, A40-ar2_arev-swap-s4, A40-ar2_arev-swap-s5, A40-ar2_arev-swap-s6, A40-ar2_arev-swap-s7, A40-ar2_arev-swap-s8, A40-ar2_arev-swap-s9, A40-ar2_arev-put-s0, A40-ar2_arev-put-s1, A40-ar2_arev-put-s2, A40-ar2_arev-put-s3, A40-ar2_arev-put-s4, A40-ar2_arev-put-s5, A40-ar2_arev-put-s6, A40-ar2_arev-put-s7, A40-ar2_arev-put-s8, A40-ar2_arev-put-s9, A40-ar2_arev-p64-vis-s0, A40-ar2_arev-p64-vis-s1, A40-ar2_arev-p64-vis-s2, A40-ar2_arev-p64-vis-s3, A40-ar2_arev-p64-vis-s4, A40-ar2_arev-p64-hid-s0, A40-ar2_arev-p64-hid-s1, A40-ar2_arev-p64-hid-s2, A40-ar2_arev-p64-hid-s3, A40-ar2_arev-p64-hid-s4, A40-ar2_arev-p256-vis-s0, A40-ar2_arev-p256-vis-s1, A40-ar2_arev-p256-vis-s2, A40-ar2_arev-p256-vis-s3, A40-ar2_arev-p256-vis-s4, A40-ar2_arev-p256-hid-s0, A40-ar2_arev-p256-hid-s1, A40-ar2_arev-p256-hid-s2, A40-ar2_arev-p256-hid-s3, A40-ar2_arev-p256-hid-s4, A40-ar2_arev-evoff-s0, A40-ar2_arev-evoff-s1, A40-ar2_arev-evoff-s2, A40-ar2_arev-evoff-s3, A40-ar2_arev-evoff-s4
  A40-ar2_tw-smoke   closed_loop after A40-fetch-ar2_tw-e30
  A40-ar2_tw-swap-s0 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-swap-s1 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-swap-s2 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-swap-s3 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-swap-s4 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-swap-s5 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-swap-s6 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-swap-s7 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-swap-s8 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-swap-s9 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-put-s0  closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-put-s1  closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-put-s2  closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-put-s3  closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-put-s4  closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-put-s5  closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-put-s6  closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-put-s7  closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-put-s8  closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-put-s9  closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-p64-vis-s0 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-p64-vis-s1 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-p64-vis-s2 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-p64-vis-s3 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-p64-vis-s4 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-p64-hid-s0 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-p64-hid-s1 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-p64-hid-s2 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-p64-hid-s3 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-p64-hid-s4 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-p256-vis-s0 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-p256-vis-s1 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-p256-vis-s2 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-p256-vis-s3 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-p256-vis-s4 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-p256-hid-s0 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-p256-hid-s1 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-p256-hid-s2 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-p256-hid-s3 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-p256-hid-s4 closed_loop after A40-ar2_tw-smoke
  A40-ar2_tw-verdict shell       after A40-ar2_tw-swap-s0, A40-ar2_tw-swap-s1, A40-ar2_tw-swap-s2, A40-ar2_tw-swap-s3, A40-ar2_tw-swap-s4, A40-ar2_tw-swap-s5, A40-ar2_tw-swap-s6, A40-ar2_tw-swap-s7, A40-ar2_tw-swap-s8, A40-ar2_tw-swap-s9, A40-ar2_tw-put-s0, A40-ar2_tw-put-s1, A40-ar2_tw-put-s2, A40-ar2_tw-put-s3, A40-ar2_tw-put-s4, A40-ar2_tw-put-s5, A40-ar2_tw-put-s6, A40-ar2_tw-put-s7, A40-ar2_tw-put-s8, A40-ar2_tw-put-s9, A40-ar2_tw-p64-vis-s0, A40-ar2_tw-p64-vis-s1, A40-ar2_tw-p64-vis-s2, A40-ar2_tw-p64-vis-s3, A40-ar2_tw-p64-vis-s4, A40-ar2_tw-p64-hid-s0, A40-ar2_tw-p64-hid-s1, A40-ar2_tw-p64-hid-s2, A40-ar2_tw-p64-hid-s3, A40-ar2_tw-p64-hid-s4, A40-ar2_tw-p256-vis-s0, A40-ar2_tw-p256-vis-s1, A40-ar2_tw-p256-vis-s2, A40-ar2_tw-p256-vis-s3, A40-ar2_tw-p256-vis-s4, A40-ar2_tw-p256-hid-s0, A40-ar2_tw-p256-hid-s1, A40-ar2_tw-p256-hid-s2, A40-ar2_tw-p256-hid-s3, A40-ar2_tw-p256-hid-s4
  A40-E24-press_clock-e10-s0 closed_loop after A40-fetch-press_clock-e10
  A40-E24-press_clock-e10-s1 closed_loop after A40-fetch-press_clock-e10
  A40-E24-press_clock-e10-s2 closed_loop after A40-fetch-press_clock-e10
  A40-E24-press_clock-e10-s3 closed_loop after A40-fetch-press_clock-e10
  A40-E24-press_clock-e10-s4 closed_loop after A40-fetch-press_clock-e10
  A40-E24-press_clock-e10-s5 closed_loop after A40-fetch-press_clock-e10
  A40-E24-press_clock-e10-s6 closed_loop after A40-fetch-press_clock-e10
  A40-E24-press_clock-e10-s7 closed_loop after A40-fetch-press_clock-e10
  A40-E24-press_clock-e10-s8 closed_loop after A40-fetch-press_clock-e10
  A40-E24-press_clock-e10-s9 closed_loop after A40-fetch-press_clock-e10
  A40-E24-press_clock-e20-s0 closed_loop after A40-fetch-press_clock-e20
  A40-E24-press_clock-e20-s1 closed_loop after A40-fetch-press_clock-e20
  A40-E24-press_clock-e20-s2 closed_loop after A40-fetch-press_clock-e20
  A40-E24-press_clock-e20-s3 closed_loop after A40-fetch-press_clock-e20
  A40-E24-press_clock-e20-s4 closed_loop after A40-fetch-press_clock-e20
  A40-E24-press_clock-e20-s5 closed_loop after A40-fetch-press_clock-e20
  A40-E24-press_clock-e20-s6 closed_loop after A40-fetch-press_clock-e20
  A40-E24-press_clock-e20-s7 closed_loop after A40-fetch-press_clock-e20
  A40-E24-press_clock-e20-s8 closed_loop after A40-fetch-press_clock-e20
  A40-E24-press_clock-e20-s9 closed_loop after A40-fetch-press_clock-e20
  A40-E24-press_clock-e30-s0 closed_loop after A40-fetch-press_clock-e30
  A40-E24-press_clock-e30-s1 closed_loop after A40-fetch-press_clock-e30
  A40-E24-press_clock-e30-s2 closed_loop after A40-fetch-press_clock-e30
  A40-E24-press_clock-e30-s3 closed_loop after A40-fetch-press_clock-e30
  A40-E24-press_clock-e30-s4 closed_loop after A40-fetch-press_clock-e30
  A40-E24-press_clock-e30-s5 closed_loop after A40-fetch-press_clock-e30
  A40-E24-press_clock-e30-s6 closed_loop after A40-fetch-press_clock-e30
  A40-E24-press_clock-e30-s7 closed_loop after A40-fetch-press_clock-e30
  A40-E24-press_clock-e30-s8 closed_loop after A40-fetch-press_clock-e30
  A40-E24-press_clock-e30-s9 closed_loop after A40-fetch-press_clock-e30
  A40-E24-select     shell       after A40-E24-press_clock-e10-s0, A40-E24-press_clock-e10-s1, A40-E24-press_clock-e10-s2, A40-E24-press_clock-e10-s3, A40-E24-press_clock-e10-s4, A40-E24-press_clock-e10-s5, A40-E24-press_clock-e10-s6, A40-E24-press_clock-e10-s7, A40-E24-press_clock-e10-s8, A40-E24-press_clock-e10-s9, A40-E24-press_clock-e20-s0, A40-E24-press_clock-e20-s1, A40-E24-press_clock-e20-s2, A40-E24-press_clock-e20-s3, A40-E24-press_clock-e20-s4, A40-E24-press_clock-e20-s5, A40-E24-press_clock-e20-s6, A40-E24-press_clock-e20-s7, A40-E24-press_clock-e20-s8, A40-E24-press_clock-e20-s9, A40-E24-press_clock-e30-s0, A40-E24-press_clock-e30-s1, A40-E24-press_clock-e30-s2, A40-E24-press_clock-e30-s3, A40-E24-press_clock-e30-s4, A40-E24-press_clock-e30-s5, A40-E24-press_clock-e30-s6, A40-E24-press_clock-e30-s7, A40-E24-press_clock-e30-s8, A40-E24-press_clock-e30-s9
  A40-E24-press_clock_sel-p64-vis-s0 closed_loop after A40-E24-select
  A40-E24-press_clock_sel-p64-vis-s1 closed_loop after A40-E24-select
  A40-E24-press_clock_sel-p64-vis-s2 closed_loop after A40-E24-select
  A40-E24-press_clock_sel-p64-vis-s3 closed_loop after A40-E24-select
  A40-E24-press_clock_sel-p64-vis-s4 closed_loop after A40-E24-select
  A40-E24-press_clock_sel-p64-hid-s0 closed_loop after A40-E24-select
  A40-E24-press_clock_sel-p64-hid-s1 closed_loop after A40-E24-select
  A40-E24-press_clock_sel-p64-hid-s2 closed_loop after A40-E24-select
  A40-E24-press_clock_sel-p64-hid-s3 closed_loop after A40-E24-select
  A40-E24-press_clock_sel-p64-hid-s4 closed_loop after A40-E24-select
  A40-E24-press_count_sel-p64-vis-s0 closed_loop after A40-E24-select
  A40-E24-press_count_sel-p64-vis-s1 closed_loop after A40-E24-select
  A40-E24-press_count_sel-p64-vis-s2 closed_loop after A40-E24-select
  A40-E24-press_count_sel-p64-vis-s3 closed_loop after A40-E24-select
  A40-E24-press_count_sel-p64-vis-s4 closed_loop after A40-E24-select
  A40-E24-press_count_sel-p64-hid-s0 closed_loop after A40-E24-select
  A40-E24-press_count_sel-p64-hid-s1 closed_loop after A40-E24-select
  A40-E24-press_count_sel-p64-hid-s2 closed_loop after A40-E24-select
  A40-E24-press_count_sel-p64-hid-s3 closed_loop after A40-E24-select
  A40-E24-press_count_sel-p64-hid-s4 closed_loop after A40-E24-select
  A40-E24-stress-verdict shell       after A40-E24-press_clock_sel-p64-vis-s0, A40-E24-press_clock_sel-p64-vis-s1, A40-E24-press_clock_sel-p64-vis-s2, A40-E24-press_clock_sel-p64-vis-s3, A40-E24-press_clock_sel-p64-vis-s4, A40-E24-press_clock_sel-p64-hid-s0, A40-E24-press_clock_sel-p64-hid-s1, A40-E24-press_clock_sel-p64-hid-s2, A40-E24-press_clock_sel-p64-hid-s3, A40-E24-press_clock_sel-p64-hid-s4, A40-E24-press_count_sel-p64-vis-s0, A40-E24-press_count_sel-p64-vis-s1, A40-E24-press_count_sel-p64-vis-s2, A40-E24-press_count_sel-p64-vis-s3, A40-E24-press_count_sel-p64-vis-s4, A40-E24-press_count_sel-p64-hid-s0, A40-E24-press_count_sel-p64-hid-s1, A40-E24-press_count_sel-p64-hid-s2, A40-E24-press_count_sel-p64-hid-s3, A40-E24-press_count_sel-p64-hid-s4
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
  A40-E22-clock-p1024-vis-swap-s0 closed_loop on hold
  A40-E22-clock-p1024-vis-swap-s1 closed_loop on hold
  A40-E22-clock-p1024-vis-swap-s2 closed_loop on hold
  A40-E22-clock-p1024-vis-swap-s3 closed_loop on hold
  A40-E22-clock-p1024-vis-swap-s4 closed_loop on hold
  A40-E22-clock-p1024-hid-swap-s0 closed_loop on hold
  A40-E22-clock-p1024-hid-swap-s1 closed_loop on hold
  A40-E22-clock-p1024-hid-swap-s2 closed_loop on hold
  A40-E22-clock-p1024-hid-swap-s3 closed_loop on hold
  A40-E22-clock-p1024-hid-swap-s4 closed_loop on hold
  A40-E22-ledger-p1024-vis-swap-s0 closed_loop on hold
  A40-E22-ledger-p1024-vis-swap-s1 closed_loop on hold
  A40-E22-ledger-p1024-vis-swap-s2 closed_loop on hold
  A40-E22-ledger-p1024-vis-swap-s3 closed_loop on hold
  A40-E22-ledger-p1024-vis-swap-s4 closed_loop on hold
  A40-E22-ledger-p1024-hid-swap-s0 closed_loop on hold
  A40-E22-ledger-p1024-hid-swap-s1 closed_loop on hold
  A40-E22-ledger-p1024-hid-swap-s2 closed_loop on hold
  A40-E22-ledger-p1024-hid-swap-s3 closed_loop on hold
  A40-E22-ledger-p1024-hid-swap-s4 closed_loop on hold
  A40-E22a-verdict   shell       after A40-E22a-fetch-all
  A40-E22b-verdict   shell       after A40-E22b-ledger-b4-swap-s2, A40-E22b-ledger-b4-swap-s3, A40-E22b-ledger-b4-swap-s4
  A40-E16-rearrange-clock-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-s5 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-s6 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-s7 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-s8 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-s9 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-p64-vis-s0 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-p64-vis-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-p64-vis-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-p64-vis-s3 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-p64-vis-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-p64-hid-s0 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-p64-hid-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-p64-hid-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-p64-hid-s3 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-p64-hid-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-p256-vis-s0 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-p256-vis-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-p256-vis-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-p256-vis-s3 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-p256-vis-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-p256-hid-s0 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-p256-hid-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-p256-hid-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-p256-hid-s3 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange-clock-p256-hid-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-swapT_clock-smoke closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-swapT-clock-s0 closed_loop after A40-swapT_clock-smoke
  A40-E16-swapT-clock-s1 closed_loop after A40-swapT_clock-smoke
  A40-E16-swapT-clock-s2 closed_loop after A40-swapT_clock-smoke
  A40-E16-swapT-clock-s3 closed_loop after A40-swapT_clock-smoke
  A40-E16-swapT-clock-s4 closed_loop after A40-swapT_clock-smoke
  A40-E16-swapT-clock-s5 closed_loop after A40-swapT_clock-smoke
  A40-E16-swapT-clock-s6 closed_loop after A40-swapT_clock-smoke
  A40-E16-swapT-clock-s7 closed_loop after A40-swapT_clock-smoke
  A40-E16-swapT-clock-s8 closed_loop after A40-swapT_clock-smoke
  A40-E16-swapT-clock-s9 closed_loop after A40-swapT_clock-smoke
  A40-E16-swapT-clock-p64-vis-s0 closed_loop after A40-swapT_clock-smoke
  A40-E16-swapT-clock-p64-vis-s1 closed_loop after A40-swapT_clock-smoke
  A40-E16-swapT-clock-p64-vis-s2 closed_loop after A40-swapT_clock-smoke
  A40-E16-swapT-clock-p64-vis-s3 closed_loop after A40-swapT_clock-smoke
  A40-E16-swapT-clock-p64-vis-s4 closed_loop after A40-swapT_clock-smoke
  A40-E16-swapT-clock-p64-hid-s0 closed_loop after A40-swapT_clock-smoke
  A40-E16-swapT-clock-p64-hid-s1 closed_loop after A40-swapT_clock-smoke
  A40-E16-swapT-clock-p64-hid-s2 closed_loop after A40-swapT_clock-smoke
  A40-E16-swapT-clock-p64-hid-s3 closed_loop after A40-swapT_clock-smoke
  A40-E16-swapT-clock-p64-hid-s4 closed_loop after A40-swapT_clock-smoke
  A40-E16-rearrange_ar-p64-vis-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange_ar-p64-vis-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange_ar-p64-vis-s3 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange_ar-p64-vis-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange_ar-p64-hid-s0 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange_ar-p64-hid-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange_ar-p64-hid-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange_ar-p64-hid-s3 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange_ar-p64-hid-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E16-rearrange_arprop-p64-vis-s0 closed_loop after A40-rearrLED30-smoke
  A40-E16-rearrange_arprop-p64-vis-s1 closed_loop after A40-rearrLED30-smoke
  A40-E16-rearrange_arprop-p64-vis-s2 closed_loop after A40-rearrLED30-smoke
  A40-E16-rearrange_arprop-p64-vis-s3 closed_loop after A40-rearrLED30-smoke
  A40-E16-rearrange_arprop-p64-vis-s4 closed_loop after A40-rearrLED30-smoke
  A40-E16-rearrange_arprop-p64-hid-s0 closed_loop after A40-rearrLED30-smoke
  A40-E16-rearrange_arprop-p64-hid-s1 closed_loop after A40-rearrLED30-smoke
  A40-E16-rearrange_arprop-p64-hid-s2 closed_loop after A40-rearrLED30-smoke
  A40-E16-rearrange_arprop-p64-hid-s3 closed_loop after A40-rearrLED30-smoke
  A40-E16-rearrange_arprop-p64-hid-s4 closed_loop after A40-rearrLED30-smoke
  A40-E16-verdict-rearrange_blocks shell       after A40-E16-rearrange-clock-s0, A40-E16-rearrange-clock-s1, A40-E16-rearrange-clock-s2, A40-E16-rearrange-clock-s3, A40-E16-rearrange-clock-s4, A40-E16-rearrange-clock-s5, A40-E16-rearrange-clock-s6, A40-E16-rearrange-clock-s7, A40-E16-rearrange-clock-s8, A40-E16-rearrange-clock-s9, A40-E16-rearrange-clock-p64-vis-s0, A40-E16-rearrange-clock-p64-vis-s1, A40-E16-rearrange-clock-p64-vis-s2, A40-E16-rearrange-clock-p64-vis-s3, A40-E16-rearrange-clock-p64-vis-s4, A40-E16-rearrange-clock-p64-hid-s0, A40-E16-rearrange-clock-p64-hid-s1, A40-E16-rearrange-clock-p64-hid-s2, A40-E16-rearrange-clock-p64-hid-s3, A40-E16-rearrange-clock-p64-hid-s4, A40-E16-rearrange-clock-p256-vis-s0, A40-E16-rearrange-clock-p256-vis-s1, A40-E16-rearrange-clock-p256-vis-s2, A40-E16-rearrange-clock-p256-vis-s3, A40-E16-rearrange-clock-p256-vis-s4, A40-E16-rearrange-clock-p256-hid-s0, A40-E16-rearrange-clock-p256-hid-s1, A40-E16-rearrange-clock-p256-hid-s2, A40-E16-rearrange-clock-p256-hid-s3, A40-E16-rearrange-clock-p256-hid-s4, A40-E16-rearrange_ar-p64-vis-s1, A40-E16-rearrange_ar-p64-vis-s2, A40-E16-rearrange_ar-p64-vis-s3, A40-E16-rearrange_ar-p64-vis-s4, A40-E16-rearrange_ar-p64-hid-s0, A40-E16-rearrange_ar-p64-hid-s1, A40-E16-rearrange_ar-p64-hid-s2, A40-E16-rearrange_ar-p64-hid-s3, A40-E16-rearrange_ar-p64-hid-s4, A40-E16-rearrange_arprop-p64-vis-s0, A40-E16-rearrange_arprop-p64-vis-s1, A40-E16-rearrange_arprop-p64-vis-s2, A40-E16-rearrange_arprop-p64-vis-s3, A40-E16-rearrange_arprop-p64-vis-s4, A40-E16-rearrange_arprop-p64-hid-s0, A40-E16-rearrange_arprop-p64-hid-s1, A40-E16-rearrange_arprop-p64-hid-s2, A40-E16-rearrange_arprop-p64-hid-s3, A40-E16-rearrange_arprop-p64-hid-s4
  A40-E16-verdict-swap_T shell       after A40-E16-swapT-clock-s0, A40-E16-swapT-clock-s1, A40-E16-swapT-clock-s2, A40-E16-swapT-clock-s3, A40-E16-swapT-clock-s4, A40-E16-swapT-clock-s5, A40-E16-swapT-clock-s6, A40-E16-swapT-clock-s7, A40-E16-swapT-clock-s8, A40-E16-swapT-clock-s9, A40-E16-swapT-clock-p64-vis-s0, A40-E16-swapT-clock-p64-vis-s1, A40-E16-swapT-clock-p64-vis-s2, A40-E16-swapT-clock-p64-vis-s3, A40-E16-swapT-clock-p64-vis-s4, A40-E16-swapT-clock-p64-hid-s0, A40-E16-swapT-clock-p64-hid-s1, A40-E16-swapT-clock-p64-hid-s2, A40-E16-swapT-clock-p64-hid-s3, A40-E16-swapT-clock-p64-hid-s4
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
  A40-E23-clock-e10-swap-s0 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E23-clock-e10-swap-s1 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E23-clock-e10-swap-s2 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E23-clock-e10-swap-s3 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E23-clock-e10-swap-s4 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E23-clock-e10-swap-s5 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E23-clock-e10-swap-s6 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E23-clock-e10-swap-s7 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E23-clock-e10-swap-s8 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E23-clock-e10-swap-s9 closed_loop no empty allowed GPU (allowed [0, 1, 2, 3, 4, 5, 6, 7])
  A40-E23-verdict    shell       after A40-E23-clock-e10-swap-s0, A40-E23-clock-e10-swap-s1, A40-E23-clock-e10-swap-s2, A40-E23-clock-e10-swap-s3, A40-E23-clock-e10-swap-s4, A40-E23-clock-e10-swap-s5, A40-E23-clock-e10-swap-s6, A40-E23-clock-e10-swap-s7, A40-E23-clock-e10-swap-s8, A40-E23-clock-e10-swap-s9

FAILURES SEEN (latest per task)
  T2                 attempt 2: rc=1: non-zero exit  -> now done PASS
  PB-events2         attempt 3: rc=1: non-zero exit  -> now done ERROR
  PB-parity          attempt 3: rc=1: non-zero exit  -> now done ERROR
  PB-parity2         attempt 3: rc=1: non-zero exit  -> now done ERROR
  PB-plan            attempt 3: rc=2: non-zero exit  -> now done PASS
  PB-s1-A            attempt 2: rc=1: non-zero exit  -> now done PASS
  A40-fetch-prop10   attempt 2: stalled: nothing written for 120 min  -> now done PASS
  A40-fetch-prop20   attempt 2: stalled: nothing written for 120 min  -> now done PASS
  A40-fetch-ar10     attempt 2: stalled: nothing written for 120 min  -> now done PASS
  A40-fetch-ar20     attempt 2: stalled: nothing written for 120 min  -> now done PASS
  A40-E5-index-matters attempt 3: rc=1: non-zero exit  -> now done ERROR
  A40-E5b-clock-put  attempt 3: rc=1: non-zero exit  -> now done ERROR
  A40-Z6-occupancy   attempt 3: rc=2: non-zero exit  -> now done ERROR

LATEST VERDICTS
  11-21 19:49  A40-E22b-ledger-b8-swap-s3 DONE          swap_blocks/on n=47 lifted=47 s1=47 s2=47 s3=47 pressed=0 success=0 prog=0.67
  11-21 19:53  A40-fetch-rearrange_clock-e30 PASS          rc=0
  11-21 20:01  A40-fetch-swapT_clock-e30 PASS          rc=0
  11-21 20:03  A40-E22b-ledger-b8-swap-s4 DONE          swap_blocks/on n=50 lifted=50 s1=50 s2=50 s3=50 pressed=0 success=0 prog=0.67
  11-21 20:10  A40-rearrange_clock-smoke PASS          rearrange_blocks/on n=1  prog=0.00
  11-21 20:17  A40-E22b-ledger-b4-swap-s0 DONE          swap_blocks/on n=28 lifted=28 s1=28 s2=28 s3=28 pressed=0 success=0 prog=0.67
  11-21 20:27  A40-E22b-ledger-b4-swap-s1 DONE          swap_blocks/on n=35 lifted=35 s1=35 s2=35 s3=35 pressed=0 success=0 prog=0.67
  11-21 20:39  A40-E16-rearrange_ar-p64-vis-s0 DONE          rearrange_blocks/on n=10  prog=0.00
```

## A40-E14-press_v3c-e30-s3 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E14-press_v3c-e30-s3.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  press_arprop_e10/on      vs press_count_e10/on       100     0       0       1       99  1.000
  press_arprop_e10/on      vs press_count_e20/on       100     0       0       0      100  1.000
  press_arprop_e10/on      vs press_count_e30/on       100     0       0      13       87  0.000
  press_arprop_e10/on      vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_arprop_e10/on      vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_arprop_e10/on      vs press_v3c_e30/on          91     0       0      15       76  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on          91     0       1      15       75  0.001
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on          91     0       0      15       76  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on          91     1      10      14       66  0.541
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on          91     0       1      15       75  0.001
  press_v3c_e20/on         vs press_v3c_e30/on          91     1       4      14       72  0.031

[summary] 691 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E14-press_v3c-e30-s3.log):
```

[pool] 2026-11-20 22:17:29 exec A40-E14-press_v3c-e30-s3 GPU 1 
[pool] 2026-11-20 22:17:31 A40-E14-press_v3c-e30-s3: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E14-press_v3c-e30-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E14-press_v3c-e30-s3.md
[queue5] 2026-11-20 23:50:17 A40-E14-press_v3c-e30-s3: DONE  press_button/on n=91 pressed=91 n1_correct=62 n2_correct=23 confirmed=91 count_correct=15 success=15 prog=0.44
```

## A40-E14-press_v3c-e30-s4 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E14-press_v3c-e30-s4.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  press_arprop_e10/on      vs press_count_e10/on       100     0       0       1       99  1.000
  press_arprop_e10/on      vs press_count_e20/on       100     0       0       0      100  1.000
  press_arprop_e10/on      vs press_count_e30/on       100     0       0      13       87  0.000
  press_arprop_e10/on      vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_arprop_e10/on      vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_arprop_e10/on      vs press_v3c_e30/on          89     0       0      15       74  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on          89     0       1      15       73  0.001
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on          89     0       0      15       74  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on          89     1      10      14       64  0.541
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on          89     0       1      15       73  0.001
  press_v3c_e20/on         vs press_v3c_e30/on          89     1       4      14       70  0.031

[summary] 689 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E14-press_v3c-e30-s4.log):
```

[pool] 2026-11-20 22:17:29 exec A40-E14-press_v3c-e30-s4 GPU 3 
[pool] 2026-11-20 22:17:31 A40-E14-press_v3c-e30-s4: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E14-press_v3c-e30-s4.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E14-press_v3c-e30-s4.md
[queue5] 2026-11-20 23:46:15 A40-E14-press_v3c-e30-s4: DONE  press_button/on n=89 pressed=89 n1_correct=60 n2_correct=23 confirmed=89 count_correct=15 success=15 prog=0.44
```

## A40-E14-press_v3c-e30-s5 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E14-press_v3c-e30-s5.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  press_arprop_e10/on      vs press_count_e10/on       100     0       0       1       99  1.000
  press_arprop_e10/on      vs press_count_e20/on       100     0       0       0      100  1.000
  press_arprop_e10/on      vs press_count_e30/on       100     0       0      13       87  0.000
  press_arprop_e10/on      vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_arprop_e10/on      vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_arprop_e10/on      vs press_v3c_e30/on          82     0       0      12       70  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on          82     0       0      12       70  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on          82     0       0      12       70  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on          82     0       9      12       61  0.664
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on          82     0       1      12       69  0.003
  press_v3c_e20/on         vs press_v3c_e30/on          82     1       4      11       66  0.118

[summary] 682 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E14-press_v3c-e30-s5.log):
```

[pool] 2026-11-20 22:17:29 exec A40-E14-press_v3c-e30-s5 GPU 4 
[pool] 2026-11-20 22:17:31 A40-E14-press_v3c-e30-s5: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E14-press_v3c-e30-s5.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E14-press_v3c-e30-s5.md
[queue5] 2026-11-20 23:36:56 A40-E14-press_v3c-e30-s5: DONE  press_button/on n=82 pressed=82 n1_correct=55 n2_correct=18 confirmed=82 count_correct=12 success=12 prog=0.42
```

## A40-E14-press_v3c-e30-s6 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E14-press_v3c-e30-s6.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  press_arprop_e10/on      vs press_count_e10/on       100     0       0       1       99  1.000
  press_arprop_e10/on      vs press_count_e20/on       100     0       0       0      100  1.000
  press_arprop_e10/on      vs press_count_e30/on       100     0       0      13       87  0.000
  press_arprop_e10/on      vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_arprop_e10/on      vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_arprop_e10/on      vs press_v3c_e30/on          84     0       0      13       71  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on          84     0       0      13       71  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on          84     0       0      13       71  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on          84     0       9      13       62  0.523
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on          84     0       1      13       70  0.002
  press_v3c_e20/on         vs press_v3c_e30/on          84     1       4      12       67  0.077

[summary] 684 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E14-press_v3c-e30-s6.log):
```

[pool] 2026-11-20 22:17:29 exec A40-E14-press_v3c-e30-s6 GPU 5 
[pool] 2026-11-20 22:17:31 A40-E14-press_v3c-e30-s6: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E14-press_v3c-e30-s6.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E14-press_v3c-e30-s6.md
[queue5] 2026-11-20 23:38:38 A40-E14-press_v3c-e30-s6: DONE  press_button/on n=84 pressed=84 n1_correct=56 n2_correct=20 confirmed=84 count_correct=13 success=13 prog=0.43
```

## A40-E14-press_v3c-e30-s7 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E14-press_v3c-e30-s7.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  press_arprop_e10/on      vs press_count_e10/on       100     0       0       1       99  1.000
  press_arprop_e10/on      vs press_count_e20/on       100     0       0       0      100  1.000
  press_arprop_e10/on      vs press_count_e30/on       100     0       0      13       87  0.000
  press_arprop_e10/on      vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_arprop_e10/on      vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_arprop_e10/on      vs press_v3c_e30/on          88     0       0      14       74  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on          88     0       1      14       73  0.001
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on          88     0       0      14       74  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on          88     1      10      13       64  0.678
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on          88     0       1      14       73  0.001
  press_v3c_e20/on         vs press_v3c_e30/on          88     1       4      13       70  0.049

[summary] 688 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E14-press_v3c-e30-s7.log):
```

[pool] 2026-11-20 22:17:29 exec A40-E14-press_v3c-e30-s7 GPU 6 
[pool] 2026-11-20 22:17:31 A40-E14-press_v3c-e30-s7: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E14-press_v3c-e30-s7.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E14-press_v3c-e30-s7.md
[queue5] 2026-11-20 23:43:32 A40-E14-press_v3c-e30-s7: DONE  press_button/on n=88 pressed=88 n1_correct=59 n2_correct=22 confirmed=88 count_correct=14 success=14 prog=0.43
```

## A40-E14-press_v3c-e30-s8 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E14-press_v3c-e30-s8.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  press_arprop_e10/on      vs press_count_e10/on       100     0       0       1       99  1.000
  press_arprop_e10/on      vs press_count_e20/on       100     0       0       0      100  1.000
  press_arprop_e10/on      vs press_count_e30/on       100     0       0      13       87  0.000
  press_arprop_e10/on      vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_arprop_e10/on      vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_arprop_e10/on      vs press_v3c_e30/on          85     0       0      14       71  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on          85     0       0      14       71  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on          85     0       0      14       71  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on          85     1       9      13       62  0.523
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on          85     0       1      14       70  0.001
  press_v3c_e20/on         vs press_v3c_e30/on          85     1       4      13       67  0.049

[summary] 685 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E14-press_v3c-e30-s8.log):
```

[pool] 2026-11-20 22:17:29 exec A40-E14-press_v3c-e30-s8 GPU 7 
[pool] 2026-11-20 22:17:31 A40-E14-press_v3c-e30-s8: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E14-press_v3c-e30-s8.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E14-press_v3c-e30-s8.md
[queue5] 2026-11-20 23:40:21 A40-E14-press_v3c-e30-s8: DONE  press_button/on n=85 pressed=85 n1_correct=57 n2_correct=21 confirmed=85 count_correct=14 success=14 prog=0.43
```

## A40-E14-press_v3c-e30-s9 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E14-press_v3c-e30-s9.log):
```

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  press_arprop_e10/on      vs press_count_e10/on       100     0       0       1       99  1.000
  press_arprop_e10/on      vs press_count_e20/on       100     0       0       0      100  1.000
  press_arprop_e10/on      vs press_count_e30/on       100     0       0      13       87  0.000
  press_arprop_e10/on      vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_arprop_e10/on      vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_arprop_e10/on      vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 700 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E14-press_v3c-e30-s9.log):
```

[pool] 2026-11-20 23:35:16 exec A40-E14-press_v3c-e30-s9 GPU 4 
[pool] 2026-11-20 23:35:18 A40-E14-press_v3c-e30-s9: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E14-press_v3c-e30-s9.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E14-press_v3c-e30-s9.md
[queue5] 2026-11-21 01:02:48 A40-E14-press_v3c-e30-s9: DONE  press_button/on n=100 pressed=100 n1_correct=69 n2_correct=25 confirmed=100 count_correct=17 success=17 prog=0.44
```

## A40-fetch-rearrange_arprop-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearrange_arprop-e30.log):
```
[fetch] 2026-11-21 10:43:22 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 10:48:23 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 10:53:23 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 10:58:24 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 11:03:24 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 11:08:25 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 11:13:25 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 11:18:26 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 11:23:26 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 11:28:27 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 11:33:28 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 11:38:28 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 11:43:29 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 11:48:30 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 11:53:30 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 11:58:31 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 12:03:31 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 12:08:32 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 12:13:33 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 12:18:33 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 12:23:34 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 12:28:34 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 12:33:35 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 12:38:35 waiting for exports/rearrange_arprop_e30 on the relay
[fetch] 2026-11-21 12:43:36 waiting for exports/rearrange_arprop_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearrange_arprop-e30.log):
```

[pool] 2026-11-19 19:17:58 exec A40-fetch-rearrange_arprop-e30 GPU None 
[pool] 2026-11-19 19:18:00 A40-fetch-rearrange_arprop-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearrange_arprop-e30.log
```

## A40-fetch-swapT_arprop-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_arprop-e30.log):
```
[fetch] 2026-11-21 10:43:23 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 10:48:23 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 10:53:24 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 10:58:24 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 11:03:25 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 11:08:25 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 11:13:26 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 11:18:27 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 11:23:27 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 11:28:28 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 11:33:28 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 11:38:29 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 11:43:29 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 11:48:30 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 11:53:31 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 11:58:31 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 12:03:32 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 12:08:32 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 12:13:33 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 12:18:33 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 12:23:34 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 12:28:35 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 12:33:35 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 12:38:36 waiting for exports/swapT_arprop_e30 on the relay
[fetch] 2026-11-21 12:43:36 waiting for exports/swapT_arprop_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-swapT_arprop-e30.log):
```

[pool] 2026-11-19 19:17:58 exec A40-fetch-swapT_arprop-e30 GPU None 
[pool] 2026-11-19 19:18:00 A40-fetch-swapT_arprop-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_arprop-e30.log
```

## A40-fetch-ar2_arev-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-ar2_arev-e30.log):
```
[fetch] 2026-11-21 10:43:27 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 10:48:28 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 10:53:28 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 10:58:29 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 11:03:29 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 11:08:30 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 11:13:30 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 11:18:31 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 11:23:32 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 11:28:32 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 11:33:33 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 11:38:33 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 11:43:34 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 11:48:34 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 11:53:35 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 11:58:36 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 12:03:36 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 12:08:37 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 12:13:37 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 12:18:38 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 12:23:38 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 12:28:39 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 12:33:40 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 12:38:40 waiting for exports/ar2_arev_e30 on the relay
[fetch] 2026-11-21 12:43:41 waiting for exports/ar2_arev_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-ar2_arev-e30.log):
```

[pool] 2026-11-19 19:17:58 exec A40-fetch-ar2_arev-e30 GPU None 
[pool] 2026-11-19 19:18:00 A40-fetch-ar2_arev-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-ar2_arev-e30.log
```

## A40-fetch-ar2_tw-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-ar2_tw-e30.log):
```
[fetch] 2026-11-21 10:43:24 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 10:48:24 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 10:53:25 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 10:58:25 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 11:03:26 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 11:08:27 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 11:13:27 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 11:18:28 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 11:23:28 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 11:28:29 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 11:33:29 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 11:38:30 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 11:43:31 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 11:48:31 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 11:53:32 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 11:58:33 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 12:03:34 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 12:08:34 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 12:13:35 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 12:18:35 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 12:23:36 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 12:28:36 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 12:33:37 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 12:38:38 waiting for exports/ar2_tw_e30 on the relay
[fetch] 2026-11-21 12:43:38 waiting for exports/ar2_tw_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-ar2_tw-e30.log):
```

[pool] 2026-11-19 19:17:58 exec A40-fetch-ar2_tw-e30 GPU None 
[pool] 2026-11-19 19:18:00 A40-fetch-ar2_tw-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-ar2_tw-e30.log
```

## A40-fetch-press_clock-e10 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-press_clock-e10.log):
```
[fetch] 2026-11-21 10:43:27 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 10:48:28 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 10:53:28 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 10:58:29 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 11:03:29 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 11:08:30 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 11:13:30 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 11:18:31 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 11:23:31 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 11:28:32 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 11:33:32 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 11:38:33 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 11:43:34 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 11:48:35 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 11:53:36 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 11:58:38 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 12:03:39 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 12:08:40 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 12:13:40 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 12:18:41 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 12:23:41 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 12:28:42 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 12:33:42 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 12:38:43 waiting for exports/press_clock_e10 on the relay
[fetch] 2026-11-21 12:43:43 waiting for exports/press_clock_e10 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-press_clock-e10.log):
```

[pool] 2026-11-19 19:17:58 exec A40-fetch-press_clock-e10 GPU None 
[pool] 2026-11-19 19:18:00 A40-fetch-press_clock-e10: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-press_clock-e10.log
```

## A40-fetch-press_clock-e20 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-press_clock-e20.log):
```
[fetch] 2026-11-21 10:43:25 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 10:48:25 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 10:53:26 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 10:58:26 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 11:03:27 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 11:08:27 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 11:13:28 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 11:18:29 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 11:23:29 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 11:28:30 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 11:33:30 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 11:38:31 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 11:43:32 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 11:48:33 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 11:53:33 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 11:58:34 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 12:03:34 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 12:08:35 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 12:13:35 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 12:18:36 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 12:23:36 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 12:28:37 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 12:33:37 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 12:38:38 waiting for exports/press_clock_e20 on the relay
[fetch] 2026-11-21 12:43:38 waiting for exports/press_clock_e20 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-press_clock-e20.log):
```

[pool] 2026-11-19 19:17:58 exec A40-fetch-press_clock-e20 GPU None 
[pool] 2026-11-19 19:18:00 A40-fetch-press_clock-e20: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-press_clock-e20.log
```

## A40-fetch-press_clock-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-press_clock-e30.log):
```
[fetch] 2026-11-21 10:43:27 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 10:48:27 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 10:53:28 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 10:58:29 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 11:03:29 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 11:08:30 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 11:13:30 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 11:18:31 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 11:23:31 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 11:28:32 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 11:33:33 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 11:38:33 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 11:43:34 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 11:48:34 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 11:53:35 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 11:58:37 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 12:03:37 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 12:08:38 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 12:13:38 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 12:18:39 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 12:23:39 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 12:28:40 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 12:33:41 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 12:38:41 waiting for exports/press_clock_e30 on the relay
[fetch] 2026-11-21 12:43:42 waiting for exports/press_clock_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-press_clock-e30.log):
```

[pool] 2026-11-19 19:17:58 exec A40-fetch-press_clock-e30 GPU None 
[pool] 2026-11-19 19:18:00 A40-fetch-press_clock-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-press_clock-e30.log
```

## A40-E21-off-swap-s3 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-off-swap-s3.log):
```
[decide] 2026-11-20 16:49:30 ar2_clock_e30_clkoff/on swap_blocks seed=4300114 frame=928/1000 hist=3 policy=0.6s elapsed=341s
[decide] 2026-11-20 16:49:41 ar2_clock_e30_clkoff/on swap_blocks seed=4300114 frame=960/1000 hist=3 policy=0.6s elapsed=352s
[decide] 2026-11-20 16:49:51 ar2_clock_e30_clkoff/on swap_blocks seed=4300114 frame=992/1000 hist=3 policy=0.6s elapsed=362s
[closed-loop] 2026-11-20 16:49:56 done  ar2_clock_e30_clkoff/on swap_blocks seed=4300114 success=False targets=1000/1000 reward=0.0 lift=0.08650785684585571  407s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_clock_e30_clkflat/onswap_blocks        2     0.00  [0.00,0.66]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_clkfreeze/onswap_blocks       38     1.00  [0.91,1.00]      1.00    1.00      586        -        -        -    0.6
ar2_clock_e30_clkoff/on swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts0.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts1.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkfreeze/on   2     0       0       2        0  0.500
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkoff/on    2     0       0       0        2  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts0.5/on     2     0       0       0        2  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts1.5/on     2     0       0       0        2  1.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_clkoff/on   38     0      38       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts0.5/on    38     0      38       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts1.5/on    38     0      38       0        0  0.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts0.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_ts0.5/on   vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000

[summary] 190 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E21-off-swap-s3.log):
```

[pool] 2026-11-20 23:36:54 exec A40-E21-off-swap-s3 GPU 5 
[pool] 2026-11-20 23:36:56 A40-E21-off-swap-s3: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-off-swap-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-off-swap-s3.md
[queue5] 2026-11-21 00:52:07 A40-E21-off-swap-s3: DONE  swap_blocks/on n=50 lifted=50 s1=50 s2=50 s3=50 pressed=0 success=0 prog=0.67
```

## A40-E21-off-swap-s4 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-off-swap-s4.log):
```
[decide] 2026-11-20 16:47:06 ar2_clock_e30_clkoff/on swap_blocks seed=4300116 frame=928/1000 hist=3 policy=0.5s elapsed=333s
[decide] 2026-11-20 16:47:16 ar2_clock_e30_clkoff/on swap_blocks seed=4300116 frame=960/1000 hist=3 policy=0.6s elapsed=343s
[decide] 2026-11-20 16:47:26 ar2_clock_e30_clkoff/on swap_blocks seed=4300116 frame=992/1000 hist=3 policy=0.5s elapsed=353s
[closed-loop] 2026-11-20 16:47:31 done  ar2_clock_e30_clkoff/on swap_blocks seed=4300116 success=False targets=1000/1000 reward=0.0 lift=0.08367282152175903  397s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_clock_e30_clkflat/onswap_blocks        1     0.00  [0.00,0.79]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_clkfreeze/onswap_blocks       37     1.00  [0.91,1.00]      1.00    1.00      585        -        -        -    0.6
ar2_clock_e30_clkoff/on swap_blocks       49     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts0.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts1.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkfreeze/on   1     0       0       1        0  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkoff/on    1     0       0       0        1  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts0.5/on     1     0       0       0        1  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts1.5/on     1     0       0       0        1  1.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_clkoff/on   37     0      37       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts0.5/on    37     0      37       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts1.5/on    37     0      37       0        0  0.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts0.5/on    49     0       0       0       49  1.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts1.5/on    49     0       0       0       49  1.000
  ar2_clock_e30_ts0.5/on   vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000

[summary] 187 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E21-off-swap-s4.log):
```

[pool] 2026-11-20 23:38:30 exec A40-E21-off-swap-s4 GPU 7 
[pool] 2026-11-20 23:38:32 A40-E21-off-swap-s4: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-off-swap-s4.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-off-swap-s4.md
[queue5] 2026-11-21 00:49:39 A40-E21-off-swap-s4: DONE  swap_blocks/on n=49 lifted=49 s1=49 s2=49 s3=49 pressed=0 success=0 prog=0.67
```

## A40-E21-freeze-swap-s0 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-freeze-swap-s0.log):
```
[decide] 2026-11-20 16:25:35 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300103 frame=352/1000 hist=3 policy=0.6s elapsed=134s
[decide] 2026-11-20 16:25:46 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300103 frame=384/1000 hist=3 policy=0.6s elapsed=144s
[decide] 2026-11-20 16:25:56 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300103 frame=416/1000 hist=3 policy=0.6s elapsed=155s
[decide] 2026-11-20 16:26:07 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300103 frame=448/1000 hist=3 policy=0.6s elapsed=166s
[decide] 2026-11-20 16:26:17 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300103 frame=480/1000 hist=3 policy=0.6s elapsed=176s
[decide] 2026-11-20 16:26:28 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300103 frame=512/1000 hist=3 policy=0.6s elapsed=187s
[decide] 2026-11-20 16:26:40 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300103 frame=544/1000 hist=3 policy=0.6s elapsed=199s
[decide] 2026-11-20 16:26:55 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300103 frame=576/1000 hist=3 policy=0.6s elapsed=213s
[closed-loop] 2026-11-20 16:27:01 done  ar2_clock_e30_clkfreeze/on swap_blocks seed=4300103 success=True targets=590/1000 reward=1.0 lift=0.10089325904846191  259s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_clock_e30_clkfreeze/onswap_blocks       27     1.00  [0.88,1.00]      1.00    1.00      584        -        -        -    0.6
ar2_clock_e30_clkoff/on swap_blocks       42     0.00  [0.00,0.08]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts0.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts1.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_clkoff/on   27     0      27       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts0.5/on    27     0      27       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts1.5/on    27     0      27       0        0  0.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts0.5/on    42     0       0       0       42  1.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts1.5/on    42     0       0       0       42  1.000
  ar2_clock_e30_ts0.5/on   vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000

[summary] 169 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E21-freeze-swap-s0.log):
```

[pool] 2026-11-20 23:41:43 exec A40-E21-freeze-swap-s0 GPU 6 
[pool] 2026-11-20 23:41:45 A40-E21-freeze-swap-s0: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-freeze-swap-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-freeze-swap-s0.md
[queue5] 2026-11-21 00:27:23 A40-E21-freeze-swap-s0: DONE  swap_blocks/on n=27 lifted=27 s1=27 s2=27 s3=27 pressed=27 success=27 prog=1.00
```

## A40-E21-freeze-swap-s1 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-freeze-swap-s1.log):
```
[decide] 2026-11-20 16:27:00 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300105 frame=352/1000 hist=3 policy=0.6s elapsed=123s
[decide] 2026-11-20 16:27:10 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300105 frame=384/1000 hist=3 policy=0.6s elapsed=134s
[decide] 2026-11-20 16:27:20 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300105 frame=416/1000 hist=3 policy=0.6s elapsed=144s
[decide] 2026-11-20 16:27:30 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300105 frame=448/1000 hist=3 policy=0.6s elapsed=154s
[decide] 2026-11-20 16:27:47 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300105 frame=480/1000 hist=3 policy=0.6s elapsed=170s
[decide] 2026-11-20 16:27:57 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300105 frame=512/1000 hist=3 policy=0.6s elapsed=181s
[decide] 2026-11-20 16:28:07 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300105 frame=544/1000 hist=3 policy=0.6s elapsed=190s
[decide] 2026-11-20 16:28:18 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300105 frame=576/1000 hist=3 policy=0.6s elapsed=202s
[closed-loop] 2026-11-20 16:28:26 done  ar2_clock_e30_clkfreeze/on swap_blocks seed=4300105 success=True targets=587/1000 reward=1.0 lift=0.09998226165771484  254s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_clock_e30_clkfreeze/onswap_blocks       29     1.00  [0.88,1.00]      1.00    1.00      584        -        -        -    0.6
ar2_clock_e30_clkoff/on swap_blocks       43     0.00  [0.00,0.08]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts0.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts1.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_clkoff/on   29     0      29       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts0.5/on    29     0      29       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts1.5/on    29     0      29       0        0  0.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts0.5/on    43     0       0       0       43  1.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts1.5/on    43     0       0       0       43  1.000
  ar2_clock_e30_ts0.5/on   vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000

[summary] 172 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E21-freeze-swap-s1.log):
```

[pool] 2026-11-20 23:44:24 exec A40-E21-freeze-swap-s1 GPU 3 
[pool] 2026-11-20 23:44:26 A40-E21-freeze-swap-s1: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-freeze-swap-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-freeze-swap-s1.md
[queue5] 2026-11-21 00:28:52 A40-E21-freeze-swap-s1: DONE  swap_blocks/on n=29 lifted=29 s1=29 s2=29 s3=29 pressed=29 success=29 prog=1.00
```

## A40-E21-freeze-swap-s2 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-freeze-swap-s2.log):
```
[decide] 2026-11-20 16:31:10 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300113 frame=352/1000 hist=3 policy=0.6s elapsed=138s
[decide] 2026-11-20 16:31:20 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300113 frame=384/1000 hist=3 policy=0.6s elapsed=148s
[decide] 2026-11-20 16:31:32 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300113 frame=416/1000 hist=3 policy=0.6s elapsed=160s
[decide] 2026-11-20 16:31:46 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300113 frame=448/1000 hist=3 policy=0.6s elapsed=174s
[decide] 2026-11-20 16:31:56 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300113 frame=480/1000 hist=3 policy=0.6s elapsed=184s
[decide] 2026-11-20 16:32:07 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300113 frame=512/1000 hist=3 policy=0.6s elapsed=195s
[decide] 2026-11-20 16:32:17 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300113 frame=544/1000 hist=3 policy=0.6s elapsed=205s
[decide] 2026-11-20 16:32:27 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300113 frame=576/1000 hist=3 policy=0.6s elapsed=215s
[closed-loop] 2026-11-20 16:32:31 done  ar2_clock_e30_clkfreeze/on swap_blocks seed=4300113 success=True targets=580/1000 reward=1.0 lift=0.10028839111328125  258s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_clock_e30_clkfreeze/onswap_blocks       30     1.00  [0.89,1.00]      1.00    1.00      584        -        -        -    0.6
ar2_clock_e30_clkoff/on swap_blocks       44     0.00  [0.00,0.08]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts0.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts1.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_clkoff/on   30     0      30       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts0.5/on    30     0      30       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts1.5/on    30     0      30       0        0  0.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts0.5/on    44     0       0       0       44  1.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts1.5/on    44     0       0       0       44  1.000
  ar2_clock_e30_ts0.5/on   vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000

[summary] 174 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E21-freeze-swap-s2.log):
```

[pool] 2026-11-20 23:48:44 exec A40-E21-freeze-swap-s2 GPU 1 
[pool] 2026-11-20 23:48:46 A40-E21-freeze-swap-s2: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-freeze-swap-s2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-freeze-swap-s2.md
[queue5] 2026-11-21 00:32:55 A40-E21-freeze-swap-s2: DONE  swap_blocks/on n=30 lifted=30 s1=30 s2=30 s3=30 pressed=30 success=30 prog=1.00
```

## A40-E21-freeze-swap-s3 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-freeze-swap-s3.log):
```
[decide] 2026-11-20 17:11:19 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300114 frame=512/1000 hist=3 policy=0.5s elapsed=187s
[decide] 2026-11-20 17:11:31 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300114 frame=544/1000 hist=3 policy=0.6s elapsed=199s
[decide] 2026-11-20 17:11:45 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300114 frame=576/1000 hist=3 policy=0.6s elapsed=214s
[closed-loop] 2026-11-20 17:11:50 done  ar2_clock_e30_clkfreeze/on swap_blocks seed=4300114 success=True targets=583/1000 reward=1.0 lift=0.1003066897392273  257s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_clock_e30_clkflat/onswap_blocks       11     0.00  [0.00,0.26]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_clkfreeze/onswap_blocks       49     1.00  [0.93,1.00]      1.00    1.00      586        -        -        -    0.6
ar2_clock_e30_clkoff/on swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts0.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts1.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkfreeze/on  11     0       0      11        0  0.001
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkoff/on   11     0       0       0       11  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts0.5/on    11     0       0       0       11  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts1.5/on    11     0       0       0       11  1.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_clkoff/on   49     0      49       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts0.5/on    49     0      49       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts1.5/on    49     0      49       0        0  0.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts0.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_ts0.5/on   vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000

[summary] 210 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E21-freeze-swap-s3.log):
```

[pool] 2026-11-21 00:28:29 exec A40-E21-freeze-swap-s3 GPU 6 
[pool] 2026-11-21 00:28:31 A40-E21-freeze-swap-s3: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-freeze-swap-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-freeze-swap-s3.md
[queue5] 2026-11-21 01:12:28 A40-E21-freeze-swap-s3: DONE  swap_blocks/on n=49 lifted=49 s1=49 s2=49 s3=49 pressed=49 success=49 prog=1.00
```

## A40-E21-freeze-swap-s4 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-freeze-swap-s4.log):
```
[decide] 2026-11-20 17:14:15 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300116 frame=512/1000 hist=3 policy=0.6s elapsed=188s
[decide] 2026-11-20 17:14:25 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300116 frame=544/1000 hist=3 policy=0.6s elapsed=198s
[decide] 2026-11-20 17:14:36 ar2_clock_e30_clkfreeze/on swap_blocks seed=4300116 frame=576/1000 hist=3 policy=0.6s elapsed=209s
[closed-loop] 2026-11-20 17:14:44 done  ar2_clock_e30_clkfreeze/on swap_blocks seed=4300116 success=True targets=594/1000 reward=1.0 lift=0.10074245929718018  255s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_clock_e30_clkflat/onswap_blocks       12     0.00  [0.00,0.24]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_clkfreeze/onswap_blocks       50     1.00  [0.93,1.00]      1.00    1.00      586        -        -        -    0.6
ar2_clock_e30_clkoff/on swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts0.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts1.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkfreeze/on  12     0       0      12        0  0.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkoff/on   12     0       0       0       12  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts0.5/on    12     0       0       0       12  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts1.5/on    12     0       0       0       12  1.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_clkoff/on   50     0      50       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts0.5/on    50     0      50       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts1.5/on    50     0      50       0        0  0.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts0.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_ts0.5/on   vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000

[summary] 212 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E21-freeze-swap-s4.log):
```

[pool] 2026-11-21 00:30:05 exec A40-E21-freeze-swap-s4 GPU 3 
[pool] 2026-11-21 00:30:07 A40-E21-freeze-swap-s4: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-freeze-swap-s4.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-freeze-swap-s4.md
[queue5] 2026-11-21 01:15:23 A40-E21-freeze-swap-s4: DONE  swap_blocks/on n=50 lifted=50 s1=50 s2=50 s3=50 pressed=50 success=50 prog=1.00
```

## A40-E21-flat-swap-s0 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-flat-swap-s0.log):
```
[decide] 2026-11-20 17:42:04 ar2_clock_e30_clkflat/on swap_blocks seed=4300103 frame=960/1000 hist=3 policy=0.6s elapsed=337s
[decide] 2026-11-20 17:42:14 ar2_clock_e30_clkflat/on swap_blocks seed=4300103 frame=992/1000 hist=3 policy=0.6s elapsed=347s
[closed-loop] 2026-11-20 17:42:20 done  ar2_clock_e30_clkflat/on swap_blocks seed=4300103 success=False targets=1000/1000 reward=0.0 lift=0.10130739212036133  412s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_clock_e30_clkflat/onswap_blocks       32     0.00  [0.00,0.11]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_clkfreeze/onswap_blocks       50     1.00  [0.93,1.00]      1.00    1.00      586        -        -        -    0.6
ar2_clock_e30_clkoff/on put_back_block     8     0.88  [0.53,0.98]      1.00    0.88      381        -        -        -    0.6
ar2_clock_e30_clkoff/on swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts0.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts1.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkfreeze/on  32     0       0      32        0  0.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkoff/on   32     0       0       0       32  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts0.5/on    32     0       0       0       32  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts1.5/on    32     0       0       0       32  1.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_clkoff/on   50     0      50       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts0.5/on    50     0      50       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts1.5/on    50     0      50       0        0  0.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts0.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_ts0.5/on   vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000

[summary] 240 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E21-flat-swap-s0.log):
```

[pool] 2026-11-21 00:33:51 exec A40-E21-flat-swap-s0 GPU 1 
[pool] 2026-11-21 00:33:53 A40-E21-flat-swap-s0: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-flat-swap-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-flat-swap-s0.md
[queue5] 2026-11-21 01:43:48 A40-E21-flat-swap-s0: DONE  swap_blocks/on n=32 lifted=32 s1=32 s2=32 s3=32 pressed=32 success=0 prog=0.83
```

## A40-E21-flat-swap-s1 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-flat-swap-s1.log):
```
[decide] 2026-11-20 17:58:51 ar2_clock_e30_clkflat/on swap_blocks seed=4300105 frame=960/1000 hist=3 policy=0.6s elapsed=364s
[decide] 2026-11-20 17:59:02 ar2_clock_e30_clkflat/on swap_blocks seed=4300105 frame=992/1000 hist=3 policy=0.6s elapsed=374s
[closed-loop] 2026-11-20 17:59:07 done  ar2_clock_e30_clkflat/on swap_blocks seed=4300105 success=False targets=1000/1000 reward=0.0 lift=0.10127246379852295  417s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_clock_e30_clkflat/onswap_blocks       43     0.00  [0.00,0.08]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_clkfreeze/onswap_blocks       50     1.00  [0.93,1.00]      1.00    1.00      586        -        -        -    0.6
ar2_clock_e30_clkoff/on put_back_block    17     0.88  [0.66,0.97]      1.00    0.88      379        -        -        -    0.6
ar2_clock_e30_clkoff/on swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts0.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts1.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkfreeze/on  43     0       0      43        0  0.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkoff/on   43     0       0       0       43  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts0.5/on    43     0       0       0       43  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts1.5/on    43     0       0       0       43  1.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_clkoff/on   50     0      50       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts0.5/on    50     0      50       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts1.5/on    50     0      50       0        0  0.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts0.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_ts0.5/on   vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000

[summary] 260 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E21-flat-swap-s1.log):
```

[pool] 2026-11-21 00:49:26 exec A40-E21-flat-swap-s1 GPU 7 
[pool] 2026-11-21 00:49:28 A40-E21-flat-swap-s1: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-flat-swap-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-flat-swap-s1.md
[queue5] 2026-11-21 02:01:01 A40-E21-flat-swap-s1: DONE  swap_blocks/on n=43 lifted=43 s1=43 s2=43 s3=43 pressed=43 success=0 prog=0.83
```

## A40-E21-flat-swap-s2 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-flat-swap-s2.log):
```
[decide] 2026-11-20 18:01:55 ar2_clock_e30_clkflat/on swap_blocks seed=4300113 frame=960/1000 hist=3 policy=0.6s elapsed=354s
[decide] 2026-11-20 18:02:08 ar2_clock_e30_clkflat/on swap_blocks seed=4300113 frame=992/1000 hist=3 policy=0.6s elapsed=367s
[closed-loop] 2026-11-20 18:02:21 done  ar2_clock_e30_clkflat/on swap_blocks seed=4300113 success=False targets=1000/1000 reward=0.0 lift=0.1012800931930542  426s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_clock_e30_clkflat/onswap_blocks       44     0.00  [0.00,0.08]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_clkfreeze/onswap_blocks       50     1.00  [0.93,1.00]      1.00    1.00      586        -        -        -    0.6
ar2_clock_e30_clkoff/on put_back_block    19     0.84  [0.62,0.94]      1.00    0.84      385        -        -        -    0.6
ar2_clock_e30_clkoff/on swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts0.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts1.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkfreeze/on  44     0       0      44        0  0.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkoff/on   44     0       0       0       44  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts0.5/on    44     0       0       0       44  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts1.5/on    44     0       0       0       44  1.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_clkoff/on   50     0      50       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts0.5/on    50     0      50       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts1.5/on    50     0      50       0        0  0.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts0.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_ts0.5/on   vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000

[summary] 263 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E21-flat-swap-s2.log):
```

[pool] 2026-11-21 00:51:35 exec A40-E21-flat-swap-s2 GPU 5 
[pool] 2026-11-21 00:51:36 A40-E21-flat-swap-s2: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-flat-swap-s2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-flat-swap-s2.md
[queue5] 2026-11-21 02:04:17 A40-E21-flat-swap-s2: DONE  swap_blocks/on n=44 lifted=44 s1=44 s2=44 s3=44 pressed=44 success=0 prog=0.83
```

## A40-E21-flat-swap-s3 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-flat-swap-s3.log):
```
[decide] 2026-11-20 18:10:12 ar2_clock_e30_clkflat/on swap_blocks seed=4300114 frame=960/1000 hist=3 policy=0.6s elapsed=364s
[decide] 2026-11-20 18:10:22 ar2_clock_e30_clkflat/on swap_blocks seed=4300114 frame=992/1000 hist=3 policy=0.6s elapsed=374s
[closed-loop] 2026-11-20 18:10:27 done  ar2_clock_e30_clkflat/on swap_blocks seed=4300114 success=False targets=1000/1000 reward=0.0 lift=0.10226553678512573  430s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_clock_e30_clkflat/onswap_blocks       47     0.00  [0.00,0.08]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_clkfreeze/onswap_blocks       50     1.00  [0.93,1.00]      1.00    1.00      586        -        -        -    0.6
ar2_clock_e30_clkoff/on put_back_block    27     0.85  [0.68,0.94]      1.00    0.85      382        -        -        -    0.6
ar2_clock_e30_clkoff/on swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts0.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts1.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkfreeze/on  47     0       0      47        0  0.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkoff/on   47     0       0       0       47  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts0.5/on    47     0       0       0       47  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts1.5/on    47     0       0       0       47  1.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_clkoff/on   50     0      50       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts0.5/on    50     0      50       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts1.5/on    50     0      50       0        0  0.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts0.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_ts0.5/on   vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000

[summary] 274 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E21-flat-swap-s3.log):
```

[pool] 2026-11-21 01:00:40 exec A40-E21-flat-swap-s3 GPU 4 
[pool] 2026-11-21 01:00:42 A40-E21-flat-swap-s3: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-flat-swap-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-flat-swap-s3.md
[queue5] 2026-11-21 02:12:34 A40-E21-flat-swap-s3: DONE  swap_blocks/on n=47 lifted=47 s1=47 s2=47 s3=47 pressed=47 success=0 prog=0.83
```

## A40-E21-flat-swap-s4 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-flat-swap-s4.log):
```
[decide] 2026-11-20 18:24:58 ar2_clock_e30_clkflat/on swap_blocks seed=4300116 frame=960/1000 hist=3 policy=0.6s elapsed=371s
[decide] 2026-11-20 18:25:09 ar2_clock_e30_clkflat/on swap_blocks seed=4300116 frame=992/1000 hist=3 policy=0.6s elapsed=381s
[closed-loop] 2026-11-20 18:25:14 done  ar2_clock_e30_clkflat/on swap_blocks seed=4300116 success=False targets=1000/1000 reward=0.0 lift=0.10198169946670532  429s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_clock_e30_clkflat/onswap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_clkfreeze/onswap_blocks       50     1.00  [0.93,1.00]      1.00    1.00      586        -        -        -    0.6
ar2_clock_e30_clkoff/on put_back_block    43     0.81  [0.67,0.90]      1.00    0.81      388        -        -        -    0.6
ar2_clock_e30_clkoff/on swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts0.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts1.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkfreeze/on  50     0       0      50        0  0.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkoff/on   50     0       0       0       50  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts0.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_clkoff/on   50     0      50       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts0.5/on    50     0      50       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts1.5/on    50     0      50       0        0  0.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts0.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_ts0.5/on   vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000

[summary] 293 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E21-flat-swap-s4.log):
```

[pool] 2026-11-21 01:13:31 exec A40-E21-flat-swap-s4 GPU 6 
[pool] 2026-11-21 01:13:33 A40-E21-flat-swap-s4: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-flat-swap-s4.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-flat-swap-s4.md
[queue5] 2026-11-21 02:27:24 A40-E21-flat-swap-s4: DONE  swap_blocks/on n=50 lifted=50 s1=50 s2=50 s3=50 pressed=50 success=0 prog=0.83
```

## A40-E21-off-put-s0 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-off-put-s0.log):
```
[decide] 2026-11-20 17:46:48 ar2_clock_e30_clkoff/on put_back_block seed=4300045 frame=320/500 hist=3 policy=0.6s elapsed=120s
[decide] 2026-11-20 17:46:58 ar2_clock_e30_clkoff/on put_back_block seed=4300045 frame=352/500 hist=3 policy=0.6s elapsed=130s
[closed-loop] 2026-11-20 17:47:02 done  ar2_clock_e30_clkoff/on put_back_block seed=4300045 success=True targets=359/500 reward=1.0 lift=0.12393146753311157  172s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_clock_e30_clkflat/onswap_blocks       35     0.00  [0.00,0.10]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_clkfreeze/onswap_blocks       50     1.00  [0.93,1.00]      1.00    1.00      586        -        -        -    0.6
ar2_clock_e30_clkoff/on put_back_block    10     0.90  [0.60,0.98]      1.00    0.90      376        -        -        -    0.6
ar2_clock_e30_clkoff/on swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts0.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts1.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkfreeze/on  35     0       0      35        0  0.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkoff/on   35     0       0       0       35  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts0.5/on    35     0       0       0       35  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts1.5/on    35     0       0       0       35  1.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_clkoff/on   50     0      50       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts0.5/on    50     0      50       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts1.5/on    50     0      50       0        0  0.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts0.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_ts0.5/on   vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000

[summary] 245 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E21-off-put-s0.log):
```

[pool] 2026-11-21 01:16:11 exec A40-E21-off-put-s0 GPU 3 
[pool] 2026-11-21 01:16:13 A40-E21-off-put-s0: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-off-put-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-off-put-s0.md
[queue5] 2026-11-21 01:47:09 A40-E21-off-put-s0: DONE  put_back_block/on n=10 lifted=10 centre=10 pressed=9 stage1=9 regrasp=9 returned=10 success=9 prog=0.93
```

## A40-E21-off-put-s1 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-off-put-s1.log):
```
[decide] 2026-11-20 18:16:05 ar2_clock_e30_clkoff/on put_back_block seed=4300046 frame=320/500 hist=3 policy=0.5s elapsed=122s
[decide] 2026-11-20 18:16:15 ar2_clock_e30_clkoff/on put_back_block seed=4300046 frame=352/500 hist=3 policy=0.5s elapsed=132s
[closed-loop] 2026-11-20 18:16:23 done  ar2_clock_e30_clkoff/on put_back_block seed=4300046 success=True targets=375/500 reward=1.0 lift=0.12192600965499878  185s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_clock_e30_clkflat/onswap_blocks       48     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_clkfreeze/onswap_blocks       50     1.00  [0.93,1.00]      1.00    1.00      586        -        -        -    0.6
ar2_clock_e30_clkoff/on put_back_block    35     0.80  [0.64,0.90]      1.00    0.80      390        -        -        -    0.6
ar2_clock_e30_clkoff/on swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts0.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts1.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkfreeze/on  48     0       0      48        0  0.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkoff/on   48     0       0       0       48  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts0.5/on    48     0       0       0       48  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts1.5/on    48     0       0       0       48  1.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_clkoff/on   50     0      50       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts0.5/on    50     0      50       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts1.5/on    50     0      50       0        0  0.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts0.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_ts0.5/on   vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000

[summary] 283 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E21-off-put-s1.log):
```

[pool] 2026-11-21 01:44:08 exec A40-E21-off-put-s1 GPU 1 
[pool] 2026-11-21 01:44:10 A40-E21-off-put-s1: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-off-put-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-off-put-s1.md
[queue5] 2026-11-21 02:16:43 A40-E21-off-put-s1: DONE  put_back_block/on n=35 lifted=35 centre=35 pressed=28 stage1=28 regrasp=28 returned=35 success=28 prog=0.87
```

## A40-E21-off-put-s2 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-off-put-s2.log):
```
[decide] 2026-11-20 18:21:17 ar2_clock_e30_clkoff/on put_back_block seed=4300047 frame=320/500 hist=3 policy=0.5s elapsed=123s
[decide] 2026-11-20 18:21:27 ar2_clock_e30_clkoff/on put_back_block seed=4300047 frame=352/500 hist=3 policy=0.5s elapsed=132s
[closed-loop] 2026-11-20 18:21:32 done  ar2_clock_e30_clkoff/on put_back_block seed=4300047 success=True targets=361/500 reward=1.0 lift=0.12374740839004517  174s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_clock_e30_clkflat/onswap_blocks       49     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_clkfreeze/onswap_blocks       50     1.00  [0.93,1.00]      1.00    1.00      586        -        -        -    0.6
ar2_clock_e30_clkoff/on put_back_block    41     0.83  [0.69,0.91]      1.00    0.83      385        -        -        -    0.6
ar2_clock_e30_clkoff/on swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts0.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts1.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkfreeze/on  49     0       0      49        0  0.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkoff/on   49     0       0       0       49  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts0.5/on    49     0       0       0       49  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts1.5/on    49     0       0       0       49  1.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_clkoff/on   50     0      50       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts0.5/on    50     0      50       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts1.5/on    50     0      50       0        0  0.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts0.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_ts0.5/on   vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000

[summary] 290 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E21-off-put-s2.log):
```

[pool] 2026-11-21 01:48:27 exec A40-E21-off-put-s2 GPU 3 
[pool] 2026-11-21 01:48:29 A40-E21-off-put-s2: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-off-put-s2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-off-put-s2.md
[queue5] 2026-11-21 02:21:54 A40-E21-off-put-s2: DONE  put_back_block/on n=41 lifted=41 centre=41 pressed=34 stage1=34 regrasp=34 returned=41 success=34 prog=0.89
```

## A40-E21-off-put-s3 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-off-put-s3.log):
```
[decide] 2026-11-20 18:33:05 ar2_clock_e30_clkoff/on put_back_block seed=4300048 frame=320/500 hist=3 policy=0.5s elapsed=109s
[decide] 2026-11-20 18:33:20 ar2_clock_e30_clkoff/on put_back_block seed=4300048 frame=352/500 hist=3 policy=0.5s elapsed=124s
[closed-loop] 2026-11-20 18:33:27 done  ar2_clock_e30_clkoff/on put_back_block seed=4300048 success=True targets=368/500 reward=1.0 lift=0.1220274567604065  171s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_clock_e30_clkflat/onswap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_clkfreeze/onswap_blocks       50     1.00  [0.93,1.00]      1.00    1.00      586        -        -        -    0.6
ar2_clock_e30_clkoff/on put_back_block    49     0.82  [0.69,0.90]      1.00    0.82      387        -        -        -    0.6
ar2_clock_e30_clkoff/on swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts0.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts1.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkfreeze/on  50     0       0      50        0  0.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkoff/on   50     0       0       0       50  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts0.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_clkoff/on   50     0      50       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts0.5/on    50     0      50       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts1.5/on    50     0      50       0        0  0.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts0.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_ts0.5/on   vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000

[summary] 299 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E21-off-put-s3.log):
```

[pool] 2026-11-21 02:00:45 exec A40-E21-off-put-s3 GPU 7 
[pool] 2026-11-21 02:00:47 A40-E21-off-put-s3: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-off-put-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-off-put-s3.md
[queue5] 2026-11-21 02:33:53 A40-E21-off-put-s3: DONE  put_back_block/on n=49 lifted=49 centre=49 pressed=40 stage1=40 regrasp=40 returned=49 success=40 prog=0.88
```

## A40-E21-off-put-s4 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-off-put-s4.log):
```
[decide] 2026-11-20 18:33:32 ar2_clock_e30_clkoff/on put_back_block seed=4300049 frame=320/500 hist=3 policy=0.6s elapsed=109s
[decide] 2026-11-20 18:33:42 ar2_clock_e30_clkoff/on put_back_block seed=4300049 frame=352/500 hist=3 policy=0.6s elapsed=119s
[closed-loop] 2026-11-20 18:33:45 done  ar2_clock_e30_clkoff/on put_back_block seed=4300049 success=True targets=354/500 reward=1.0 lift=0.12480819225311279  161s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_clock_e30_clkflat/onswap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_clkfreeze/onswap_blocks       50     1.00  [0.93,1.00]      1.00    1.00      586        -        -        -    0.6
ar2_clock_e30_clkoff/on put_back_block    50     0.82  [0.69,0.90]      1.00    0.82      387        -        -        -    0.6
ar2_clock_e30_clkoff/on swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts0.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6
ar2_clock_e30_ts1.5/on  swap_blocks       50     0.00  [0.00,0.07]      1.00    0.00     1000        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkfreeze/on  50     0       0      50        0  0.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_clkoff/on   50     0       0       0       50  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts0.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_clkflat/on vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_clkoff/on   50     0      50       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts0.5/on    50     0      50       0        0  0.000
  ar2_clock_e30_clkfreeze/on vs ar2_clock_e30_ts1.5/on    50     0      50       0        0  0.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts0.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_clkoff/on  vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000
  ar2_clock_e30_ts0.5/on   vs ar2_clock_e30_ts1.5/on    50     0       0       0       50  1.000

[summary] 300 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e21/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E21-off-put-s4.log):
```

[pool] 2026-11-21 02:03:58 exec A40-E21-off-put-s4 GPU 5 
[pool] 2026-11-21 02:04:00 A40-E21-off-put-s4: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-off-put-s4.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-off-put-s4.md
[queue5] 2026-11-21 02:34:11 A40-E21-off-put-s4: DONE  put_back_block/on n=50 lifted=50 centre=50 pressed=41 stage1=41 regrasp=41 returned=50 success=41 prog=0.88
```

## A40-E17-press_arprop-e20-s0 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e20-s0.log):
```
  press_arprop_e10/on      vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_arprop_e10/on      vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_arprop_e20/on      vs press_count_e10/on        46     0       4       0       42  0.125
  press_arprop_e20/on      vs press_count_e20/on        46     0       4       0       42  0.125
  press_arprop_e20/on      vs press_count_e30/on        46     1       3       6       36  0.508
  press_arprop_e20/on      vs press_v3c_e10/on          46     0       4       0       42  0.125
  press_arprop_e20/on      vs press_v3c_e20/on          46     0       4       3       39  1.000
  press_arprop_e20/on      vs press_v3c_e30/on          46     0       4       4       38  1.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 746 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_arprop-e20-s0.log):
```

[pool] 2026-11-21 02:12:04 exec A40-E17-press_arprop-e20-s0 GPU 4 
[pool] 2026-11-21 02:12:06 A40-E17-press_arprop-e20-s0: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e20-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e20-s0.md
[queue5] 2026-11-21 03:39:03 A40-E17-press_arprop-e20-s0: DONE  press_button/on n=46 pressed=46 n1_correct=21 n2_correct=14 confirmed=45 count_correct=4 success=4 prog=0.34
```

## A40-E17-press_arprop-e20-s1 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e20-s1.log):
```
  press_arprop_e10/on      vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_arprop_e10/on      vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_arprop_e20/on      vs press_count_e10/on        52     0       5       0       47  0.062
  press_arprop_e20/on      vs press_count_e20/on        52     0       5       0       47  0.062
  press_arprop_e20/on      vs press_count_e30/on        52     1       4       6       41  0.754
  press_arprop_e20/on      vs press_v3c_e10/on          52     0       5       0       47  0.062
  press_arprop_e20/on      vs press_v3c_e20/on          52     0       5       4       43  1.000
  press_arprop_e20/on      vs press_v3c_e30/on          52     0       5       5       42  1.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 752 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_arprop-e20-s1.log):
```

[pool] 2026-11-21 02:18:00 exec A40-E17-press_arprop-e20-s1 GPU 1 
[pool] 2026-11-21 02:18:02 A40-E17-press_arprop-e20-s1: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e20-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e20-s1.md
[queue5] 2026-11-21 03:49:39 A40-E17-press_arprop-e20-s1: DONE  press_button/on n=52 pressed=52 n1_correct=25 n2_correct=16 confirmed=51 count_correct=5 success=5 prog=0.35
```

## A40-E17-press_arprop-e20-s2 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e20-s2.log):
```
  press_arprop_e10/on      vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_arprop_e10/on      vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_arprop_e20/on      vs press_count_e10/on        59     0       5       0       54  0.062
  press_arprop_e20/on      vs press_count_e20/on        59     0       5       0       54  0.062
  press_arprop_e20/on      vs press_count_e30/on        59     1       4       6       48  0.754
  press_arprop_e20/on      vs press_v3c_e10/on          59     0       5       0       54  0.062
  press_arprop_e20/on      vs press_v3c_e20/on          59     0       5       4       50  1.000
  press_arprop_e20/on      vs press_v3c_e30/on          59     0       5       7       47  0.774
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 759 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_arprop-e20-s2.log):
```

[pool] 2026-11-21 02:22:52 exec A40-E17-press_arprop-e20-s2 GPU 3 
[pool] 2026-11-21 02:22:54 A40-E17-press_arprop-e20-s2: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e20-s2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e20-s2.md
[queue5] 2026-11-21 04:01:17 A40-E17-press_arprop-e20-s2: DONE  press_button/on n=59 pressed=59 n1_correct=30 n2_correct=18 confirmed=58 count_correct=5 success=5 prog=0.35
```

## A40-E17-press_arprop-e20-s3 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e20-s3.log):
```
  press_arprop_e10/on      vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_arprop_e10/on      vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_arprop_e20/on      vs press_count_e10/on        62     0       5       0       57  0.062
  press_arprop_e20/on      vs press_count_e20/on        62     0       5       0       57  0.062
  press_arprop_e20/on      vs press_count_e30/on        62     1       4       6       51  0.754
  press_arprop_e20/on      vs press_v3c_e10/on          62     0       5       0       57  0.062
  press_arprop_e20/on      vs press_v3c_e20/on          62     0       5       4       53  1.000
  press_arprop_e20/on      vs press_v3c_e30/on          62     0       5       8       49  0.581
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 762 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_arprop-e20-s3.log):
```

[pool] 2026-11-21 02:27:11 exec A40-E17-press_arprop-e20-s3 GPU 6 
[pool] 2026-11-21 02:27:13 A40-E17-press_arprop-e20-s3: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e20-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e20-s3.md
[queue5] 2026-11-21 04:05:43 A40-E17-press_arprop-e20-s3: DONE  press_button/on n=62 pressed=62 n1_correct=32 n2_correct=19 confirmed=61 count_correct=5 success=5 prog=0.35
```

## A40-E17-press_arprop-e20-s4 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e20-s4.log):
```
  press_arprop_e10/on      vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_arprop_e10/on      vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_arprop_e20/on      vs press_count_e10/on        57     0       5       0       52  0.062
  press_arprop_e20/on      vs press_count_e20/on        57     0       5       0       52  0.062
  press_arprop_e20/on      vs press_count_e30/on        57     1       4       6       46  0.754
  press_arprop_e20/on      vs press_v3c_e10/on          57     0       5       0       52  0.062
  press_arprop_e20/on      vs press_v3c_e20/on          57     0       5       4       48  1.000
  press_arprop_e20/on      vs press_v3c_e30/on          57     0       5       7       45  0.774
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 757 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_arprop-e20-s4.log):
```

[pool] 2026-11-21 02:35:13 exec A40-E17-press_arprop-e20-s4 GPU 5 
[pool] 2026-11-21 02:35:15 A40-E17-press_arprop-e20-s4: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e20-s4.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e20-s4.md
[queue5] 2026-11-21 03:56:10 A40-E17-press_arprop-e20-s4: DONE  press_button/on n=57 pressed=57 n1_correct=29 n2_correct=17 confirmed=56 count_correct=5 success=5 prog=0.35
```

## A40-E17-press_arprop-e20-s5 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e20-s5.log):
```
  press_arprop_e10/on      vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_arprop_e10/on      vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_arprop_e20/on      vs press_count_e10/on        64     0       5       0       59  0.062
  press_arprop_e20/on      vs press_count_e20/on        64     0       5       0       59  0.062
  press_arprop_e20/on      vs press_count_e30/on        64     1       4       6       53  0.754
  press_arprop_e20/on      vs press_v3c_e10/on          64     0       5       0       59  0.062
  press_arprop_e20/on      vs press_v3c_e20/on          64     0       5       4       55  1.000
  press_arprop_e20/on      vs press_v3c_e30/on          64     0       5       8       51  0.581
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 764 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_arprop-e20-s5.log):
```

[pool] 2026-11-21 02:35:13 exec A40-E17-press_arprop-e20-s5 GPU 7 
[pool] 2026-11-21 02:35:15 A40-E17-press_arprop-e20-s5: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e20-s5.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e20-s5.md
[queue5] 2026-11-21 04:09:53 A40-E17-press_arprop-e20-s5: DONE  press_button/on n=64 pressed=64 n1_correct=34 n2_correct=19 confirmed=62 count_correct=5 success=5 prog=0.35
```

## A40-E17-press_arprop-e20-s6 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e20-s6.log):
```
  press_arprop_e20/on      vs press_v3c_e20/on          90     0       8       4       78  0.388
  press_arprop_e20/on      vs press_v3c_e30/on          90     1       7      14       68  0.189
  press_arprop_e30/on      vs press_count_e10/on        10     0       0       0       10  1.000
  press_arprop_e30/on      vs press_count_e20/on        10     0       0       0       10  1.000
  press_arprop_e30/on      vs press_count_e30/on        10     0       0       2        8  0.500
  press_arprop_e30/on      vs press_v3c_e10/on          10     0       0       0       10  1.000
  press_arprop_e30/on      vs press_v3c_e20/on          10     0       0       0       10  1.000
  press_arprop_e30/on      vs press_v3c_e30/on          10     0       0       0       10  1.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 800 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_arprop-e20-s6.log):
```

[pool] 2026-11-21 03:38:35 exec A40-E17-press_arprop-e20-s6 GPU 4 
[pool] 2026-11-21 03:38:37 A40-E17-press_arprop-e20-s6: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e20-s6.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e20-s6.md
[queue5] 2026-11-21 05:04:27 A40-E17-press_arprop-e20-s6: DONE  press_button/on n=90 pressed=90 n1_correct=51 n2_correct=25 confirmed=88 count_correct=8 success=8 prog=0.37
```

## A40-E17-press_arprop-e20-s7 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e20-s7.log):
```
  press_arprop_e20/on      vs press_v3c_e20/on          97     0       8       5       84  0.581
  press_arprop_e20/on      vs press_v3c_e30/on          97     1       7      15       74  0.134
  press_arprop_e30/on      vs press_count_e10/on        15     0       0       0       15  1.000
  press_arprop_e30/on      vs press_count_e20/on        15     0       0       0       15  1.000
  press_arprop_e30/on      vs press_count_e30/on        15     0       0       2       13  0.500
  press_arprop_e30/on      vs press_v3c_e10/on          15     0       0       0       15  1.000
  press_arprop_e30/on      vs press_v3c_e20/on          15     0       0       0       15  1.000
  press_arprop_e30/on      vs press_v3c_e30/on          15     0       0       0       15  1.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 812 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_arprop-e20-s7.log):
```

[pool] 2026-11-21 03:48:47 exec A40-E17-press_arprop-e20-s7 GPU 1 
[pool] 2026-11-21 03:48:49 A40-E17-press_arprop-e20-s7: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e20-s7.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e20-s7.md
[queue5] 2026-11-21 05:25:03 A40-E17-press_arprop-e20-s7: DONE  press_button/on n=97 pressed=97 n1_correct=55 n2_correct=25 confirmed=95 count_correct=8 success=8 prog=0.36
```

## A40-E17-press_arprop-e20-s8 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e20-s8.log):
```
  press_arprop_e20/on      vs press_v3c_e20/on         100     0       8       5       87  0.581
  press_arprop_e20/on      vs press_v3c_e30/on         100     1       7      16       76  0.093
  press_arprop_e30/on      vs press_count_e10/on        18     0       0       0       18  1.000
  press_arprop_e30/on      vs press_count_e20/on        18     0       0       0       18  1.000
  press_arprop_e30/on      vs press_count_e30/on        18     0       0       3       15  0.250
  press_arprop_e30/on      vs press_v3c_e10/on          18     0       0       0       18  1.000
  press_arprop_e30/on      vs press_v3c_e20/on          18     0       0       0       18  1.000
  press_arprop_e30/on      vs press_v3c_e30/on          18     0       0       0       18  1.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 818 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_arprop-e20-s8.log):
```

[pool] 2026-11-21 03:55:13 exec A40-E17-press_arprop-e20-s8 GPU 5 
[pool] 2026-11-21 03:55:15 A40-E17-press_arprop-e20-s8: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e20-s8.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e20-s8.md
[queue5] 2026-11-21 05:34:48 A40-E17-press_arprop-e20-s8: DONE  press_button/on n=100 pressed=100 n1_correct=56 n2_correct=25 confirmed=98 count_correct=8 success=8 prog=0.36
```

## A40-E17-press_arprop-e20-s9 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e20-s9.log):
```
  press_arprop_e20/on      vs press_v3c_e20/on          99     0       8       5       86  0.581
  press_arprop_e20/on      vs press_v3c_e30/on          99     1       7      15       76  0.134
  press_arprop_e30/on      vs press_count_e10/on        18     0       0       0       18  1.000
  press_arprop_e30/on      vs press_count_e20/on        18     0       0       0       18  1.000
  press_arprop_e30/on      vs press_count_e30/on        18     0       0       3       15  0.250
  press_arprop_e30/on      vs press_v3c_e10/on          18     0       0       0       18  1.000
  press_arprop_e30/on      vs press_v3c_e20/on          18     0       0       0       18  1.000
  press_arprop_e30/on      vs press_v3c_e30/on          18     0       0       0       18  1.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 817 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_arprop-e20-s9.log):
```

[pool] 2026-11-21 04:00:03 exec A40-E17-press_arprop-e20-s9 GPU 3 
[pool] 2026-11-21 04:00:05 A40-E17-press_arprop-e20-s9: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e20-s9.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e20-s9.md
[queue5] 2026-11-21 05:32:09 A40-E17-press_arprop-e20-s9: DONE  press_button/on n=99 pressed=99 n1_correct=56 n2_correct=25 confirmed=97 count_correct=8 success=8 prog=0.36
```

## A40-E17-press_arprop-e30-s0 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e30-s0.log):
```
  press_arprop_e20/on      vs press_v3c_e20/on         100     0       8       5       87  0.581
  press_arprop_e20/on      vs press_v3c_e30/on         100     1       7      16       76  0.093
  press_arprop_e30/on      vs press_count_e10/on        26     0       0       0       26  1.000
  press_arprop_e30/on      vs press_count_e20/on        26     0       0       0       26  1.000
  press_arprop_e30/on      vs press_count_e30/on        26     0       0       3       23  0.250
  press_arprop_e30/on      vs press_v3c_e10/on          26     0       0       0       26  1.000
  press_arprop_e30/on      vs press_v3c_e20/on          26     0       0       0       26  1.000
  press_arprop_e30/on      vs press_v3c_e30/on          26     0       0       1       25  1.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 826 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_arprop-e30-s0.log):
```

[pool] 2026-11-21 04:04:52 exec A40-E17-press_arprop-e30-s0 GPU 6 
[pool] 2026-11-21 04:04:54 A40-E17-press_arprop-e30-s0: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e30-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e30-s0.md
[queue5] 2026-11-21 05:42:30 A40-E17-press_arprop-e30-s0: DONE  press_button/on n=26 pressed=26 n1_correct=6 n2_correct=2 confirmed=26 count_correct=0 success=0 prog=0.25
```

## A40-E17-press_arprop-e30-s1 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e30-s1.log):
```
  press_arprop_e20/on      vs press_v3c_e20/on         100     0       8       5       87  0.581
  press_arprop_e20/on      vs press_v3c_e30/on         100     1       7      16       76  0.093
  press_arprop_e30/on      vs press_count_e10/on        24     0       0       0       24  1.000
  press_arprop_e30/on      vs press_count_e20/on        24     0       0       0       24  1.000
  press_arprop_e30/on      vs press_count_e30/on        24     0       0       3       21  0.250
  press_arprop_e30/on      vs press_v3c_e10/on          24     0       0       0       24  1.000
  press_arprop_e30/on      vs press_v3c_e20/on          24     0       0       0       24  1.000
  press_arprop_e30/on      vs press_v3c_e30/on          24     0       0       1       23  1.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 824 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_arprop-e30-s1.log):
```

[pool] 2026-11-21 04:08:39 exec A40-E17-press_arprop-e30-s1 GPU 7 
[pool] 2026-11-21 04:08:41 A40-E17-press_arprop-e30-s1: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e30-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e30-s1.md
[queue5] 2026-11-21 05:41:02 A40-E17-press_arprop-e30-s1: DONE  press_button/on n=24 pressed=24 n1_correct=6 n2_correct=1 confirmed=24 count_correct=0 success=0 prog=0.25
```

## A40-E17-press_arprop-e30-s2 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e30-s2.log):
```
  press_arprop_e20/on      vs press_v3c_e20/on         100     0       8       5       87  0.581
  press_arprop_e20/on      vs press_v3c_e30/on         100     1       7      16       76  0.093
  press_arprop_e30/on      vs press_count_e10/on        60     0       1       0       59  1.000
  press_arprop_e30/on      vs press_count_e20/on        60     0       1       0       59  1.000
  press_arprop_e30/on      vs press_count_e30/on        60     0       1       8       51  0.039
  press_arprop_e30/on      vs press_v3c_e10/on          60     0       1       0       59  1.000
  press_arprop_e30/on      vs press_v3c_e20/on          60     0       1       3       56  0.625
  press_arprop_e30/on      vs press_v3c_e30/on          60     0       1       6       53  0.125
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 860 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_arprop-e30-s2.log):
```

[pool] 2026-11-21 05:02:22 exec A40-E17-press_arprop-e30-s2 GPU 4 
[pool] 2026-11-21 05:02:24 A40-E17-press_arprop-e30-s2: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e30-s2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e30-s2.md
[queue5] 2026-11-21 06:36:37 A40-E17-press_arprop-e30-s2: DONE  press_button/on n=60 pressed=60 n1_correct=13 n2_correct=10 confirmed=60 count_correct=1 success=1 prog=0.25
```

## A40-E17-press_arprop-e30-s3 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e30-s3.log):
```
  press_arprop_e20/on      vs press_v3c_e20/on         100     0       8       5       87  0.581
  press_arprop_e20/on      vs press_v3c_e30/on         100     1       7      16       76  0.093
  press_arprop_e30/on      vs press_count_e10/on        72     0       2       0       70  0.500
  press_arprop_e30/on      vs press_count_e20/on        72     0       2       0       70  0.500
  press_arprop_e30/on      vs press_count_e30/on        72     0       2       8       62  0.109
  press_arprop_e30/on      vs press_v3c_e10/on          72     0       2       0       70  0.500
  press_arprop_e30/on      vs press_v3c_e20/on          72     0       2       4       66  0.688
  press_arprop_e30/on      vs press_v3c_e30/on          72     1       1       8       62  0.039
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 872 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_arprop-e30-s3.log):
```

[pool] 2026-11-21 05:22:45 exec A40-E17-press_arprop-e30-s3 GPU 1 
[pool] 2026-11-21 05:22:47 A40-E17-press_arprop-e30-s3: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e30-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e30-s3.md
[queue5] 2026-11-21 06:53:38 A40-E17-press_arprop-e30-s3: DONE  press_button/on n=72 pressed=72 n1_correct=17 n2_correct=12 confirmed=72 count_correct=2 success=2 prog=0.26
```

## A40-E17-press_arprop-e30-s4 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e30-s4.log):
```
  press_arprop_e20/on      vs press_v3c_e20/on         100     0       8       5       87  0.581
  press_arprop_e20/on      vs press_v3c_e30/on         100     1       7      16       76  0.093
  press_arprop_e30/on      vs press_count_e10/on        80     0       2       0       78  0.500
  press_arprop_e30/on      vs press_count_e20/on        80     0       2       0       78  0.500
  press_arprop_e30/on      vs press_count_e30/on        80     0       2       8       70  0.109
  press_arprop_e30/on      vs press_v3c_e10/on          80     0       2       1       77  1.000
  press_arprop_e30/on      vs press_v3c_e20/on          80     0       2       4       74  0.688
  press_arprop_e30/on      vs press_v3c_e30/on          80     1       1      10       68  0.012
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 880 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_arprop-e30-s4.log):
```

[pool] 2026-11-21 05:29:42 exec A40-E17-press_arprop-e30-s4 GPU 3 
[pool] 2026-11-21 05:29:44 A40-E17-press_arprop-e30-s4: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e30-s4.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e30-s4.md
[queue5] 2026-11-21 07:07:54 A40-E17-press_arprop-e30-s4: DONE  press_button/on n=80 pressed=80 n1_correct=18 n2_correct=13 confirmed=80 count_correct=2 success=2 prog=0.26
```

## A40-E17-press_arprop-e30-s5 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e30-s5.log):
```
  press_arprop_e20/on      vs press_v3c_e20/on         100     0       8       5       87  0.581
  press_arprop_e20/on      vs press_v3c_e30/on         100     1       7      16       76  0.093
  press_arprop_e30/on      vs press_count_e10/on        79     0       2       0       77  0.500
  press_arprop_e30/on      vs press_count_e20/on        79     0       2       0       77  0.500
  press_arprop_e30/on      vs press_count_e30/on        79     0       2       8       69  0.109
  press_arprop_e30/on      vs press_v3c_e10/on          79     0       2       1       76  1.000
  press_arprop_e30/on      vs press_v3c_e20/on          79     0       2       4       73  0.688
  press_arprop_e30/on      vs press_v3c_e30/on          79     1       1       9       68  0.021
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 879 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_arprop-e30-s5.log):
```

[pool] 2026-11-21 05:32:26 exec A40-E17-press_arprop-e30-s5 GPU 5 
[pool] 2026-11-21 05:32:28 A40-E17-press_arprop-e30-s5: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e30-s5.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e30-s5.md
[queue5] 2026-11-21 07:06:53 A40-E17-press_arprop-e30-s5: DONE  press_button/on n=79 pressed=79 n1_correct=18 n2_correct=13 confirmed=79 count_correct=2 success=2 prog=0.26
```

## A40-E17-press_arprop-e30-s6 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e30-s6.log):
```
  press_arprop_e20/on      vs press_v3c_e20/on         100     0       8       5       87  0.581
  press_arprop_e20/on      vs press_v3c_e30/on         100     1       7      16       76  0.093
  press_arprop_e30/on      vs press_count_e10/on        82     0       2       0       80  0.500
  press_arprop_e30/on      vs press_count_e20/on        82     0       2       0       80  0.500
  press_arprop_e30/on      vs press_count_e30/on        82     0       2       8       72  0.109
  press_arprop_e30/on      vs press_v3c_e10/on          82     0       2       1       79  1.000
  press_arprop_e30/on      vs press_v3c_e20/on          82     0       2       4       76  0.688
  press_arprop_e30/on      vs press_v3c_e30/on          82     1       1      12       68  0.003
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 882 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_arprop-e30-s6.log):
```

[pool] 2026-11-21 05:41:34 exec A40-E17-press_arprop-e30-s6 GPU 7 
[pool] 2026-11-21 05:41:35 A40-E17-press_arprop-e30-s6: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e30-s6.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e30-s6.md
[queue5] 2026-11-21 07:09:53 A40-E17-press_arprop-e30-s6: DONE  press_button/on n=82 pressed=82 n1_correct=18 n2_correct=13 confirmed=82 count_correct=2 success=2 prog=0.26
```

## A40-E17-press_arprop-e30-s7 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e30-s7.log):
```
  press_arprop_e20/on      vs press_v3c_e20/on         100     0       8       5       87  0.581
  press_arprop_e20/on      vs press_v3c_e30/on         100     1       7      16       76  0.093
  press_arprop_e30/on      vs press_count_e10/on        86     0       2       1       83  1.000
  press_arprop_e30/on      vs press_count_e20/on        86     0       2       0       84  0.500
  press_arprop_e30/on      vs press_count_e30/on        86     0       2      10       74  0.039
  press_arprop_e30/on      vs press_v3c_e10/on          86     0       2       1       83  1.000
  press_arprop_e30/on      vs press_v3c_e20/on          86     0       2       4       80  0.688
  press_arprop_e30/on      vs press_v3c_e30/on          86     1       1      13       71  0.002
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 886 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_arprop-e30-s7.log):
```

[pool] 2026-11-21 05:42:38 exec A40-E17-press_arprop-e30-s7 GPU 6 
[pool] 2026-11-21 05:42:40 A40-E17-press_arprop-e30-s7: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e30-s7.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e30-s7.md
[queue5] 2026-11-21 07:21:26 A40-E17-press_arprop-e30-s7: DONE  press_button/on n=86 pressed=86 n1_correct=18 n2_correct=13 confirmed=86 count_correct=2 success=2 prog=0.26
```

## A40-E17-press_arprop-e30-s8 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e30-s8.log):
```
  press_arprop_e20/on      vs press_v3c_e20/on         100     0       8       5       87  0.581
  press_arprop_e20/on      vs press_v3c_e30/on         100     1       7      16       76  0.093
  press_arprop_e30/on      vs press_count_e10/on        98     0       2       1       95  1.000
  press_arprop_e30/on      vs press_count_e20/on        98     0       2       0       96  0.500
  press_arprop_e30/on      vs press_count_e30/on        98     0       2      13       83  0.007
  press_arprop_e30/on      vs press_v3c_e10/on          98     0       2       1       95  1.000
  press_arprop_e30/on      vs press_v3c_e20/on          98     0       2       5       91  0.453
  press_arprop_e30/on      vs press_v3c_e30/on          98     1       1      16       80  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 922 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_arprop-e30-s8.log):
```

[pool] 2026-11-21 06:35:12 exec A40-E17-press_arprop-e30-s8 GPU 4 
[pool] 2026-11-21 06:35:14 A40-E17-press_arprop-e30-s8: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e30-s8.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e30-s8.md
[queue5] 2026-11-21 08:15:05 A40-E17-press_arprop-e30-s8: DONE  press_button/on n=98 pressed=98 n1_correct=20 n2_correct=16 confirmed=98 count_correct=2 success=2 prog=0.25
```

## A40-E17-press_arprop-e30-s9 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e30-s9.log):
```
  press_arprop_e20/on      vs press_v3c_e20/on         100     0       8       5       87  0.581
  press_arprop_e20/on      vs press_v3c_e30/on         100     1       7      16       76  0.093
  press_arprop_e30/on      vs press_count_e10/on       100     0       2       1       97  1.000
  press_arprop_e30/on      vs press_count_e20/on       100     0       2       0       98  0.500
  press_arprop_e30/on      vs press_count_e30/on       100     0       2      13       85  0.007
  press_arprop_e30/on      vs press_v3c_e10/on         100     0       2       1       97  1.000
  press_arprop_e30/on      vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_arprop_e30/on      vs press_v3c_e30/on         100     1       1      16       82  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 931 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_arprop-e30-s9.log):
```

[pool] 2026-11-21 06:51:51 exec A40-E17-press_arprop-e30-s9 GPU 1 
[pool] 2026-11-21 06:51:53 A40-E17-press_arprop-e30-s9: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_arprop-e30-s9.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e30-s9.md
[queue5] 2026-11-21 08:28:22 A40-E17-press_arprop-e30-s9: DONE  press_button/on n=100 pressed=100 n1_correct=20 n2_correct=17 confirmed=100 count_correct=2 success=2 prog=0.25
```

## A40-E17-press_ar-e30-s0 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_ar-e30-s0.log):
```
  press_arprop_e20/on      vs press_v3c_e20/on         100     0       8       5       87  0.581
  press_arprop_e20/on      vs press_v3c_e30/on         100     1       7      16       76  0.093
  press_arprop_e30/on      vs press_count_e10/on       100     0       2       1       97  1.000
  press_arprop_e30/on      vs press_count_e20/on       100     0       2       0       98  0.500
  press_arprop_e30/on      vs press_count_e30/on       100     0       2      13       85  0.007
  press_arprop_e30/on      vs press_v3c_e10/on         100     0       2       1       97  1.000
  press_arprop_e30/on      vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_arprop_e30/on      vs press_v3c_e30/on         100     1       1      16       82  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 941 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_ar-e30-s0.log):
```

[pool] 2026-11-21 07:05:14 exec A40-E17-press_ar-e30-s0 GPU 5 
[pool] 2026-11-21 07:05:16 A40-E17-press_ar-e30-s0: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_ar-e30-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_ar-e30-s0.md
[queue5] 2026-11-21 08:42:02 A40-E17-press_ar-e30-s0: DONE  press_button/on n=41 pressed=41 n1_correct=6 n2_correct=5 confirmed=16 count_correct=2 success=2 prog=0.26
```

## A40-E17-press_ar-e30-s1 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_ar-e30-s1.log):
```
  press_arprop_e20/on      vs press_v3c_e20/on         100     0       8       5       87  0.581
  press_arprop_e20/on      vs press_v3c_e30/on         100     1       7      16       76  0.093
  press_arprop_e30/on      vs press_count_e10/on       100     0       2       1       97  1.000
  press_arprop_e30/on      vs press_count_e20/on       100     0       2       0       98  0.500
  press_arprop_e30/on      vs press_count_e30/on       100     0       2      13       85  0.007
  press_arprop_e30/on      vs press_v3c_e10/on         100     0       2       1       97  1.000
  press_arprop_e30/on      vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_arprop_e30/on      vs press_v3c_e30/on         100     1       1      16       82  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 944 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_ar-e30-s1.log):
```

[pool] 2026-11-21 07:05:46 exec A40-E17-press_ar-e30-s1 GPU 3 
[pool] 2026-11-21 07:05:48 A40-E17-press_ar-e30-s1: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_ar-e30-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_ar-e30-s1.md
[queue5] 2026-11-21 08:44:23 A40-E17-press_ar-e30-s1: DONE  press_button/on n=44 pressed=44 n1_correct=7 n2_correct=5 confirmed=17 count_correct=2 success=2 prog=0.26
```

## A40-E17-press_ar-e30-s2 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_ar-e30-s2.log):
```
  press_arprop_e20/on      vs press_v3c_e20/on         100     0       8       5       87  0.581
  press_arprop_e20/on      vs press_v3c_e30/on         100     1       7      16       76  0.093
  press_arprop_e30/on      vs press_count_e10/on       100     0       2       1       97  1.000
  press_arprop_e30/on      vs press_count_e20/on       100     0       2       0       98  0.500
  press_arprop_e30/on      vs press_count_e30/on       100     0       2      13       85  0.007
  press_arprop_e30/on      vs press_v3c_e10/on         100     0       2       1       97  1.000
  press_arprop_e30/on      vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_arprop_e30/on      vs press_v3c_e30/on         100     1       1      16       82  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 934 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_ar-e30-s2.log):
```

[pool] 2026-11-21 07:07:54 exec A40-E17-press_ar-e30-s2 GPU 7 
[pool] 2026-11-21 07:07:56 A40-E17-press_ar-e30-s2: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_ar-e30-s2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_ar-e30-s2.md
[queue5] 2026-11-21 08:31:59 A40-E17-press_ar-e30-s2: DONE  press_button/on n=34 pressed=34 n1_correct=5 n2_correct=4 confirmed=12 count_correct=1 success=1 prog=0.25
```

## A40-E17-press_ar-e30-s3 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_ar-e30-s3.log):
```
  press_arprop_e20/on      vs press_v3c_e20/on         100     0       8       5       87  0.581
  press_arprop_e20/on      vs press_v3c_e30/on         100     1       7      16       76  0.093
  press_arprop_e30/on      vs press_count_e10/on       100     0       2       1       97  1.000
  press_arprop_e30/on      vs press_count_e20/on       100     0       2       0       98  0.500
  press_arprop_e30/on      vs press_count_e30/on       100     0       2      13       85  0.007
  press_arprop_e30/on      vs press_v3c_e10/on         100     0       2       1       97  1.000
  press_arprop_e30/on      vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_arprop_e30/on      vs press_v3c_e30/on         100     1       1      16       82  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 947 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_ar-e30-s3.log):
```

[pool] 2026-11-21 07:19:11 exec A40-E17-press_ar-e30-s3 GPU 6 
[pool] 2026-11-21 07:19:13 A40-E17-press_ar-e30-s3: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_ar-e30-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_ar-e30-s3.md
[queue5] 2026-11-21 08:52:37 A40-E17-press_ar-e30-s3: DONE  press_button/on n=47 pressed=47 n1_correct=7 n2_correct=5 confirmed=17 count_correct=2 success=2 prog=0.26
```

## A40-E17-press_ar-e30-s4 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_ar-e30-s4.log):
```
  press_arprop_e20/on      vs press_v3c_e20/on         100     0       8       5       87  0.581
  press_arprop_e20/on      vs press_v3c_e30/on         100     1       7      16       76  0.093
  press_arprop_e30/on      vs press_count_e10/on       100     0       2       1       97  1.000
  press_arprop_e30/on      vs press_count_e20/on       100     0       2       0       98  0.500
  press_arprop_e30/on      vs press_count_e30/on       100     0       2      13       85  0.007
  press_arprop_e30/on      vs press_v3c_e10/on         100     0       2       1       97  1.000
  press_arprop_e30/on      vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_arprop_e30/on      vs press_v3c_e30/on         100     1       1      16       82  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 984 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_ar-e30-s4.log):
```

[pool] 2026-11-21 08:12:19 exec A40-E17-press_ar-e30-s4 GPU 4 
[pool] 2026-11-21 08:12:21 A40-E17-press_ar-e30-s4: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_ar-e30-s4.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_ar-e30-s4.md
[queue5] 2026-11-21 09:49:48 A40-E17-press_ar-e30-s4: DONE  press_button/on n=84 pressed=84 n1_correct=10 n2_correct=10 confirmed=31 count_correct=2 success=2 prog=0.24
```

## A40-E17-press_ar-e30-s5 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_ar-e30-s5.log):
```
  press_arprop_e20/on      vs press_v3c_e20/on         100     0       8       5       87  0.581
  press_arprop_e20/on      vs press_v3c_e30/on         100     1       7      16       76  0.093
  press_arprop_e30/on      vs press_count_e10/on       100     0       2       1       97  1.000
  press_arprop_e30/on      vs press_count_e20/on       100     0       2       0       98  0.500
  press_arprop_e30/on      vs press_count_e30/on       100     0       2      13       85  0.007
  press_arprop_e30/on      vs press_v3c_e10/on         100     0       2       1       97  1.000
  press_arprop_e30/on      vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_arprop_e30/on      vs press_v3c_e30/on         100     1       1      16       82  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 990 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_ar-e30-s5.log):
```

[pool] 2026-11-21 08:25:45 exec A40-E17-press_ar-e30-s5 GPU 1 
[pool] 2026-11-21 08:25:47 A40-E17-press_ar-e30-s5: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_ar-e30-s5.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_ar-e30-s5.md
[queue5] 2026-11-21 10:00:05 A40-E17-press_ar-e30-s5: DONE  press_button/on n=90 pressed=90 n1_correct=10 n2_correct=10 confirmed=32 count_correct=2 success=2 prog=0.24
```

## A40-E17-press_ar-e30-s6 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_ar-e30-s6.log):
```
  press_arprop_e20/on      vs press_v3c_e20/on         100     0       8       5       87  0.581
  press_arprop_e20/on      vs press_v3c_e30/on         100     1       7      16       76  0.093
  press_arprop_e30/on      vs press_count_e10/on       100     0       2       1       97  1.000
  press_arprop_e30/on      vs press_count_e20/on       100     0       2       0       98  0.500
  press_arprop_e30/on      vs press_count_e30/on       100     0       2      13       85  0.007
  press_arprop_e30/on      vs press_v3c_e10/on         100     0       2       1       97  1.000
  press_arprop_e30/on      vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_arprop_e30/on      vs press_v3c_e30/on         100     1       1      16       82  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 993 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_ar-e30-s6.log):
```

[pool] 2026-11-21 08:32:10 exec A40-E17-press_ar-e30-s6 GPU 7 
[pool] 2026-11-21 08:32:12 A40-E17-press_ar-e30-s6: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_ar-e30-s6.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_ar-e30-s6.md
[queue5] 2026-11-21 10:04:48 A40-E17-press_ar-e30-s6: DONE  press_button/on n=93 pressed=93 n1_correct=11 n2_correct=10 confirmed=33 count_correct=2 success=2 prog=0.24
```

## A40-E17-press_ar-e30-s7 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_ar-e30-s7.log):
```
  press_arprop_e30/on      vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_arprop_e30/on      vs press_v3c_e30/on         100     1       1      16       82  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_fast_e10/on          3     0       0       0        3  1.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_fast_e10/on          3     0       0       0        3  1.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on          3     0       0       0        3  1.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_v3c_e10/on           3     0       0       0        3  1.000
  press_fast_e10/on        vs press_v3c_e20/on           3     0       0       0        3  1.000
  press_fast_e10/on        vs press_v3c_e30/on           3     0       0       0        3  1.000
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1000 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_ar-e30-s7.log):
```

[pool] 2026-11-21 08:41:48 exec A40-E17-press_ar-e30-s7 GPU 5 
[pool] 2026-11-21 08:41:50 A40-E17-press_ar-e30-s7: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_ar-e30-s7.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_ar-e30-s7.md
[queue5] 2026-11-21 10:16:57 A40-E17-press_ar-e30-s7: DONE  press_button/on n=97 pressed=97 n1_correct=12 n2_correct=10 confirmed=34 count_correct=2 success=2 prog=0.24
```

## A40-E17-press_ar-e30-s8 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_ar-e30-s8.log):
```
  press_arprop_e30/on      vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_arprop_e30/on      vs press_v3c_e30/on         100     1       1      16       82  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_fast_e10/on          4     0       0       0        4  1.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_fast_e10/on          4     0       0       0        4  1.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on          4     0       0       0        4  1.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_v3c_e10/on           4     0       0       0        4  1.000
  press_fast_e10/on        vs press_v3c_e20/on           4     0       0       0        4  1.000
  press_fast_e10/on        vs press_v3c_e30/on           4     0       0       0        4  1.000
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1003 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_ar-e30-s8.log):
```

[pool] 2026-11-21 08:43:56 exec A40-E17-press_ar-e30-s8 GPU 3 
[pool] 2026-11-21 08:43:58 A40-E17-press_ar-e30-s8: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_ar-e30-s8.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_ar-e30-s8.md
[queue5] 2026-11-21 10:21:55 A40-E17-press_ar-e30-s8: DONE  press_button/on n=99 pressed=99 n1_correct=12 n2_correct=10 confirmed=34 count_correct=2 success=2 prog=0.24
```

## A40-E17-press_ar-e30-s9 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_ar-e30-s9.log):
```
  press_arprop_e30/on      vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_arprop_e30/on      vs press_v3c_e30/on         100     1       1      16       82  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_fast_e10/on          7     0       0       0        7  1.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_fast_e10/on          7     0       0       0        7  1.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on          7     0       2       0        5  0.500
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_v3c_e10/on           7     0       0       0        7  1.000
  press_fast_e10/on        vs press_v3c_e20/on           7     0       0       0        7  1.000
  press_fast_e10/on        vs press_v3c_e30/on           7     0       0       0        7  1.000
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1007 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_ar-e30-s9.log):
```

[pool] 2026-11-21 08:51:58 exec A40-E17-press_ar-e30-s9 GPU 6 
[pool] 2026-11-21 08:52:00 A40-E17-press_ar-e30-s9: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_ar-e30-s9.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_ar-e30-s9.md
[queue5] 2026-11-21 10:29:18 A40-E17-press_ar-e30-s9: DONE  press_button/on n=100 pressed=100 n1_correct=12 n2_correct=10 confirmed=34 count_correct=2 success=2 prog=0.24
```

## A40-E17-press_fast-e10-s0 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e10-s0.log):
```
  press_arprop_e30/on      vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_arprop_e30/on      vs press_v3c_e30/on         100     1       1      16       82  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_fast_e10/on         49     0       0       0       49  1.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_fast_e10/on         49     0       0       0       49  1.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on         49     0       7       0       42  0.016
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_v3c_e10/on          49     0       0       0       49  1.000
  press_fast_e10/on        vs press_v3c_e20/on          49     0       0       3       46  0.250
  press_fast_e10/on        vs press_v3c_e30/on          49     0       0       5       44  0.062
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1049 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e10-s0.log):
```

[pool] 2026-11-21 09:47:46 exec A40-E17-press_fast-e10-s0 GPU 4 
[pool] 2026-11-21 09:47:48 A40-E17-press_fast-e10-s0: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e10-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e10-s0.md
[queue5] 2026-11-21 11:27:03 A40-E17-press_fast-e10-s0: DONE  press_button/on n=49 pressed=49 n1_correct=3 n2_correct=9 confirmed=46 count_correct=0 success=0 prog=0.21
```

## A40-E17-press_fast-e10-s1 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e10-s1.log):
```
  press_arprop_e30/on      vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_arprop_e30/on      vs press_v3c_e30/on         100     1       1      16       82  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_fast_e10/on         53     0       0       0       53  1.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_fast_e10/on         53     0       0       0       53  1.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on         53     0       7       0       46  0.016
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_v3c_e10/on          53     0       0       0       53  1.000
  press_fast_e10/on        vs press_v3c_e20/on          53     0       0       3       50  0.250
  press_fast_e10/on        vs press_v3c_e30/on          53     0       0       5       48  0.062
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1053 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e10-s1.log):
```

[pool] 2026-11-21 09:57:57 exec A40-E17-press_fast-e10-s1 GPU 1 
[pool] 2026-11-21 09:57:59 A40-E17-press_fast-e10-s1: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e10-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e10-s1.md
[queue5] 2026-11-21 11:32:33 A40-E17-press_fast-e10-s1: DONE  press_button/on n=53 pressed=53 n1_correct=3 n2_correct=9 confirmed=50 count_correct=0 success=0 prog=0.21
```

## A40-E17-press_fast-e10-s2 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e10-s2.log):
```
  press_arprop_e30/on      vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_arprop_e30/on      vs press_v3c_e30/on         100     1       1      16       82  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_fast_e10/on         57     0       0       0       57  1.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_fast_e10/on         57     0       0       0       57  1.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on         57     0       7       0       50  0.016
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_v3c_e10/on          57     0       0       0       57  1.000
  press_fast_e10/on        vs press_v3c_e20/on          57     0       0       4       53  0.125
  press_fast_e10/on        vs press_v3c_e30/on          57     0       0       6       51  0.031
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1057 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e10-s2.log):
```

[pool] 2026-11-21 10:02:14 exec A40-E17-press_fast-e10-s2 GPU 7 
[pool] 2026-11-21 10:02:16 A40-E17-press_fast-e10-s2: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e10-s2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e10-s2.md
[queue5] 2026-11-21 11:39:50 A40-E17-press_fast-e10-s2: DONE  press_button/on n=57 pressed=57 n1_correct=3 n2_correct=9 confirmed=54 count_correct=0 success=0 prog=0.21
```

## A40-E17-press_fast-e10-s3 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e10-s3.log):
```
  press_arprop_e30/on      vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_arprop_e30/on      vs press_v3c_e30/on         100     1       1      16       82  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_fast_e10/on         64     0       0       0       64  1.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_fast_e10/on         64     0       0       0       64  1.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on         64     0       7       0       57  0.016
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_v3c_e10/on          64     0       0       0       64  1.000
  press_fast_e10/on        vs press_v3c_e20/on          64     0       0       4       60  0.125
  press_fast_e10/on        vs press_v3c_e30/on          64     0       0       7       57  0.016
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1064 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e10-s3.log):
```

[pool] 2026-11-21 10:14:34 exec A40-E17-press_fast-e10-s3 GPU 5 
[pool] 2026-11-21 10:14:36 A40-E17-press_fast-e10-s3: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e10-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e10-s3.md
[queue5] 2026-11-21 11:49:42 A40-E17-press_fast-e10-s3: DONE  press_button/on n=64 pressed=64 n1_correct=3 n2_correct=9 confirmed=60 count_correct=0 success=0 prog=0.21
```

## A40-E17-press_fast-e10-s4 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e10-s4.log):
```
  press_arprop_e30/on      vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_arprop_e30/on      vs press_v3c_e30/on         100     1       1      16       82  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_fast_e10/on         70     0       0       0       70  1.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_fast_e10/on         70     0       0       0       70  1.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on         70     0       7       0       63  0.016
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_v3c_e10/on          70     0       0       0       70  1.000
  press_fast_e10/on        vs press_v3c_e20/on          70     0       0       4       66  0.125
  press_fast_e10/on        vs press_v3c_e30/on          70     0       0       9       61  0.004
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1070 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e10-s4.log):
```

[pool] 2026-11-21 10:19:25 exec A40-E17-press_fast-e10-s4 GPU 3 
[pool] 2026-11-21 10:19:27 A40-E17-press_fast-e10-s4: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e10-s4.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e10-s4.md
[queue5] 2026-11-21 11:58:23 A40-E17-press_fast-e10-s4: DONE  press_button/on n=70 pressed=70 n1_correct=3 n2_correct=10 confirmed=65 count_correct=0 success=0 prog=0.21
```

## A40-E17-press_fast-e10-s5 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e10-s5.log):
```
  press_arprop_e30/on      vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_arprop_e30/on      vs press_v3c_e30/on         100     1       1      16       82  0.000
  press_count_e10/on       vs press_count_e20/on       100     0       1       0       99  1.000
  press_count_e10/on       vs press_count_e30/on       100     1       0      12       87  0.000
  press_count_e10/on       vs press_fast_e10/on         72     0       0       0       72  1.000
  press_count_e10/on       vs press_v3c_e10/on         100     0       1       1       98  1.000
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_fast_e10/on         72     0       0       0       72  1.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on         72     0       8       0       64  0.008
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_v3c_e10/on          72     0       0       0       72  1.000
  press_fast_e10/on        vs press_v3c_e20/on          72     0       0       4       68  0.125
  press_fast_e10/on        vs press_v3c_e30/on          72     0       0       9       63  0.004
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1072 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e10-s5.log):
```

[pool] 2026-11-21 10:26:25 exec A40-E17-press_fast-e10-s5 GPU 6 
[pool] 2026-11-21 10:26:26 A40-E17-press_fast-e10-s5: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e10-s5.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e10-s5.md
[queue5] 2026-11-21 12:02:22 A40-E17-press_fast-e10-s5: DONE  press_button/on n=72 pressed=72 n1_correct=3 n2_correct=11 confirmed=67 count_correct=0 success=0 prog=0.21
```

## A40-E17-press_fast-e10-s6 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e10-s6.log):
```
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_fast_e10/on         86     0       0       1       85  1.000
  press_count_e20/on       vs press_fast_e20/on         10     0       0       2        8  0.500
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on         86     0      10       1       75  0.012
  press_count_e30/on       vs press_fast_e20/on         10     0       3       2        5  1.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on         10     0       0       2        8  0.500
  press_fast_e10/on        vs press_v3c_e10/on          86     0       1       0       85  1.000
  press_fast_e10/on        vs press_v3c_e20/on          86     0       1       4       81  0.375
  press_fast_e10/on        vs press_v3c_e30/on          86     0       1      14       71  0.001
  press_fast_e20/on        vs press_v3c_e10/on          10     0       2       0        8  0.500
  press_fast_e20/on        vs press_v3c_e20/on          10     0       2       0        8  0.500
  press_fast_e20/on        vs press_v3c_e30/on          10     0       2       0        8  0.500
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1096 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e10-s6.log):
```

[pool] 2026-11-21 10:53:46 exec A40-E17-press_fast-e10-s6 GPU 0 
[pool] 2026-11-21 10:53:48 A40-E17-press_fast-e10-s6: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e10-s6.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e10-s6.md
[queue5] 2026-11-21 12:31:05 A40-E17-press_fast-e10-s6: DONE  press_button/on n=86 pressed=85 n1_correct=4 n2_correct=16 confirmed=80 count_correct=1 success=1 prog=0.21
```

## A40-E17-press_fast-e10-s7 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e10-s7.log):
```
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_fast_e10/on         97     0       0       2       95  0.500
  press_count_e20/on       vs press_fast_e20/on         26     0       0       7       19  0.016
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on         97     0      12       2       83  0.013
  press_count_e30/on       vs press_fast_e20/on         26     0       5       7       14  0.774
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on         26     0       0       7       19  0.016
  press_fast_e10/on        vs press_v3c_e10/on          97     1       1       0       95  1.000
  press_fast_e10/on        vs press_v3c_e20/on          97     0       2       5       90  0.453
  press_fast_e10/on        vs press_v3c_e30/on          97     0       2      16       79  0.001
  press_fast_e20/on        vs press_v3c_e10/on          26     0       7       0       19  0.016
  press_fast_e20/on        vs press_v3c_e20/on          26     0       7       1       18  0.070
  press_fast_e20/on        vs press_v3c_e30/on          26     0       7       2       17  0.180
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1123 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e10-s7.log):
```

[pool] 2026-11-21 11:26:31 exec A40-E17-press_fast-e10-s7 GPU 4 
[pool] 2026-11-21 11:26:33 A40-E17-press_fast-e10-s7: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e10-s7.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e10-s7.md
[queue5] 2026-11-21 13:04:22 A40-E17-press_fast-e10-s7: DONE  press_button/on n=97 pressed=96 n1_correct=5 n2_correct=19 confirmed=91 count_correct=2 success=2 prog=0.22
```

## A40-E17-press_fast-e10-s8 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e10-s8.log):
```
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_fast_e10/on         98     0       0       2       96  0.500
  press_count_e20/on       vs press_fast_e20/on         26     0       0       7       19  0.016
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on         98     0      13       2       83  0.007
  press_count_e30/on       vs press_fast_e20/on         26     0       5       7       14  0.774
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on         26     0       0       7       19  0.016
  press_fast_e10/on        vs press_v3c_e10/on          98     1       1       0       96  1.000
  press_fast_e10/on        vs press_v3c_e20/on          98     0       2       5       91  0.453
  press_fast_e10/on        vs press_v3c_e30/on          98     0       2      17       79  0.001
  press_fast_e20/on        vs press_v3c_e10/on          26     0       7       0       19  0.016
  press_fast_e20/on        vs press_v3c_e20/on          26     0       7       1       18  0.070
  press_fast_e20/on        vs press_v3c_e30/on          26     0       7       2       17  0.180
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1124 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e10-s8.log):
```

[pool] 2026-11-21 11:31:51 exec A40-E17-press_fast-e10-s8 GPU 1 
[pool] 2026-11-21 11:31:53 A40-E17-press_fast-e10-s8: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e10-s8.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e10-s8.md
[queue5] 2026-11-21 13:04:41 A40-E17-press_fast-e10-s8: DONE  press_button/on n=98 pressed=97 n1_correct=5 n2_correct=19 confirmed=92 count_correct=2 success=2 prog=0.22
```

## A40-E17-press_fast-e10-s9 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e10-s9.log):
```
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_fast_e10/on        100     0       0       2       98  0.500
  press_count_e20/on       vs press_fast_e20/on         33     0       0       8       25  0.008
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on        100     0      13       2       85  0.007
  press_count_e30/on       vs press_fast_e20/on         33     0       5       8       20  0.581
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on         33     0       0       8       25  0.008
  press_fast_e10/on        vs press_v3c_e10/on         100     1       1       0       98  1.000
  press_fast_e10/on        vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_fast_e10/on        vs press_v3c_e30/on         100     0       2      17       81  0.001
  press_fast_e20/on        vs press_v3c_e10/on          33     0       8       0       25  0.008
  press_fast_e20/on        vs press_v3c_e20/on          33     0       8       1       24  0.039
  press_fast_e20/on        vs press_v3c_e30/on          33     0       8       2       23  0.109
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1133 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e10-s9.log):
```

[pool] 2026-11-21 11:38:50 exec A40-E17-press_fast-e10-s9 GPU 7 
[pool] 2026-11-21 11:38:52 A40-E17-press_fast-e10-s9: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e10-s9.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e10-s9.md
[queue5] 2026-11-21 13:18:47 A40-E17-press_fast-e10-s9: DONE  press_button/on n=100 pressed=99 n1_correct=5 n2_correct=19 confirmed=94 count_correct=2 success=2 prog=0.22
```

## A40-E17-press_fast-e20-s0 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e20-s0.log):
```
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_fast_e10/on         98     0       0       2       96  0.500
  press_count_e20/on       vs press_fast_e20/on         28     0       0       8       20  0.008
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on         98     0      13       2       83  0.007
  press_count_e30/on       vs press_fast_e20/on         28     0       5       8       15  0.581
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on         28     0       0       8       20  0.008
  press_fast_e10/on        vs press_v3c_e10/on          98     1       1       0       96  1.000
  press_fast_e10/on        vs press_v3c_e20/on          98     0       2       5       91  0.453
  press_fast_e10/on        vs press_v3c_e30/on          98     0       2      17       79  0.001
  press_fast_e20/on        vs press_v3c_e10/on          28     0       8       0       20  0.008
  press_fast_e20/on        vs press_v3c_e20/on          28     0       8       1       19  0.039
  press_fast_e20/on        vs press_v3c_e30/on          28     0       8       2       18  0.109
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1126 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e20-s0.log):
```

[pool] 2026-11-21 11:48:29 exec A40-E17-press_fast-e20-s0 GPU 5 
[pool] 2026-11-21 11:48:31 A40-E17-press_fast-e20-s0: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e20-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e20-s0.md
[queue5] 2026-11-21 13:01:39 A40-E17-press_fast-e20-s0: DONE  press_button/on n=28 pressed=28 n1_correct=20 n2_correct=9 confirmed=28 count_correct=8 success=8 prog=0.51
```

## A40-E17-press_fast-e20-s1 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e20-s1.log):
```
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_fast_e10/on        100     0       0       2       98  0.500
  press_count_e20/on       vs press_fast_e20/on         39     0       0      10       29  0.002
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on        100     0      13       2       85  0.007
  press_count_e30/on       vs press_fast_e20/on         39     0       5      10       24  0.302
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on         39     0       0      10       29  0.002
  press_fast_e10/on        vs press_v3c_e10/on         100     1       1       0       98  1.000
  press_fast_e10/on        vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_fast_e10/on        vs press_v3c_e30/on         100     0       2      17       81  0.001
  press_fast_e20/on        vs press_v3c_e10/on          39     0      10       0       29  0.002
  press_fast_e20/on        vs press_v3c_e20/on          39     0      10       1       28  0.012
  press_fast_e20/on        vs press_v3c_e30/on          39     1       9       3       26  0.146
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1139 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e20-s1.log):
```

[pool] 2026-11-21 11:57:03 exec A40-E17-press_fast-e20-s1 GPU 3 
[pool] 2026-11-21 11:57:05 A40-E17-press_fast-e20-s1: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e20-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e20-s1.md
[queue5] 2026-11-21 13:20:07 A40-E17-press_fast-e20-s1: DONE  press_button/on n=39 pressed=39 n1_correct=27 n2_correct=13 confirmed=39 count_correct=10 success=10 prog=0.49
```

## A40-E17-press_fast-e20-s2 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e20-s2.log):
```
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_fast_e10/on        100     0       0       2       98  0.500
  press_count_e20/on       vs press_fast_e20/on         41     0       0      11       30  0.001
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on        100     0      13       2       85  0.007
  press_count_e30/on       vs press_fast_e20/on         41     0       5      11       25  0.210
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on         41     0       0      11       30  0.001
  press_fast_e10/on        vs press_v3c_e10/on         100     1       1       0       98  1.000
  press_fast_e10/on        vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_fast_e10/on        vs press_v3c_e30/on         100     0       2      17       81  0.001
  press_fast_e20/on        vs press_v3c_e10/on          41     0      11       0       30  0.001
  press_fast_e20/on        vs press_v3c_e20/on          41     0      11       1       29  0.006
  press_fast_e20/on        vs press_v3c_e30/on          41     1      10       3       27  0.092
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1141 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e20-s2.log):
```

[pool] 2026-11-21 12:00:48 exec A40-E17-press_fast-e20-s2 GPU 6 
[pool] 2026-11-21 12:00:49 A40-E17-press_fast-e20-s2: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e20-s2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e20-s2.md
[queue5] 2026-11-21 13:24:08 A40-E17-press_fast-e20-s2: DONE  press_button/on n=41 pressed=41 n1_correct=29 n2_correct=14 confirmed=41 count_correct=11 success=11 prog=0.50
```

## A40-E17-press_fast-e20-s3 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e20-s3.log):
```
  press_count_e10/on       vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_count_e10/on       vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_count_e20/on       vs press_count_e30/on       100     0       0      13       87  0.000
  press_count_e20/on       vs press_fast_e10/on        100     0       0       2       98  0.500
  press_count_e20/on       vs press_fast_e20/on         74     0       0      18       56  0.000
  press_count_e20/on       vs press_v3c_e10/on         100     0       0       1       99  1.000
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on        100     0      13       2       85  0.007
  press_count_e30/on       vs press_fast_e20/on         74     1       9      17       47  0.169
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on         74     0       0      18       56  0.000
  press_fast_e10/on        vs press_v3c_e10/on         100     1       1       0       98  1.000
  press_fast_e10/on        vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_fast_e10/on        vs press_v3c_e30/on         100     0       2      17       81  0.001
  press_fast_e20/on        vs press_v3c_e10/on          74     0      18       0       56  0.000
  press_fast_e20/on        vs press_v3c_e20/on          74     0      18       3       53  0.001
  press_fast_e20/on        vs press_v3c_e30/on          74     3      15       6       50  0.078
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1174 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e20-s3.log):
```

[pool] 2026-11-21 12:28:41 exec A40-E17-press_fast-e20-s3 GPU 0 
[pool] 2026-11-21 12:28:43 A40-E17-press_fast-e20-s3: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e20-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e20-s3.md
[queue5] 2026-11-21 14:05:39 A40-E17-press_fast-e20-s3: DONE  press_button/on n=74 pressed=74 n1_correct=51 n2_correct=25 confirmed=74 count_correct=18 success=18 prog=0.48
```

## A40-E17-press_fast-e20-s4 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e20-s4.log):
```
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on        100     0      13       2       85  0.007
  press_count_e30/on       vs press_fast_e20/on         87     1      10      19       57  0.136
  press_count_e30/on       vs press_fast_e30/on          1     0       0       0        1  1.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on         87     0       1      20       66  0.000
  press_fast_e10/on        vs press_fast_e30/on          1     0       0       0        1  1.000
  press_fast_e10/on        vs press_v3c_e10/on         100     1       1       0       98  1.000
  press_fast_e10/on        vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_fast_e10/on        vs press_v3c_e30/on         100     0       2      17       81  0.001
  press_fast_e20/on        vs press_fast_e30/on          1     0       0       0        1  1.000
  press_fast_e20/on        vs press_v3c_e10/on          87     0      20       0       67  0.000
  press_fast_e20/on        vs press_v3c_e20/on          87     0      20       4       63  0.002
  press_fast_e20/on        vs press_v3c_e30/on          87     3      17      10       57  0.248
  press_fast_e30/on        vs press_v3c_e10/on           1     0       0       0        1  1.000
  press_fast_e30/on        vs press_v3c_e20/on           1     0       0       0        1  1.000
  press_fast_e30/on        vs press_v3c_e30/on           1     0       0       0        1  1.000
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1188 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e20-s4.log):
```

[pool] 2026-11-21 13:02:00 exec A40-E17-press_fast-e20-s4 GPU 1 
[pool] 2026-11-21 13:02:02 A40-E17-press_fast-e20-s4: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e20-s4.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e20-s4.md
[queue5] 2026-11-21 14:21:55 A40-E17-press_fast-e20-s4: DONE  press_button/on n=87 pressed=87 n1_correct=58 n2_correct=29 confirmed=87 count_correct=20 success=20 prog=0.47
```

## A40-E17-press_fast-e20-s5 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e20-s5.log):
```
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on        100     0      13       2       85  0.007
  press_count_e30/on       vs press_fast_e20/on         95     1      10      20       64  0.099
  press_count_e30/on       vs press_fast_e30/on          6     1       0       2        3  0.500
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on         95     0       2      21       72  0.000
  press_fast_e10/on        vs press_fast_e30/on          6     0       0       3        3  0.250
  press_fast_e10/on        vs press_v3c_e10/on         100     1       1       0       98  1.000
  press_fast_e10/on        vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_fast_e10/on        vs press_v3c_e30/on         100     0       2      17       81  0.001
  press_fast_e20/on        vs press_fast_e30/on          6     1       0       2        3  0.500
  press_fast_e20/on        vs press_v3c_e10/on          95     0      21       1       73  0.000
  press_fast_e20/on        vs press_v3c_e20/on          95     0      21       5       69  0.002
  press_fast_e20/on        vs press_v3c_e30/on          95     4      17      12       62  0.458
  press_fast_e30/on        vs press_v3c_e10/on           6     0       3       0        3  0.250
  press_fast_e30/on        vs press_v3c_e20/on           6     0       3       0        3  0.250
  press_fast_e30/on        vs press_v3c_e30/on           6     0       3       0        3  0.250
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1201 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e20-s5.log):
```

[pool] 2026-11-21 13:02:00 exec A40-E17-press_fast-e20-s5 GPU 4 
[pool] 2026-11-21 13:02:02 A40-E17-press_fast-e20-s5: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e20-s5.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e20-s5.md
[queue5] 2026-11-21 14:36:28 A40-E17-press_fast-e20-s5: DONE  press_button/on n=95 pressed=95 n1_correct=65 n2_correct=30 confirmed=95 count_correct=21 success=21 prog=0.47
```

## A40-E17-press_fast-e20-s6 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e20-s6.log):
```
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on        100     0      13       2       85  0.007
  press_count_e30/on       vs press_fast_e20/on         88     1      10      19       58  0.136
  press_count_e30/on       vs press_fast_e30/on          1     0       0       0        1  1.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on         88     0       1      20       67  0.000
  press_fast_e10/on        vs press_fast_e30/on          1     0       0       0        1  1.000
  press_fast_e10/on        vs press_v3c_e10/on         100     1       1       0       98  1.000
  press_fast_e10/on        vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_fast_e10/on        vs press_v3c_e30/on         100     0       2      17       81  0.001
  press_fast_e20/on        vs press_fast_e30/on          1     0       0       0        1  1.000
  press_fast_e20/on        vs press_v3c_e10/on          88     0      20       0       68  0.000
  press_fast_e20/on        vs press_v3c_e20/on          88     0      20       4       64  0.002
  press_fast_e20/on        vs press_v3c_e30/on          88     3      17      11       57  0.345
  press_fast_e30/on        vs press_v3c_e10/on           1     0       0       0        1  1.000
  press_fast_e30/on        vs press_v3c_e20/on           1     0       0       0        1  1.000
  press_fast_e30/on        vs press_v3c_e30/on           1     0       0       0        1  1.000
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1189 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e20-s6.log):
```

[pool] 2026-11-21 13:02:00 exec A40-E17-press_fast-e20-s6 GPU 5 
[pool] 2026-11-21 13:02:02 A40-E17-press_fast-e20-s6: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e20-s6.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e20-s6.md
[queue5] 2026-11-21 14:22:08 A40-E17-press_fast-e20-s6: DONE  press_button/on n=88 pressed=88 n1_correct=59 n2_correct=29 confirmed=88 count_correct=20 success=20 prog=0.47
```

## A40-E17-press_fast-e20-s7 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e20-s7.log):
```
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on        100     0      13       2       85  0.007
  press_count_e30/on       vs press_fast_e20/on         99     2      11      20       66  0.150
  press_count_e30/on       vs press_fast_e30/on         11     2       1       4        4  0.375
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on         99     0       2      22       75  0.000
  press_fast_e10/on        vs press_fast_e30/on         11     0       0       6        5  0.031
  press_fast_e10/on        vs press_v3c_e10/on         100     1       1       0       98  1.000
  press_fast_e10/on        vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_fast_e10/on        vs press_v3c_e30/on         100     0       2      17       81  0.001
  press_fast_e20/on        vs press_fast_e30/on         11     1       1       5        4  0.219
  press_fast_e20/on        vs press_v3c_e10/on          99     0      22       1       76  0.000
  press_fast_e20/on        vs press_v3c_e20/on          99     0      22       5       72  0.002
  press_fast_e20/on        vs press_v3c_e30/on          99     5      17      12       65  0.458
  press_fast_e30/on        vs press_v3c_e10/on          11     0       6       0        5  0.031
  press_fast_e30/on        vs press_v3c_e20/on          11     0       6       0        5  0.031
  press_fast_e30/on        vs press_v3c_e30/on          11     1       5       0        5  0.062
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1210 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e20-s7.log):
```

[pool] 2026-11-21 13:16:05 exec A40-E17-press_fast-e20-s7 GPU 7 
[pool] 2026-11-21 13:16:07 A40-E17-press_fast-e20-s7: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e20-s7.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e20-s7.md
[queue5] 2026-11-21 14:45:24 A40-E17-press_fast-e20-s7: DONE  press_button/on n=99 pressed=99 n1_correct=67 n2_correct=31 confirmed=99 count_correct=22 success=22 prog=0.47
```

## A40-E17-press_fast-e20-s8 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e20-s8.log):
```
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on        100     0      13       2       85  0.007
  press_count_e30/on       vs press_fast_e20/on         97     2      10      20       65  0.099
  press_count_e30/on       vs press_fast_e30/on          9     2       1       2        4  1.000
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on         97     0       2      22       73  0.000
  press_fast_e10/on        vs press_fast_e30/on          9     0       0       4        5  0.125
  press_fast_e10/on        vs press_v3c_e10/on         100     1       1       0       98  1.000
  press_fast_e10/on        vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_fast_e10/on        vs press_v3c_e30/on         100     0       2      17       81  0.001
  press_fast_e20/on        vs press_fast_e30/on          9     1       1       3        4  0.625
  press_fast_e20/on        vs press_v3c_e10/on          97     0      22       1       74  0.000
  press_fast_e20/on        vs press_v3c_e20/on          97     0      22       5       70  0.002
  press_fast_e20/on        vs press_v3c_e30/on          97     5      17      12       63  0.458
  press_fast_e30/on        vs press_v3c_e10/on           9     0       4       0        5  0.125
  press_fast_e30/on        vs press_v3c_e20/on           9     0       4       0        5  0.125
  press_fast_e30/on        vs press_v3c_e30/on           9     0       4       0        5  0.125
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1206 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e20-s8.log):
```

[pool] 2026-11-21 13:20:22 exec A40-E17-press_fast-e20-s8 GPU 3 
[pool] 2026-11-21 13:20:24 A40-E17-press_fast-e20-s8: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e20-s8.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e20-s8.md
[queue5] 2026-11-21 14:41:47 A40-E17-press_fast-e20-s8: DONE  press_button/on n=97 pressed=97 n1_correct=66 n2_correct=31 confirmed=97 count_correct=22 success=22 prog=0.47
```

## A40-E17-press_fast-e20-s9 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e20-s9.log):
```
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on        100     0      13       2       85  0.007
  press_count_e30/on       vs press_fast_e20/on        100     2      11      20       67  0.150
  press_count_e30/on       vs press_fast_e30/on         16     2       1       5        8  0.219
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on        100     0       2      22       76  0.000
  press_fast_e10/on        vs press_fast_e30/on         16     0       0       7        9  0.016
  press_fast_e10/on        vs press_v3c_e10/on         100     1       1       0       98  1.000
  press_fast_e10/on        vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_fast_e10/on        vs press_v3c_e30/on         100     0       2      17       81  0.001
  press_fast_e20/on        vs press_fast_e30/on         16     2       2       5        7  0.453
  press_fast_e20/on        vs press_v3c_e10/on         100     0      22       1       77  0.000
  press_fast_e20/on        vs press_v3c_e20/on         100     0      22       5       73  0.002
  press_fast_e20/on        vs press_v3c_e30/on         100     5      17      12       66  0.458
  press_fast_e30/on        vs press_v3c_e10/on          16     0       7       0        9  0.016
  press_fast_e30/on        vs press_v3c_e20/on          16     0       7       0        9  0.016
  press_fast_e30/on        vs press_v3c_e30/on          16     1       6       1        8  0.125
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1216 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e20-s9.log):
```

[pool] 2026-11-21 13:24:08 exec A40-E17-press_fast-e20-s9 GPU 6 
[pool] 2026-11-21 13:24:10 A40-E17-press_fast-e20-s9: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e20-s9.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e20-s9.md
[queue5] 2026-11-21 14:53:53 A40-E17-press_fast-e20-s9: DONE  press_button/on n=100 pressed=100 n1_correct=68 n2_correct=31 confirmed=100 count_correct=22 success=22 prog=0.47
```

## A40-E17-press_fast-e30-s0 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e30-s0.log):
```
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on        100     0      13       2       85  0.007
  press_count_e30/on       vs press_fast_e20/on        100     2      11      20       67  0.150
  press_count_e30/on       vs press_fast_e30/on         46     3       3       9       31  0.146
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on        100     0       2      22       76  0.000
  press_fast_e10/on        vs press_fast_e30/on         46     0       0      12       34  0.000
  press_fast_e10/on        vs press_v3c_e10/on         100     1       1       0       98  1.000
  press_fast_e10/on        vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_fast_e10/on        vs press_v3c_e30/on         100     0       2      17       81  0.001
  press_fast_e20/on        vs press_fast_e30/on         46     3       8       9       26  1.000
  press_fast_e20/on        vs press_v3c_e10/on         100     0      22       1       77  0.000
  press_fast_e20/on        vs press_v3c_e20/on         100     0      22       5       73  0.002
  press_fast_e20/on        vs press_v3c_e30/on         100     5      17      12       66  0.458
  press_fast_e30/on        vs press_v3c_e10/on          46     0      12       0       34  0.000
  press_fast_e30/on        vs press_v3c_e20/on          46     0      12       2       32  0.013
  press_fast_e30/on        vs press_v3c_e30/on          46     1      11       3       31  0.057
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1246 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e30-s0.log):
```

[pool] 2026-11-21 14:04:22 exec A40-E17-press_fast-e30-s0 GPU 0 
[pool] 2026-11-21 14:04:24 A40-E17-press_fast-e30-s0: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e30-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e30-s0.md
[queue5] 2026-11-21 15:27:45 A40-E17-press_fast-e30-s0: DONE  press_button/on n=46 pressed=46 n1_correct=33 n2_correct=15 confirmed=46 count_correct=12 success=12 prog=0.50
```

## A40-E17-press_fast-e30-s1 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e30-s1.log):
```
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on        100     0      13       2       85  0.007
  press_count_e30/on       vs press_fast_e20/on        100     2      11      20       67  0.150
  press_count_e30/on       vs press_fast_e30/on         58     3       4      10       41  0.180
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on        100     0       2      22       76  0.000
  press_fast_e10/on        vs press_fast_e30/on         58     0       0      13       45  0.000
  press_fast_e10/on        vs press_v3c_e10/on         100     1       1       0       98  1.000
  press_fast_e10/on        vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_fast_e10/on        vs press_v3c_e30/on         100     0       2      17       81  0.001
  press_fast_e20/on        vs press_fast_e30/on         58     3      10      10       35  1.000
  press_fast_e20/on        vs press_v3c_e10/on         100     0      22       1       77  0.000
  press_fast_e20/on        vs press_v3c_e20/on         100     0      22       5       73  0.002
  press_fast_e20/on        vs press_v3c_e30/on         100     5      17      12       66  0.458
  press_fast_e30/on        vs press_v3c_e10/on          58     0      13       0       45  0.000
  press_fast_e30/on        vs press_v3c_e20/on          58     0      13       3       42  0.021
  press_fast_e30/on        vs press_v3c_e30/on          58     1      12       4       41  0.077
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1258 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e30-s1.log):
```

[pool] 2026-11-21 14:20:28 exec A40-E17-press_fast-e30-s1 GPU 1 
[pool] 2026-11-21 14:20:29 A40-E17-press_fast-e30-s1: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e30-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e30-s1.md
[queue5] 2026-11-21 15:45:53 A40-E17-press_fast-e30-s1: DONE  press_button/on n=58 pressed=58 n1_correct=40 n2_correct=18 confirmed=58 count_correct=13 success=13 prog=0.47
```

## A40-E17-press_fast-e30-s2 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e30-s2.log):
```
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on        100     0      13       2       85  0.007
  press_count_e30/on       vs press_fast_e20/on        100     2      11      20       67  0.150
  press_count_e30/on       vs press_fast_e30/on         44     3       3       8       30  0.227
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on        100     0       2      22       76  0.000
  press_fast_e10/on        vs press_fast_e30/on         44     0       0      11       33  0.001
  press_fast_e10/on        vs press_v3c_e10/on         100     1       1       0       98  1.000
  press_fast_e10/on        vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_fast_e10/on        vs press_v3c_e30/on         100     0       2      17       81  0.001
  press_fast_e20/on        vs press_fast_e30/on         44     2       8       9       25  1.000
  press_fast_e20/on        vs press_v3c_e10/on         100     0      22       1       77  0.000
  press_fast_e20/on        vs press_v3c_e20/on         100     0      22       5       73  0.002
  press_fast_e20/on        vs press_v3c_e30/on         100     5      17      12       66  0.458
  press_fast_e30/on        vs press_v3c_e10/on          44     0      11       0       33  0.001
  press_fast_e30/on        vs press_v3c_e20/on          44     0      11       2       31  0.022
  press_fast_e30/on        vs press_v3c_e30/on          44     1      10       3       30  0.092
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1244 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e30-s2.log):
```

[pool] 2026-11-21 14:20:28 exec A40-E17-press_fast-e30-s2 GPU 5 
[pool] 2026-11-21 14:20:29 A40-E17-press_fast-e30-s2: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e30-s2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e30-s2.md
[queue5] 2026-11-21 15:26:24 A40-E17-press_fast-e30-s2: DONE  press_button/on n=44 pressed=44 n1_correct=31 n2_correct=14 confirmed=44 count_correct=11 success=11 prog=0.49
```

## A40-E17-press_fast-e30-s3 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e30-s3.log):
```
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on        100     0      13       2       85  0.007
  press_count_e30/on       vs press_fast_e20/on        100     2      11      20       67  0.150
  press_count_e30/on       vs press_fast_e30/on         73     3       5      13       52  0.096
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on        100     0       2      22       76  0.000
  press_fast_e10/on        vs press_fast_e30/on         73     0       0      16       57  0.000
  press_fast_e10/on        vs press_v3c_e10/on         100     1       1       0       98  1.000
  press_fast_e10/on        vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_fast_e10/on        vs press_v3c_e30/on         100     0       2      17       81  0.001
  press_fast_e20/on        vs press_fast_e30/on         73     4      14      12       43  0.845
  press_fast_e20/on        vs press_v3c_e10/on         100     0      22       1       77  0.000
  press_fast_e20/on        vs press_v3c_e20/on         100     0      22       5       73  0.002
  press_fast_e20/on        vs press_v3c_e30/on         100     5      17      12       66  0.458
  press_fast_e30/on        vs press_v3c_e10/on          73     0      16       0       57  0.000
  press_fast_e30/on        vs press_v3c_e20/on          73     0      16       4       53  0.012
  press_fast_e30/on        vs press_v3c_e30/on          73     3      13       7       50  0.263
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1273 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e30-s3.log):
```

[pool] 2026-11-21 14:34:27 exec A40-E17-press_fast-e30-s3 GPU 4 
[pool] 2026-11-21 14:34:29 A40-E17-press_fast-e30-s3: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e30-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e30-s3.md
[queue5] 2026-11-21 16:01:28 A40-E17-press_fast-e30-s3: DONE  press_button/on n=73 pressed=73 n1_correct=50 n2_correct=22 confirmed=73 count_correct=16 success=16 prog=0.47
```

## A40-E17-press_fast-e30-s4 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e30-s4.log):
```
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on        100     0      13       2       85  0.007
  press_count_e30/on       vs press_fast_e20/on        100     2      11      20       67  0.150
  press_count_e30/on       vs press_fast_e30/on         83     3       7      19       54  0.029
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on        100     0       2      22       76  0.000
  press_fast_e10/on        vs press_fast_e30/on         83     1       0      21       61  0.000
  press_fast_e10/on        vs press_v3c_e10/on         100     1       1       0       98  1.000
  press_fast_e10/on        vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_fast_e10/on        vs press_v3c_e30/on         100     0       2      17       81  0.001
  press_fast_e20/on        vs press_fast_e30/on         83     5      15      17       46  0.860
  press_fast_e20/on        vs press_v3c_e10/on         100     0      22       1       77  0.000
  press_fast_e20/on        vs press_v3c_e20/on         100     0      22       5       73  0.002
  press_fast_e20/on        vs press_v3c_e30/on         100     5      17      12       66  0.458
  press_fast_e30/on        vs press_v3c_e10/on          83     0      22       0       61  0.000
  press_fast_e30/on        vs press_v3c_e20/on          83     0      22       4       57  0.001
  press_fast_e30/on        vs press_v3c_e30/on          83     4      18      10       51  0.185
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1283 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e30-s4.log):
```

[pool] 2026-11-21 14:39:51 exec A40-E17-press_fast-e30-s4 GPU 3 
[pool] 2026-11-21 14:39:53 A40-E17-press_fast-e30-s4: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e30-s4.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e30-s4.md
[queue5] 2026-11-21 16:12:58 A40-E17-press_fast-e30-s4: DONE  press_button/on n=83 pressed=83 n1_correct=59 n2_correct=28 confirmed=83 count_correct=22 success=22 prog=0.50
```

## A40-E17-press_fast-e30-s5 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e30-s5.log):
```
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on        100     0      13       2       85  0.007
  press_count_e30/on       vs press_fast_e20/on        100     2      11      20       67  0.150
  press_count_e30/on       vs press_fast_e30/on         85     3       7      20       55  0.019
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on        100     0       2      22       76  0.000
  press_fast_e10/on        vs press_fast_e30/on         85     1       0      22       62  0.000
  press_fast_e10/on        vs press_v3c_e10/on         100     1       1       0       98  1.000
  press_fast_e10/on        vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_fast_e10/on        vs press_v3c_e30/on         100     0       2      17       81  0.001
  press_fast_e20/on        vs press_fast_e30/on         85     5      15      18       47  0.728
  press_fast_e20/on        vs press_v3c_e10/on         100     0      22       1       77  0.000
  press_fast_e20/on        vs press_v3c_e20/on         100     0      22       5       73  0.002
  press_fast_e20/on        vs press_v3c_e30/on         100     5      17      12       66  0.458
  press_fast_e30/on        vs press_v3c_e10/on          85     0      23       0       62  0.000
  press_fast_e30/on        vs press_v3c_e20/on          85     0      23       4       58  0.000
  press_fast_e30/on        vs press_v3c_e30/on          85     4      19      10       52  0.136
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1285 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e30-s5.log):
```

[pool] 2026-11-21 14:43:36 exec A40-E17-press_fast-e30-s5 GPU 7 
[pool] 2026-11-21 14:43:38 A40-E17-press_fast-e30-s5: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e30-s5.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e30-s5.md
[queue5] 2026-11-21 16:14:59 A40-E17-press_fast-e30-s5: DONE  press_button/on n=85 pressed=85 n1_correct=61 n2_correct=29 confirmed=85 count_correct=23 success=23 prog=0.51
```

## A40-E17-press_fast-e30-s6 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e30-s6.log):
```
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on        100     0      13       2       85  0.007
  press_count_e30/on       vs press_fast_e20/on        100     2      11      20       67  0.150
  press_count_e30/on       vs press_fast_e30/on         77     3       6      16       52  0.052
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on        100     0       2      22       76  0.000
  press_fast_e10/on        vs press_fast_e30/on         77     0       0      19       58  0.000
  press_fast_e10/on        vs press_v3c_e10/on         100     1       1       0       98  1.000
  press_fast_e10/on        vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_fast_e10/on        vs press_v3c_e30/on         100     0       2      17       81  0.001
  press_fast_e20/on        vs press_fast_e30/on         77     4      14      15       44  1.000
  press_fast_e20/on        vs press_v3c_e10/on         100     0      22       1       77  0.000
  press_fast_e20/on        vs press_v3c_e20/on         100     0      22       5       73  0.002
  press_fast_e20/on        vs press_v3c_e30/on         100     5      17      12       66  0.458
  press_fast_e30/on        vs press_v3c_e10/on          77     0      19       0       58  0.000
  press_fast_e30/on        vs press_v3c_e20/on          77     0      19       4       54  0.003
  press_fast_e30/on        vs press_v3c_e30/on          77     4      15       7       51  0.134
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1277 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e30-s6.log):
```

[pool] 2026-11-21 14:51:42 exec A40-E17-press_fast-e30-s6 GPU 6 
[pool] 2026-11-21 14:51:43 A40-E17-press_fast-e30-s6: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e30-s6.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e30-s6.md
[queue5] 2026-11-21 16:04:16 A40-E17-press_fast-e30-s6: DONE  press_button/on n=77 pressed=77 n1_correct=54 n2_correct=25 confirmed=77 count_correct=19 success=19 prog=0.49
```

## A40-E17-press_fast-e30-s7 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e30-s7.log):
```
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on        100     0      13       2       85  0.007
  press_count_e30/on       vs press_fast_e20/on        100     2      11      20       67  0.150
  press_count_e30/on       vs press_fast_e30/on         98     4       9      21       64  0.043
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on        100     0       2      22       76  0.000
  press_fast_e10/on        vs press_fast_e30/on         98     1       1      24       72  0.000
  press_fast_e10/on        vs press_v3c_e10/on         100     1       1       0       98  1.000
  press_fast_e10/on        vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_fast_e10/on        vs press_v3c_e30/on         100     0       2      17       81  0.001
  press_fast_e20/on        vs press_fast_e30/on         98     7      15      18       58  0.728
  press_fast_e20/on        vs press_v3c_e10/on         100     0      22       1       77  0.000
  press_fast_e20/on        vs press_v3c_e20/on         100     0      22       5       73  0.002
  press_fast_e20/on        vs press_v3c_e30/on         100     5      17      12       66  0.458
  press_fast_e30/on        vs press_v3c_e10/on          98     0      25       1       72  0.000
  press_fast_e30/on        vs press_v3c_e20/on          98     0      25       5       68  0.000
  press_fast_e30/on        vs press_v3c_e30/on          98     6      19      11       62  0.200
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1298 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e30-s7.log):
```

[pool] 2026-11-21 15:26:09 exec A40-E17-press_fast-e30-s7 GPU 5 
[pool] 2026-11-21 15:26:11 A40-E17-press_fast-e30-s7: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e30-s7.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e30-s7.md
[queue5] 2026-11-21 17:00:48 A40-E17-press_fast-e30-s7: DONE  press_button/on n=98 pressed=98 n1_correct=69 n2_correct=32 confirmed=98 count_correct=25 success=25 prog=0.49
```

## A40-E17-press_fast-e30-s8 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e30-s8.log):
```
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on        100     0      13       2       85  0.007
  press_count_e30/on       vs press_fast_e20/on        100     2      11      20       67  0.150
  press_count_e30/on       vs press_fast_e30/on         92     4       7      20       61  0.019
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on        100     0       2      22       76  0.000
  press_fast_e10/on        vs press_fast_e30/on         92     1       0      23       68  0.000
  press_fast_e10/on        vs press_v3c_e10/on         100     1       1       0       98  1.000
  press_fast_e10/on        vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_fast_e10/on        vs press_v3c_e30/on         100     0       2      17       81  0.001
  press_fast_e20/on        vs press_fast_e30/on         92     6      15      18       53  0.728
  press_fast_e20/on        vs press_v3c_e10/on         100     0      22       1       77  0.000
  press_fast_e20/on        vs press_v3c_e20/on         100     0      22       5       73  0.002
  press_fast_e20/on        vs press_v3c_e30/on         100     5      17      12       66  0.458
  press_fast_e30/on        vs press_v3c_e10/on          92     0      24       0       68  0.000
  press_fast_e30/on        vs press_v3c_e20/on          92     0      24       5       63  0.001
  press_fast_e30/on        vs press_v3c_e30/on          92     5      19      10       58  0.136
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1292 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e30-s8.log):
```

[pool] 2026-11-21 15:27:45 exec A40-E17-press_fast-e30-s8 GPU 0 
[pool] 2026-11-21 15:27:47 A40-E17-press_fast-e30-s8: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e30-s8.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e30-s8.md
[queue5] 2026-11-21 16:36:02 A40-E17-press_fast-e30-s8: DONE  press_button/on n=92 pressed=92 n1_correct=64 n2_correct=30 confirmed=92 count_correct=24 success=24 prog=0.50
```

## A40-E17-press_fast-e30-s9 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e30-s9.log):
```
  press_count_e20/on       vs press_v3c_e20/on         100     0       0       5       95  0.062
  press_count_e20/on       vs press_v3c_e30/on         100     0       0      17       83  0.000
  press_count_e30/on       vs press_fast_e10/on        100     0      13       2       85  0.007
  press_count_e30/on       vs press_fast_e20/on        100     2      11      20       67  0.150
  press_count_e30/on       vs press_fast_e30/on        100     4       9      22       65  0.029
  press_count_e30/on       vs press_v3c_e10/on         100     0      13       1       86  0.002
  press_count_e30/on       vs press_v3c_e20/on         100     3      10       2       85  0.039
  press_count_e30/on       vs press_v3c_e30/on         100     2      11      15       72  0.557
  press_fast_e10/on        vs press_fast_e20/on        100     0       2      22       76  0.000
  press_fast_e10/on        vs press_fast_e30/on        100     1       1      25       73  0.000
  press_fast_e10/on        vs press_v3c_e10/on         100     1       1       0       98  1.000
  press_fast_e10/on        vs press_v3c_e20/on         100     0       2       5       93  0.453
  press_fast_e10/on        vs press_v3c_e30/on         100     0       2      17       81  0.001
  press_fast_e20/on        vs press_fast_e30/on        100     7      15      19       59  0.608
  press_fast_e20/on        vs press_v3c_e10/on         100     0      22       1       77  0.000
  press_fast_e20/on        vs press_v3c_e20/on         100     0      22       5       73  0.002
  press_fast_e20/on        vs press_v3c_e30/on         100     5      17      12       66  0.458
  press_fast_e30/on        vs press_v3c_e10/on         100     0      26       1       73  0.000
  press_fast_e30/on        vs press_v3c_e20/on         100     0      26       5       69  0.000
  press_fast_e30/on        vs press_v3c_e30/on         100     6      20      11       63  0.150
  press_v3c_e10/on         vs press_v3c_e20/on         100     0       1       5       94  0.219
  press_v3c_e10/on         vs press_v3c_e30/on         100     0       1      17       82  0.000
  press_v3c_e20/on         vs press_v3c_e30/on         100     1       4      16       79  0.012

[summary] 1300 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e17/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-press_fast-e30-s9.log):
```

[pool] 2026-11-21 15:45:29 exec A40-E17-press_fast-e30-s9 GPU 1 
[pool] 2026-11-21 15:45:31 A40-E17-press_fast-e30-s9: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-press_fast-e30-s9.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e30-s9.md
[queue5] 2026-11-21 17:10:57 A40-E17-press_fast-e30-s9: DONE  press_button/on n=100 pressed=100 n1_correct=71 n2_correct=33 confirmed=100 count_correct=26 success=26 prog=0.50
```

## A40-E17-report (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-report.log):
```

[queue5] 2026-11-21 17:07:54 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/e17_report.py
press_arprop_e10   1-50:  0/50 (first right  2)   51-100:  0/50 (first right  1)
press_arprop_e20   1-50:  4/50 (first right 28)   51-100:  4/50 (first right 28)
press_arprop_e30   1-50:  0/50 (first right 10)   51-100:  2/50 (first right 10)
press_ar_e30       1-50:  2/50 (first right  7)   51-100:  0/50 (first right  5)
press_fast_e10     1-50:  1/50 (first right  4)   51-100:  1/50 (first right  1)
press_fast_e20     1-50: 11/50 (first right 33)   51-100: 11/50 (first right 35)
press_fast_e30     1-50: 13/50 (first right 35)   51-100: 13/50 (first right 36)
press_count_e10    1-50:  0/50 (first right  3)   51-100:  1/50 (first right  5)
press_count_e20    1-50:  0/50 (first right  1)   51-100:  0/50 (first right  2)
press_count_e30    1-50:  8/50 (first right 27)   51-100:  5/50 (first right 23)
P-SEL picks (1-50): {'press_arprop': 'e20', 'press_ar': 'e30', 'press_fast': 'e30', 'press_count': 'e30'}
E3 analogue on 51-100 (A40, descriptive): {'a': 'press_fast_e30', 'b': 'press_arprop_e20', 'n': 50, 'a_success': 13, 'b_success': 4, 'diff': 9, 'only_a': 11, 'only_b': 2, 'p': 0.0224609375}
E4 analogue on 51-100 (A40, descriptive): {'a': 'press_count_e30', 'b': 'press_fast_e30', 'n': 50, 'a_success': 5, 'b_success': 13, 'diff': -8, 'only_a': 4, 'only_b': 12, 'p': 0.076812744140625}
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E17-report.log):
```

[pool] 2026-11-21 17:07:52 exec A40-E17-report GPU None 
[pool] 2026-11-21 17:07:54 A40-E17-report: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E17-report.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-report.md
[queue5] 2026-11-21 17:19:56 A40-E17-report: PASS  rc=0
```

## A40-E14-verdict (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E14-verdict.log):
```

[queue5] 2026-11-21 00:59:38 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/e14_verdict_a40.py
press_v3c_e10 on 1-50: success 0/50, first right 5
press_v3c_e20 on 1-50: success 1/50, first right 5
press_v3c_e30 on 1-50: success 9/50, first right 36
press_count_e10 on 1-50: success 0/50, first right 3
press_count_e20 on 1-50: success 0/50, first right 1
press_count_e30 on 1-50: success 8/50, first right 27
E14 (A40): press_v3c_e30 vs press_count_e30 on 51-100, n=50: 8 vs 5; only new 7, only ref 4, sign p 0.5488
E14 VERDICT (A40): NO EFFECT; >= 25/50: False
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E14-verdict.log):
```

[pool] 2026-11-21 00:59:36 exec A40-E14-verdict GPU None 
[pool] 2026-11-21 00:59:38 A40-E14-verdict: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E14-verdict.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E14-verdict.md
[queue5] 2026-11-21 01:06:49 A40-E14-verdict: PASS  rc=0
```

## A40-E22b-clock-b16-swap-s0 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b16-swap-s0.log):
```
[decide] 2026-11-21 08:46:00 ar2_clock_e30_b16/on swap_blocks seed=4300103 frame=512/1000 hist=3 policy=0.6s elapsed=202s
[decide] 2026-11-21 08:46:13 ar2_clock_e30_b16/on swap_blocks seed=4300103 frame=544/1000 hist=3 policy=0.6s elapsed=214s
[decide] 2026-11-21 08:46:28 ar2_clock_e30_b16/on swap_blocks seed=4300103 frame=576/1000 hist=3 policy=0.6s elapsed=229s
[closed-loop] 2026-11-21 08:46:35 done  ar2_clock_e30_b16/on swap_blocks seed=4300103 success=True targets=592/1000 reward=1.0 lift=0.10325485467910767  276s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_clock_e30_b16/on    swap_blocks       35     1.00  [0.90,1.00]      1.00    1.00      586        -        -        -    0.6
ar2_clock_e30_p256_hid/onput_back_block    50     0.98  [0.90,1.00]      1.00    0.98      352        -        -        -    0.6
ar2_clock_e30_p256_hid/onswap_blocks       50     0.14  [0.07,0.26]      1.00    0.14      942        -        -        -    0.6
ar2_clock_e30_p256_vis/onput_back_block    50     0.98  [0.90,1.00]      1.00    0.98      352        -        -        -    0.7
ar2_clock_e30_p256_vis/onswap_blocks       50     0.14  [0.07,0.26]      1.00    0.14      942        -        -        -    0.7
ar2_prop_e30_p256_hid/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6
ar2_prop_e30_p256_vis/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_hid/on  35     5      30       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_vis/on  35     5      30       0        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 335 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-clock-b16-swap-s0.log):
```

[pool] 2026-11-21 16:00:31 exec A40-E22b-clock-b16-swap-s0 GPU 4 
[pool] 2026-11-21 16:00:32 A40-E22b-clock-b16-swap-s0: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b16-swap-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b16-swap-s0.md
[queue5] 2026-11-21 16:47:03 A40-E22b-clock-b16-swap-s0: DONE  swap_blocks/on n=35 lifted=35 s1=35 s2=35 s3=35 pressed=35 success=35 prog=1.00
```

## A40-E22b-clock-b16-swap-s1 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b16-swap-s1.log):
```
[decide] 2026-11-21 08:48:01 ar2_clock_e30_b16/on swap_blocks seed=4300105 frame=512/1000 hist=3 policy=0.6s elapsed=191s
[decide] 2026-11-21 08:48:17 ar2_clock_e30_b16/on swap_blocks seed=4300105 frame=544/1000 hist=3 policy=0.6s elapsed=208s
[decide] 2026-11-21 08:48:27 ar2_clock_e30_b16/on swap_blocks seed=4300105 frame=576/1000 hist=3 policy=0.6s elapsed=218s
[closed-loop] 2026-11-21 08:48:31 done  ar2_clock_e30_b16/on swap_blocks seed=4300105 success=True targets=582/1000 reward=1.0 lift=0.10091215372085571  259s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_clock_e30_b16/on    swap_blocks       37     1.00  [0.91,1.00]      1.00    1.00      586        -        -        -    0.6
ar2_clock_e30_p256_hid/onput_back_block    50     0.98  [0.90,1.00]      1.00    0.98      352        -        -        -    0.6
ar2_clock_e30_p256_hid/onswap_blocks       50     0.14  [0.07,0.26]      1.00    0.14      942        -        -        -    0.6
ar2_clock_e30_p256_vis/onput_back_block    50     0.98  [0.90,1.00]      1.00    0.98      352        -        -        -    0.7
ar2_clock_e30_p256_vis/onswap_blocks       50     0.14  [0.07,0.26]      1.00    0.14      942        -        -        -    0.7
ar2_prop_e30_p256_hid/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6
ar2_prop_e30_p256_vis/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_hid/on  37     5      32       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_vis/on  37     5      32       0        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 337 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-clock-b16-swap-s1.log):
```

[pool] 2026-11-21 16:03:13 exec A40-E22b-clock-b16-swap-s1 GPU 6 
[pool] 2026-11-21 16:03:15 A40-E22b-clock-b16-swap-s1: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b16-swap-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b16-swap-s1.md
[queue5] 2026-11-21 16:49:00 A40-E22b-clock-b16-swap-s1: DONE  swap_blocks/on n=37 lifted=37 s1=37 s2=37 s3=37 pressed=37 success=37 prog=1.00
```

## A40-E22b-clock-b16-swap-s2 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b16-swap-s2.log):
```

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_clock_e30_b16/on    swap_blocks       43     1.00  [0.92,1.00]      1.00    1.00      586        -        -        -    0.6
ar2_clock_e30_b8/on     swap_blocks        2     1.00  [0.34,1.00]      1.00    1.00      590        -        -        -    0.6
ar2_clock_e30_p256_hid/onput_back_block    50     0.98  [0.90,1.00]      1.00    0.98      352        -        -        -    0.6
ar2_clock_e30_p256_hid/onswap_blocks       50     0.14  [0.07,0.26]      1.00    0.14      942        -        -        -    0.6
ar2_clock_e30_p256_vis/onput_back_block    50     0.98  [0.90,1.00]      1.00    0.98      352        -        -        -    0.7
ar2_clock_e30_p256_vis/onswap_blocks       50     0.14  [0.07,0.26]      1.00    0.14      942        -        -        -    0.7
ar2_prop_e30_p256_hid/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6
ar2_prop_e30_p256_vis/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b8/on        2     2       0       0        0  1.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_hid/on  43     6      37       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_vis/on  43     6      37       0        0  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on   2     0       2       0        0  0.500
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on   2     0       2       0        0  0.500
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 345 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-clock-b16-swap-s2.log):
```

[pool] 2026-11-21 16:11:48 exec A40-E22b-clock-b16-swap-s2 GPU 3 
[pool] 2026-11-21 16:11:50 A40-E22b-clock-b16-swap-s2: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b16-swap-s2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b16-swap-s2.md
[queue5] 2026-11-21 16:57:11 A40-E22b-clock-b16-swap-s2: DONE  swap_blocks/on n=43 lifted=43 s1=43 s2=43 s3=43 pressed=43 success=43 prog=1.00
```

## A40-E22b-clock-b16-swap-s3 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b16-swap-s3.log):
```

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
ar2_clock_e30_b16/on    swap_blocks       45     1.00  [0.92,1.00]      1.00    1.00      586        -        -        -    0.6
ar2_clock_e30_b8/on     swap_blocks        3     1.00  [0.44,1.00]      1.00    1.00      586        -        -        -    0.6
ar2_clock_e30_p256_hid/onput_back_block    50     0.98  [0.90,1.00]      1.00    0.98      352        -        -        -    0.6
ar2_clock_e30_p256_hid/onswap_blocks       50     0.14  [0.07,0.26]      1.00    0.14      942        -        -        -    0.6
ar2_clock_e30_p256_vis/onput_back_block    50     0.98  [0.90,1.00]      1.00    0.98      352        -        -        -    0.7
ar2_clock_e30_p256_vis/onswap_blocks       50     0.14  [0.07,0.26]      1.00    0.14      942        -        -        -    0.7
ar2_prop_e30_p256_hid/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6
ar2_prop_e30_p256_vis/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b8/on        3     3       0       0        0  1.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_hid/on  45     7      38       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_vis/on  45     7      38       0        0  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on   3     0       3       0        0  0.250
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on   3     0       3       0        0  0.250
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 348 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-clock-b16-swap-s3.log):
```

[pool] 2026-11-21 16:13:25 exec A40-E22b-clock-b16-swap-s3 GPU 7 
[pool] 2026-11-21 16:13:26 A40-E22b-clock-b16-swap-s3: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b16-swap-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b16-swap-s3.md
[queue5] 2026-11-21 17:00:07 A40-E22b-clock-b16-swap-s3: DONE  swap_blocks/on n=45 lifted=45 s1=45 s2=45 s3=45 pressed=45 success=45 prog=1.00
```

## A40-E22b-clock-b16-swap-s4 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b16-swap-s4.log):
```
ar2_clock_e30_p256_hid/onput_back_block    50     0.98  [0.90,1.00]      1.00    0.98      352        -        -        -    0.6
ar2_clock_e30_p256_hid/onswap_blocks       50     0.14  [0.07,0.26]      1.00    0.14      942        -        -        -    0.6
ar2_clock_e30_p256_vis/onput_back_block    50     0.98  [0.90,1.00]      1.00    0.98      352        -        -        -    0.7
ar2_clock_e30_p256_vis/onswap_blocks       50     0.14  [0.07,0.26]      1.00    0.14      942        -        -        -    0.7
ar2_prop_e30_p256_hid/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6
ar2_prop_e30_p256_vis/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b4/on        1     0       1       0        0  1.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b8/on       22    21       1       0        0  1.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_hid/on  50     7      43       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_vis/on  50     7      43       0        0  0.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_b8/on        1     0       0       1        0  1.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_hid/on   1     0       0       0        1  1.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_vis/on   1     0       0       0        1  1.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  22     2      19       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  22     2      19       0        1  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 373 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-clock-b16-swap-s4.log):
```

[pool] 2026-11-21 16:34:28 exec A40-E22b-clock-b16-swap-s4 GPU 0 
[pool] 2026-11-21 16:34:30 A40-E22b-clock-b16-swap-s4: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b16-swap-s4.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b16-swap-s4.md
[queue5] 2026-11-21 17:20:53 A40-E22b-clock-b16-swap-s4: DONE  swap_blocks/on n=50 lifted=50 s1=50 s2=50 s3=50 pressed=50 success=50 prog=1.00
```

## A40-E22b-clock-b8-swap-s0 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b8-swap-s0.log):
```
ar2_clock_e30_p256_hid/onput_back_block    50     0.98  [0.90,1.00]      1.00    0.98      352        -        -        -    0.6
ar2_clock_e30_p256_hid/onswap_blocks       50     0.14  [0.07,0.26]      1.00    0.14      942        -        -        -    0.6
ar2_clock_e30_p256_vis/onput_back_block    50     0.98  [0.90,1.00]      1.00    0.98      352        -        -        -    0.7
ar2_clock_e30_p256_vis/onswap_blocks       50     0.14  [0.07,0.26]      1.00    0.14      942        -        -        -    0.7
ar2_prop_e30_p256_hid/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6
ar2_prop_e30_p256_vis/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b4/on        6     4       2       0        0  0.500
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b8/on       40    39       1       0        0  1.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_hid/on  50     7      43       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_vis/on  50     7      43       0        0  0.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_b8/on        6     4       0       2        0  0.500
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_hid/on   6     0       4       1        1  0.375
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_vis/on   6     0       4       1        1  0.375
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  40     5      34       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  40     5      34       0        1  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 396 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-clock-b8-swap-s0.log):
```

[pool] 2026-11-21 16:47:57 exec A40-E22b-clock-b8-swap-s0 GPU 4 
[pool] 2026-11-21 16:47:59 A40-E22b-clock-b8-swap-s0: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b8-swap-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b8-swap-s0.md
[queue5] 2026-11-21 17:35:30 A40-E22b-clock-b8-swap-s0: DONE  swap_blocks/on n=40 lifted=40 s1=40 s2=40 s3=40 pressed=39 success=39 prog=0.99
```

## A40-E22b-clock-b8-swap-s1 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b8-swap-s1.log):
```
ar2_clock_e30_p256_hid/onput_back_block    50     0.98  [0.90,1.00]      1.00    0.98      352        -        -        -    0.6
ar2_clock_e30_p256_hid/onswap_blocks       50     0.14  [0.07,0.26]      1.00    0.14      942        -        -        -    0.6
ar2_clock_e30_p256_vis/onput_back_block    50     0.98  [0.90,1.00]      1.00    0.98      352        -        -        -    0.7
ar2_clock_e30_p256_vis/onswap_blocks       50     0.14  [0.07,0.26]      1.00    0.14      942        -        -        -    0.7
ar2_prop_e30_p256_hid/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6
ar2_prop_e30_p256_vis/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b4/on        7     4       3       0        0  0.250
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b8/on       43    42       1       0        0  1.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_hid/on  50     7      43       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_vis/on  50     7      43       0        0  0.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_b8/on        7     4       0       3        0  0.250
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_hid/on   7     0       4       1        2  0.375
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_vis/on   7     0       4       1        2  0.375
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  43     5      37       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  43     5      37       0        1  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 400 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-clock-b8-swap-s1.log):
```

[pool] 2026-11-21 16:50:06 exec A40-E22b-clock-b8-swap-s1 GPU 6 
[pool] 2026-11-21 16:50:08 A40-E22b-clock-b8-swap-s1: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b8-swap-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b8-swap-s1.md
[queue5] 2026-11-21 17:39:39 A40-E22b-clock-b8-swap-s1: DONE  swap_blocks/on n=44 lifted=44 s1=44 s2=44 s3=44 pressed=43 success=43 prog=0.99
```

## A40-E22b-clock-b8-swap-s2 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b8-swap-s2.log):
```
ar2_clock_e30_p256_hid/onput_back_block    50     0.98  [0.90,1.00]      1.00    0.98      352        -        -        -    0.6
ar2_clock_e30_p256_hid/onswap_blocks       50     0.14  [0.07,0.26]      1.00    0.14      942        -        -        -    0.6
ar2_clock_e30_p256_vis/onput_back_block    50     0.98  [0.90,1.00]      1.00    0.98      352        -        -        -    0.7
ar2_clock_e30_p256_vis/onswap_blocks       50     0.14  [0.07,0.26]      1.00    0.14      942        -        -        -    0.7
ar2_prop_e30_p256_hid/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6
ar2_prop_e30_p256_vis/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b4/on       10     6       4       0        0  0.125
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b8/on       47    46       1       0        0  1.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_hid/on  50     7      43       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_vis/on  50     7      43       0        0  0.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_b8/on       10     6       0       4        0  0.125
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_hid/on  10     0       6       1        3  0.125
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_vis/on  10     0       6       1        3  0.125
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  47     6      40       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  47     6      40       0        1  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 407 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-clock-b8-swap-s2.log):
```

[pool] 2026-11-21 16:58:10 exec A40-E22b-clock-b8-swap-s2 GPU 3 
[pool] 2026-11-21 16:58:12 A40-E22b-clock-b8-swap-s2: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b8-swap-s2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b8-swap-s2.md
[queue5] 2026-11-21 17:44:10 A40-E22b-clock-b8-swap-s2: DONE  swap_blocks/on n=47 lifted=47 s1=47 s2=47 s3=47 pressed=46 success=46 prog=0.99
```

## A40-E22b-clock-b8-swap-s3 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b8-swap-s3.log):
```
ar2_clock_e30_p256_hid/onput_back_block    50     0.98  [0.90,1.00]      1.00    0.98      352        -        -        -    0.6
ar2_clock_e30_p256_hid/onswap_blocks       50     0.14  [0.07,0.26]      1.00    0.14      942        -        -        -    0.6
ar2_clock_e30_p256_vis/onput_back_block    50     0.98  [0.90,1.00]      1.00    0.98      352        -        -        -    0.7
ar2_clock_e30_p256_vis/onswap_blocks       50     0.14  [0.07,0.26]      1.00    0.14      942        -        -        -    0.7
ar2_prop_e30_p256_hid/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6
ar2_prop_e30_p256_vis/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b4/on       10     6       4       0        0  0.125
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b8/on       49    48       1       0        0  1.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_hid/on  50     7      43       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_vis/on  50     7      43       0        0  0.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_b8/on       10     6       0       4        0  0.125
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_hid/on  10     0       6       1        3  0.125
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_vis/on  10     0       6       1        3  0.125
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  49     7      41       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  49     7      41       0        1  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 409 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-clock-b8-swap-s3.log):
```

[pool] 2026-11-21 16:59:14 exec A40-E22b-clock-b8-swap-s3 GPU 5 
[pool] 2026-11-21 16:59:16 A40-E22b-clock-b8-swap-s3: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b8-swap-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b8-swap-s3.md
[queue5] 2026-11-21 17:45:30 A40-E22b-clock-b8-swap-s3: DONE  swap_blocks/on n=49 lifted=49 s1=49 s2=49 s3=49 pressed=48 success=48 prog=0.99
```

## A40-E22b-clock-b8-swap-s4 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b8-swap-s4.log):
```
ar2_clock_e30_p256_hid/onput_back_block    50     0.98  [0.90,1.00]      1.00    0.98      352        -        -        -    0.6
ar2_clock_e30_p256_hid/onswap_blocks       50     0.14  [0.07,0.26]      1.00    0.14      942        -        -        -    0.6
ar2_clock_e30_p256_vis/onput_back_block    50     0.98  [0.90,1.00]      1.00    0.98      352        -        -        -    0.7
ar2_clock_e30_p256_vis/onswap_blocks       50     0.14  [0.07,0.26]      1.00    0.14      942        -        -        -    0.7
ar2_prop_e30_p256_hid/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6
ar2_prop_e30_p256_vis/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b4/on       14    10       4       0        0  0.125
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b8/on       50    49       1       0        0  1.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_hid/on  50     7      43       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_vis/on  50     7      43       0        0  0.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_b8/on       14     9       1       4        0  0.375
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_hid/on  14     0      10       1        3  0.012
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_vis/on  14     0      10       1        3  0.012
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  50     7      42       0        1  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 414 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-clock-b8-swap-s4.log):
```

[pool] 2026-11-21 17:01:25 exec A40-E22b-clock-b8-swap-s4 GPU 7 
[pool] 2026-11-21 17:01:27 A40-E22b-clock-b8-swap-s4: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b8-swap-s4.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b8-swap-s4.md
[queue5] 2026-11-21 17:49:41 A40-E22b-clock-b8-swap-s4: DONE  swap_blocks/on n=50 lifted=50 s1=50 s2=50 s3=50 pressed=49 success=49 prog=0.99
```

## A40-E22b-clock-b4-swap-s0 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b4-swap-s0.log):
```
ar2_prop_e30_p256_vis/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b4/on       29    21       8       0        0  0.008
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b8/on       50    49       1       0        0  1.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_hid/on  50     7      43       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_vis/on  50     7      43       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_prop_e30_b16/on        5     5       0       0        0  1.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_b8/on       29    20       1       8        0  0.039
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_hid/on  29     0      21       3        5  0.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_vis/on  29     0      21       3        5  0.000
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b16/on        5     4       0       1        0  1.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b16/on        5     5       0       0        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b16/on        5     0       0       5        0  0.062
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b16/on        5     0       0       5        0  0.062
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 434 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-clock-b4-swap-s0.log):
```

[pool] 2026-11-21 17:08:58 exec A40-E22b-clock-b4-swap-s0 GPU 1 
[pool] 2026-11-21 17:09:00 A40-E22b-clock-b4-swap-s0: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b4-swap-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b4-swap-s0.md
[queue5] 2026-11-21 18:04:24 A40-E22b-clock-b4-swap-s0: DONE  swap_blocks/on n=29 lifted=29 s1=29 s2=29 s3=29 pressed=24 success=21 prog=0.93
```

## A40-E22b-clock-b4-swap-s1 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b4-swap-s1.log):
```
ar2_prop_e30_p256_vis/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b4/on       38    27      11       0        0  0.001
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b8/on       50    49       1       0        0  1.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_hid/on  50     7      43       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_vis/on  50     7      43       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_prop_e30_b16/on       13    13       0       0        0  1.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_b8/on       38    26       1      11        0  0.006
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_hid/on  38     2      25       3        8  0.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_vis/on  38     2      25       3        8  0.000
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b16/on       13     9       0       4        0  0.125
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b16/on       13    12       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b16/on       13     1       0      12        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b16/on       13     1       0      12        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 451 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-clock-b4-swap-s1.log):
```

[pool] 2026-11-21 17:21:53 exec A40-E22b-clock-b4-swap-s1 GPU 0 
[pool] 2026-11-21 17:21:55 A40-E22b-clock-b4-swap-s1: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b4-swap-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b4-swap-s1.md
[queue5] 2026-11-21 18:17:41 A40-E22b-clock-b4-swap-s1: DONE  swap_blocks/on n=38 lifted=38 s1=38 s2=38 s3=38 pressed=30 success=27 prog=0.92
```

## A40-E22b-clock-b4-swap-s2 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b4-swap-s2.log):
```
ar2_prop_e30_p256_vis/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b4/on       47    36      11       0        0  0.001
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b8/on       50    49       1       0        0  1.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_hid/on  50     7      43       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_vis/on  50     7      43       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_prop_e30_b16/on       20    20       0       0        0  1.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_b8/on       47    35       1      11        0  0.006
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_hid/on  47     3      33       3        8  0.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_vis/on  47     3      33       3        8  0.000
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b16/on       20    14       0       6        0  0.031
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b16/on       20    19       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b16/on       20     2       0      18        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b16/on       20     2       0      18        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 467 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-clock-b4-swap-s2.log):
```

[pool] 2026-11-21 17:36:23 exec A40-E22b-clock-b4-swap-s2 GPU 4 
[pool] 2026-11-21 17:36:25 A40-E22b-clock-b4-swap-s2: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b4-swap-s2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b4-swap-s2.md
[queue5] 2026-11-21 18:29:15 A40-E22b-clock-b4-swap-s2: DONE  swap_blocks/on n=47 lifted=47 s1=47 s2=47 s3=47 pressed=39 success=36 prog=0.93
```

## A40-E22b-clock-b4-swap-s3 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b4-swap-s3.log):
```
ar2_prop_e30_p256_vis/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b4/on       49    38      11       0        0  0.001
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b8/on       50    49       1       0        0  1.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_hid/on  50     7      43       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_vis/on  50     7      43       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_prop_e30_b16/on       24    24       0       0        0  1.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_b8/on       49    37       1      11        0  0.006
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_hid/on  49     4      34       3        8  0.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_vis/on  49     4      34       3        8  0.000
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b16/on       24    17       0       7        0  0.016
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b16/on       24    23       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b16/on       24     4       0      20        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b16/on       24     4       0      20        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 473 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-clock-b4-swap-s3.log):
```

[pool] 2026-11-21 17:40:42 exec A40-E22b-clock-b4-swap-s3 GPU 6 
[pool] 2026-11-21 17:40:44 A40-E22b-clock-b4-swap-s3: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b4-swap-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b4-swap-s3.md
[queue5] 2026-11-21 18:33:51 A40-E22b-clock-b4-swap-s3: DONE  swap_blocks/on n=49 lifted=49 s1=49 s2=49 s3=49 pressed=41 success=38 prog=0.94
```

## A40-E22b-clock-b4-swap-s4 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b4-swap-s4.log):
```
ar2_prop_e30_p256_vis/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b4/on       50    39      11       0        0  0.001
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b8/on       50    49       1       0        0  1.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_hid/on  50     7      43       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_vis/on  50     7      43       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_prop_e30_b16/on       29    29       0       0        0  1.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_b8/on       50    38       1      11        0  0.006
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_hid/on  50     4      35       3        8  0.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_vis/on  50     4      35       3        8  0.000
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b16/on       29    21       0       8        0  0.008
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b16/on       29    28       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b16/on       29     5       0      24        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b16/on       29     5       0      24        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 479 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-clock-b4-swap-s4.log):
```

[pool] 2026-11-21 17:44:58 exec A40-E22b-clock-b4-swap-s4 GPU 3 
[pool] 2026-11-21 17:45:00 A40-E22b-clock-b4-swap-s4: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-clock-b4-swap-s4.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b4-swap-s4.md
[queue5] 2026-11-21 18:37:09 A40-E22b-clock-b4-swap-s4: DONE  swap_blocks/on n=50 lifted=50 s1=50 s2=50 s3=50 pressed=42 success=39 prog=0.94
```

## A40-E22b-ledger-b16-swap-s0 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b16-swap-s0.log):
```
ar2_prop_e30_p256_vis/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b4/on       49    38      11       0        0  0.001
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b8/on       50    49       1       0        0  1.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_hid/on  50     7      43       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_vis/on  50     7      43       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_prop_e30_b16/on       28    28       0       0        0  1.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_b8/on       49    37       1      11        0  0.006
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_hid/on  49     4      34       3        8  0.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_vis/on  49     4      34       3        8  0.000
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b16/on       28    20       0       8        0  0.008
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b16/on       28    27       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b16/on       28     5       0      23        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b16/on       28     5       0      23        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 477 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-ledger-b16-swap-s0.log):
```

[pool] 2026-11-21 17:46:36 exec A40-E22b-ledger-b16-swap-s0 GPU 5 
[pool] 2026-11-21 17:46:37 A40-E22b-ledger-b16-swap-s0: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b16-swap-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b16-swap-s0.md
[queue5] 2026-11-21 18:34:56 A40-E22b-ledger-b16-swap-s0: DONE  swap_blocks/on n=28 lifted=28 s1=28 s2=28 s3=28 pressed=28 success=28 prog=1.00
```

## A40-E22b-ledger-b16-swap-s1 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b16-swap-s1.log):
```
ar2_prop_e30_p256_vis/onput_back_block    50     1.00  [0.93,1.00]      1.00    1.00      343        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b4/on       50    39      11       0        0  0.001
  ar2_clock_e30_b16/on     vs ar2_clock_e30_b8/on       50    49       1       0        0  1.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_hid/on  50     7      43       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_vis/on  50     7      43       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_prop_e30_b16/on       30    30       0       0        0  1.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_b8/on       50    38       1      11        0  0.006
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_hid/on  50     4      35       3        8  0.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_vis/on  50     4      35       3        8  0.000
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b16/on       30    22       0       8        0  0.008
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b16/on       30    29       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b16/on       30     5       0      25        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b16/on       30     5       0      25        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 480 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-ledger-b16-swap-s1.log):
```

[pool] 2026-11-21 17:50:52 exec A40-E22b-ledger-b16-swap-s1 GPU 7 
[pool] 2026-11-21 17:50:54 A40-E22b-ledger-b16-swap-s1: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b16-swap-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b16-swap-s1.md
[queue5] 2026-11-21 18:37:52 A40-E22b-ledger-b16-swap-s1: DONE  swap_blocks/on n=30 lifted=30 s1=30 s2=30 s3=30 pressed=30 success=30 prog=1.00
```

## A40-E22b-ledger-b16-swap-s2 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b16-swap-s2.log):
```
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_vis/on  50     7      43       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_prop_e30_b16/on       41    41       0       0        0  1.000
  ar2_clock_e30_b16/on     vs ar2_prop_e30_b8/on         5     0       5       0        0  0.062
  ar2_clock_e30_b4/on      vs ar2_clock_e30_b8/on       50    38       1      11        0  0.006
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_hid/on  50     4      35       3        8  0.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_vis/on  50     4      35       3        8  0.000
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b16/on       41    30       0      11        0  0.001
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b8/on         5     0       4       0        1  0.125
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b16/on       41    40       0       1        0  1.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b8/on         5     0       5       0        0  0.062
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b16/on       41     6       0      35        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b8/on         5     0       0       0        5  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b16/on       41     6       0      35        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b8/on         5     0       0       0        5  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_b16/on      vs ar2_prop_e30_b8/on         5     0       5       0        0  0.062
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 496 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-ledger-b16-swap-s2.log):
```

[pool] 2026-11-21 18:05:25 exec A40-E22b-ledger-b16-swap-s2 GPU 1 
[pool] 2026-11-21 18:05:27 A40-E22b-ledger-b16-swap-s2: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b16-swap-s2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b16-swap-s2.md
[queue5] 2026-11-21 18:51:41 A40-E22b-ledger-b16-swap-s2: DONE  swap_blocks/on n=41 lifted=41 s1=41 s2=41 s3=41 pressed=41 success=41 prog=1.00
```

## A40-E22b-ledger-b16-swap-s3 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b16-swap-s3.log):
```
  ar2_clock_e30_b16/on     vs ar2_clock_e30_p256_vis/on  50     7      43       0        0  0.000
  ar2_clock_e30_b16/on     vs ar2_prop_e30_b16/on       47    47       0       0        0  1.000
  ar2_clock_e30_b16/on     vs ar2_prop_e30_b8/on        14     0      14       0        0  0.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_b8/on       50    38       1      11        0  0.006
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_hid/on  50     4      35       3        8  0.000
  ar2_clock_e30_b4/on      vs ar2_clock_e30_p256_vis/on  50     4      35       3        8  0.000
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b16/on       47    36       0      11        0  0.001
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b8/on        14     0       9       0        5  0.004
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b16/on       47    46       0       1        0  1.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b8/on        14     0      14       0        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b16/on       47     7       0      40        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b8/on        14     0       2       0       12  0.500
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b16/on       47     7       0      40        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b8/on        14     0       2       0       12  0.500
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_b16/on      vs ar2_prop_e30_b8/on        14     0      14       0        0  0.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 511 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-ledger-b16-swap-s3.log):
```

[pool] 2026-11-21 18:18:20 exec A40-E22b-ledger-b16-swap-s3 GPU 0 
[pool] 2026-11-21 18:18:22 A40-E22b-ledger-b16-swap-s3: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b16-swap-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b16-swap-s3.md
[queue5] 2026-11-21 19:05:00 A40-E22b-ledger-b16-swap-s3: DONE  swap_blocks/on n=47 lifted=47 s1=47 s2=47 s3=47 pressed=47 success=47 prog=1.00
```

## A40-E22b-ledger-b16-swap-s4 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b16-swap-s4.log):
```
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b16/on       50    39       0      11        0  0.001
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b4/on         1     0       0       0        1  1.000
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b8/on        23     0      15       0        8  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b16/on       50    49       0       1        0  1.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b4/on         1     0       1       0        0  1.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b8/on        23     0      22       0        1  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b16/on       50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b4/on         1     0       0       0        1  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b8/on        23     0       2       0       21  0.500
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b16/on       50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b4/on         1     0       0       0        1  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b8/on        23     0       2       0       21  0.500
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_b16/on      vs ar2_prop_e30_b4/on         1     0       1       0        0  1.000
  ar2_prop_e30_b16/on      vs ar2_prop_e30_b8/on        23     0      23       0        0  0.000
  ar2_prop_e30_b4/on       vs ar2_prop_e30_b8/on         1     0       0       0        1  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 524 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-ledger-b16-swap-s4.log):
```

[pool] 2026-11-21 18:30:13 exec A40-E22b-ledger-b16-swap-s4 GPU 4 
[pool] 2026-11-21 18:30:15 A40-E22b-ledger-b16-swap-s4: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b16-swap-s4.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b16-swap-s4.md
[queue5] 2026-11-21 19:17:05 A40-E22b-ledger-b16-swap-s4: DONE  swap_blocks/on n=50 lifted=50 s1=50 s2=50 s3=50 pressed=50 success=50 prog=1.00
```

## A40-E22b-ledger-b8-swap-s0 (done, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b8-swap-s0.log):
```
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b16/on       50    39       0      11        0  0.001
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b4/on         8     0       4       0        4  0.125
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b8/on        44     0      33       0       11  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b16/on       50    49       0       1        0  1.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b4/on         8     0       8       0        0  0.008
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b8/on        44     0      43       0        1  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b16/on       50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b4/on         8     0       1       0        7  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b8/on        44     0       5       0       39  0.062
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b16/on       50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b4/on         8     0       1       0        7  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b8/on        44     0       5       0       39  0.062
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_b16/on      vs ar2_prop_e30_b4/on         8     0       8       0        0  0.008
  ar2_prop_e30_b16/on      vs ar2_prop_e30_b8/on        44     0      44       0        0  0.000
  ar2_prop_e30_b4/on       vs ar2_prop_e30_b8/on         8     0       0       0        8  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 552 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-ledger-b8-swap-s0.log):
```

[pool] 2026-11-21 18:34:30 exec A40-E22b-ledger-b8-swap-s0 GPU 6 
[pool] 2026-11-21 18:34:32 A40-E22b-ledger-b8-swap-s0: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b8-swap-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b8-swap-s0.md
[queue5] 2026-11-21 19:47:40 A40-E22b-ledger-b8-swap-s0: DONE  swap_blocks/on n=44 lifted=44 s1=44 s2=44 s3=44 pressed=0 success=0 prog=0.67
```

## A40-E22b-ledger-b8-swap-s1 (done, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b8-swap-s1.log):
```
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b16/on       50    39       0      11        0  0.001
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b4/on         8     0       4       0        4  0.125
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b8/on        45     0      34       0       11  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b16/on       50    49       0       1        0  1.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b4/on         8     0       8       0        0  0.008
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b8/on        45     0      44       0        1  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b16/on       50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b4/on         8     0       1       0        7  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b8/on        45     0       5       0       40  0.062
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b16/on       50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b4/on         8     0       1       0        7  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b8/on        45     0       5       0       40  0.062
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_b16/on      vs ar2_prop_e30_b4/on         8     0       8       0        0  0.008
  ar2_prop_e30_b16/on      vs ar2_prop_e30_b8/on        45     0      45       0        0  0.000
  ar2_prop_e30_b4/on       vs ar2_prop_e30_b8/on         8     0       0       0        8  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 553 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-ledger-b8-swap-s1.log):
```

[pool] 2026-11-21 18:36:07 exec A40-E22b-ledger-b8-swap-s1 GPU 5 
[pool] 2026-11-21 18:36:08 A40-E22b-ledger-b8-swap-s1: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b8-swap-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b8-swap-s1.md
[queue5] 2026-11-21 19:47:42 A40-E22b-ledger-b8-swap-s1: DONE  swap_blocks/on n=45 lifted=45 s1=45 s2=45 s3=45 pressed=0 success=0 prog=0.67
```

## A40-E22b-ledger-b8-swap-s2 (done, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b8-swap-s2.log):
```
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b16/on       50    39       0      11        0  0.001
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b4/on         9     0       5       0        4  0.062
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b8/on        46     0      35       0       11  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b16/on       50    49       0       1        0  1.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b4/on         9     0       9       0        0  0.004
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b8/on        46     0      45       0        1  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b16/on       50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b4/on         9     0       1       0        8  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b8/on        46     0       6       0       40  0.031
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b16/on       50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b4/on         9     0       1       0        8  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b8/on        46     0       6       0       40  0.031
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_b16/on      vs ar2_prop_e30_b4/on         9     0       9       0        0  0.004
  ar2_prop_e30_b16/on      vs ar2_prop_e30_b8/on        46     0      46       0        0  0.000
  ar2_prop_e30_b4/on       vs ar2_prop_e30_b8/on         9     0       0       0        9  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 555 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-ledger-b8-swap-s2.log):
```

[pool] 2026-11-21 18:37:43 exec A40-E22b-ledger-b8-swap-s2 GPU 3 
[pool] 2026-11-21 18:37:45 A40-E22b-ledger-b8-swap-s2: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b8-swap-s2.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b8-swap-s2.md
[queue5] 2026-11-21 19:48:38 A40-E22b-ledger-b8-swap-s2: DONE  swap_blocks/on n=46 lifted=46 s1=46 s2=46 s3=46 pressed=0 success=0 prog=0.67
```

## A40-E22b-ledger-b8-swap-s3 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b8-swap-s3.log):
```
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b16/on       50    39       0      11        0  0.001
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b4/on        10     0       6       0        4  0.031
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b8/on        47     0      36       0       11  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b16/on       50    49       0       1        0  1.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b4/on        10     0      10       0        0  0.002
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b8/on        47     0      46       0        1  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b16/on       50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b4/on        10     0       1       0        9  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b8/on        47     0       7       0       40  0.016
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b16/on       50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b4/on        10     0       1       0        9  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b8/on        47     0       7       0       40  0.016
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_b16/on      vs ar2_prop_e30_b4/on        10     0      10       0        0  0.002
  ar2_prop_e30_b16/on      vs ar2_prop_e30_b8/on        47     0      47       0        0  0.000
  ar2_prop_e30_b4/on       vs ar2_prop_e30_b8/on        10     0       0       0       10  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 557 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-ledger-b8-swap-s3.log):
```

[pool] 2026-11-21 18:38:47 exec A40-E22b-ledger-b8-swap-s3 GPU 7 
[pool] 2026-11-21 18:38:49 A40-E22b-ledger-b8-swap-s3: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b8-swap-s3.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b8-swap-s3.md
[queue5] 2026-11-21 19:51:08 A40-E22b-ledger-b8-swap-s3: DONE  swap_blocks/on n=47 lifted=47 s1=47 s2=47 s3=47 pressed=0 success=0 prog=0.67
```

## A40-E22b-ledger-b8-swap-s4 (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b8-swap-s4.log):
```
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b16/on       50    39       0      11        0  0.001
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b4/on        19     0      14       0        5  0.000
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b8/on        50     0      39       0       11  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b16/on       50    49       0       1        0  1.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b4/on        19     0      18       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b8/on        50     0      49       0        1  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b16/on       50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b4/on        19     0       2       0       17  0.500
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b8/on        50     0       7       0       43  0.016
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b16/on       50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b4/on        19     0       2       0       17  0.500
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b8/on        50     0       7       0       43  0.016
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_b16/on      vs ar2_prop_e30_b4/on        19     0      19       0        0  0.000
  ar2_prop_e30_b16/on      vs ar2_prop_e30_b8/on        50     0      50       0        0  0.000
  ar2_prop_e30_b4/on       vs ar2_prop_e30_b8/on        19     0       0       0       19  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 569 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-ledger-b8-swap-s4.log):
```

[pool] 2026-11-21 18:52:47 exec A40-E22b-ledger-b8-swap-s4 GPU 1 
[pool] 2026-11-21 18:52:48 A40-E22b-ledger-b8-swap-s4: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b8-swap-s4.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b8-swap-s4.md
[queue5] 2026-11-21 20:05:15 A40-E22b-ledger-b8-swap-s4: DONE  swap_blocks/on n=50 lifted=50 s1=50 s2=50 s3=50 pressed=0 success=0 prog=0.67
```

## A40-E22b-ledger-b4-swap-s0 (done, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b4-swap-s0.log):
```
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b16/on       50    39       0      11        0  0.001
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b4/on        28     0      20       0        8  0.000
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b8/on        50     0      39       0       11  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b16/on       50    49       0       1        0  1.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b4/on        28     0      27       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b8/on        50     0      49       0        1  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b16/on       50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b4/on        28     0       4       0       24  0.125
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b8/on        50     0       7       0       43  0.016
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b16/on       50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b4/on        28     0       4       0       24  0.125
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b8/on        50     0       7       0       43  0.016
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_b16/on      vs ar2_prop_e30_b4/on        28     0      28       0        0  0.000
  ar2_prop_e30_b16/on      vs ar2_prop_e30_b8/on        50     0      50       0        0  0.000
  ar2_prop_e30_b4/on       vs ar2_prop_e30_b8/on        28     0       0       0       28  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 578 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-ledger-b4-swap-s0.log):
```

[pool] 2026-11-21 19:06:14 exec A40-E22b-ledger-b4-swap-s0 GPU 0 
[pool] 2026-11-21 19:06:16 A40-E22b-ledger-b4-swap-s0: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b4-swap-s0.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b4-swap-s0.md
[queue5] 2026-11-21 20:18:19 A40-E22b-ledger-b4-swap-s0: DONE  swap_blocks/on n=28 lifted=28 s1=28 s2=28 s3=28 pressed=0 success=0 prog=0.67
```

## A40-E22b-ledger-b4-swap-s1 (done, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b4-swap-s1.log):
```
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b16/on       50    39       0      11        0  0.001
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b4/on        35     0      25       0       10  0.000
  ar2_clock_e30_b4/on      vs ar2_prop_e30_b8/on        50     0      39       0       11  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_hid/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_clock_e30_p256_vis/on  50     7      42       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b16/on       50    49       0       1        0  1.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b4/on        35     0      34       0        1  0.000
  ar2_clock_e30_b8/on      vs ar2_prop_e30_b8/on        50     0      49       0        1  0.000
  ar2_clock_e30_p256_hid/on vs ar2_clock_e30_p256_vis/on 100    56       0       0       44  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b16/on       50     7       0      43        0  0.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b4/on        35     0       4       0       31  0.125
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_b8/on        50     0       7       0       43  0.016
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b16/on       50     7       0      43        0  0.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b4/on        35     0       4       0       31  0.125
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_b8/on        50     0       7       0       43  0.016
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_hid/on  50    49       0       1        0  1.000
  ar2_clock_e30_p256_vis/on vs ar2_prop_e30_p256_vis/on  50    49       0       1        0  1.000
  ar2_prop_e30_b16/on      vs ar2_prop_e30_b4/on        35     0      35       0        0  0.000
  ar2_prop_e30_b16/on      vs ar2_prop_e30_b8/on        50     0      50       0        0  0.000
  ar2_prop_e30_b4/on       vs ar2_prop_e30_b8/on        35     0       0       0       35  1.000
  ar2_prop_e30_p256_hid/on vs ar2_prop_e30_p256_vis/on  50    50       0       0        0  1.000

[summary] 585 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-ledger-b4-swap-s1.log):
```

[pool] 2026-11-21 19:18:03 exec A40-E22b-ledger-b4-swap-s1 GPU 4 
[pool] 2026-11-21 19:18:05 A40-E22b-ledger-b4-swap-s1: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b4-swap-s1.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b4-swap-s1.md
[queue5] 2026-11-21 20:28:33 A40-E22b-ledger-b4-swap-s1: DONE  swap_blocks/on n=35 lifted=35 s1=35 s2=35 s3=35 pressed=0 success=0 prog=0.67
```

## A40-E22b-ledger-b4-swap-s2 (running, attempt 1, GPU 5)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b4-swap-s2.log):
```
[decide] 2026-11-21 12:39:50 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=64/1000 hist=3 policy=0.6s elapsed=27s
[decide] 2026-11-21 12:40:01 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=96/1000 hist=3 policy=0.6s elapsed=38s
[decide] 2026-11-21 12:40:12 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=128/1000 hist=3 policy=0.6s elapsed=49s
[decide] 2026-11-21 12:40:22 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=160/1000 hist=3 policy=0.6s elapsed=59s
[decide] 2026-11-21 12:40:32 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=192/1000 hist=3 policy=0.6s elapsed=70s
[decide] 2026-11-21 12:40:43 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=224/1000 hist=3 policy=0.6s elapsed=81s
[decide] 2026-11-21 12:40:54 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=256/1000 hist=3 policy=0.6s elapsed=91s
[decide] 2026-11-21 12:41:07 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=288/1000 hist=3 policy=0.6s elapsed=105s
[decide] 2026-11-21 12:41:24 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=320/1000 hist=3 policy=0.6s elapsed=121s
[decide] 2026-11-21 12:41:40 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=352/1000 hist=3 policy=0.6s elapsed=138s
[decide] 2026-11-21 12:41:55 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=384/1000 hist=3 policy=0.6s elapsed=153s
[decide] 2026-11-21 12:42:08 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=416/1000 hist=3 policy=0.6s elapsed=165s
[decide] 2026-11-21 12:42:22 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=448/1000 hist=3 policy=0.6s elapsed=179s
[decide] 2026-11-21 12:42:33 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=480/1000 hist=3 policy=0.6s elapsed=190s
[decide] 2026-11-21 12:42:43 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=512/1000 hist=3 policy=0.6s elapsed=201s
[decide] 2026-11-21 12:42:54 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=544/1000 hist=3 policy=0.6s elapsed=211s
[decide] 2026-11-21 12:43:05 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=576/1000 hist=3 policy=0.6s elapsed=222s
[decide] 2026-11-21 12:43:15 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=608/1000 hist=3 policy=0.6s elapsed=233s
[decide] 2026-11-21 12:43:26 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=640/1000 hist=3 policy=0.6s elapsed=244s
[decide] 2026-11-21 12:43:43 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=672/1000 hist=3 policy=0.6s elapsed=261s
[decide] 2026-11-21 12:43:54 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=704/1000 hist=3 policy=0.6s elapsed=271s
[decide] 2026-11-21 12:44:04 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=736/1000 hist=3 policy=0.6s elapsed=282s
[decide] 2026-11-21 12:44:17 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=768/1000 hist=3 policy=0.6s elapsed=294s
[decide] 2026-11-21 12:44:34 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=800/1000 hist=3 policy=0.6s elapsed=311s
[decide] 2026-11-21 12:44:50 ar2_prop_e30_b4/on swap_blocks seed=4300078 frame=832/1000 hist=3 policy=0.6s elapsed=328s
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-ledger-b4-swap-s2.log):
```

[pool] 2026-11-21 19:47:29 exec A40-E22b-ledger-b4-swap-s2 GPU 5 
[pool] 2026-11-21 19:47:31 A40-E22b-ledger-b4-swap-s2: start (attempt 1/3) on GPU 5; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b4-swap-s2.log
```

## A40-E22b-ledger-b4-swap-s3 (running, attempt 1, GPU 6)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b4-swap-s3.log):
```
[decide] 2026-11-21 12:39:50 ar2_prop_e30_b4/on swap_blocks seed=4300080 frame=416/1000 hist=3 policy=0.5s elapsed=160s
[decide] 2026-11-21 12:40:01 ar2_prop_e30_b4/on swap_blocks seed=4300080 frame=448/1000 hist=3 policy=0.5s elapsed=171s
[decide] 2026-11-21 12:40:11 ar2_prop_e30_b4/on swap_blocks seed=4300080 frame=480/1000 hist=3 policy=0.5s elapsed=181s
[decide] 2026-11-21 12:40:21 ar2_prop_e30_b4/on swap_blocks seed=4300080 frame=512/1000 hist=3 policy=0.5s elapsed=191s
[decide] 2026-11-21 12:40:31 ar2_prop_e30_b4/on swap_blocks seed=4300080 frame=544/1000 hist=3 policy=0.5s elapsed=201s
[decide] 2026-11-21 12:40:41 ar2_prop_e30_b4/on swap_blocks seed=4300080 frame=576/1000 hist=3 policy=0.5s elapsed=211s
[decide] 2026-11-21 12:40:52 ar2_prop_e30_b4/on swap_blocks seed=4300080 frame=608/1000 hist=3 policy=0.5s elapsed=221s
[decide] 2026-11-21 12:41:04 ar2_prop_e30_b4/on swap_blocks seed=4300080 frame=640/1000 hist=3 policy=0.5s elapsed=234s
[decide] 2026-11-21 12:41:20 ar2_prop_e30_b4/on swap_blocks seed=4300080 frame=672/1000 hist=3 policy=0.5s elapsed=250s
[decide] 2026-11-21 12:41:34 ar2_prop_e30_b4/on swap_blocks seed=4300080 frame=704/1000 hist=3 policy=0.5s elapsed=263s
[decide] 2026-11-21 12:41:50 ar2_prop_e30_b4/on swap_blocks seed=4300080 frame=736/1000 hist=3 policy=0.5s elapsed=279s
[decide] 2026-11-21 12:42:00 ar2_prop_e30_b4/on swap_blocks seed=4300080 frame=768/1000 hist=3 policy=0.5s elapsed=289s
[decide] 2026-11-21 12:42:12 ar2_prop_e30_b4/on swap_blocks seed=4300080 frame=800/1000 hist=3 policy=0.5s elapsed=302s
[decide] 2026-11-21 12:42:27 ar2_prop_e30_b4/on swap_blocks seed=4300080 frame=832/1000 hist=3 policy=0.5s elapsed=316s
[decide] 2026-11-21 12:42:37 ar2_prop_e30_b4/on swap_blocks seed=4300080 frame=864/1000 hist=3 policy=0.5s elapsed=326s
[decide] 2026-11-21 12:42:47 ar2_prop_e30_b4/on swap_blocks seed=4300080 frame=896/1000 hist=3 policy=0.5s elapsed=337s
[decide] 2026-11-21 12:42:57 ar2_prop_e30_b4/on swap_blocks seed=4300080 frame=928/1000 hist=3 policy=0.5s elapsed=347s
[decide] 2026-11-21 12:43:07 ar2_prop_e30_b4/on swap_blocks seed=4300080 frame=960/1000 hist=3 policy=0.5s elapsed=357s
[decide] 2026-11-21 12:43:18 ar2_prop_e30_b4/on swap_blocks seed=4300080 frame=992/1000 hist=3 policy=0.5s elapsed=367s
[closed-loop] 2026-11-21 12:43:23 done  ar2_prop_e30_b4/on swap_blocks seed=4300080 success=False targets=1000/1000 reward=0.0 lift=0.10132604837417603  410s
[closed-loop] 2026-11-21 12:43:23 start ar2_prop_e30_b4/on swap_blocks seed=4300098 target_limit=1000 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e22/ar2_prop_e30_b4/on/swap_blocks/seed_4300098
[decide] 2026-11-21 12:44:06 ar2_prop_e30_b4/on swap_blocks seed=4300098 frame=0/1000 hist=0 policy=0.4s elapsed=5s
[decide] 2026-11-21 12:44:19 ar2_prop_e30_b4/on swap_blocks seed=4300098 frame=32/1000 hist=2 policy=0.5s elapsed=18s
[decide] 2026-11-21 12:44:34 ar2_prop_e30_b4/on swap_blocks seed=4300098 frame=64/1000 hist=3 policy=0.5s elapsed=33s
[decide] 2026-11-21 12:44:51 ar2_prop_e30_b4/on swap_blocks seed=4300098 frame=96/1000 hist=3 policy=0.5s elapsed=50s
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-ledger-b4-swap-s3.log):
```

[pool] 2026-11-21 19:47:29 exec A40-E22b-ledger-b4-swap-s3 GPU 6 
[pool] 2026-11-21 19:47:31 A40-E22b-ledger-b4-swap-s3: start (attempt 1/3) on GPU 6; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b4-swap-s3.log
```

## A40-E22b-ledger-b4-swap-s4 (running, attempt 1, GPU 3)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b4-swap-s4.log):
```
[decide] 2026-11-21 12:39:55 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=128/1000 hist=3 policy=0.6s elapsed=47s
[decide] 2026-11-21 12:40:05 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=160/1000 hist=3 policy=0.6s elapsed=58s
[decide] 2026-11-21 12:40:15 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=192/1000 hist=3 policy=0.6s elapsed=68s
[decide] 2026-11-21 12:40:26 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=224/1000 hist=3 policy=0.6s elapsed=78s
[decide] 2026-11-21 12:40:36 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=256/1000 hist=3 policy=0.6s elapsed=88s
[decide] 2026-11-21 12:40:47 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=288/1000 hist=3 policy=0.6s elapsed=99s
[decide] 2026-11-21 12:40:57 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=320/1000 hist=3 policy=0.6s elapsed=109s
[decide] 2026-11-21 12:41:14 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=352/1000 hist=3 policy=0.6s elapsed=127s
[decide] 2026-11-21 12:41:30 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=384/1000 hist=3 policy=0.6s elapsed=143s
[decide] 2026-11-21 12:41:43 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=416/1000 hist=3 policy=0.6s elapsed=155s
[decide] 2026-11-21 12:41:58 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=448/1000 hist=3 policy=0.6s elapsed=170s
[decide] 2026-11-21 12:42:10 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=480/1000 hist=3 policy=0.6s elapsed=182s
[decide] 2026-11-21 12:42:24 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=512/1000 hist=3 policy=0.6s elapsed=197s
[decide] 2026-11-21 12:42:34 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=544/1000 hist=3 policy=0.6s elapsed=207s
[decide] 2026-11-21 12:42:45 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=576/1000 hist=3 policy=0.6s elapsed=217s
[decide] 2026-11-21 12:42:55 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=608/1000 hist=3 policy=0.6s elapsed=227s
[decide] 2026-11-21 12:43:05 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=640/1000 hist=3 policy=0.6s elapsed=237s
[decide] 2026-11-21 12:43:15 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=672/1000 hist=3 policy=0.6s elapsed=248s
[decide] 2026-11-21 12:43:26 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=704/1000 hist=3 policy=0.6s elapsed=258s
[decide] 2026-11-21 12:43:43 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=736/1000 hist=3 policy=0.6s elapsed=275s
[decide] 2026-11-21 12:43:53 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=768/1000 hist=3 policy=0.6s elapsed=285s
[decide] 2026-11-21 12:44:03 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=800/1000 hist=3 policy=0.6s elapsed=296s
[decide] 2026-11-21 12:44:16 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=832/1000 hist=3 policy=0.6s elapsed=308s
[decide] 2026-11-21 12:44:33 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=864/1000 hist=3 policy=0.6s elapsed=325s
[decide] 2026-11-21 12:44:50 ar2_prop_e30_b4/on swap_blocks seed=4300081 frame=896/1000 hist=3 policy=0.6s elapsed=342s
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22b-ledger-b4-swap-s4.log):
```

[pool] 2026-11-21 19:48:33 exec A40-E22b-ledger-b4-swap-s4 GPU 3 
[pool] 2026-11-21 19:48:35 A40-E22b-ledger-b4-swap-s4: start (attempt 1/3) on GPU 3; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22b-ledger-b4-swap-s4.log
```

## A40-E21-verdict (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-verdict.log):
```

[queue5] 2026-11-21 02:34:11 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/e21_verdict.py
untreated   50/50 finished; failures {}; vs untreated {'n': 50, 'only_this': 0, 'only_untreated': 0}
a            0/50 finished; failures {'pressed before s3': 50}; vs untreated {'n': 50, 'only_this': 0, 'only_untreated': 50}
b            0/50 finished; failures {'pressed after s3': 31, 'kept moving': 19}; vs untreated {'n': 50, 'only_this': 0, 'only_untreated': 50}
c            0/50 finished; failures {'kept moving': 50}; vs untreated {'n': 50, 'only_this': 0, 'only_untreated': 50}
d           50/50 finished; failures {}; vs untreated {'n': 50, 'only_this': 0, 'only_untreated': 0}
e            0/50 finished; failures {'pressed after s3': 50}; vs untreated {'n': 50, 'only_this': 0, 'only_untreated': 50}
c_put       41/50 finished; failures {'unclassified': 9}; vs untreated {'n': 27, 'only_this': 0, 'only_untreated': 4}
E21 VERDICT: time code TIME CODE READ; dependence DEPENDS; content DOES NOT READ CONTENT; put with clock off 41/50 (reported only; expectation >= 45/50)
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E21-verdict.log):
```

[pool] 2026-11-21 02:34:09 exec A40-E21-verdict GPU None 
[pool] 2026-11-21 02:34:11 A40-E21-verdict: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E21-verdict.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-verdict.md
[queue5] 2026-11-21 02:36:13 A40-E21-verdict: PASS  rc=0
```

## A40-E22a-fetch-256 (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22a-fetch-256.log):
```
[e22a100] 2026-11-21 15:16:27 waiting for diag/e22_a100/E22_A100_256.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 15:21:27 waiting for diag/e22_a100/E22_A100_256.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 15:26:28 waiting for diag/e22_a100/E22_A100_256.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 15:31:28 waiting for diag/e22_a100/E22_A100_256.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 15:36:29 waiting for diag/e22_a100/E22_A100_256.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 15:41:29 waiting for diag/e22_a100/E22_A100_256.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 15:46:30 waiting for diag/e22_a100/E22_A100_256.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 15:51:30 waiting for diag/e22_a100/E22_A100_256.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 15:56:31 waiting for diag/e22_a100/E22_A100_256.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 16:01:31 waiting for diag/e22_a100/E22_A100_256.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 16:06:32 waiting for diag/e22_a100/E22_A100_256.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 16:11:33 waiting for diag/e22_a100/E22_A100_256.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 16:16:33 waiting for diag/e22_a100/E22_A100_256.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 16:21:34 waiting for diag/e22_a100/E22_A100_256.tar.gz (the A100 uploads it after its E22a cards)
[relay] get hhyfred/memwam-diag-v1/diag/e22_a100/E22_A100_256.tar.gz -> /workspace/FastWAM-memory2/outputs/fullft/relay_in/e22_a100/E22_A100_256.tar.gz (996721451 bytes)
[relay] get hhyfred/memwam-diag-v1/diag/e22_a100/E22_A100_256.tar.gz.sha256 -> /workspace/FastWAM-memory2/outputs/fullft/relay_in/e22_a100/E22_A100_256.tar.gz.sha256 (86 bytes)
[relay] get hhyfred/memwam-diag-v1/diag/e22_a100/E22_A100_256_seeds.json -> /workspace/FastWAM-memory2/outputs/fullft/relay_in/e22_a100/E22_A100_256_seeds.json (938 bytes)
E22_A100_256.tar.gz: OK
[e22a100] 2026-11-21 16:28:27 same first 50 seeds (swap / put) on both machines
[e22a100] 2026-11-21 16:28:50 unpacked; episodes per label now:
     17 ar2_clock_e30_b16
    100 ar2_clock_e30_p256_hid
    100 ar2_clock_e30_p256_vis
     50 ar2_prop_e30_p256_hid
     50 ar2_prop_e30_p256_vis
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22a-fetch-256.log):
```

[pool] 2026-11-20 17:18:55 exec A40-E22a-fetch-256 GPU None 
[pool] 2026-11-20 17:18:57 A40-E22a-fetch-256: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22a-fetch-256.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22a-fetch-256.md
[queue5] 2026-11-21 16:28:53 A40-E22a-fetch-256: PASS  rc=0
```

## A40-E22a-fetch-all (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22a-fetch-all.log):
```
[e22a100] 2026-11-21 18:42:01 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 18:47:01 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 18:52:02 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 18:57:02 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 19:02:03 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 19:07:03 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 19:12:04 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 19:17:05 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 19:22:05 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 19:27:06 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 19:32:06 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 19:37:07 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 19:42:07 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 19:47:09 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 19:52:10 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 19:57:11 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 20:02:12 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 20:07:12 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 20:12:13 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 20:17:13 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 20:22:14 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 20:27:14 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 20:32:15 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 20:37:15 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
[e22a100] 2026-11-21 20:42:16 waiting for diag/e22_a100/E22_A100_all.tar.gz (the A100 uploads it after its E22a cards)
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22a-fetch-all.log):
```

[pool] 2026-11-20 17:18:55 exec A40-E22a-fetch-all GPU None 
[pool] 2026-11-20 17:18:57 A40-E22a-fetch-all: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22a-fetch-all.log
```

## A40-E22a-verdict-256 (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22a-verdict-256.log):
```

[queue5] 2026-11-21 16:29:05 $ bash -c cd /workspace/FastWAM-memory2 && PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/e22_verdict.py --part a
ar2_clock_e30  swap_blocks     pause   64: valid pairs 50, vis-only 0, hid-only 3, Delta -3, p 0.2500, hidden 50/50, slot share 0.17 -> NOT HURT
ar2_clock_e30  swap_blocks     pause  256: valid pairs 50, vis-only 0, hid-only 0, Delta +0, p 1.0000, hidden 7/50, slot share 0.42 -> FLOOR NOT MET
ar2_clock_e30  swap_blocks     pause 1024: valid pairs 0, vis-only 0, hid-only 0, Delta +0, p 1.0000, hidden 0/50, slot share - -> WAIT
ar2_prop_e30   swap_blocks     pause   64: valid pairs 50, vis-only 0, hid-only 0, Delta +0, p 1.0000, hidden 50/50, slot share 0.00 -> NOT HURT
ar2_prop_e30   swap_blocks     pause 1024: valid pairs 0, vis-only 0, hid-only 0, Delta +0, p 1.0000, hidden 0/50, slot share - -> WAIT
E22a swap_blocks: WAIT
ar2_clock_e30  put_back_block  pause   64: valid pairs 50, vis-only 0, hid-only 0, Delta +0, p 1.0000, hidden 49/50, slot share 0.17 -> NOT HURT
ar2_clock_e30  put_back_block  pause  256: valid pairs 50, vis-only 0, hid-only 0, Delta +0, p 1.0000, hidden 49/50, slot share 0.44 -> NOT HURT
ar2_prop_e30   put_back_block  pause   64: valid pairs 50, vis-only 0, hid-only 0, Delta +0, p 1.0000, hidden 50/50, slot share 0.00 -> NOT HURT
ar2_prop_e30   put_back_block  pause  256: valid pairs 50, vis-only 0, hid-only 0, Delta +0, p 1.0000, hidden 50/50, slot share 0.00 -> NOT HURT
E22a put_back_block: NO DOSE EFFECT
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E22a-verdict-256.log):
```

[pool] 2026-11-21 16:29:03 exec A40-E22a-verdict-256 GPU None 
[pool] 2026-11-21 16:29:05 A40-E22a-verdict-256: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E22a-verdict-256.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22a-verdict-256.md
[queue5] 2026-11-21 16:31:13 A40-E22a-verdict-256: PASS  rc=0
```

## A40-fetch-rearrange_clock-e30 (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearrange_clock-e30.log):
```
[fetch] 2026-11-21 10:28:22 waiting for exports/rearrange_clock_e30 on the relay
[fetch] 2026-11-21 10:33:22 waiting for exports/rearrange_clock_e30 on the relay
[fetch] 2026-11-21 10:38:23 waiting for exports/rearrange_clock_e30 on the relay
[fetch] 2026-11-21 10:43:24 waiting for exports/rearrange_clock_e30 on the relay
[fetch] 2026-11-21 10:48:24 waiting for exports/rearrange_clock_e30 on the relay
[fetch] 2026-11-21 10:53:25 waiting for exports/rearrange_clock_e30 on the relay
[fetch] 2026-11-21 10:58:25 waiting for exports/rearrange_clock_e30 on the relay
[fetch] 2026-11-21 11:03:26 waiting for exports/rearrange_clock_e30 on the relay
[fetch] 2026-11-21 11:08:26 waiting for exports/rearrange_clock_e30 on the relay
[fetch] 2026-11-21 11:13:27 waiting for exports/rearrange_clock_e30 on the relay
[fetch] 2026-11-21 11:18:27 waiting for exports/rearrange_clock_e30 on the relay
[fetch] 2026-11-21 11:23:28 waiting for exports/rearrange_clock_e30 on the relay
[fetch] 2026-11-21 11:28:28 waiting for exports/rearrange_clock_e30 on the relay
[fetch] 2026-11-21 11:33:29 waiting for exports/rearrange_clock_e30 on the relay
[fetch] 2026-11-21 11:38:29 waiting for exports/rearrange_clock_e30 on the relay
[fetch] disk before: /dev/sdb         19T  9.6T  7.7T  56% /workspace/FastWAM-memory2
[fetch] 2026-11-21 11:43:30 fetching rearrange_clock_e30 (attempt 1)
[relay] get hhyfred/memwam-fullft/exports/rearrange_clock_e30/export_e30.pt -> /workspace/FastWAM-memory2/outputs/fullft/exports/rearrange_clock_e30/export_e30.pt (12042325765 bytes)
[relay] get hhyfred/memwam-fullft/exports/rearrange_clock_e30/export_e30.pt.sha256 -> /workspace/FastWAM-memory2/outputs/fullft/exports/rearrange_clock_e30/export_e30.pt.sha256 (80 bytes)
export_e30.pt: OK
total 11760100
drwxr-xr-x  2 root root        4096 Nov 21 11:51 .
drwxr-xr-x 34 root root        4096 Nov 21 11:53 ..
-rw-r--r--  1 root root 12042325765 Nov 21 11:51 export_e30.pt
-rw-r--r--  1 root root          80 Nov 21 11:51 export_e30.pt.sha256
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-rearrange_clock-e30.log):
```

[pool] 2026-11-19 19:17:58 exec A40-fetch-rearrange_clock-e30 GPU None 
[pool] 2026-11-19 19:18:00 A40-fetch-rearrange_clock-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-rearrange_clock-e30.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-rearrange_clock-e30.md
[queue5] 2026-11-21 19:54:02 A40-fetch-rearrange_clock-e30: PASS  rc=0
```

## A40-rearrange_clock-smoke (done, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-rearrange_clock-smoke.log):
```
[closed-loop] 2026-11-21 12:07:42 1 scenes x modes ['on'] -> labels {'on': 'rearrange_clock_e30_smoke'}; checkpoint /workspace/FastWAM-memory2/outputs/fullft/exports/rearrange_clock_e30/export_e30.pt; T5 on CPU; max_targets=official
[closed-loop] WARNING dense config was recorded for sm9.0; this GPU is sm8.6: TORCH_EXTENSIONS_DIR -> /workspace/FastWAM/outputs/fused_environment_memory_v2_sm86/torch_extensions (give --extensions-dir to reuse built kernels)
[closed-loop] 2026-11-21 12:07:42 start rearrange_clock_e30_smoke/on rearrange_blocks seed=4300000 target_limit=700 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e16smoke/rearrange_clock_e30_smoke/on/rearrange_blocks/seed_4300000
[fullft] text from the training cache (rearrange_blocks/episode_0000000, 50 episodes share it; fingerprint 73739a6aa417)
/restore-tmp/dense_joint_v1/data_path.py:16: UserWarning: The given NumPy array is not writable, and PyTorch does not support non-writable tensors. This means writing to this tensor will result in undefined behavior. You may want to copy the array to protect its data or make it writable before converting it to a tensor. This type of warning will be suppressed for the rest of this program. (Triggered internally at /opt/pytorch/pytorch/torch/csrc/utils/tensor_numpy.cpp:206.)
  return torch.stack([TF.resize(torch.from_numpy(np.ascontiguousarray(a)).permute(2,0,1).float()/255.,
[decide] 2026-11-21 12:08:24 rearrange_clock_e30_smoke/on rearrange_blocks seed=4300000 frame=0/700 hist=0 policy=0.7s elapsed=5s
[decide] 2026-11-21 12:08:35 rearrange_clock_e30_smoke/on rearrange_blocks seed=4300000 frame=32/700 hist=2 policy=0.6s elapsed=16s
[decide] 2026-11-21 12:08:45 rearrange_clock_e30_smoke/on rearrange_blocks seed=4300000 frame=64/700 hist=3 policy=0.6s elapsed=26s
[decide] 2026-11-21 12:08:55 rearrange_clock_e30_smoke/on rearrange_blocks seed=4300000 frame=96/700 hist=3 policy=0.6s elapsed=36s
[decide] 2026-11-21 12:09:05 rearrange_clock_e30_smoke/on rearrange_blocks seed=4300000 frame=128/700 hist=3 policy=0.6s elapsed=45s
[decide] 2026-11-21 12:09:17 rearrange_clock_e30_smoke/on rearrange_blocks seed=4300000 frame=160/700 hist=3 policy=0.6s elapsed=58s
[decide] 2026-11-21 12:09:32 rearrange_clock_e30_smoke/on rearrange_blocks seed=4300000 frame=192/700 hist=3 policy=0.6s elapsed=73s
[decide] 2026-11-21 12:09:47 rearrange_clock_e30_smoke/on rearrange_blocks seed=4300000 frame=224/700 hist=3 policy=0.6s elapsed=88s
[decide] 2026-11-21 12:09:57 rearrange_clock_e30_smoke/on rearrange_blocks seed=4300000 frame=256/700 hist=3 policy=0.6s elapsed=98s
[decide] 2026-11-21 12:10:11 rearrange_clock_e30_smoke/on rearrange_blocks seed=4300000 frame=288/700 hist=3 policy=0.6s elapsed=112s
[decide] 2026-11-21 12:10:30 rearrange_clock_e30_smoke/on rearrange_blocks seed=4300000 frame=320/700 hist=3 policy=0.6s elapsed=131s
[decide] 2026-11-21 12:10:40 rearrange_clock_e30_smoke/on rearrange_blocks seed=4300000 frame=352/700 hist=3 policy=0.6s elapsed=141s
[decide] 2026-11-21 12:10:50 rearrange_clock_e30_smoke/on rearrange_blocks seed=4300000 frame=384/700 hist=3 policy=0.6s elapsed=151s
[closed-loop] 2026-11-21 12:10:58 done  rearrange_clock_e30_smoke/on rearrange_blocks seed=4300000 success=True targets=397/700 reward=1.0 lift=0.12106055021286011  196s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
rearrange_clock_e30_smoke/onrearrange_blocks   1     1.00  [0.21,1.00]      1.00    1.00      397        -        -        -    0.6

[summary] 1 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e16smoke/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-rearrange_clock-smoke.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-21 20:11:01 A40-rearrange_clock-smoke: PASS  rearrange_blocks/on n=1  prog=0.00
```

## A40-E16-rearrange-clock-s0 (running, attempt 1, GPU 1)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E16-rearrange-clock-s0.log):
```
[decide] 2026-11-21 12:39:36 rearrange_clock_e30/on rearrange_blocks seed=4300060 frame=448/700 hist=3 policy=0.6s elapsed=176s
[decide] 2026-11-21 12:39:46 rearrange_clock_e30/on rearrange_blocks seed=4300060 frame=480/700 hist=3 policy=0.6s elapsed=186s
[decide] 2026-11-21 12:39:56 rearrange_clock_e30/on rearrange_blocks seed=4300060 frame=512/700 hist=3 policy=0.6s elapsed=196s
[decide] 2026-11-21 12:40:06 rearrange_clock_e30/on rearrange_blocks seed=4300060 frame=544/700 hist=3 policy=0.6s elapsed=206s
[decide] 2026-11-21 12:40:15 rearrange_clock_e30/on rearrange_blocks seed=4300060 frame=576/700 hist=3 policy=0.6s elapsed=216s
[decide] 2026-11-21 12:40:25 rearrange_clock_e30/on rearrange_blocks seed=4300060 frame=608/700 hist=3 policy=0.6s elapsed=225s
[decide] 2026-11-21 12:40:35 rearrange_clock_e30/on rearrange_blocks seed=4300060 frame=640/700 hist=3 policy=0.6s elapsed=235s
[decide] 2026-11-21 12:40:45 rearrange_clock_e30/on rearrange_blocks seed=4300060 frame=672/700 hist=3 policy=0.6s elapsed=245s
[closed-loop] 2026-11-21 12:40:56 done  rearrange_clock_e30/on rearrange_blocks seed=4300060 success=False targets=700/700 reward=0.0 lift=0.1237560510635376  297s
[closed-loop] 2026-11-21 12:40:56 start rearrange_clock_e30/on rearrange_blocks seed=4300070 target_limit=700 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e16/rearrange_clock_e30/on/rearrange_blocks/seed_4300070
[decide] 2026-11-21 12:41:51 rearrange_clock_e30/on rearrange_blocks seed=4300070 frame=0/700 hist=0 policy=0.4s elapsed=10s
[decide] 2026-11-21 12:42:01 rearrange_clock_e30/on rearrange_blocks seed=4300070 frame=32/700 hist=2 policy=0.6s elapsed=20s
[decide] 2026-11-21 12:42:17 rearrange_clock_e30/on rearrange_blocks seed=4300070 frame=64/700 hist=3 policy=0.6s elapsed=36s
[decide] 2026-11-21 12:42:28 rearrange_clock_e30/on rearrange_blocks seed=4300070 frame=96/700 hist=3 policy=0.6s elapsed=47s
[decide] 2026-11-21 12:42:38 rearrange_clock_e30/on rearrange_blocks seed=4300070 frame=128/700 hist=3 policy=0.6s elapsed=56s
[decide] 2026-11-21 12:42:48 rearrange_clock_e30/on rearrange_blocks seed=4300070 frame=160/700 hist=3 policy=0.6s elapsed=67s
[decide] 2026-11-21 12:42:58 rearrange_clock_e30/on rearrange_blocks seed=4300070 frame=192/700 hist=3 policy=0.6s elapsed=76s
[decide] 2026-11-21 12:43:08 rearrange_clock_e30/on rearrange_blocks seed=4300070 frame=224/700 hist=3 policy=0.6s elapsed=86s
[decide] 2026-11-21 12:43:18 rearrange_clock_e30/on rearrange_blocks seed=4300070 frame=256/700 hist=3 policy=0.6s elapsed=97s
[decide] 2026-11-21 12:43:30 rearrange_clock_e30/on rearrange_blocks seed=4300070 frame=288/700 hist=3 policy=0.6s elapsed=109s
[decide] 2026-11-21 12:43:45 rearrange_clock_e30/on rearrange_blocks seed=4300070 frame=320/700 hist=3 policy=0.6s elapsed=124s
[decide] 2026-11-21 12:43:55 rearrange_clock_e30/on rearrange_blocks seed=4300070 frame=352/700 hist=3 policy=0.6s elapsed=134s
[decide] 2026-11-21 12:44:05 rearrange_clock_e30/on rearrange_blocks seed=4300070 frame=384/700 hist=3 policy=0.6s elapsed=144s
[closed-loop] 2026-11-21 12:44:09 done  rearrange_clock_e30/on rearrange_blocks seed=4300070 success=True targets=388/700 reward=1.0 lift=0.12234824895858765  192s
[closed-loop] 2026-11-21 12:44:09 start rearrange_clock_e30/on rearrange_blocks seed=4300080 target_limit=700 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e16/rearrange_clock_e30/on/rearrange_blocks/seed_4300080
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E16-rearrange-clock-s0.log):
```

[pool] 2026-11-21 20:12:15 exec A40-E16-rearrange-clock-s0 GPU 1 
[pool] 2026-11-21 20:12:17 A40-E16-rearrange-clock-s0: start (attempt 1/3) on GPU 1; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E16-rearrange-clock-s0.log
```

## A40-E16-rearrange-clock-s1 (running, attempt 1, GPU 0)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E16-rearrange-clock-s1.log):
```
[decide] 2026-11-21 12:39:52 rearrange_clock_e30/on rearrange_blocks seed=4300041 frame=160/700 hist=3 policy=0.6s elapsed=60s
[decide] 2026-11-21 12:40:02 rearrange_clock_e30/on rearrange_blocks seed=4300041 frame=192/700 hist=3 policy=0.6s elapsed=70s
[decide] 2026-11-21 12:40:12 rearrange_clock_e30/on rearrange_blocks seed=4300041 frame=224/700 hist=3 policy=0.6s elapsed=80s
[decide] 2026-11-21 12:40:22 rearrange_clock_e30/on rearrange_blocks seed=4300041 frame=256/700 hist=3 policy=0.6s elapsed=90s
[decide] 2026-11-21 12:40:32 rearrange_clock_e30/on rearrange_blocks seed=4300041 frame=288/700 hist=3 policy=0.6s elapsed=100s
[decide] 2026-11-21 12:40:42 rearrange_clock_e30/on rearrange_blocks seed=4300041 frame=320/700 hist=3 policy=0.6s elapsed=110s
[decide] 2026-11-21 12:40:52 rearrange_clock_e30/on rearrange_blocks seed=4300041 frame=352/700 hist=3 policy=0.6s elapsed=120s
[decide] 2026-11-21 12:41:04 rearrange_clock_e30/on rearrange_blocks seed=4300041 frame=384/700 hist=3 policy=0.6s elapsed=132s
[closed-loop] 2026-11-21 12:41:09 done  rearrange_clock_e30/on rearrange_blocks seed=4300041 success=True targets=391/700 reward=1.0 lift=0.12199437618255615  188s
[closed-loop] 2026-11-21 12:41:09 start rearrange_clock_e30/on rearrange_blocks seed=4300051 target_limit=700 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e16/rearrange_clock_e30/on/rearrange_blocks/seed_4300051
[decide] 2026-11-21 12:41:59 rearrange_clock_e30/on rearrange_blocks seed=4300051 frame=0/700 hist=0 policy=0.4s elapsed=5s
[decide] 2026-11-21 12:42:12 rearrange_clock_e30/on rearrange_blocks seed=4300051 frame=32/700 hist=2 policy=0.6s elapsed=18s
[decide] 2026-11-21 12:42:26 rearrange_clock_e30/on rearrange_blocks seed=4300051 frame=64/700 hist=3 policy=0.6s elapsed=32s
[decide] 2026-11-21 12:42:36 rearrange_clock_e30/on rearrange_blocks seed=4300051 frame=96/700 hist=3 policy=0.6s elapsed=42s
[decide] 2026-11-21 12:42:46 rearrange_clock_e30/on rearrange_blocks seed=4300051 frame=128/700 hist=3 policy=0.6s elapsed=52s
[decide] 2026-11-21 12:42:56 rearrange_clock_e30/on rearrange_blocks seed=4300051 frame=160/700 hist=3 policy=0.6s elapsed=62s
[decide] 2026-11-21 12:43:06 rearrange_clock_e30/on rearrange_blocks seed=4300051 frame=192/700 hist=3 policy=0.6s elapsed=72s
[decide] 2026-11-21 12:43:15 rearrange_clock_e30/on rearrange_blocks seed=4300051 frame=224/700 hist=3 policy=0.6s elapsed=81s
[decide] 2026-11-21 12:43:25 rearrange_clock_e30/on rearrange_blocks seed=4300051 frame=256/700 hist=3 policy=0.6s elapsed=91s
[decide] 2026-11-21 12:43:42 rearrange_clock_e30/on rearrange_blocks seed=4300051 frame=288/700 hist=3 policy=0.6s elapsed=108s
[decide] 2026-11-21 12:43:53 rearrange_clock_e30/on rearrange_blocks seed=4300051 frame=320/700 hist=3 policy=0.6s elapsed=119s
[decide] 2026-11-21 12:44:03 rearrange_clock_e30/on rearrange_blocks seed=4300051 frame=352/700 hist=3 policy=0.6s elapsed=129s
[decide] 2026-11-21 12:44:14 rearrange_clock_e30/on rearrange_blocks seed=4300051 frame=384/700 hist=3 policy=0.6s elapsed=140s
[closed-loop] 2026-11-21 12:44:18 done  rearrange_clock_e30/on rearrange_blocks seed=4300051 success=True targets=389/700 reward=1.0 lift=0.12245690822601318  189s
[closed-loop] 2026-11-21 12:44:18 start rearrange_clock_e30/on rearrange_blocks seed=4300061 target_limit=700 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e16/rearrange_clock_e30/on/rearrange_blocks/seed_4300061
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E16-rearrange-clock-s1.log):
```

[pool] 2026-11-21 20:18:41 exec A40-E16-rearrange-clock-s1 GPU 0 
[pool] 2026-11-21 20:18:43 A40-E16-rearrange-clock-s1: start (attempt 1/3) on GPU 0; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E16-rearrange-clock-s1.log
```

## A40-E16-rearrange-clock-s2 (running, attempt 1, GPU 4)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E16-rearrange-clock-s2.log):
```
[decide] 2026-11-21 12:39:47 rearrange_clock_e30/on rearrange_blocks seed=4300022 frame=96/700 hist=3 policy=0.6s elapsed=36s
[decide] 2026-11-21 12:39:57 rearrange_clock_e30/on rearrange_blocks seed=4300022 frame=128/700 hist=3 policy=0.6s elapsed=46s
[decide] 2026-11-21 12:40:07 rearrange_clock_e30/on rearrange_blocks seed=4300022 frame=160/700 hist=3 policy=0.6s elapsed=56s
[decide] 2026-11-21 12:40:17 rearrange_clock_e30/on rearrange_blocks seed=4300022 frame=192/700 hist=3 policy=0.6s elapsed=65s
[decide] 2026-11-21 12:40:27 rearrange_clock_e30/on rearrange_blocks seed=4300022 frame=224/700 hist=3 policy=0.6s elapsed=75s
[decide] 2026-11-21 12:40:37 rearrange_clock_e30/on rearrange_blocks seed=4300022 frame=256/700 hist=3 policy=0.6s elapsed=85s
[decide] 2026-11-21 12:40:47 rearrange_clock_e30/on rearrange_blocks seed=4300022 frame=288/700 hist=3 policy=0.6s elapsed=96s
[decide] 2026-11-21 12:40:57 rearrange_clock_e30/on rearrange_blocks seed=4300022 frame=320/700 hist=3 policy=0.6s elapsed=106s
[decide] 2026-11-21 12:41:12 rearrange_clock_e30/on rearrange_blocks seed=4300022 frame=352/700 hist=3 policy=0.6s elapsed=120s
[closed-loop] 2026-11-21 12:41:31 done  rearrange_clock_e30/on rearrange_blocks seed=4300022 success=True targets=383/700 reward=1.0 lift=0.12160110473632812  188s
[closed-loop] 2026-11-21 12:41:31 start rearrange_clock_e30/on rearrange_blocks seed=4300032 target_limit=700 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e16/rearrange_clock_e30/on/rearrange_blocks/seed_4300032
[decide] 2026-11-21 12:42:21 rearrange_clock_e30/on rearrange_blocks seed=4300032 frame=0/700 hist=0 policy=0.5s elapsed=9s
[decide] 2026-11-21 12:42:32 rearrange_clock_e30/on rearrange_blocks seed=4300032 frame=32/700 hist=2 policy=0.6s elapsed=20s
[decide] 2026-11-21 12:42:41 rearrange_clock_e30/on rearrange_blocks seed=4300032 frame=64/700 hist=3 policy=0.6s elapsed=29s
[decide] 2026-11-21 12:42:52 rearrange_clock_e30/on rearrange_blocks seed=4300032 frame=96/700 hist=3 policy=0.6s elapsed=40s
[decide] 2026-11-21 12:43:02 rearrange_clock_e30/on rearrange_blocks seed=4300032 frame=128/700 hist=3 policy=0.6s elapsed=50s
[decide] 2026-11-21 12:43:12 rearrange_clock_e30/on rearrange_blocks seed=4300032 frame=160/700 hist=3 policy=0.6s elapsed=60s
[decide] 2026-11-21 12:43:22 rearrange_clock_e30/on rearrange_blocks seed=4300032 frame=192/700 hist=3 policy=0.6s elapsed=70s
[decide] 2026-11-21 12:43:34 rearrange_clock_e30/on rearrange_blocks seed=4300032 frame=224/700 hist=3 policy=0.6s elapsed=82s
[decide] 2026-11-21 12:43:48 rearrange_clock_e30/on rearrange_blocks seed=4300032 frame=256/700 hist=3 policy=0.6s elapsed=96s
[decide] 2026-11-21 12:43:58 rearrange_clock_e30/on rearrange_blocks seed=4300032 frame=288/700 hist=3 policy=0.6s elapsed=106s
[decide] 2026-11-21 12:44:08 rearrange_clock_e30/on rearrange_blocks seed=4300032 frame=320/700 hist=3 policy=0.6s elapsed=116s
[decide] 2026-11-21 12:44:21 rearrange_clock_e30/on rearrange_blocks seed=4300032 frame=352/700 hist=3 policy=0.6s elapsed=129s
[closed-loop] 2026-11-21 12:44:40 done  rearrange_clock_e30/on rearrange_blocks seed=4300032 success=True targets=377/700 reward=1.0 lift=0.12234961986541748  189s
[closed-loop] 2026-11-21 12:44:40 start rearrange_clock_e30/on rearrange_blocks seed=4300042 target_limit=700 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e16/rearrange_clock_e30/on/rearrange_blocks/seed_4300042
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E16-rearrange-clock-s2.log):
```

[pool] 2026-11-21 20:28:57 exec A40-E16-rearrange-clock-s2 GPU 4 
[pool] 2026-11-21 20:28:59 A40-E16-rearrange-clock-s2: start (attempt 1/3) on GPU 4; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E16-rearrange-clock-s2.log
```

## A40-E16-rearrange-clock-s3 (running, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E16-rearrange-clock-s3.log):
```

[queue5] 2026-11-21 20:40:48 $ /opt/mwam/bin/python -m fastwam.memory_v2.online run --checkpoint /workspace/FastWAM-memory2/outputs/fullft/exports/rearrange_clock_e30/export_e30.pt --label rearrange_clock_e30 --modes on --scenes /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/scenes_seed42_n100_rearrange_blocks --output /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e16 --tasks rearrange_blocks --execute 8 --limit 100 --shard 3/10
[dense] WARNING runtime packages differ from the dense preparation receipt (cache is read, not re-encoded): {"python": {"recorded": "3.12.3 (main, Aug 14 2025, 17:47:21) [GCC 13.3.0]", "actual": "3.12.3 (main, Nov  6 2024, 18:32:19) [GCC 13.2.0]"}, "packages.Pillow": {"recorded": "12.0.0", "actual": "11.0.0"}, "packages.numpy": {"recorded": "2.1.0", "actual": "1.26.4"}, "packages.torch": {"recorded": "2.10.0a0+b558c986e8.nv25.11", "actual": "2.6.0a0+df5bbc09d1.nv24.12"}, "packages.torchvision": {"recorded": "0.25.0a0+7a13ad0f", "actual": "0.20.0a0"}}
[closed-loop] 2026-11-21 12:41:59 10 scenes x modes ['on'] -> labels {'on': 'rearrange_clock_e30'}; checkpoint /workspace/FastWAM-memory2/outputs/fullft/exports/rearrange_clock_e30/export_e30.pt; T5 on CPU; max_targets=official
[closed-loop] WARNING dense config was recorded for sm9.0; this GPU is sm8.6: TORCH_EXTENSIONS_DIR -> /workspace/FastWAM/outputs/fused_environment_memory_v2_sm86/torch_extensions (give --extensions-dir to reuse built kernels)
[closed-loop] 2026-11-21 12:41:59 start rearrange_clock_e30/on rearrange_blocks seed=4300003 target_limit=700 -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e16/rearrange_clock_e30/on/rearrange_blocks/seed_4300003
[fullft] text from the training cache (rearrange_blocks/episode_0000000, 50 episodes share it; fingerprint 73739a6aa417)
/restore-tmp/dense_joint_v1/data_path.py:16: UserWarning: The given NumPy array is not writable, and PyTorch does not support non-writable tensors. This means writing to this tensor will result in undefined behavior. You may want to copy the array to protect its data or make it writable before converting it to a tensor. This type of warning will be suppressed for the rest of this program. (Triggered internally at /opt/pytorch/pytorch/torch/csrc/utils/tensor_numpy.cpp:206.)
  return torch.stack([TF.resize(torch.from_numpy(np.ascontiguousarray(a)).permute(2,0,1).float()/255.,
[decide] 2026-11-21 12:42:43 rearrange_clock_e30/on rearrange_blocks seed=4300003 frame=0/700 hist=0 policy=0.7s elapsed=6s
[decide] 2026-11-21 12:42:53 rearrange_clock_e30/on rearrange_blocks seed=4300003 frame=32/700 hist=2 policy=0.6s elapsed=16s
[decide] 2026-11-21 12:43:03 rearrange_clock_e30/on rearrange_blocks seed=4300003 frame=64/700 hist=3 policy=0.6s elapsed=26s
[decide] 2026-11-21 12:43:14 rearrange_clock_e30/on rearrange_blocks seed=4300003 frame=96/700 hist=3 policy=0.6s elapsed=36s
[decide] 2026-11-21 12:43:23 rearrange_clock_e30/on rearrange_blocks seed=4300003 frame=128/700 hist=3 policy=0.6s elapsed=46s
[decide] 2026-11-21 12:43:37 rearrange_clock_e30/on rearrange_blocks seed=4300003 frame=160/700 hist=3 policy=0.6s elapsed=60s
[decide] 2026-11-21 12:43:50 rearrange_clock_e30/on rearrange_blocks seed=4300003 frame=192/700 hist=3 policy=0.6s elapsed=72s
[decide] 2026-11-21 12:44:00 rearrange_clock_e30/on rearrange_blocks seed=4300003 frame=224/700 hist=3 policy=0.6s elapsed=82s
[decide] 2026-11-21 12:44:10 rearrange_clock_e30/on rearrange_blocks seed=4300003 frame=256/700 hist=3 policy=0.6s elapsed=92s
[decide] 2026-11-21 12:44:22 rearrange_clock_e30/on rearrange_blocks seed=4300003 frame=288/700 hist=3 policy=0.6s elapsed=104s
[decide] 2026-11-21 12:44:43 rearrange_clock_e30/on rearrange_blocks seed=4300003 frame=320/700 hist=3 policy=0.6s elapsed=125s
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E16-rearrange-clock-s3.log):
```

[pool] 2026-11-21 20:40:46 exec A40-E16-rearrange-clock-s3 GPU 7 
[pool] 2026-11-21 20:40:48 A40-E16-rearrange-clock-s3: start (attempt 1/3) on GPU 7; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E16-rearrange-clock-s3.log
```

## A40-fetch-swapT_clock-e30 (done, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_clock-e30.log):
```
[fetch] 2026-11-21 10:38:22 waiting for exports/swapT_clock_e30 on the relay
[fetch] 2026-11-21 10:43:23 waiting for exports/swapT_clock_e30 on the relay
[fetch] 2026-11-21 10:48:23 waiting for exports/swapT_clock_e30 on the relay
[fetch] 2026-11-21 10:53:24 waiting for exports/swapT_clock_e30 on the relay
[fetch] 2026-11-21 10:58:24 waiting for exports/swapT_clock_e30 on the relay
[fetch] 2026-11-21 11:03:25 waiting for exports/swapT_clock_e30 on the relay
[fetch] 2026-11-21 11:08:25 waiting for exports/swapT_clock_e30 on the relay
[fetch] 2026-11-21 11:13:26 waiting for exports/swapT_clock_e30 on the relay
[fetch] 2026-11-21 11:18:26 waiting for exports/swapT_clock_e30 on the relay
[fetch] 2026-11-21 11:23:27 waiting for exports/swapT_clock_e30 on the relay
[fetch] 2026-11-21 11:28:27 waiting for exports/swapT_clock_e30 on the relay
[fetch] 2026-11-21 11:33:28 waiting for exports/swapT_clock_e30 on the relay
[fetch] 2026-11-21 11:38:28 waiting for exports/swapT_clock_e30 on the relay
[fetch] 2026-11-21 11:43:29 waiting for exports/swapT_clock_e30 on the relay
[fetch] 2026-11-21 11:48:30 waiting for exports/swapT_clock_e30 on the relay
[fetch] disk before: /dev/sdb         19T  9.6T  7.7T  56% /workspace/FastWAM-memory2
[fetch] 2026-11-21 11:53:31 fetching swapT_clock_e30 (attempt 1)
[relay] get hhyfred/memwam-fullft/exports/swapT_clock_e30/export_e30.pt -> /workspace/FastWAM-memory2/outputs/fullft/exports/swapT_clock_e30/export_e30.pt (12042325701 bytes)
[relay] get hhyfred/memwam-fullft/exports/swapT_clock_e30/export_e30.pt.sha256 -> /workspace/FastWAM-memory2/outputs/fullft/exports/swapT_clock_e30/export_e30.pt.sha256 (80 bytes)
export_e30.pt: OK
total 11760100
drwxr-xr-x  2 root root        4096 Nov 21 12:01 .
drwxr-xr-x 34 root root        4096 Nov 21 11:53 ..
-rw-r--r--  1 root root 12042325701 Nov 21 12:01 export_e30.pt
-rw-r--r--  1 root root          80 Nov 21 12:01 export_e30.pt.sha256
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-swapT_clock-e30.log):
```

[pool] 2026-11-19 19:17:58 exec A40-fetch-swapT_clock-e30 GPU None 
[pool] 2026-11-19 19:18:00 A40-fetch-swapT_clock-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-swapT_clock-e30.log
[autopsy] /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-swapT_clock-e30.md
[queue5] 2026-11-21 20:01:26 A40-fetch-swapT_clock-e30: PASS  rc=0
```

## A40-E16-rearrange_ar-p64-vis-s0 (done, attempt 1, GPU 7)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-E16-rearrange_ar-p64-vis-s0.log):
```
[decide] 2026-11-21 12:36:42 rearrange_ar_e30_p64_vis/on rearrange_blocks seed=4300045 frame=288/700 hist=3 policy=0.5s elapsed=97s
[decide] 2026-11-21 12:36:57 rearrange_ar_e30_p64_vis/on rearrange_blocks seed=4300045 frame=320/700 hist=3 policy=0.6s elapsed=111s
[decide] 2026-11-21 12:37:06 rearrange_ar_e30_p64_vis/on rearrange_blocks seed=4300045 frame=352/700 hist=3 policy=0.5s elapsed=120s
[decide] 2026-11-21 12:37:15 rearrange_ar_e30_p64_vis/on rearrange_blocks seed=4300045 frame=384/700 hist=3 policy=0.5s elapsed=130s
[decide] 2026-11-21 12:37:24 rearrange_ar_e30_p64_vis/on rearrange_blocks seed=4300045 frame=416/700 hist=3 policy=0.5s elapsed=139s
[decide] 2026-11-21 12:37:34 rearrange_ar_e30_p64_vis/on rearrange_blocks seed=4300045 frame=448/700 hist=3 policy=0.5s elapsed=148s
[decide] 2026-11-21 12:37:43 rearrange_ar_e30_p64_vis/on rearrange_blocks seed=4300045 frame=480/700 hist=3 policy=0.6s elapsed=158s
[decide] 2026-11-21 12:37:53 rearrange_ar_e30_p64_vis/on rearrange_blocks seed=4300045 frame=512/700 hist=3 policy=0.5s elapsed=167s
[decide] 2026-11-21 12:38:02 rearrange_ar_e30_p64_vis/on rearrange_blocks seed=4300045 frame=544/700 hist=3 policy=0.5s elapsed=177s
[decide] 2026-11-21 12:38:15 rearrange_ar_e30_p64_vis/on rearrange_blocks seed=4300045 frame=576/700 hist=3 policy=0.6s elapsed=189s
[decide] 2026-11-21 12:38:33 rearrange_ar_e30_p64_vis/on rearrange_blocks seed=4300045 frame=608/700 hist=3 policy=0.6s elapsed=207s
[decide] 2026-11-21 12:38:51 rearrange_ar_e30_p64_vis/on rearrange_blocks seed=4300045 frame=640/700 hist=3 policy=0.6s elapsed=225s
[decide] 2026-11-21 12:39:04 rearrange_ar_e30_p64_vis/on rearrange_blocks seed=4300045 frame=672/700 hist=3 policy=0.6s elapsed=239s
[decide] 2026-11-21 12:39:14 rearrange_ar_e30_p64_vis/on rearrange_blocks seed=4300045 frame=704/700 hist=3 policy=0.5s elapsed=248s
[decide] 2026-11-21 12:39:23 rearrange_ar_e30_p64_vis/on rearrange_blocks seed=4300045 frame=736/700 hist=3 policy=0.5s elapsed=258s
[closed-loop] 2026-11-21 12:39:35 done  rearrange_ar_e30_p64_vis/on rearrange_blocks seed=4300045 success=False targets=700/700 reward=0.0 lift=0.12327975034713745  308s

label/mode              task               n  success  95% CI        lift5cm  reward  targets dep_null  dep_off   dep_on  pol_s
rearrange_ar_e30_p64_vis/onrearrange_blocks  10     0.30  [0.11,0.60]      1.00    0.30      607        -        -        -    0.6
rearrange_clock_e30/on  rearrange_blocks  12     0.50  [0.25,0.75]      1.00    0.50      546        -        -        -    0.6

paired on common scenes (A vs B):                         n  both  only A  only B  neither  McNemar p
  rearrange_ar_e30_p64_vis/on vs rearrange_clock_e30/on     5     1       1       3        0  0.625

[summary] 22 episodes, 0 open errors -> /workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/e16/SUMMARY.json
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-E16-rearrange_ar-p64-vis-s0.log):
```
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 386, in main
    lines += section_result(task, s)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/workspace/FastWAM-memory2/scripts/memory_v2/autopsy.py", line 154, in section_result
    out += ["", "| condition | n | " + " | ".join(ORDER[cells[0][0].split('/')[0]]) + " | progress | decision correct | reference (same scenes) |",
                                                  ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'rearrange_blocks'
[queue5] 2026-11-21 20:39:41 A40-E16-rearrange_ar-p64-vis-s0: DONE  rearrange_blocks/on n=10  prog=0.00
```

## A40-fetch-battery_count-e30 (running, attempt 1, GPU None)

job log tail (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-battery_count-e30.log):
```
[fetch] 2026-11-21 10:43:23 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 10:48:23 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 10:53:24 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 10:58:24 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 11:03:25 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 11:08:25 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 11:13:26 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 11:18:26 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 11:23:27 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 11:28:27 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 11:33:28 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 11:38:28 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 11:43:29 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 11:48:30 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 11:53:30 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 11:58:31 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 12:03:31 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 12:08:32 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 12:13:32 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 12:18:33 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 12:23:33 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 12:28:34 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 12:33:35 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 12:38:35 waiting for exports/battery_count_e30 on the relay
[fetch] 2026-11-21 12:43:36 waiting for exports/battery_count_e30 on the relay
```
pool log for this task (/workspace/FastWAM-memory2/outputs/memory_v2/queue5/exec/A40-fetch-battery_count-e30.log):
```

[pool] 2026-11-19 19:17:58 exec A40-fetch-battery_count-e30 GPU None 
[pool] 2026-11-19 19:18:00 A40-fetch-battery_count-e30: start (attempt 1/3) on GPU None; job log /workspace/FastWAM-memory2/outputs/memory_v2/queue5/tasks/A40-fetch-battery_count-e30.log
```

## verdicts in the last 24.0 h

- A40-E14-press_v3c-e30-s3: **DONE** (2026-11-20 23:47:06) press_button/on n=91 pressed=91 n1_correct=62 n2_correct=23 confirmed=91 count_correct=15 success=15 prog=0.44
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E14-press_v3c-e30-s3.md
- A40-E14-press_v3c-e30-s4: **DONE** (2026-11-20 23:43:06) press_button/on n=89 pressed=89 n1_correct=60 n2_correct=23 confirmed=89 count_correct=15 success=15 prog=0.44
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E14-press_v3c-e30-s4.md
- A40-E14-press_v3c-e30-s5: **DONE** (2026-11-20 23:33:56) press_button/on n=82 pressed=82 n1_correct=55 n2_correct=18 confirmed=82 count_correct=12 success=12 prog=0.42
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E14-press_v3c-e30-s5.md
- A40-E14-press_v3c-e30-s6: **DONE** (2026-11-20 23:35:36) press_button/on n=84 pressed=84 n1_correct=56 n2_correct=20 confirmed=84 count_correct=13 success=13 prog=0.43
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E14-press_v3c-e30-s6.md
- A40-E14-press_v3c-e30-s7: **DONE** (2026-11-20 23:40:25) press_button/on n=88 pressed=88 n1_correct=59 n2_correct=22 confirmed=88 count_correct=14 success=14 prog=0.43
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E14-press_v3c-e30-s7.md
- A40-E14-press_v3c-e30-s8: **DONE** (2026-11-20 23:37:19) press_button/on n=85 pressed=85 n1_correct=57 n2_correct=21 confirmed=85 count_correct=14 success=14 prog=0.43
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E14-press_v3c-e30-s8.md
- A40-E14-press_v3c-e30-s9: **DONE** (2026-11-21 00:59:17) press_button/on n=100 pressed=100 n1_correct=69 n2_correct=25 confirmed=100 count_correct=17 success=17 prog=0.44
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E14-press_v3c-e30-s9.md
- A40-E21-off-swap-s3: **DONE** (2026-11-21 00:50:29) swap_blocks/on n=50 lifted=50 s1=50 s2=50 s3=50 pressed=0 success=0 prog=0.67
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-off-swap-s3.md
- A40-E21-off-swap-s4: **DONE** (2026-11-21 00:48:03) swap_blocks/on n=49 lifted=49 s1=49 s2=49 s3=49 pressed=0 success=0 prog=0.67
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-off-swap-s4.md
- A40-E21-freeze-swap-s0: **DONE** (2026-11-21 00:27:12) swap_blocks/on n=27 lifted=27 s1=27 s2=27 s3=27 pressed=27 success=27 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-freeze-swap-s0.md
- A40-E21-freeze-swap-s1: **DONE** (2026-11-21 00:28:40) swap_blocks/on n=29 lifted=29 s1=29 s2=29 s3=29 pressed=29 success=29 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-freeze-swap-s1.md
- A40-E21-freeze-swap-s2: **DONE** (2026-11-21 00:32:42) swap_blocks/on n=30 lifted=30 s1=30 s2=30 s3=30 pressed=30 success=30 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-freeze-swap-s2.md
- A40-E21-freeze-swap-s3: **DONE** (2026-11-21 01:12:09) swap_blocks/on n=49 lifted=49 s1=49 s2=49 s3=49 pressed=49 success=49 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-freeze-swap-s3.md
- A40-E21-freeze-swap-s4: **DONE** (2026-11-21 01:15:03) swap_blocks/on n=50 lifted=50 s1=50 s2=50 s3=50 pressed=50 success=50 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-freeze-swap-s4.md
- A40-E21-flat-swap-s0: **DONE** (2026-11-21 01:42:41) swap_blocks/on n=32 lifted=32 s1=32 s2=32 s3=32 pressed=32 success=0 prog=0.83
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-flat-swap-s0.md
- A40-E21-flat-swap-s1: **DONE** (2026-11-21 01:59:35) swap_blocks/on n=43 lifted=43 s1=43 s2=43 s3=43 pressed=43 success=0 prog=0.83
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-flat-swap-s1.md
- A40-E21-flat-swap-s2: **DONE** (2026-11-21 02:02:49) swap_blocks/on n=44 lifted=44 s1=44 s2=44 s3=44 pressed=44 success=0 prog=0.83
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-flat-swap-s2.md
- A40-E21-flat-swap-s3: **DONE** (2026-11-21 02:10:58) swap_blocks/on n=47 lifted=47 s1=47 s2=47 s3=47 pressed=47 success=0 prog=0.83
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-flat-swap-s3.md
- A40-E21-flat-swap-s4: **DONE** (2026-11-21 02:25:46) swap_blocks/on n=50 lifted=50 s1=50 s2=50 s3=50 pressed=50 success=0 prog=0.83
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-flat-swap-s4.md
- A40-E21-off-put-s0: **DONE** (2026-11-21 01:47:05) put_back_block/on n=10 lifted=10 centre=10 pressed=9 stage1=9 regrasp=9 returned=10 success=9 prog=0.93
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-off-put-s0.md
- A40-E21-off-put-s1: **DONE** (2026-11-21 02:16:31) put_back_block/on n=35 lifted=35 centre=35 pressed=28 stage1=28 regrasp=28 returned=35 success=28 prog=0.87
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-off-put-s1.md
- A40-E21-off-put-s2: **DONE** (2026-11-21 02:21:41) put_back_block/on n=41 lifted=41 centre=41 pressed=34 stage1=34 regrasp=34 returned=41 success=34 prog=0.89
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-off-put-s2.md
- A40-E21-off-put-s3: **DONE** (2026-11-21 02:33:37) put_back_block/on n=49 lifted=49 centre=49 pressed=40 stage1=40 regrasp=40 returned=49 success=40 prog=0.88
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-off-put-s3.md
- A40-E21-off-put-s4: **DONE** (2026-11-21 02:33:55) put_back_block/on n=50 lifted=50 centre=50 pressed=41 stage1=41 regrasp=41 returned=50 success=41 prog=0.88
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-off-put-s4.md
- A40-E17-press_arprop-e20-s0: **DONE** (2026-11-21 03:37:16) press_button/on n=46 pressed=46 n1_correct=21 n2_correct=14 confirmed=45 count_correct=4 success=4 prog=0.34
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e20-s0.md
- A40-E17-press_arprop-e20-s1: **DONE** (2026-11-21 03:47:38) press_button/on n=52 pressed=52 n1_correct=25 n2_correct=16 confirmed=51 count_correct=5 success=5 prog=0.35
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e20-s1.md
- A40-E17-press_arprop-e20-s2: **DONE** (2026-11-21 03:58:55) press_button/on n=59 pressed=59 n1_correct=30 n2_correct=18 confirmed=58 count_correct=5 success=5 prog=0.35
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e20-s2.md
- A40-E17-press_arprop-e20-s3: **DONE** (2026-11-21 04:03:17) press_button/on n=62 pressed=62 n1_correct=32 n2_correct=19 confirmed=61 count_correct=5 success=5 prog=0.35
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e20-s3.md
- A40-E17-press_arprop-e20-s4: **DONE** (2026-11-21 03:53:57) press_button/on n=57 pressed=57 n1_correct=29 n2_correct=17 confirmed=56 count_correct=5 success=5 prog=0.35
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e20-s4.md
- A40-E17-press_arprop-e20-s5: **DONE** (2026-11-21 04:07:23) press_button/on n=64 pressed=64 n1_correct=34 n2_correct=19 confirmed=62 count_correct=5 success=5 prog=0.35
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e20-s5.md
- A40-E17-press_arprop-e20-s6: **DONE** (2026-11-21 05:00:58) press_button/on n=90 pressed=90 n1_correct=51 n2_correct=25 confirmed=88 count_correct=8 success=8 prog=0.37
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e20-s6.md
- A40-E17-press_arprop-e20-s7: **DONE** (2026-11-21 05:21:13) press_button/on n=97 pressed=97 n1_correct=55 n2_correct=25 confirmed=95 count_correct=8 success=8 prog=0.36
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e20-s7.md
- A40-E17-press_arprop-e20-s8: **DONE** (2026-11-21 05:30:54) press_button/on n=100 pressed=100 n1_correct=56 n2_correct=25 confirmed=98 count_correct=8 success=8 prog=0.36
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e20-s8.md
- A40-E17-press_arprop-e20-s9: **DONE** (2026-11-21 05:28:18) press_button/on n=99 pressed=99 n1_correct=56 n2_correct=25 confirmed=97 count_correct=8 success=8 prog=0.36
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e20-s9.md
- A40-E17-press_arprop-e30-s0: **DONE** (2026-11-21 05:41:23) press_button/on n=26 pressed=26 n1_correct=6 n2_correct=2 confirmed=26 count_correct=0 success=0 prog=0.25
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e30-s0.md
- A40-E17-press_arprop-e30-s1: **DONE** (2026-11-21 05:40:01) press_button/on n=24 pressed=24 n1_correct=6 n2_correct=1 confirmed=24 count_correct=0 success=0 prog=0.25
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e30-s1.md
- A40-E17-press_arprop-e30-s2: **DONE** (2026-11-21 06:34:08) press_button/on n=60 pressed=60 n1_correct=13 n2_correct=10 confirmed=60 count_correct=1 success=1 prog=0.25
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e30-s2.md
- A40-E17-press_arprop-e30-s3: **DONE** (2026-11-21 06:50:43) press_button/on n=72 pressed=72 n1_correct=17 n2_correct=12 confirmed=72 count_correct=2 success=2 prog=0.26
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e30-s3.md
- A40-E17-press_arprop-e30-s4: **DONE** (2026-11-21 07:04:38) press_button/on n=80 pressed=80 n1_correct=18 n2_correct=13 confirmed=80 count_correct=2 success=2 prog=0.26
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e30-s4.md
- A40-E17-press_arprop-e30-s5: **DONE** (2026-11-21 07:03:40) press_button/on n=79 pressed=79 n1_correct=18 n2_correct=13 confirmed=79 count_correct=2 success=2 prog=0.26
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e30-s5.md
- A40-E17-press_arprop-e30-s6: **DONE** (2026-11-21 07:06:34) press_button/on n=82 pressed=82 n1_correct=18 n2_correct=13 confirmed=82 count_correct=2 success=2 prog=0.26
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e30-s6.md
- A40-E17-press_arprop-e30-s7: **DONE** (2026-11-21 07:17:57) press_button/on n=86 pressed=86 n1_correct=18 n2_correct=13 confirmed=86 count_correct=2 success=2 prog=0.26
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e30-s7.md
- A40-E17-press_arprop-e30-s8: **DONE** (2026-11-21 08:11:06) press_button/on n=98 pressed=98 n1_correct=20 n2_correct=16 confirmed=98 count_correct=2 success=2 prog=0.25
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e30-s8.md
- A40-E17-press_arprop-e30-s9: **DONE** (2026-11-21 08:24:14) press_button/on n=100 pressed=100 n1_correct=20 n2_correct=17 confirmed=100 count_correct=2 success=2 prog=0.25
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_arprop-e30-s9.md
- A40-E17-press_ar-e30-s0: **DONE** (2026-11-21 08:40:24) press_button/on n=41 pressed=41 n1_correct=6 n2_correct=5 confirmed=16 count_correct=2 success=2 prog=0.26
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_ar-e30-s0.md
- A40-E17-press_ar-e30-s1: **DONE** (2026-11-21 08:42:39) press_button/on n=44 pressed=44 n1_correct=7 n2_correct=5 confirmed=17 count_correct=2 success=2 prog=0.26
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_ar-e30-s1.md
- A40-E17-press_ar-e30-s2: **DONE** (2026-11-21 08:30:34) press_button/on n=34 pressed=34 n1_correct=5 n2_correct=4 confirmed=12 count_correct=1 success=1 prog=0.25
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_ar-e30-s2.md
- A40-E17-press_ar-e30-s3: **DONE** (2026-11-21 08:50:42) press_button/on n=47 pressed=47 n1_correct=7 n2_correct=5 confirmed=17 count_correct=2 success=2 prog=0.26
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_ar-e30-s3.md
- A40-E17-press_ar-e30-s4: **DONE** (2026-11-21 09:46:24) press_button/on n=84 pressed=84 n1_correct=10 n2_correct=10 confirmed=31 count_correct=2 success=2 prog=0.24
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_ar-e30-s4.md
- A40-E17-press_ar-e30-s5: **DONE** (2026-11-21 09:56:30) press_button/on n=90 pressed=90 n1_correct=10 n2_correct=10 confirmed=32 count_correct=2 success=2 prog=0.24
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_ar-e30-s5.md
- A40-E17-press_ar-e30-s6: **DONE** (2026-11-21 10:01:03) press_button/on n=93 pressed=93 n1_correct=11 n2_correct=10 confirmed=33 count_correct=2 success=2 prog=0.24
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_ar-e30-s6.md
- A40-E17-press_ar-e30-s7: **DONE** (2026-11-21 10:13:03) press_button/on n=97 pressed=97 n1_correct=12 n2_correct=10 confirmed=34 count_correct=2 success=2 prog=0.24
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_ar-e30-s7.md
- A40-E17-press_ar-e30-s8: **DONE** (2026-11-21 10:17:56) press_button/on n=99 pressed=99 n1_correct=12 n2_correct=10 confirmed=34 count_correct=2 success=2 prog=0.24
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_ar-e30-s8.md
- A40-E17-press_ar-e30-s9: **DONE** (2026-11-21 10:25:18) press_button/on n=100 pressed=100 n1_correct=12 n2_correct=10 confirmed=34 count_correct=2 success=2 prog=0.24
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_ar-e30-s9.md
- A40-E17-press_fast-e10-s0: **DONE** (2026-11-21 11:25:03) press_button/on n=49 pressed=49 n1_correct=3 n2_correct=9 confirmed=46 count_correct=0 success=0 prog=0.21
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e10-s0.md
- A40-E17-press_fast-e10-s1: **DONE** (2026-11-21 11:30:23) press_button/on n=53 pressed=53 n1_correct=3 n2_correct=9 confirmed=50 count_correct=0 success=0 prog=0.21
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e10-s1.md
- A40-E17-press_fast-e10-s2: **DONE** (2026-11-21 11:37:27) press_button/on n=57 pressed=57 n1_correct=3 n2_correct=9 confirmed=54 count_correct=0 success=0 prog=0.21
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e10-s2.md
- A40-E17-press_fast-e10-s3: **DONE** (2026-11-21 11:47:04) press_button/on n=64 pressed=64 n1_correct=3 n2_correct=9 confirmed=60 count_correct=0 success=0 prog=0.21
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e10-s3.md
- A40-E17-press_fast-e10-s4: **DONE** (2026-11-21 11:55:33) press_button/on n=70 pressed=70 n1_correct=3 n2_correct=10 confirmed=65 count_correct=0 success=0 prog=0.21
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e10-s4.md
- A40-E17-press_fast-e10-s5: **DONE** (2026-11-21 11:59:25) press_button/on n=72 pressed=72 n1_correct=3 n2_correct=11 confirmed=67 count_correct=0 success=0 prog=0.21
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e10-s5.md
- A40-E17-press_fast-e10-s6: **DONE** (2026-11-21 12:27:35) press_button/on n=86 pressed=85 n1_correct=4 n2_correct=16 confirmed=80 count_correct=1 success=1 prog=0.21
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e10-s6.md
- A40-E17-press_fast-e10-s7: **DONE** (2026-11-21 13:00:25) press_button/on n=97 pressed=96 n1_correct=5 n2_correct=19 confirmed=91 count_correct=2 success=2 prog=0.22
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e10-s7.md
- A40-E17-press_fast-e10-s8: **DONE** (2026-11-21 13:00:45) press_button/on n=98 pressed=97 n1_correct=5 n2_correct=19 confirmed=92 count_correct=2 success=2 prog=0.22
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e10-s8.md
- A40-E17-press_fast-e10-s9: **DONE** (2026-11-21 13:14:48) press_button/on n=100 pressed=99 n1_correct=5 n2_correct=19 confirmed=94 count_correct=2 success=2 prog=0.22
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e10-s9.md
- A40-E17-press_fast-e20-s0: **DONE** (2026-11-21 13:00:45) press_button/on n=28 pressed=28 n1_correct=20 n2_correct=9 confirmed=28 count_correct=8 success=8 prog=0.51
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e20-s0.md
- A40-E17-press_fast-e20-s1: **DONE** (2026-11-21 13:18:51) press_button/on n=39 pressed=39 n1_correct=27 n2_correct=13 confirmed=39 count_correct=10 success=10 prog=0.49
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e20-s1.md
- A40-E17-press_fast-e20-s2: **DONE** (2026-11-21 13:22:48) press_button/on n=41 pressed=41 n1_correct=29 n2_correct=14 confirmed=41 count_correct=11 success=11 prog=0.50
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e20-s2.md
- A40-E17-press_fast-e20-s3: **DONE** (2026-11-21 14:03:08) press_button/on n=74 pressed=74 n1_correct=51 n2_correct=25 confirmed=74 count_correct=18 success=18 prog=0.48
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e20-s3.md
- A40-E17-press_fast-e20-s4: **DONE** (2026-11-21 14:18:57) press_button/on n=87 pressed=87 n1_correct=58 n2_correct=29 confirmed=87 count_correct=20 success=20 prog=0.47
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e20-s4.md
- A40-E17-press_fast-e20-s5: **DONE** (2026-11-21 14:33:16) press_button/on n=95 pressed=95 n1_correct=65 n2_correct=30 confirmed=95 count_correct=21 success=21 prog=0.47
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e20-s5.md
- A40-E17-press_fast-e20-s6: **DONE** (2026-11-21 14:19:10) press_button/on n=88 pressed=88 n1_correct=59 n2_correct=29 confirmed=88 count_correct=20 success=20 prog=0.47
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e20-s6.md
- A40-E17-press_fast-e20-s7: **DONE** (2026-11-21 14:42:04) press_button/on n=99 pressed=99 n1_correct=67 n2_correct=31 confirmed=99 count_correct=22 success=22 prog=0.47
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e20-s7.md
- A40-E17-press_fast-e20-s8: **DONE** (2026-11-21 14:38:34) press_button/on n=97 pressed=97 n1_correct=66 n2_correct=31 confirmed=97 count_correct=22 success=22 prog=0.47
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e20-s8.md
- A40-E17-press_fast-e20-s9: **DONE** (2026-11-21 14:50:31) press_button/on n=100 pressed=100 n1_correct=68 n2_correct=31 confirmed=100 count_correct=22 success=22 prog=0.47
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e20-s9.md
- A40-E17-press_fast-e30-s0: **DONE** (2026-11-21 15:26:16) press_button/on n=46 pressed=46 n1_correct=33 n2_correct=15 confirmed=46 count_correct=12 success=12 prog=0.50
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e30-s0.md
- A40-E17-press_fast-e30-s1: **DONE** (2026-11-21 15:43:57) press_button/on n=58 pressed=58 n1_correct=40 n2_correct=18 confirmed=58 count_correct=13 success=13 prog=0.47
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e30-s1.md
- A40-E17-press_fast-e30-s2: **DONE** (2026-11-21 15:24:56) press_button/on n=44 pressed=44 n1_correct=31 n2_correct=14 confirmed=44 count_correct=11 success=11 prog=0.49
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e30-s2.md
- A40-E17-press_fast-e30-s3: **DONE** (2026-11-21 15:59:01) press_button/on n=73 pressed=73 n1_correct=50 n2_correct=22 confirmed=73 count_correct=16 success=16 prog=0.47
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e30-s3.md
- A40-E17-press_fast-e30-s4: **DONE** (2026-11-21 16:10:21) press_button/on n=83 pressed=83 n1_correct=59 n2_correct=28 confirmed=83 count_correct=22 success=22 prog=0.50
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e30-s4.md
- A40-E17-press_fast-e30-s5: **DONE** (2026-11-21 16:12:17) press_button/on n=85 pressed=85 n1_correct=61 n2_correct=29 confirmed=85 count_correct=23 success=23 prog=0.51
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e30-s5.md
- A40-E17-press_fast-e30-s6: **DONE** (2026-11-21 16:01:46) press_button/on n=77 pressed=77 n1_correct=54 n2_correct=25 confirmed=77 count_correct=19 success=19 prog=0.49
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e30-s6.md
- A40-E17-press_fast-e30-s7: **DONE** (2026-11-21 16:57:38) press_button/on n=98 pressed=98 n1_correct=69 n2_correct=32 confirmed=98 count_correct=25 success=25 prog=0.49
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e30-s7.md
- A40-E17-press_fast-e30-s8: **DONE** (2026-11-21 16:33:06) press_button/on n=92 pressed=92 n1_correct=64 n2_correct=30 confirmed=92 count_correct=24 success=24 prog=0.50
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e30-s8.md
- A40-E17-press_fast-e30-s9: **DONE** (2026-11-21 17:07:47) press_button/on n=100 pressed=100 n1_correct=71 n2_correct=33 confirmed=100 count_correct=26 success=26 prog=0.50
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-press_fast-e30-s9.md
- A40-E17-report: **PASS** (2026-11-21 17:19:54) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E17-report.md
- A40-E14-verdict: **PASS** (2026-11-21 01:06:47) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E14-verdict.md
- A40-E22b-clock-b16-swap-s0: **DONE** (2026-11-21 16:46:49) swap_blocks/on n=35 lifted=35 s1=35 s2=35 s3=35 pressed=35 success=35 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b16-swap-s0.md
- A40-E22b-clock-b16-swap-s1: **DONE** (2026-11-21 16:48:46) swap_blocks/on n=37 lifted=37 s1=37 s2=37 s3=37 pressed=37 success=37 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b16-swap-s1.md
- A40-E22b-clock-b16-swap-s2: **DONE** (2026-11-21 16:56:54) swap_blocks/on n=43 lifted=43 s1=43 s2=43 s3=43 pressed=43 success=43 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b16-swap-s2.md
- A40-E22b-clock-b16-swap-s3: **DONE** (2026-11-21 16:59:49) swap_blocks/on n=45 lifted=45 s1=45 s2=45 s3=45 pressed=45 success=45 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b16-swap-s3.md
- A40-E22b-clock-b16-swap-s4: **DONE** (2026-11-21 17:20:34) swap_blocks/on n=50 lifted=50 s1=50 s2=50 s3=50 pressed=50 success=50 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b16-swap-s4.md
- A40-E22b-clock-b8-swap-s0: **DONE** (2026-11-21 17:35:12) swap_blocks/on n=40 lifted=40 s1=40 s2=40 s3=40 pressed=39 success=39 prog=0.99
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b8-swap-s0.md
- A40-E22b-clock-b8-swap-s1: **DONE** (2026-11-21 17:39:20) swap_blocks/on n=44 lifted=44 s1=44 s2=44 s3=44 pressed=43 success=43 prog=0.99
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b8-swap-s1.md
- A40-E22b-clock-b8-swap-s2: **DONE** (2026-11-21 17:43:50) swap_blocks/on n=47 lifted=47 s1=47 s2=47 s3=47 pressed=46 success=46 prog=0.99
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b8-swap-s2.md
- A40-E22b-clock-b8-swap-s3: **DONE** (2026-11-21 17:45:09) swap_blocks/on n=49 lifted=49 s1=49 s2=49 s3=49 pressed=48 success=48 prog=0.99
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b8-swap-s3.md
- A40-E22b-clock-b8-swap-s4: **DONE** (2026-11-21 17:49:20) swap_blocks/on n=50 lifted=50 s1=50 s2=50 s3=50 pressed=49 success=49 prog=0.99
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b8-swap-s4.md
- A40-E22b-clock-b4-swap-s0: **DONE** (2026-11-21 18:04:00) swap_blocks/on n=29 lifted=29 s1=29 s2=29 s3=29 pressed=24 success=21 prog=0.93
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b4-swap-s0.md
- A40-E22b-clock-b4-swap-s1: **DONE** (2026-11-21 18:17:08) swap_blocks/on n=38 lifted=38 s1=38 s2=38 s3=38 pressed=30 success=27 prog=0.92
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b4-swap-s1.md
- A40-E22b-clock-b4-swap-s2: **DONE** (2026-11-21 18:28:39) swap_blocks/on n=47 lifted=47 s1=47 s2=47 s3=47 pressed=39 success=36 prog=0.93
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b4-swap-s2.md
- A40-E22b-clock-b4-swap-s3: **DONE** (2026-11-21 18:33:14) swap_blocks/on n=49 lifted=49 s1=49 s2=49 s3=49 pressed=41 success=38 prog=0.94
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b4-swap-s3.md
- A40-E22b-clock-b4-swap-s4: **DONE** (2026-11-21 18:36:32) swap_blocks/on n=50 lifted=50 s1=50 s2=50 s3=50 pressed=42 success=39 prog=0.94
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-clock-b4-swap-s4.md
- A40-E22b-ledger-b16-swap-s0: **DONE** (2026-11-21 18:34:44) swap_blocks/on n=28 lifted=28 s1=28 s2=28 s3=28 pressed=28 success=28 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b16-swap-s0.md
- A40-E22b-ledger-b16-swap-s1: **DONE** (2026-11-21 18:37:39) swap_blocks/on n=30 lifted=30 s1=30 s2=30 s3=30 pressed=30 success=30 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b16-swap-s1.md
- A40-E22b-ledger-b16-swap-s2: **DONE** (2026-11-21 18:51:24) swap_blocks/on n=41 lifted=41 s1=41 s2=41 s3=41 pressed=41 success=41 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b16-swap-s2.md
- A40-E22b-ledger-b16-swap-s3: **DONE** (2026-11-21 19:04:41) swap_blocks/on n=47 lifted=47 s1=47 s2=47 s3=47 pressed=47 success=47 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b16-swap-s3.md
- A40-E22b-ledger-b16-swap-s4: **DONE** (2026-11-21 19:16:46) swap_blocks/on n=50 lifted=50 s1=50 s2=50 s3=50 pressed=50 success=50 prog=1.00
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b16-swap-s4.md
- A40-E22b-ledger-b8-swap-s0: **DONE** (2026-11-21 19:46:10) swap_blocks/on n=44 lifted=44 s1=44 s2=44 s3=44 pressed=0 success=0 prog=0.67
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b8-swap-s0.md
- A40-E22b-ledger-b8-swap-s1: **DONE** (2026-11-21 19:46:13) swap_blocks/on n=45 lifted=45 s1=45 s2=45 s3=45 pressed=0 success=0 prog=0.67
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b8-swap-s1.md
- A40-E22b-ledger-b8-swap-s2: **DONE** (2026-11-21 19:47:06) swap_blocks/on n=46 lifted=46 s1=46 s2=46 s3=46 pressed=0 success=0 prog=0.67
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b8-swap-s2.md
- A40-E22b-ledger-b8-swap-s3: **DONE** (2026-11-21 19:49:33) swap_blocks/on n=47 lifted=47 s1=47 s2=47 s3=47 pressed=0 success=0 prog=0.67
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b8-swap-s3.md
- A40-E22b-ledger-b8-swap-s4: **DONE** (2026-11-21 20:03:37) swap_blocks/on n=50 lifted=50 s1=50 s2=50 s3=50 pressed=0 success=0 prog=0.67
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b8-swap-s4.md
- A40-E22b-ledger-b4-swap-s0: **DONE** (2026-11-21 20:17:22) swap_blocks/on n=28 lifted=28 s1=28 s2=28 s3=28 pressed=0 success=0 prog=0.67
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b4-swap-s0.md
- A40-E22b-ledger-b4-swap-s1: **DONE** (2026-11-21 20:27:24) swap_blocks/on n=35 lifted=35 s1=35 s2=35 s3=35 pressed=0 success=0 prog=0.67
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22b-ledger-b4-swap-s1.md
- A40-E21-verdict: **PASS** (2026-11-21 02:36:11) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E21-verdict.md
- A40-E22a-fetch-256: **PASS** (2026-11-21 16:28:50) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22a-fetch-256.md
- A40-E22a-verdict-256: **PASS** (2026-11-21 16:31:11) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-E22a-verdict-256.md
- A40-fetch-rearrange_clock-e30: **PASS** (2026-11-21 19:53:59) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-rearrange_clock-e30.md
- A40-rearrange_clock-smoke: **PASS** (2026-11-21 20:10:59) rearrange_blocks/on n=1  prog=0.00
- A40-fetch-swapT_clock-e30: **PASS** (2026-11-21 20:01:23) rc=0
  autopsy: /workspace/FastWAM-memory2/outputs/memory_v2/autopsy/AUTOPSY_A40-fetch-swapT_clock-e30.md
- A40-E16-rearrange_ar-p64-vis-s0: **DONE** (2026-11-21 20:39:39) rearrange_blocks/on n=10  prog=0.00

## dispatcher log (pool.log, last 40 lines)
```
[pool] 2026-11-21 14:51:42 A40-E17-press_fast-e30-s6: started on GPU 6 (attempt 1, exec pid 1827970)
[pool] 2026-11-21 15:26:09 A40-E17-press_fast-e30-s7: started on GPU 5 (attempt 1, exec pid 1836815)
[pool] 2026-11-21 15:27:45 A40-E17-press_fast-e30-s8: started on GPU 0 (attempt 1, exec pid 1837219)
[pool] 2026-11-21 15:45:29 A40-E17-press_fast-e30-s9: started on GPU 1 (attempt 1, exec pid 1841517)
[pool] 2026-11-21 16:00:31 A40-E22b-clock-b16-swap-s0: started on GPU 4 (attempt 1, exec pid 1846631)
[pool] 2026-11-21 16:03:13 A40-E22b-clock-b16-swap-s1: started on GPU 6 (attempt 1, exec pid 1847722)
[pool] 2026-11-21 16:11:48 A40-E22b-clock-b16-swap-s2: started on GPU 3 (attempt 1, exec pid 1850580)
[pool] 2026-11-21 16:13:25 A40-E22b-clock-b16-swap-s3: started on GPU 7 (attempt 1, exec pid 1851094)
[pool] 2026-11-21 16:34:28 A40-E22b-clock-b16-swap-s4: started on GPU 0 (attempt 1, exec pid 1859066)
[pool] 2026-11-21 16:47:57 A40-E22b-clock-b8-swap-s0: started on GPU 4 (attempt 1, exec pid 1864675)
[pool] 2026-11-21 16:50:06 A40-E22b-clock-b8-swap-s1: started on GPU 6 (attempt 1, exec pid 1865765)
[pool] 2026-11-21 16:58:10 A40-E22b-clock-b8-swap-s2: started on GPU 3 (attempt 1, exec pid 1868865)
[pool] 2026-11-21 16:59:14 A40-E22b-clock-b8-swap-s3: started on GPU 5 (attempt 1, exec pid 1869387)
[pool] 2026-11-21 17:01:25 A40-E22b-clock-b8-swap-s4: started on GPU 7 (attempt 1, exec pid 1870466)
[pool] 2026-11-21 17:08:58 A40-E22b-clock-b4-swap-s0: started on GPU 1 (attempt 1, exec pid 1873622)
[pool] 2026-11-21 17:21:53 A40-E22b-clock-b4-swap-s1: started on GPU 0 (attempt 1, exec pid 1879264)
[pool] 2026-11-21 17:36:23 A40-E22b-clock-b4-swap-s2: started on GPU 4 (attempt 1, exec pid 1885842)
[pool] 2026-11-21 17:40:42 A40-E22b-clock-b4-swap-s3: started on GPU 6 (attempt 1, exec pid 1887519)
[pool] 2026-11-21 17:44:58 A40-E22b-clock-b4-swap-s4: started on GPU 3 (attempt 1, exec pid 1889363)
[pool] 2026-11-21 17:46:36 A40-E22b-ledger-b16-swap-s0: started on GPU 5 (attempt 1, exec pid 1890120)
[pool] 2026-11-21 17:50:52 A40-E22b-ledger-b16-swap-s1: started on GPU 7 (attempt 1, exec pid 1891898)
[pool] 2026-11-21 18:05:25 A40-E22b-ledger-b16-swap-s2: started on GPU 1 (attempt 1, exec pid 1897759)
[pool] 2026-11-21 18:18:20 A40-E22b-ledger-b16-swap-s3: started on GPU 0 (attempt 1, exec pid 1903207)
[pool] 2026-11-21 18:30:13 A40-E22b-ledger-b16-swap-s4: started on GPU 4 (attempt 1, exec pid 1908806)
[pool] 2026-11-21 18:34:30 A40-E22b-ledger-b8-swap-s0: started on GPU 6 (attempt 1, exec pid 1910709)
[pool] 2026-11-21 18:36:07 A40-E22b-ledger-b8-swap-s1: started on GPU 5 (attempt 1, exec pid 1911164)
[pool] 2026-11-21 18:37:43 A40-E22b-ledger-b8-swap-s2: started on GPU 3 (attempt 1, exec pid 1911946)
[pool] 2026-11-21 18:38:47 A40-E22b-ledger-b8-swap-s3: started on GPU 7 (attempt 1, exec pid 1912746)
[pool] 2026-11-21 18:52:47 A40-E22b-ledger-b8-swap-s4: started on GPU 1 (attempt 1, exec pid 1917906)
[pool] 2026-11-21 19:06:14 A40-E22b-ledger-b4-swap-s0: started on GPU 0 (attempt 1, exec pid 1922456)
[pool] 2026-11-21 19:18:03 A40-E22b-ledger-b4-swap-s1: started on GPU 4 (attempt 1, exec pid 1926448)
[pool] 2026-11-21 19:47:29 A40-E22b-ledger-b4-swap-s2: started on GPU 5 (attempt 1, exec pid 1935633)
[pool] 2026-11-21 19:47:29 A40-E22b-ledger-b4-swap-s3: started on GPU 6 (attempt 1, exec pid 1935634)
[pool] 2026-11-21 19:48:33 A40-E22b-ledger-b4-swap-s4: started on GPU 3 (attempt 1, exec pid 1935886)
[pool] 2026-11-21 19:50:44 A40-E16-rearrange_ar-p64-vis-s0: started on GPU 7 (attempt 1, exec pid 1937530)
[pool] 2026-11-21 20:05:17 A40-rearrange_clock-smoke: started on GPU 1 (attempt 1, exec pid 1942183)
[pool] 2026-11-21 20:12:15 A40-E16-rearrange-clock-s0: started on GPU 1 (attempt 1, exec pid 1944490)
[pool] 2026-11-21 20:18:41 A40-E16-rearrange-clock-s1: started on GPU 0 (attempt 1, exec pid 1946916)
[pool] 2026-11-21 20:28:57 A40-E16-rearrange-clock-s2: started on GPU 4 (attempt 1, exec pid 1950874)
[pool] 2026-11-21 20:40:46 A40-E16-rearrange-clock-s3: started on GPU 7 (attempt 1, exec pid 1955416)
```
## lane cpu log (last 10 lines)
```
```

disk free: 7790G

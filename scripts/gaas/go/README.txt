One file per run that a slot job (scripts/gaas/slots.txt) may start. Written by Opus once the run's reading is
registered in gaas_queue.txt and its prerequisites are on the relays (or will be fetched in the job). An empty file
means "ready"; a non-empty file is a cheap shell test (file checks only), run in the repository root on the node.
Remove a file to take a run out of every slot list.

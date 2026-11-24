"""Plan v20 card 8 (11-24, Opus; user 11-24: the benchmark's own generation script may be run). SIMULATOR side: runs in
the simulator python with cwd = the RMBench checkout the closed loop evaluates with (same commit, nothing pulled), started
by `fastwam.memory_v2.online gen` (the same render environment as `plan` / `run`).
It loads RMBench's scripts/collect_data.py UNMODIFIED and calls its main() (config demo_clean, its embodiment and camera
settings) with ONE change made from outside: its run() is replaced by run_seeds() below, a copy of collect_data.run()
whose seed loop starts at --start-seed (the original starts at 0 or after seed.txt) or walks an explicit --seeds list,
and whose save path is --out. The two phases are the original's: (1) setup_demo / play_once / plan_success and
check_success -> save_traj_data, seed.txt after every seed; (2) replay with save_data -> merge_pkl_to_hdf5_video (the
official hdf5 + instruction json + scene_info). Resumable (seed.txt / existing hdf5).
  python -B -u gen_demos.py --task observe_and_pickup --start-seed 10000000 --episodes 155 --out <dir>
  python -B -u gen_demos.py --task observe_and_pickup --seeds 0 1 2 --out <dir>          (render check: official seeds)
Output: <out>/demo_clean/<task>/aloha_agilex/{data/episode_*.hdf5, instruction/, seed.txt, scene_info.json} + GEN.json.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time


def load_collect():
    sys.path.insert(0, os.getcwd())
    spec = importlib.util.spec_from_file_location("rmbench_collect_data", os.path.join(os.getcwd(), "scripts", "collect_data.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--config", default="demo_clean")
    ap.add_argument("--start-seed", type=int, default=None)
    ap.add_argument("--seeds", type=int, nargs="*", default=None)
    ap.add_argument("--episodes", type=int, default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    if (args.start_seed is None) == (args.seeds is None):
        raise SystemExit("give exactly one of --start-seed / --seeds")
    cd = load_collect()
    want = len(args.seeds) if args.seeds is not None else int(args.episodes)
    UnStableError = getattr(cd, "UnStableError", Exception)

    def run_seeds(TASK_ENV, a):
        a["save_path"] = os.path.join(args.out, a["task_config"], str(a["task_name"]),
                                      os.path.basename(a["save_path"]))
        a["episode_num"] = want
        os.makedirs(a["save_path"], exist_ok=True)
        meta = {"task": a["task_name"], "config": a["task_config"], "start_seed": args.start_seed, "seeds": args.seeds,
                "episodes": want, "cwd": os.getcwd(), "started": time.strftime("%F %T")}
        print(f"[gen] {json.dumps(meta)}", flush=True)
        seed_file = os.path.join(a["save_path"], "seed.txt")
        seed_list = []
        if os.path.exists(seed_file):
            seed_list = [int(x) for x in open(seed_file).read().split()]
        queue = list(args.seeds) if args.seeds is not None else None
        epid = (max(seed_list) + 1 if seed_list else args.start_seed) if queue is None else None
        tried = 0
        a["need_plan"] = True
        # ---- phase 1: seeds whose expert succeeds (collect_data.run, seed loop changed only)
        while len(seed_list) < want:
            if queue is not None:
                if not queue:
                    break
                epid = queue.pop(0)
                if epid in seed_list:
                    continue
            suc_num = len(seed_list)
            tried += 1
            try:
                TASK_ENV.setup_demo(now_ep_num=suc_num, seed=epid, **a)
                TASK_ENV.play_once()
                if TASK_ENV.plan_success and TASK_ENV.check_success():
                    print(f"[gen] seed {epid}: expert success -> episode {suc_num}", flush=True)
                    seed_list.append(epid)
                    TASK_ENV.save_traj_data(suc_num)
                else:
                    print(f"[gen] seed {epid}: expert failed", flush=True)
                TASK_ENV.close_env()
            except UnStableError as e:
                print(f"[gen] seed {epid}: unstable ({e})", flush=True)
                TASK_ENV.close_env()
                time.sleep(0.3)
            except Exception as e:                                           # noqa: BLE001 (as the original)
                print(f"[gen] seed {epid}: error ({type(e).__name__}: {e})", flush=True)
                TASK_ENV.close_env()
                time.sleep(1)
            if queue is None:
                epid += 1
            with open(seed_file, "w") as f:
                f.write(" ".join(str(s) for s in seed_list) + " ")
        print(f"[gen] phase 1: {len(seed_list)} expert-successful seeds after {tried} tries", flush=True)
        # ---- phase 2: the original data collection (replay, save the official hdf5)
        a["need_plan"], a["render_freq"], a["save_data"] = False, 0, True
        clear_cache_freq = a["clear_cache_freq"]
        st = 0
        while os.path.exists(os.path.join(a["save_path"], "data", f"episode_{st:07d}.hdf5")):
            st += 1
        lang = os.path.join(a["save_path"], "language_annotation.json")
        for k in range(st, len(seed_list)):
            TASK_ENV.setup_demo(now_ep_num=k, seed=seed_list[k], **a)
            traj = TASK_ENV.load_tran_data(k)
            a["left_joint_path"], a["right_joint_path"] = traj["left_joint_path"], traj["right_joint_path"]
            TASK_ENV.set_path_lst(a)
            info_path = os.path.join(a["save_path"], "scene_info.json")
            db = json.load(open(info_path)) if os.path.exists(info_path) else {}
            info = TASK_ENV.play_once()
            db[f"episode_{k}"] = info
            json.dump(db, open(info_path, "w"), ensure_ascii=False, indent=4)
            ldb = json.load(open(lang)) if os.path.exists(lang) else {}
            ldb[f"episode_{k}"] = TASK_ENV.language_annotation
            json.dump(ldb, open(lang, "w"), ensure_ascii=False, indent=4)
            desc = cd.build_episode_instructions(a, info, k)
            TASK_ENV.close_env(clear_cache=((k + 1) % clear_cache_freq == 0))
            TASK_ENV.merge_pkl_to_hdf5_video(instructions=desc["seen"])
            TASK_ENV.remove_data_cache()
            ok = TASK_ENV.check_success()
            print(f"[gen] episode {k} (seed {seed_list[k]}) saved; check_success {ok}", flush=True)
            if not ok:
                raise SystemExit("Collect Error (the replay did not succeed), as the original's assert")
        meta.update(finished=time.strftime("%F %T"), seeds_ok=seed_list, tries=tried)
        json.dump(meta, open(os.path.join(a["save_path"], "GEN.json"), "w"), indent=1)
        print(f"[gen] done: {len(seed_list)} episodes in {a['save_path']}", flush=True)

    cd.run = run_seeds
    import torch.multiprocessing as mp
    mp.set_start_method("spawn", force=True)
    cd.main(args.task, args.config)


if __name__ == "__main__":
    main()

"""robomme_convert.py on fake HDF5 files built like RoboMME's RecordWrapper writes them (src/robomme/env_record_wrapper/
RecordWrapper.py, doc/h5_data_format.md): timestep_<i>[_dup<k>], video-demo steps, a "None" action, a (1, 8) action,
string setup fields. The converter is run from a tools folder holding it, h5_events.py and events.py, as the 5090
launcher does.  python3 -m pytest -q -p no:cacheprovider scripts/robomme/tests"""
import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
h5py = pytest.importorskip("h5py")

REPO = Path(__file__).resolve().parents[3]
GOALS = {"PickXtimes": ("pick up the red cube two times", 2), "BinFill": ("put two red cubes and one blue cube into the bin", 3)}


def _write_episode(h, n, task, seed, cycles, video_steps=2, none_at=None, wide_at=None, dup_at=None):
    ep = h.create_group(f"episode_{n}")
    t = 0
    z_plan, g_plan = [], []
    for _ in range(video_steps):                                    # conditioning video (skipped by the converter)
        z_plan.append(0.30); g_plan.append(1.0)
    for c in range(cycles):                                         # down, close, up, move, down, open, up
        for z in np.linspace(0.30, 0.10, 6):
            z_plan.append(z); g_plan.append(1.0)
        for _ in range(2):
            z_plan.append(0.10); g_plan.append(-1.0)
        for z in np.linspace(0.10, 0.30, 6):
            z_plan.append(z); g_plan.append(-1.0)
        for z in np.linspace(0.30, 0.12, 6):
            z_plan.append(z); g_plan.append(-1.0)
        for _ in range(2):
            z_plan.append(0.12); g_plan.append(1.0)
        for z in np.linspace(0.12, 0.30, 6):
            z_plan.append(z); g_plan.append(1.0)
    rng = np.random.default_rng(n)
    for i, (z, g) in enumerate(zip(z_plan, g_plan)):
        name = f"timestep_{t}"
        if dup_at is not None and i == dup_at:
            name = f"timestep_{t - 1}_dup1"                        # the recorder's collision suffix
        else:
            t += 1
        ts = ep.create_group(name)
        obs = ts.create_group("obs")
        obs.create_dataset("front_rgb", data=np.full((256, 256, 3), i % 256, np.uint8))
        obs.create_dataset("wrist_rgb", data=rng.integers(0, 255, (256, 256, 3), dtype=np.uint8))
        obs.create_dataset("front_depth", data=np.zeros((256, 256, 1), np.int16))
        obs.create_dataset("wrist_depth", data=np.zeros((256, 256, 1), np.int16))
        obs.create_dataset("joint_state", data=np.full(7, i, np.float32))
        obs.create_dataset("gripper_state", data=np.full(2, 0.04 if g > 0 else 0.0, np.float32))
        obs.create_dataset("is_gripper_close", data=g < 0)
        obs.create_dataset("front_camera_extrinsic", data=np.zeros((3, 4), np.float32))
        obs.create_dataset("wrist_camera_extrinsic", data=np.zeros((3, 4), np.float32))
        x = 0.1 * i                                                 # the end effector also travels sideways
        obs.create_dataset("eef_state", data=np.array([x, 0.0, z, 0.0, 0.0, 0.0], np.float32))
        act = ts.create_group("action")
        if none_at is not None and i == none_at:
            act.create_dataset("joint_action", data="None", dtype=h5py.special_dtype(vlen=str))
        elif wide_at is not None and i == wide_at:
            act.create_dataset("joint_action", data=np.array([[0.5] * 7 + [g]], np.float32))     # (1, 8)
        else:
            act.create_dataset("joint_action", data=np.array([0.5] * 7 + [g], np.float32))
        act.create_dataset("eef_action", data=np.array([x, 0.0, z, 0.0, 0.0, 0.0, g], np.float32))
        act.create_dataset("waypoint_action", data=np.full(7, np.nan, np.float32))
        act.create_dataset("choice_action", data="{}", dtype=h5py.special_dtype(vlen=str))
        info = ts.create_group("info")
        text = "pick up the cube" if g > 0 else "put down the cube"
        for k in ("simple_subgoal", "simple_subgoal_online", "grounded_subgoal", "grounded_subgoal_online"):
            info.create_dataset(k, data=text.encode())
        info.create_dataset("is_completed", data=i == len(z_plan) - 1)
        info.create_dataset("is_video_demo", data=i < video_steps)
        info.create_dataset("is_subgoal_boundary", data=i % 10 == 0)
    setup = ep.create_group("setup")
    setup.create_dataset("seed", data=seed)
    setup.create_dataset("available_multi_choices", data="", dtype=h5py.string_dtype(encoding="utf-8"))
    setup.create_dataset("difficulty", data="easy", dtype=h5py.string_dtype(encoding="utf-8"))
    setup.create_dataset("front_camera_intrinsic", data=np.eye(3, dtype=np.float32))
    setup.create_dataset("task_goal", data=np.asarray([GOALS[task][0], "alt goal"], dtype=object),
                         dtype=h5py.string_dtype(encoding="utf-8"))
    return len(z_plan) - video_steps


@pytest.fixture()
def world(tmp_path):
    tools = tmp_path / "tools"
    tools.mkdir()
    shutil.copy(REPO / "scripts/robomme/robomme_convert.py", tools)
    shutil.copy(REPO / "scripts/robomme/h5_events.py", tools)
    shutil.copy(REPO / "src/fastwam/fullft/events.py", tools)
    data = tmp_path / "data"
    data.mkdir()
    meta = tmp_path / "meta"
    lengths = {}
    for task, (_, cycles) in GOALS.items():
        with h5py.File(data / f"record_dataset_{task}.h5", "w") as h:
            lengths[(task, 0)] = _write_episode(h, 0, task, 1000, cycles, none_at=9, wide_at=11, dup_at=13)
            lengths[(task, 1)] = _write_episode(h, 1, task, 1101, cycles)
            lengths[(task, 2)] = _write_episode(h, 2, task, 77, cycles, video_steps=0)      # seed in no list
        for split, seeds in (("train", [1000, 1101]), ("val", [5]), ("test", [6])):
            (meta / split).mkdir(parents=True, exist_ok=True)
            (meta / split / f"record_dataset_{task}_metadata.json").write_text(json.dumps(
                {"env_id": task, "record_count": len(seeds),
                 "records": [{"task": task, "episode": k, "seed": s, "difficulty": "easy"} for k, s in enumerate(seeds)]}))
    spec = importlib.util.spec_from_file_location("robomme_convert", tools / "robomme_convert.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    yield mod, data, meta, tmp_path / "out", lengths
    for k in ("events", "h5_events", "robomme_convert"):
        sys.modules.pop(k, None)


def _run(mod, data, meta, out, *extra):
    return mod.main(["--data", str(data), "--out", str(out), "--metadata", str(meta), "--min-free-gb", "0", *extra])


def test_layout_values_events(world):
    mod, data, meta, out, lengths = world
    assert _run(mod, data, meta, out, "--commit", "test") == 0
    recs = json.loads((out / "RECORDS.json").read_text())
    assert [r["episode_id"] for r in recs] == [f"{t}/episode_{k:07d}" for t in ("PickXtimes", "BinFill") for k in range(3)]
    by = {r["episode_id"]: r for r in recs}
    assert by["PickXtimes/episode_0000000"]["N"] == 2 and by["BinFill/episode_0000000"]["N"] == 3
    assert [by[f"PickXtimes/episode_{k:07d}"]["robomme_split"] for k in range(3)] == ["train", "train", "unknown"]
    z = np.load(out / "PickXtimes/episode_0000000.npz")
    T = lengths[("PickXtimes", 0)]
    assert z["front_rgb"].shape == (T, 256, 256, 3) and z["front_rgb"].dtype == np.uint8
    assert z["joint_state"].shape == (T, 7) and z["eef_state"].shape == (T, 6) and z["gripper_state"].shape == (T, 2)
    assert z["joint_action"].shape == (T, 8) and z["eef_action"].shape == (T, 7)
    # the 2 video-demo steps are gone: row 0 is recorded step 2 (front_rgb holds the recorded index i)
    assert int(z["front_rgb"][0, 0, 0, 0]) == 2 and z["joint_state"][0, 0] == 2.0
    # None action (recorded i = 9 -> row 7): invalid, NaN; the (1, 8) action (i = 11 -> row 9) is read as 8 numbers
    assert not z["action_valid"][7] and np.isnan(z["joint_action"][7]).all() and z["action_valid"].sum() == T - 1
    assert z["joint_action"][9].tolist()[:7] == [0.5] * 7
    # the dup step (recorded i = 13, named timestep_<t-1>_dup1) sits right after its base step
    assert z["joint_state"][10, 0] == 12.0 and z["joint_state"][11, 0] == 13.0
    assert z["source_step"][10] == z["source_step"][11]
    j = json.loads((out / "PickXtimes/episode_0000000.json").read_text())
    assert j["skipped_video_demo_steps"] == 2 and j["invalid_action_rows"] == 1 and j["goals"][1] == "alt goal"
    assert j["difficulty"] == "easy" and j["seed"] == 1000 and j["simple_subgoal_runs"][0][2] == "pick up the cube"
    # events: our rule, one close and one open per cycle (count N), file format = fullft's
    ev = json.loads((out / "events_PickXtimes.json").read_text())
    assert ev["rule"].startswith("EventRule(")
    for k in range(3):
        e = ev["episodes"][f"PickXtimes/episode_{k:07d}"]
        assert sum(x["kind"] == "close" for x in e) == 2 and sum(x["kind"] == "open" for x in e) == 2
        assert all(x["arm"] == 0 for x in e)
    # the check fullft's load_events makes: the file's rule field gives rule A's thresholds
    assert sys.modules["events"].parse_rule(ev["rule"]) == {"delta": 0.015, "min_path": 0.03}
    b = json.loads((out / "events_BinFill.json").read_text())["episodes"]["BinFill/episode_0000001"]
    assert sum(x["kind"] == "close" for x in b) == 3 and all({"frame", "arm", "kind", "confirmed"} <= set(x) for x in b)
    # the events are the rule applied to the stored rows (gripper command of the action, height of the end effector)
    cmd, last = [], 1.0
    for ok, a in zip(z["action_valid"], z["joint_action"]):
        last = (float(a[7]) + 1.0) / 2.0 if ok else last
        cmd.append([last, 1.0])
    pos = np.stack([z["eef_state"][:, :3], np.zeros((T, 3))], axis=1)
    again = sys.modules["events"].detect(np.asarray(cmd), pos)
    assert again == ev["episodes"]["PickXtimes/episode_0000000"]
    ident = json.loads((out / "IDENTITY.json").read_text())
    assert ident["commit"] == "test" and len(ident["sources"]) == 2 and len(ident["sources"][0]["sha256"]) == 64


def test_resume_never_rewrites(world):
    mod, data, meta, out, _ = world
    assert _run(mod, data, meta, out) == 0
    f = out / "BinFill/episode_0000001.npz"
    before = {p: p.stat().st_mtime_ns for p in out.rglob("episode_*")}
    (out / "BinFill/episode_0000002.json").unlink()                  # an unfinished episode is redone
    assert _run(mod, data, meta, out) == 0
    after = {p: p.stat().st_mtime_ns for p in out.rglob("episode_*")}
    changed = sorted(p.name for p in after if before.get(p) != after[p])
    assert changed == ["episode_0000002.json", "episode_0000002.npz"] and f.stat().st_mtime_ns == before[f]
    assert len(json.loads((out / "RECORDS.json").read_text())) == 6


def test_limit_and_size(world):
    mod, data, meta, out, lengths = world
    assert _run(mod, data, meta, out, "--limit", "1", "--size", "224", "--tasks", "PickXtimes") == 0
    z = np.load(out / "PickXtimes/episode_0000000.npz")
    assert z["front_rgb"].shape == (lengths[("PickXtimes", 0)], 224, 224, 3) and z["wrist_rgb"].dtype == np.uint8
    assert int(z["front_rgb"][0, 100, 100, 0]) == 2                  # a flat image stays flat after resizing
    assert len(json.loads((out / "RECORDS.json").read_text())) == 1

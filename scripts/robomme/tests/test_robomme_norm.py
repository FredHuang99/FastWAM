"""11-28 RoboMME step 2: robomme_norm.py on a fake dense root (stats from train only, held invalid actions, wrap stop)."""
import importlib.util
import json
import math
import sys
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("robomme_norm", HERE / "robomme_norm.py")
norm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(norm)


def make_root(tmp, wrap=False):
    recs = []
    for k, split in enumerate(("train", "train", "val")):
        eid = f"PickXtimes/episode_{k}"
        d = tmp / "cache" / eid.replace("/", "_")
        d.mkdir(parents=True)
        L = 6
        pr = torch.arange(L * 8, dtype=torch.float32).reshape(L, 8) / 10 + k
        ac = torch.arange(L * 7, dtype=torch.float32).reshape(L, 7) / 10 - k
        ac[:, 6] = torch.tensor([-1., -1, 1, 1, -1, 1])
        if wrap and k == 1:
            pr[3, 4] += 2 * math.pi
        valid = torch.ones(L, dtype=torch.bool)
        valid[2] = False
        ac[2] = 100.0                                   # an invalid action must not enter the stats
        torch.save({"latent": torch.zeros(L, 2), "proprio_raw": pr, "actions_raw": ac, "action_valid": valid}, d / "encodings.pt")
        (d / "COMPLETE.json").write_text("{}")
        recs.append({"episode_id": eid, "task": "PickXtimes", "split": split, "length": L})
    (tmp / "RECORDS.json").write_text(json.dumps(recs))
    return recs


def run(root, *args):
    old = sys.argv
    sys.argv = ["robomme_norm.py", "--root", str(root), *args]
    try:
        return norm.main()
    finally:
        sys.argv = old


def test_norm_writes_keys(tmp_path):
    make_root(tmp_path)
    assert run(tmp_path) == 0
    st = json.loads((tmp_path / "NORM_STATS.json").read_text())
    assert st["invalid_action_frames"] == 3 and st["stats"]["actions"]["frames"] == 10
    assert max(st["stats"]["actions"]["max"][:6]) < 100            # invalid action left out
    e = torch.load(tmp_path / "cache/PickXtimes_episode_0/encodings.pt", weights_only=True)
    assert e["proprio"].shape == (6, 8) and e["actions"].shape == (6, 7)
    assert torch.equal(e["actions"][2], e["actions"][1])           # held
    assert e["proprio"][:, 0].min() >= -1 - 1e-6 and float(e["actions"][:, 6].abs().max()) == 1.0
    assert torch.equal(e["proprio_raw"], torch.arange(48, dtype=torch.float32).reshape(6, 8) / 10)   # raw kept
    assert json.loads((tmp_path / "CACHE.json").read_text())["episodes"] == 3
    assert run(tmp_path) == 0                                        # second run skips
    v = torch.load(tmp_path / "cache/PickXtimes_episode_2/encodings.pt", weights_only=True)
    assert v["proprio"].max() > 1                                    # val outside the train range is not clipped to 1


def test_wrap_stops(tmp_path):
    make_root(tmp_path, wrap=True)
    assert run(tmp_path) == 1
    assert json.loads((tmp_path / "NORM_STATS.json").read_text())["angle_wrap_episodes"] == 1
    e = torch.load(tmp_path / "cache/PickXtimes_episode_0/encodings.pt", weights_only=True)
    assert "proprio" not in e and not (tmp_path / "CACHE.json").exists()

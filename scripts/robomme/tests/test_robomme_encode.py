"""robomme_encode.py without the real VAE / T5 (they run on the 5090): clip indices and padding, the episode loop with
fake encoders (shapes, valid masks, raw proprio / actions, splits, resume, events copy). The image pipeline itself
needs torchvision and Fast-WAM's dataset code; it is tested only where torchvision is installed.
  python3 -m pytest -q -p no:cacheprovider scripts/robomme/tests"""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
torch = pytest.importorskip("torch")

REPO = Path(__file__).resolve().parents[3]


@pytest.fixture()
def mod():
    spec = importlib.util.spec_from_file_location("robomme_encode", REPO / "scripts/robomme/robomme_encode.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    yield m
    sys.modules.pop("robomme_encode", None)


def test_clip_indices(mod):
    assert mod.OFFSETS == [0, 4, 8, 12, 16, 20, 24, 28, 32]
    idx, ok = mod.clip_indices(0, 100, "repeat")
    assert idx == mod.OFFSETS and all(ok)
    idx, ok = mod.clip_indices(90, 100, "repeat")                  # 90, 94, 98, then past the end
    assert idx == [90, 94, 98] + [99] * 6 and ok == [True] * 3 + [False] * 6
    idx, ok = mod.clip_indices(99, 100, "zero")
    assert idx == [99] + [None] * 8 and ok == [True] + [False] * 8


class FakeEncoders:
    seen = []

    def __init__(self, cfg, device):
        pass

    def frames(self, images):
        return images.mean(dim=(1, 2, 3)).view(-1, 1, 1, 1, 1).expand(-1, 48, 1, 2, 4).clone()

    def clips(self, clips):
        FakeEncoders.seen.append(clips[:, 0, :, 0, 0].clone())      # [B, 9]: the first pixel of each frame
        return clips.mean(dim=(1, 3, 4))[:, :3].view(-1, 1, 3, 1, 1).expand(-1, 48, 3, 2, 4).clone()

    def prompt(self, goal):
        valid = torch.zeros(128, dtype=torch.bool)
        valid[:len(goal.split())] = True
        return torch.ones(128, 16) * valid[:, None], valid


def _convert(tmp_path, n_eps=11, length=40):
    conv = tmp_path / "convert"
    rows = []
    for k in range(n_eps):
        task = "PickXtimes"
        (conv / task).mkdir(parents=True, exist_ok=True)
        f = conv / task / f"episode_{k:07d}.npz"
        frames = np.zeros((length, 16, 16, 3), np.uint8)
        for t in range(length):
            frames[t] = t                                           # the frame index as its colour
        np.savez(f, front_rgb=frames, wrist_rgb=frames, eef_state=np.full((length, 6), 0.5, np.float32),
                 gripper_state=np.full((length, 2), 0.04, np.float32), eef_action=np.ones((length, 7), np.float32),
                 action_valid=np.ones(length, bool), joint_state=np.zeros((length, 7), np.float32),
                 joint_action=np.zeros((length, 8), np.float32))
        f.with_suffix(".json").write_text(json.dumps({"goal": "pick up the red cube two times"}))
        rows.append({"episode_id": f"{task}/episode_{k:07d}", "task": task, "split": "train", "robomme_split": "train",
                     "N": 2, "length": length, "seed": 1000 + k, "difficulty": "easy",
                     "file": f"{task}/episode_{k:07d}.npz"})
    (conv / "RECORDS.json").write_text(json.dumps(rows))
    (conv / "IDENTITY.json").write_text(json.dumps({"commit": "x"}))
    (conv / "events_PickXtimes.json").write_text(json.dumps({"rule": "EventRule()", "episodes": {}}))
    root = tmp_path / "rt"
    root.mkdir()
    (root / "IDENTITY.json").write_text(json.dumps({"config": {"paths": {}}}))
    return conv, root


def _image(front, wrist):                                           # stands in for the torchvision pipeline
    x = torch.from_numpy(np.concatenate([front, wrist], axis=2)).permute(0, 3, 1, 2).float()
    return x / 255.0 * 2 - 1


def test_episode_loop(mod, tmp_path, monkeypatch):
    conv, root = _convert(tmp_path)
    monkeypatch.setattr(mod, "Encoders", FakeEncoders)
    monkeypatch.setattr(mod, "libero_image", _image)
    monkeypatch.setattr(mod, "image_selftest", lambda: True)
    monkeypatch.setattr(mod, "pipeline_check",
                        lambda enc, r, report: report.update(last_clip={"repeat": [True, 0.0]}) or True)
    out = tmp_path / "out"
    assert mod.main(["--convert", str(conv), "--out", str(out), "--check-root", str(root), "--batch", "3"]) == 0
    recs = json.loads((out / "RECORDS.json").read_text())
    assert len(recs) == 11 and [r["split"] for r in recs] == ["train"] * 9 + ["val", "train"]
    e = torch.load(out / "cache/PickXtimes_episode_0000000/encodings.pt", weights_only=True)
    assert e["latent"].shape == (40, 48, 1, 2, 4) and e["video_latent"].shape == (40, 48, 3, 2, 4)
    assert e["video_valid"].shape == (40, 9) and e["video_valid"][0].all()
    assert e["video_valid"][39].tolist() == [True] + [False] * 8 and e["video_valid"][30].tolist() == [True] * 3 + [False] * 6
    assert "proprio" not in e and "actions" not in e
    assert e["proprio_raw"].shape == (40, 8) and float(e["proprio_raw"][0, 6]) == pytest.approx(0.04)
    assert e["actions_raw"].shape == (40, 7) and e["text"].shape == (128, 16) and int(e["text_valid"].sum()) == 7
    # the clip of the last anchor repeats the last frame (colour 39): every one of its 9 frames
    last = torch.cat(FakeEncoders.seen)[39]
    assert torch.allclose(last, torch.full((9,), 39 / 255.0 * 2 - 1))
    assert torch.allclose(torch.cat(FakeEncoders.seen)[0], torch.tensor([t / 255.0 * 2 - 1 for t in mod.OFFSETS]))
    assert (out / "events/events_PickXtimes.json").exists()
    ident = json.loads((out / "IDENTITY.json").read_text())
    assert ident["clip"]["padding"] == "repeat" and ident["episodes"] == 11
    # resume: finished episodes are not encoded again
    before = (out / "cache/PickXtimes_episode_0000003/encodings.pt").stat().st_mtime_ns
    FakeEncoders.seen = []
    assert mod.main(["--convert", str(conv), "--out", str(out), "--check-root", str(root)]) == 0
    assert FakeEncoders.seen == [] and (out / "cache/PickXtimes_episode_0000003/encodings.pt").stat().st_mtime_ns == before


def test_failed_check_encodes_nothing(mod, tmp_path, monkeypatch):
    conv, root = _convert(tmp_path, n_eps=2)
    monkeypatch.setattr(mod, "Encoders", FakeEncoders)
    monkeypatch.setattr(mod, "pipeline_check", lambda enc, r, report: False)
    monkeypatch.setattr(mod, "image_selftest", lambda: True)
    out = tmp_path / "out"
    assert mod.main(["--convert", str(conv), "--out", str(out), "--check-root", str(root)]) == 1
    assert not (out / "cache").exists() and (out / "IDENTITY.json").exists()


def test_libero_image_pipeline(mod):
    pytest.importorskip("torchvision")
    sys.path.insert(0, str(REPO / "src"))
    pytest.importorskip("fastwam.datasets.dataset_utils")
    f = np.full((3, 256, 256, 3), 255, np.uint8)
    w = np.zeros((3, 256, 256, 3), np.uint8)
    x = mod.libero_image(f, w)
    assert x.shape == (3, 3, 224, 448)
    assert torch.allclose(x[..., :224], torch.ones(1)) and torch.allclose(x[..., 224:], -torch.ones(1))

"""History selection and archive tests (pure Python; torch only for collate)."""
import pytest

from fastwam.memory_v2.config import (HistoryPolicyConfig, ROLE_ANCHOR, ROLE_CURRENT, ROLE_LANDMARK,
                                      ROLE_RECENT)
from fastwam.memory_v2.history import EpisodeArchive, select_history


def test_never_reads_future_and_excludes_current_by_default():
    policy = HistoryPolicyConfig(anchor_frames=1, landmark_stride=24, recent_frames=2, recent_stride=8)
    selection = select_history(range(0, 201), 100, policy)
    assert all(i < 100 for i in selection.ids)
    assert 0 in selection.ids and selection.roles[selection.ids.index(0)] == ROLE_ANCHOR
    assert 92 in selection.ids and 84 in selection.ids
    assert {i for i, r in zip(selection.ids, selection.roles) if r == ROLE_LANDMARK} == {24, 48, 72, 96}


def test_include_current_marks_role():
    policy = HistoryPolicyConfig(include_current=True)
    selection = select_history(range(10), 9, policy)
    assert selection.ids[-1] == 9 and selection.roles[-1] == ROLE_CURRENT


def test_first_decision_has_empty_history():
    assert len(select_history([0], 0, HistoryPolicyConfig())) == 0


def test_cap_keeps_anchor_and_recent():
    policy = HistoryPolicyConfig(anchor_frames=2, landmark_stride=1, recent_frames=2, recent_stride=1, max_frames=8)
    selection = select_history(range(1000), 999, policy)
    assert len(selection) == 8
    assert {0, 1, 998, 997} <= set(selection.ids)
    roles = dict(zip(selection.ids, selection.roles))
    assert roles[0] == roles[1] == ROLE_ANCHOR and roles[998] == roles[997] == ROLE_RECENT


def test_offline_equals_online_for_dense_archive():
    policy = HistoryPolicyConfig()
    archive = EpisodeArchive(policy)
    archive.reset("env0", "put_back_block:1", "sig")
    for frame in range(0, 120):
        archive.append("env0", frame, frame, "sig")
        if frame % 24 == 0:
            online, payload = archive.select("env0", frame)
            offline = select_history(range(frame + 1), frame, policy)
            assert online == offline and payload == list(offline.ids)


def test_archive_idempotent_and_isolated():
    archive = EpisodeArchive(HistoryPolicyConfig())
    archive.reset(0, "a", "sig")
    archive.reset(1, "b", "sig")
    assert archive.append(0, 0, "x", "sig") is True
    assert archive.append(0, 0, "x", "sig") is False
    with pytest.raises(ValueError):
        archive.append(0, 0, "y", "sig")
    with pytest.raises(ValueError):
        archive.append(0, 1, "z", "other-signature")
    archive.append(0, 5, "f5", "sig")
    with pytest.raises(ValueError):
        archive.append(0, 3, "late", "sig")
    assert archive.ids(1) == []
    archive.reset(0, "c", "sig")
    assert archive.ids(0) == []


def test_unknown_current_rejected():
    with pytest.raises(ValueError):
        select_history([0, 1, 2], 5, HistoryPolicyConfig())


def test_mixed_strides_are_deterministic_and_training_only():
    from fastwam.memory_v2.config import V2Config
    from fastwam.memory_v2.history import pairs_with_strides, pick_stride, row_policy, with_strides
    policy = V2Config.from_dict({"history": {"landmark_strides": [8, 12, 16, 24, 32]}}).history
    assert policy.landmark_strides == (8, 12, 16, 24, 32) and policy.landmark_stride == 24
    assert V2Config.from_dict(V2Config.from_dict({"history": {"landmark_strides": [8, 16]}}).to_dict()).history.landmark_strides == (8, 16)
    with pytest.raises(ValueError):
        HistoryPolicyConfig(landmark_strides=[8, 0])
    rows = [{"episode_id": f"e{e}", "anchor": a} for e in range(4) for a in range(0, 400, 5)]
    a, b = with_strides(rows, policy.landmark_strides, 17, 1), with_strides(rows, policy.landmark_strides, 17, 1)
    assert a == b and {r["landmark_stride"] for r in a} == set(policy.landmark_strides)
    assert with_strides(rows, policy.landmark_strides, 17, 2) != a                  # a new draw every epoch
    assert with_strides(rows, (), 17, 1) == rows                                   # fixed stride: rows unchanged
    assert pick_stride((8, 24), 1, "x") == pick_stride((8, 24), 1, "x")
    pairs = [{"query": rows[i], "donor": rows[-1 - i], "task": "t"} for i in range(30)]
    for p in pairs_with_strides(pairs, policy.landmark_strides, 17, 3):
        assert p["query"]["landmark_stride"] == p["donor"]["landmark_stride"]
    assert "landmark_stride" not in pairs[0]["query"]
    window = {"episode_id": "e0", "anchor": 300}                                     # evaluation / online: no field
    assert row_policy(policy, window) is policy
    s8 = select_history(range(301), 300, row_policy(policy, dict(window, landmark_stride=8)))
    s24 = select_history(range(301), 300, row_policy(policy, window))
    assert len(s8.ids) > len(s24.ids) and s24 == select_history(range(301), 300, HistoryPolicyConfig())

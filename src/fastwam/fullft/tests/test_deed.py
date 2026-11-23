"""Plan v19 3.2 (11-22, Deed Memory training parts) on CPU: (1) decision-point weighting and (2) the next-event head.
Acceptance (plan v19): with the parts off, samples, parameters, random draws and the training loss are exactly the
earlier ones; each part has a unit test."""
import json

import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("einops")

from torch import nn  # noqa: E402

from fastwam.fullft.data import (NEXT_EVENT_CLASSES, DenseEpisodes, Samples, collate, decision_weight,  # noqa: E402
                                 next_event_label, train_items)
from fastwam.fullft.history import HistoryRule  # noqa: E402
from fastwam.fullft.model import FullModel  # noqa: E402

LAYERS, HEADS, HEAD_DIM, VIDEO, ACTION, TEXT = 2, 4, 24, 96, 32, 16

EVENTS = [{"frame": 10, "arm": 0, "kind": "close", "confirmed": 10},
          {"frame": 20, "arm": 0, "kind": "bottom", "confirmed": 24},
          {"frame": 30, "arm": 1, "kind": "open", "confirmed": 30},
          {"frame": 30, "arm": 0, "kind": "top", "confirmed": 33}]


def _model(next_event=False, seed=0, variant="ar", next_pose=False):
    from fastwam.models.wan22.action_dit import ActionDiT
    from fastwam.models.wan22.mot import MoT
    from fastwam.models.wan22.wan_video_dit import WanVideoDiT
    torch.manual_seed(seed)
    video = WanVideoDiT(hidden_dim=VIDEO, in_dim=48, ffn_dim=64, out_dim=48, text_dim=TEXT, freq_dim=32, eps=1e-6,
                        patch_size=(1, 2, 2), num_heads=HEADS, attn_head_dim=HEAD_DIM, num_layers=LAYERS,
                        has_image_input=False, seperated_timestep=True, fuse_vae_embedding_in_latents=True,
                        action_dim=14, video_attention_mask_mode="first_frame_causal")
    action = ActionDiT(hidden_dim=ACTION, action_dim=14, ffn_dim=64, text_dim=TEXT, freq_dim=32, eps=1e-6,
                       num_heads=HEADS, attn_head_dim=HEAD_DIM, num_layers=LAYERS)
    mot = MoT({"video": video, "action": action}, mot_checkpoint_mixed_attn=False)
    m = FullModel(mot, nn.Linear(14, TEXT), variant=variant, next_event=next_event, next_pose=next_pose)
    rng_after_build = torch.get_rng_state()
    with torch.no_grad():                         # lift zero-initialised output layers (not the new head)
        for name, p in m.named_parameters():
            if p.abs().sum() == 0 and not name.startswith(("hist_gate", "extra", "ledger", "next_event_head",
                                                                       "next_pose_head")):
                p.normal_(0, 0.02)
    return m.float(), rng_after_build


def _dense(tmp_path, n=60, episodes=2):
    root = tmp_path / "dense"
    records = []
    for k in range(episodes):
        eid = f"swap_blocks/episode_{k:07d}"
        folder = root / "cache" / eid.replace("/", "_")
        folder.mkdir(parents=True)
        text = torch.cat((torch.randn(3, TEXT), torch.zeros(12, TEXT)))
        torch.save({"latent": torch.randn(n, 48, 1, 4, 4), "video_latent": torch.randn(n, 48, 3, 4, 4),
                    "video_valid": torch.ones(n, 9, dtype=torch.bool), "text": text,
                    "text_valid": torch.tensor([True] * 3 + [False] * 12), "proprio": torch.randn(n, 14),
                    "actions": torch.randn(n, 14)}, folder / "encodings.pt")
        (folder / "COMPLETE.json").write_text("{}")
        records.append({"episode_id": eid, "task": "swap_blocks", "split": "train", "length": n})
    (root / "RECORDS.json").write_text(json.dumps(records))
    eps = DenseEpisodes([str(root)], ["swap_blocks"])
    return eps, {r["episode_id"]: EVENTS for r in eps.records}


def _noise(batch, seed=1):
    g = torch.Generator().manual_seed(seed)
    b = batch["actions"].shape[0]
    return {"video": torch.randn(batch["video_latent"].shape, generator=g),
            "action": torch.randn(batch["actions"].shape, generator=g),
            "t_video": torch.rand(b, generator=g) * 1000, "t_action": torch.rand(b, generator=g) * 1000}


def test_decision_weight_windows():
    w = [decision_weight(EVENTS, a, 3.0, 16) for a in (0, 10, 23, 24, 29, 39, 40, 45, 46)]
    # close never counts; bottom confirmed at 24 -> 24..39; open confirmed at 30 -> 30..45
    assert w == [1.0, 1.0, 1.0, 3.0, 3.0, 3.0, 3.0, 3.0, 1.0]
    assert decision_weight(EVENTS, 26, 3.0, 2) == 1.0          # window 2: 24, 25 only
    assert decision_weight(EVENTS, 11, 3.0, 16, ("close",)) == 3.0
    assert decision_weight([{"frame": 5, "arm": 0, "kind": "open"}], 5, 2.0, 1) == 2.0   # no 'confirmed' -> its frame
    assert decision_weight([], 5, 3.0, 16) == 1.0


def test_next_event_label():
    labels = [next_event_label(EVENTS, a) for a in (0, 10, 11, 20, 21, 30, 31)]
    # close arm 0 = 0; bottom arm 0 = 2 * 2 + 0 = 4; frame 30: arm 0 (top, 3 * 2 + 0 = 6) before arm 1; none = 8
    assert labels == [0, 0, 4, 4, 6, 6, NEXT_EVENT_CLASSES - 1]
    assert NEXT_EVENT_CLASSES == 9
    assert next_event_label([{"frame": 3, "arm": 1, "kind": "open"}], 0) == 1 * 2 + 1


def test_samples_off_unchanged_on_add_fields(tmp_path):
    eps, events = _dense(tmp_path)
    items = train_items(eps)
    for rule in (HistoryRule("ar"), HistoryRule("arprop", event_max=4, lag=4, ordinal=16)):
        base = Samples(eps, items, rule, events, "valid", augment=True, seed=3)
        off = Samples(eps, items, rule, events, "valid", augment=True, seed=3, decision=None, next_event=False)
        on = Samples(eps, items, rule, events, "valid", augment=True, seed=3, decision=(3.0, 16, ("open", "bottom")),
                     next_event=True)
        for i in (0, 25, 31, 59, 75):
            r0, r1, r2 = base[i], off[i], on[i]
            assert set(r0) == set(r1) and all(torch.equal(r0[k], r1[k]) for k in r0)
            assert set(r2) - set(r0) == {"loss_weight", "next_event"}
            assert all(torch.equal(r0[k], r2[k]) for k in r0)
            e, a = items[i]
            assert float(r2["loss_weight"]) == decision_weight(EVENTS, a, 3.0, 16)
            assert int(r2["next_event"]) == next_event_label(EVENTS, a)
        batch = collate([on[i] for i in (0, 25, 31)])
        assert batch["loss_weight"].tolist() == [1.0, 3.0, 3.0] and batch["next_event"].tolist() == [0, 6, 8]
    with pytest.raises(ValueError):                 # the three-frame model needs the events file for the new parts
        Samples(eps, items, HistoryRule("ar"), {}, "valid", decision=(3.0, 16, ("open",)))
    Samples(eps, items, HistoryRule("ar"), {}, "valid")       # off: no events needed, as before


def test_config_parts(tmp_path):
    from fastwam.fullft.config import load
    cfg = load(None, [])
    assert cfg.decision is None and not cfg.next_event_head
    assert cfg.model.decision_weight == 1.0 and cfg.model.next_event_loss == 0.0
    with pytest.raises(ValueError):
        load(None, ["model.decision_weight=3"])                 # needs data.events
    with pytest.raises(ValueError):
        load(None, ["model.next_event_loss=0.1"])
    ev = ["data.events=[/x/events_swap_blocks.json]"]
    cfg = load(None, ev + ["model.decision_weight=3", "model.next_event_loss=0.1"])
    assert cfg.decision == (3.0, 16, ("open", "bottom")) and cfg.next_event_head
    for bad in ("model.decision_weight=0", "model.decision_window=0", "model.decision_kinds=[press]",
                "model.next_event_loss=-1"):
        with pytest.raises(ValueError):
            load(None, ev + [bad])
    # an export written before 11-22 (its config has none of the new keys) builds the same model as before
    from fastwam.fullft.config import _build, RunConfig
    old = cfg.to_dict()
    for k in ("decision_weight", "decision_window", "decision_kinds", "next_event_loss"):
        old["model"].pop(k)
    rebuilt = _build(RunConfig, old)
    assert rebuilt.decision is None and not rebuilt.next_event_head


def test_head_draws_no_random_numbers_and_changes_nothing_at_start(tmp_path):
    m0, rng0 = _model(next_event=False)
    m1, rng1 = _model(next_event=True)
    assert torch.equal(rng0, rng1)                             # the head drew no random number
    s0, s1 = m0.state_dict(), m1.state_dict()
    assert set(s1) - set(s0) == {"next_event_head.weight", "next_event_head.bias"}
    assert all(torch.equal(s0[k], s1[k]) for k in s0)
    assert m1.next_event_head.weight.shape == (NEXT_EVENT_CLASSES, ACTION)
    eps, events = _dense(tmp_path)
    items = train_items(eps)
    ds = Samples(eps, items, HistoryRule("ar"), events, "valid", next_event=True)
    batch = collate([ds[i] for i in (5, 25, 40)])
    noise = _noise(batch)
    v0, a0 = m0.loss(batch, noise)
    aux = {}
    v1, a1 = m1.loss(batch, noise, aux=aux)
    assert torch.equal(v0, v1) and torch.equal(a0, a1)         # the returned losses do not depend on the head
    assert torch.allclose(aux["next_event"], torch.full((3,), float(torch.log(torch.tensor(9.0)))))
    v2, a2 = m1.loss(batch, noise)                             # no aux: head not run
    assert torch.equal(v1, v2) and torch.equal(a1, a2)
    # step 0: the zero head sends no gradient into the trunk; the head itself gets one
    aux = {}
    m1.loss(batch, noise, aux=aux)
    aux["next_event"].mean().backward()
    trunk = [p.grad for n, p in m1.named_parameters() if not n.startswith("next_event_head") and p.grad is not None]
    assert all(float(g.abs().sum()) == 0.0 for g in trunk)
    assert float(m1.next_event_head.weight.grad.abs().sum()) > 0
    # after one step on the head, the cross entropy reaches the action branch
    with torch.no_grad():
        m1.next_event_head.weight -= 0.5 * m1.next_event_head.weight.grad
    m1.zero_grad()
    aux = {}
    m1.loss(batch, noise, aux=aux)
    aux["next_event"].mean().backward()
    g = sum(float(p.grad.abs().sum()) for n, p in m1.named_parameters()
            if n.startswith("mot.mixtures.action") and p.grad is not None)
    assert g > 0


def test_objective_off_is_the_earlier_expression_and_on_weights():
    from fastwam.fullft.config import load
    from fastwam.fullft.train import objective
    cfg = load(None, ["model.video_loss=0.7"])
    g = torch.Generator().manual_seed(0)
    v, a = torch.rand(4, generator=g), torch.rand(4, generator=g)
    earlier = (cfg.model.video_loss * v.mean() + cfg.model.action_loss * a.mean()) / 8
    assert torch.equal(objective(cfg, v, a, {}, None, 8), earlier)
    assert torch.equal(objective(cfg, v, a, {}, {}, 8), earlier)            # an empty aux adds nothing
    w = torch.tensor([3.0, 1.0, 1.0, 3.0])
    want = (0.7 * (w * v).mean() + 1.0 * (w * a).mean()) / 8
    assert torch.allclose(objective(cfg, v, a, {"loss_weight": w}, None, 8), want)
    cfg2 = load(None, ["data.events=[/x.json]", "model.next_event_loss=0.1"])
    ce = torch.tensor([2.0, 1.0, 0.5, 0.5])
    got = objective(cfg2, v, a, {}, {"next_event": ce}, 8)
    assert torch.allclose(got, (v.mean() + a.mean()) / 8 + 0.1 * ce.mean() / 8)


def test_export_with_head_loads_strict(tmp_path):
    """online.load_export builds the head from the export's config (strict load); exports without it are unchanged."""
    m1, _ = _model(next_event=True)
    m0, _ = _model(next_event=False)
    with pytest.raises(RuntimeError):
        m0.load_state_dict(m1.state_dict(), strict=True)
    m1b, _ = _model(next_event=True, seed=5)
    m1b.load_state_dict(m1.state_dict(), strict=True)


# ----------------------------------------------------------------------------- (3) in-place repeat count, (4) augmentation
PLACE = {"A": [0.0] * 6, "B": [1.0] * 6}
FRAMES = {10: "A", 12: "A", 20: "A", 22: "A", 30: "A", 32: "A", 40: "B", 42: "B", 50: "B", 52: "B", 45: "A"}
PRESSES = sorted([{"frame": f, "arm": 0, "kind": "bottom", "confirmed": f + 1} for f in (10, 20, 30, 40, 50)]
                 + [{"frame": f, "arm": 0, "kind": "top", "confirmed": f + 1} for f in (12, 22, 32, 42, 52)]
                 + [{"frame": 45, "arm": 1, "kind": "bottom", "confirmed": 46}], key=lambda e: e["frame"])


def _proprio(f):
    p = torch.zeros(14)
    place = PLACE[FRAMES.get(int(f), "A")]
    p[0:6] = torch.tensor(place)
    p[7:13] = torch.tensor(place) + 5.0        # the right arm's joints never matter for the left arm's count
    p[6] = p[13] = 0.3
    return p


def test_repeat_count_resets_at_a_new_place():
    from fastwam.fullft.history import ledger_entries, with_ordinals, with_repeats
    got = with_repeats(PRESSES, _proprio, 0.5)
    by = {(e["frame"], e["kind"], e["arm"]): e["ordinal"] for e in got}
    assert [by[(f, "bottom", 0)] for f in (10, 20, 30, 40, 50)] == [1, 2, 3, 1, 2]
    assert [by[(f, "top", 0)] for f in (12, 22, 32, 42, 52)] == [1, 2, 3, 1, 2]
    assert by[(45, "bottom", 1)] == 1
    assert [e["ordinal"] for e in with_ordinals(PRESSES) if e["kind"] == "bottom" and e["arm"] == 0] == [1, 2, 3, 4, 5]
    rule = HistoryRule("arprop", event_max=3, ordinal=16, repeat_theta=0.5)
    capped = ledger_entries(rule, 100, PRESSES, _proprio)          # counted over everything, then capped
    assert [(e["frame"], e["ordinal"]) for e in capped] == [(45, 1), (50, 2), (52, 2)]
    with pytest.raises(ValueError):
        ledger_entries(rule, 100, PRESSES)                         # needs proprio_of
    off = HistoryRule("arprop", event_max=3, ordinal=16)
    assert ledger_entries(off, 100, PRESSES, _proprio) == ledger_entries(off, 100, PRESSES)   # proprio ignored when off
    for bad in (dict(repeat_theta=-1.0, ordinal=16), dict(repeat_theta=0.5)):
        with pytest.raises(ValueError):
            HistoryRule("arprop", **bad)


def test_repeat_count_in_samples_and_features(tmp_path):
    from fastwam.fullft.data import ledger_tensor
    from fastwam.fullft.history import ledger_entries, ordinal_code
    eps, _ = _dense(tmp_path)
    items = train_items(eps)
    events = {r["episode_id"]: PRESSES for r in eps.records}
    rule = HistoryRule("arprop", event_max=8, ordinal=16, repeat_theta=0.5)
    ds = Samples(eps, items, rule, events, "valid")
    e = eps(items[0][0])
    row = ds[items.index((items[0][0], 55))]
    want = ledger_entries(rule, 55, PRESSES, lambda f: e["proprio"][f])
    feat, valid = ledger_tensor(rule, want, lambda f: e["proprio"][f])
    assert torch.equal(row["ledger"], feat) and torch.equal(row["ledger_valid"], valid)
    flag = 20 + 8
    last = feat[int(valid.sum()) - 1]
    assert last[flag + 1:].tolist() == ordinal_code(want[-1]["ordinal"], 16)


def test_ledger_augmentation():
    import random
    from fastwam.fullft.history import augment_ledger, last_cycle, ledger_entries, run_ended
    rule = HistoryRule("arprop", event_max=32, ordinal=16, repeat_theta=0.5, ledger_over_p=1.0, ledger_over_max=2)
    full = ledger_entries(rule, 34, PRESSES, _proprio)             # ... b30 (3), t32 (3): the run at A ends (next top at B)
    assert full[-1]["frame"] == 32 and run_ended(full[-1], PRESSES, _proprio, 0.5)
    assert [(e["frame"], e["kind"]) for e in last_cycle(full)] == [(30, "bottom"), (32, "top")]
    seen_k = set()
    for seed in range(20):
        out = augment_ledger(rule, 34, PRESSES, full, _proprio, random.Random(seed))
        assert out[:len(full)] == full                            # the real entries are untouched
        extra = out[len(full):]
        k = len(extra) // 2
        seen_k.add(k)
        assert [(e["frame"], e["kind"], e["ordinal"]) for e in extra] == [
            x for j in range(1, k + 1) for x in ((30, "bottom", 3 + j), (32, "top", 3 + j))]
    assert seen_k == {1, 2}
    mid = ledger_entries(rule, 24, PRESSES, _proprio)              # latest t22 (2): the next top (32) is in place
    assert not run_ended(mid[-1], PRESSES, _proprio, 0.5)
    assert augment_ledger(rule, 24, PRESSES, mid, _proprio, random.Random(0)) == mid
    small = HistoryRule("arprop", event_max=5, ordinal=16, repeat_theta=0.5, ledger_over_p=1.0)
    capped = augment_ledger(small, 34, PRESSES, ledger_entries(small, 34, PRESSES, _proprio), _proprio, random.Random(1))
    assert len(capped) == 5 and capped[-1]["frame"] == 32 and capped[-1]["ordinal"] > 3
    drop = HistoryRule("arprop", event_max=32, ordinal=16, repeat_theta=0.5, ledger_drop_p=1.0, ledger_keep=4)
    base = ledger_entries(drop, 100, PRESSES, _proprio)
    lengths = set()
    for seed in range(30):
        out = augment_ledger(drop, 100, PRESSES, base, _proprio, random.Random(seed))
        assert out == base[-len(out):] and 4 <= len(out) < len(base)   # oldest dropped, last 4 kept, counts kept
        lengths.add(len(out))
    assert len(lengths) > 3
    tiny = ledger_entries(drop, 24, PRESSES, _proprio)[-4:]
    assert augment_ledger(drop, 24, PRESSES, tiny, _proprio, random.Random(0)) == tiny   # nothing older than the last 4
    with pytest.raises(ValueError):
        HistoryRule("arprop", ordinal=16, ledger_over_p=0.3)       # over-count needs the repeat count
    with pytest.raises(ValueError):
        HistoryRule("ar", ledger_drop_p=0.3)


def test_augmentation_in_samples_only_touches_the_ledger(tmp_path):
    eps, _ = _dense(tmp_path)
    items = train_items(eps)
    events = {r["episode_id"]: PRESSES for r in eps.records}
    plain = HistoryRule("arprop", event_max=8, ordinal=16, repeat_theta=0.5)
    aug = HistoryRule("arprop", event_max=8, ordinal=16, repeat_theta=0.5, ledger_drop_p=0.5, ledger_over_p=0.5)
    d0 = Samples(eps, items, plain, events, "valid", augment=True, seed=3)
    d1 = Samples(eps, items, aug, events, "valid", augment=True, seed=3)
    dv = Samples(eps, items, aug, events, "valid", augment=False, seed=3)      # validation: never augmented
    changed = 0
    for i in range(0, len(items), 3):
        r0, r1, rv = d0[i], d1[i], dv[i]
        assert all(torch.equal(r0[k], r1[k]) for k in r0 if not k.startswith("ledger"))
        assert all(torch.equal(r0[k], rv[k]) for k in r0)
        changed += not torch.equal(r0["ledger"], r1["ledger"])
        assert torch.equal(r1["ledger"], d1[i]["ledger"])                       # deterministic per (seed, epoch, item)
    assert changed > 0


# ----------------------------------------------------------------------------- plan v19 3.3: zoom frames (A3)
def test_zoom_crop_and_rule():
    import numpy as np
    from PIL import Image
    from fastwam.fullft.zoom import ZOOM_REF, box_tag, crop_resize, cur_key, pixel_box, zoom_images
    rng = np.random.default_rng(0)
    head = rng.integers(0, 255, (240, 320, 3), dtype=np.uint8)
    wrists = [rng.integers(0, 255, (120, 160, 3), dtype=np.uint8) for _ in range(2)]
    box = (0.5, 0.0, 1.0, 0.5)
    got = crop_resize(head, box)
    want = np.asarray(Image.fromarray(np.ascontiguousarray(head[0:120, 160:320])).resize((320, 240),
                                                                                           Image.Resampling.BILINEAR))
    assert got.shape == head.shape and got.dtype == np.uint8 and np.array_equal(got, want)
    assert np.array_equal(crop_resize(head, (0.0, 0.0, 1.0, 1.0)), head)          # the full box is the image
    out = zoom_images([head] + wrists, box, 0)
    assert np.array_equal(out[0], got) and out[1] is wrists[0] and out[2] is wrists[1]
    assert pixel_box((0.0, 0.0, 0.001, 0.001), 320, 240) == (0, 0, 1, 1)           # at least one pixel
    with pytest.raises(ValueError):
        crop_resize(head.astype(np.float32), box)
    assert ZOOM_REF == -1 and cur_key(0) == -2 and cur_key(40) == -42
    on = HistoryRule("ar", zoom=True, zoom_ref_box=(0.1, 0.1, 0.5, 0.5), zoom_cur_box=(0.2, 0.4, 0.9, 1.0))
    assert on.max_frames == HistoryRule("ar").max_frames + 2
    assert box_tag(on) != box_tag(HistoryRule("ar", zoom=True)) and len(box_tag(on)) == 8
    for bad in (dict(zoom_ref_box=(0.5, 0.0, 0.4, 1.0)), dict(zoom_cur_box=(0.0, 0.0, 1.0)), dict(zoom_camera=3)):
        with pytest.raises(ValueError):
            HistoryRule("ar", zoom=True, **bad)
    with pytest.raises(ValueError):
        HistoryRule("prop", zoom=True)                         # no history frames to add to
    from fastwam.fullft.history import zoom_positions
    assert zoom_positions(HistoryRule("ar"), 40, 3) == (-4.0, 0.0)
    assert zoom_positions(HistoryRule("tw", index="time"), 48, 5) == (-3.0, 0.0)


def _zoom_root(tmp_path, eps, rule, n=60):
    from fastwam.fullft.zoom import box_tag
    root = tmp_path / "zoom"
    root.mkdir()
    g = torch.Generator().manual_seed(9)
    for r in eps.records:
        torch.save({"ref": torch.randn(48, 1, 4, 4, generator=g), "cur": torch.randn(n, 48, 1, 4, 4, generator=g),
                    "tag": box_tag(rule), "episode_id": r["episode_id"], "length": n},
                   root / (r["episode_id"].replace("/", "_") + ".pt"))
    return root


def test_zoom_in_samples(tmp_path):
    from fastwam.fullft.history import select, zoom_positions
    eps, events = _dense(tmp_path)
    items = train_items(eps)
    rule = HistoryRule("ar", zoom=True, zoom_ref_box=(0.1, 0.1, 0.5, 0.5), zoom_cur_box=(0.2, 0.4, 0.9, 1.0))
    root = _zoom_root(tmp_path, eps, rule)
    ds = Samples(eps, items, rule, events, "valid", zoom_root=str(root))
    plain = Samples(eps, items, HistoryRule("ar"), events, "valid")
    eid = items[0][0]
    z = torch.load(root / (eid.replace("/", "_") + ".pt"), weights_only=True)
    e = eps(eid)
    for a in (0, 10, 40, 59):
        row, base = ds[items.index((eid, a))], plain[items.index((eid, a))]
        ids, pos = select(HistoryRule("ar"), a)
        n = len(ids)
        assert row["hist_valid"].tolist() == [True] * (n + 2) + [False] * (rule.max_frames - n - 2)
        k0 = HistoryRule("ar").max_frames
        assert torch.equal(row["hist_latent"][:k0][:n], base["hist_latent"][:n])
        assert torch.equal(row["hist_latent"][n], z["ref"]) and torch.equal(row["hist_latent"][n + 1], z["cur"][a])
        assert torch.equal(row["hist_proprio"][n], e["proprio"][0]) and torch.equal(row["hist_proprio"][n + 1], e["proprio"][a])
        assert row["hist_pos"][n:n + 2].tolist() == list(zoom_positions(rule, a, n))
        assert row["hist_ids"][n:n + 2].tolist() == [-1, -1]
        assert all(torch.equal(row[k], base[k]) for k in ("video_latent", "actions", "proprio", "text"))
    with pytest.raises(ValueError):
        Samples(eps, items, rule, events, "valid")                        # zoom needs its cache folder
    other = HistoryRule("ar", zoom=True, zoom_ref_box=(0.0, 0.0, 0.5, 0.5))
    with pytest.raises(ValueError):
        Samples(eps, items, other, events, "valid", zoom_root=str(root))[0]   # boxes differ from the cache's


def test_zoom_online_decision_equals_offline_sampling():
    """decide_encoded with the zoom frames (session-encoded under ZOOM_REF / cur_key) gives exactly the chunk of
    FullModel.sample on the training-style batch (ordinary frames, then the reference and the current crop)."""
    from fastwam.fullft.history import select, zoom_positions
    from fastwam.fullft.online import FrameCache, decide_encoded
    from fastwam.fullft.zoom import ZOOM_REF, cur_key
    m, _ = _model()
    with torch.no_grad():
        m.hist_gate.fill_(0.5)
    g = torch.Generator().manual_seed(5)
    encoded = {i: (torch.randn(48, 1, 8, 6, generator=g), torch.randn(14, generator=g)) for i in range(60)}
    encoded[ZOOM_REF] = (torch.randn(48, 1, 8, 6, generator=g), encoded[0][1])
    text = torch.randn(1, 5, TEXT, generator=g)
    rule = HistoryRule("ar", zoom=True, zoom_ref_box=(0.1, 0.1, 0.5, 0.5), zoom_cur_box=(0.2, 0.4, 0.9, 1.0))
    cache = FrameCache()
    for current in (0, 40, 48):
        encoded[cur_key(current)] = (torch.randn(48, 1, 8, 6, generator=g), encoded[current][1])
        noise = torch.randn(1, 32, 14, generator=g)
        out = decide_encoded(m, rule, cache, encoded, current, text, noise, steps=3)
        ids, pos = select(HistoryRule("ar"), current)
        zr, zc = zoom_positions(rule, current, len(ids))
        keys, pos = ids + [ZOOM_REF, cur_key(current)], pos + [zr, zc]
        batch = {"latent": encoded[current][0][None], "text": text, "proprio": encoded[current][1][None],
                 "anchor": torch.tensor([current]),
                 "hist_latent": torch.stack([encoded[i][0] for i in keys])[None],
                 "hist_proprio": torch.stack([encoded[i][1] for i in keys])[None],
                 "hist_valid": torch.ones(1, len(keys), dtype=torch.bool), "hist_pos": torch.tensor([pos])}
        ref = m.sample(batch, noise, steps=3)
        assert out["ids"] == keys and torch.allclose(out["normalised"], ref[0], atol=1e-6)
        assert ZOOM_REF in cache.kv and cur_key(current) not in cache.kv        # the current crop leaves with the decision


def test_object_record_helpers(monkeypatch):
    """scripts/memory_v2/sim/sim_adapter.py object record (A3): passive reads on duck-typed entities; off by default."""
    import importlib.util
    import json as _json
    from pathlib import Path
    from types import SimpleNamespace
    path = Path(__file__).resolve().parents[4] / "scripts/memory_v2/sim/sim_adapter.py"
    monkeypatch.delenv("MWAM_OBJECT_LOG", raising=False)
    spec = importlib.util.spec_from_file_location("mwam_sim_adapter_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.OBJECT_LOG is False                                   # off unless MWAM_OBJECT_LOG=1

    class Ent:
        def __init__(self, name, p):
            self._n, self.p = name, p

        def get_name(self):
            return self._n

        def get_pose(self):
            return SimpleNamespace(p=self.p)

    class Broken:
        def get_pose(self):
            raise RuntimeError("no pose")

    class Wrapped:                                                   # RMBench's Actor keeps the entity in .actor
        def __init__(self, ent):
            self.actor = ent

    # the attribute layout of RMBench envs/observe_and_pickup.py (object list, target_object_idx, target_object, ...)
    a, b, c = Ent("010_mouse", [0.1, -0.2, 0.741]), Ent("011_stapler", [-0.2, -0.15, 0.741]), Ent("008_shelf", [0, 0.15, 0.781])
    ref = Ent("011_stapler", [0.0, 0.15, 0.88])
    scene = SimpleNamespace(get_all_actors=lambda: [a, b, c, ref])
    env = SimpleNamespace(scene=scene, object=[a, Wrapped(b)], target_object_idx=1, target_object=ref, shelf=c,
                          object_modelnames=["010_mouse", "011_stapler"], object_ids=[0, 3], fail_flag=False,
                          get_obs_cnt=7, robot=Ent("robot", [9, 9, 9]), broken=Broken(), big=list(range(100)))
    assert mod.task_actors(env) == {"object[0]": [0.1, -0.2, 0.741], "object[1]": [-0.2, -0.15, 0.741],
                                    "shelf": [0.0, 0.15, 0.781], "target_object": [0.0, 0.15, 0.88]}   # robot skipped
    assert mod.task_flags(env) == {"fail_flag": False, "get_obs_cnt": 7, "target_object_idx": 1}
    meta = mod.object_meta(env)
    assert meta["scalars"] == {"fail_flag": False, "get_obs_cnt": 7, "target_object_idx": 1}
    assert meta["lists"] == {"object_modelnames": ["010_mouse", "011_stapler"], "object_ids": [0, 3]}
    assert meta["actors"]["target_object"] == {"entity": "011_stapler", "p": [0.0, 0.15, 0.88]}
    assert [x["entity"] for x in meta["actors"]["object"]] == ["010_mouse", "011_stapler"]
    assert [x["name"] for x in meta["scene_entities"]] == ["010_mouse", "011_stapler", "008_shelf", "011_stapler"]
    _json.dumps(meta)                                                # serialisable
    assert mod.task_actors(SimpleNamespace()) == {} and mod.scene_entities(SimpleNamespace(scene=None)) == []
    monkeypatch.setenv("MWAM_OBJECT_LOG", "1")
    spec.loader.exec_module(mod)
    assert mod.OBJECT_LOG is True

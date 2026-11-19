"""11-19 plan v14 E14: the provisional write (EventRule.provisional). numpy only (runs without torch)."""
import numpy as np

from fastwam.fullft.events import EventDetector, EventRule, detect


def press_track(n=420, presses=6, depth=0.03, start=30, period=30, dips=()):
    """Right arm presses `presses` times (down `depth` over 10 frames, up over 10, then still); left arm still; a small
    x drift so the debounce path grows. dips: (frame, metres) small up-wiggles during a descent (not presses)."""
    z = np.full(n, 0.10)
    t = start
    for _ in range(presses):
        z[t:t + 10] = np.linspace(0.10, 0.10 - depth, 10)
        z[t + 10:t + 20] = np.linspace(0.10 - depth, 0.10, 10)
        t += period
    for f, h in dips:
        z[f:f + 2] += h
    pos = np.zeros((n, 2, 3))
    pos[:, 1, 2], pos[:, 0, 2] = z, 0.2
    pos[:, 1, 0] = np.linspace(0, 0.01, n)
    return np.zeros((n, 2)), pos


def first_rise(pos, e, eps):
    z = pos[:, e["arm"], 2]
    sign = 1.0 if e["kind"] == "bottom" else -1.0
    return next(t for t in range(e["frame"] + 1, len(z)) if sign * (z[t] - z[e["frame"]]) >= eps)


def test_off_is_unchanged_and_on_keeps_the_same_events():
    grip, pos = press_track()
    std = detect(grip, pos, EventRule(delta=0.012, min_path=0.015))
    off = detect(grip, pos, EventRule(delta=0.012, min_path=0.015, provisional=0.0))
    on = detect(grip, pos, EventRule(delta=0.012, min_path=0.015, provisional=0.002))
    assert [(e["frame"], e["arm"], e["kind"], e["confirmed"]) for e in std] == \
           [(e["frame"], e["arm"], e["kind"], e["confirmed"]) for e in off]
    assert [(e["frame"], e["arm"], e["kind"]) for e in std] == [(e["frame"], e["arm"], e["kind"]) for e in on]
    assert all("visible" not in e for e in on)
    for s, p in zip(std, on):
        assert p["confirmed"] <= s["confirmed"]
        if p["kind"] in ("bottom", "top"):
            assert p["confirmed"] == min(first_rise(pos, p, 0.002), s["confirmed"])
    assert any(p["confirmed"] < s["confirmed"] for s, p in zip(std, on))


def test_streaming_shows_every_event_from_its_visible_frame():
    """Online (emitted + pending) at frame t contains every final event whose visible frame <= t, at its frame."""
    grip, pos = press_track(dips=((37, 0.006),))           # a 6 mm wiggle inside the first descent: shown, then dropped
    rule = EventRule(delta=0.012, min_path=0.015, provisional=0.002)
    final = detect(grip, pos, rule)
    d, emitted, retracted_seen = EventDetector(rule), [], False
    for t in range(len(grip)):
        for e in d.step(t, grip[t], pos[t]):
            e["confirmed"] = e.pop("visible", t)
            emitted.append(e)
        shown = {(e["frame"], e["arm"], e["kind"]) for e in emitted + d.pending() if e["confirmed"] <= t}
        want = {(e["frame"], e["arm"], e["kind"]) for e in final if e["confirmed"] <= t}
        assert want <= shown, (t, want - shown)
        retracted_seen |= bool(shown - want - {(e["frame"], e["arm"], e["kind"]) for e in final})
    assert [(e["frame"], e["kind"], e["confirmed"]) for e in emitted] == [(e["frame"], e["kind"], e["confirmed"]) for e in final]
    assert retracted_seen                                   # the wiggle was shown provisionally and later withdrawn


def test_pause_shifts_frames_only():
    grip, pos = press_track()
    rule = EventRule(delta=0.012, min_path=0.015, provisional=0.002)
    base = detect(grip, pos, rule)
    k, at = 40, 100                                         # hold still for k frames at frame `at`
    pos2 = np.concatenate([pos[:at], np.repeat(pos[at:at + 1], k, 0), pos[at:]])
    grip2 = np.concatenate([grip[:at], np.repeat(grip[at:at + 1], k, 0), grip[at:]])
    shifted = detect(grip2, pos2, rule)
    move = lambda f: f if f < at else f + k                  # noqa: E731
    assert [(e["kind"], e["arm"]) for e in base] == [(e["kind"], e["arm"]) for e in shifted]
    for a, b in zip(base, shifted):
        assert b["frame"] in (move(a["frame"]), a["frame"])
        assert b["confirmed"] in (move(a["confirmed"]), a["confirmed"])

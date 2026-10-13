"""One-factor query-scale intervention and preregistered diagnostic gates."""
from __future__ import annotations

from contextlib import contextmanager
import math
import statistics

MODES = ("original", "query_scale_64")
QUERY_SCALE = 64.0
ARMS = (0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12)


@contextmanager
def query_scale(memory, mode):
    """Scale only the learned slots entering reader block zero; no new parameters.

    Public conditions, history projection, later blocks, gates and sampler are
    unchanged. Install before diagnostic observers; checkpoint recomputation
    uses the same hook. The original mode installs nothing.
    """
    if mode not in MODES:
        raise ValueError(f"Unknown query intervention: {mode}")
    if mode == "original":
        yield
        return
    if getattr(memory, "_query_scale_repair_active", False):
        raise ValueError("Query intervention must not be installed twice")
    memory._query_scale_repair_active = True
    def change(_module, args):
        if len(args) != 3 or args[0].shape[1:] != memory.queries.shape:
            raise ValueError("Reader input contract changed")
        # Gradients intentionally flow through the scaled slot parameters.
        value = args[0] + (QUERY_SCALE - 1.0) * memory.queries[None]
        return (value, *args[1:])
    handle = memory.reader[0].register_forward_pre_hook(change)
    try:
        yield
    finally:
        handle.remove()
        del memory._query_scale_repair_active


def gradient_summary(values):
    layers = {}
    for layer in (4, 9, 14, 19, 24, 29):
        prefix = f"injectors.{layer}.attention."
        q, k, v = (values.get(prefix + part + ".weight", 0.0) for part in ("q", "k", "v"))
        if v <= 0 or not all(math.isfinite(x) for x in (q, k, v)):
            raise ValueError(f"Missing/non-finite injector gradient at layer {layer}")
        layers[str(layer)] = {"q_norm": q, "k_norm": k, "v_norm": v,
                              "q_over_v": q / max(v, 1e-30), "k_over_v": k / max(v, 1e-30)}
    return {"layers": layers, "median_q_over_v": statistics.median(x["q_over_v"] for x in layers.values()),
            "queries_norm": values.get("queries", 0.0)}


def mechanism_gate(rows, thresholds):
    """Mechanism improvement only, never a task-success or causality claim."""
    pairs = {}
    for row in rows:
        if row["weight"] == "step_002000":
            key = row["case"]
            if row["mode"] in pairs.setdefault(key, {}):
                raise ValueError("Duplicate zero-update case")
            pairs[key][row["mode"]] = row
    if len(pairs) != 4 or any(set(x) != set(MODES) for x in pairs.values()):
        raise ValueError("Expected four paired step-2000 mechanism cases")
    slot_gain, gradient_gain = [], []
    for pair in pairs.values():
        a, b = pair[MODES[0]], pair[MODES[1]]
        slot_gain.append(b["readout"]["centered_norm_ratio"] / max(a["readout"]["centered_norm_ratio"], 1e-30))
        gradient_gain.append(b["gradients"]["median_q_over_v"] / max(a["gradients"]["median_q_over_v"], 1e-30))
    if not all(math.isfinite(x) for x in slot_gain + gradient_gain):
        raise ValueError("Non-finite mechanism comparison")
    result = {"median_slot_diversity_gain": statistics.median(slot_gain),
              "median_q_over_v_gain": statistics.median(gradient_gain), "thresholds": thresholds,
              "scope": "eligibility for bounded fitting; not proof of root cause"}
    result["passed"] = (result["median_slot_diversity_gain"] >= thresholds["slot_gain"]
                        and result["median_q_over_v_gain"] >= thresholds["gradient_gain"])
    return result


def fit_gate(rows, thresholds):
    """Fixed held-out windows/noises, paired post-fit arms; no seed selection."""
    pairs = {}
    baseline = {}
    for row in rows:
        if row["phase"] == "before" and row["group"] == "heldout" and row["mode"] == MODES[0]:
            key = (row["case"], row["noise"])
            if key in baseline: raise ValueError("Duplicate pre-fit baseline")
            baseline[key] = row
        if row["phase"] == "after" and row["group"] == "heldout":
            key = (row["case"], row["noise"])
            if row["mode"] in pairs.setdefault(key, {}):
                raise ValueError("Duplicate held-out measurement")
            pairs[key][row["mode"]] = row
    if len(pairs) != 12 or set(baseline) != set(pairs) or any(set(x) != set(MODES) for x in pairs.values()):
        raise ValueError("Expected four held-out windows x three noises x two arms")
    tasks = {}
    for task in ("put_back_block", "swap_blocks"):
        selected = [p for p in pairs.values() if p[MODES[0]]["task"] == task]
        if len(selected) != 6:
            raise ValueError("Each task requires two held-out windows x three noises")
        values = {}
        for mode in MODES:
            measurements = [p[mode] for p in selected]
            values[mode] = {"arm_mean": statistics.mean(x["arm_rmse_first16_rad"] for x in measurements),
                           "arm_worst": max(x["arm_rmse_first16_rad"] for x in measurements),
                           "gripper_mean": statistics.mean(x["gripper_mae_first16"] for x in measurements),
                           "gripper_worst": max(x["gripper_mae_first16"] for x in measurements)}
        before = [x for x in baseline.values() if x["task"] == task]
        values["original_before"] = {"arm_mean": statistics.mean(x["arm_rmse_first16_rad"] for x in before),
                                     "arm_worst": max(x["arm_rmse_first16_rad"] for x in before),
                                     "gripper_mean": statistics.mean(x["gripper_mae_first16"] for x in before),
                                     "gripper_worst": max(x["gripper_mae_first16"] for x in before)}
        a, b = values[MODES[0]], values[MODES[1]]
        improve = (b["arm_mean"] < a["arm_mean"] - thresholds["arm_margin_rad"]
                   or b["gripper_mean"] < a["gripper_mean"] - thresholds["gripper_margin"])
        stable = all(b[field] <= a[field] * thresholds["max_regression_factor"] + margin
                     for field, margin in (("arm_mean", thresholds["arm_margin_rad"]),
                                           ("arm_worst", thresholds["arm_margin_rad"]),
                                           ("gripper_mean", thresholds["gripper_margin"]),
                                           ("gripper_worst", thresholds["gripper_margin"])))
        initial = values["original_before"]
        improves_initial = (b["arm_mean"] < initial["arm_mean"] - thresholds["arm_margin_rad"]
                            or b["gripper_mean"] < initial["gripper_mean"] - thresholds["gripper_margin"])
        preserves_initial = all(b[field] <= initial[field] * thresholds["max_regression_factor"] + margin
                                for field, margin in (("arm_mean", thresholds["arm_margin_rad"]),
                                                      ("arm_worst", thresholds["arm_margin_rad"]),
                                                      ("gripper_mean", thresholds["gripper_margin"]),
                                                      ("gripper_worst", thresholds["gripper_margin"])))
        tasks[task] = {"metrics": values, "improved": improve, "within_regression_limit": stable,
                       "improved_vs_original_before": improves_initial, "preserved_original_before": preserves_initial,
                       "passed": improve and stable and improves_initial and preserves_initial}
    if any(not math.isfinite(x[field]) for t in tasks.values() for x in t["metrics"].values() for field in x):
        raise ValueError("Non-finite held-out comparison")
    return {"eligible_for_physical": all(x["passed"] for x in tasks.values()), "tasks": tasks,
            "thresholds": thresholds, "scope": "bounded diagnostic gate; no benchmark accuracy or unique-root-cause claim"}

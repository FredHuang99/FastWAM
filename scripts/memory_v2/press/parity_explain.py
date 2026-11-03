"""PB-parity2: is the PB-parity mismatch numerical noise from another GPU type, or a builder bug?

PB-parity (build_dense.py parity) FAILED on one check only: latents and text were not within the recipe's
VAE tolerance (allclose atol 2e-3). That tolerance is the recipe's *same-run* check (causal VAE: first frame
encoded alone vs inside the clip, same GPU, same process). The reference it was compared with,
outputs/s1_dense_joint_h100_v1, was encoded on an H100; the rebuild ran on an A100. bf16 kernels differ
between GPU types, so bit-level agreement was never expected there. The PB-parity verdict stays FAIL (it is
not re-judged); this task measures the difference against a noise floor and against the size of a real bug,
with criteria written down before it runs:

    C1  proprio / actions / video_valid / text_valid identical to the H100 cache            (indexing, normalizer)
    C2  latent, video_latent, text: relative L2 vs the H100 cache <= 2e-2                    (noise level)
    C3  latent, video_latent: worst single frame relative L2 <= 5e-2                          (no bad frame)
    C4  latent, video_latent: relative L2 <= 0.25 x the off-by-one-frame control;
        text: <= 0.25 x the control "text of a put_back episode with another instruction"  (smaller than a bug)
    C5  history features vs features_dense_v1: relative L2 <= 5e-2, and the other PB-parity checks
        (memory_v2 bind + episode store, base dataset .at) passed                           (from PARITY.json)

Reported, not judged:
    D1  determinism on this GPU type: the same episode encoded again (build_dense.encode, unchanged) into a
        second scratch folder, compared with the PB-parity rebuild -> the noise floor of our own builder
    D2  encoder_software drift between the H100 receipt and this host; GPU names

    PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/press/parity_explain.py
Writes outputs/memory_v2/press/parity_put_v1/PARITY_EXPLAIN.{json,md}; exit 0 only if C1-C5 all pass.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_dense as bd   # noqa: E402  (same folder; its functions are called, not copied)

TOL_REL = 2e-2
TOL_FRAME = 5e-2
TOL_RATIO = 0.25
TOL_FEATURES = 5e-2


def log(msg):
    print(f"[parity2] {time.strftime('%F %T')} {msg}", flush=True)


def rel(x, y):
    import torch
    x, y = x.double(), y.double()
    return float((x - y).norm() / y.norm().clamp_min(1e-12))


def stats(x, y):
    import torch
    d = (x.float() - y.float()).abs().flatten()
    s = d[:: -(-d.numel() // (1 << 24))]             # quantile on a strided sample (torch limit 2^24)
    per = [rel(x[i], y[i]) for i in range(x.shape[0])] if x.dim() > 2 else None
    out = {"relative_l2": rel(x, y), "max_abs": float(d.max()), "mean_abs": float(d.mean()),
           "p999_abs": float(torch.quantile(s, 0.999)), "share_above_2e-3": float((d > 2e-3).float().mean()),
           "reference_rms": float(y.double().pow(2).mean().sqrt())}
    if per is not None:
        worst = max(range(len(per)), key=per.__getitem__)
        out.update(worst_frame=worst, worst_frame_relative_l2=per[worst],
                   median_frame_relative_l2=sorted(per)[len(per) // 2])
    return out


def main():
    import torch
    common, data_path = bd.setup()
    sys.path.insert(0, str(bd.M / "src"))
    from fastwam.memory_v2 import dense
    out1 = bd.PRESS / "parity_put_v1"
    parity = common.read(out1 / "PARITY.json")
    ep = bd.PARITY_EPISODE
    base_records = common.read(bd.BASE / "RECORDS.json")
    rec = next(r for r in base_records if r["episode_id"] == ep)
    load = lambda root, e: torch.load(data_path.paths(root, e) / "encodings.pt", map_location="cpu", weights_only=True)
    ours, h100 = load(out1, ep), load(bd.BASE, ep)
    res = {"episode": ep, "reference": str(bd.BASE), "rebuild": str(out1),
           "gpu_here": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
           "tolerances": {"relative_l2": TOL_REL, "worst_frame": TOL_FRAME, "ratio_to_bug_control": TOL_RATIO,
                          "features": TOL_FEATURES}, "checks": {}, "noise": {}, "controls": {}}

    # C1 exact fields
    exact = {k: bool(torch.equal(ours[k], h100[k])) for k in ("proprio", "actions", "video_valid", "text_valid")}
    res["exact_fields"] = exact
    res["checks"]["C1_exact_fields"] = all(exact.values())

    # C2 / C3 noise vs the H100 cache
    for k in ("latent", "video_latent", "text"):
        res["noise"][k] = stats(ours[k], h100[k])
    res["checks"]["C2_relative_l2"] = all(res["noise"][k]["relative_l2"] <= TOL_REL for k in res["noise"])
    res["checks"]["C3_worst_frame"] = all(res["noise"][k]["worst_frame_relative_l2"] <= TOL_FRAME
                                          for k in ("latent", "video_latent"))

    # C4 bug-size controls
    for k in ("latent", "video_latent"):
        res["controls"][f"{k}_off_by_one_frame"] = rel(ours[k][1:], h100[k][:-1])
    other = next((r for r in base_records if r["episode_id"].startswith("put_back_block/")
                  and r["instruction"] != rec["instruction"]), None)
    if other is not None:
        t_other = torch.load(data_path.paths(bd.BASE, other["episode_id"]) / "encodings.pt", map_location="cpu",
                             weights_only=True, mmap=True)["text"]
        res["controls"]["text_other_instruction"] = rel(ours["text"], t_other)
        res["controls"]["text_other_episode"] = other["episode_id"]
    ratios = {k: res["noise"][k]["relative_l2"] / max(res["controls"][f"{k}_off_by_one_frame"], 1e-12)
              for k in ("latent", "video_latent")}
    if "text_other_instruction" in res["controls"]:
        ratios["text"] = res["noise"]["text"]["relative_l2"] / max(res["controls"]["text_other_instruction"], 1e-12)
    res["noise_to_bug_ratio"] = ratios
    res["checks"]["C4_smaller_than_a_bug"] = all(v <= TOL_RATIO for v in ratios.values())

    # C5 features + the rest of PB-parity
    f = parity.get("features_vs_features_dense_v1", {})
    others = {k: v for k, v in parity["checks"].items() if k not in ("encodings", "features")}
    res["pb_parity_checks"] = parity["checks"]
    res["features_vs_features_dense_v1"] = f
    res["checks"]["C5_features_and_memory_v2"] = (f.get("max_relative_l2", 1.0) <= TOL_FEATURES
                                                  and all(v is True for v in others.values()))

    # D1 determinism of our builder on this GPU type (build_dense.prepare + encode, unchanged)
    out2 = bd.PRESS / "parity_put_v1_rerun"
    if not (out2 / "PREPARED.json").exists():
        bd.prepare(common, out2, [dict(rec)], "put_back_block", "PB-parity2 determinism rerun of the parity episode")
    log(f"re-encoding {ep} into {out2} (determinism on this GPU type)")
    bd.encode(common, data_path, out2)
    again = load(out2, ep)
    res["determinism_same_gpu_type"] = {k: {"exact": bool(torch.equal(again[k], ours[k])),
                                            "relative_l2": rel(again[k], ours[k])}
                                        for k in ("latent", "video_latent", "text")}

    # D2 software receipt drift + where the reference was encoded
    rec_sw = common.read(bd.BASE / "IDENTITY.json").get("encoder_software", {})
    our_sw = common.read(out1 / "IDENTITY.json").get("encoder_software", {})
    res["encoder_software_drift_h100_vs_here"] = dense._software_drift(rec_sw, our_sw)
    res["reference_folder_says"] = "h100" if "h100" in bd.BASE.name else "unknown"

    res["passed"] = all(res["checks"].values())
    common.write(out1 / "PARITY_EXPLAIN.json", res)
    md = [f"# PB-parity2: {'PASS' if res['passed'] else 'FAIL'}", "",
          f"episode {ep}; reference {bd.BASE.name} (folder name: {res['reference_folder_says']}); GPU here {res['gpu_here']}", "",
          "| check | pass |", "|---|---|"] + [f"| {k} | {v} |" for k, v in res["checks"].items()] + [
          "", "| tensor | rel L2 vs H100 | worst frame rel L2 (frame) | max abs | mean abs | bug control | ratio | rerun here rel L2 (exact) |",
          "|---|---|---|---|---|---|---|---|"]
    for k in ("latent", "video_latent", "text"):
        n = res["noise"][k]
        ctl = res["controls"].get(f"{k}_off_by_one_frame", res["controls"].get("text_other_instruction") if k == "text" else None)
        d = res["determinism_same_gpu_type"][k]
        wf = f"{n['worst_frame_relative_l2']:.2e} ({n['worst_frame']})" if "worst_frame" in n else "-"
        md.append(f"| {k} | {n['relative_l2']:.2e} | {wf} | {n['max_abs']:.3g} | {n['mean_abs']:.2e} | "
                  f"{(f'{ctl:.2e}' if ctl is not None else 'n/a')} | {ratios.get(k, float('nan')):.3f} | "
                  f"{d['relative_l2']:.2e} ({d['exact']}) |")
    md += ["", f"exact fields: {exact}", f"features vs features_dense_v1: {f}",
           f"encoder_software drift (H100 receipt vs here): {json.dumps(res['encoder_software_drift_h100_vs_here'])}"]
    (out1 / "PARITY_EXPLAIN.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    print(f"PARITY2: {'PASS' if res['passed'] else 'FAIL'} ({out1 / 'PARITY_EXPLAIN.json'})")
    sys.exit(0 if res["passed"] else 1)


if __name__ == "__main__":
    main()

"""Card 13a, find-same match probe FS-P1 (plan v20 3.3; 11-24, Opus). Zero training, read-only.
Question: without any training on our data, can a fixed matcher tell which table object is the same as the reference
in frame 0? On the 50 observe_and_pickup demos (the training cache's RECORDS + the delivery's raw frames, frame 0 head
camera), every matcher scores each candidate object against the reference crop; "chosen" = the highest-scoring
candidate; a hit = the candidate the demo actually grasps.

Where things are (frame 0, head camera):
  reference  the box fixed 11-22 (x 0.395-0.675, y 0.06-0.34 of the image; frames sheet: the reference lies in x 0.49-0.58,
             y 0.13-0.27); its central half is the object, the rest shelf
  candidates connected regions of the table box (x 0-1, y 0.42-1) whose colour differs from the table's median colour
             (distance > --fg, area >= --min-area px at the image's own size), inside the projected candidate area
  target     the demo's own data, no annotation: the end-effector position of the arm that closes first (gripper
             0.65 -> 0.35), projected through the head camera of the robot config (zoom_tools.head_camera; the same
             pinhole model as the zoom boxes); the target = the candidate nearest to that point. Sanity checks printed:
             the projected reference centre (0, 0.15, 0.88) against the frames sheet; the end-effector height at the
             close (world frame expected: ~0.74-0.85); the pixel distance from the projected point to the target
             candidate (large distances = an unreliable target, said so)
Matchers (both run, fixed before any result):
  colour     joint RGB histogram (8 x 8 x 8) of the reference's object pixels (central half of its box, pixels far from the
             box border's median colour) against each candidate's pixels; histogram intersection
  dinov2     a frozen public self-supervised image encoder (default facebook/dinov2-base, Apache-2.0, no login; loaded
             with transformers' native Dinov2Model from safetensors, trust_remote_code off; the user approved 11-24):
             (a) crop: cosine of the CLS embeddings of the reference box and of each candidate's box (margin 30 %,
             resized to 224); (b) map: patch features of the table box (upsampled x3) against the reference's central
             patches (max cosine), the candidate's score = the map's max inside its box; the map is the card 7 picture
Gate (plan v20 card 13a, registered before the probe): best matcher >= 35/50 -> card 7 with it; < 25/50 -> this path
stops; in between -> look at which objects it confuses (supplement 10). Ties / no candidates count as misses.
Outputs: outputs/fullft/match_probe/MATCH_PROBE.json (per demo: candidates, target, scores, picks), contact sheets
sheet_*.png (frame 0 with the candidates, the projected point, the target and each matcher's pick), and the encoder's
name / revision / file sha256.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/match_probe.py [--device cuda:0] [--model facebook/dinov2-base]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
R = Path("/workspace/FastWAM-memory2")
ROOT = R / "outputs/memory_v2/press/dense_observe_and_pickup_v1"
RMBENCH = Path("/workspace/FastWAM/resources/RMBench")
OUT = R / "outputs/fullft/match_probe"
REF_BOX = (0.395, 0.06, 0.675, 0.34)
CUR_BOX = (0.0, 0.42, 1.0, 1.0)
CAND_3D = ((-0.40, 0.40), (-0.30, -0.05), (0.741, 0.80))     # env: x in [-0.35, 0.35], y in [-0.25, -0.10], with margin
REF_CENTRE = (0.0, 0.15, 0.88)


def first_close(grip):
    opened = [False, False]
    for t in range(len(grip)):
        for a in (0, 1):
            v = float(grip[t, a])
            if v > 0.65:
                opened[a] = True
            elif opened[a] and v < 0.35:
                return t, a
    return None, None


def project(point, cam):
    pos, fwd, left, fovy, w, h = (np.asarray(cam[0], float), np.asarray(cam[1], float), np.asarray(cam[2], float),
                                  cam[3], cam[4], cam[5])
    fwd, left = fwd / np.linalg.norm(fwd), left / np.linalg.norm(left)
    up = np.cross(fwd, left)
    f = (h / 2.0) / math.tan(math.radians(fovy) / 2.0)
    d = np.asarray(point, float) - pos
    depth = float(fwd @ d)
    if depth <= 0:
        return None
    return (w / 2.0 - f * float(left @ d) / depth) / w, (h / 2.0 - f * float(up @ d) / depth) / h


def components(mask):
    try:
        from scipy import ndimage
        lab, n = ndimage.label(mask)
        return lab, n
    except ImportError:
        lab = np.zeros(mask.shape, int)
        n = 0
        for y0, x0 in zip(*np.nonzero(mask)):
            if lab[y0, x0]:
                continue
            n += 1
            stack = [(y0, x0)]
            lab[y0, x0] = n
            while stack:
                y, x = stack.pop()
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < mask.shape[0] and 0 <= xx < mask.shape[1] and mask[yy, xx] and not lab[yy, xx]:
                        lab[yy, xx] = n
                        stack.append((yy, xx))
        return lab, n


def merge_close(cands, px):
    """v2: components whose boxes lie within `px` pixels of each other are one object (a split object / its shadow)."""
    out = [dict(c) for c in cands]
    changed = True
    while changed and px > 0:
        changed = False
        for i in range(len(out)):
            for j in range(i + 1, len(out)):
                a, b = out[i]["bbox"], out[j]["bbox"]
                gap = max(a[0] - b[2], b[0] - a[2], a[1] - b[3], b[1] - a[3], 0)
                if gap <= px:
                    ys = np.concatenate([out[i]["pixels"][0], out[j]["pixels"][0]])
                    xs = np.concatenate([out[i]["pixels"][1], out[j]["pixels"][1]])
                    h_, w_ = out[i]["_hw"]
                    out[i] = {"bbox": [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)],
                              "centre": [round(float(xs.mean()) / w_, 4), round(float(ys.mean()) / h_, 4)],
                              "area": int(len(ys)), "pixels": (ys, xs), "_hw": (h_, w_)}
                    del out[j]
                    changed = True
                    break
            if changed:
                break
    return out


def candidates(img, fg, min_area, area_box):
    h, w = img.shape[:2]
    x0, y0, x1, y1 = int(CUR_BOX[0] * w), int(CUR_BOX[1] * h), int(CUR_BOX[2] * w), int(CUR_BOX[3] * h)
    crop = img[y0:y1, x0:x1].astype(np.float32)
    table = np.median(crop.reshape(-1, 3), axis=0)
    mask = np.linalg.norm(crop - table, axis=2) > fg
    lab, n = components(mask)
    out = []
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        if len(ys) < min_area:
            continue
        cx, cy = (xs.mean() + x0) / w, (ys.mean() + y0) / h
        if area_box and not (area_box[0] <= cx <= area_box[2] and area_box[1] <= cy <= area_box[3]):
            continue
        out.append({"bbox": [int(xs.min() + x0), int(ys.min() + y0), int(xs.max() + x0 + 1), int(ys.max() + y0 + 1)],
                    "centre": [round(float(cx), 4), round(float(cy), 4)], "area": int(len(ys)),
                    "pixels": (ys + y0, xs + x0), "_hw": (h, w)})
    return out, table


def hist(pixels):
    q = (np.clip(pixels, 0, 255) // 32).astype(int)
    h = np.bincount(q[:, 0] * 64 + q[:, 1] * 8 + q[:, 2], minlength=512).astype(np.float64)
    return h / max(h.sum(), 1.0)


def ref_object_pixels(img, fg):
    h, w = img.shape[:2]
    x0, y0, x1, y1 = int(REF_BOX[0] * w), int(REF_BOX[1] * h), int(REF_BOX[2] * w), int(REF_BOX[3] * h)
    crop = img[y0:y1, x0:x1].astype(np.float32)
    border = np.concatenate([crop[0], crop[-1], crop[:, 0], crop[:, -1]])
    bg = np.median(border, axis=0)
    ch, cw = crop.shape[:2]
    centre = crop[ch // 4: 3 * ch // 4, cw // 4: 3 * cw // 4]
    m = np.linalg.norm(centre - bg, axis=2) > fg
    px = centre[m] if m.sum() >= 10 else centre.reshape(-1, 3)
    return px, (x0, y0, x1, y1)


def crop_box(img, bbox, margin=0.3):
    h, w = img.shape[:2]
    x0, y0, x1, y1 = bbox
    mx, my = (x1 - x0) * margin, (y1 - y0) * margin
    return img[max(0, int(y0 - my)): min(h, int(y1 + my)), max(0, int(x0 - mx)): min(w, int(x1 + mx))]


def _license(info):
    for attr in ("card_data", "cardData"):
        try:
            v = getattr(info, attr, None)
            if v is not None:
                return v.get("license") if hasattr(v, "get") else getattr(v, "license", None)
        except Exception:                                                    # noqa: BLE001
            pass
    return None


class Dino:
    def __init__(self, name, device):
        import torch
        from huggingface_hub import HfApi, hf_hub_download
        from transformers import Dinov2Model
        self.torch, self.device = torch, device
        info = HfApi().model_info(name)
        self.revision = info.sha
        path = hf_hub_download(name, "model.safetensors", revision=self.revision)
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for block in iter(lambda: f.read(1 << 24), b""):
                h.update(block)
        self.meta = {"model": name, "revision": self.revision, "file": "model.safetensors",
                     "sha256": h.hexdigest(), "bytes": Path(path).stat().st_size,
                     "license": _license(info),
                     "loader": "transformers.Dinov2Model.from_pretrained(use_safetensors=True, trust_remote_code=False)"}
        self.model = Dinov2Model.from_pretrained(name, revision=self.revision, use_safetensors=True,
                                                 trust_remote_code=False).to(device).eval()
        self.mean = torch.tensor([0.485, 0.456, 0.406], device=device).view(1, 3, 1, 1)
        self.std = torch.tensor([0.229, 0.224, 0.225], device=device).view(1, 3, 1, 1)

    def _prep(self, img, size):
        t = self.torch.from_numpy(np.ascontiguousarray(img)).float().permute(2, 0, 1)[None].to(self.device) / 255.0
        t = self.torch.nn.functional.interpolate(t, size=size, mode="bilinear", align_corners=False)
        return (t - self.mean) / self.std

    def feats(self, img, size):
        with self.torch.no_grad():
            out = self.model(pixel_values=self._prep(img, size)).last_hidden_state[0]
        cls, patches = out[0], out[1:]
        gh, gw = size[0] // 14, size[1] // 14
        return cls, patches.reshape(gh, gw, -1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--rmbench", default=str(RMBENCH))
    ap.add_argument("--device", default="cuda:0")
    ap.add_argument("--model", default="facebook/dinov2-base")
    ap.add_argument("--fg", type=float, default=40.0)
    ap.add_argument("--min-area", type=int, default=12)
    ap.add_argument("--sheets", type=int, default=12)
    # v2 (11-24 19:00, fixed from run 1's own sanity checks, before any v2 result): the end-effector height at the close
    # was 0.90-0.92 m while the candidates stand on the table at 0.741 m, and 49 / 50 projected points lay > 10 px
    # (median 39 px) from every candidate: the logged end-effector is the wrist link ~16 cm above the fingers. The
    # gripper's position (plan v20 card 13a: "夹爪的位置") is taken as the wrist's x, y at the object height --gt-z; and,
    # as the plan's fallback, the candidate whose box changes most between frame 0 and the demo's last frame (the
    # object lifted away) is the second target, their agreement reported. Run 1 found 4-9 components per demo for five
    # objects: components closer than --merge-px are merged and the --keep largest kept (the env places five).
    ap.add_argument("--v1", action="store_true", help="run 1's settings (wrist point, no merging)")
    ap.add_argument("--gt-z", type=float, default=0.76)
    ap.add_argument("--merge-px", type=int, default=6)
    ap.add_argument("--keep", type=int, default=5)
    ap.add_argument("--change", type=float, default=30.0, help="per-pixel |difference| counted as changed")
    args = ap.parse_args()
    global OUT
    if not args.v1:
        OUT = OUT.parent / "match_probe_v2"
    OUT.mkdir(parents=True, exist_ok=True)
    from zoom_tools import delivery, head_camera
    import events_stats as es
    common, data_path = delivery()
    cfg = common.read(Path(args.root) / "IDENTITY.json")["config"]
    records = common.read(Path(args.root) / "RECORDS.json")
    cam = head_camera(Path(args.rmbench))
    rc = project(REF_CENTRE, cam)
    print(f"[match] head camera {cam[7]} fovy {cam[3]} {cam[4]}x{cam[5]}; projected reference centre "
          f"({rc[0]:.3f}, {rc[1]:.3f}) (frames sheet: x 0.49-0.58, y 0.13-0.27)", flush=True)
    corners = [project((x, y, z), cam) for x in CAND_3D[0] for y in CAND_3D[1] for z in CAND_3D[2]]
    area_box = [min(c[0] for c in corners), min(c[1] for c in corners), max(c[0] for c in corners), max(c[1] for c in corners)]
    print(f"[match] projected candidate area x {area_box[0]:.3f}-{area_box[2]:.3f}, y {area_box[1]:.3f}-{area_box[3]:.3f}")
    demos = {f"observe_and_pickup/{p.stem}": p for p in es.demo_files("observe_and_pickup")}
    dino = None
    try:
        dino = Dino(args.model, args.device)
        print(f"[match] encoder {json.dumps(dino.meta)}", flush=True)
    except Exception as e:                                                   # noqa: BLE001
        print(f"[match] dinov2 NOT available ({type(e).__name__}: {str(e)[:300]}): colour matcher only", flush=True)
    rows, tiles = [], []
    for rec in records:
        eid = rec["episode_id"]
        path = demos.get(eid) or next((p for k, p in demos.items() if k.endswith(eid.split("/")[-1])), None)
        raw = data_path.Raw(cfg, rec)
        try:
            img = np.asarray(raw.images(0)[0]).astype(np.uint8)
            last = np.asarray(raw.images(int(rec["length"]) - 1)[0]).astype(np.uint8)
        finally:
            raw.close()
        h, w = img.shape[:2]
        row = {"episode": eid, "size": [w, h]}
        if path is None:
            row["why"] = "no demo file"
            rows.append(row)
            continue
        grip, pos = es.read_demo(path)
        g, arm = first_close(np.asarray(grip))
        if g is None:
            row["why"] = "no gripper close"
            rows.append(row)
            continue
        ee = np.asarray(pos)[g, arm]
        pt = project(ee if args.v1 else (ee[0], ee[1], args.gt_z), cam)
        cands, table = candidates(img, args.fg, args.min_area, area_box)
        if not args.v1:
            cands = merge_close(cands, args.merge_px)
            cands = sorted(cands, key=lambda c: -c["area"])[: args.keep]
            cands.sort(key=lambda c: c["centre"][0])
        row.update(close_frame=int(g), arm="left" if arm == 0 else "right", ee=[round(float(v), 4) for v in ee],
                   point=[round(pt[0], 4), round(pt[1], 4)] if pt else None, n_candidates=len(cands),
                   table_colour=[round(float(v), 1) for v in table])
        if not cands or pt is None:
            row["why"] = "no candidates" if not cands else "point not projectable"
            rows.append(row)
            continue
        dist = [math.hypot((c["centre"][0] - pt[0]) * w, (c["centre"][1] - pt[1]) * h) for c in cands]
        tgt = int(np.argmin(dist))
        row.update(target=tgt, target_dist_px=round(dist[tgt], 1),
                   second_dist_px=round(sorted(dist)[1], 1) if len(dist) > 1 else None)
        diff = np.abs(img.astype(np.int16) - last.astype(np.int16)).max(axis=-1) > args.change
        changed = [float(diff[c["bbox"][1]:c["bbox"][3], c["bbox"][0]:c["bbox"][2]].mean()) for c in cands]
        row.update(changed=[round(v, 3) for v in changed], target_change=int(np.argmax(changed)),
                   targets_agree=int(np.argmax(changed)) == tgt)
        ref_px, rbox = ref_object_pixels(img, args.fg)
        href = hist(ref_px)
        sc = {"colour": [float(np.minimum(href, hist(img[c["pixels"]].astype(np.float32))).sum()) for c in cands]}
        if dino is not None:
            rcrop = img[rbox[1]:rbox[3], rbox[0]:rbox[2]]
            rcls, rpatch = dino.feats(rcrop, (224, 224))
            gh, gw = rpatch.shape[:2]
            rcen = rpatch[gh // 4: 3 * gh // 4, gw // 4: 3 * gw // 4].reshape(-1, rpatch.shape[-1])
            rcen = dino.torch.nn.functional.normalize(rcen, dim=-1)
            crop_scores = []
            for c in cands:
                ccls, _ = dino.feats(crop_box(img, c["bbox"]), (224, 224))
                crop_scores.append(float(dino.torch.nn.functional.cosine_similarity(rcls, ccls, dim=0)))
            sc["dinov2_crop"] = crop_scores
            x0, y0, x1, y1 = int(CUR_BOX[0] * w), int(CUR_BOX[1] * h), int(CUR_BOX[2] * w), int(CUR_BOX[3] * h)
            tb = img[y0:y1, x0:x1]
            size = ((tb.shape[0] * 3) // 14 * 14, (tb.shape[1] * 3) // 14 * 14)
            _, tp = dino.feats(tb, size)
            tpn = dino.torch.nn.functional.normalize(tp, dim=-1)
            sim = (tpn.reshape(-1, tpn.shape[-1]) @ rcen.T).max(dim=1).values.reshape(tp.shape[0], tp.shape[1])
            sim = sim.float().cpu().numpy()
            sy, sx = sim.shape[0] / tb.shape[0], sim.shape[1] / tb.shape[1]
            map_scores = []
            for c in cands:
                bx0, by0, bx1, by1 = c["bbox"]
                a0, a1 = int((by0 - y0) * sy), max(int((by0 - y0) * sy) + 1, int(math.ceil((by1 - y0) * sy)))
                b0, b1 = int((bx0 - x0) * sx), max(int((bx0 - x0) * sx) + 1, int(math.ceil((bx1 - x0) * sx)))
                map_scores.append(float(sim[a0:a1, b0:b1].max()))
            sc["dinov2_map"] = map_scores
            iy, ix = np.unravel_index(int(np.argmax(sim)), sim.shape)
            px_, py_ = x0 + (ix + 0.5) / sx, y0 + (iy + 0.5) / sy
            tb_ = cands[tgt]["bbox"]
            row["map_argmax_in_target_box"] = bool(tb_[0] - 3 <= px_ <= tb_[2] + 3 and tb_[1] - 3 <= py_ <= tb_[3] + 3)
            np.save(OUT / f"map_{eid.replace('/', '_')}.npy", sim)
        picks = {}
        for name, s in sc.items():
            best = int(np.argmax(s))
            tie = sum(abs(v - s[best]) < 1e-9 for v in s) > 1
            picks[name] = {"pick": best, "hit": (best == tgt) and not tie, "hit_change": (best == row["target_change"]) and not tie,
                           "scores": [round(v, 4) for v in s]}
        row["matchers"] = picks
        row["candidates"] = [{k: v for k, v in c.items() if k not in ("pixels", "_hw")} for c in cands]
        rows.append(row)
        if len(tiles) < args.sheets:
            from PIL import Image, ImageDraw
            im = Image.fromarray(img).convert("RGB").resize((w * 2, h * 2))
            d = ImageDraw.Draw(im)
            d.rectangle([rbox[0] * 2, rbox[1] * 2, rbox[2] * 2, rbox[3] * 2], outline=(255, 0, 0), width=2)
            for k, c in enumerate(cands):
                b = [v * 2 for v in c["bbox"]]
                d.rectangle(b, outline=(0, 255, 0) if k == tgt else (255, 255, 0), width=2)
                d.text((b[0], b[1] - 10), str(k), fill=(255, 255, 255))
            d.ellipse([pt[0] * w * 2 - 4, pt[1] * h * 2 - 4, pt[0] * w * 2 + 4, pt[1] * h * 2 + 4], outline=(0, 0, 255), width=2)
            cb = [v * 2 for v in cands[row["target_change"]]["bbox"]]
            d.rectangle([cb[0] - 3, cb[1] - 3, cb[2] + 3, cb[3] + 3], outline=(255, 0, 255), width=1)
            d.text((4, 4), f"{eid.split('/')[-1]} target {tgt} " + " ".join(f"{n[:6]}:{p['pick']}" for n, p in picks.items()),
                   fill=(255, 0, 0))
            tiles.append(im)
        print(f"[match] {eid}: {len(cands)} candidates, target {tgt} ({dist[tgt]:.1f} px from the projected point); "
              + "; ".join(f"{n} pick {p['pick']} {'HIT' if p['hit'] else 'miss'}" for n, p in picks.items()), flush=True)
    if tiles:
        from PIL import Image
        tw, th = tiles[0].size
        cols = 3
        for s in range(0, len(tiles), 6):
            part = tiles[s:s + 6]
            sheet = Image.new("RGB", (tw * cols, th * ((len(part) + cols - 1) // cols)))
            for k, t in enumerate(part):
                sheet.paste(t, ((k % cols) * tw, (k // cols) * th))
            sheet.save(OUT / f"sheet_{s // 6}.png")
    valid = [r for r in rows if "matchers" in r]
    summary = {"demos": len(rows), "valid": len(valid), "why_invalid": [r.get("why") for r in rows if "matchers" not in r]}
    for name in (valid[0]["matchers"] if valid else {}):
        summary[name] = sum(r["matchers"][name]["hit"] for r in valid)
        summary[f"{name}_vs_change_target"] = sum(r["matchers"][name]["hit_change"] for r in valid)
        agree = [r for r in valid if r.get("targets_agree")]
        summary[f"{name}_on_agreed"] = f"{sum(r['matchers'][name]['hit'] for r in agree)}/{len(agree)}"
    summary["targets_agree"] = sum(bool(r.get("targets_agree")) for r in valid)
    summary["settings"] = "v1 (wrist point, no merging)" if args.v1 else \
        f"v2: point at z {args.gt_z}; merge {args.merge_px} px; keep {args.keep}; change > {args.change}"
    if valid and "map_argmax_in_target_box" in valid[0]:
        summary["dinov2_map_argmax_in_target_box"] = sum(r["map_argmax_in_target_box"] for r in valid)
    d = sorted(r["target_dist_px"] for r in valid)
    if d:
        summary["target_dist_px"] = {"median": d[len(d) // 2], "max": d[-1], "over_10px": sum(x > 10 for x in d)}
        s2 = sorted(r["second_dist_px"] for r in valid if r.get("second_dist_px") is not None)
        summary["second_dist_px_median"] = s2[len(s2) // 2] if s2 else None
    z = sorted(r["ee"][2] for r in valid)
    if z:
        summary["ee_height_at_close"] = {"min": z[0], "median": z[len(z) // 2], "max": z[-1]}
    nc = [r["n_candidates"] for r in valid]
    summary["candidates_per_demo"] = {k: nc.count(k) for k in sorted(set(nc))}
    names = [k for k in summary if k in ("colour", "dinov2_crop", "dinov2_map")]
    best = max(names, key=lambda k: summary[k]) if names else None
    if best:
        b = summary[best]
        summary["gate"] = {"best": best, "hits": b, "of": 50,
                           "reading": "CARD 7 WITH THIS MATCHER" if b >= 35 else "PATH STOPS" if b < 25 else
                           "IN BETWEEN: look at the confused objects (supplement 10)"}
    if dino is not None:
        summary["encoder"] = dino.meta
    (OUT / "MATCH_PROBE.json").write_text(json.dumps({"summary": summary, "demos": rows}, indent=1) + "\n")
    print(f"[match] SUMMARY {json.dumps(summary)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

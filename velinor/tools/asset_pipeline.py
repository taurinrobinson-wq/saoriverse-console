#!/usr/bin/env python3
"""
Batch NPC asset processor

Features:
- Find candidate NPC images (suffix `_nobg.png` or in repo root) and standardize size.
- Preserve or generate alpha channel if missing (simple background removal)
- Apply a lightweight painterly filter (pyrMeanShift + bilateral) and edge overlay
- Export standardized PNGs and thumbnails into `assets/npcs/`

Usage:
    python tools/asset_pipeline.py --input-dir . --out-dir assets/npcs --size 1024

Notes:
- This is a deterministic, fast filter intended to give a painterly look without ML.
- For higher-quality neural style transfer, integrate an external model and run separately.
"""
from pathlib import Path
import argparse
import sys
import os
from typing import Tuple

try:
    from PIL import Image, ImageFilter
except Exception:
    print("Pillow is required. Install with: pip install pillow")
    raise

try:
    import numpy as np
    import cv2
except Exception:
    print("numpy and opencv-python are required. Install with: pip install numpy opencv-python")
    raise


def find_candidates(input_dir: Path):
    # Heuristic: files that end with _nobg.png or are in root and are PNGs with small filenames
    candidates = []
    for p in input_dir.rglob('*.png'):
        name = p.name.lower()
        if name.endswith('_nobg.png') or 'nobg' in name:
            candidates.append(p)
    # fallback: any png in root-level that look like NPCs (contain name hints)
    if not candidates:
        for p in input_dir.glob('*.png'):
            candidates.append(p)
    return sorted(set(candidates))


def ensure_alpha(pil: Image.Image) -> Image.Image:
    """Return RGBA image. If alpha exists, keep it. Otherwise create mask by corner bg color threshold."""
    if pil.mode == 'RGBA':
        return pil
    rgb = pil.convert('RGB')
    arr = np.array(rgb)

    # estimate background color from 4 corners
    h, w = arr.shape[:2]
    corners = np.vstack([
        arr[0:5, 0:5].reshape(-1,3),
        arr[0:5, w-5:w].reshape(-1,3),
        arr[h-5:h, 0:5].reshape(-1,3),
        arr[h-5:h, w-5:w].reshape(-1,3),
    ])
    bg = np.median(corners.astype(np.int32), axis=0)

    # distance from bg
    dist = np.linalg.norm(arr.astype(np.int32) - bg[None,None,:], axis=2)
    # dynamic threshold
    thr = max(20, np.percentile(dist, 30))
    mask = (dist > thr).astype('uint8') * 255

    # refine mask
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)

    # smooth alpha edges
    mask = cv2.GaussianBlur(mask, (7,7), 0)

    rgba = np.dstack([arr, mask])
    return Image.fromarray(rgba.astype('uint8'), 'RGBA')


def painterly_filter(pil: Image.Image) -> Image.Image:
    """Apply a lightweight painterly effect and return RGBA image."""
    # Work in BGRA for OpenCV
    rgba = pil.convert('RGBA')
    arr = np.array(rgba)
    bgr = arr[..., :3][:, :, ::-1].astype('uint8')
    alpha = arr[..., 3]

    # Reduce noise and simplify colors
    # pyrMeanShiftFiltering gives a posterized / smoothed painterly look
    shifted = cv2.pyrMeanShiftFiltering(bgr, sp=12, sr=30)

    # further smooth with bilateral filter
    for _ in range(2):
        shifted = cv2.bilateralFilter(shifted, d=9, sigmaColor=75, sigmaSpace=75)

    # Enhance edges
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 80, 150)
    edges = cv2.dilate(edges, np.ones((3,3), np.uint8), iterations=1)
    edges_col = np.stack([edges]*3, axis=2)
    # darken along edges
    shaded = shifted.copy()
    shaded[edges_col>0] = (shaded[edges_col>0] * 0.6).astype('uint8')

    # slight blur to integrate
    shaded = cv2.GaussianBlur(shaded, (3,3), 0)

    out = np.dstack([shaded[..., ::-1], alpha])
    return Image.fromarray(out.astype('uint8'), 'RGBA')


def process_image(path: Path, out_dir: Path, size: int = 1024):
    pil = Image.open(path)
    pil = ensure_alpha(pil)

    # resize preserving aspect; put on transparent square canvas
    w,h = pil.size
    scale = size / max(w,h)
    new_w, new_h = int(w*scale), int(h*scale)
    pil_resized = pil.resize((new_w, new_h), resample=Image.LANCZOS)
    canvas = Image.new('RGBA', (size,size), (0,0,0,0))
    canvas.paste(pil_resized, ((size-new_w)//2, (size-new_h)//2), pil_resized)

    # Apply painterly filter
    painted = painterly_filter(canvas)

    # output files
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / path.name
    painted.save(out_path)

    # thumbnails
    thumb_dir = out_dir / 'thumbnails'
    thumb_dir.mkdir(parents=True, exist_ok=True)
    for t in (512, 256, 128):
        tn = painted.copy()
        tn = tn.resize((t,t), resample=Image.LANCZOS)
        tn.save(thumb_dir / f"{path.stem}_{t}.png")

    print(f"Processed {path} -> {out_path} (thumbnails in {thumb_dir})")


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input-dir', default='.', help='Root to search for NPC images')
    p.add_argument('--out-dir', default='assets/npcs', help='Output directory')
    p.add_argument('--size', type=int, default=1024, help='Output size (square)')
    p.add_argument('--dry', action='store_true', help='List candidates only')
    args = p.parse_args()

    inp = Path(args.input_dir)
    out = Path(args.out_dir)

    candidates = find_candidates(inp)
    if not candidates:
        print('No PNG candidates found')
        return

    print(f'Found {len(candidates)} candidates')
    for pth in candidates:
        print(' -', pth)
    if args.dry:
        return

    for pth in candidates:
        try:
            process_image(pth, out, size=args.size)
        except Exception as e:
            print('Failed:', pth, e)


if __name__ == '__main__':
    main()

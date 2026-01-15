#!/usr/bin/env python3
"""
Color-match a source image to a target image using Reinhard color transfer.
Preserves alpha channel if present.

Usage: python tools/color_match.py source.png target.png output.png [--mode chroma|full|blend]

Requires: opencv-python, numpy
Install: pip install opencv-python numpy
"""
import sys
import argparse
import cv2
import numpy as np


def reinhard_color_transfer(src_bgr, tgt_bgr):
    # Full Reinhard transfer (all LAB channels)
    src_lab = cv2.cvtColor(src_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    tgt_lab = cv2.cvtColor(tgt_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)

    src_means, src_stds = cv2.meanStdDev(src_lab)
    tgt_means, tgt_stds = cv2.meanStdDev(tgt_lab)

    result = np.zeros_like(src_lab)
    for ch in range(3):
        s_mean = src_means[ch, 0]
        s_std = src_stds[ch, 0]
        t_mean = tgt_means[ch, 0]
        t_std = tgt_stds[ch, 0]
        if s_std < 1e-6:
            s_std = 1.0
        result[..., ch] = (src_lab[..., ch] - s_mean) / s_std * (t_std if t_std > 1e-6 else 1.0) + t_mean

    result = np.clip(result, 0, 255).astype(np.uint8)
    out_bgr = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
    return out_bgr


def chroma_only_transfer(src_bgr, tgt_bgr):
    # Keep source L (lightness), transfer only a/b chroma channels from target
    src_lab = cv2.cvtColor(src_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    tgt_lab = cv2.cvtColor(tgt_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)

    # Compute means and stds for a and b channels only
    src_means, src_stds = cv2.meanStdDev(src_lab[..., 1:3])
    tgt_means, tgt_stds = cv2.meanStdDev(tgt_lab[..., 1:3])

    result = np.zeros_like(src_lab)
    # L channel: keep source
    result[..., 0] = src_lab[..., 0]

    for i, ch in enumerate((1, 2)):
        s_mean = src_means[i, 0]
        s_std = src_stds[i, 0]
        t_mean = tgt_means[i, 0]
        t_std = tgt_stds[i, 0]
        if s_std < 1e-6:
            s_std = 1.0
        result[..., ch] = (src_lab[..., ch] - s_mean) / s_std * (t_std if t_std > 1e-6 else 1.0) + t_mean

    result = np.clip(result, 0, 255).astype(np.uint8)
    out_bgr = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
    return out_bgr


def blend_luminance_transfer(src_bgr, tgt_bgr, blend=0.5):
    # Blend L channel between source and target; transfer a/b via Reinhard
    src_lab = cv2.cvtColor(src_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    tgt_lab = cv2.cvtColor(tgt_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)

    # Perform Reinhard on a/b channels
    src_ab = src_lab[..., 1:3]
    tgt_ab = tgt_lab[..., 1:3]
    src_means, src_stds = cv2.meanStdDev(src_ab)
    tgt_means, tgt_stds = cv2.meanStdDev(tgt_ab)

    result = np.zeros_like(src_lab)
    # L = blend * tgt_L + (1-blend) * src_L
    result[..., 0] = np.clip((1.0 - blend) * src_lab[..., 0] + blend * tgt_lab[..., 0], 0, 255)

    for i, ch in enumerate((1, 2)):
        s_mean = src_means[i, 0]
        s_std = src_stds[i, 0]
        t_mean = tgt_means[i, 0]
        t_std = tgt_stds[i, 0]
        if s_std < 1e-6:
            s_std = 1.0
        result[..., ch] = (src_lab[..., ch] - s_mean) / s_std * (t_std if t_std > 1e-6 else 1.0) + t_mean

    result = np.clip(result, 0, 255).astype(np.uint8)
    out_bgr = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
    return out_bgr


def load_image_preserve_alpha(path):
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(path)

    if img.ndim == 2:
        bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        alpha = None
    elif img.shape[2] == 4:
        bgr = img[..., :3]
        alpha = img[..., 3]
    else:
        bgr = img
        alpha = None
    return bgr, alpha


def save_with_alpha(path, bgr, alpha):
    if alpha is None:
        cv2.imwrite(path, bgr)
    else:
        # Ensure alpha is uint8 and same shape
        a = alpha
        if a.dtype != np.uint8:
            a = np.clip(a, 0, 255).astype(np.uint8)
        rgba = np.dstack((bgr, a))
        cv2.imwrite(path, rgba)


def main():
    parser = argparse.ArgumentParser(description='Color-match a source image to a target using Reinhard variants')
    parser.add_argument('source')
    parser.add_argument('target')
    parser.add_argument('output')
    parser.add_argument('--mode', choices=('full', 'chroma', 'blend'), default='chroma',
                        help='Matching mode: full (all channels), chroma (keep source lightness), blend (blend L)')
    parser.add_argument('--blend', type=float, default=0.5, help='Blend factor for L channel when mode=blend (0..1)')
    args = parser.parse_args()

    src_path = args.source
    tgt_path = args.target
    out_path = args.output

    src_bgr, src_alpha = load_image_preserve_alpha(src_path)
    tgt_bgr, _ = load_image_preserve_alpha(tgt_path)

    if src_bgr.shape != tgt_bgr.shape:
        tgt_resized = cv2.resize(tgt_bgr, (src_bgr.shape[1], src_bgr.shape[0]), interpolation=cv2.INTER_AREA)
    else:
        tgt_resized = tgt_bgr

    if args.mode == 'full':
        out_bgr = reinhard_color_transfer(src_bgr, tgt_resized)
    elif args.mode == 'chroma':
        out_bgr = chroma_only_transfer(src_bgr, tgt_resized)
    else:
        out_bgr = blend_luminance_transfer(src_bgr, tgt_resized, blend=args.blend)

    save_with_alpha(out_path, out_bgr, src_alpha)
    print(f"Saved matched image to {out_path} (mode={args.mode}, blend={args.blend})")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Overlay two images for visual comparison.
Creates side-by-side and 50% blended composites.
"""
import sys
import cv2
import numpy as np


def load_png(path):
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(path)
    
    # Handle alpha
    if img.ndim == 3 and img.shape[2] == 4:
        bgr = img[..., :3]
        alpha = img[..., 3:4] / 255.0
        # Composite onto white background
        bg = np.ones_like(bgr, dtype=np.float32) * 255
        result = (bgr.astype(np.float32) * alpha + bg * (1 - alpha)).astype(np.uint8)
        return result
    return img


def main():
    if len(sys.argv) < 4:
        print("Usage: python tools/overlay_compare.py intact_path destroyed_path output_dir")
        sys.exit(2)
    
    intact_path = sys.argv[1]
    destroyed_path = sys.argv[2]
    output_dir = sys.argv[3]
    
    intact = load_png(intact_path)
    destroyed = load_png(destroyed_path)
    
    # Ensure same size
    if intact.shape != destroyed.shape:
        h, w = destroyed.shape[:2]
        intact = cv2.resize(intact, (w, h), interpolation=cv2.INTER_AREA)
    
    # Side-by-side
    side_by_side = np.hstack([intact, destroyed])
    cv2.imwrite(f"{output_dir}/compare_side_by_side.png", side_by_side)
    print(f"Saved side-by-side to {output_dir}/compare_side_by_side.png")
    
    # 50% blend
    blended = cv2.addWeighted(intact, 0.5, destroyed, 0.5, 0)
    cv2.imwrite(f"{output_dir}/compare_blended_50.png", blended)
    print(f"Saved 50% blend to {output_dir}/compare_blended_50.png")
    
    # Destroyed on top (check color differences)
    cv2.imwrite(f"{output_dir}/compare_destroyed_only.png", destroyed)
    cv2.imwrite(f"{output_dir}/compare_intact_only.png", intact)


if __name__ == '__main__':
    main()

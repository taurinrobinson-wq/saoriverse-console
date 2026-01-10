#!/usr/bin/env python3
"""Extract MediaPipe pose landmarks from a video and save JSON + overlay video.

Usage:
  python scripts/extract_mediapipe_pose.py --input path/to/video.mp4 --output-dir path/to/out
"""
import argparse
import json
import os
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision as mp_tasks_vision
from mediapipe.tasks.python.core import base_options as mp_base_options
from mediapipe.tasks.python.vision.core import image as mp_image
from tqdm import tqdm


def draw_landmarks_cv(frame, landmarks, width, height):
    # landmarks: list of normalized landmarks (x,y,z,visibility)
    for lm in landmarks:
        x = int(lm['x'] * width)
        y = int(lm['y'] * height)
        cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)


def extract(input_path, output_dir):
    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video {input_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    overlay_path = out_dir / "overlay.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(overlay_path), fourcc, fps, (width, height))

    # Prepare MediaPipe Pose Landmarker (Tasks API) using provided model file
    # Default model path: look for pose_landmarker.task next to the input video if not provided
    results_list = []

    model_path = os.environ.get('MEDIAPIPE_POSE_MODEL')
    if model_path is None:
        # common location next to videos
        model_path = os.path.join(os.path.dirname(str(input_path)), 'pose_landmarker.task')
    if not os.path.exists(model_path):
        raise FileNotFoundError(f'MediaPipe model not found at {model_path}. Set MEDIAPIPE_POSE_MODEL env or place pose_landmarker.task next to the video.')

    base_options = mp_base_options.BaseOptions(model_asset_path=model_path)
    options = mp_tasks_vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=mp_tasks_vision.RunningMode.VIDEO,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    with mp_tasks_vision.PoseLandmarker.create_from_options(options) as landmarker:
        pbar = tqdm(total=total_frames if total_frames>0 else None, desc="Processing frames")
        frame_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Convert BGR->RGB and create MediaPipe Image
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image_obj = mp_image.Image(mp_image.ImageFormat.SRGB, image_rgb)
            timestamp_ms = int(frame_idx * (1000.0 / fps))
            res = landmarker.detect_for_video(mp_image_obj, timestamp_ms)

            frame_data = {"frame_index": frame_idx, "pose_landmarks": None}
            if res and res.pose_landmarks:
                # Take first detected pose
                landmarks = []
                for lm in res.pose_landmarks[0]:
                    landmarks.append({"x": lm.x, "y": lm.y, "z": lm.z, "visibility": getattr(lm, 'visibility', 0.0)})
                frame_data["pose_landmarks"] = landmarks
                draw_landmarks_cv(frame, landmarks, width, height)

            results_list.append(frame_data)
            writer.write(frame)
            frame_idx += 1
            pbar.update(1)
        pbar.close()

    cap.release()
    writer.release()

    json_path = out_dir / "pose_landmarks.json"
    with open(json_path, "w") as f:
        json.dump(results_list, f)

    print(f"Wrote landmarks JSON: {json_path}")
    print(f"Wrote overlay video: {overlay_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    extract(args.input, args.output_dir)


if __name__ == "__main__":
    main()

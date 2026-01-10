#!/usr/bin/env python3
"""Convert MediaPipe pose_landmarks.json to a simple BVH mocap file.

This is a best-effort exporter that builds a minimal skeleton and
computes per-joint rotations by aligning rest bone vectors to frame
bone vectors using quaternions.

Usage:
  python scripts/pose_json_to_bvh.py --input path/to/pose_landmarks.json --video path/to/video.mp4 --output path/to/out.bvh

Notes:
 - Result may need cleanup/retargeting in Blender or other DCC.
 - Uses a reduced skeleton based on MediaPipe landmarks.
"""
import argparse
import json
import math
from pathlib import Path

import numpy as np
import cv2


# MediaPipe landmark indices
LM = {
    'nose': 0,
    'left_shoulder': 11,
    'right_shoulder': 12,
    'left_elbow': 13,
    'right_elbow': 14,
    'left_wrist': 15,
    'right_wrist': 16,
    'left_hip': 23,
    'right_hip': 24,
    'left_knee': 25,
    'right_knee': 26,
    'left_ankle': 27,
    'right_ankle': 28,
}


SKELETON = [
    ("Hips", None, 'hip_center'),
    ("Spine", "Hips", 'spine'),
    ("Chest", "Spine", 'chest'),
    ("Neck", "Chest", 'neck'),
    ("Head", "Neck", 'nose'),
    ("LeftShoulder", "Chest", 'left_shoulder'),
    ("LeftElbow", "LeftShoulder", 'left_elbow'),
    ("LeftWrist", "LeftElbow", 'left_wrist'),
    ("RightShoulder", "Chest", 'right_shoulder'),
    ("RightElbow", "RightShoulder", 'right_elbow'),
    ("RightWrist", "RightElbow", 'right_wrist'),
    ("LeftHip", "Hips", 'left_hip'),
    ("LeftKnee", "LeftHip", 'left_knee'),
    ("LeftAnkle", "LeftKnee", 'left_ankle'),
    ("RightHip", "Hips", 'right_hip'),
    ("RightKnee", "RightHip", 'right_knee'),
    ("RightAnkle", "RightKnee", 'right_ankle'),
]


def load_landmarks(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    frames = []
    for item in data:
        if item.get('pose_landmarks'):
            frames.append(item['pose_landmarks'])
    return frames


def landmark_to_xyz(lm, width, height, scale=1.0):
    # Convert normalized image coords to camera space approximation
    x = (lm['x'] - 0.5) * width * scale
    y = -(lm['y'] - 0.5) * height * scale
    z = lm.get('z', 0.0) * width * scale
    return np.array([x, y, z], dtype=float)


def compute_joint_positions(frame_lm, width, height, scale=1.0):
    # returns dict of named joint positions
    pos = {}
    # hip center
    lhip = landmark_to_xyz(frame_lm[LM['left_hip']], width, height, scale)
    rhip = landmark_to_xyz(frame_lm[LM['right_hip']], width, height, scale)
    hip_center = (lhip + rhip) / 2.0
    pos['hip_center'] = hip_center
    # shoulders
    lsh = landmark_to_xyz(frame_lm[LM['left_shoulder']], width, height, scale)
    rsh = landmark_to_xyz(frame_lm[LM['right_shoulder']], width, height, scale)
    shoulder_center = (lsh + rsh) / 2.0
    pos['spine'] = hip_center + (shoulder_center - hip_center) * 0.33
    pos['chest'] = hip_center + (shoulder_center - hip_center) * 0.66
    pos['neck'] = shoulder_center
    pos['nose'] = landmark_to_xyz(frame_lm[LM['nose']], width, height, scale)
    pos['left_shoulder'] = lsh
    pos['right_shoulder'] = rsh
    pos['left_elbow'] = landmark_to_xyz(frame_lm[LM['left_elbow']], width, height, scale)
    pos['right_elbow'] = landmark_to_xyz(frame_lm[LM['right_elbow']], width, height, scale)
    pos['left_wrist'] = landmark_to_xyz(frame_lm[LM['left_wrist']], width, height, scale)
    pos['right_wrist'] = landmark_to_xyz(frame_lm[LM['right_wrist']], width, height, scale)
    pos['left_hip'] = lhip
    pos['right_hip'] = rhip
    pos['left_knee'] = landmark_to_xyz(frame_lm[LM['left_knee']], width, height, scale)
    pos['right_knee'] = landmark_to_xyz(frame_lm[LM['right_knee']], width, height, scale)
    pos['left_ankle'] = landmark_to_xyz(frame_lm[LM['left_ankle']], width, height, scale)
    pos['right_ankle'] = landmark_to_xyz(frame_lm[LM['right_ankle']], width, height, scale)
    return pos


def quat_from_vectors(a, b):
    # compute quaternion that rotates vector a to b
    a = a / (np.linalg.norm(a) + 1e-8)
    b = b / (np.linalg.norm(b) + 1e-8)
    v = np.cross(a, b)
    w = 1.0 + np.dot(a, b)
    if np.linalg.norm(v) < 1e-8 and w < 1e-6:
        # opposite vectors
        # find orthogonal
        axis = np.cross(a, np.array([1, 0, 0]))
        if np.linalg.norm(axis) < 1e-6:
            axis = np.cross(a, np.array([0, 1, 0]))
        axis = axis / (np.linalg.norm(axis) + 1e-8)
        return np.array([0.0, axis[0], axis[1], axis[2]])
    q = np.array([w, v[0], v[1], v[2]])
    q = q / (np.linalg.norm(q) + 1e-8)
    return q


def quat_to_euler_xyz(q):
    # q as [w, x, y, z]
    w, x, y, z = q
    # Convert to rotation matrix then to Euler XYZ
    R = np.zeros((3, 3))
    R[0, 0] = 1 - 2 * (y * y + z * z)
    R[0, 1] = 2 * (x * y - z * w)
    R[0, 2] = 2 * (x * z + y * w)
    R[1, 0] = 2 * (x * y + z * w)
    R[1, 1] = 1 - 2 * (x * x + z * z)
    R[1, 2] = 2 * (y * z - x * w)
    R[2, 0] = 2 * (x * z - y * w)
    R[2, 1] = 2 * (y * z + x * w)
    R[2, 2] = 1 - 2 * (x * x + y * y)
    # Euler XYZ
    sy = math.sqrt(max(0.0, R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0]))
    singular = sy < 1e-6
    if not singular:
        x_ang = math.degrees(math.atan2(R[2, 1], R[2, 2]))
        y_ang = math.degrees(math.atan2(-R[2, 0], sy))
        z_ang = math.degrees(math.atan2(R[1, 0], R[0, 0]))
    else:
        x_ang = math.degrees(math.atan2(-R[1, 2], R[1, 1]))
        y_ang = math.degrees(math.atan2(-R[2, 0], sy))
        z_ang = 0.0
    return x_ang, y_ang, z_ang


def write_bvh(out_path, frames_eulers, joints, offsets, frame_time):
    # joints: list of joint names and parent indices
    with open(out_path, 'w') as f:
        f.write('HIERARCHY\n')
        # write recursively starting from root (assume index 0 is Hips)

        def write_joint(idx, indent=0):
            name, parent, key = joints[idx]
            pad = '  ' * indent
            if parent is None:
                f.write(f'{pad}ROOT {name}\n')
            else:
                f.write(f'{pad}JOINT {name}\n')
            f.write(f'{pad}{{\n')
            off = offsets[name]
            f.write(f"{pad}  OFFSET {off[0]:.6f} {off[1]:.6f} {off[2]:.6f}\n")
            if parent is None:
                f.write(f"{pad}  CHANNELS 6 Xposition Yposition Zposition Xrotation Yrotation Zrotation\n")
            else:
                f.write(f"{pad}  CHANNELS 3 Xrotation Yrotation Zrotation\n")
            # children
            for i, j in enumerate(joints):
                if j[1] == name:
                    write_joint(i, indent + 1)
            # if no children, write End Site
            children = [j for j in joints if j[1] == name]
            if not children:
                f.write(f"{pad}  End Site\n{pad}  {{\n")
                f.write(f"{pad}    OFFSET 0.000000 0.000000 0.000000\n")
                f.write(f"{pad}  }}\n")
            f.write(f'{pad}}}\n')

        write_joint(0)
        # MOTION
        f.write('MOTION\n')
        f.write(f'Frames: {len(frames_eulers)}\n')
        f.write(f'Frame Time: {frame_time:.6f}\n')
        # write frame data
        for fe in frames_eulers:
            f.write(' '.join([f'{v:.6f}' for v in fe]) + '\n')


def build_skeleton_mapping():
    # return joints list with parent names or None
    name_to_parent = {name: parent for (name, parent, key) in SKELETON}
    return SKELETON


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--video', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    frames = load_landmarks(args.input)
    if len(frames) == 0:
        print('No frames found in JSON')
        return

    # get video dims
    cap = cv2.VideoCapture(args.video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    scale = 1.0
    joints = build_skeleton_mapping()

    # compute rest positions from first frame
    rest_pos = compute_joint_positions(frames[0], width, height, scale)

    # offsets for BVH: child offset = child_pos - parent_pos (use rest pose)
    offsets = {}
    for name, parent, key in joints:
        if parent is None:
            offsets[name] = rest_pos['hip_center']
        else:
            child = rest_pos.get(key)
            parent_pos = rest_pos.get(parent.lower() if parent.lower() in rest_pos else parent)
            if child is None or parent_pos is None:
                offsets[name] = np.array([0.0, 0.0, 0.0])
            else:
                off = child - parent_pos
                offsets[name] = off

    # prepare frames: for each frame, produce BVH channel order matching hierarchy
    frames_eulers = []
    for fidx, fr in enumerate(frames):
        pos = compute_joint_positions(fr, width, height, scale)
        frame_channels = []
        # root position (Hips center)
        root_pos = pos['hip_center']
        frame_channels.extend([root_pos[0], root_pos[1], root_pos[2]])
        # root rotation set to zero (we'll compute rotations per bone)
        frame_channels.extend([0.0, 0.0, 0.0])
        # for each joint (excluding root), compute rotation aligning rest bone to current bone
        for name, parent, key in joints[1:]:
            parent_name = parent
            parent_key = None
            # rest vector
            rest_child = rest_pos.get(key)
            rest_parent = rest_pos.get(parent_name.lower() if parent_name.lower() in rest_pos else parent_name)
            if rest_child is None or rest_parent is None:
                frame_channels.extend([0.0, 0.0, 0.0])
                continue
            rest_vec = rest_child - rest_parent
            # current
            cur_child = pos.get(key)
            cur_parent = pos.get(parent_name.lower() if parent_name.lower() in pos else parent_name)
            if cur_child is None or cur_parent is None:
                frame_channels.extend([0.0, 0.0, 0.0])
                continue
            cur_vec = cur_child - cur_parent
            q = quat_from_vectors(rest_vec, cur_vec)
            e = quat_to_euler_xyz(q)
            frame_channels.extend([e[0], e[1], e[2]])
        frames_eulers.append(frame_channels)

    out_path = Path(args.output)
    write_bvh(out_path, frames_eulers, joints, offsets, 1.0 / fps)
    print(f'Wrote BVH: {out_path}')


if __name__ == '__main__':
    main()

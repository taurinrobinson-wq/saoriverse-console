#!/usr/bin/env python3
"""
Procedural building generator: defines a BuildingProfile, generates bricks
in brick-unit coordinates, and renders an intact building as PNG.

Usage: python tools/procedural_building.py output.png

This is a lightweight prototype to create an intact building from a profile.
"""
import argparse
import json
import math
import random
import pygame
import numpy as np
import cv2


class BuildingProfile:
    def __init__(self, stories=2, width_bricks=10, rows_per_story=8,
                 window_layout=None, door=(4, 0), roof_pitch=45, style='abandoned'):
        self.stories = stories
        self.width_bricks = width_bricks
        self.rows_per_story = rows_per_story
        self.height_rows = stories * rows_per_story
        self.window_layout = window_layout or {
            'floor1': [(2, 2), (6, 2)],
            'floor2': [(2, 10), (6, 10)]
        }
        self.door = door  # (col, row) in brick units (col index, row index from bottom)
        self.roof_pitch = roof_pitch
        self.style = style

    def to_dict(self):
        return self.__dict__


def generate_bricks(profile, brick_w=35, brick_h=18, gutter=1):
    """Generate brick objects (pixel coords) from profile using running-bond."""
    bricks = []
    total_rows = profile.height_rows
    # base pixel origin for bottom-left of building
    base_x = 50
    base_y = 700 - 100  # match earlier canvas assumptions
    # Define window holes region in pixel coordinates: convert profile window points to 2x2 brick holes
    window_rects = []
    for floor_key, wins in profile.window_layout.items():
        for (wc, wr) in wins:
            wx = base_x + wc * (brick_w + gutter)
            wy = base_y - wr * (brick_h + gutter)
            w_px = 2 * brick_w + gutter
            h_px = 2 * brick_h + gutter
            # window rect uses top-left origin in pixel coords
            window_rects.append((wx, wy - h_px, w_px, h_px))

    # For each row (0 = bottom)
    for row in range(total_rows):
        y = base_y - row * (brick_h + gutter)

        # Determine running-bond offset: odd (1-based) rows offset by half a brick
        row_one_based = row + 1
        offset = (brick_w // 2) if (row_one_based % 2 == 1) else 0

        # Compute wall pixel extents so bricks always fill the same wall width
        wall_left = base_x
        wall_right = base_x + profile.width_bricks * (brick_w + gutter) - gutter

        x_cursor = wall_left + offset
        # place bricks left-to-right, trimming final brick to fit the wall width (creates half bricks)
        while x_cursor < wall_right - 0.5:
            # default full brick width
            w = brick_w
            # if the next full brick would exceed wall_right, trim it to fit
            if x_cursor + w > wall_right:
                w = int(max(1, wall_right - x_cursor))

            # brick rect in pixel coords (top-left)
            brick_left = x_cursor
            brick_top = y - brick_h
            brick_rect = (brick_left, brick_top, w, brick_h)

            # Door check (profile.door is in brick units) -> convert to pixel rect
            door_col, door_row = profile.door
            door_x = base_x + door_col * (brick_w + gutter)
            door_y = base_y - door_row * (brick_h + gutter)
            door_w = brick_w * 2
            door_h = 90
            door_rect = (door_x, door_y - door_h + 10, door_w, door_h)

            # Skip brick if it intersects door rect
            def rects_intersect(a, b):
                ax, ay, aw, ah = a
                bx, by, bw, bh = b
                return not (ax + aw <= bx or bx + bw <= ax or ay + ah <= by or by + bh <= ay)

            if rects_intersect(brick_rect, door_rect):
                x_cursor += w + gutter
                continue

            # Skip if intersects any window rect
            skip = False
            for wr in window_rects:
                if rects_intersect(brick_rect, wr):
                    skip = True
                    break
            if skip:
                x_cursor += w + gutter
                continue

            # place brick (store center-based coords as before)
            bricks.append({'x': brick_left + w / 2, 'y': y - brick_h / 2, 'w': w, 'h': brick_h, 'angle': 0, 'type': 'wall'})

            x_cursor += w + gutter
    return bricks


def render_intact(profile, bricks, roof_rows=6, output='out.png', width=600, height=700):
    pygame.init()
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))

    # brick dimensions must match generator defaults
    brick_w = 35
    brick_h = 18

    # simple backdrop and ground
    base_y = height - 100
    wall_left = 10
    wall_right = width - 10
    wall_top = int(base_y - profile.height_rows * 18 - 40)
    wall_rect = pygame.Rect(wall_left, wall_top, wall_right - wall_left, base_y - wall_top)
    pygame.draw.rect(surface, (40, 35, 30, 14), wall_rect)
    pygame.draw.line(surface, (40, 30, 20, 160), (0, base_y), (width, base_y), 2)

    # draw roof wedge
    # draw roof triangle centered above top layer
    roof_color = (30, 40, 25)
    peak_x = width // 2
    # position peak a little above top wall
    peak_y = wall_top - max(60, int(brick_h * 2))
    # make roof base wider than building
    extra = int(brick_w * 2)
    left_x = max(0, wall_left - extra)
    right_x = min(width, wall_right + extra)
    pygame.draw.polygon(surface, roof_color, [(left_x, wall_top), (peak_x, peak_y), (right_x, wall_top)])

    # draw bricks
    for b in bricks:
        bx = int(b['x'])
        by = int(b['y'])
        w = int(b['w'])
        h = int(b['h'])
        # color variation
        base = np.array((180, 100, 60))
        jitter = np.random.randint(-10, 10, size=3)
        col = tuple(np.clip(base + jitter, 20, 255).astype(int))
        brick_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(brick_surf, col, (0, 0, w, h))
        pygame.draw.rect(brick_surf, (80, 40, 25), (0, 0, w, h), 1)
        surface.blit(brick_surf, (bx - w//2, by - h//2))

    # draw door and windows using profile units -> pixel mapping
    brick_w = 35
    brick_h = 18
    base_x = 50
    gutter = 1
    door_col, door_row = profile.door
    door_x = base_x + door_col * (brick_w + gutter)
    door_y = base_y - door_row * (brick_h + gutter)
    door_w = brick_w * 2
    door_h = 90
    door_rect = pygame.Rect(door_x, door_y - door_h + 10, door_w, door_h)
    pygame.draw.rect(surface, (25, 18, 12), door_rect)
    pygame.draw.rect(surface, (80, 60, 40), door_rect, 3)

    # windows
    for floor_key, wins in profile.window_layout.items():
        for (wc, wr) in wins:
            wx = base_x + wc * (brick_w + gutter)
            wy = base_y - wr * (brick_h + gutter)
            w_px = 2 * brick_w + gutter
            h_px = 2 * brick_h + gutter
            wrect = pygame.Rect(wx, wy - h_px, w_px, h_px)
            glass = pygame.Surface((wrect.width, wrect.height), pygame.SRCALPHA)
            glass.fill((80, 110, 130, 140))
            surface.blit(glass, (wrect.left, wrect.top))
            pygame.draw.rect(surface, (30, 30, 30), wrect, 3)

    pygame.image.save(surface, output)
    pygame.quit()

    # small tint to match game palette
    img = cv2.imread(output, cv2.IMREAD_UNCHANGED).astype(np.float32)
    b, g, r = cv2.split(img[..., :3])
    g = g * 1.05
    r = r * 0.95
    out = cv2.merge([b, g, r]).astype(np.uint8)
    cv2.imwrite(output, out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)

    profile = BuildingProfile()
    bricks = generate_bricks(profile)
    render_intact(profile, bricks, output=args.output)
    print('Wrote', args.output)


if __name__ == '__main__':
    main()

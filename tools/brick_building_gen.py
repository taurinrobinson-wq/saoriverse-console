#!/usr/bin/env python3
"""
Generate a procedural brick building (intact or collapsed).
Creates a 2-story building with sloped roof.

Usage: python tools/brick_building_gen.py output.png [--width 600] [--height 700] [--mode intact|collapsed] [--seed 42]

Requires: pygame, numpy, opencv-python
Install: pip install pygame numpy opencv-python
"""
import sys
import argparse
import math
import random
import numpy as np
import pygame
from pygame.locals import *
import cv2


class BrickBuilding:
    def __init__(self, width=600, height=700, seed=42):
        self.width = width
        self.height = height
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        self.bricks = []
        self.roof_bricks = []
        self.center_x = width / 2
        self.base_y = height - 100
        
        self._create_building()
    
    def _create_building(self):
        """Create a 2-story brick building structure (intact standing form).

        This builds semantic regions (walls with openings and a coherent roof)
        instead of naively filling a rectangle with bricks.
        """
        brick_w, brick_h = 35, 18

        # Wall parameters
        story1_y = self.base_y
        story2_y = story1_y - 160

        # Door and window placement (in pixels)
        self.door_x_min, self.door_x_max = int(self.center_x - 60), int(self.center_x + 60)
        self.window1_x_min, self.window1_x_max = 120, 200
        self.window2_x_min, self.window2_x_max = 420, 500
        window_y_min = story1_y - 5 * (brick_h + 1)
        window_y_max = story1_y - 2 * (brick_h + 1)

        # Helper to add wall rows with openings
        def add_wall_rows(base_y):
            # Use running bond: offset every other row by half a brick
            for row in range(8):
                y = base_y - row * (brick_h + 1)
                offset = 0 if row % 2 == 0 else (brick_w // 2)
                for col in range(12):
                    x = 10 + offset + col * (brick_w + 1)

                    # Door void on lower rows
                    if base_y == story1_y and row < 5 and self.door_x_min <= x <= self.door_x_max:
                        continue

                    # Window voids on appropriate rows
                    if window_y_min <= y <= window_y_max:
                        if (self.window1_x_min <= x <= self.window1_x_max) or (self.window2_x_min <= x <= self.window2_x_max):
                            continue

                    self.bricks.append({'x': x, 'y': y, 'w': brick_w, 'h': brick_h,
                                        'angle': 0, 'type': 'wall'})

        add_wall_rows(story1_y)
        add_wall_rows(story2_y)

        # Sloped roof: build two coherent sloping bands (left and right)
        roof_base_y = story2_y - 40
        roof_rows = 8
        for row in range(roof_rows):
            y = roof_base_y - row * (brick_h + 2)
            span = max(1, 12 - row * 1)  # narrower as we go up
            for i in range(span):
                # Left side
                x_left = int(self.center_x - (span * brick_w) / 2 + i * (brick_w + 1) - 80)
                w_left = max(20, brick_w - row)
                self.roof_bricks.append({'x': x_left, 'y': y, 'w': w_left, 'h': brick_h,
                                         'angle': -10 - row * 2, 'type': 'roof'})
                # Right side
                x_right = int(self.center_x + (span * brick_w) / 2 - i * (brick_w + 1) + 80)
                w_right = max(20, brick_w - row)
                self.roof_bricks.append({'x': x_right, 'y': y, 'w': w_right, 'h': brick_h,
                                         'angle': 10 + row * 2, 'type': 'roof'})
    
    def apply_collapse_physics(self, duration_frames=300, strength=1.0):
        """Apply physics-based collapse (simulates for several seconds)"""
        import pymunk

        space = pymunk.Space()
        space.gravity = (0, 500)

        # Build a list of all bricks, but optionally simulate only the upper/dynamic subset
        all_bricks = self.bricks + self.roof_bricks

        # Decide which bricks are dynamic: above a certain height (keep base rows static)
        dynamic_threshold = self.base_y - 80
        bodies = []
        body_to_index = []
        for idx, brick in enumerate(all_bricks):
            # If brick is low (near base) keep static by not adding physics body
            if brick['y'] > dynamic_threshold and brick['type'] == 'wall':
                bodies.append(None)
                body_to_index.append(idx)
                continue

            moment = pymunk.moment_for_box(1, (brick['w'], brick['h']))
            body = pymunk.Body(1, moment)
            body.position = (brick['x'], brick['y'])
            body.angle = math.radians(brick.get('angle', 0))
            shape = pymunk.Poly.create_box(body, (brick['w'], brick['h']))
            shape.friction = 0.5
            space.add(body, shape)
            bodies.append(body)
            body_to_index.append(idx)

        # Run physics simulation
        for frame in range(duration_frames):
            for b in bodies:
                if b is None:
                    continue
                dx = self.center_x - b.position.x
                dy = self.base_y + 80 - b.position.y
                dist = math.sqrt(dx*dx + dy*dy) + 1e-6

                fx = (dx / dist) * strength * b.mass * 200
                fy = (dy / dist) * strength * b.mass * 150

                b.velocity = (b.velocity.x * 0.92, b.velocity.y * 0.92)
                offset = pymunk.Vec2d(random.uniform(-8, 8), random.uniform(-4, 4))
                b.apply_force_at_world_point((fx, fy), b.position + offset)
                b.torque += random.uniform(-4000, 4000)

            space.step(1 / 60.0)

        # Update brick positions and angles from physics for bricks that had bodies
        for body, idx in zip(bodies, body_to_index):
            if body is None:
                continue
            target = all_bricks[idx]
            target['x'] = body.position.x
            target['y'] = body.position.y
            target['angle'] = math.degrees(body.angle)
    
    def render_to_surface(self, surface):
        """Render bricks to a pygame surface"""
        surface.fill((0, 0, 0, 0))  # Transparent background
        
        # Add shadow blob under the building for depth
        shadow_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        shadow_color = (0, 0, 0, 60)
        pygame.draw.ellipse(shadow_surface, shadow_color, 
                           (self.center_x - 140, self.base_y - 10, 280, 50))
        surface.blit(shadow_surface, (0, 0))
        
        # Draw ground line
        pygame.draw.line(surface, (40, 30, 20, 100), 
                        (0, self.base_y), (self.width, self.base_y), 2)

        # Draw a subtle wall backdrop so gaps/voids read as negative space
        wall_left = 10
        wall_right = self.width - 10
        wall_top = int(self.base_y - 360)
        wall_rect = pygame.Rect(wall_left, wall_top, wall_right - wall_left, self.base_y - wall_top)
        pygame.draw.rect(surface, (40, 35, 30, 12), wall_rect)
        
        # Draw all bricks
        for brick_info in self.bricks + self.roof_bricks:
            self._draw_brick(surface, brick_info)

        # Draw doors and windows (frame + glass/void)
        # Door
        door_w = self.door_x_max - self.door_x_min
        door_h = 90
        door_rect = pygame.Rect(self.door_x_min - door_w//2 + (self.door_x_max - self.door_x_min)//2, self.base_y - door_h, door_w, door_h)
        pygame.draw.rect(surface, (30, 20, 15, 255), door_rect)  # dark door
        pygame.draw.rect(surface, (90, 60, 40, 255), door_rect, 4)
        # Doorknob
        pygame.draw.circle(surface, (200, 180, 120), (door_rect.right - 20, door_rect.centery), 4)

        # Windows (left & right)
        win_w = self.window1_x_max - self.window1_x_min
        win_h = 60
        w1_rect = pygame.Rect(self.window1_x_min, int(self.base_y - 4*(win_h/2) - 40), win_w, win_h)
        w2_rect = pygame.Rect(self.window2_x_min, int(self.base_y - 4*(win_h/2) - 40), win_w, win_h)
        for wr in (w1_rect, w2_rect):
            # Glass (slightly transparent bluish)
            glass = pygame.Surface((wr.width, wr.height), pygame.SRCALPHA)
            glass.fill((80, 110, 130, 140))
            surface.blit(glass, (wr.left, wr.top))
            pygame.draw.rect(surface, (30, 30, 30), wr, 4)
    
    def _draw_brick(self, surface, brick_info):
        """Draw a single brick with rotation"""
        x, y = brick_info['x'], brick_info['y']
        w, h = brick_info['w'], brick_info['h']
        angle = brick_info['angle']
        
        # Create brick rect and rotate
        rect = pygame.Rect(x - w/2, y - h/2, w, h)
        
        # Base brick color with per-brick variation
        if brick_info['type'] == 'roof':
            base_color = np.array([150, 80, 40], dtype=np.float32)
        else:
            base_color = np.array([180, 100, 60], dtype=np.float32)
        
        # Add color jitter
        jitter = np.random.randint(-12, 12, size=3)
        brick_color = tuple(np.clip(base_color + jitter, 30, 255).astype(int))
        outline_color = (80, 40, 25)
        
        # Create a small surface for the brick and rotate it
        brick_surf = pygame.Surface((int(w), int(h)), pygame.SRCALPHA)
        pygame.draw.rect(brick_surf, brick_color, (0, 0, int(w), int(h)))
        pygame.draw.rect(brick_surf, outline_color, (0, 0, int(w), int(h)), 1)
        
        if angle != 0:
            brick_surf = pygame.transform.rotate(brick_surf, angle)
        
        # Blit to main surface
        pos = brick_surf.get_rect(center=(int(x), int(y)))
        surface.blit(brick_surf, pos)


def apply_forest_tint(input_path, output_path, tint_strength=0.3):
    """Apply a greenish forest tint to match the background"""
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED).astype(np.float32)
    
    if img.shape[2] == 4:
        # Has alpha
        b, g, r, a = cv2.split(img)
        # Apply tint: add green bias, reduce red, keep blue similar
        b = b * (1 - tint_strength * 0.1)
        g = g * (1 + tint_strength * 0.25)
        r = r * (1 - tint_strength * 0.15)
        result = cv2.merge([b, g, r, a])
    else:
        b, g, r = cv2.split(img)
        b = b * (1 - tint_strength * 0.1)
        g = g * (1 + tint_strength * 0.25)
        r = r * (1 - tint_strength * 0.15)
        result = cv2.merge([b, g, r])
    
    result = np.clip(result, 0, 255).astype(np.uint8)
    cv2.imwrite(output_path, result)


def main():
    parser = argparse.ArgumentParser(description='Generate a brick building (intact or collapsed)')
    parser.add_argument('output', help='Output PNG file path')
    parser.add_argument('--width', type=int, default=600, help='Image width')
    parser.add_argument('--height', type=int, default=700, help='Image height')
    parser.add_argument('--mode', choices=('intact', 'collapsed'), default='intact',
                        help='Building state: intact (standing) or collapsed (physics sim)')
    parser.add_argument('--collapse-strength', type=float, default=1.0, help='Collapse force (0..1)')
    parser.add_argument('--duration', type=int, default=300, help='Physics frames for collapse')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--tint-strength', type=float, default=0.35, help='Green forest tint strength')
    args = parser.parse_args()
    
    # Initialize pygame
    pygame.init()
    surface = pygame.Surface((args.width, args.height), pygame.SRCALPHA)
    
    # Create building
    building = BrickBuilding(args.width, args.height, args.seed)
    
    # Apply physics if collapsed mode
    if args.mode == 'collapsed':
        print(f"Simulating collapse: {len(building.bricks) + len(building.roof_bricks)} bricks")
        building.apply_collapse_physics(duration_frames=args.duration, strength=args.collapse_strength)
    
    # Render to surface
    building.render_to_surface(surface)
    
    # Save to file using pygame
    pygame.image.save(surface, args.output)
    pygame.quit()
    
    # Post-process: apply greenish forest tint
    apply_forest_tint(args.output, args.output, tint_strength=args.tint_strength)
    
    print(f"Saved {args.mode} building to {args.output}")


if __name__ == '__main__':
    main()

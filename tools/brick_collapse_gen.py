#!/usr/bin/env python3
"""
Generate a procedural brick building with physics-based inward collapse.
Creates a 2-story building with sloped roof, simulates bricks falling inward,
and renders to PNG with transparency.

Usage: python tools/brick_collapse_gen.py output.png [--width 400] [--height 500] [--collapse 0.8] [--seed 42]

Requires: pymunk, pygame, numpy, opencv-python
Install: pip install pymunk pygame numpy opencv-python
"""
import sys
import argparse
import math
import random
import numpy as np
import pymunk
import pymunk.pygame_util
import pygame
from pygame.locals import *
import cv2


class BrickBuilding:
    def __init__(self, width=400, height=500, seed=42):
        self.width = width
        self.height = height
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        # Physics space
        self.space = pymunk.Space()
        self.space.gravity = (0, 500)  # Downward gravity
        
        self.bricks = []
        self.roof_bricks = []
        self.center_x = width / 2
        self.base_y = height - 80
        
        self._create_building()
    
    def _create_building(self):
        """Create a 2-story brick building structure"""
        brick_w, brick_h = 35, 18
        
        # Story 1 (bottom) - wider base
        story1_y = self.base_y
        for row in range(8):  # Increased from 5
            for col in range(10):  # Increased from 8
                x = 20 + col * (brick_w + 1)
                y = story1_y - row * (brick_h + 1)
                self._add_brick(x, y, brick_w, brick_h)
        
        # Story 2 (top)
        story2_y = story1_y - 160
        for row in range(8):  # Increased from 5
            for col in range(10):  # Increased from 8
                x = 20 + col * (brick_w + 1)
                y = story2_y - row * (brick_h + 1)
                self._add_brick(x, y, brick_w, brick_h)
        
        # Sloped roof (left and right triangular sections)
        roof_top_y = story2_y - 160
        
        # Left roof - more bricks
        for i in range(8):
            for j in range(3 - min(i // 3, 2)):
                x = self.center_x - 40 - i * 32 + j * (brick_w + 2)
                y = roof_top_y - i * 22
                w, h = max(25, 35 - i * 2), 18
                self._add_brick(x, y, w, h, is_roof=True)
        
        # Right roof - more bricks
        for i in range(8):
            for j in range(3 - min(i // 3, 2)):
                x = self.center_x + 40 + i * 32 - j * (brick_w + 2)
                y = roof_top_y - i * 22
                w, h = max(25, 35 - i * 2), 18
                self._add_brick(x, y, w, h, is_roof=True)
    
    def _add_brick(self, x, y, w, h, is_roof=False):
        """Add a brick to the building"""
        moment = pymunk.moment_for_box(1, (w, h))
        body = pymunk.Body(1, moment)
        body.position = (x, y)
        shape = pymunk.Poly.create_box(body, (w, h))
        shape.friction = 0.5
        shape.density = 1
        self.space.add(body, shape)
        
        brick_info = {'body': body, 'shape': shape, 'w': w, 'h': h, 'is_roof': is_roof}
        if is_roof:
            self.roof_bricks.append(brick_info)
        else:
            self.bricks.append(brick_info)
    
    def apply_collapse_force(self, strength=0.8, duration_frames=120):
        """Apply inward-pulling forces to collapse the building"""
        print(f"Simulating collapse: {len(self.bricks) + len(self.roof_bricks)} bricks, "
              f"strength={strength}, duration={duration_frames} frames")
        
        for frame in range(duration_frames):
            # Apply forces toward center
            for brick_info in self.bricks + self.roof_bricks:
                body = brick_info['body']
                dx = self.center_x - body.position.x
                dy = self.base_y + 80 - body.position.y  # Bias strongly toward base
                dist = math.sqrt(dx*dx + dy*dy) + 1e-6
                
                # Normalize and scale — MUCH stronger forces
                fx = (dx / dist) * strength * body.mass * 200  # Doubled from 100
                fy = (dy / dist) * strength * body.mass * 150  # Doubled from 80
                
                body.velocity = (body.velocity.x * 0.92, body.velocity.y * 0.92)  # More damping
                
                # Apply force off-center for rotation
                offset = pymunk.Vec2d(random.uniform(-8, 8), random.uniform(-4, 4))
                body.apply_force_at_world_point((fx, fy), body.position + offset)
                
                # Add stronger random torque for tumbling
                body.torque += random.uniform(-4000, 4000)
            
            # Step physics
            self.space.step(1 / 60.0)
            
            if (frame + 1) % 60 == 0:
                print(f"  Frame {frame + 1}/{duration_frames}")
        
        print("Collapse simulation complete.")
    
    def render_to_surface(self, surface):
        """Render bricks to a pygame surface"""
        surface.fill((0, 0, 0, 0))  # Transparent background
        
        # Add shadow blob under the pile for depth
        shadow_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        shadow_color = (0, 0, 0, 60)
        pygame.draw.ellipse(shadow_surface, shadow_color, 
                           (self.center_x - 120, self.base_y - 20, 240, 60))
        surface.blit(shadow_surface, (0, 0))
        
        # Draw ground plane (very subtle dark line)
        pygame.draw.line(surface, (40, 30, 20, 100), 
                        (0, self.base_y), (self.width, self.base_y), 2)
        
        # Draw bricks with color variation and shading
        for brick_info in self.bricks + self.roof_bricks:
            body = brick_info['body']
            shape = brick_info['shape']
            
            # Get vertices in world space
            vertices = [(body.position.x + v.x, body.position.y + v.y) 
                       for v in shape.get_vertices()]
            
            # Skip if off-screen
            if all(v[1] > self.height + 50 or v[0] < -50 or v[0] > self.width + 50 
                   for v in vertices):
                continue
            
            # Base brick color with per-brick variation
            if brick_info['is_roof']:
                base_color = np.array([150, 80, 40], dtype=np.float32)
            else:
                base_color = np.array([180, 100, 60], dtype=np.float32)
            
            # Add color jitter for variation
            jitter = np.random.randint(-12, 12, size=3)
            brick_color = tuple(np.clip(base_color + jitter, 30, 255).astype(int))
            outline_color = (80, 40, 25)
            
            # Draw filled brick
            if len(vertices) >= 3:
                pygame.draw.polygon(surface, brick_color, vertices)
                pygame.draw.polygon(surface, outline_color, vertices, 1)
            
            # Add subtle shadow/highlight based on rotation for 3D feel
            angle_deg = math.degrees(body.angle) % 360
            if 45 < angle_deg < 225:
                # Facing down/back = darker
                shadow_overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
                pygame.draw.polygon(shadow_overlay, (0, 0, 0, 30), vertices)
                surface.blit(shadow_overlay, (0, 0))


def main():
    parser = argparse.ArgumentParser(description='Generate a collapsing brick building')
    parser.add_argument('output', help='Output PNG file path')
    parser.add_argument('--width', type=int, default=400, help='Image width')
    parser.add_argument('--height', type=int, default=500, help='Image height')
    parser.add_argument('--collapse', type=float, default=0.8, help='Collapse force strength (0..1)')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--tint-strength', type=float, default=0.3, help='Green forest tint strength (0..1)')
    parser.add_argument('--duration', type=int, default=300, help='Physics simulation frames')
    args = parser.parse_args()
    
    # Initialize pygame
    pygame.init()
    surface = pygame.Surface((args.width, args.height), pygame.SRCALPHA)
    
    # Create building and simulate
    building = BrickBuilding(args.width, args.height, args.seed)
    building.apply_collapse_force(strength=args.collapse, duration_frames=args.duration)
    
    # Render to surface
    building.render_to_surface(surface)
    
    # Save to file using pygame
    pygame.image.save(surface, args.output)
    pygame.quit()
    
    # Post-process: apply greenish forest tint via OpenCV
    apply_forest_tint(args.output, args.output, tint_strength=args.tint_strength)
    
    print(f"Saved collapsing building to {args.output}")


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


if __name__ == '__main__':
    main()

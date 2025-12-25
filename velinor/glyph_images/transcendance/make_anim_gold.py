#!/usr/bin/env python3
"""Generate golden-glow animated GIFs for the glyph.
Outputs:
 - transcendance_pulse_gold.gif (transparent/dark canvas)
 - transcendance_on_boss_chamber_gold.gif (composited onto boss_chamber01.png)
"""
from PIL import Image, ImageFilter, ImageEnhance
import math
import os

HERE = os.path.dirname(__file__)
INPUT = os.path.join(HERE, 'triglyph.png')
BG = os.path.join(HERE, '..', '..', 'backgrounds', 'boss_chamber01.png')
OUT_PULSE = os.path.join(HERE, 'transcendance_pulse_gold.gif')
OUT_ON_BG = os.path.join(HERE, 'transcendance_on_boss_chamber_gold.gif')

# Parameters
frames = 36
fps = 12
duration_ms = int(1000 / fps)
bob_amp = 10
scale_amp = 0.035
glow_max_radius = 28
# warm golden glow
glow_color = (255, 210, 100)

if not os.path.exists(INPUT):
    raise SystemExit(f"Input glyph not found: {INPUT}")

base = Image.open(INPUT).convert('RGBA')
W, H = base.size

# --- create pulsing transparent/dark canvas GIF ---
frames_list = []
for i in range(frames):
    t = i / frames
    bob = math.sin(t * 2 * math.pi) * bob_amp
    pulse = (math.sin(t * 2 * math.pi - math.pi/2) + 1) / 2
    scale = 1.0 + (pulse - 0.5) * 2 * scale_amp

    pad = glow_max_radius * 3
    canvas_w = int(W * 1.0 + pad * 2)
    canvas_h = int(H * 1.0 + pad * 2 + abs(bob))
    canvas = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))

    scaled = base.resize((int(W * scale), int(H * scale)), Image.LANCZOS)
    alpha = scaled.split()[3]

    glow = Image.new('RGBA', scaled.size, glow_color + (0,))
    glow_alpha = ImageEnhance.Brightness(alpha).enhance(0.6 + pulse * 1.3)
    glow.putalpha(glow_alpha)
    glow = glow.filter(ImageFilter.GaussianBlur(radius=glow_max_radius * (0.6 + pulse * 0.6)))

    x = (canvas_w - scaled.width) // 2
    y = (canvas_h - scaled.height) // 2 - int(bob)
    canvas.paste(glow, (x, y), glow)
    canvas.paste(scaled, (x, y), scaled)

    # dark background with subtle overlay
    bg = Image.new('RGBA', canvas.size, (8, 10, 14, 255))
    overlay = Image.new('RGBA', canvas.size, (0, 0, 0, 48))
    composed = Image.alpha_composite(bg, canvas)
    composed = Image.alpha_composite(composed, overlay)

    frames_list.append(composed)

frames_list[0].save(
    OUT_PULSE,
    format='GIF',
    save_all=True,
    append_images=frames_list[1:],
    duration=duration_ms,
    loop=0,
    disposal=2,
    optimize=True
)
print('Wrote', OUT_PULSE)

# --- composite onto boss chamber background ---
if not os.path.exists(BG):
    raise SystemExit(f"Background not found: {BG}")

bg_img = Image.open(BG).convert('RGBA')
bg_w, bg_h = bg_img.size

# scale glyph relative to bg width
glyph_fraction = 0.28
target_w = int(bg_w * glyph_fraction)
scale_base = target_w / base.width
base_scaled = base.resize((int(base.width * scale_base), int(base.height * scale_base)), Image.LANCZOS)

frames_on_bg = []
for i in range(frames):
    t = i / frames
    bob = math.sin(t * 2 * math.pi) * bob_amp
    pulse = (math.sin(t * 2 * math.pi - math.pi/2) + 1) / 2
    scale = 1.0 + (pulse - 0.5) * 2 * scale_amp

    scaled = base_scaled.resize((int(base_scaled.width * scale), int(base_scaled.height * scale)), Image.LANCZOS)
    alpha = scaled.split()[3]

    glow = Image.new('RGBA', scaled.size, glow_color + (0,))
    glow_alpha = ImageEnhance.Brightness(alpha).enhance(0.6 + pulse * 1.3)
    glow.putalpha(glow_alpha)
    glow = glow.filter(ImageFilter.GaussianBlur(radius=glow_max_radius * (0.6 + pulse * 0.6)))

    frame = bg_img.copy()
    x = (bg_w - scaled.width) // 2
    y = int((bg_h - scaled.height) // 2 - bob)
    frame.paste(glow, (x, y), glow)
    frame.paste(scaled, (x, y), scaled)
    frames_on_bg.append(frame)

frames_on_bg[0].save(
    OUT_ON_BG,
    format='GIF',
    save_all=True,
    append_images=frames_on_bg[1:],
    duration=duration_ms,
    loop=0,
    disposal=2,
    optimize=True
)
print('Wrote', OUT_ON_BG)

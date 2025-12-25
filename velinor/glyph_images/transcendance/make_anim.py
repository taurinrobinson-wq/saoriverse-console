#!/usr/bin/env python3
"""Generate a pulsing glow + bobbing animated GIF from triglyph.png.
Outputs: transcendance_pulse.gif (in same folder)
"""
from PIL import Image, ImageFilter, ImageChops, ImageEnhance
import math
import os

HERE = os.path.dirname(__file__)
INPUT = os.path.join(HERE, 'triglyph.png')
OUT_GIF = os.path.join(HERE, 'transcendance_pulse.gif')

# Parameters
frames = 36
fps = 12
duration_ms = int(1000 / fps)
bob_amp = 8            # pixels vertical bob amplitude
scale_amp = 0.03       # scale amplitude (fraction)
glow_max_radius = 20   # blur radius for glow
glow_color = (140, 190, 255)  # RGB glow color

if not os.path.exists(INPUT):
    raise SystemExit(f"Input not found: {INPUT}")

base = Image.open(INPUT).convert('RGBA')
W, H = base.size

frames_list = []
for i in range(frames):
    t = i / frames  # 0..1
    # bob using sine wave (smooth)
    bob = math.sin(t * 2 * math.pi) * bob_amp
    # pulse value 0..1
    pulse = (math.sin(t * 2 * math.pi - math.pi/2) + 1) / 2
    # scale
    scale = 1.0 + (pulse - 0.5) * 2 * scale_amp

    # create a transparent canvas slightly larger for glow space
    pad = glow_max_radius * 3
    canvas_w = int(W * 1.0 + pad * 2)
    canvas_h = int(H * 1.0 + pad * 2 + abs(bob))
    canvas = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))

    # scaled glyph
    scaled = base.resize((int(W * scale), int(H * scale)), Image.LANCZOS)

    # create glow: take alpha channel, colorize and blur
    alpha = scaled.split()[3]
    glow = Image.new('RGBA', scaled.size, glow_color + (0,))
    glow.putalpha(alpha)
    # enhance glow opacity with pulse
    glow_alpha = ImageEnhance.Brightness(alpha).enhance(0.6 + pulse * 1.2)
    glow.putalpha(glow_alpha)
    # apply blur to glow to create halo
    glow = glow.filter(ImageFilter.GaussianBlur(radius=glow_max_radius * (0.6 + pulse * 0.6)))

    # paste glow onto canvas centered
    x = (canvas_w - scaled.width) // 2
    y = (canvas_h - scaled.height) // 2 - int(bob)
    canvas.paste(glow, (x, y), glow)
    canvas.paste(scaled, (x, y), scaled)

    # composite onto a simple dark background with a subtle translucent overlay
    bg = Image.new('RGBA', canvas.size, (6, 8, 12, 255))
    # light translucent overlay instead of expensive per-pixel vignette
    overlay = Image.new('RGBA', canvas.size, (0, 0, 0, 48))
    composed = Image.alpha_composite(bg, canvas)
    composed = Image.alpha_composite(composed, overlay)

    # convert to P mode for GIF (adaptive palette)
    frame = composed.convert('RGBA')
    frames_list.append(frame)

# Save as animated GIF
frames_list[0].save(
    OUT_GIF,
    format='GIF',
    save_all=True,
    append_images=frames_list[1:],
    duration=duration_ms,
    loop=0,
    disposal=2,
    optimize=True
)

print('Wrote', OUT_GIF)

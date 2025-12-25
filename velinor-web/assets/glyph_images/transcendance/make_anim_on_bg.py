#!/usr/bin/env python3
"""Generate animated GIF of the pulsing/bobbing glyph composited onto a background.
Outputs: transcendance_on_boss_chamber.gif in the same folder.
"""
from PIL import Image, ImageFilter, ImageEnhance
import math
import os

HERE = os.path.dirname(__file__)
GLYPH = os.path.join(HERE, 'triglyph.png')
BACKGROUND = os.path.join(HERE, '..', '..', 'backgrounds', 'boss_chamber01.png')
OUT_GIF = os.path.join(HERE, 'transcendance_on_boss_chamber.gif')

# Parameters
frames = 36
fps = 12
duration_ms = int(1000 / fps)
bob_amp = 10            # pixels vertical bob amplitude
scale_amp = 0.035       # scale amplitude (fraction)
glow_max_radius = 26    # blur radius for glow
glow_color = (140, 190, 255)  # RGB glow color
glyph_width_frac = 0.28  # glyph width relative to background width

if not os.path.exists(GLYPH):
    raise SystemExit(f"Glyph not found: {GLYPH}")
if not os.path.exists(BACKGROUND):
    raise SystemExit(f"Background not found: {BACKGROUND}")

bg = Image.open(BACKGROUND).convert('RGBA')
bg_w, bg_h = bg.size

base = Image.open(GLYPH).convert('RGBA')
# target glyph width
target_w = int(bg_w * glyph_width_frac)
scale_base = target_w / base.width
base_scaled = base.resize((int(base.width * scale_base), int(base.height * scale_base)), Image.LANCZOS)

frames_list = []
for i in range(frames):
    t = i / frames  # 0..1
    bob = math.sin(t * 2 * math.pi) * bob_amp
    pulse = (math.sin(t * 2 * math.pi - math.pi/2) + 1) / 2
    scale = 1.0 + (pulse - 0.5) * 2 * scale_amp

    # scaled glyph for this frame
    scaled = base_scaled.resize((int(base_scaled.width * scale), int(base_scaled.height * scale)), Image.LANCZOS)

    # create glow from alpha
    alpha = scaled.split()[3]
    glow = Image.new('RGBA', scaled.size, glow_color + (0,))
    # make glow alpha stronger with pulse
    glow_alpha = ImageEnhance.Brightness(alpha).enhance(0.6 + pulse * 1.2)
    glow.putalpha(glow_alpha)
    glow = glow.filter(ImageFilter.GaussianBlur(radius=glow_max_radius * (0.6 + pulse * 0.6)))

    # composite onto a copy of background
    frame = bg.copy()
    # center position (x,y), apply bob to y
    x = (bg_w - scaled.width) // 2
    y = int((bg_h - scaled.height) // 2 - bob)

    # paste glow and glyph
    frame.paste(glow, (x, y), glow)
    frame.paste(scaled, (x, y), scaled)

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

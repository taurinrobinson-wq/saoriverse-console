from PIL import Image, ImageDraw

W, H = 2048, 1365
overlay = Image.new('RGBA', (W, H), (0,0,0,0))
draw = ImageDraw.Draw(overlay)

import random
random.seed(42)

# draw rubble clusters: semi-transparent dark polygons
for i in range(40):
    x = random.randint(int(W*0.1), int(W*0.9))
    y = random.randint(int(H*0.5), int(H*0.95))
    scale = random.uniform(0.03, 0.15)
    w = int(W*scale)
    h = int(H*scale*0.6)
    # polygon
    points = [(x + random.randint(-w,w), y + random.randint(-h,h)) for _ in range(6)]
    alpha = random.randint(140, 220)
    color = (30, 20, 15, alpha)
    draw.polygon(points, fill=color)

# draw dust layer: translucent noise-like ellipses
for i in range(200):
    x = random.randint(0, W)
    y = random.randint(int(H*0.3), H)
    r = random.randint(10, 120)
    alpha = random.randint(6, 26)
    color = (120, 100, 80, alpha)
    draw.ellipse((x-r, y-r, x+r, y+r), fill=color)

# save
overlay_fp = 'velinor/art/overlays/collapse_overlay.png'
overlay.save(overlay_fp)
print('Wrote overlay to', overlay_fp)

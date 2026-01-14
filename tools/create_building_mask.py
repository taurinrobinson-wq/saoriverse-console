from PIL import Image, ImageDraw

# Create a coarse mask for old_city_center_forest.png
# White = area to inpaint (collapsed building), black = keep
src = 'velinor/backgrounds/old_city_center_forest.png'
mask_out = 'velinor/art/masks/old_city_center_forest_building_mask.png'

im = Image.open(src).convert('RGBA')
w,h = im.size
mask = Image.new('L', (w,h), 0)
d = ImageDraw.Draw(mask)

# Heuristic polygon focusing on right-side upper building area
# Coordinates are relative fractions -> tune if needed
poly = [
    (int(w*0.62), int(h*0.15)),
    (int(w*0.95), int(h*0.12)),
    (int(w*0.95), int(h*0.65)),
    (int(w*0.7), int(h*0.72)),
    (int(w*0.62), int(h*0.45))
]

d.polygon(poly, fill=255)
# soften edges by blur (optional) - use a small radius
try:
    from PIL import ImageFilter
    mask = mask.filter(ImageFilter.GaussianBlur(radius=int(min(w,h)*0.01)))
except Exception:
    pass

mask.save(mask_out)
print('Wrote mask:', mask_out)

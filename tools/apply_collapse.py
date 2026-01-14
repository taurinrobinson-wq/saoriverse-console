from PIL import Image, ImageEnhance, ImageFilter

bg_path = 'velinor/backgrounds/old_city_center_forest.png'
overlay_path = 'velinor/art/overlays/collapse_overlay.png'
out_path = 'velinor/backgrounds/old_city_center_forest_collapsed.png'

bg = Image.open(bg_path).convert('RGBA')
# desaturate
converter = ImageEnhance.Color(bg)
bg = converter.enhance(0.45)
# darken
enh = ImageEnhance.Brightness(bg)
bg = enh.enhance(0.7)
# slight blur
bg = bg.filter(ImageFilter.GaussianBlur(radius=1.2))

# open overlay and resize to background if needed
ol = Image.open(overlay_path).convert('RGBA')
if ol.size != bg.size:
    ol = ol.resize(bg.size, resample=Image.LANCZOS)

# composite: paste overlay using alpha
result = Image.alpha_composite(bg, ol)
# subtle vignette: darken edges
w,h = result.size
vignette = Image.new('L', (w,h), 0)
from PIL import ImageDraw
vd = ImageDraw.Draw(vignette)
vd.ellipse((-int(w*0.2), -int(h*0.2), int(w*1.2), int(h*1.2)), fill=255)
# invert vignette to use as mask of darkening center
v = vignette.filter(ImageFilter.GaussianBlur(radius=int(min(w,h)*0.12)))
# darken with mask
dark = Image.new('RGBA', (w,h), (0,0,0,40))
result = Image.composite(result, Image.alpha_composite(result, dark), v.convert('L'))

result.save(out_path)
print('Wrote collapsed background:', out_path)

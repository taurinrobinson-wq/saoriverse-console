from PIL import Image, ImageFilter, ImageOps
import os, math

INPUTS = [
    "velinor/overlays/devil_cards/hell_world.png",
    "velinor/overlays/devil_cards/hunger_world.png",
]
CLEAN_DIR = "velinor/overlays/devil_cards/cleaned"
GIF_DIR = "velinor/overlays/devil_cards/gifs"
os.makedirs(CLEAN_DIR, exist_ok=True)
os.makedirs(GIF_DIR, exist_ok=True)

# copy of functions from generate_card_gifs
from PIL import ImageDraw, ImageFont

def color_distance(c1, c2):
    return math.sqrt(sum((a-b)**2 for a,b in zip(c1,c2)))


def detect_background_color(im: Image.Image, edge_px=6):
    w,h = im.size
    pixels = im.load()
    samples = []
    # sample border strips
    for x in range(w):
        for y in range(edge_px):
            samples.append(pixels[x,y][:3])
        for y in range(h-edge_px, h):
            samples.append(pixels[x,y][:3])
    for y in range(h):
        for x in range(edge_px):
            samples.append(pixels[x,y][:3])
        for x in range(w-edge_px, w):
            samples.append(pixels[x,y][:3])
    # compute median per channel
    rs = sorted([s[0] for s in samples])
    gs = sorted([s[1] for s in samples])
    bs = sorted([s[2] for s in samples])
    mid = len(samples)//2
    return (rs[mid], gs[mid], bs[mid])


def remove_background(im: Image.Image, bg_color, tol=40):
    im = im.convert('RGBA')
    px = im.load()
    w,h = im.size
    for y in range(h):
        for x in range(w):
            r,g,b,a = px[x,y]
            if color_distance((r,g,b), bg_color) <= tol:
                px[x,y] = (r,g,b,0)
    # optional cleanup: trim and smooth alpha
    im = im.filter(ImageFilter.GaussianBlur(0))
    return im


def trim_alpha(im: Image.Image) -> Image.Image:
    if im.mode in ("RGBA", "LA") or ("A" in im.getbands()):
        alpha = im.split()[-1]
        bbox = alpha.getbbox()
        if bbox:
            return im.crop(bbox)
    return im

# reuse GIF makers from generator
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from generate_card_gifs import make_flip_frames, make_hover_frames, make_tap_frames, save_gif

if __name__ == '__main__':
    for inp in INPUTS:
        if not os.path.exists(inp):
            print('Missing', inp)
            continue
        im = Image.open(inp).convert('RGBA')
        bg = detect_background_color(im, edge_px=max(4, min(im.size)//50))
        cleaned = remove_background(im, bg, tol=38)
        base = os.path.splitext(os.path.basename(inp))[0]
        out_clean = os.path.join(CLEAN_DIR, f"{base}_clean.png")
        cleaned.save(out_clean)
        print('Wrote cleaned image', out_clean)
        # normalize size as generator does
        max_h = 420
        w,h = cleaned.size
        if h > max_h:
            new_w = int(w * (max_h / h))
            cleaned = cleaned.resize((new_w, max_h), resample=Image.LANCZOS)
        # create GIFs
        flip = make_flip_frames(cleaned, frames=12)
        hover = make_hover_frames(cleaned, frames=10)
        tap = make_tap_frames(cleaned, frames=10)
        out_flip = os.path.join(GIF_DIR, f"{base}_clean_flip.gif")
        out_hover = os.path.join(GIF_DIR, f"{base}_clean_hover.gif")
        out_tap = os.path.join(GIF_DIR, f"{base}_clean_tap.gif")
        save_gif(flip, out_flip, duration=45)
        save_gif(hover, out_hover, duration=60)
        save_gif(tap, out_tap, duration=90)
        print('Wrote cleaned GIFs for', base, out_flip, out_hover, out_tap)

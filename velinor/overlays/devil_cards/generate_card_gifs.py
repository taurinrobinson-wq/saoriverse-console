from PIL import Image, ImageDraw, ImageFilter
from PIL import ImageFont
import os

# Input files (relative to repo root)
INPUTS = [
    "velinor/overlays/devil_cards/hell_world.png",
    "velinor/overlays/devil_cards/hunger_world.png",
]
OUT_DIR = "velinor/overlays/devil_cards/gifs"

os.makedirs(OUT_DIR, exist_ok=True)


def trim_alpha(im: Image.Image) -> Image.Image:
    if im.mode in ("RGBA", "LA") or ("A" in im.getbands()):
        alpha = im.split()[-1]
        bbox = alpha.getbbox()
        if bbox:
            return im.crop(bbox)
    return im


def make_backcard(size, label):
    w, h = size
    back = Image.new("RGBA", (w, h), (30, 30, 30, 255))
    d = ImageDraw.Draw(back)
    # simple centered label
    text = label
    font = ImageFont.load_default()
    bbox = d.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    d.text(((w - text_w) / 2, (h - text_h) / 2), text, fill=(220, 220, 220, 255), font=font)
    return back


def make_flip_frames(im: Image.Image, frames=10):
    w, h = im.size
    back = make_backcard((w, h), "Back")
    seq = []
    # shrink to middle, swap to back, expand
    for i in range(frames // 2):
        t = 1 - (i / max(1, (frames // 2 - 1)))
        scale = max(0.02, t)
        new_w = max(1, int(w * scale))
        frame = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        img_scaled = im.resize((new_w, h), resample=Image.LANCZOS)
        x = (w - new_w) // 2
        frame.paste(img_scaled, (x, 0), img_scaled)
        seq.append(frame)
    # middle frame: tiny width showing back
    seq.append(back)
    for i in range(frames // 2):
        t = i / max(1, (frames // 2 - 1))
        scale = max(0.02, t)
        new_w = max(1, int(w * scale))
        frame = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        img_scaled = im.resize((new_w, h), resample=Image.LANCZOS)
        x = (w - new_w) // 2
        frame.paste(img_scaled, (x, 0), img_scaled)
        seq.append(frame)
    return seq


def make_hover_frames(im: Image.Image, frames=8):
    w, h = im.size
    seq = []
    for i in range(frames):
        t = (i / (frames - 1))
        # scale between 1.0 and 1.06 and back
        if t <= 0.5:
            s = 1.0 + 0.06 * (t / 0.5)
        else:
            s = 1.06 - 0.06 * ((t - 0.5) / 0.5)
        new_w = int(w * s)
        new_h = int(h * s)
        img_scaled = im.resize((new_w, new_h), resample=Image.LANCZOS)
        frame = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        x = (w - new_w) // 2
        y = (h - new_h) // 2
        # soft shadow
        shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sh = Image.new("RGBA", img_scaled.size, (0, 0, 0, 120))
        shadow.paste(sh, (x + 6, y + 6), sh)
        shadow = shadow.filter(ImageFilter.GaussianBlur(4))
        frame = Image.alpha_composite(frame, shadow)
        frame.paste(img_scaled, (x, y), img_scaled)
        seq.append(frame)
    return seq


def make_tap_frames(im: Image.Image, frames=6):
    w, h = im.size
    seq = []
    for i in range(frames):
        t = i / (frames - 1)
        # quick squish down then back up
        if t <= 0.5:
            s = 1.0 - 0.08 * (t / 0.5)
            ty = int(6 * (t / 0.5))
        else:
            s = 0.92 + 0.08 * ((t - 0.5) / 0.5)
            ty = int(6 * (1 - ((t - 0.5) / 0.5)))
        new_w = int(w * s)
        new_h = int(h * s)
        img_scaled = im.resize((new_w, new_h), resample=Image.LANCZOS)
        frame = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        x = (w - new_w) // 2
        y = (h - new_h) // 2 + ty
        frame.paste(img_scaled, (x, y), img_scaled)
        seq.append(frame)
    return seq


def save_gif(frames, outpath, duration=60, loop=0):
    if not frames:
        return
    # GIF only supports single-color transparency and no partial alpha.
    # To avoid visible magenta fringes from semi-transparent edges, composite
    # each frame onto a matte color sampled from the image border (this
    # matches the background where the card will be used), then quantize to a
    # shared palette and save with no magenta marker.
    def sample_matte_color(rgba_img):
        w, h = rgba_img.size
        px = rgba_img.load()
        samples = []
        # look a few pixels inward from edges for opaque pixels
        margin = max(2, min(w, h) // 50)
        for x in range(w):
            for y in range(margin):
                r,g,b,a = px[x,y]
                if a > 0:
                    samples.append((r,g,b))
            for y in range(h-margin, h):
                r,g,b,a = px[x,y]
                if a > 0:
                    samples.append((r,g,b))
        for y in range(h):
            for x in range(margin):
                r,g,b,a = px[x,y]
                if a > 0:
                    samples.append((r,g,b))
            for x in range(w-margin, w):
                r,g,b,a = px[x,y]
                if a > 0:
                    samples.append((r,g,b))
        if not samples:
            return (0,0,0)
        rs = sum([s[0] for s in samples]) // len(samples)
        gs = sum([s[1] for s in samples]) // len(samples)
        bs = sum([s[2] for s in samples]) // len(samples)
        return (rs, gs, bs)

    matte = sample_matte_color(frames[0].convert('RGBA'))

    def to_paletted_with_matte(f):
        rgba = f.convert('RGBA')
        bg = Image.new('RGBA', rgba.size, matte + (255,))
        comp = Image.alpha_composite(bg, rgba)
        return comp.convert('P', palette=Image.ADAPTIVE, dither=0)

    pal_frames = [to_paletted_with_matte(fr) for fr in frames]
    pal_frames[0].save(outpath, save_all=True, append_images=pal_frames[1:], duration=duration, loop=loop, disposal=2)


if __name__ == '__main__':
    for inp in INPUTS:
        if not os.path.exists(inp):
            print(f"Missing input: {inp}")
            continue
        im = Image.open(inp).convert("RGBA")
        im = trim_alpha(im)
        base = os.path.splitext(os.path.basename(inp))[0]
        # Normalize size to max height 420 while preserving aspect
        max_h = 420
        w, h = im.size
        if h > max_h:
            new_w = int(w * (max_h / h))
            im = im.resize((new_w, max_h), resample=Image.LANCZOS)
            w, h = im.size
        # create outputs
        flip = make_flip_frames(im, frames=12)
        hover = make_hover_frames(im, frames=10)
        tap = make_tap_frames(im, frames=10)
        out_flip = os.path.join(OUT_DIR, f"{base}_flip.gif")
        out_hover = os.path.join(OUT_DIR, f"{base}_hover.gif")
        out_tap = os.path.join(OUT_DIR, f"{base}_tap.gif")
        save_gif(flip, out_flip, duration=45)
        save_gif(hover, out_hover, duration=60)
        save_gif(tap, out_tap, duration=90)
        print(f"Wrote GIFs for {base}:", out_flip, out_hover, out_tap)

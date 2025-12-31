Optimize assets (boss sprites)

This repository ships the original high-resolution boss sprites under `velinor/bosses/`.
To reduce bytes on disk / network while keeping the boss larger on-screen, create lower-resolution recompressed images and place them in `velinor-web/public/velinor/bosses/`.

Quick steps:

1. From the project root, install `sharp` (Node.js):

```bash
cd velinor-web
npm install sharp
```

2. Run the optimization script (created at `velinor-web/scripts/optimize-assets.js`):

```bash
node scripts/optimize-assets.js
```

This script will:
- Read files from `../velinor/bosses/` matching `triglyph_boss*`.
- Resize them to a maximum width (default 800px) and recompress as JPEG (quality 72).
- Write results into `velinor-web/public/velinor/bosses/` as `.jpg` files.

Notes:
- After running, update `BossFight.tsx` if you want to reference the `.jpg` low-res files explicitly (the component currently points to PNGs; browsers will still load the PNG if present). You can replace URLs like `/velinor/bosses/triglyph_boss_nobg_forward2.png` with `/velinor/bosses/triglyph_boss_nobg_forward2.jpg` to force the smaller files.
- Adjust `MAX_WIDTH` and `JPG_QUALITY` in `scripts/optimize-assets.js` to tune filesize vs quality.
- Consider committing optimized files to the repo or adding them to your CI/publish pipeline to avoid running this step locally on every machine.

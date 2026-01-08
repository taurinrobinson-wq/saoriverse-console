// optimize-assets.js
// Downscale and recompress boss images to reduce file size while allowing them
// to be displayed larger on-screen via CSS scaling.
// Usage: npm install sharp && node scripts/optimize-assets.js

const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

const SRC_DIR = path.join(__dirname, '..', '..', 'velinor', 'bosses');
const OUT_DIR = path.join(__dirname, '..', 'public', 'velinor', 'bosses');

const MAX_WIDTH = 800; // target max width in px for low-res versions
const JPG_QUALITY = 72; // jpeg quality

if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });

async function processFile(file) {
    const inPath = path.join(SRC_DIR, file);
    const outPath = path.join(OUT_DIR, file);
    try {
        const img = sharp(inPath);
        const metadata = await img.metadata();
        if (!metadata.width) {
            console.warn('Skipping (no width):', file);
            return;
        }
        const targetWidth = Math.min(metadata.width, MAX_WIDTH);
        await img
            .resize({ width: targetWidth })
            .jpeg({ quality: JPG_QUALITY, mozjpeg: true })
            .toFile(outPath.replace(/\.[a-zA-Z]+$/, '.jpg'));
        console.log('Wrote', outPath.replace(/\.[a-zA-Z]+$/, '.jpg'));
    } catch (err) {
        console.error('Failed:', file, err.message);
    }
}

(async () => {
    const entries = fs.readdirSync(SRC_DIR).filter(f => /triglyph_boss/i.test(f));
    for (const f of entries) await processFile(f);
    console.log('Done optimizing boss assets.');
})();

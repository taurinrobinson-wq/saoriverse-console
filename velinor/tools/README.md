# Video grading helper — Velinor aesthetic

This folder contains a small helper script `grade_video.sh` that applies a muted, slightly somber aesthetic to source videos so they fit the Velinor visual tone.

Recommended adjustments applied by default:
- lower saturation (default 0.6)
- slight darkening (brightness -0.03)
- small contrast tweak (1.02)
- vignette to darken edges
- film grain (default 12)

Usage:

```bash
cd velinor/tools
./grade_video.sh ../assets/videos/sealina_final.mp4 ../assets/videos/sealina_final_grade.mp4
```

Custom parameters (optional):

```bash
# saturation brightness contrast grain
./grade_video.sh in.mp4 out.mp4 0.55 -0.04 1.05 14
```

Notes & tips:
- This script requires `ffmpeg` on PATH. On Debian/Ubuntu: `sudo apt install ffmpeg`.
- If you need more precise color grading, create or use a 3D LUT and apply with `-vf lut3d=file.cube`.
- Consider rendering to a high bitrate/quality, then run a secondary compressor if you need smaller files.
- If the source video looks too dull, reduce the vignette radius or lower grain.

Using a 3D LUT (Velinor palette):

We include a small example LUT `velinor_palette.cube` that applies a subtle tint and desaturation tuned for Velinor. Use it like:

```bash
./grade_video.sh ../assets/videos/tessa_intro.mp4 ../assets/videos/tessa_intro_grade.mp4 0.6 -0.03 1.02 12 velinor_palette.cube
```

Notes about the LUT:
- The provided `velinor_palette.cube` is a tiny 2x2x2 LUT for quick testing. For production, generate a larger, higher-precision LUT (17x17x17 or 33x33x33) using a color grading tool.
- To apply more precise color grading, create a 3D LUT in your grading app (DaVinci Resolve, Photoshop Camera Raw, etc.) and pass its `.cube` path to the script as the 7th argument.


**Glyph Codex Assets**
- **Location:** assets/glyph_codex/
- **Files added:**
  - codex_frame.svg : Base codex frame with transparent screen area. Place glyph artwork centered at (512,400) within a ~300x300px area.
  - arrow_left.svg / arrow_right.svg : Navigation buttons sized 128x128. Designed to be placed over left/right placeholders in the codex frame.
  - glyph_placeholder.svg : Example floating glyph (SVG) with glow. Replace with your glyph artworks.

Usage notes:
- The SVGs are vector; export to PNG at any desired size (e.g., 512x512, 1024x1024) with a raster tool or an automated export script.
- For the codex frame, render glyph artwork centered at the coordinates above so it appears on the black screen area.
- The left/right arrow SVGs can be placed into the left/right button rectangles or exported separately as UI elements.

If you want, I can:
- Export PNG variants at specific sizes (e.g., 512, 1024) and add them to the repo.
- Create pressed/disabled states for the arrow buttons.
- Render a composed preview (console image + glyph over screen) to show final look.

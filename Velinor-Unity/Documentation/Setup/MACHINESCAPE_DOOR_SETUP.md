# MachinesCave Door Sequence Setup Guide

## Current State
You now have the foundation for the door puzzle sequence:

### What's Set Up:
1. **PanelInteraction.cs** - Detects player proximity to panel, shows "Press E to access panel" prompt
2. **CodexController.cs** - Updated to load and display glyphs from GlyphsDatabase
3. **GlyphsDatabase.cs** - Central system for managing available glyphs
4. **GlyphSelectable.cs** - Updated to allow dynamic glyph assignment
5. **GlyphPlacementManager.cs** - Waits for 3 glyphs to be placed to open door

---

## Next Steps: Configure Glyphs for Testing

### Option 1: Inspector Setup (Easiest for Testing)
1. **Create** an empty GameObject in your scene called "GlyphsDatabase"
2. **Add Component**: GlyphsDatabase script
3. In the Inspector, expand the "Available Glyphs" list
4. **Add 3 glyphs** from your archived collection:
   - glyph_Sorrow_nobg.png
   - glyph_Remembrance_nobg.png
   - glyph_Covenant_Flame_nobg.png
5. Drag each sprite into the "Sprite" field
6. Save the scene

### Available Glyphs in `Assets/Graphics/Glyphs/archived_full-color_glyphs/`:
- Glyph_Ancestral_Record_nobg.png
- glyph_Covenant_Flame_nobg.png
- glyph_Echoed_Breath_nobg.png
- glyph_Echo_Communion_nobg.png
- Glyph_Infrasensory_Oblivion_nobg.png
- Glyph_legacy_blue_nobg.png
- Glyph_legacy_nobg.png
- glyph_primal_Oblivion_nobg.png
- glyph_Remembrance_nobg.png
- glyph_Remembrance_nobg2.png
- glyph_Returning_Song_nobg.png
- glyph_Sensory_Oblivion_nobg.png
- glyph_shared_burden_3.png
- glyph_sorrow_nobg.png
- glyph_sorrow_nobg2.png

---

## Testing the Sequence

1. **Play the scene** (MachinesCave_00)
2. **Walk to the panel** on the right side of the door
3. **Press E** when in range - you should see:
   - "Press E to access panel" prompt appears
   - TrigglyphPanel pops up
   - Codex opens showing your configured glyphs
4. **Click a glyph** to select it
5. **Place 3 glyphs** total to trigger door opening

---

## Scene Wiring Checklist

- [ ] GlyphsDatabase created with 3+ glyphs assigned
- [ ] PanelInteraction collider positioned at panel location
- [ ] PanelInteraction references:
  - [ ] triglyphPanelUI assigned
  - [ ] codexUI assigned (UI_Canvas)
  - [ ] interactionPrompt assigned (text element)
- [ ] GlyphPlacementManager assigned references for overlays/door animation
- [ ] Player has "Player" tag
- [ ] Panel area has trigger collider with correct layer/tag setup

---

## Future Improvements

When you're happy with the basic sequence, you can:
- **Animate** the door opening
- **Add sound effects** for glyph placement
- **Create specific glyph requirements** (only certain glyphs unlock the door)
- **Add visual feedback** when glyphs are placed on the panel
- **Tie to story progression** (glyphs change based on game state)

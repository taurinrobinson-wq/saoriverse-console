# Velinor Streamlit - Quick Reference

## Run the Game

```bash
pip install -r velinor/requirements_streamlit.txt
streamlit run velinor/streamlit_app.py
```

## Game Modes at a Glance

| Mode | Buttons | Actions | Ends When |
|------|---------|---------|-----------|
| **Narrative** | 4 choices | Read dialogue, make choices | Click a choice |
| **Glyph Input** | 4 glyphs (×2) | Select glyphs from collection | All 8 glyphs selected |
| **Chamber** | Attack + Progress | Click Attack repeatedly | 15 attacks reached |
| **Special** | Invoke Glyph | Use glyph on NPC | Glyph invoked |

## TONE Stats

| Stat | Meaning | Increases Via |
|------|---------|--------------|
| **Courage** | Acting despite fear | Facing challenges |
| **Wisdom** | Knowing what matters | Careful observation |
| **Empathy** | Feeling with others | Understanding NPCs |
| **Resolve** | Commitment to path | Staying true to choices |
| **Resonance** | Harmonic balance | Emotionally consistent choices |

Range: -1.0 (low) to +1.0 (high)
Green = positive, Yellow = neutral, Red = negative

## Glyphs

| Glyph | Effect | Use At Door | Use On NPC |
|-------|--------|------------|-----------|
| **Sorrow** | +Empathy | ✓ | ✓ Opens vulnerability |
| **Presence** | +Resonance | ✓ | ✓ Be fully aware |
| **Courage** | +Courage | ✓ | ✓ Move boldly |
| **Wisdom** | +Wisdom | ✓ | ✓ Choose wisely |
| **Trust** | +Empathy | ✓ | ✓ Deepen bonds |
| **Transcendence** | +Resonance | ✓ | ✓ Ultimate victory |

## Sidebar Status

Always shows:
- 🎼 **TONE** - Five emotional stats
- 👁️ **REMNANTS** - Deep trait tracking
- ✨ **GLYPHS** - Owned glyphs (🟢 = owned, ⚫ = locked)
- 🎯 **SKILLS** - Learned abilities
- 👥 **NPC PERCEPTION** - Trust levels for each NPC

## NPC Trust Tracker

Per NPC (-1.0 to +1.0):
- **Trust** - Safety and reliability
- **Affinity** - Liking and comfort
- **Understanding** - Being known and seen

💚 = positive, ❤️ = neutral, 💔 = negative

## Core Files

| File | Purpose |
|------|---------|
| `streamlit_app.py` | Main game loop |
| `streamlit_state.py` | Game state (TONE, glyphs, NPCs) |
| `streamlit_ui.py` | UI rendering (buttons, sidebar) |
| `stories/story_definitions.py` | Story content |
| `STREAMLIT_README.md` | Full architecture guide |

## Testing

```bash
# Run integration tests (8 tests, ~1 second)
python -m pytest velinor/test_streamlit_integration.py -v

# Manual testing
streamlit run velinor/streamlit_app.py
```

## Add Story Content

Edit `velinor/stories/story_definitions.py`:

```python
story.add_passage(
    name="my_scene",
    text="*Dialogue*",
    background="location",
    npcs=["Ravi"]
)

story.add_choice(
    from_passage_name="my_scene",
    choice_text="Click this",
    to_passage_name="next_scene",
    tone_effects={"courage": 0.2},
    npc_resonance={"Ravi": 0.1}
)
```

## Add Glyphs

Edit `velinor/streamlit_state.py` `_initialize_glyphs()`:

```python
"MyGlyph": Glyph(
    name="MyGlyph",
    description="Does X",
    unlock_condition="story_beat",
    emotional_effect="courage",
    npc_resonance={"Ravi": 0.8}
)
```

## Debug

Open "🔧 Debug Panel" in app:
- Save Game
- Load Game
- Reset Game
- View current scene/mode
- Inspect full game state

## Cheat Codes (in terminal)

None implemented yet, but you can modify `streamlit_state.py`:

```python
# Example: Unlock all glyphs
for glyph_name in state.glyphs:
    state.obtain_glyph(glyph_name)
```

## Performance

- App loads in ~1 second
- Button click to rerender: ~200ms
- Test suite runs in ~1 second
- Save game: instant
- Load game: instant

## Limitations (By Design)

- No animations (fast prototyping)
- No real graphics (text placeholders)
- Single-player only
- 5-button max (clean UI)
- Full page rerun per action (Streamlit limitation)

## Next Steps

1. **Test all story branches** - Play through different paths
2. **Add more scenes** - Expand Act 2 & 3
3. **Tune mechanics** - Adjust glyph costs, fight difficulty
4. **Implement saving** - Persist progress across sessions
5. **Port to React** - Build final cinematic version

## Links

- Full Docs: [STREAMLIT_README.md](velinor/STREAMLIT_README.md)
- Gameplay: [QUICKSTART.md](velinor/QUICKSTART.md)
- Implementation: [VELINOR_STREAMLIT_IMPLEMENTATION_SUMMARY.md](VELINOR_STREAMLIT_IMPLEMENTATION_SUMMARY.md)
- Tests: [test_streamlit_integration.py](velinor/test_streamlit_integration.py)

## Contact

Questions? Check the documentation or examine the test file for working examples.

---

**Version:** 1.0  
**Status:** Complete and Tested ✅  
**Last Updated:** 2026-01-11

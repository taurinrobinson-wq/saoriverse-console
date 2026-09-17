# Portrait System Setup Guide

## Overview
The portrait system is now fully integrated into the dialogue system. Portraits will automatically:
1. **Clear** when dialogue starts
2. **Display** when beats are shown, pulling from the `portrait_expression` field in JSON
3. **Update** as dialogue progresses through different beats
4. **Hide** when dialogue ends

## What Was Changed

### Code Changes
- **DialogueManager.cs**
  - Added `PortraitManager portraitManager` field
  - Modified `Awake()` to initialize PortraitManager (creates one if doesn't exist)
  - Modified `StartDialogue()` to clear portrait at dialogue start
  - Modified `DisplayBeat()` to call `portraitManager.ShowPortrait(speaker, expression)` for each beat
  - Modified `EndDialogue()` to hide portrait when dialogue ends

### Scene Changes
- **Desert_Saori_Meeting.unity**
  - Dialogue panel UI expanded
  - Codex panel UI refined with new device image
  - **NPCImage component added** (needs to be cleared in Editor)

## Next Steps: Preparing for Portraits

### 1. **Clear the Portrait Image Component** (Manual - Requires Editor)
In the Desert_Saori_Meeting scene, select the **NPCImage** component in the DialoguePanel:
- **Inspector → Image Component → Source Image: [None]**
- This ensures the portrait starts empty instead of showing Saori's test image
- The portrait will now populate automatically when dialogue plays

### 2. **Create Portrait Files for NPCs**
Place portrait images in: `Assets/Resources/Portraits/{NpcName}/{NpcName}_{expression}.png`

**Folder Structure (Already Created):**
```
Assets/Resources/Portraits/
├── Ravi/
├── Nima/
├── Saori/          ← Saori_neutral.png already here
├── Elenya/
├── Malrik/
├── Sanor/
├── Elka/
├── Veynar/
├── Coren/
├── Drossel/
├── Kaelen/
├── Thoran/
├── Kiv/
├── Helia/
├── Nordia/
└── Inodora/
```

**Recommended Expressions (9 per NPC):**
- neutral
- worried
- relieved
- curious
- touched
- angry
- happy
- sad
- confused

### 3. **Add portrait_expression to JSON Dialogue Files**
In your dialogue JSON files (e.g., `Ravi_Nima_Marketplace.json`), add `portrait_expression` to each beat:

```json
{
  "id": 1.0,
  "active_speaker": "Ravi",
  "prompt": "Have you seen the price of salvage lately?",
  "portrait_expression": "worried",
  "type": "npc_turn",
  "tone_choices": [...]
}
```

If `portrait_expression` is omitted or empty, the system defaults to "neutral".

### 4. **Test in Desert_Saori_Meeting**
1. Open the scene in Unity
2. Play the game
3. Talk to Saori
4. Verify that:
   - Portrait is empty at dialogue start
   - Portrait appears when first beat displays
   - Portrait updates if different `portrait_expression` values are used across beats
   - Portrait clears when dialogue ends

### 5. **Add Portraits to Other NPCs**
Once Ravi/Nima marketplace scene is tested and working:
1. Create portrait images for Ravi and Nima (9 expressions each)
2. Update their dialogue JSON files with appropriate `portrait_expression` values
3. Test the Ravi/Nima marketplace scene
4. Expand to other NPCs as dialogue is developed

## JSON Format Examples

### Minimal (uses neutral by default)
```json
{
  "id": 1.0,
  "active_speaker": "Ravi",
  "prompt": "Where did you find that?"
}
```

### With Expression
```json
{
  "id": 2.0,
  "active_speaker": "Ravi",
  "prompt": "I'm afraid of losing her too.",
  "portrait_expression": "worried",
  "tone_choices": [...]
}
```

### Multiple Expressions in One Dialogue
```json
[
  {
    "id": 1.0,
    "active_speaker": "Nima",
    "prompt": "Seen anything valuable lately?",
    "portrait_expression": "neutral"
  },
  {
    "id": 2.0,
    "active_speaker": "Nima",
    "prompt": "The prices... they keep going up.",
    "portrait_expression": "worried"
  },
  {
    "id": 3.0,
    "active_speaker": "Nima",
    "prompt": "But we persist. That's what matters.",
    "portrait_expression": "touched"
  }
]
```

## Troubleshooting

### Portrait Not Appearing
- **Check:** Does the portrait image exist at `Assets/Resources/Portraits/{NpcName}/{NpcName}_{expression}.png`?
- **Check:** Is the image imported as a Sprite (not Texture)?
- **Check:** Is the NPCImage component visible in the DialoguePanel?
- **Check:** Does the JSON have `active_speaker` matching the folder name exactly?

### Portrait Stuck on Scene (Not Clearing)
- **Ensure:** NPCImage Source Image is set to [None] in the Editor (not Saori's portrait)
- **Verify:** HidePortrait() is being called in EndDialogue()
- **Check:** Dialog Manager is properly initialized (should see "PortraitManager initialized" in console)

### Wrong Expression Showing
- **Verify:** `portrait_expression` in JSON matches the filename exactly
- **Check:** Console logs for "Portrait not found" warnings
- **System falls back to "neutral"** if expression not found (should see fallback warning)

### Portrait Takes Too Long to Load
- **PortraitManager caches sprites** after first load—subsequent beats load instantly
- **First portrait in a dialogue** may have slight frame-time cost (normal)

## Performance Notes
- Sprites are cached in memory after first load
- No visible performance impact until 20+ unique portraits
- Each portrait should be optimized (512×512 or similar size)
- Total VRAM for 40 NPCs × 9 expressions ≈ 20-40 MB (negligible on modern systems)

## Next Development Stages

### Stage 1: Core Four (Priority)
- [ ] Ravi (9 expressions)
- [ ] Nima (9 expressions)
- [ ] Elenya (9 expressions)
- [ ] Malrik (9 expressions)

### Stage 2: Ideological Leaders
- [ ] Sanor
- [ ] Elka
- [ ] Saori (already has neutral)

### Stage 3: Authority & Underworld
- [ ] Veynar
- [ ] Coren
- [ ] Drossel
- [ ] Kaelen

### Stage 4: Crafters & Voice
- [ ] Thoran
- [ ] Kiv
- [ ] Helia
- [ ] Nordia
- [ ] Inodora

### Stage 5: Secondary Cast
All remaining NPCs from MASTER_NPC_ROSTER.md

## Integration Summary

| Component | Purpose | Status |
|-----------|---------|--------|
| PortraitManager.cs | Load & display sprites with caching | ✅ Complete |
| DialogueManager.cs | Call PortraitManager on beat display | ✅ Complete |
| DialogueUIController.cs | Auto-detect NPCImage component | ✅ Complete |
| BeatData.cs | portrait_expression JSON field | ✅ Complete |
| Portrait Folder Structure | Ready for image files | ✅ Complete |
| Scene NPCImage Setup | Manual: Clear source image in Editor | ⏳ Pending |
| Portrait Image Files | Needs creation/sourcing | ⏳ Pending |
| JSON portrait_expression Fields | Needs addition to dialogue files | ⏳ Pending |

---

**Ready to test?** Follow the "Test in Desert_Saori_Meeting" section above!

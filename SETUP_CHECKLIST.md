# Persistent State System - Setup Checklist

## ✅ Code Changes (DONE)
- [x] Modified `GlyphPickup.cs` - adds GameFlags persistence
- [x] Expanded `DialogueManager.cs` - handles set_flag, movement_speed, diary_append
- [x] Added `SetMoveSpeed()` to `PlayerController2D5.cs`
- [x] Created `SceneStateController.cs` - NEW reusable script

## 🎮 Unity Setup (TODO - Do These in Editor)

### For Each Scene That Needs State Persistence:

#### 1. Add SceneStateController
- [ ] Open scene (e.g., InsideMarket_01)
- [ ] Select scene root GameObject (usually called "Scene" or empty root)
- [ ] Inspector → Add Component → SceneStateController
- [ ] Configure StateActions (see below)

#### 2. Configure State Actions for Willy Scene

**Action 1: Hide Willy after dialogue**
- Required Flag: `willy_dialogue_complete`
- Target: Willy (the NPC GameObject)
- Set Active: `☐` (unchecked = disabled/hidden)

**Action 2: Disable glyph after collection**
- Required Flag: `sorrow_glyph_collected`
- Target: GlyphPickup (or the glyph's root GameObject)
- Set Active: `☐` (unchecked = disabled)

#### 3. Update Dialogue JSON

**In your payment dialogue beat** (after player collects glyph), add system_triggers:

```json
{
  "system_triggers": [
    {
      "type": "set_flag",
      "data": ["willy_dialogue_complete", "true"]
    },
    {
      "type": "movement_speed",
      "data": ["0.5"]
    },
    {
      "type": "diary_append",
      "data": [
        "Met a scrapper named Willy in the Concourse Ruins. He was an odd character...laughing at suffering, coughing constantly...but helpful and not malicious. He helped me uncover the Glyph of Sorrow, though not without cost. Everything down here has a price.",
        "Willy Encounter"
      ]
    },
    {
      "type": "close_dialogue"
    }
  ]
}
```

### For All Scenes Using Glyphs:

Each scene that spawns a GlyphPickup should have a StateAction:

| Scene | Required Flag | Target | Set Active |
|-------|---|---|---|
| InsideMarket_01 | `sorrow_glyph_collected` | GlyphPickup_Sorrow | ☐ |
| Concourse_Ruins | `sorrow_glyph_collected` | GlyphPickup_Sorrow | ☐ |
| MachinesCave_00 | (any glyph collected flags) | (corresponding glyphs) | ☐ |

---

## 🧪 Testing Workflow

### Test 1: Glyph Persistence
1. Play game
2. Navigate to glyph location
3. Collect glyph
4. Observe glyph disappears
5. Return to same location (e.g., via menu or scene transition)
6. Glyph should STILL be gone ✓
7. Check Console: should see `[GlyphPickup] already collected, disabling`

### Test 2: Movement Speed Effect
1. Play game
2. Trigger Willy dialogue and complete payment beat
3. Observe player movement is slower (0.5x speed)
4. Transition to another scene
5. Return to Willy's location
6. Movement should still be slow (0.5x) ✓
7. Check Console: should see `[PlayerController2D5] Move speed changed to: 0.5`

### Test 3: MindLog Entry
1. Complete Willy encounter (collect glyph + dialogue)
2. Open Codex
3. Go to MindLog tab
4. "Willy Encounter" should appear in grid ✓
5. Single-click shows summary
6. Leave game and reload
7. Entry should still be there (if MindLogManager is DontDestroyOnLoad) ✓

### Test 4: NPC Visibility Persistence
1. After completing Willy dialogue
2. Transition to next scene (if you have one set up)
3. Check: Willy should be hidden in InsideMarket_01 ✓
4. Check Scene view or inspector: Willy GameObject should be inactive
5. Return to InsideMarket_01
6. Willy should still be hidden ✓

---

## 🐛 Troubleshooting

### Problem: Glyph still respawns
- Check: `GlyphPickup.cs` at Start() - should check GameFlags for `glyph_collected_*` flag
- Check: Console logs for "already collected"
- Action: Make sure GlyphPickup is up to date

### Problem: Speed doesn't change
- Check: Dialogue has `movement_speed` trigger with correct format
- Check: Console logs for "Move speed changed to"
- Action: Verify trigger data has float value (e.g., "0.5")

### Problem: NPC not hiding after dialogue
- Check: SceneStateController is on scene root
- Check: StateAction has correct flag name
- Check: Target GameObject is correctly assigned
- Check: Console logs from SceneStateController

### Problem: MindLog entry not showing
- Check: MindLogManager is DontDestroyOnLoad
- Check: Dialogue has `diary_append` trigger
- Check: MindLogManager singleton created successfully

---

## 📝 Important Notes

- **GameFlags** is static and persists automatically across scenes
- **MindLogManager** must be DontDestroyOnLoad to persist entries (it already is)
- **Movement speed** affects player immediately and persists in GameFlags
- **SceneStateController** runs once at Start() - it reads GameFlags state
- **Glyph persistence** is built into GlyphPickup - no extra setup needed beyond JSON flags

---

## 🚀 Next Steps After Setup

1. [ ] Add SceneStateController to all scenes
2. [ ] Configure StateActions for NPCs and glyphs
3. [ ] Update dialogue JSON files with system_triggers
4. [ ] Test persistence in each scene
5. [ ] Verify MindLog entries appear correctly
6. [ ] Test glyph count for MachinesCave_00 triglyph puzzle

---

## 📚 Reference Files

- Implementation Guide: `PERSISTENCE_IMPLEMENTATION_GUIDE.md`
- Architecture Inventory: `VELINOR_ARCHITECTURE_INVENTORY.md`
- This Checklist: `SETUP_CHECKLIST.md`

# NPC Visibility & Scene Stage System

## Overview
This system manages NPC appearance and disappearance in scene stages, particularly for `InsideMarket_00` which hosts multiple NPCs at different dialogue stages.

## InsideMarket_00 - NPC Stage Progression

### Stage 1: Initial Encounter
**Dialogue:** `ravi_nima_market_discovery.json`
**Active NPCs:** Ravi, Nima
**Trigger:** Scene load (default)
**Required Flags:** `met_saori == true`, `obtain_codex == true`
**On Dialogue End:**
- `disable_npc: Ravi`
- `disable_npc: Nima`
- `set_flag: ravi_nima_market_discovery_complete`

**Purpose:** Player meets Ravi and Nima in the market and learns about the sorrow glyph.

---

### Stage 2: Kaelen's Confession
**Dialogue:** `kaelen_confession_01.json`
**Active NPCs:** Kaelen
**Trigger:** After `willy_dialogue_complete` flag is set
**Required Flags:** `willy_dialogue_complete == true`, `kaelen_has_secret == true`
**On Dialogue End:**
- `disable_npc: Kaelen`
- `set_flag: kaelen_confessed`

**Purpose:** Player confronts Kaelen about his role in Ophina's death. Codex activates to track remembrance glyph.

---

### Stage 3: Nima Alone
**Dialogue:** `nima_encounter_01.json`
**Active NPCs:** Nima (alone)
**Trigger:** After `remembrance_glyph_obtained` + `sorrow_glyph_obtained` flags are set
**Required Flags:** `sorrow_glyph_obtained == true`, `remembrance_glyph_obtained == true`, `kaelen_confessed == true`
**On Dialogue End:**
- `disable_npc: Nima`
- `set_flag: nima_encounter_complete`
- `trigger_codex_pulse` (track legacy glyph)

**Purpose:** Player finds Nima mourning. She reveals Ophina's photograph and asks player to help carry her loss. Codex activates to track legacy glyph.

---

### Stage 4: Ravi's Discovery
**Dialogue:** `ravi_encounter_01.json`
**Active NPCs:** Ravi (alone)
**Trigger:** After `legacy_glyph_obtained` flag is set
**Required Flags:** `legacy_glyph_obtained == true`, `nima_encounter_complete == true`
**On Dialogue End:**
- Codex activates to track metallic panel location
- Leads to `MachinesCave_00_URP`

**Purpose:** Ravi describes finding the metallic panel on the mountainside. Player receives directions to the artifact vault entrance.

---

## System Trigger Format

### NPC Control Triggers

**Disable NPC:**
```json
{
  "type": "disable_npc",
  "key": "NPC_NAME",
  "note": "Optional description of why/when this happens"
}
```

**Enable NPC:**
```json
{
  "type": "enable_npc",
  "key": "NPC_NAME",
  "note": "Optional description"
}
```

### Flag Management

**Set Flag:**
```json
{
  "type": "set_flag",
  "key": "flag_name",
  "value": true,
  "note": "Optional description"
}
```

**Scene/Visual Triggers:**
```json
{
  "type": "show_sprite",
  "key": "ophina_photo",
  "duration": "until_scene_end",
  "note": "Display photo sprite for beat 6-7 inner thought"
}
```

---

## Scene Behavior Contract

When implementing the NPC Visibility system in your scene scripts:

1. **On Scene Awake:**
   - Load all NPC prefabs into scene
   - Query current flag state
   - Disable NPCs that don't meet `required_flags`
   - Show only NPCs with met conditions

2. **On Dialogue Complete:**
   - Execute system triggers in order
   - Run `disable_npc` triggers immediately
   - Set all flags
   - Record dialogue completion state

3. **On Scene Exit:**
   - NPC disable triggers should prevent NPCs from persisting
   - Flags remain set (used for stage progression on re-entry)

4. **On Scene Re-Entry:**
   - Only show NPCs matching current flag state
   - Skip any dialogue that's already been marked complete

---

## Implementation Checklist

### Scene Setup (Unity)
- [ ] Create NPC instances for all potential characters in InsideMarket_00
  - [ ] Ravi (disabled by default)
  - [ ] Nima (disabled by default)
  - [ ] Kaelen (disabled by default)
  - [ ] Willy (disabled - not in this scene)

- [ ] Each NPC needs `NPCVisibilityComponent`:
  ```csharp
  public List<string> RequiredFlags; // Must ALL be true
  public List<string> ForbiddenFlags; // Must ALL be false
  public string NpcId; // "Ravi", "Nima", etc.
  ```

### Dialogue Files
- [x] `ravi_nima_market_discovery.json` - NPC disable + completion flag
- [x] `willy_concourse_ruins.json` - Set `willy_dialogue_complete` flag
- [x] `kaelen_confession_01.json` - NPC disable + completion flag
- [x] `nima_encounter_01.json` - NPC disable + completion flag + codex pulse
- [ ] `ravi_encounter_01.json` - Requires `legacy_glyph_obtained` flag

### Flag Definitions
Required flags to be set throughout game:
- `met_saori` - Set after Desert_Saori_Meeting dialogue
- `obtain_codex` - Set when player first obtains codex
- `willy_dialogue_complete` - Set at end of willy_concourse_ruins.json
- `sorrow_glyph_obtained` - Set when player collects sorrow glyph
- `remembrance_glyph_obtained` - Set when player collects remembrance glyph
- `legacy_glyph_obtained` - Set when player collects legacy glyph
- `kaelen_confessed` - Set at end of kaelen_confession_01.json
- `nima_encounter_complete` - Set at end of nima_encounter_01.json
- `ravi_nima_market_discovery_complete` - Set at end of ravi_nima_market_discovery.json

---

## Example: InsideMarket_00 Scene Manager

```csharp
public class InsideMarket00Manager : MonoBehaviour
{
    private Dictionary<string, NPCDialogueDriver> npcs;
    private GameFlagManager flagManager;
    
    void Awake()
    {
        flagManager = FindObjectOfType<GameFlagManager>();
        npcs = new Dictionary<string, NPCDialogueDriver>();
        
        // Collect all NPCs in this scene
        foreach(var npc in GetComponentsInChildren<NPCDialogueDriver>())
        {
            npcs[npc.npcId] = npc;
        }
        
        UpdateNPCVisibility();
    }
    
    private void UpdateNPCVisibility()
    {
        if (flagManager.GetFlag("legacy_glyph_obtained"))
        {
            // Stage 4: Only Ravi
            SetNPCActive("Ravi", true);
            SetNPCActive("Nima", false);
            SetNPCActive("Kaelen", false);
        }
        else if (flagManager.GetFlag("nima_encounter_complete"))
        {
            // Between Stage 3 and 4: No one
            SetNPCActive("Ravi", false);
            SetNPCActive("Nima", false);
            SetNPCActive("Kaelen", false);
        }
        else if (flagManager.GetFlag("remembrance_glyph_obtained"))
        {
            // Stage 3: Only Nima
            SetNPCActive("Ravi", false);
            SetNPCActive("Nima", true);
            SetNPCActive("Kaelen", false);
        }
        else if (flagManager.GetFlag("willy_dialogue_complete"))
        {
            // Stage 2: Only Kaelen
            SetNPCActive("Ravi", false);
            SetNPCActive("Nima", false);
            SetNPCActive("Kaelen", true);
        }
        else if (flagManager.GetFlag("ravi_nima_market_discovery_complete"))
        {
            // Between Stage 1 and 2: No one
            SetNPCActive("Ravi", false);
            SetNPCActive("Nima", false);
            SetNPCActive("Kaelen", false);
        }
        else
        {
            // Stage 1: Ravi and Nima
            SetNPCActive("Ravi", true);
            SetNPCActive("Nima", true);
            SetNPCActive("Kaelen", false);
        }
    }
    
    private void SetNPCActive(string npcId, bool active)
    {
        if (npcs.TryGetValue(npcId, out var npc))
        {
            npc.gameObject.SetActive(active);
        }
    }
}
```

---

## Future Scene Stages

This system can be expanded to other scenes:

- **InsideMarket_01, InsideMarket_02:** Secondary locations with optional NPCs
- **MachinesCave_00:** Interior scene where player places glyphs
- **Desert Locations:** Potential encounters based on exploration order

Each scene simply follows the same pattern: Load all NPCs, check flags, show/hide accordingly.

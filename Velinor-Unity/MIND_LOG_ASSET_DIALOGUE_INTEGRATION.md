# Mind Log Asset System - Dialogue Integration

## Overview
Mind Log entries are now **asset-based** (like Glyphs), allowing them to be:
- Referenced by GUID in dialogue JSON
- Automatically loaded when dialogue completes
- Registered with MindLogManager without manual code changes

## Architecture

### MindLogAsset (Scriptable Object)
The asset type that holds all Mind Log data.

**Fields:**
- `logID` - Unique ID (e.g., "memory_saori_desert_encounter")
- `displayName` - Human-readable name
- `icon` - Sprite for grid display
- `summaryText` - 2-3 word synopsis
- `fullText` - Full memory text
- `combineTags` - Tags for combination logic

### DialogueMindLogHandler
Processes Mind Log unlocks from dialogue JSON.

**Usage:**
```csharp
var unlocks = new List<DialogueMindLogHandler.MindLogUnlock>
{
    new DialogueMindLogHandler.MindLogUnlock 
    { 
        asset_guid = "920ede2975b53bc48b6e08bcdf26a4bd",
        asset_path = "MindLogs/MindLog_Saori_Desert_Encounter"
    }
};
DialogueMindLogHandler.ProcessMindLogUnlocks(unlocks);
```

## Dialogue JSON Format

In any dialogue beat's final node, add:

```json
{
  "id": "final_beat_node",
  "character_name": "Saori",
  "dialogue_text": "Take this... you'll understand someday.",
  "responses": [],
  "next_beat_id": null,
  "system_triggers": [
    "npc_disappear",
    "diary_update"
  ],
  "diary_entries": [
    "Met a mysterious older woman..."
  ],
  "mind_log_unlocks": [
    {
      "asset_guid": "920ede2975b53bc48b6e08bcdf26a4bd",
      "asset_path": "MindLogs/MindLog_Saori_Desert_Encounter"
    }
  ]
}
```

**Fields:**
- `asset_guid` - The Unity GUID from the asset's .meta file (used for reference integrity)
- `asset_path` - Resources path to load from (without extension)

## Example: Saori Encounter

### 1. Asset Created
File: `Assets/Resources/MindLogs/MindLog_Saori_Desert_Encounter.asset`
- logID: `memory_saori_desert_encounter`
- displayName: `Mysterious Encounter`
- icon: `920ede2975b53bc48b6e08bcdf26a4bd` (your GUID)
- summaryText: `Mysterious Encounter`
- fullText: Long narrative text
- combineTags: `[saori, marketplace, device, mystery]`

### 2. Dialogue JSON Updated
In `saori_desert_encounter_01.json`, final node now has:
```json
"mind_log_unlocks": [
  {
    "asset_guid": "920ede2975b53bc48b6e08bcdf26a4bd",
    "asset_path": "MindLogs/MindLog_Saori_Desert_Encounter"
  }
]
```

### 3. Dialogue System Integration
When the dialogue completes:
```csharp
// In your DialogueUIController or similar
if (currentBeat.mind_log_unlocks != null)
{
    DialogueMindLogHandler.ProcessMindLogUnlocks(currentBeat.mind_log_unlocks);
}
```

### 4. User Sees
- Dialogue ends
- Saori's memory is automatically added to Mind Log grid
- Next time they open Mind Log, Saori's illustration appears
- Single-click: "Mysterious Encounter"
- Double-click: Full expanded text

## Creating New Mind Log Assets

### Step 1: In Unity Editor
1. Right-click in `Assets/Resources/MindLogs/`
2. Create → Codex → Mind Log
3. Name it: `MindLog_[Character]_[Encounter]`

### Step 2: Fill Fields
- logID: `memory_[character]_[encounter]` (must be unique)
- displayName: User-friendly name
- icon: Drag sprite (your GUID will auto-populate)
- summaryText: 2-3 words
- fullText: Full narrative
- combineTags: Metadata for combinations

### Step 3: Get the GUID
1. Select the asset in Project
2. Look at `.asset.meta` file (in text editor)
3. Copy the `guid:` value
4. Use in dialogue JSON

### Step 4: Add to Dialogue JSON
```json
"mind_log_unlocks": [
  {
    "asset_guid": "[GUID_HERE]",
    "asset_path": "MindLogs/MindLog_[Name]"
  }
]
```

## Data Flow

```
Dialogue JSON with mind_log_unlocks
        ↓
Dialogue system completes beat
        ↓
DialogueMindLogHandler.ProcessMindLogUnlocks()
        ↓
Loads MindLogAsset from Resources
        ↓
Converts to MindLogEntry
        ↓
MindLogManager.AddLog()
        ↓
Memory appears in grid next time Mind Log opens
```

## Best Practices

1. **Asset Naming:** Use consistent pattern `MindLog_[Character]_[Event]`
2. **LogIDs:** Use format `memory_[character]_[encounter]`
3. **Tags:** Use lowercase, underscore-separated for consistency
4. **GUID Tracking:** Keep dialogue JSON and asset GUID in sync
5. **Testing:** Log output confirms asset loaded: `[DialogueMindLogHandler] Unlocked Mind Log: ...`

## Troubleshooting

**"Failed to load Mind Log asset: ..."**
- Check asset_path matches actual file location
- Verify asset is in `Resources/MindLogs/` folder
- Ensure filename matches path exactly (case-sensitive)

**Memory doesn't appear after dialogue**
- Check that DialogueMindLogHandler is called when dialogue completes
- Verify MindLogManager exists in scene
- Check console for error messages

**Asset shows in editor but not at runtime**
- Ensure asset is in a `Resources/` folder
- Verify `.meta` file exists alongside asset
- Try reimporting: right-click asset → Reimport

## Future Enhancements

- Multi-unlock per dialogue (multiple memories from one beat)
- Conditional unlocks (only if player passed dialogue check)
- Unlock animation/feedback UI
- "New Memory" indicator in Mind Log UI

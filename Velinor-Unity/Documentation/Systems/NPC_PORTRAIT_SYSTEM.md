# NPC Portrait Expression System - Implementation Guide

## Overview
This system allows NPC dialogue to display character portraits with emotional expressions, decoupling character emotions from 3D model animations.

## Architecture

### 1. **BeatData.cs** (Updated)
- Added field: `portrait_expression`
- Optional field in JSON dialogue entries
- Examples: "neutral", "worried", "relieved", "curious", "touched", etc.

### 2. **PortraitManager.cs** (New)
- Singleton-style manager for loading and displaying portraits
- Handles sprite caching to avoid repeated file loads
- Auto-detects portrait Image component in DialoguePanel
- Falls back to "neutral" expression if specific one not found

### 3. **File Structure**
Create this folder structure in your project:
```
Assets/Resources/Portraits/
├── Ravi/
│   ├── Ravi_neutral.png
│   ├── Ravi_worried.png
│   ├── Ravi_relieved.png
│   ├── Ravi_curious.png
│   ├── Ravi_touched.png
│   └── (other expressions...)
├── Nima/
│   ├── Nima_neutral.png
│   ├── Nima_worried.png
│   └── (other expressions...)
└── (Other NPCs...)
```

**Important:** The folder must be named `Resources` and located directly in `Assets/`.

### 4. **JSON Format Example**
```json
{
  "beats": [
    {
      "id": 1,
      "type": "npc_turn",
      "active_speaker": "Ravi",
      "prompt": "I'm worried about the marketplace...",
      "portrait_expression": "worried",
      "next_beat_id": 2
    },
    {
      "id": 2,
      "type": "npc_turn",
      "active_speaker": "Ravi",
      "prompt": "But I'm relieved you're here to help!",
      "portrait_expression": "relieved",
      "next_beat_id": 3
    }
  ]
}
```

## Integration Steps

### Step 1: Add PortraitManager to Your Scene
1. Create an empty GameObject named "PortraitManager" in your scene
2. Add the `PortraitManager` script component to it
3. It will auto-find the portrait image if named correctly

### Step 2: Create Portrait Images
1. Create a folder: `Assets/Resources/Portraits/{NPCName}/`
2. Add portrait PNG files named: `{NPCName}_{expression}.png`
3. Each image should be imported as a Sprite in Unity Inspector
4. Use transparent PNG for better visual integration

### Step 3: Integrate with DialogueManager
Modify `DialogueManager.cs` to call the portrait manager when displaying dialogue:

```csharp
// In DialogueManager, after setting up dialogue text:
private void DisplayBeat(BeatData beat)
{
    // ... existing dialogue text code ...
    
    // NEW: Show portrait if specified
    if (!string.IsNullOrEmpty(beat.active_speaker))
    {
        string expression = beat.portrait_expression ?? "neutral";
        var portraitMgr = FindAnyObjectByType<PortraitManager>();
        if (portraitMgr != null)
        {
            portraitMgr.ShowPortrait(beat.active_speaker, expression);
        }
    }
}
```

### Step 4: Add DialogueUIController Updates
The `npcPortraitImage` field was added to DialogueUIController but needs proper integration in the UI display methods.

## Emotion Expressions (Recommended)
You can start with these 9 basic expressions and expand:
1. **neutral** - Default/calm state
2. **worried** - Concerned, anxious
3. **relieved** - Pleased, comfortable  
4. **curious** - Questioning, interested
5. **touched** - Emotional, moved
6. **angry** - Frustrated, upset
7. **happy** - Joyful, content
8. **sad** - Sorrowful, disappointed
9. **confused** - Uncertain, bewildered

## Usage Examples

### Example 1: Ravi's Market Dialogue
```json
{
  "beats": [
    {
      "id": 1,
      "type": "npc_turn",
      "active_speaker": "Ravi",
      "prompt": "The market has been difficult lately...",
      "portrait_expression": "worried"
    },
    {
      "id": 2,
      "type": "player_posture",
      "active_speaker": "Player",
      "prompt": "I understand, I'm here to help",
      "next_beat_id": 3
    },
    {
      "id": 3,
      "type": "npc_turn",
      "active_speaker": "Ravi",
      "prompt": "Thank you... your support means everything",
      "portrait_expression": "touched",
      "next_beat_id": 0
    }
  ]
}
```

### Example 2: Nima's Discovery
```json
{
  "id": 5,
  "type": "npc_turn",
  "active_speaker": "Nima",
  "prompt": "Wait... could this be what we're looking for?",
  "portrait_expression": "curious",
  "next_beat_id": 6
}
```

## Benefits of This Approach

✅ **Decoupled from 3D Animation**: Express emotion through UI instead of character models  
✅ **Easy to Create**: Just draw portraits, no rigging/animation needed  
✅ **Quick Iteration**: Change emotions in JSON without rebuilding  
✅ **Scalable**: Works for any number of NPCs and expressions  
✅ **Performance**: Sprite-based, lightweight, cached  
✅ **Modular**: Works alongside any dialogue system  

## Potential Enhancements

- **Crossfade Transitions**: Smooth blend between expressions  
- **Animation**: Subtle animations within each portrait (eye blink, lips)  
- **Partial Swap**: Swap just the face while keeping body  
- **Intensity Levels**: "worried_mild" vs "worried_intense"  
- **Combination Expressions**: "happy_worried" for complex emotions  

## Troubleshooting

**Portrait not showing:**
- Ensure folder is `Assets/Resources/Portraits/` (exact name important)
- Check file naming: `{NPCName}_{expression}.png` (case-sensitive)
- Verify image is imported as "Sprite" in Inspector
- Check Debug.Log output for load errors

**Fallback to neutral not working:**
- Ensure `{NPCName}_neutral.png` exists and is accessible
- Check Resources folder path

**Performance issues:**
- PortraitManager caches sprites automatically
- If needed, pre-load common expressions in Awake()

## Next Steps

1. Create `Assets/Resources/Portraits/` folder structure
2. Add portrait images for Ravi and Nima  
3. Update JSON dialogue files with `portrait_expression` fields
4. Integrate PortraitManager.ShowPortrait() calls in DialogueManager
5. Test in-game with various expressions

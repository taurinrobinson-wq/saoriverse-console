# Codex / Mind Log System — Design Document

## Overview
The Codex has two modes:
- Glyph Mode (emotional fragments)
- Mind Log Mode (memory fragments)

Both modes use the same 3x3 grid layout. Each grid cell contains an icon representing either:
- A glyph (symbol)
- A memory fragment (scene icon)

The player interacts with these icons to expand, select, and combine fragments.

---

## Memory Fragment Structure
Each memory fragment consists of:
- **Icon** (square image representing the scene)
- **Short Synopsis** (2–3 words)
- **Expanded Text** (full memory description)
- **Metadata** (scene ID, unlock conditions)

Memory fragments are stored as ScriptableObjects.

---

## Interaction Rules

### Single Click
- Selects a memory fragment.
- Multiple fragments can be selected.
- When 2+ fragments are selected, the synopsis area changes to a **Combine** button.
- Displays a 2-3 word summary of the selected fragment in the bottom-middle area.

### Double Click
- Expands the memory fragment into full text.
- Shows a "Back" button to return to the grid.
- Navigates to the secondary "expanded memory view" screen.

### Combine Button
- **Green** = fragments can combine → creates a new deduction fragment.
- **Grey** = fragments cannot combine (default when no valid combination exists).
- Only appears when 2+ fragments are selected.
- Animation when combine is successful: logs slide/push together visually.

Combined fragments generate:
- A new icon
- A new synopsis
- A new expanded deduction text
- Notification: "Mind Logs successfully combined, double click new icon to read combined log."

This deduction is NOT exposition — it is the player's reasoning.

---

## Screen Layout

### Primary Screen: Mind Log Grid Mode
```
┌─────────────────────────────────────────────┐
│  [GLYPHS]  [MIND LOG]  [x]                 │ ← Mode toggle + Close
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────┐  ┌──────┐  ┌──────┐             │
│  │ Icon │  │ Icon │  │ Icon │             │
│  └──────┘  └──────┘  └──────┘             │
│                                             │ ← 3x3 Grid
│  ┌──────┐  ┌──────┐  ┌──────┐             │
│  │ Icon │  │ Icon │  │ Icon │             │
│  └──────┘  └──────┘  └──────┘             │
│                                             │
│  ┌──────┐  ┌──────┐  ┌──────┐             │
│  │ Icon │  │ Icon │  │ Icon │             │
│  └──────┘  └──────┘  └──────┘             │
│                                             │
├─────────────────────────────────────────────┤
│  Selected Summary (2-3 words)   [Combine]   │ ← Bottom info panel
└─────────────────────────────────────────────┘
```

### Secondary Screen: Expanded Memory View
```
┌─────────────────────────────────────────────┐
│  [BACK]                               [x]   │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │          Memory Icon                  │  │
│  └──────────────────────────────────────┘  │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  Full Expanded Memory Text Display    │  │
│  │                                       │  │
│  │  Can be multiple paragraphs.          │  │
│  │  Can include scene details, player    │  │
│  │  deductions, or combined logic.       │  │
│  │                                       │  │
│  └──────────────────────────────────────┘  │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Mode Integration

### Glyph Mode (Default)
- Top bar displays: **Glyph Name**
- Grid shows glyph symbols
- Single-click displays glyph resonance info
- Double-click expands glyph details

### Mind Log Mode
- Top bar displays: **Memory Synopsis** (when fragment selected)
- Grid shows memory icons (scene thumbnails)
- Single-click displays memory synopsis (2-3 words)
- Double-click expands to secondary screen
- Multiple selections enable **Combine** button

---

## Combination System

### When Can Fragments Combine?
Fragments can be combined when:
- They share thematic tags
- They reference adjacent scenes or locations
- They represent cause-and-effect relationships
- Explicitly authored as combinable in metadata

### Combination Logic
- Maintained in `MemoryCombineSystem.cs`
- Can use tag matching or narrative logic
- Recommended: Manual authoring of valid combinations
- Invalid combinations: button stays grey, non-interactive

### Result of Combination
- New MemoryFragment (ScriptableObject) is created
- Original fragments remain in Codex
- New fragment appears in grid (with animation)
- New fragment has unique icon + synopsis
- Double-clicking reveals synthesized expanded text
- Notification displays: "Mind Logs successfully combined, double click new icon to read combined log."

---

## Visual Feedback

### Button States
- **Combine Button Green**: Valid combination available
- **Combine Button Grey**: No valid combination selected
- **Combine Button (on success)**: Notification + animation

### Selection Feedback
- Highlight selected fragment icons
- Update synopsis in real-time
- Show number of selected fragments (optional: "2 selected" in UI)

### Animation on Combine
- Logs slide/push together toward each other
- New icon appears at center point
- Fade-out old icons, fade-in new icon
- Optional: sparkle/glow effect to indicate success

---

## Notification System Integration

### Memory Unlock Trigger
```
[Notification] Memory Fragment Acquired: "Fragment Name"
```

### Successful Combination
```
[Notification] Mind Logs Successfully Combined
[Action] Double click new icon to read combined log
```

### Failed Combination Attempt (optional)
```
[Notification] These memories don't connect...yet
```

---

## Glyph Mode Integration

The top bar normally shows:
- Glyph Name (when selected)

When in Mind Log mode:
- Shows Memory Synopsis (when fragment selected)
- Shows "Combine" when multiple fragments are selected

---

## Implementation Notes
- Use Unity UI Toolkit or Canvas UI (your existing system)
- Icons are square sprites (256x256 recommended)
- Expanded memory view is a separate panel overlay
- Combined fragments are stored as new ScriptableObjects
- The Codex controller manages:
  - Mode switching (Glyph ↔ Mind Log)
  - Grid population
  - Selection logic
  - Combination logic
  - Expanded view triggers

---

## Required Scripts
- **CodexController.cs** — Main orchestration
- **MemoryFragment.cs** — ScriptableObject for memories
- **GlyphFragment.cs** — ScriptableObject for glyphs (existing)
- **MemoryGridUI.cs** — Grid display and interaction
- **MemoryExpandUI.cs** — Expanded view panel
- **MemoryCombineSystem.cs** — Combination logic engine
- **MemoryNotificationTrigger.cs** — Unlock and combination notifications

---

## Data Structure: MemoryFragment ScriptableObject

```csharp
[CreateAssetMenu(menuName = "Codex/Memory Fragment")]
public class MemoryFragment : ScriptableObject
{
    public string fragmentID;                    // Unique identifier
    public Sprite icon;                          // Grid display icon
    public string shortSynopsis;                 // 2-3 word summary
    public string expandedText;                  // Full memory description
    
    public List<string> tags;                    // For combination logic
    public bool isDeduction;                     // True if combined fragment
    
    public List<string> combinesWith;            // Valid combine partner IDs
    public string deductionResult;               // If combined, result fragment ID
    
    public SceneData linkedScene;                // Which scene triggered this
    public float unlockCondition;                // Gate/flag requirement
}
```

---

## Combination Metadata

When authoring combinations, store:
```csharp
[System.Serializable]
public class MemoryCombination
{
    public string firstFragmentID;
    public string secondFragmentID;
    public string resultFragmentID;              // New deduction
    public string combinationLogic;              // Why they combine
}
```

Example:
```
firstFragmentID: "memory_ravi_daughter"
secondFragmentID: "memory_nima_loss"
resultFragmentID: "deduction_shared_grief"
combinationLogic: "Both memories reveal loss. Player realizes shared trauma."
```

---

## Future Additions

### Unlock Conditions
- Tied to Codex pulses
- Triggered by dialogue choices
- Revealed by environmental exploration

### Advanced Triggers
- Surveillance video integration
- Environmental memory triggers
- Glyph resonance cascades
- NPC dialogue unlocks

### Extended Combinations
- 3+ fragment combinations
- Deduction chains (combining deductions)
- Narrative branching based on combinations

---

## Success Criteria

✅ Grid displays 9 memory icons correctly  
✅ Single-click selects fragment and updates synopsis  
✅ Double-click expands to secondary view with Back button  
✅ Multiple selections enable Combine button  
✅ Combine button is grey by default, green when valid  
✅ Successful combination creates new fragment + animation  
✅ Notification displays on unlock and combination  
✅ Player can double-click combined fragment to read deduction  
✅ UI feels responsive and polished  

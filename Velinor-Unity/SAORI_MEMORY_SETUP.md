# Creating the Saori Memory Asset

## Option 1: Quick Test (Runtime Generation)
1. In your scene, create an empty GameObject called "SaoriMemorySetup"
2. Add the `SaoriMemorySetup` component
3. **Assign an icon sprite** to the "Saori Icon" field
4. Enable "Auto Create On Start"
5. When the scene runs, the Saori memory is created and ready in the Mind Log grid

This is perfect for testing the UI flow without needing to create assets yet.

---

## Option 2: Proper Asset (Recommended for Real Use)

### Step 1: Create the MemoryFragment Asset
1. In Project window, navigate to `Assets/Resources/Memories` (create folder if needed)
2. Right-click → Create → Codex → Memory Fragment
3. Name it: `Saori_Desert_Encounter`

### Step 2: Fill in the Fields

**Identity Section:**
- Fragment ID: `memory_saori_desert_encounter`
- Display Name: `Mysterious Encounter`

**Display Section:**
- Icon: [Drag a square icon sprite here - 256x256 recommended]
- Short Synopsis: `Mysterious Encounter`

**Content Section:**
- Expanded Text: 
```
I met an older woman on the way to the marketplace. I didn't get her name, but she handed me this strange device without much explanation. 

There was something knowing in her eyes—as if she recognized me, or perhaps knew something about me that I didn't know myself. 

The device she gave me feels important, though I can't explain why. It has strange markings on it, almost like symbols from a language I should know but can't quite remember.
```

**Metadata Section:**
- Tags: (Add these)
  - `saori`
  - `marketplace`
  - `device`
  - `mystery`
- Is Deduction: `false` (it's a base memory, not a combined result)

**Combination Section:**
- Combines With: (Leave empty for now, or add IDs of memories that can combine with this)

**Source Section:**
- Linked Scene: (optional, e.g., "Desert_Saori_Meeting")
- Unlock Condition: `0` (always available)

### Step 3: Save the Asset
Click Save (Ctrl+S) - the asset is now created!

### Step 4: Load it into the Manager

**Option A - Auto-load with MindLogInitializer:**
1. In your scene, create a GameObject called "MindLogInitializer"
2. Add the `MindLogInitializer` component
3. Set "Memory Fragments" list size to 1
4. Drag the `Saori_Desert_Encounter` asset into the list
5. Enable "Auto Initialize On Start"

**Option B - Load at Runtime:**
```csharp
public void OnSaoriEncounterComplete()
{
    var fragment = Resources.Load<MemoryFragment>("Memories/Saori_Desert_Encounter");
    var initializer = FindObjectOfType<MindLogInitializer>();
    initializer.AddFragment(fragment);
}
```

---

## Testing the Setup

1. Make sure you have:
   - ✅ MindLogManager in scene
   - ✅ SaoriMemorySetup (or MindLogInitializer) set up
   - ✅ Icon sprite assigned
   - ✅ MemoryGridController ready

2. Run the scene
3. Click "Open Mind Log" (or your test button)
4. The Saori memory should appear in the grid as a colored square
5. Single-click it → "Mysterious Encounter" appears
6. Double-click it → Full text displays

---

## What Happens Behind the Scenes

```
SaoriMemorySetup.CreateSaoriMemory()
        ↓
Creates MindLogEntry with all text
        ↓
Adds to MindLogManager.AddLog()
        ↓
MemoryGridController.PopulateFromManager()
        ↓
UI displays in grid
```

---

## Next: Trigger from Dialogue

Once you verify this works in testing, you can hook it into your Saori dialogue:

```csharp
// In your dialogue system, when Saori encounter ends:
public void OnSaoriDialogueComplete()
{
    // Create the memory
    var initializer = FindObjectOfType<SaoriMemorySetup>();
    initializer.CreateSaoriMemory();
    
    // Or load from asset
    var fragment = Resources.Load<MemoryFragment>("Memories/Saori_Desert_Encounter");
    var mgr = FindObjectOfType<MindLogInitializer>();
    mgr.AddFragment(fragment);
    
    Debug.Log("Saori's memory saved to Mind Log");
}
```

---

## Icon Asset Notes

The icon should be:
- **Size:** 256x256 pixels (or a square)
- **Format:** PNG with transparency recommended
- **Style:** Match your UI aesthetic (the test used plain colored squares)

For now, you can use a simple colored square:
- Open any image editor
- Create a 256x256 square
- Fill with a color (e.g., #04F404 for green to match your UI)
- Save as PNG
- Drag into your Saori asset's Icon field

Or use an actual illustration if you have one!

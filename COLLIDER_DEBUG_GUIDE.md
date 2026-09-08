# Collider Switching Debug Guide

## What to do:

1. **Play the game and complete the triglyph puzzle** (select 3 glyphs, press E)
2. **Open the Console** (Ctrl+Shift+C or Window > TextMeshPro > Console)
3. **Copy the entire output** related to colliders - look for lines starting with `[Triglyph Puzzle]`

## What to look for:

### Expected Output (if working):
```
[Triglyph Puzzle] Attempting to activate scene transition collider...
[Triglyph Puzzle] sceneTransitionCollider reference status: ASSIGNED
[Triglyph Puzzle] doorCollider reference status: ASSIGNED
[Triglyph Puzzle] Scene collider BEFORE: enabled=False, isTrigger=True, name=YourColliderName
[Triglyph Puzzle] Scene collider AFTER: enabled=True
[Triglyph Puzzle] ✅ Scene transition collider ACTIVATED. New state: True
[Triglyph Puzzle] Door collider BEFORE: enabled=True, isTrigger=False, name=YourDoorColliderName
[Triglyph Puzzle] Door collider AFTER: enabled=False
[Triglyph Puzzle] ✅ Door collider DEACTIVATED. Player can now pass through.
```

### If references are NULL:
- Check Inspector on TriglyphPuzzleController
- Both fields should have colliders assigned
- If they're empty, that's the problem - assign them

### If colliders don't change state:
- Check if the colliders are on **disabled GameObjects**
  - If so, you need to enable the GameObject first, then change the collider
- Check if there's a **script resetting the collider state**
- Check if the colliders are the **wrong type** (trigger vs non-trigger)

## Requirements:

- **doorCollider**: Should be enabled initially (blocks player), then disabled
- **sceneTransitionCollider**: Should be disabled initially, then enabled
- Both should be on **active GameObjects**

## Possible Fix:

If colliders are on disabled GameObjects, add this code at the start of `ActivateSceneTransition()`:

```csharp
if (sceneTransitionCollider != null && !sceneTransitionCollider.gameObject.activeSelf)
{
    sceneTransitionCollider.gameObject.SetActive(true);
}
```

Please share the Console output and let me know what you see!

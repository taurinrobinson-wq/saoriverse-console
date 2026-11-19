# Lioren Character Integration - Quick Guide

## The Concept
Your `VelinorPlayerController` works by sending animator parameters (`Speed`, `Grounded`, `MotionSpeed`). Swap the model, keep the same parameters = works with any character.

## Steps

### 1. Export from Artist
Have artist export as `.fbx` with:
- Mesh + skeleton + skinning
- Animation clips (idle, walk, run, jump, fall, land) or note they'll be added separately

### 2. Import FBX
1. Place `.fbx` in `Assets/Models/Characters/`
2. Select → Inspector → Import Settings:
   - Model: Humanoid (or Generic)
   - Animation: Import Animation (checked)
   - Avatar: Create From This Model
3. Click Apply

### 3. Create Animator Controller
1. Right-click Project → Create → Animator Controller → `LiorenAnimator`
2. Open it (double-click)
3. Add parameters (bottom left):
   - `Speed` (Float, default 0)
   - `Grounded` (Bool, default true)
   - `MotionSpeed` (Float, default 1)

### 4. Add Animation States
Create these states and assign animation clips:
- **Idle** (loop enabled)
- **Walk** (loop enabled)
- **Run** (loop enabled)
- **Jump** (loop disabled)
- **Fall** (loop enabled)
- **Land** (loop disabled)

### 5. Add Transitions
```
Idle ↔ Walk: Speed > 0.1 / Speed < 0.1
Walk ↔ Run:  Speed > 1.5 / Speed < 1.5
Any → Jump:  Grounded = false
Jump → Fall: (auto after animation)
Fall → Land: Grounded = true
Land → Idle: (auto after animation)
```

Each transition: 
- Exit Time: 0.9
- Transition Duration: 0.1-0.2

### 6. Create Character Prefab
1. Drag Lioren FBX into scene → Creates GameObject
2. Add components:
   - **Animator**: Controller = LiorenAnimator
   - **CharacterController**: Height ~1.7, Radius 0.35, Center (0, 0.85, 0)
   - **CapsuleCollider**: Same dimensions, Tag: "Player", Layer: "Player"
   - **Script**: VelinorPlayerController
   - **Script**: VelinorStarterAssetsInputs
   - **Camera** (child): LocalPos (0, 0.93, 0), Tag: "MainCamera"

3. Drag into prefab folder: `Assets/Prefabs/Characters/LiorenCharacter.prefab`

### 7. Replace in Scenes
For each scene:
1. Delete old player
2. Drag LiorenCharacter prefab in
3. Position at spawn point

### 8. Test
- WASD moves → animations transition idle/walk/run
- Right-click + mouse rotates camera
- Space jumps → see jump/fall/land
- E interacts with NPCs
- No console errors

---

## Critical: Parameter Names Must Match Exactly
- `Speed` (not "speed")
- `Grounded` (not "grounded")
- `MotionSpeed` (not "motionSpeed")

If names don't match, animations won't play.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Animations don't play | Check parameter names are exact (case-sensitive) |
| Character T-poses | Check avatar bone mapping in import settings |
| Black/pink mesh | Re-import with correct material settings |
| Movement too slow/fast | Adjust `MoveSpeed` in VelinorPlayerController |
| Camera clips through body | Adjust Camera child object's local Y position |
| Character falls through floor | Check Ground Layer in VelinorPlayerController inspector |

---

## File Structure After Integration
```
Assets/
├── Models/Characters/LiorenCharacter.fbx
├── Animators/Characters/LiorenAnimator.controller
└── Prefabs/Characters/LiorenCharacter.prefab ← Use this in all scenes

Scenes/
├── MainScene.unity (contains LiorenCharacter prefab instance)
└── OtherScenes.unity (replace old player with prefab)
```

---

## Default Settings Reference

**VelinorPlayerController:**
- MoveSpeed: 2.0
- SpeedChangeRate: 10.0
- GroundedRadius: 0.28
- GroundedOffset: -0.14

**CharacterController:**
- Height: ~1.7 (match Lioren's height)
- Radius: 0.35
- Center: (0, 0.85, 0)

**Camera:**
- LocalPosition: (0, 0.93, 0)

Adjust if Lioren looks wrong proportionally.

---

## Why No Code Changes?

Your controller is parameter-based:
```csharp
_animator.SetFloat("Speed", moveSpeed);
_animator.SetBool("Grounded", isGrounded);
```

It doesn't care what model it's attached to—only that the animator responds to these parameters. That's why integration is just swapping the mesh and animator controller.

---

## Timeline
- Artist export: ~1 hour
- Import & setup: ~30 min
- Animator controller: ~1-2 hours
- Prefab assembly: ~45 min
- Replace scenes: ~15-30 min per scene
- **Total: 4-6 hours**

---

That's it. Start with the export, follow the steps, test, done.

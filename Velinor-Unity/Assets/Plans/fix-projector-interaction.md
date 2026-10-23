# Project Overview
- Game Title: Velinor
- High-Level Concept: Narrative-driven 3D exploration and social simulation.
- Players: Single player.
- Target Platform: PC (StandaloneWindows64).
- Render Pipeline: Built-in.

# Game Mechanics
## Core Gameplay Loop
Exploration and interaction with world objects (Projectors, NPCs) to progress the narrative and collect logs/glyphs.
## Controls and Input Methods
- WASD for movement (handled by `PlayerController2D5`).
- 'E' key for interacting with the Projector.
- 'G' key for general NPC interaction.

# UI
- Interaction prompt ("Press E to Interact with Projector").
- Notification Panel for messages.

# Key Asset & Context
- `Collider_ProjectorBase` (GameObject): The trigger object in scene `MachinesCave_02_01`.
- `ProjectorInteractionController.cs`: Script managing the projector interaction logic.
- `[Player]` (GameObject): The player character with `PlayerController2D5` and a 3D `CapsuleCollider`.

# Implementation Steps
## Step 1: Align Physics Systems (Converge on 3D)
The current issue is a mismatch between the Player's 3D CapsuleCollider and the Projector's 2D CircleCollider2D. While the `PlayerController2D5` supports both 2D and 3D for obstacle detection, its interaction system (`HandleInteraction`) and other interactables in the scene (like `NPCInteraction`) rely exclusively on 3D physics (`Physics.OverlapSphere`). Therefore, the Projector should be updated to 3D to be consistent with the player's interaction range and other world objects.

1. **Modify Player**: Add a `Rigidbody` component to the `[Player]` GameObject.
   - Set `isKinematic = true`.
   - Set `useGravity = false`.
   - *Reasoning*: Unity requires at least one object in a collision/trigger pair to have a Rigidbody. The Projector's trigger will be Kinematic, so the Player needs a Rigidbody (Kinematic is fine) to ensure `OnTriggerEnter` fires.
2. **Modify Projector**: Update `Collider_ProjectorBase` in scene `MachinesCave_02_01`.
   - Remove `CircleCollider2D`.
   - Remove `Rigidbody2D`.
   - Add `SphereCollider`.
     - Set `Is Trigger = true`.
     - Set `Radius = 0.75`.
   - Add `Rigidbody`.
     - Set `isKinematic = true`.
     - Set `useGravity = false`.

## Step 2: Update Script (Optional Cleanup)
The `ProjectorInteractionController` script currently has a `Collider2D` field that is unused. While not strictly necessary for fixing the trigger, updating it to a generic `Collider` is good practice if it's meant to represent the trigger.
1. In `ProjectorInteractionController.cs`, change `[SerializeField] private Collider2D projectorCollider;` to `[SerializeField] private Collider projectorCollider;`.

# Verification & Testing
1. **Manual Verification**: 
   - Enter Play Mode in scene `MachinesCave_02_01`.
   - Approach the Projector.
   - Check the Console for the message: `[Projector Interaction] Player near projector`.
   - Verify the UI prompt "Press E to Interact with Projector" appears.
   - Press 'E' to verify the interaction triggers the log: `[Projector Interaction] Interaction triggered - Stage: Stage01`.

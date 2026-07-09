# Velinor: Technical Project Overview

## 1. Project Description
**Velinor** is a narrative-driven 3D exploration and social simulation experience set in a world of atmospheric ruins and complex social dynamics. The project centers on the **Resonance System**, where player choices—defined by "Tone"—physically and emotionally reshape the "Remnants" (personality traits) of the NPCs they encounter. It is designed for players who enjoy deep character interactions, environmental storytelling, and seeing their narrative influence ripple through a social graph.

**Core Pillars:**
*   **Narrative Resonance:** Player choices adjust emotional "Tone," which correlates to changes in NPC personalities.
*   **The Social Ripple:** An influence map ensures that changing one NPC's traits cascades to their connected social circle.
*   **Atmospheric Exploration:** A "Built-in" Unity pipeline project utilizing high-quality assets to create a hauntingly beautiful, ruined world.
*   **Data-Driven Storytelling:** Dialogue and character states are managed via external JSON files for rapid iteration and complex branching.

## 2. Gameplay Flow / User Loop
The experience follows a loop of exploration, interaction, and narrative consequence:
1.  **Boot & Title:** The user starts in `TitleScene`, where they can manage settings or begin the journey.
2.  **Exploration:** The player explores 3D environments (e.g., `Marketplace`) using a third-person controller.
3.  **Interaction:** Approaching an NPC or object triggers an interaction prompt. Pressing the interaction key transitions the game into a focused Dialogue Mode.
4.  **Dialogue & Choice:** The player engages in branching dialogue managed by `DialogueManager`. Choices apply "Tone" effects to the player and "Resonance" to NPCs.
5.  **State Ripple:** `StatManager` calculates the effects of these choices, updating the player’s global standing and cascading personality shifts across the NPC network via the Influence Map.
6.  **Persistence:** Character states and encounter histories are snapshotted and can be persisted to JSON.

## 3. Architecture
The project follows a **Manager-Pattern** architecture with a strong separation between the narrative simulation (Data) and the gameplay representation (View).

*   **Core Managers:** Singleton managers like `DialogueManager` and `StatManager` handle the high-level logic and data processing.
*   **Data-Driven Design:** The game state is not hardcoded but loaded from `Resources/velinor/data/` and `Resources/velinor/stories/`.
*   **Decoupled Interaction:** The interaction system uses the `IInteractable` interface, allowing the player to interact with NPCs, pedestals, and glyphs through a unified system.
*   **State Persistence:** The `StatManager` snapshots NPC Remnants after every encounter, providing a historical record of how the world has changed.

`Location: Assets/Scripts/Core`

## 4. Game Systems & Domain Concepts

### Resonance & Stat System
The heart of the game, managing two distinct but correlated stat pools.
*   `ToneType`: Player stats representing emotional qualities: `Courage`, `Empathy`, `Observation`, `Wisdom`, and `NarrativePresence`.
*   `RemnantType`: NPC personality traits: `Resolve`, `Empathy`, `Memory`, `Nuance`, `Authority`, `Need`, `Trust`, and `Skepticism`.
*   `StatManager`: The simulation engine. It handles "Tone→Remnants" correlations (e.g., high Player Wisdom increases NPC Memory) and manages the `influence_map` for cascading changes.

`Location: Assets/Scripts/Core/StatManager.cs`

### Dialogue System
A JSON-powered narrative engine that handles branching story paths.
*   `DialogueManager`: Loads `sample_story.json`, manages the dialogue UI, and communicates choice results to the `StatManager`.
*   `DialogueData`: Defines the structure of passages and choices.
*   `DialogueGateEvaluator`: (Optional/Extended) Logic for locking/unlocking choices based on current stats.

`Location: Assets/Scripts/Core/DialogueManager.cs`

### Interaction System
A proximity and raycast-based system for triggering world events.
*   `IInteractable`: Interface that must be implemented by any object the player can "Interact" with.
*   `NPCInteraction`: An implementation of `IInteractable` that triggers a dialogue sequence with a specific NPC ID.
*   `VelinorPlayerController`: Handles the player-side raycasting and input consumption for interactions.

`Location: Assets/Scripts/Core/NPCInteraction.cs`, `Assets/Scripts/Core/VelinorPlayerController.cs`

### NPC Behavior
*   `NPCRoaming`: Simple AI for ambient movement within the world.
*   `NPCObject`: A container component for NPC-specific data and visual references.

`Location: Assets/Scripts/Core/`

## 5. Scene Overview
*   `TitleScene`: The entry point. Handles menu logic and initial state setup.
*   `Marketplace`: The primary gameplay scene. Contains the NPC social hub and environment art.
*   `MarketplaceBlockA`: A modular subsection of the marketplace used for testing specific layouts.
*   `VelinorNarrativeTest`: A dedicated scene for testing dialogue triggers and stat ripples without environmental overhead.
*   `MalrikElenyaTestScene`: Specialized test environment for specific character dialogue sequences.

`Location: Assets/Scenes/`

## 6. UI System
The UI is built using **UGUI (Unity UI)** and **TextMesh Pro**, with a focus on clean, narrative-first presentation.
*   **Dialogue UI:** Managed by `DialogueManager`, consisting of an NPC name plate, body text, and a dynamic container for choice buttons.
*   **Interaction Prompt:** A world-space or overlay UI that appears when the player is in range of an interactable object (`InteractionUI`).
*   **Stat Display:** Debug or menu-based screens to visualize current Tone and Remnant levels (`StatDisplayUI`).

`Location: Assets/Scripts/UI/`

## 7. Asset & Data Model
*   **JSON Data:** The "Source of Truth" for the game.
    *   `npc_state.json`: Defines NPC profiles, the influence map (weighted social links), and encounter history.
    *   `sample_story.json`: Contains the full branching narrative structure (Twine-like).
*   **Resources Folder:** Used for runtime loading of data files via `Resources.Load<TextAsset>`.
*   **ScriptableObjects:** (Used sparingly) Primarily for static configuration or audio/visual mappings.
*   **Prefabs:** Standardized NPC prefabs and interaction triggers allow for rapid scene assembly.

`Location: Assets/Resources/velinor/`

## 8. Notes, Caveats & Gotchas
*   **Tone Correlation:** Changing a player's Tone automatically triggers a "Direct" change to **all** NPCs. If the choice also has "Resonance," that triggers a **Cascaded** change. This can lead to significant stat shifts from a single choice—test multipliers carefully.
*   **Stat Clamping:** Remnants are strictly clamped between `0.1` and `0.9`. They can never reach `0` or `1`, representing the idea that no trait is ever entirely gone or absolute.
*   **Singleton Pattern:** `DialogueManager` and `StatManager` use `DontDestroyOnLoad`. If creating new scenes, ensures these managers are not duplicated or lost during scene transitions.
*   **Input Handling:** The project supports both the New Input System and Legacy Manager, but `VelinorPlayerController` is designed primarily for the New Input System with a fallback for keyboard/mouse assumptions.
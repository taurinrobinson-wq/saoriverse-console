# Game Design

This document outlines the design specifications for the Velinor project, focusing on the desert environment, player interaction, and the NPC setup for Saori. The design adheres to the "Resonance System" where player choices impact NPC traits (Remnants) through Tone.

## UI Design

- **Color system:**
    - **Primary:** Deep Slate (#333333) for main panels.
    - **Secondary:** Sandstone (#D2B48C) for highlighting and labels.
    - **Accent:** Velinor Purple (#800080) for resonance and important narrative beats.
    - **Surface hierarchy:** Base (World) → Dialogue Panel (Translucent Deep Slate) → Choice Buttons (Opaque Dark Grey).

- **Typography:**
    - **Headline:** Bold, serif font for NPC names.
    - **Body:** Readable sans-serif for dialogue text.
    - **Labels:** Monospace or clean sans-serif for stat labels and interaction prompts.

- **Layout:**
    - **Dialogue Panel:** Bottom-third of the screen, spanning 80% width. Depth provided by a subtle drop shadow and semi-transparency.
    - **Choice Container:** Vertical list of buttons on the right side of the dialogue panel.
    - **Interaction Prompt:** Floating label above interactable objects or centered at the bottom of the HUD.

- **Components:**
    - **Buttons:** Dark grey (#333333) with 10px rounded corners. Visual state: Lighten on hover, darken on click.
    - **Dialogue Window:** Inset appearance with a slight inner glow.
    - **Interaction Prompt:** "Press E to [Action]" in white text with a dark outline for readability against desert backgrounds.

## Asset Design

- **Visual identity:** "Atmospheric Ruins" — a blend of ancient, decaying architecture and a harsh but beautiful desert.
- **Saori NPC:**
    - **Type:** Billboard Sprite (core).
    - **Style:** 2D hand-drawn aesthetic with a "nobg" (no background) treatment, facing the camera.
    - **Reference:** `Assets/Graphics/NPCs/Saori_device_nobg_left.png`.
- **Desert Environment:**
    - **Ground Plane:** Large plane with a "Cracked Earth" or "Fine Sand" texture (core). Color temperature: Warm, golden-orange.
    - **Trees:** Organic placement of `URP_Tree_1`, `URP_Tree_2`, and `URP_Tree_3` (core).
        - **Placement Rule:** Trees should be clumped in small groups (2-3) near ruins or in depressions, rather than evenly distributed.
        - **Style:** Desiccated, twisted trunks with sparse, pale foliage.
- **Player:**
    - **Type:** 3rd-person humanoid (core).
    - **Style:** Consistent with the ruined world — weathered clothing, functional gear.

## Game Feedback

- **Genre profile:** Atmospheric Exploration / Narrative RPG.
- **Interaction map:**

| Interaction | Tier | Importance | Camera | Time | Transform | Visual | Audio | Input | Rationale |
|------------|------|-----------|--------|------|-----------|--------|-------|-------|-----------|
| Walk/Move | core | low | — | — | — | Dust puff (opt) | Footsteps | — | Ground the player in the desert. |
| Near Interactable | core | medium | Subtle zoom | — | — | Prompt appears | Soft hum | — | Direct attention to NPCs/Doors. |
| Press 'E' | core | medium | — | — | Button depress | Pulse effect | Click/Thud | Buffering | Confirm interaction intent. |
| NPC Dialogue | core | high | Focus on NPC | — | — | Panel fade-in | Voice/Beep | — | Transition to narrative mode. |
| Choice Selected | core | high | — | 0.05s stop | — | Stat Ripple | Shimmer SFX | — | Emphasize the weight of the choice. |

- **Assets needed:**
    - **Ground Plane:** (core) Texture: Cracked sand. Size: 100x100 units.
    - **Saori Billboard:** (core) Sprite: Saori. Placement: Inside building.
    - **Desert Trees:** (core) Prefabs: URP_Tree_1, 2, 3. Placement: Clustered outside.
    - **Dialogue Canvas:** (core) Layout: Name, Body, Choices.
    - **Interaction Canvas:** (core) Layout: Prompt Text.

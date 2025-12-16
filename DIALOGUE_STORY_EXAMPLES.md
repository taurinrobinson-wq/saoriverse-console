# Story Scene Examples — Dialogue System in Action

Real-world story scenarios using the auto-generated dialogue system.
## 

## Scene 1: The Marketplace Greeting

**Setup:** Player enters marketplace for the first time. All 9 NPCs react.

```python
def scene_marketplace_greeting():
    """Player arrives at marketplace. All NPCs acknowledge their presence."""
    from velinor.engine.npc_manager import NPCManager, create_marketplace_npcs
    from velinor.engine.npc_encounter import generate_scene, print_scene

    manager = NPCManager()
    manager.add_npcs_batch(create_marketplace_npcs())

    # No player choices yet — just reactions
    npcs_dict = {name: npc.remnants for name, npc in manager.npcs.items()}
    scene = generate_scene(npcs_dict, encounter_id=1, context="greeting")

    print("\n🏪 You enter the marketplace...")
    print_scene(scene, summary_only=True)

    return scene
```


**Output:**

```
[1] Ravi         | I see calculate in you., spoken with measured merchant caution...
[2] Nima         | I see complexity in you. — always watching, always wary...
[3] Kaelen       | I see a path in you.... said with a sly, calculating grin...
[4] Tovren       | I see fragile in you., practical as iron and twice as reliable...
[5] Sera         | I see sprout in you.... like herbs, it blooms so softly...
[6] Dalen        | I see steel in you., considered before the next step...
[7] Mariel       | I see understand in you., woven patiently into the tapestry of memory...
[8] Korrin       | I see never forget in you., whispered like gossip in the alley...
[9] Drossel      | I see a path in you., mon cher — but shadows linger...
```


**Key Insight:** All 9 NPCs' first impressions vary based on their REMNANTS traits. On replay with different player TONE values, these would be completely different.
## 

## Scene 2: Sera's Quest — The Redemption Arc

**Setup:** Multi-turn dialogue with Sera showing emotional progression.

```python
def scene_sera_redemption_arc():
    """Multi-turn Sera encounter showing transformation through player empathy."""
    from velinor.engine.npc_manager import NPCManager, create_marketplace_npcs
    from velinor.engine.npc_encounter import generate_encounter, print_encounter

    manager = NPCManager()
    manager.add_npcs_batch(create_marketplace_npcs())

    print("\n🌿 SERA'S REDEMPTION ARC\n")

    # Turn 1: Greeting (Sera unsure, fragile)
    print("--- TURN 1: First Meeting ---")
    sera = manager.get_npc("Sera")
    enc1 = generate_encounter("Sera", sera.remnants, 1, context="greeting")
    print_encounter(enc1, full_details=False)

    # Player chooses empathy
    player_choice = 0  # [empathy] in choices
    manager.apply_tone_effects({"empathy": 0.15})
    print("You choose: Listen deeply.")

    # Turn 2: Alliance building (Sera opening up)
    print("\n--- TURN 2: Building Trust ---")
    sera = manager.get_npc("Sera")
    enc2 = generate_encounter("Sera", sera.remnants, 2, context="alliance")
    print_encounter(enc2, full_details=False)

    # Player continues with empathy + wisdom
    manager.apply_tone_effects({"empathy": 0.15, "wisdom": 0.1})
    print("You choose: Understand her pain.")

    # Turn 3: Resolution (Sera transformed)
    print("\n--- TURN 3: A New Beginning ---")
    sera = manager.get_npc("Sera")
    enc3 = generate_encounter("Sera", sera.remnants, 3, context="resolution")
    print_encounter(enc3, full_details=False)

    print("\n✓ Sera gains: Flicker Ritual ability")
    print("✓ Shrine keepers soften (ripple effect)")
    print("✓ Trust unlocks new story paths")

# Run it:

# scene_sera_redemption_arc()
```


**Expected Output Evolution:**

```
TURN 1: "I see fragile in you.... like herbs, it fades to shadow."
Choices: [NEED] Ask for help. [NUANCE] Perhaps...

TURN 2: "My empathy feels bloom.... like herbs, it blooms so softly."
Choices: [EMPATHY] Listen deeply. [NEED] Seek connection.

TURN 3: "Maybe we've found bloom in each other.... like herbs..."
Choices: [EMPATHY] Share understanding. [TRUST] Express your faith.
```

## 

## Scene 3: Kaelen's Betrayal → Redemption

**Setup:** Kaelen as antagonist, then potential redemption based on empathy.

```python
def scene_kaelen_betrayal_to_redemption():
    """Kaelen dual-path: betrayal or redemption based on player choices."""
    from velinor.engine.npc_manager import NPCManager, create_marketplace_npcs
    from velinor.engine.npc_encounter import generate_encounter, print_encounter

    manager = NPCManager()
    manager.add_npcs_batch(create_marketplace_npcs())

    print("\n🗡️ KAELEN: BETRAYAL OR REDEMPTION?\n")

    # PATH A: Aggressive response (confrontation)
    print("--- PATH A: Aggressive Approach ---")
    manager_a = NPCManager()
    manager_a.add_npcs_batch(create_marketplace_npcs())

    kaelen_a = manager_a.get_npc("Kaelen")
    enc_a1 = generate_encounter("Kaelen", kaelen_a.remnants, 1, context="conflict")
    print("You confront Kaelen...")
    print_encounter(enc_a1, full_details=False)

    # Player chooses skepticism
    manager_a.apply_tone_effects({"courage": 0.2})  # Aggressive
    kaelen_a = manager_a.get_npc("Kaelen")
    enc_a2 = generate_encounter("Kaelen", kaelen_a.remnants, 2, context="conflict")
    print("\nKaelen's Response to Aggression:")
    print_encounter(enc_a2, full_details=False)

    # PATH B: Empathetic response (understanding)
    print("\n--- PATH B: Empathetic Approach ---")
    manager_b = NPCManager()
    manager_b.add_npcs_batch(create_marketplace_npcs())

    kaelen_b = manager_b.get_npc("Kaelen")
    enc_b1 = generate_encounter("Kaelen", kaelen_b.remnants, 1, context="greeting")
    print("You approach Kaelen gently...")
    print_encounter(enc_b1, full_details=False)

    # Player chooses empathy
    manager_b.apply_tone_effects({"empathy": 0.2})
    kaelen_b = manager_b.get_npc("Kaelen")
    enc_b2 = generate_encounter("Kaelen", kaelen_b.remnants, 2, context="alliance")
    print("\nKaelen's Response to Empathy:")
    print_encounter(enc_b2, full_details=False)

    print("\n✓ PATH A leads to: Conflict, loss of trust")
    print("✓ PATH B leads to: Redemption, gain of powerful ally")

# Run it:

# scene_kaelen_betrayal_to_redemption()
```


**Expected Output:**

```
PATH A (Aggressive):
TURN 1: "I see a path in you.... said with a sly, calculating grin."
Choices: [SKEPTICISM] Question their motives.

TURN 2: "I feel something between us now.... said with a sly, calculating grin."
Choices: [RESOLVE] Stand firm. [SKEPTICISM] Doubt openly.

PATH B (Empathetic):
TURN 1: "I see a moment in you.... said with a sly, calculating grin."
Choices: [EMPATHY] Share understanding.

TURN 2: "My empathy feels redeem.... said with genuine remorse."
Choices: [EMPATHY] Listen deeply. [TRUST] Offer your faith.
```

## 

## Scene 4: Drossel's Deal — Crime Boss Negotiation

**Setup:** High-stakes negotiation with Drossel. Trust matters.

```python
def scene_drossel_deal():
    """Drossel offers a dangerous deal. Trust determines outcome."""
    from velinor.engine.npc_manager import NPCManager, create_marketplace_npcs
    from velinor.engine.npc_encounter import generate_encounter, print_encounter

    manager = NPCManager()
    manager.add_npcs_batch(create_marketplace_npcs())

    print("\n🔪 DROSSEL: THE DEAL\n")

    # Turn 1: Drossel proposes
    print("--- THE PROPOSAL ---")
    drossel = manager.get_npc("Drossel")

    # Drossel with low trust (default)
    enc1 = generate_encounter("Drossel", drossel.remnants, 1, context="greeting")
    print("Drossel emerges from the shadows...")
    print_encounter(enc1, full_details=False)

    print("\n'I have use for someone like you, mon ami.'")
    print("'But can I trust you?'")
    print("\nYour options:")
    for i, choice in enumerate(enc1['choices'], 1):
        print(f"  {i}. [{choice['trait'].upper()}] {choice['text']}")

    # PATH A: Build trust
    print("\n--- PATH A: Build Trust ---")
    manager.apply_tone_effects({"trust": 0.2})
    drossel = manager.get_npc("Drossel")

    enc2 = generate_encounter("Drossel", drossel.remnants, 2, context="alliance")
    print("\nDrossel (Trust Building):")
    print_encounter(enc2, full_details=False)

    if drossel.remnants["trust"] > 0.6:
        print("\n✓ Drossel believes you. Deal accepted.")
        print("✓ Unlock: Shadow Path quest, access to thieves' network")

    # Reset
    manager = NPCManager()
    manager.add_npcs_batch(create_marketplace_npcs())

    # PATH B: Maintain distance
    print("\n--- PATH B: Maintain Skepticism ---")
    drossel = manager.get_npc("Drossel")

    # Don't increase trust, keep skepticism high
    manager.apply_tone_effects({"observation": 0.2})  # Neutral trait
    drossel = manager.get_npc("Drossel")

    enc3 = generate_encounter("Drossel", drossel.remnants, 2, context="conflict")
    print("\nDrossel (Skepticism Maintained):")
    print_encounter(enc3, full_details=False)

    if drossel.remnants["trust"] < 0.3:
        print("\n✗ Drossel sees you as risk. Deal rejected.")
        print("✗ Consequence: Shadow Path becomes enemy path")

# Run it:

# scene_drossel_deal()
```


**Expected Output:**

```
TURN 1 (Low Trust):
"I see something in you., mon cher — but shadows linger."
[AUTHORITY] Command action.
[SKEPTICISM] Doubt openly.

TURN 2A (High Trust Built):
"My trust feels mon ami.... mon cher — a deal is a deal."
[TRUST] Offer your faith.
[RESOLVE] Stand firm.

TURN 2B (Skepticism Maintained):
"I feel something between us now., mon cher — but shadows linger."
[SKEPTICISM] Question their motives.
[RESOLVE] Hold your ground.
```

## 

## Scene 5: The Marketplace Conspiracy — Multi-NPC Pressure

**Setup:** Multiple NPCs gang up on player. How do you defuse it?

```python
def scene_marketplace_conspiracy():
    """Multiple NPCs oppose you. Your response determines outcomes."""
    from velinor.engine.npc_manager import NPCManager, create_marketplace_npcs
    from velinor.engine.npc_encounter import generate_scene, print_scene

    manager = NPCManager()
    manager.add_npcs_batch(create_marketplace_npcs())

    print("\n⚔️ THE MARKETPLACE TURNS AGAINST YOU\n")

    # Turn 1: Accusation (conflict context, all NPCs hostile)
    print("--- THE ACCUSATIONS ---")
    npcs_dict = {name: npc.remnants for name, npc in manager.npcs.items()}
    scene1 = generate_scene(npcs_dict, 1, context="conflict")
    print_scene(scene1, summary_only=True)

    print("\nThey all speak at once, accusations flying...")
    print(f"Dominant mood: {scene1['dominant_mood'].upper()}")

    # Turn 2: Your Response - Empathy (try to calm them)
    print("\n--- YOUR EMPATHETIC RESPONSE ---")
    print("You speak from the heart, addressing each one...")

    manager.apply_tone_effects({"empathy": 0.3})  # Large empathy boost
    npcs_dict = {name: npc.remnants for name, npc in manager.npcs.items()}
    scene2 = generate_scene(npcs_dict, 2, context="resolution")

    print("\nNPCs' Response to Your Empathy:")
    print_scene(scene2, summary_only=True)

    if scene2['dominant_mood'] == "empathy":
        print("\n✓ Success! The crowd softens.")
        print("✓ Sera extends her hand. Ravi nods respectfully.")
        print("✓ Even Drossel seems... less hostile.")
    else:
        print("\n✗ They remain unconvinced.")
        print("✗ You may need a different approach.")

    # Show individual trait changes
    print("\n--- INDIVIDUAL SHIFTS ---")
    for npc_encounter in scene2['npcs']:
        npc = manager.get_npc(npc_encounter['npc'])
        print(f"{npc_encounter['npc']:12} | Dominant: {npc_encounter['dialogue_meta']['dominant_trait']:12} ({npc_encounter['dialogue_meta']['dominant_value']})")

# Run it:

# scene_marketplace_conspiracy()
```


**Expected Output:**

```
TURN 1 (Conflict):
Dominant Mood: SKEPTICISM
[Multiple NPCs speaking harshly, doubting you]

TURN 2 (Resolution + Empathy):
Dominant Mood: EMPATHY
[NPCs softening, listening to your perspective]

INDIVIDUAL SHIFTS:
Sera         | Dominant: empathy         (0.95)
Ravi         | Dominant: empathy         (0.85)
Mariel       | Dominant: empathy         (0.88)
[etc]
```

## 

## Scene 6: Tutorial - Learning the System

**Setup:** Simple first-time dialogue teaching player the mechanics.

```python
def scene_tutorial_dialogue_mechanics():
    """Tutorial showing how dialogue changes based on choices."""
    from velinor.engine.npc_manager import NPCManager, create_marketplace_npcs
    from velinor.engine.npc_dialogue import generate_dialogue, generate_choices

    manager = NPCManager()
    manager.add_npcs_batch(create_marketplace_npcs())

    print("\n📖 TUTORIAL: DIALOGUE SYSTEM\n")

    sera = manager.get_npc("Sera")

    print("--- Before Any Interaction ---")
    print(f"Sera's Empathy: {sera.remnants['empathy']}")
    d1 = generate_dialogue("Sera", sera.remnants)
    print(f"Sera says: {d1}\n")

    print("--- You Show Compassion (Empathy Choice) ---")
    manager.apply_tone_effects({"empathy": 0.2})
    sera = manager.get_npc("Sera")
    print(f"Sera's Empathy: {sera.remnants['empathy']}")
    d2 = generate_dialogue("Sera", sera.remnants)
    print(f"Sera says: {d2}\n")

    print("--- You Show Understanding (Wisdom + Empathy) ---")
    manager.apply_tone_effects({"wisdom": 0.1})
    sera = manager.get_npc("Sera")
    print(f"Sera's Empathy: {sera.remnants['empathy']}")
    d3 = generate_dialogue("Sera", sera.remnants)
    print(f"Sera says: {d3}\n")

    print("KEY INSIGHT:")
    print("✓ Higher empathy → Sera's dialogue uses words like 'bloom', 'soften', 'gentle'")
    print("✓ Lower empathy → Sera's dialogue uses words like 'fragile', 'fade', 'wither'")
    print("✓ Your choices shape how she speaks to you")

# Run it:

# scene_tutorial_dialogue_mechanics()
```

## 

## Scene 7: Branching Story Based on Reputation

**Setup:** How past interactions affect current dialogue.

```python
def scene_reputation_system():
    """Same encounter with different histories produces different dialogue."""
    from velinor.engine.npc_manager import NPCManager, create_marketplace_npcs
    from velinor.engine.npc_encounter import generate_encounter, print_encounter

    print("\n🏆 REPUTATION SYSTEM\n")

    # Scenario A: First-time meeting
    print("--- SCENARIO A: First Time Meeting ---")
    manager_a = NPCManager()
    manager_a.add_npcs_batch(create_marketplace_npcs())

    kaelen_a = manager_a.get_npc("Kaelen")
    enc_a = generate_encounter("Kaelen", kaelen_a.remnants, 1, context="greeting")
    print("Kaelen (First meeting):")
    print_encounter(enc_a, full_details=False)

    # Scenario B: You've been helping the marketplace (high trust)
    print("\n--- SCENARIO B: After Many Acts of Kindness ---")
    manager_b = NPCManager()
    manager_b.add_npcs_batch(create_marketplace_npcs())

    # Simulate past interactions boosting all NPCs
    for _ in range(5):
        manager_b.apply_tone_effects({"empathy": 0.15, "wisdom": 0.1})

    kaelen_b = manager_b.get_npc("Kaelen")
    enc_b = generate_encounter("Kaelen", kaelen_b.remnants, 1, context="greeting")
    print("Kaelen (After 5 kind acts):")
    print_encounter(enc_b, full_details=False)

    print("\n✓ Same NPC, same context, different history → different dialogue")
    print(f"Kaelen's trust: {kaelen_a.remnants['trust']:.2f} → {kaelen_b.remnants['trust']:.2f}")
    print(f"Kaelen's empathy: {kaelen_a.remnants['empathy']:.2f} → {kaelen_b.remnants['empathy']:.2f}")

# Run it:

# scene_reputation_system()
```

## 

## Running These Scenes

Copy any function into your game code, then:

```python
from dialogue_story_examples import *

# Run individual scenes:
scene_marketplace_greeting()
scene_sera_redemption_arc()
scene_kaelen_betrayal_to_redemption()
scene_drossel_deal()
scene_marketplace_conspiracy()
scene_tutorial_dialogue_mechanics()
scene_reputation_system()
```


Each scene demonstrates different dialogue system capabilities:
- **Scene 1:** Multi-NPC simultaneous reactions
- **Scene 2:** Emotional progression (3-turn arc)
- **Scene 3:** Branching paths (aggressive vs. empathetic)
- **Scene 4:** Conditional outcomes (trust determines success)
- **Scene 5:** Group dynamics (majority mood shift)
- **Scene 6:** Learning mechanics (before/after comparison)
- **Scene 7:** Historical persistence (reputation effects)
## 

## Key Takeaways

All these scenes use the **same underlying system**: 1. Generate dialogue from current REMNANTS 2.
Show player choices 3. Apply choice as TONE effect 4. Regenerate dialogue with new traits 5. Repeat
until story beat complete

**No branching trees. No hand-coded branches. Just personality + choice = emergent narrative.**

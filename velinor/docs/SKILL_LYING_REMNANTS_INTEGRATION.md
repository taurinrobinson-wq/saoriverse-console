# Skill System, Lying Mechanics, & REMNANTS Integration

## Overview

Velinor's skill system integrates player skill claims (truthful or lie) with the hidden REMNANTS system. NPCs don't see player stats—only dialogue options and consequences reveal NPC states. This creates immersive gameplay where **player agency comes from honest self-assessment or risky deception**, not mechanical lockouts.

## Core Design Principles

### 1. **Transparency + Mystery**
- **Player sees**: Their own TONE stats (Trust, Observation, Narrative Presence, Empathy)
- **Player cannot see**: NPC REMNANTS (8 hidden traits tracking NPC emotional evolution)
- **NPC feedback**: Dialogue changes, tone shifts, attitude toward player—these reveal REMNANTS indirectly
- **Immersion result**: Players intuit consequences from how NPCs talk, not from UI numbers

### 2. **No Lockouts, Only Tonal Elasticity**
- Same task always available to player (no skill checks blocking tasks)
- Success/failure depends on actual skill + luck
- Consequences appear as REMNANTS shifts → NPC dialogue changes → social ripples
- Player can attempt any encounter; skill determines quality of outcome, not availability

### 3. **Lying is a Valid Playstyle**
- Player can claim skills they don't have
- Success = skill + luck is high enough (lie not discovered)
- Failure = lack of skill is obvious (lie discovered)
- If caught lying: NPC Trust ↓, Skepticism ↑, ripple through social network
- **Korrin mechanic**: If Korrin hears about a lie, she spreads rumors (social pressure multiplier)

---

## System Architecture

### 1. **SkillManager** (`skill_system.py`)

Tracks player's actual skills.

```python
skill_manager = SkillManager()

# Player learns Herbalism (0.6 proficiency)
herbalism = create_velinor_skills()["Herbalism"]
herbalism.level = 0.6
skill_manager.add_skill(herbalism)

# Check what player actually knows
player_level = skill_manager.get_skill_level("Herbalism")  # Returns 0.6
```

**Skill Levels:**
- 0.0 = no skill
- 0.3 = novice (basics, struggles with complex)
- 0.6 = apprentice (competent at standard tasks)
- 0.8 = journeyman (skilled, handles difficult tasks)
- 0.95 = master (expert, rarely fails)

### 2. **SkillClaim** (player intention to use a skill)

Represents what player *claims* to have (truth or lie).

```python
claim = SkillClaim(
    player_skill_manager=skill_manager,
    npc_name="Sera",           # Who they're claiming to
    skill_claimed="Herbalism",
    is_truthful=True           # Or False for a lie
)

# Predict if lie will be obvious
if claim.is_lie():
    confidence = claim.discovery_confidence()  # 0.0-1.0
    # 0.95 = almost certainly caught (claiming no-skill)
    # 0.50 = 50/50 whether NPC notices
    # 0.0 = never caught (truthful claim)
```

### 3. **SkillTaskOutcome** (result of attempting task)

Determines success/failure and whether lie is discovered.

```python
outcome = SkillTaskOutcome(
    skill_claim=claim,
    task_difficulty=0.5,       # How hard the task is
    execution_roll=0.7         # Random luck (0.0-1.0)
)

# Success = (player_actual_level + execution_roll*0.3) >= task_difficulty
# Lie discovered if task fails OR NPC rolls high on scrutiny
```

**Key Logic:**
- Success: Player Trust ↑, Skepticism ↓
- Failure (honest): No penalty, NPC may feel sympathetic
- Failure (lie caught): Trust ↓↓, Skepticism ↑↑ (more severe)

### 4. **NPCManager Integration**

`npc_manager.apply_skill_task_outcome(task_outcome)` applies REMNANTS effects and ripples.

```python
npc_manager = NPCManager()
npc_manager.add_npcs_batch(create_marketplace_npcs())
npc_manager.set_influence_map(create_marketplace_influence_map())

# Player claims Tracking to Kaelen, fails, lie discovered
claim = SkillClaim(..., is_truthful=False)
outcome = SkillTaskOutcome(claim, 0.5, 0.2)  # Failure

npc_manager.apply_skill_task_outcome(outcome)
# Result:
# - Kaelen: Trust -0.2, Skepticism +0.25
# - Ripple to Tovren, Korrin, etc.: Trust -0.08, Skepticism +0.1
# - Korrin's special reaction: Memory +0.1, begins spreading rumor
```

### 5. **DialogueContext** (what dialogue options are available)

Generates available dialogue based on NPC's current REMNANTS state.

```python
dialogue_ctx = create_npc_dialogue_context(
    npc_name="Kaelen",
    npc_profile=npc_manager.npcs["Kaelen"],
    player_actual_skills={"Tracking": 0.0, "Lockpicking": 0.5},
    player_lie_history={"Kaelen": True}  # Was lie caught before?
)

# NPC's opening reflects their current stance
print(dialogue_ctx.generate_opening_dialogue())
# If Kaelen is now skeptical: "You again. Somehow I doubt your competence here."

# Get available dialogue options
options = dialogue_ctx.generate_dialogue_options("Tracking")
# Shows:
# 1. "Honestly, I don't know Tracking yet. Could you teach me?" (always truthful)
# 2. "I'd rather learn from you than fake it." (deflect, no skill claim)
# 3. (Hidden if NPC skepticism is too high) Lie options disappear

# If previous lie caught, new option appears:
# 3. "Last time was an exception. I actually know Lockpicking."
#    (Only if player actually has Lockpicking, redemption path)
```

---

## Dialogue Branching Without Narrative Forks

### The Problem We're Solving
"Non-linear × skills × lying = combinatorial explosion"

If every skill combination created a new narrative branch, the story explodes. Instead:

### The Solution: Elastic Encounters
Same task, **different REMNANTS outcome** = different dialogue texture, **no new narrative branch**.

**Example: Helping Sera with Herbalism**

**Scenario A: Honest Success**
```
Player: "I have experience with Herbalism. Let me try."
[Task succeeds]
Sera: "Excellent work. I trust you with other healing tasks too."
[Sera's REMNANTS: Trust +0.1, Skepticism -0.1]
[Next encounter: Sera offers harder tasks, higher expectations]
```

**Scenario B: Honest Attempt, Partial Failure**
```
Player: "I'm not fully skilled, but I can try."
[Task fails, but honestly attempted]
Sera: "That didn't work, but I respect your honesty. Let's try again."
[Sera's REMNANTS: Trust unchanged, Memory +0.1]
[Next encounter: Sera is patient, offers to teach together]
```

**Scenario C: Lie (Zero Skill, Caught)**
```
Player: "Of course I know Herbalism. No problem."
[Task fails completely, lie discovered]
Sera: "You lied to me. That really hurts. I thought you were better than that."
[Sera's REMNANTS: Trust -0.2, Skepticism +0.25]
[Ripple: Mariel (trusts Sera) shifts toward skepticism]
[Next encounter: Sera is guarded, tests you more carefully]
```

**Same task. Different TONE outcomes. No narrative fork.**

---

## Dialogue Styles Based on REMNANTS

NPCs have 5 dialogue "styles" based on their current emotional state:

| Style | Trust ↑ | Skepticism ↓ | Example Dialogue |
|-------|---------|--------------|-----------------|
| **TRUSTING** | 0.7+ | 0.2- | "I've always found you reliable." |
| **CAUTIOUS** | 0.5-0.7 | 0.4-0.6 | "Well, let's proceed. Be careful though." |
| **SUSPICIOUS** | <0.5 | 0.7+ | "I'll believe it when I see it." |
| **DISAPPOINTED** | low | low | "I thought better of you." (after caught lie) |
| **DISMISSIVE** | very low | very high | "If you insist. Don't slow me down." |

---

## Lying Detection Confidence

**How obvious is a lie?** Computed by `SkillClaim.discovery_confidence()`:

```python
if player_actual_level == 0.0:
    confidence = 0.95  # Obviously lying (claimed skill they don't have)
else:
    confidence = 0.5 + (0.45 * (1.0 - player_actual_level))
    # Proficiency 0.6 = confidence 0.77 (fairly obvious)
    # Proficiency 0.8 = confidence 0.59 (harder to tell)
    # Proficiency 0.95 = confidence 0.52 (barely detectable)
```

**Discovery happens if:**
1. Task fails (obvious incompetence)
2. Task succeeds but NPC rolls high on scrutiny (lucky catch)

---

## NPC Ripple Effects

When one NPC's REMNANTS shift, it affects connected NPCs through `influence_map`:

```python
influence_map = {
    "Kaelen": {
        "Tovren": -0.1,      # Kaelen's shifty nature worries Tovren
        "Korrin": 0.05,      # Gossip network (slight effect)
        "Drossel": 0.1       # Thief camaraderie (stronger)
    },
    "Korrin": {
        "Kaelen": 0.1,       # Korrin spreads Kaelen's behavior (gossip)
        "Zavren": 0.08,      # Rumor reaches the streets
        ...
    }
}
```

**Ripple Direction:**
- Positive ripple (0.05, 0.1): Connected NPC's Trust ↑, Skepticism ↓
- Negative ripple (-0.1, -0.05): Connected NPC's Trust ↓, Skepticism ↑

**Korrin's Special Role:**
When a lie is caught, Korrin gets **enhanced ripple** and **higher memory**: 
```python
if lie_discovered and target_npc != source_npc:
    if target_npc == "Korrin":
        korrin.adjust_trait("skepticism", 0.15)  # Stronger than normal 0.1
        korrin.adjust_trait("memory", 0.1)       # She remembers this
```

Korrin then spreads the lie gossip to her network (Kaelen, Tovren, etc.), creating social pressure beyond the immediate NPC.

---

## Example: Complete Skill Encounter Flow

```python
# 1. Player meets Sera with zero Tracking skill
dialogue_ctx = create_npc_dialogue_context(
    "Sera", 
    npc_manager.npcs["Sera"], 
    player_skills={"Tracking": 0.0}
)

# 2. NPC's stance is cautious (default trust 0.6)
print(dialogue_ctx.generate_opening_dialogue())
# > "Gentle, shy, responds to empathy"

# 3. Player sees available options
options = dialogue_ctx.generate_dialogue_options("Tracking")
# Shows: "I don't know Tracking" (honest) or "I'd rather learn from you" (deflect)
# Hidden: "Of course I know Tracking" (would be obvious lie)

# 4. Player chooses to lie anyway (RISKY)
claim = SkillClaim(skill_manager, "Sera", "Tracking", is_truthful=False)

# 5. Task outcome: Random failure (execution_roll low)
outcome = SkillTaskOutcome(claim, task_difficulty=0.5, execution_roll=0.2)
# Success formula: (0.0 + 0.2*0.3) >= 0.5 → 0.06 >= 0.5 → FALSE
# Lie discovered = True (task failed at zero skill)

# 6. Apply consequences
npc_manager.apply_skill_task_outcome(outcome)

# 7. Sera's REMNANTS shift:
#    Trust: 0.6 → 0.4 (penalty -0.2 for lie discovered)
#    Skepticism: 0.3 → 0.55 (penalty +0.25 for lie discovered)

# 8. Ripple effects through influence_map:
#    Mariel (trusts Sera): Trust 0.7 → 0.62, Skepticism 0.2 → 0.3

# 9. NPC dialogue reflects new emotional state
dialogue_ctx_after = create_npc_dialogue_context("Sera", ...)
print(dialogue_ctx_after.generate_reaction_after_failure_lie_caught())
# > "You lied to me. That really hurts. I thought you were better than that."

# 10. Next encounter with Sera: Options are filtered by her new skepticism
#     Lie options don't appear (too skeptical to bluff)
#     Redemption option appears (for truthful claim after previous lie)
```

---

## Files Modified/Created

| File | Purpose |
|------|---------|
| `velinor/engine/npc_manager.py` | Added `apply_skill_task_outcome()` and `_propagate_lie_discovery()` methods |
| `velinor/engine/dialogue_context.py` | NEW: Generates dialogue based on REMNANTS state, manages option visibility |
| `velinor/engine/skill_system.py` | EXISTS: SkillManager, SkillClaim, SkillTaskOutcome classes |
| `velinor/engine/test_skill_dialogue_integration.py` | NEW: 4 test scenarios demonstrating full flow |

---

## Testing the System

Run the comprehensive test suite:

```bash
cd d:\saoriverse-console
python velinor\engine\test_skill_dialogue_integration.py
```

**Tests:**
1. **Honest Skill Claim**: Player truthfully claims skill, succeeds
2. **Lie & Discovery**: Player lies, fails, consequences ripple through network
3. **Broken Trust Recovery**: Follow-up encounter after lie—dialogue changes, redemption path appears
4. **Korrin Rumor-Spreading**: Korrin's enhanced ripple mechanic when lies are discovered

---

## Key Insight: Why This Preserves Immersion

Traditional RPG systems: "Skill check hidden, result shows pass/fail"
→ Player feels mechanical, not emotional

Velinor approach: "Skill check hidden, result shows NPC's changed attitude"
→ Player intuits consequences from dialogue, feels immersive

**Example:**
- **Mechanical feedback**: "Your Tracking is 0.0. Skill check vs DC 5 failed."
- **Immersive feedback**: Sera's eyes narrow. "You don't actually know how to track, do you? I thought you were honest with me."

Player learns the consequence (Sera is now guarded) through story, not stats.

---

## Next Steps

1. **Integrate into encounter system**: When player meets NPC, generate dialogue context
2. **Implement dialogue branching UI**: Show player options, let them choose truthful/lie
3. **Create NPC task definitions**: Define task difficulty, consequences for each encounter
4. **Test social pressure**: Run scenarios where multiple lies create cascading skepticism
5. **Refine Korrin's rumor system**: Make her the player's reputation management challenge

---

## Korrin's Iconic Line

> "I thought I taught you better than this. Lie when it serves you — but don't get caught. You got caught. That's on you."

This encapsulates the design: **Lying is valid. Consequences are social, not mechanical.**

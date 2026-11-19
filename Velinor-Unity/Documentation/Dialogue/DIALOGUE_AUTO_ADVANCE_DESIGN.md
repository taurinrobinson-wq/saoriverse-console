# Dialogue Auto-Advance System Design

## Overview

A narrative-aware auto-advance feature that automatically progresses `Continue` dialogue beats after appropriate reading time, while pausing indefinitely on TONE choice prompts. This creates a cinematic pacing for witnessed scenes while maintaining player agency at moments of participation.

**Core Narrative Grammar:**
- **Continue = Observe the conversation** (auto-advances when enabled)
- **TONE choices = Enter the conversation** (always pauses for player input)

## Behavior Rules

### When Auto-Advance is OFF
- Every `Continue` beat requires explicit player input
- TONE choice beats wait for player input (always required)
- Traditional dialogue pacing

### When Auto-Advance is ON

#### Continue Beats (NPC-to-NPC dialogue)
1. Display the line
2. Wait for calculated reading time (see **Reading Time Calculation** below)
3. Auto-advance to next beat
4. Repeat until TONE choices appear

#### TONE Choice Beats
1. Display all four TONE options (Trust, Observation, Narrative, Empathy)
2. **PAUSE INDEFINITELY** — wait for player input
3. Player selects one TONE
4. Display branch-specific NPC response
5. If Auto-Advance is still toggled ON, resume auto-advancing after the response

#### Toggle Persistence
- Auto-Advance toggle state **persists** across TONE choices
- Player does **not** have to re-enable it after each choice
- Player can toggle Auto off at any point to regain manual control

## Reading Time Calculation

Base the auto-advance delay on **text length** with a **minimum floor**:

```
delay = max(MIN_DELAY, BASE_RATE * character_count)

Suggested values:
- MIN_DELAY: 1.5 seconds (for very short lines like "Hmph.")
- BASE_RATE: 0.03 seconds per character (reading speed ~20 chars/sec)
- MAX_DELAY: 8 seconds (optional cap for very long dialogue)
```

**Example timing:**
- `"Hm."` (2 chars) → 1.5s minimum
- `"I mean… you surprised me."` (28 chars) → 1.84s (capped at minimum)
- `"Getting everyone involved in this. Organizing them. Keeping them at it."` (71 chars) → 2.13s
- Longer monologues → proportional delay, up to reasonable cap

This prevents short, impactful lines from vanishing instantly while giving proper reading time to substantial dialogue.

## UI Implementation

**Dialogue Panel Enhancement:**
- Add a small **▶ / ⏸** toggle control to the existing dialogue panel
- Visual indicator that shows current auto-advance state
- No additional UI menu or settings subsystem needed
- Toggle remains accessible throughout gameplay

**Interface Signal:**
When auto-advance is active and the display **stops mid-scene and shows choices**, the pause itself communicates: "You are now a participant in this conversation."

## Scene Examples

### Lighthouse Part I (Mostly Witnessed)

With Auto ON, this flows cinematically without manual intervention:

```
Malrik: "Hmph… you surprised me."
[1.5s] →
Elenya: "Sorry. Did I sneak up on you?"
[2.1s] →
Malrik: "No. I mean… you surprised me."
[2.5s] →
Elenya: "Oh?"
[1.5s] →
Malrik: "Getting everyone involved in this. Organizing them. Keeping them at it."
[2.1s] →
...continues until end of scene
```

### Lighthouse Part II (Witnessed Until Participation)

The auto-pause on choices signals the narrative shift:

```
Malrik: "Lioren. How long have you been standing there?"
[2.3s] →

🛑 AUTO-PAUSE 🛑

[Trust] Not long. I wasn't trying to listen.
[Observation] Long enough to hear you call Elenya a decent leader.
[Narrative] Long enough to be surprised to find the two of you up here together.
[Empathy] I can give you two a minute.

← Player now chooses →
```

This natural pause tells the player: *"Your presence matters now. What will Lioren do?"*

## Extension Points for Future Evolution

### Voice Acting Integration
- When voice clips are added, use **audio clip duration** as the auto-advance trigger
- Replace manual reading-time calculation with actual playback time
- Extends naturally to: dialogue continues until voice finishes, then auto-advances

### Adaptive Pacing
- Could vary minimum delay based on **speaker** (Malrik's dry quips might feel snappier than Elenya's reverent observations)
- Could vary based on **scene context** (slower pacing during emotionally heavy moments)
- Could vary based on **player preference** via settings

### Advanced Features (Future Consideration)
- Keyboard/gamepad shortcut to manually advance during auto-play
- Fade-out indicator showing time until next auto-advance
- Rewind capability for witnessed scenes
- Scene replay mechanics for favorite dialogues

## Implementation Checklist

- [ ] Add `auto_advance_enabled` toggle to dialogue UI
- [ ] Implement reading-time calculation based on text length
- [ ] Modify dialogue manager to auto-advance on Continue beats when enabled
- [ ] Ensure TONE choice beats always pause regardless of toggle state
- [ ] Persist toggle state across scenes
- [ ] Allow manual toggle during active dialogue
- [ ] Test with existing dialogue files (lighthouse Part I/II, Ravi/Nima, etc.)
- [ ] Ensure accessibility (players should always be able to disable auto-advance)

## Design Philosophy

This feature **does not replace player agency**—it enhances narrative pacing while maintaining it. The player always has immediate control, and the auto-pause on choices is a design signal, not a forced wait state. The feature becomes more than a convenience when the **interface itself reinforces the story grammar**: observation mode vs. participation mode.

By basing reading time on actual text, not arbitrary timed sequences, the feature respects both short, punchy exchanges and longer revelations with equal care.

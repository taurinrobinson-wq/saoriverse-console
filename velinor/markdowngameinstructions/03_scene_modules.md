# Scene Module Template: Reusable NPC Encounters

## Overview
A standardized structure for building **modular NPC encounter scenes** with:
- Background/foreground asset layering
- Multi-stage presence (distant → near)
- Glyph resonance triggers
- Dialogue bubble progression
- Player choice architecture
##

## Template Structure

### Scene Metadata

```text
```

Scene ID:             Unique identifier (e.g., market_intro_velinor_01)
Background Image:     Path to background asset
Foreground Image:     Path to NPC/character asset
Ambient Sound:        Optional audio layer
Glyph Triggers:       Glyphs activated during scene
NPC Name:             Primary character in scene

```



### Scene 1: Distant Presence

**Purpose**: Establish atmosphere and introduce the NPC from a distance

```markdown


## Scene 1: Distant Presence

**Visual Setup**:
- Background Image: [full marketplace/environment]
- Foreground Image: [NPC scaled small, lower opacity]
- Position: Far background, center or off-center

**Narration**:
[2-3 lines establishing the NPC's presence, appearance, mood]
[Avoid revealing too much; maintain mystery]

**Sensory Layer** (Ambient Sound):
[Wind, music, marketplace sounds, chimes, etc.]

**Glyph Glow**:

```text
```




**Design Notes**:
- Foreground opacity: 40-60%
- Foreground scale: 0.6-0.7x normal
- Narration tone: Observational, not yet intimate
- Glyph is *passive* — just awareness beginning
##

### Scene 2: Approach

**Purpose**: Collapse distance; establish connection

```markdown

## Scene 2: Approach

**Visual Setup**:
- Background Image: [same or adjusted for proximity]
- Foreground Image: [NPC scaled larger, full opacity]
- Position: Center, larger, immediately present

**Narration**:
[NPC moves closer or player is suddenly face-to-face]
[Emotional shift: intrigue, intimidation, recognition]

**Dialogue Bubble (NPC)**:
[2-4 lines of opening dialogue]
[Establish tone: reverent, challenging, mysterious, warm]

**Glyph Glow**:
```text
```text
```



**Design Notes**:
- Foreground opacity: 100%
- Foreground scale: 1.0x (full size) or 1.1x (commanding presence)
- Dialogue is the **first interaction** — tone is crucial
- Glyphs now *active* — resonance responding to moment
##

### Scene 3: Player Response (Optional Multi-Stage)

**Purpose**: Branch based on player choice

```markdown


## Player Options

**Option A: [Dialogue Choice 1]**
- Glyph Trigger: [Querrä] (inquiry)
- NPC Response: [2-3 lines]
- Foreground Shift: [Static or alternate expression]

**Option B: [Dialogue Choice 2]**
- Glyph Trigger: [Thalen̈] (longing)
- NPC Response: [2-3 lines, different tone]
- Foreground Shift: [Static or alternate expression]

**Option C: [Dialogue Choice 3 — Silence/Observation]**
- Glyph Trigger: [Aelitḧ] (stillness, witness)
- NPC Response: [NPC reacts to player's silence]

```text
```




**Design Notes**:
- Each option should feel **meaningfully different**
- NPC responses vary not just in content but in **tone and pacing**
- Glyphs reflect player's internal state, not just NPC action
- One path can lead to faster trust; others preserve mystery
##

## Example: Velinor's First Encounter

### Scene Metadata

```
Scene ID:             market_intro_velinor_01
Background Image:     velinor_marketplace_distant.png
Foreground Image:     velinor_priestess_distant.png (Scene 1)
                      velinor_priestess_close.png (Scene 2)
Ambient Sound:        wind_through_ruins.mp3 + faint_chimes.mp3
Glyph Triggers:       [Esḧ], [Cinarä̈], [Brethielï̈], [Querrä], [Thalen̈], [Aelitḧ]
```text
```text
```



### Scene 1: Distant Presence

```


## Scene 1: Distant Presence

**Visual**:
- Velinor visible amid marketplace ruins, still and observant
- Draped in dark teal robe with symbols you don't recognize
- Presence feels older than appearance suggests

**Narration**:
You notice someone in the distance.
She stands still amid the ruins, as if she's been waiting.
She appears to be some kind of priestess… or something older.

**Ambient Sound**: Wind through broken towers, faint chime resonance

```text
```




### Scene 2: Approach

```

## Scene 2: Approach

**Visual**:
- Velinor steps closer, eyes unblinking, gaze locked on player
- Foreground now fills center of vision
- Emotional tension: intrigued + intimidated

**Narration**:
She comes closer to you.
Her eyes are transfixed on you — unblinking, unreadable.
You are intrigued. And a little intimidated.
Before you have a chance to speak, she does.

**Dialogue**:
"I see you. Not just your shape… but your ache."
"I am Velinor. And you are not lost — only unremembered."

```text
```text
```



### Player Options

```

**Option A**: "Who are you really?"
- Glyph: [Querrä] (inquiry) glows
- Velinor Response: "A question for another day. First, you must listen."
- Foreground: Velinor's expression softens slightly

**Option B**: "What do you mean, 'unremembered'?"
- Glyph: [Thalen̈] (longing) glows
- Velinor Response: "The glyphs will show you. But you must be ready to see."
- Foreground: Velinor's hand extends, palm open

**Option C**: [Remain silent]
- Glyph: [Aelitḧ] (stillness) glows
- Velinor Response: "Good. You know when to listen. That is rare."

```text
```



##

## Implementation Guide

### For Streamlit Integration

```python

# Scene 1: Distant presence
col1, col2 = st.columns([3, 1])
with col1:
    background = st.image("velinor_marketplace_distant.png")
    foreground = st.image("velinor_priestess_distant.png", width=150)

# Display narration and glyph
st.write("You notice someone in the distance...")
display_glyph([Esḧ])

# Player advances (button, timer, or next section)
if st.button("Continue"):
    # Scene 2: Approach
    st.image("velinor_marketplace_distant.png")
    st.image("velinor_priestess_close.png", width=400)
    st.write("She comes closer to you...")
    display_dialogue("I see you. Not just your shape… but your ache.")

    # Player options
    choice = st.radio("How do you respond?",
        ["Who are you really?",
         "What do you mean, 'unremembered'?",
         "Remain silent"])

    if choice == "Who are you really?":
        trigger_glyph([Querrä])
        st.write("Velinor Response: 'A question for another day...'")
```



##

## Reuse Across NPCs

This template is **standardized** so you can quickly create encounters for:
- Nima (Mistrusting Guard)
- Ravi (Welcoming Guide)
- Shrine Keepers
- Mysterious Travelers
- Saori (later encounter)

Each NPC gets their own **Scene Metadata** and **Scene 2+ Dialogue**, but the structure remains consistent.

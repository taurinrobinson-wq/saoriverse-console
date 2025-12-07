# NPC Reaction Library: Reusable Dialogue & Responses

## Overview
A **palette of interchangeable dialogue lines** for NPCs to react to collapse events, player choices, and marketplace moments. Mix and match based on NPC personality, trust level, and story context.

---

## Static NPC Reactions (Desensitized to Collapse)

### Resigned Tone
```
"Looks like you really are new to the city.
You get used to it. We barely notice it now."

"Another wall falls, another path closes.
We've stopped counting."

"The city argues with itself. We learned to sleep through it."

"You'll understand soon enough. Collapse is just Tuesday here."

"Your shock will fade. Then you'll be like us."
```

### Wry/Dark Humor Tone
```
"The city's sense of humor is getting darker every day."

"At least it makes the maze interesting.
Keeps everyone on their toes."

"It's not collapse anymore — it's just redecorating."

"The merchants complain, but honestly? Keeps business unpredictable."

"You get numb to anything if it happens enough times."
```

### Ritualized Tone
```
"The city exhales. We breathe with it.
Collapse is just another rhythm."

"The earth remembers. We are small within it."

"This is the way of things now. There is grace in acceptance."

"We move with the city's heartbeat, not against it."

"Collapse speaks. Those who listen survive."
```

---

## Reactive NPC Reactions (Still Affected by Collapse)

### Fearful Tone
```
"I thought that was it. I thought we were finally coming down."

"Did you feel that? The ground almost gave way!
It still shakes me every time."

"Will it ever stop? Some days I wonder if we're all just waiting for the final collapse."

"That's... that's closer than last time. The collapses are getting closer."

"I had family in that sector. I have to check if they're—"
```

### Empathetic Tone
```
"Are you alright? New arrivals always find this unsettling."

"It gets easier. The fear, I mean. But it takes time."

"I still flinch. I think that's normal, even after all this time."

"Your hands are shaking. Mine did too, the first time.
Come, sit. It will pass."

"I understand. This is your first real taste of how fragile we all are."
```

### Determined Tone
```
"Another collapse means new opportunities. Stay alert."

"This is how we learn the city. Through its changes."

"Could be dangerous, but it could also mean new resources, new paths."

"Every collapse teaches us something. Pay attention."

"The city tests us. Those who adapt, survive."
```

---

## Generic Closing Line (All NPCs, Post-Collapse)

### Standard Version
```
"We must be going. A new passageway may have opened up in the collapse.
We suggest you keep track of your surroundings.
The only constant here is change."
```

### Alternate Versions by Tone

**Ominous**:
```
"The city devours itself. Best not to be caught in its mouth.
Watch the map. Watch the ground. Watch your back."
```

**Hopeful**:
```
"Collapse opens doors. Keep your eyes sharp for what emerges.
Sometimes loss is just opportunity in disguise."
```

**Ritualized**:
```
"The city remembers. We walk the broken paths. You will learn.
The map is your first teacher. The collapse is the second."
```

**Practical**:
```
"Mark it on your mental map where the blockage is.
The city changes constantly — staying oriented is half the battle."
```

---

## Player Dialogue Response Options

### Shock/Alarm
```
"What was that? Are you two okay!?
I'm surprised you didn't even flinch."

"Did the whole marketplace just shake, or is it just me?"

"Should we be running? Should I be more worried?"

"How often does that happen? Is this normal?!"
```

**Glyph Trigger**: [Thalen̈] (longing, concern)
**NPC Reading**: Player is new, sensitive, inexperienced

---

### Observation/Inquiry
```
"I'm surprised you didn't even flinch."

"That didn't seem to bother you at all.
Does everyone just... accept this?"

"How long have you been living like this?
You don't even react anymore."

"It's fascinating how differently we respond.
You're so calm, and I'm terrified."
```

**Glyph Trigger**: [Querrä] (inquiry, observation)
**NPC Reading**: Player is perceptive, learning, analytical

---

### Acceptance/Stillness
```
[Remain silent, observing both the collapse and the NPCs' reaction]

[Wait, watching how the NPCs respond before speaking]

[Take a breath, center yourself, acknowledge the change without fear]
```

**Glyph Trigger**: [Aelitḧ] (stillness, witness)
**NPC Reading**: Player has composure, wisdom, or shocking calm

---

## NPC Dialogue by Trust Level

### Low Trust (First Collapse Encounter)
- NPCs are more guarded in responses
- Static NPCs: Terse, unwelcoming
- Reactive NPCs: Slightly suspicious of player's reaction
- No personal details shared

**Example (Mistrusting NPC, Static)**:
```
"You're new. This is how things are now.
Best you get used to it fast or get out."
```

---

### Medium Trust (Repeated Encounters)
- NPCs begin to distinguish player from other outsiders
- Static NPCs: More resigned than hostile
- Reactive NPCs: Willing to acknowledge shared experience
- Hints of personal stories emerge

**Example (Mistrusting NPC, Medium Trust)**:
```
"You've been around a few days now. At least you don't panic like most.
The collapses... yeah, they're part of life. Learn the patterns."
```

---

### High Trust (Established Relationship)
- NPCs actively reassure or guide player
- Static NPCs: Share why they've hardened (story implicit)
- Reactive NPCs: Open about their ongoing fear or coping
- Full stories and motivations revealed

**Example (Mistrusting NPC, High Trust)**:
```
"I've lost people to these collapses. That's why I don't react anymore.
If I flinched every time, I'd never survive. You understand?
But you're different. You still feel. That's good. Don't lose that."
```

---

## Special Moments: Dialogue Combinations

### If Player Remains Calm During First Collapse
```
Velinor (Reactive NPC):
"Most new arrivals scream or panic.
You... you watched. You listened.
That is rare."

[Glyph resonance: [Aelitḧ] + [Cinarä̈] combine]
```

### If Player Shows Immediate Concern for NPC
```
Ravi (Welcoming NPC):
"You were worried about us. Even as a stranger.
That kindness... the city needs more of it.
I think you'll do well here."

[Glyph resonance: [Thalen̈] + [Brethielï̈] combine]
```

### If Player Questions the Cycle
```
Nima (Mistrusting NPC):
"You're asking the right question. 'Will it ever stop?'
The answer is... we don't know. That's what makes us human.
We keep going anyway."

[Glyph resonance: [Querrä] + [Ruuñ] + [Sha'rú] combine]
```

---

## Implementation Strategy

### For Streamlit Integration
```python
# Define reaction library
STATIC_NPC_RESPONSES = {
    "resigned": [
        "Looks like you really are new to the city. You get used to it.",
        "Another wall falls, another path closes. We've stopped counting.",
        # ... more variants
    ],
    "wry": [
        "The city's sense of humor is getting darker every day.",
        # ... more variants
    ],
    # ... more tones
}

REACTIVE_NPC_RESPONSES = {
    "fearful": [...],
    "empathetic": [...],
    "determined": [...]
}

# Use in collapse event
def trigger_collapse_event(npc_name, npc_archetype, npc_tone):
    # Select dialogue based on archetype and tone
    if npc_archetype == "static":
        dialogue = random.choice(STATIC_NPC_RESPONSES[npc_tone])
    else:
        dialogue = random.choice(REACTIVE_NPC_RESPONSES[npc_tone])
    
    # Trigger glyph
    trigger_glyph(get_resonance_for_tone(npc_tone))
    
    # Display dialogue
    st.write(dialogue)
```

---

## Notes for Consistency

- **Tone should match established NPC personality**
- **Trust level should gate deeper/more personal lines**
- **Collapse should always reference change/instability as core theme**
- **Player should feel heard — their shock is valid**
- **Glyphs tie emotional response to narrative world**

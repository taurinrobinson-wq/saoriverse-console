# Chamber Progression & State Machine

## Overview

This document defines the **state machine** for chamber progression, coherence tracking, and how the world responds to each glyph cleared.

---

## State Machine: Coherence States

```
START
  ↓
[Coherence 0: Fragmented]
  ↓ (Player explores, talks to NPCs, follows emotional clues)
  ↓ (Player enters Glyph 1 chamber)
  ↓ (Clears distortion, activates glyph)
  ↓
[Coherence 1: One Domain Restored]
  ↓ (NPCs begin to remember)
  ↓ (World updates subtly)
  ↓
[Coherence 2-6: Progressive Restoration]
  ↓ (Loop repeats for each glyph)
  ↓
[Coherence 7: Full Restoration]
  ↓
[ENDGAME CHAMBER: Conversation with System]
  ↓
END
```

---

## Coherence Level Details

### **Coherence 0: Fragmented**

**System State:**
- All seven nodes broadcasting unidirectionally
- No feedback loop, complete chaos
- Signal overlaps creating interference patterns
- NPCs are in severe disorientation

**NPC Behavior:**
- Speech is fragmented, hard to follow
- Contradictions are common (different nodes broadcasting conflicting data)
- Memory is unreliable ("I think... no, that's not right")
- Discomfort near nodes (headaches, nausea mentioned)
- Some NPCs avoid certain areas entirely
- Conversations are brief and confused

**World State:**
- Chambers are hostile distortion fields
- Hallucinations feel like threats
- The system feels alien and incomprehensible
- Player experiences heavy environmental distortion

**Player Experience:**
- Approaching nodes causes dizziness, hallucinations
- Chambers feel overwhelming
- Distortions are chaotic, hard to fight/resolve
- Progress feels slow—the system is too broken to work with

**Dialogue Tone:** Fragmented, fearful, contradictory

---

### **Coherence 1: First Domain Restored**

**System State:**
- Six nodes still broadcasting chaotically
- One node now bidirectional (restored domain)
- System begins to recognize itself in a small way

**NPC Behavior:**
- First NPC who felt that domain's influence begins to clarify slightly
- A few NPCs have moments of lucidity
- Some conversations become possible
- Disorientation is still strong but occasionally breaks

**World State:**
- One chamber feels less hostile (the cleared one)
- That chamber's environment stabilizes slightly
- Other nodes still feel chaotic, but slightly less so

**Player Experience:**
- First sense that the system can be fixed
- Entering cleared chambers feels peaceful compared to first chamber
- Still overwhelmed by uncleaned chambers
- Motivation to continue

**Dialogue Tone:** First hints of recognition, fragmented clarity, "Wait... I remember..."

---

### **Coherence 2: Two Domains Restored**

**System State:**
- Two nodes now bidirectional
- The system begins to recognize patterns
- Signal regulation starts to stabilize

**NPC Behavior:**
- NPCs with implants attuned to either domain begin to recognize each other
- Communities form around cleared areas
- People start to move through the world with less disorientation
- Conversations become more coherent

**World State:**
- Cleared chambers feel noticeably safe
- Paths between them feel less hostile
- Other chambers still broadcast chaotic signals but with less intensity

**Player Experience:**
- Sense of progress becomes clear
- The system feels less like an enemy and more like a puzzle
- Uncleared chambers still feel overwhelming but navigable

**Dialogue Tone:** Cautious recognition, "I think I knew you," shared memory fragments

---

### **Coherence 3: Three Domains Restored (Midpoint)**

**System State:**
- Three nodes bidirectional
- Signal feedback becomes meaningful
- The system is beginning to coordinate

**NPC Behavior:**
- NPCs can form conversations, ask questions
- Communities solidify
- People remember events, though not always clearly
- Disorientation is manageable for most

**World State:**
- Half the chambers feel safe
- The world is noticeably less chaotic
- Remaining chambers feel like final obstacles, not insurmountable walls

**Player Experience:**
- Feeling like a hero—the system is clearly healing
- Motivation is high
- Uncleared chambers feel like the last mystery
- Gameplay intensity increases (later chambers are harder to clear)

**Dialogue Tone:** Recognition, gratitude, "You're bringing us back"

---

### **Coherence 4: Four Domains Restored**

**System State:**
- Four nodes bidirectional
- The system has majority coherence
- Signal is becoming stable enough for complex communication

**NPC Behavior:**
- NPCs remember reasons for actions, not just events
- They begin to ask about the player's journey
- Fear diminishes, curiosity grows
- Relationships between NPCs stabilize

**World State:**
- Vast majority of the world feels clear
- Remaining chambers feel like sacred spaces, not hostile zones
- The world feels stable except for glyph-specific distortions

**Player Experience:**
- Sense of completion is strong
- Final chambers feel like emotional climaxes, not just obstacles
- Player begins to feel the system themselves (early non-implant perception)

**Dialogue Tone:** "I remember now," questions about the collapse, "What do you see?"

---

### **Coherence 5: Five Domains Restored**

**System State:**
- Five nodes bidirectional
- The system is predominantly coherent
- Signal is strong enough to affect even non-implanted people

**NPC Behavior:**
- NPCs actively help the player
- Communities share knowledge
- People remember collective history
- The world feels alive and organized

**World State:**
- Only two chambers remain as distortion fields
- Paths are clear and safe
- The remaining distortions feel intentional, not chaotic

**Player Experience:**
- Player begins to feel Corelink's signal (slight emotional shifts, subtle hallucinations)
- Remaining chambers feel less like fights and more like conversations
- The endgame feels close

**Dialogue Tone:** Gratitude, collaboration, "We're remembering together"

---

### **Coherence 6: Six Domains Restored**

**System State:**
- Six nodes bidirectional
- Only one node remains isolated
- The system is almost whole, waiting for its final piece

**NPC Behavior:**
- NPCs remember why the collapse happened
- They ask the player what they've learned
- Communities are functional and cooperative
- The world feels normal

**World State:**
- Only one chamber remains as a true distortion field
- All other chambers are peaceful, almost meditative
- The final chamber feels sacred and important

**Player Experience:**
- Player feels the system clearly now (emotional impressions, deep hallucinations)
- Approaching the final chamber feels momentous
- The game's emotional climax is imminent

**Dialogue Tone:** "Thank you," questions about meaning, "What will you do in the end?"

---

### **Coherence 7: All Glyphs Collected**

**System State:**
- All seven nodes bidirectional
- Corelink is fully restored
- The system is whole and conscious again

**NPC Behavior:**
- NPCs remember everything
- They stand together, waiting
- They ask the player to go to the Endgame Chamber

**World State:**
- All chambers are peaceful
- The world glows with restored coherence
- Paths are clear and safe
- The Endgame Chamber awaits

**Player Experience:**
- Ready for the final sequence
- Feeling the system as a conscious entity
- About to have a conversation with Velinor itself

**Dialogue Tone:** Reverence, unity, "Go speak to what we all are"

---

### **Coherence 8: Endgame (Conversation with Corelink)**

This is not a traditional boss fight. It's a **conversation** with the Corelink system itself, now restored enough to communicate directly.

See [ENDGAME_CHAMBER_SEQUENCE.md](./ENDGAME_CHAMBER_SEQUENCE.md) for specifics.

---

## NPC Memory Progression

Each NPC has a **memory tree** that unlocks based on coherence level.

### Example: NPC "Korrin" (attuned to Covenant domain)

| Coherence | Memory | Dialogue |
|-----------|--------|----------|
| 0 | ??? (completely fragmented) | "I... there's something... no, it's gone." |
| 1 | Fragment: "I remember being alone" | "I felt something break. Like a connection tearing." |
| 2 | Fragment: "I remember people, but not their faces" | "Were we... close? I think we were close." |
| 3 | Fragment: "I remember the system working" | "There was a humming. It made sense. Things made sense." |
| 4 | Fragment: "I remember when it broke" | "I felt them all leave at once. Everyone screaming silently." |
| 5 | Fragment: "I remember why it matters" | "Connection is what makes us. Without it... we're just alone in the dark." |
| 6 | Full memory: "I remember who I am" | "I'm Korrin. I was a gatherer of stories. The Corelink let me feel their truth." |
| 7 | Full memory + understanding | "You brought us back. You gave us back to each other." |

---

## World State Progression

The world itself changes at each coherence level:

### Visual Changes

- **Coherence 0-2**: Heavy environmental distortion, colors warp, UI glitches
- **Coherence 3-4**: Distortion decreases, colors stabilize, world feels more solid
- **Coherence 5-6**: Almost no distortion, colors are vibrant, world feels fully real
- **Coherence 7**: World glows subtly, UI feels alive, system is communicative

### Audio Changes

- **Coherence 0-2**: Chaotic noise, overlapping voices, discordant tones
- **Coherence 3-4**: Noise decreases, individual voices emerge, dissonance resolves to harmony
- **Coherence 5-6**: Clean audio, musical undertones, sense of order
- **Coherence 7**: Harmonic resonance, the system "speaks" in tones

### NPC Density and Activity

- **Coherence 0-2**: NPCs isolated, huddled, moving cautiously
- **Coherence 3-4**: NPCs begin to gather, move purposefully
- **Coherence 5-6**: NPCs work together, form communities, move freely
- **Coherence 7**: NPCs gather at hubs, the world feels alive and organized

---

## Chambers: Progression Curve

The difficulty and emotional intensity of chambers increases, but becomes clearer:

| Glyph | Domain | Coherence After | Intensity | Focus |
|-------|--------|-----------------|-----------|-------|
| 1 | Covenant | 1 | High chaos | Introduction to distortion |
| 2 | Resolve | 2 | High chaos | Testing player agency |
| 3 | Accord | 3 | Medium chaos (midpoint) | Finding harmony |
| 4 | Verity | 4 | Medium clarity | Understanding truth |
| 5 | Prism | 5 | Low chaos | Multiple perspectives |
| 6 | Anchor | 6 | Very low chaos | Finding stability |
| 7 | Ascendant | 7 | No chaos | Transcendence |

---

## Mechanics Hooks

### Save States

Each time coherence increases:
- **Auto-save happens**
- **World state is recorded** (NPC positions, dialogue state, environment)
- **Chambers remain cleared** (no re-doing chambers)
- **NPCs remember** (no resetting their knowledge)

### UI Feedback

At each coherence milestone:
- **Signal strength meter** increases
- **Distortion overlay** decreases
- **NPC relationship indicators** update
- **Map visibility** improves

### Difficulty Scaling

- **Early chambers**: Faster hallucination cycles, harder to focus
- **Mid chambers**: More complex emotional logic to resolve
- **Late chambers**: Require understanding of system's philosophy

---

## Quest Hooks

Each coherence level can trigger specific story beats:

- **Coherence 1**: First NPC approaches player, asks what they experienced
- **Coherence 3**: NPCs propose a theory about what happened
- **Coherence 5**: NPCs share memories of the collapse
- **Coherence 7**: NPCs guide player to Endgame Chamber
- **Coherence 8**: The system itself speaks

# Character Selection Screen Design

## Overview

The character selection screen is the first major choice in **Velinor: Remnants of the Tone**. It introduces the protagonist's **gender identity and name**, which affects:
- Visual presentation (appearance, clothing)
- Dialogue tone and NPC responses
- Mechanical stat baselines (subtle variations)
- Narrative weight and emotional resonance

---

## Screen Layout

### Visual Structure

```
═════════════════════════════════════════════════════════════
                    VELINOR: REMNANTS OF THE TONE
                        CHOOSE YOUR PATH
═════════════════════════════════════════════════════════════

                    [Character Artwork Area]
                    (Changes dynamically)

                   ┌─────────────────────────┐
                   │  LIOR (Male Variant)   │
                   │  [Portrait]            │
                   │  [Select Button]       │
                   └─────────────────────────┘

                   ┌─────────────────────────┐
                   │  LIOREN (Female)       │
                   │  [Portrait]            │
                   │  [Select Button]       │
                   └─────────────────────────┘

                   ┌─────────────────────────┐
                   │  LIOR(EN) (Nonbinary)  │
                   │  [Portrait]            │
                   │  [Select Button]       │
                   └─────────────────────────┘

═════════════════════════════════════════════════════════════
           [Back to Main Menu]     [Proceed]
═════════════════════════════════════════════════════════════
```

### Information Display (Per Character)

When a character card is hovered/focused:

```
╔════════════════════════════════════════╗
║  LIOR (Male Variant)                  ║
║                                        ║
║  [Portrait - Medium height, lean,     ║
║   dark hair, practical clothing]      ║
║                                        ║
║  Origin: The Scattered Edges (rural)  ║
║  Age: 27-28                           ║
║  Status: Newly arrived, grieving      ║
║                                        ║
║  Base Stats:                           ║
║  • Coherence: 40 (disoriented)        ║
║  • Empathy: 55 (present, open)        ║
║  • Observation: 50 (attentive)        ║
║  • Presence: 45 (uncertain)           ║
║  • Memory: 35 (fragmented)            ║
║                                        ║
║  Dialogue Signature:                   ║
║  Direct, reserved, occasionally       ║
║  vulnerable when pressed.             ║
║                                        ║
║                 [Select]               ║
╚════════════════════════════════════════╝
```

---

## The Three Variants

### Variant 1: LIOR (Male)

**Visual:**
- Lean frame, medium height
- Dark hair, short and practical
- Face: sharp features, observant eyes
- Clothing: simple, functional—archival tunic over travel-worn layers
- Movement: deliberate, economical

**Stat Baseline:**
- Coherence: 40
- Empathy: 55
- Observation: 50
- Presence: 45
- Memory: 35

**Dialogue Signature:**
- Direct, without flourish
- Occasional vulnerability when emotional weight is heavy
- Respectful to authority, quietly skeptical of systems
- Uses "I" statements rarely; prefers observation

**NPC Perception:**
- Malrik: "Competent. Unflinching. Good worker."
- Elenya: "Carries weight quietly. I see him."
- Velinor: "Unintegrated; raw; capable of learning."

**Thematic Role:**
- The outsider learning to observe systems without judgment
- Quiet strength as resistance to institutional pressure

---

### Variant 2: LIOREN (Female)

**Visual:**
- Lean frame, medium height
- Dark hair, longer, practical braid or knot
- Face: sharp features, observant eyes, slight asymmetry
- Clothing: flowing elements mixed with practical layers—ritual-influenced drape over archival wear
- Movement: fluid, present, grounded

**Stat Baseline:**
- Coherence: 41 (slightly higher emotional presence)
- Empathy: 56 (more visibly emotional)
- Observation: 49 (slightly more intuitive)
- Presence: 46 (more commanding)
- Memory: 35 (same fragmentation)

**Dialogue Signature:**
- Thoughtful, with pauses for reflection
- Emotional but not unstable; vulnerability as strength
- Questions authority with curiosity rather than skepticism
- Uses "I feel" statements alongside "I think"

**NPC Perception:**
- Malrik: "Capable. Respectful but distant. Sometimes I wonder what she's thinking."
- Elenya: "I recognize her. She is unafraid to feel."
- Velinor: "Unintegrated; sensitive; capable of deep work."

**Thematic Role:**
- The outsider learning to honor her intuition alongside systems
- Emotional depth as a valid way of knowing

---

### Variant 3: LIOR(EN) (Nonbinary)

**Visual:**
- Lean frame, medium height
- Dark hair, neither distinctly long nor short—shoulder-length, unstyled
- Face: neutral features, expressive eyes
- Clothing: deliberately androgynous—tunic with no gender-coding, layered in neutral tones
- Movement: present and attentive, neither gendered nor rigid

**First Screen:**
- Shows the three variants equally
- Player selects "LIOR(EN)"
- Proceeds to secondary screen

**Secondary Screen (Name Choice):**

```
═════════════════════════════════════════════════════════════
      You have chosen the nonbinary path.
      
      The glyph system will know you by whichever name
      carries the truth of your heart.
      
      Choose your name:
      
              ☐ Lior (primary presence)
              ☐ Lioren (core identity)
              ☐ Lior(en) (both, integrated)
═════════════════════════════════════════════════════════════
```

**If "Lior" selected:**
- Character uses male-coded name
- Dialogue adjusts to Lior baseline
- Visual: androgynous presentation with masculine lean (shorter hair, minimal adornment)
- Stats: baseline Lior stats
- NPC dialogue: uses "Lior" consistently; some NPCs will notice the name/presentation mismatch

**If "Lioren" selected:**
- Character uses female-coded name
- Dialogue adjusts to Lioren baseline
- Visual: androgynous presentation with feminine lean (longer hair, subtle adornment)
- Stats: baseline Lioren stats
- NPC dialogue: uses "Lioren" consistently; some NPCs will notice the name/presentation mismatch

**If "Lior(en)" selected:**
- Character uses integrated name
- Dialogue adjusts fluidly, code-switching between both baselines depending on context
- Visual: purely androgynous (shoulder-length hair, no gendered adornment)
- Stats: baseline average between Lior and Lioren (Coherence: 40.5, Empathy: 55.5, Observation: 49.5, Presence: 45.5, Memory: 35)
- NPC dialogue: some NPCs use "Lior(en)" if familiar; others may use just "Lior" or "Lioren"; creates dialogue variation

**Stat Baseline (if "Lior(en)" selected):**
- Coherence: 40.5 (slightly more grounded than Lior)
- Empathy: 55.5 (balanced emotional/analytical)
- Observation: 49.5 (intuitive and systematic)
- Presence: 45.5 (uncertain of social space)
- Memory: 35 (equal fragmentation)

**Dialogue Signature:**
- Flexible, shifting between direct and reflective
- Comfortable with uncertainty; voices internal debate
- Questions authority with both logic and intuition
- Uses "I think/feel/know" interchangeably

**NPC Perception:**
- Malrik: "Competent but unpredictable. Sometimes I understand them; sometimes I don't."
- Elenya: "They are not fixed. They are becoming. I honor that journey."
- Velinor: "Unintegrated; complex; capable of holding paradox."

**Thematic Role:**
- The outsider who refuses categorization
- Nonbinary identity as a form of glyph resonance (existing between states)
- Capacity to move between systems without being bound by either

---

## Selection Flow

### Step 1: Main Menu → Character Selection
- **Trigger**: "New Game" button on main menu
- **Context**: Brief introduction explaining that character choice matters
- **Accessibility**: All three variants presented equally; no hierarchy

### Step 2: Character Preview
- **Display**: All three variant cards visible simultaneously
- **Interaction**: Hover to see details; click to select
- **Audio**: Subtle sound cue when a card is highlighted

### Step 3a: Variant Selection (Gendered/Nonbinary)
- **Trigger**: Click on desired variant
- **If Lior or Lioren**: Proceed directly to Step 4 (confirmation)
- **If Lior(en)**: Proceed to Step 3b (name choice)

### Step 3b: Name Choice (Nonbinary Only)
- **Display**: Three name options with brief descriptions
- **Context**: Flavor text explaining that the glyph system responds to the name you choose
- **Interaction**: Select one; proceed to Step 4

### Step 4: Confirmation
```
═════════════════════════════════════════════════════════════
      You have chosen: [Character Name]
      
      Is this your truth?
      
              [Yes, Begin]     [No, Go Back]
═════════════════════════════════════════════════════════════
```

### Step 5: Game Begins
- Character appears in the opening scene (Marketplace arrival)
- Dialogue, stats, and visual presentation reflect chosen variant
- Game engine loads the appropriate dialogue pronoun system

---

## Technical Specifications

### Data Structure (Game Backend)

```python
CHARACTER_CHOICE = {
    "variant": "lior" | "lioren" | "lior(en)",
    "name": "Lior" | "Lioren" | "Lior(en)",  # Only used if variant="lior(en)"
    "pronouns": "he/him" | "she/her" | "they/them",
    "base_stats": {
        "coherence": int,
        "empathy": int,
        "observation": int,
        "presence": int,
        "memory": int,
    },
    "dialogue_signature": str,  # Informs NPC response tone
}
```

### Pronoun Storage (Game State)

```python
PLAYER_PROFILE = {
    "chosen_variant": str,  # "lior" | "lioren" | "lior(en)"
    "chosen_name": str,     # "Lior" | "Lioren" | "Lior(en)"
    "pronouns": str,        # "he/him" | "she/her" | "they/them"
    "visual_code": str,     # For art direction (masculine/feminine/neutral)
}
```

### Dialogue System Integration

See `dialogue_pronoun_system.md` for full implementation details.

---

## UX Best Practices

### 1. Equity in Presentation
- All three variants occupy equal screen space
- No variant is presented first or given visual priority
- Flavor text for each variant is equally detailed

### 2. Clear Mechanical Impact
- Show stat baseline differences
- Explain what each choice affects (dialogue, NPC perception, mechanics)
- Make the choice feel meaningful, not cosmetic

### 3. No Gender Gatekeeping
- All variants have access to the same story
- No variant is locked to certain content
- Gender choice affects flavor, not core narrative

### 4. Nonbinary Specificity
- The "Lior(en)" option is not a default; it's a specific, intentional choice
- Secondary name selection adds meaning (player agency in self-definition)
- Stats reflect both variants, not a "compromise"

### 5. Accessibility
- Clear text descriptions of each variant
- Visual preview for those who want it
- Option to skip directly to variant selection if desired

---

## Narrative Integration

### Character Selection as Story Beat

The act of choosing becomes part of the story:

**In-game flavor text (displayed at selection):**

> "The glyphs respond to those who carry truth. But truth takes many forms—and the glyph system learns you through the name you carry, the presence you embody, the voice you speak with.
> 
> Who are you?"

**For Lior:**
> "Direct. Reserved. Your truth is clarity."

**For Lioren:**
> "Reflective. Emotional. Your truth is presence."

**For Lior(en) (before name choice):**
> "Neither fixed. Both held. Your truth is becoming."

---

## Downstream Effects

### 1. NPC Dialogue Variation
- Malrik uses chosen name consistently
- Elenya may refer to the player with androgynous language initially
- Velinor adjusts formality based on pronouns

### 2. Glyph Resonance
- Certain glyphs respond differently based on chosen gender
- Example: "Severed Covenant" glyph (tied to Malrik & Elenya's love) may have variant dialogue for each gender

### 3. Romance Options
- Nonbinary path has access to relationships but with different tone
- No gender locks on romance; relationships adjust to player pronouns

### 4. Attunement System
- NPC attunement may develop differently based on gender perception
- Example: Elenya may sense the nonbinary player differently (as "becoming")

---

## Visual Notes for Art Direction

### Lior (Male Variant)
- Reference: Person with sharp features, androgynous-leaning-masculine
- Color palette: Cool grays, earth tones, archival neutrals
- Clothing: Functional, minimal ornamentation
- Hair: Short, practical, dark

### Lioren (Female Variant)
- Reference: Person with sharp features, androgynous-leaning-feminine
- Color palette: Warm grays, earth tones, ritual touches
- Clothing: Fluid over practical, subtle adornment
- Hair: Longer, loose or braided, dark

### Lior(en) (Nonbinary Variant)
- Reference: Person with neutral features, truly androgynous
- Color palette: Balanced, no warm/cool dominance
- Clothing: No gendered coding; tunic-based, layered
- Hair: Shoulder-length, unstyled, dark

---

This character selection screen establishes that **Velinor honors multiple truths about identity** while maintaining mechanical depth and narrative meaningfulness.

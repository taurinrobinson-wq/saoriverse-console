# Swamp Maze: NPC Dialogue Samples

This file contains character voice examples for the three passages of the Swamp Maze side-quest. Use these as templates when generating dynamic dialogue based on player resonance stats.

---

## Passage 1: The False Path

### Kaelen (High Trust, Present)

**If player is confused by the pedestal:**
> "This place… it's not what he said it was. Feels like the swamp's playin' tricks. That mark there — it's old. Older than memory. My people used to think marks like that meant somethin'. Maybe they did. Maybe they still do."

**If player examines the moss pattern:**
> "You're seein' it, aren't you? The way the moss falls. Like it remembers a shape. The swamp doesn't forget, even when we do."

**If player hesitates:**
> "Don't linger here too long. This place eats at you. The stillness gets under your skin. Move when you feel ready."

### Nima (High Skepticism, if encountered)

> "Symbols carved in stone. Moss that patterns itself. Either there's a logic to it, or the world likes to mock us with resemblance. I've seen both."

### Ravi (High Observation, marketplace hint if player asks beforehand)

> "The hollow groves past the water... there's a story there. My grandfather spoke of places where the world felt *deliberate*. Where nothing happened by accident. He'd stand still in those places for hours."

---

## Voice Notes: Kaelen vs. The Trickster

Important: Kaelen and the Trickster are never present in the same scene at the same time. They are two distinct personae the player will encounter; their language must consistently differ to cue the player to this structural truth without an explicit reveal.

- **Kaelen (choppy, shifty)**: Short, halting phrases; always half-distracted, thinking about exits and contingencies. Uses contractions, stopped sentences, repeated small words. He rarely finishes thoughts fully and often trails off or repeats a word as if searching for the next step.

    Example Kaelen lines (choppy):
    > "You—look, listen. Quick now. We move before it remembers you."

    > "I don't... I don't keep things long. Names, times—slip. Best to mark it while it's warm."

- **The Trickster (smooth, deliberate)**: Long, measured sentences; coy, theatrical, never hurried. He speaks as if describing a small, elegant game. His voice puts space between ideas and bends meaning gently.

    Example Trickster lines (smooth):
    > "Ah, wanderer—how tidy your footsteps are. Do you prefer a story or an arrangement? I have both."

    > "You may follow my directions. Or you may not. Either choice is delightful; I will enjoy the consequence." 

Implementation notes:
- When the maze engine spawns a guidance NPC, pick `persona='trickster'` for smooth lines, `persona='kaelen'` for choppy lines. Never spawn both together.
- Use `playerHasStillness` (boolean) to enable a small, clarifying Kaelen line that gently steadies the player when they possess the Stillness token. This should not fully explain the phenomenon—only anchor it.


## Passage 2: The Fog Logic Puzzle

### Kaelen (High Trust, guiding)

**After the fog clears slightly, revealing the five stones:**
> "Five markers. Drossel showed me this once. Said each stone held a truth, but the truth only lived in the person who could feel it. Not know it. Feel it."

**When the player struggles:**
> "Listen. Forget what you think. Your body knows the answer before your mind does. Which one calls you back? Which one feels like... like comin' home?"

**If player finds the still stone correctly:**
> "That's it. That's the one. You felt it right. Drossel always said the quiet ones are the dangerous ones. Not because they're loud, but because they know how to wait."

### The Fog Itself (narrative voice)

> "The swamp whispers. Not words. Not quite sounds. Impressions that land in your chest. Fear. Longing. Rest. Anger. And underneath them all—a quietness that feels like understanding."

### Environmental Hints (High Observation reading)

**Noticing the ground settlement:**
> "The stones sink deeper into the earth in order. The first one, disturbed and restless. The last one—smooth, settled, as if it's always been patient."

**Noticing the moss distribution:**
> "There's no moss on the fifth stone. It's too still, too balanced. The swamp doesn't grow on stillness."

---

## Passage 3: The Hidden Threshold

### Kaelen (High Trust, moment of revelation)

> "You weren't meant to find this easy. Drossel always hid where the world felt… still. Where waiting felt natural. This place… he chose it for a reason. Maybe because he needed to remember what quiet felt like. Maybe because he was afraid of loud things."

**After the threshold opens:**
> "The tokens. Five of them. He always carried all five. I asked him once why. He said: 'Because alone, each one is a fragment. Together, they're a voice. And sometimes a voice is all you have in the dark.'"

### Environmental Resonance (High Empathy sensing)

> "The air here is heavy. Not with weight—with presence. You feel it in your chest, like someone's been standing here for a long time, waiting. Like they left their ache behind when they left."

**When touching the tokens:**
> "They're warm. Like they've been held recently. Like the person who carried them is still holding on somehow."

### Shrine Keeper (if encountered later, after collecting a token)

> "You have one of those marks. I haven't seen one in... years. My mother used to say they were tied to people. That carrying one meant you'd touched something sacred in them. Not a good thing, necessarily. Just—sacred."

---

## Optional: NPC Reactions to Specific Player Choices

### If player struggles at the puzzle (Low Empathy, Low Observation)

**Kaelen becomes more explicit:**
> "The quiet stone. Not the angry one. Not the sad one. The one that feels like... like when you stop fightin' and let yourself just *be*."

**Nima (if nearby, High Skepticism):**
> "Emotional logic. It's still logic. Find the pattern in how you feel, and you'll find your answer."

### If player passes with High Observation but Low Empathy

**Environmental response:**
> "You read the signs correctly. Your mind mapped the pattern. But you still don't quite *feel* it. That's okay. Understanding takes many forms."

### If player passes with High Empathy but Low Observation

**Kaelen's acknowledgment:**
> "You felt your way through. That's the older way. Before people needed to understand—they just *knew*. You still know how."

---

## Passage 3 Extended: Token Reactions

### When player collects the first token

**Kaelen:**
> "Hold it. Let it rest in your palm. Feel the weight. That's Drossel, right there. His waiting. His silence. His choice to hide instead of run."

### When player collects multiple tokens

**Kaelen (with growing revelation):**
> "Four left. Each one different. Each one part of the same voice. You're holdin' his secrets now. Don't carry them lightly."

**Late game echo (if player brings tokens to Drossel encounter):**
> "You found them. All of them. Then you know what I know. That even the quietest people leave echoes. Even the ones who hide. Especially the ones who hide."

---

## Dialogue State Tracking

For implementation, track these conditions:

- **Kaelen's Trust Level**: Affects how much he reveals and how personal his guidance becomes
- **Passage Completion**: Each passage unlocks new dialogue lines in subsequent encounters
- **Token Collection**: Each token triggers optional dialogue callbacks
- **Observation vs. Empathy**: Determines whether Kaelen offers logical hints or emotional guidance

---

## Usage Notes for Designers

1. **Layer the dialogue**: Don't use all of Kaelen's lines at once. Reserve deeper reveals for later encounters.
2. **Respect player agency**: If player solves the puzzle without help, acknowledge it differently than if they need guidance.
3. **Echo the choice**: Reference the player's emotional journey in later conversations with other NPCs.
4. **Build to confrontation**: These tokens should feel like fragments of Drossel's character, preparing the player emotionally for meeting him.

---

## Integration with Main Dialogue System

These samples should be used with the existing NPC dialogue engine:

- **apply_temperament()**: Kaelen's voice shifts based on trust and observation remnants
- **glyph_triggers()**: Collecting tokens could trigger emotional OS shifts
- **npc_resonance**: Each encounter adjusts Kaelen's and Drossel's future dialogue differently

Example integration:
```python
if kaelen.remnants['trust'] > 0.6 and player.has_token('first'):
    dialogue = "You're holdin' his secrets now. Don't carry them lightly."
else:
    dialogue = "That mark there — it's old. Older than memory."
```

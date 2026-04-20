# Key Design Insights: Skill-Lying-REMNANTS System

## The Core Design Principle: "Visible Self, Invisible World"

This system elegantly separates what the player experiences from what NPCs experience:

### Player's Perspective
✅ **See:** Own TONE stats (Trust, Observation, Narrative Presence, Empathy) ❌ **Don't See:** NPC
REMNANTS, game systems, mechanical rules 📍 **Learn:** NPC state ONLY through dialogue shifts and
social consequences

### NPC's Perspective (Hidden)
✅ **Have:** REMNANTS traits that evolve based on player actions ✅ **Know:** When player is lying
(through discovery mechanics) ✅ **Remember:** Past deceptions (Memory trait + Korrin's
rumor-spreading) ❌ **Cannot:** Block access or create narrative lockouts

---

## Why This Design Works

### 1. Immersion Through Ignorance
By hiding REMNANTS, the player experiences consequence-through-inference rather than
consequence-through-mechanics. This feels more like real social interaction:

- **Traditional RPG:** "Kaelen's trust is now 0.2 (too low for quests)"
- **This System:** "Kaelen says, 'I thought better of you. Let's just get this done.' [Something is wrong]"

The player *learns* the state from dialogue, creating emergent storytelling.

### 2. Lying is a Valid Playstyle
Unlike games with binary trust meters that lock content:

- Player can always attempt tasks
- Success determined by actual_skill + luck, not NPC disposition
- Lying doesn't create narrative forks (same task, different texture)
- Consequences are social pressure, not mechanical barriers

### 3. Ripple Effects Create Organic Community Dynamics

When player lies to Kaelen:
- Kaelen becomes skeptical ✅ (expected)
- Torvren hears about it → also skeptical ✅ (social learning)
- Korrin weaponizes the lie → becomes rumor-spreader ✅ (personality-driven)
- Drossel's caution increases ✅ (through Korrin's network)

Result: A living social ecosystem where consequences ripple naturally.

### 4. Korrin's Special Role: The Chaos Agent

Korrin's enhanced rumor-spreading creates narrative tension:

```
Player lies once          → Kaelen skeptical
Player lies twice         → Korrin starts spreading rumors
                          → Community grows suspicious
                          → Same task, different dialogue tone
```

This incentivizes *some* honesty, but doesn't enforce it. The player can continue lying and facing
escalating social friction—the choice remains theirs.

---

## Technical Elegance: Decoupled Systems

The implementation elegantly separates concerns:

```
┌─────────────────────────────────────────────────────┐
│ Game State (High Level)                             │
│ - Player TONE stats visible                         │
│ - NPC dialogue context generated                    │
│ - Dialogue options filtered/shown dynamically       │
└─────────────────────────────────────────────────────┘
                        ↕ (apply_skill_task_outcome)
┌─────────────────────────────────────────────────────┐
│ NPC Manager (REMNANTS Layer)                        │
│ - apply_skill_task_outcome() bridges systems        │
│ - _propagate_lie_discovery() spreads skepticism     │
│ - Influence map defines community structure         │
└─────────────────────────────────────────────────────┘
                        ↕ (SkillTaskOutcome.get_remnants_effects())
┌─────────────────────────────────────────────────────┐
│ Skill System (Outcome Layer)                        │
│ - SkillClaim determines lie likelihood              │
│ - SkillTaskOutcome calculates consequences          │
│ - get_remnants_effects() translates to trait deltas │
└─────────────────────────────────────────────────────┘
                        ↕ (NPCDialogueContext)
┌─────────────────────────────────────────────────────┐
│ Dialogue System (Presentation Layer)                │
│ - Reads NPC REMNANTS state                          │
│ - Generates DialogueStyle (TRUSTING/SUSPICIOUS)     │
│ - Filters options based on trust/skepticism         │
└─────────────────────────────────────────────────────┘
```

Each layer has a single responsibility:
- **Skill System**: Calculate outcome
- **NPC Manager**: Update state based on outcome
- **Dialogue System**: Render state as dialogue

No layer knows about the others' internals—only the APIs.

---

## The Lying Mechanics: Discovery Confidence

When a player lies about having a skill, the lie isn't binary—it's graduated:

```
Player's Actual Skill Level    → Discovery Confidence
─────────────────────────────────────────────────────
0.0 (novice)                   → 0.95 (VERY obvious lie)
0.3 (novice+)                  → 0.88 (obvious)
0.6 (apprentice)               → 0.69 (suspicious)
0.8 (journeyman)               → 0.61 (plausible)
0.95 (master)                  → 0.52 (barely detectable)

Formula: discovery_confidence = 0.95 - (player_level × 0.43)
```

This means:
- **Master trying to exaggerate skills**: Lie is hardest to catch
- **Novice claiming expertise**: Obviously lying
- **Intermediate player**: Credible to some NPCs, suspicious to others

This creates natural difficulty scaling without explicit difficulty numbers.

---

## Dialogue Filtering: The Smart Option System

Not all dialogue options show up. They're filtered based on NPC state:

```python
Option("I know this skill well", skill="Tracking", is_lie=True)
    Hidden if NPC Skepticism >= 0.8  # Too suspicious to bluff

Option("Let me try something risky", skill="Stealth", is_lie=True)
    Hidden if NPC Skepticism >= 0.6  # Even moderate skepticism sees through it

Option("I learned from my mistakes", is_redemption=True)
    Only shown if: previous_lie_caught=True AND Trust >= 0.3
                   (Can't redeem with someone who completely distrusts you)
```

Result: NPC dialogue feels intelligent—they don't offer obviously unbelievable options.

---

## Redemption Paths: Trust Can Be Rebuilt

Unlike many games, broken trust isn't permanent:

```
Initial state: Sera trusts you (Trust 0.7)
                    ↓
Player lies, caught
                    ↓
Broken: Sera is disappointed (Trust 0.2)
                    ↓
Player learns actual skill
                    ↓
Player encounters Sera again
Redemption option appears: "Last time I wasn't ready..."
                    ↓
Player succeeds honestly
                    ↓
Partial recovery: Sera still cautious (Trust 0.3) but less hostile
```

Key insight: **Trust rebuilds slowly**. One honest success doesn't erase the lie, but it begins the
process.

This creates natural story beats:
- Act 1: Establish trust through honesty
- Act 2 (Optional): Betray trust for short-term gain
- Act 3: Long redemption arc rebuilding relationships

---

## Social Network: Why Korrin Matters

The influence map defines how information spreads:

```
Kaelen (lies to me about Tracking)
    ↓
    ├→ Torvren (my friend, tells him I'm deceptive)
    ├→ Korrin (she LOVES gossip, tells everyone)
    └→ Drossel (connected through Kaelen)

Result: Lie to one NPC → community learns about it → 
        everyone becomes more skeptical → 
        player's reputation precedes them
```

Korrin is special because she's the **hub** of the social network. When she discovers a lie:
- Her skepticism jumps 0.15 (vs normal 0.10)
- Her memory jumps 0.10 (she literally remembers this)
- She spreads the news to her entire network

This creates narrative pressure without mechanical enforcement:
- "I can keep lying, but Korrin will make sure everyone knows"
- "Maybe I should be more careful around Korrin-adjacent NPCs"
- "If I need community trust, I should focus on Korrin first"

---

## Why No Mechanical Lockouts?

Traditional RPGs with reputation systems often do:
```
IF player_trust_with_NPC < 0.5:
    THEN NPC refuses to give quest
    THEN narrative forks into different branch
```

This system deliberately avoids this because:

1. **Agency Preservation**: Player can always attempt tasks 2. **Narrative Coherence**: Same story
with different emotional texture is more elegant than parallel timelines 3. **Social Realism**: In
real life, you don't become "blocked" from social interactions; they become *uncomfortable* 4.
**Replay Value**: Same task played differently based on trust state is more interesting than blocked
content

---

## The Elegant Solution: Elastic Encounters

```
Game Designer's Intent: "Sera teaches Herbalism"

Traditional Approach:
  - If trust too low: NPC refuses to teach → narrative fork
  - Creates branching story → content multiplication

This System's Approach:
  - Sera always teaches Herbalism (she's kind-hearted, never refuses)
  - Lesson scope/complexity reflects REMNANTS state:
    * High trust: "I'm delighted to teach you."
      → Complex lesson on ingestible anti-viral
    * Low trust: "I'm a little busy so I'll have to give you a quick lesson."
      → Simple lesson on making a basic salve
  - Same character, different scope
  - Different scope creates authentic game consequence without personality shift
```

Result: More content with same effort. Player feels respected (agency) and the story feels organic
(emergence).

---

## Integration with Glyphs

The skill system integrates beautifully with the existing glyph architecture:

```
NPC Arc (Building Debate):
  - Malrik vs Elenya argue about the archive
  - Player can claim skills to help (mediation, observation, etc.)
  
Glyph Obtained:
  - Glyph 22: Coren's "Held Ache" at archive
  - Triggers when player demonstrates empathy/nuance
  
REMNANTS Shift:
  - Player's Empathy claim (honest) → Coren's Empathy ↑
  - Or: Player's Trust claim (lie) → Coren's Skepticism ↑
  
Dialogue Ripple:
  - Malrik hears Coren is skeptical → assumes player is untrustworthy
  - Elenya becomes more cautious → less open in future discussions
```

Glyphs and skills work orthogonally:
- **Glyphs**: Emotional arcs, character discovery
- **Skills**: Practical competencies, agency in tasks

Learning a glyph doesn't teach you a skill; learning a skill doesn't reveal a glyph. But together
they create a cohesive character arc where the player's choices ripple through the world.

---

## Conclusion: A System That Respects Player Intelligence

This design respects the player by:

1. **Trusting intuition**: Hidden stats mean players read social cues like real life 2. **Respecting
agency**: Lying is possible; consequences are social, not mechanical 3. **Rewarding roleplay**: Same
mechanics serve both honest and deceptive playstyles 4. **Creating emergence**: Organic ripple
effects and community dynamics feel alive

The result is a system where the player doesn't solve a puzzle (get trust to X, get skill to Y) but
rather navigates a social ecosystem where their choices matter and consequences ripple naturally.

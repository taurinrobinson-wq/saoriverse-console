# FirstPerson + Velinor: Quick Reference

## 🎯 Integration at a Glance

Your Velinor game now uses FirstPerson to make NPC dialogue **emotionally responsive**. Here's what happens:

```
You type: "I'm overwhelmed by all of this"
           ↓
FirstPerson analyzes:
  - Tone: "heavy" (negative emotion)
  - Theme: "general" (burden/overwhelm)
  - Valence: -0.7 (quite negative)
  - Intensity: 0.8 (strong emotion)
           ↓
NPC adapts response:
  - Opening acknowledges weight: "I hear the weight in that"
  - Connects to theme: "The burden can feel immense"
  - Invites exploration: "What needs to be said about it?"
```



## 🧠 Emotional Analysis Components

### 1. **Tone** (How they're saying it)
| Tone | Indicators | NPC Opening |
|------|-----------|------------|
| **uplifting** | happy, joy, wonderful, amazing | "I feel that brightness too" |
| **heavy** | sad, angry, frustrated, hurt | "I hear the weight in that" |
| **reflective** | confused, uncertain, curious | "There's something to sit with there" |
| **curious** | questions, wondering, exploring | "Tell me more about that" |

### 2. **Valence** (-1 to +1)
- **< -0.5**: Strongly negative → NPC emphasizes listening
- **-0.5 to 0.5**: Neutral → NPC mirrors curiosity
- **> 0.5**: Strongly positive → NPC shares brightness

### 3. **Intensity** (0 to 1)
- **< 0.3**: Calm, quiet → NPC asks gentle questions
- **0.3-0.7**: Moderate → NPC engages directly
- **> 0.7**: Intense → NPC acknowledges weight/urgency

### 4. **Theme**
- **grief**: Loss, death, endings
- **joy**: Happiness, celebration, connection
- **general**: Everything else

## 📊 Memory & Patterns

FirstPerson tracks across turns:

### Conversation Memory

```
Turn 1: "I feel disconnected"     → Theme: general, Valence: -0.6
Turn 2: "It's like I've lost them" → Theme: grief, Valence: -0.8
Turn 3: "But maybe there's hope"  → Theme: grief, Valence: -0.1

→ Detects: 'grief' is recurring
→ Emotional trend: Improving (from -0.8 to -0.1)
```



### NPC Responds to Pattern

```
Turn 3 NPC: "I'm noticing a shift in what you're saying.
What's helping you see this differently?"
```



## 💬 Response Generation

### Three-Part Structure

1. **Opening** (mirrors tone)
   - Heavy: "I hear the weight in that"
   - Uplifting: "I feel that brightness too"
   - Reflective: "There's something to sit with there"

2. **Middle** (acknowledges theme + memory)
   - Theme-specific: "Loss shapes us in ways words can't reach"
   - Memory-aware: "And I'm noticing grief keeps coming back to you"

3. **Closing** (invites deeper exploration)
   - High intensity: "What needs to be said about it?"
   - Low intensity: "What's sitting underneath that?"
   - Medium: "What would help you carry this?"

## 🛠 Code Integration Points

### In `velinor_app.py`

```python

# FirstPerson initialized on startup
st.session_state.firstperson_orchestrator = FirstPersonOrchestrator(...)

# Passed to game engine
orchestrator = VelinorTwineOrchestrator(
    first_person_module=firstperson_orchestrator,
    ...
)
```



### In `velinor/engine/orchestrator.py`

```python

# Step 1: Analyze player input
player_analysis = self._summarize_player_intent(player_input, player_id)

# Returns: {emotional_tone, detected_theme, valence, intensity, memory_context}

# Step 2: Apply to NPC dialogue
npc_dialogue = self._generate_npc_dialogue(
    npc_name='Keeper',
    context=updated_state  # Contains player_analysis
)
```



## 🎮 Real Example

**Game Scenario:** Meeting an NPC named Keeper

### Scenario 1: Heavy Emotional Weight

```
You: "Everything feels too heavy. I don't know if I can go on."

FirstPerson Analysis:
{
  tone: 'heavy',
  theme: 'general',
  valence: -0.8,
  intensity: 0.9
}

Keeper's Response:
"I hear the weight in that. The gravity of what you're carrying—
I feel it too. What needs to be said about it? Sometimes naming it
helps."
```



### Scenario 2: Recurring Theme (After 3rd mention of loss)

```
You: "I keep coming back to what I've lost..."

FirstPerson Analysis:
{
  tone: 'heavy',
  theme: 'grief',
  valence: -0.7,
  intensity: 0.6,
  memory_context: {
    recurring_themes: ['grief'],
    emotional_trend: 'stable',
    num_turns: 5
  }
}

Keeper's Response:
"I hear the weight in that. And I'm noticing grief keeps coming
back to you—it's sitting heavy. That tells me something. What do
you need in this moment?"
```



### Scenario 3: Emotional Improvement

```
You: "Maybe there's something I can learn from this pain..."

FirstPerson Analysis:
{
  tone: 'reflective',
  theme: 'grief',
  valence: -0.2,  ← Improved!
  intensity: 0.4,
  memory_context: {
    emotional_trend: 'improving'  ← Detected!
  }
}

Keeper's Response:
"There's something to sit with there. I'm also noticing a shift
in what you're saying. What's helping you see this differently?"
```



## 🚀 How to Use It

### Local Play

```bash

# Just run it—integration works automatically!
streamlit run velinor_app.py
```



No configuration needed. FirstPerson analysis happens client-side.

### Observing the Analysis
The terminal shows debug info (if logging enabled):

```
[Player Input] "I'm struggling with loss"
[FirstPerson] tone='heavy', theme='grief', valence=-0.7, intensity=0.8
[NPC] Keeper generates response...
```



### Customizing Responses
Edit `_generate_emotionally_aware_response()` in `orchestrator.py`:

```python

# Modify opening responses
response_openings = {
    'uplifting': ["Your custom uplifting response"],
    'heavy': ["Your custom heavy response"],
    ...
}

# Modify theme acknowledgments
theme_acknowledgments = {
    'grief': "Your custom grief acknowledgment",
    ...
}
```



## 📈 What Improves Player Experience

✨ **Personalized Responses**: NPCs don't repeat generic dialogue

✨ **Contextual Awareness**: References previous turns and themes

✨ **Emotional Attunement**: Tone matches player's emotional state

✨ **Pattern Recognition**: Notices when players struggle with same issue

✨ **Growth Tracking**: Acknowledges when emotional state improves

✨ **Immersive**: Feels like NPCs genuinely understand and care

## 🔄 Memory Tracking Examples

### Turn Tracking

```python
self.memory.record_turn(
    user_input="I feel lost",
    affect={valence: -0.7, intensity: 0.8, tone: 'heavy'},
    theme='general',
    glyph_name=None
)
```



### Recurring Theme Detection

```python
Turn 1: "I miss them" → theme='general'
Turn 2: "The loss keeps returning" → theme='grief'
Turn 3: "Grief is still with me" → theme='grief' (2nd occurrence)

# FirstPerson detects 'grief' is recurring:
memory.repeated_patterns = ['grief']

# Next NPC response includes:
"I'm noticing grief keeps coming back to you."
```



### Emotional Trajectory

```python
Valence history: [-0.8, -0.7, -0.6, -0.4, -0.2]
→ Trend: 'improving'

NPC: "I'm also noticing a shift. What's helping?"
```



## 🎯 Key Features

| Feature | What It Does |
|---------|-------------|
| **Affect Analysis** | Extracts emotional tone from text in real-time |
| **Theme Detection** | Identifies what player is talking about |
| **Memory Tracking** | Remembers all turns with emotional context |
| **Pattern Detection** | Notices when themes recur (not just one-offs) |
| **Trajectory Sensing** | Tracks if emotions improve, worsen, or stay stable |
| **Adaptive Responses** | NPC tone changes based on all of the above |
| **Multiplayer Aware** | Notes when others are listening |

## 🔐 Privacy

✅ All analysis happens locally on your machine
✅ No data sent to external servers (unless you configure it)
✅ No configuration required for local play
✅ Conversation history stored only in session memory

## 📚 Files

| File | Purpose |
|------|---------|
| `velinor_app.py` | Main game UI, initializes FirstPerson |
| `velinor/engine/orchestrator.py` | Connects emotional analysis to NPC dialogue |
| `src/emotional_os/deploy/core/firstperson.py` | FirstPerson module (emotional analysis) |
| `FIRSTPERSON_INTEGRATION_TEST.py` | Test script to validate integration |
| `FIRSTPERSON_VELINOR_INTEGRATION_GUIDE.md` | Detailed technical guide |

## ❓ FAQ

**Q: Does the game work without FirstPerson?**
A: Yes! It gracefully falls back to basic responses if FirstPerson unavailable.

**Q: Can I customize how emotions are detected?**
A: Yes, edit `AffectParser.analyze_affect()` in `firstperson.py`

**Q: Do I need secrets or API keys?**
A: No, not for local play. Only if deploying with external backends.

**Q: How much emotional history is kept?**
A: Entire conversation is tracked in session memory. Clears on new game.

**Q: Can I export emotional analysis data?**
A: Not yet, but the infrastructure is there. See `memory.get_memory_context()`
##

**Status:** ✅ **Ready to Play**

Your Velinor game now delivers emotionally responsive, contextually aware dialogue that adapts to your emotional state in real-time!

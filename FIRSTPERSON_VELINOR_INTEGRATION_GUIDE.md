# FirstPerson + Velinor Integration Guide

## 🎯 Overview

Your Velinor game now integrates with the FirstPerson emotional analysis system to deliver **nuanced, emotionally-aware NPC responses**. Instead of generic dialogue, NPCs adapt their tone, empathy, and responses based on real-time analysis of the player's emotional state.

## 🔗 Integration Architecture

```
Player Input (typed or choice)
        ↓
┌─────────────────────────────────────────────┐
│   FirstPerson Orchestrator                  │
│  - Analyzes emotional tone                  │
│  - Extracts detected themes (grief, joy)    │
│  - Tracks conversation memory               │
│  - Detects recurring patterns                │
└─────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────┐
│   Velinor Game Engine                       │
│  - Maps emotional analysis to story context │
│  - Applies game mechanics (dice, stats)     │
│  - Routes to appropriate NPC encounter      │
└─────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────┐
│   NPC Response Generation                   │
│  - Adapts opening based on emotional tone   │
│  - Acknowledges recurring themes            │
│  - Reflects emotional trajectory            │
│  - Adjusts intensity of response            │
└─────────────────────────────────────────────┘
        ↓
    Chat Display
```

## 📊 What Gets Analyzed

When a player types a message, FirstPerson extracts:

### 1. **Emotional Tone**
- `uplifting`: Positive, hopeful language
- `heavy`: Dark, serious, melancholic language
- `reflective`: Contemplative, uncertain language
- `curious`: Exploratory, questioning language

### 2. **Emotional Metrics**
- **Valence**: -1 (very negative) to +1 (very positive)
- **Intensity**: 0 (calm) to 1 (highly emotional)
- **Arousal**: How activated/engaged the emotion is

### 3. **Detected Themes**
- `grief`: Loss, death, endings
- `joy`: Happiness, celebration, hope
- `general`: Other topics

### 4. **Conversation Memory**
- Tracks all turns with their emotional context
- Detects recurring themes across turns
- Measures emotional trajectory (improving/worsening/stable)
- Identifies entities and relationships mentioned

## 🎮 How NPC Responses Adapt

### Based on Emotional Tone

**If player is "uplifting":**
```
NPC: I feel that brightness too.
That's a light worth holding.
Tell me more about what that feels like.
```

**If player is "heavy":**
```
NPC: I hear the weight in that.
The gravity of it—I feel it too.
What needs to be said about it?
```

**If player is "reflective":**
```
NPC: There's something to sit with there.
That deserves thought.
What's sitting underneath that?
```

### Based on Theme Recurrence

If the player keeps mentioning grief:
```
NPC: The weight in that stays with you, doesn't it?
I keep hearing grief come back for you.
I'm noticing the weight of it.
What do you need?
```

### Based on Emotional Trajectory

If emotions are **worsening** (getting more negative):
```
NPC: I'm noticing the weight increasing.
What's happening?
```

If emotions are **improving** (getting more positive):
```
NPC: I'm also noticing a shift.
What's helping?
```

## 🛠 Technical Integration Points

### 1. **Velinor App Initialization** (`velinor_app.py`)

```python
# Automatically initializes FirstPerson on app startup
if 'firstperson_orchestrator' not in st.session_state:
    st.session_state.firstperson_orchestrator = FirstPersonOrchestrator(
        user_id='velinor_player',
        conversation_id='velinor_game'
    )
    st.session_state.firstperson_orchestrator.initialize_session()
```

### 2. **Game Initialization** (`start_new_game()`)

```python
# FirstPerson is passed to orchestrator when game starts
firstperson_orchestrator = st.session_state.get('firstperson_orchestrator')

orchestrator = VelinorTwineOrchestrator(
    game_engine=engine,
    story_path=str(story_path),
    first_person_module=firstperson_orchestrator,  # ← Connected here
    npc_system=None
)
```

### 3. **Player Input Processing** (`orchestrator.py`)

```python
# Player input is analyzed through FirstPerson
player_analysis = self._summarize_player_intent(player_input, player_id)

# Returns:
{
    'original_input': "I'm struggling with loss",
    'emotional_tone': 'heavy',
    'detected_theme': 'grief',
    'valence': -0.6,
    'intensity': 0.8,
    'memory_context': {
        'has_context': True,
        'recurring_themes': ['grief'],
        'emotional_trend': 'stable'
    }
}
```

### 4. **NPC Response Generation** (`_generate_npc_dialogue()`)

```python
# NPC response uses emotional analysis to craft nuanced dialogue
dialogue = self._generate_emotionally_aware_response(
    npc_name='Keeper',
    player_input='I feel lost',
    emotional_tone='heavy',
    theme='grief',
    valence=-0.7,
    intensity=0.7,
    memory=memory_context,
    npc_personality=npc_personality,
    is_multiplayer=False
)
```

## 📝 Response Generation Logic

The `_generate_emotionally_aware_response()` method constructs responses in three parts:

### 1. **Opening** (mirrors emotional tone)
```
uplifting:   "I feel that brightness too"
heavy:       "I hear the weight in that"
reflective:  "There's something to sit with there"
curious:     "Tell me more about that"
```

### 2. **Middle** (acknowledges theme + memory)
```
Theme acknowledgment:
- grief:     "Loss shapes us in ways words can't reach"
- joy:       "Joy that's felt this deeply matters"
- general:   "What you're naming has weight"

+ Memory awareness (if recurring):
"I'm noticing {theme} keeps coming back to you"
```

### 3. **Closing** (invites deeper exploration, adjusted for intensity)
```
High intensity (>0.7):  "What needs to be said about it?"
Low intensity (<0.3):   "What's sitting underneath that?"
Medium:                 "What would help you carry this?"
```

## 🧠 Conversation Memory System

FirstPerson maintains memory across turns:

### Tracked Elements
- **Turns**: Each turn records input, affect analysis, detected theme
- **Themes**: Tracks frequency, recency, intensity history
- **Entities**: People, relationships, work situations mentioned
- **Patterns**: Detects when themes recur (not just mentioned once)
- **Trajectory**: Analyzes if emotional trend is improving/worsening

### Memory Awareness Examples

**After 2-3 mentions of a theme:**
```python
frequency_reflection = orchestrator.memory.get_frequency_reflection("grief")
# Returns: "I'm hearing grief come up again. That's important."
```

**Emotional trend detection:**
```python
memory = orchestrator.memory.get_memory_context()
trend = memory['emotional_trend']  # 'improving', 'worsening', or 'stable'

if trend == 'worsening':
    response += " I'm noticing the weight increasing. What's happening?"
elif trend == 'improving':
    response += " What's helping?"
```

## 🚀 How to Run

### Local Development

```bash
# Activate venv if not already active
source venv/bin/activate

# Run the Velinor game
streamlit run velinor_app.py
```

The integration works automatically—no configuration needed!

### Testing the Integration

```bash
# Run the integration test
python3 FIRSTPERSON_INTEGRATION_TEST.py
```

Output shows:
- ✓ FirstPerson imports successful
- ✓ Orchestrator initialized
- ✓ Emotional analysis on sample inputs
- ✓ Memory tracking multi-turn conversations
- ✓ NPC response generation with emotional awareness

## 🔄 Data Flow Example

### Turn 1: Player expresses grief
```
Input:  "I keep thinking about what I lost"
Analysis: {
    tone: 'heavy',
    theme: 'grief',
    valence: -0.7,
    intensity: 0.6,
    memory: { has_context: false }
}
NPC Response:
"I hear the weight in that. Loss shapes us in ways words 
sometimes can't reach. What would help you carry this?"
```

### Turn 2: Player mentions same theme
```
Input:  "The grief just won't let go"
Analysis: {
    tone: 'heavy',
    theme: 'grief',
    valence: -0.8,
    intensity: 0.7,
    memory: { 
        has_context: true,
        recurring_themes: ['grief'],
        emotional_trend: 'stable',
        num_turns: 2
    }
}
NPC Response:
"I hear the weight in that. And I'm noticing grief keeps 
coming back to you. That tells me something. What needs 
to be said about it?"
```

### Turn 3: Player expresses slight improvement
```
Input:  "Maybe there's hope in how I'm remembering them"
Analysis: {
    tone: 'reflective',
    theme: 'grief',
    valence: -0.2,  # ← Improved!
    intensity: 0.4,
    memory: {
        has_context: true,
        recurring_themes: ['grief'],
        emotional_trend: 'improving',  # ← Detected!
        num_turns: 3
    }
}
NPC Response:
"There's something to sit with there. I'm also noticing 
a shift. What's helping? Tell me more about what you're 
remembering."
```

## 🎯 Features

✅ **Real-time Emotional Analysis** - Every player input is analyzed instantly  
✅ **Conversation Memory** - Multi-turn context awareness  
✅ **Theme Detection** - Identifies what the player is talking about  
✅ **Recurring Pattern Detection** - Notices when themes come back  
✅ **Emotional Trajectory** - Tracks if player is improving/worsening  
✅ **Adaptive NPC Responses** - Dialogue changes based on emotional state  
✅ **Graceful Fallback** - Works without FirstPerson if needed  
✅ **Multiplayer Aware** - Notes when others are listening  

## 🔐 No Secrets Required (Locally)

The integrated game works **without any configuration** for local development. FirstPerson analysis runs client-side, analyzing emotions without external API calls.

Optional: For cloud deployment or advanced features, you can add:
```toml
# .streamlit/secrets.toml (if deploying with Streamlit Cloud)
[firstperson]
enable_affect_analysis = true
session_scope = "velinor_game"
```

## 📚 Code Changes Summary

### Files Modified

1. **`velinor_app.py`**
   - Added FirstPerson imports
   - Initialize FirstPerson orchestrator at app startup
   - Pass FirstPerson to game engine

2. **`velinor/engine/orchestrator.py`**
   - Enhanced `_summarize_player_intent()` to extract emotional analysis
   - New `_generate_emotionally_aware_response()` for nuanced dialogue
   - Updated `_generate_npc_dialogue()` to use emotional context
   - Modified `process_player_action()` to attach emotional analysis

### New Functions

- `_summarize_player_intent()` - Analyzes player input through FirstPerson
- `_generate_emotionally_aware_response()` - Constructs NPC dialogue with emotional awareness
- `_generate_npc_dialogue()` - Routes to emotionally-aware response generation

### Integration Hooks

- FirstPerson orchestrator initialized in `velinor_app.py`
- Passed to `VelinorTwineOrchestrator` at game start
- Used in every `process_player_action()` call
- Feeds emotional analysis into NPC response generation

## 🎮 Example Gameplay

### Story Encounter: Keeper in the Market

**Game State:** Player meets Keeper in marketplace

**Player:** "I'm not sure if I can handle the responsibility of collecting glyphs. It feels overwhelming."

**FirstPerson Analysis:**
- Tone: `heavy`
- Theme: `general` (responsibility/burden)
- Valence: -0.6
- Intensity: 0.7

**NPC (Keeper) Response:**
"I hear the weight in that. The path of a glyph-seeker isn't without its burdens. What needs to be said about it? Sometimes the weight lessens when shared."

---

**Player:** "Maybe you're right. I think I just needed someone to acknowledge how hard this is."

**FirstPerson Analysis:**
- Tone: `reflective`
- Theme: `general`
- Valence: -0.2 ← (Improving!)
- Intensity: 0.4
- Memory: Detects emotional trajectory shift

**NPC (Keeper) Response:**
"There's something to sit with there. I'm also noticing a shift in what you're saying. What's helping you see this differently? That matters."

## 🛠 Troubleshooting

### "FirstPerson module not found"
```bash
# Make sure src/ is in Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/saoriverse-console/src"
streamlit run velinor_app.py
```

### "AttributeError on emotional_tone"
This means the emotional analysis didn't complete. The game gracefully falls back to basic responses. Check the terminal for errors.

### "Memory context empty"
This is expected on first turn. Memory builds up after multiple player inputs.

## 📖 Next Steps

1. **Test locally** - Run `streamlit run velinor_app.py` and notice how NPC responses adapt
2. **Play through scenarios** - See how dialogue changes based on your emotional expression
3. **Monitor the logs** - Check terminal output for emotional analysis data
4. **Expand story** - Add more passages and NPC encounters
5. **Deploy** - Push to Streamlit Cloud or your own server

## 📞 Support

If you need to:
- **Debug emotional analysis**: Check `FirstPersonOrchestrator.affect_parser` output
- **Adjust response tone**: Modify `_generate_emotionally_aware_response()` templates
- **Change themes detected**: Update `_extract_theme()` in FirstPerson module
- **Add new NPCs**: Use same response generation pattern with different personality templates

---

**Status:** ✅ **FirstPerson + Velinor Integration Complete**

The game is now emotionally aware and ready to deliver nuanced, responsive dialogue!

# LimbicAI Quick Start Guide

Get up and running with LimbicAI in 5 minutes!

## Option 1: Web Interface (Recommended)

### 1. Install Dependencies
```bash
cd D:\saoriverse-console
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python -m limbic_ai.app
```

### 3. Open in Browser
```
http://localhost:5000
```

### 4. Try It Out
- Paste a scenario in the text box
- Click "Analyze"
- View your limbic activation map!

**Example Scenario**:
```
My girlfriend broke up with me because she said I don't listen to her 
emotionally, but I think she's just too dramatic. Her job loss isn't 
that big a deal anyway. I don't understand why she's making such a fuss.
```

---

## Option 2: Command Line

### 1. Install Dependencies (2)
```bash
cd D:\saoriverse-console
pip install -r requirements.txt
```

### 2. Run Example
```bash
python examples.py
```

Choose from:
- `breakup_rationalization` - Dismissing emotional needs
- `job_loss_self_blame` - Internalizing responsibility
- `empathetic_response` - High empathy engagement
- `identity_threat` - Self-concept challenge
- `loss_aversion` - Future-focused regret

### 3. View Results
See feature extraction, limbic activations, and detailed analysis.

---

## Option 3: Python API

### Quick Import
```python
from limbic_ai import get_or_create_mind

mind = get_or_create_mind("demo-session")

turn = mind.step("I got fired and it's all my fault...")

## Access results
print(turn.limbic_state)
print(turn.emotional_features)
print(turn.state.narrative)
```

---

## Understanding the Output

### Limbic Activation Levels

```
Amygdala       (███████░░) 0.70  - Threat/rejection detection
Insula         (███░░░░░░) 0.30  - Empathy/body awareness
dlPFC          (████████░) 0.80  - Cognitive control
```

- **Low** (0-33%): System not strongly engaged
- **Medium** (33-67%): System moderately active
- **High** (67-100%): System strongly activated

### Brain Regions

| Region | What It Does |
|--------|-------------|
| **Amygdala** | Detects threat, triggers alarm |
| **ACC** | Monitors emotional pain, conflict |
| **Insula** | Feels others' emotions, body awareness |
| **vmPFC** | Decides what matters emotionally |
| **dlPFC** | Rationalizes, controls emotion |
| **Nucleus Accumbens** | Tracks losses and gains |
| **Hippocampus** | Forms emotional memories |

---

## Science Behind It

LimbicAI now uses a **persistent internal-state loop** to accumulate emotional and goal state over time:

1. **Parse** - Extract emotional features from incoming text
2. **State update** - Update memory, bodily state, valuation, goals, and self-model
3. **Conflict** - Let competing subsystems disagree and persist
4. **Narrate** - Build an ongoing first-person internal narrative
5. **Visualize** - Show the current state as a limbic-style map

**It is still not consciousness or a clinical diagnosis.** It is:
- ✅ Stateful across turns
- ✅ Modular, with separate memory, goal, conflict, and valuation loops
- ✅ Designed for agent-style continuity and self-modeling
- ❌ Not a human brain model
- ❌ Not clinically validated

---

## Common Patterns

### Pattern: High Rationalization + Low Empathy
**What it means**: Using logic to minimize emotional reality
```
"It's not a big deal. People deal with it all the time."
→ dlPFC high, Insula low
```

### Pattern: High Social Rejection + High Self-Blame
**What it means**: Internalizing relational pain
```
"They left because I'm not good enough."
→ Amygdala & ACC high, Self-blame high
```

### Pattern: High Empathy + Moderate Activation
**What it means**: Engaged but balanced processing
```
"I feel their pain and I want to help."
→ Insula high, balanced limbic state
```

---

## Troubleshooting

### Flask won't start?
```bash
pip install --upgrade flask werkzeug
```

### Module not found error?
```bash
## Make sure you're in the right directory
cd limbic_ai

## Install in development mode
pip install -e .
```

### Getting "scenario too short"? 
The system needs at least 10 words to meaningfully analyze.

---

## Next Steps

1. **Try web interface**: Watch the internal state accumulate across turns
2. **Explore examples**: Understand different patterns
3. **Review code**: Start with `limbic_ai/agent_core.py`
4. **Extend the state loop**: Add better memory, goals, or environment feedback
5. **Contribute**: Improve the model boundaries and evaluation

---

## Questions?

- Check the `README.md` for detailed docs
- Review `models.py` for data structures
- See `examples.py` for usage patterns
- Look at `tests.py` for expected behavior

Happy analyzing! 🧠

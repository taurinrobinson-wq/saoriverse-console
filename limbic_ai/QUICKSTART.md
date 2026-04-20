# LimbicAI Quick Start Guide

Get up and running with LimbicAI in 5 minutes!

## Option 1: Web Interface (Recommended)

### 1. Install Dependencies
```bash
cd limbic_ai
pip install -r requirements.txt
```

### 2. Start the Server
```bash
python app.py
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
cd limbic_ai
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
from limbic_ai import LimbicAnalyzer

analyzer = LimbicAnalyzer()

scenario = "I got fired and it's all my fault..."
analysis = analyzer.analyze(scenario)

## Access results
print(analysis.limbic_state)
print(analysis.emotional_features)
print(analyzer.get_summary(analysis))
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

LimbicAI uses **keyword density analysis** to identify emotional patterns:

1. **Parse** - Find emotion-related keywords in your text 2. **Weight** - Assign importance based on
frequency 3. **Map** - Convert to brain region activations 4. **Visualize** - Show limbic system
"heatmap" 5. **Explain** - Provide context and guidance

**It's not mind-reading!** Rather, it's:
- ✅ Evidence-based (grounded in neuroscience)
- ✅ Pattern recognition (keyword matching + weighting)
- ✅ Educational (helps you understand emotional mechanisms)
- ❌ Not diagnostic
- ❌ Not clinical judgment

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

1. **Try web interface**: Most user-friendly 2. **Explore examples**: Understand different patterns
3. **Read full README**: Deeper technical details 4. **Review code**: See how mapping works 5.
**Contribute**: Add features or improve NLP

---

## Questions?

- Check the `README.md` for detailed docs
- Review `models.py` for data structures
- See `examples.py` for usage patterns
- Look at `tests.py` for expected behavior

Happy analyzing! 🧠

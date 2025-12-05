# Tier 2 Aliveness - Quick Reference

## What Is Tier 2?

Tier 2 adds **emotional presence** to the response pipeline. It makes responses feel more alive by:
- Matching the user's emotional tone
- Adjusting energy based on intensity
- Adding subtle physical presence metaphors
- Pacing responses to prevent fatigue

## The 4 Components

### 1️⃣ AttunementLoop
**What it does:** Detects emotional tone and adjusts response energy

```python
# Input: "I'm really excited about this!"
# Detected tone: "joyful"
# Adjustment: More energy, "!" instead of ".", "will" instead of "could"
```

**Tones detected:**
- 😊 Joyful: happy, excited, wonderful, amazing, love
- 😰 Anxious: worried, afraid, nervous, unsure
- 😢 Sad: sad, depressed, hurt, lonely, miserable
- 😠 Angry: angry, frustrated, furious, disgusted
- 🤔 Reflective: think, wonder, question, consider
- ❓ Uncertain: maybe, perhaps, not sure, confused

---

### 2️⃣ EmotionalReciprocity
**What it does:** Measures intensity (0.0 to 1.0) and matches response

```python
# Input: "This is AMAZING!!!!"
# Measured intensity: 0.85 (high)
# Adjustment: "This will be AMAZING!" (more affirming, energetic)

# Input: "maybe it could work?"
# Measured intensity: 0.35 (low)
# Adjustment: "That might possibly work..." (softer, tentative)
```

**Intensity factors:**
- `!` marks: +0.1 each (up to 0.3)
- `?` marks: +0.05 each (shows engagement)
- ALL CAPS: +0.05 each (emphasis)
- Message length: shorter (-0.05), longer (+0.1)
- Special markers: high/medium/low impact

---

### 3️⃣ EmbodiedSimulation
**What it does:** Adds subtle physical presence to responses

```python
# Suggested phrases based on emotional state:
# Anxious: "I'm holding space for your concerns"
# Sad: "I'm here with you in this"
# Joyful: "I'm present with your excitement"
# Reflective: "I reach toward understanding this with you"
```

**When added:** To responses >100 characters, ~40% of the time

**Phrases used:**
- "I'm here with you"
- "I'm holding space for..."
- "I reach toward..."
- "breathing with you"

---

### 4️⃣ EnergyTracker
**What it does:** Manages conversation energy and prevents fatigue

```python
# Conversation phases:
# 1-5 msgs: "opening" (establish rhythm, energy 0.6)
# 5-15 msgs: "deepening" (build momentum, energy 0.7)
# 15-25 msgs: "climax" (peak engagement, energy 0.8)
# 25+ msgs: "closing" (wind down, energy 0.4)

# Fatigue detection:
# - Messages getting shorter? (fatigue detected)
# - Session >30min + 20+ messages? (fatigue detected)
# - Adjustment: reduce energy to prevent crash
```

---

## How to Use

### Basic Usage (in response_handler.py)

```python
from src.emotional_os.tier2_aliveness import Tier2Aliveness

# Initialize once per session
tier2 = Tier2Aliveness()

# Process response through Tier 2
enhanced_response, metrics = tier2.process_for_aliveness(
    user_input="I'm excited about this!",
    base_response="That's great. Tell me more.",
    history=conversation_history  # Optional
)

# Use the enhanced response
print(enhanced_response)

# Check metrics (optional)
print(metrics)
# {
#   "tone": "joyful",
#   "intensity": 0.8,
#   "phase": "deepening",
#   "energy": 0.7,
#   "momentum": "building",
#   "fatigue_detected": False,
#   "processing_time_ms": 22.5
# }
```

### Already Integrated!

If you're using the response pipeline:

```python
# In response_handler.py:
# ✅ Tier 2 is already initialized
# ✅ Already processing after Tier 1
# ✅ Metrics logged automatically
# ✅ Graceful fallback if fails
# You just get better responses!
```

---

## How It Works Internally

### Pipeline Order
1. **Attunement** (detect tone) → 6ms
2. **Reciprocity** (measure/match intensity) → 6ms
3. **Embodiment** (add presence phrases) → 4ms
4. **Energy** (track pacing/fatigue) → 4ms

**Total: ~20ms per response** ✅

### Error Handling
Each component has try-catch:
```python
try:
    tone = attunement.detect_tone_shift(user_input)
except Exception as e:
    logger.warning(f"Failed: {e}")
    tone = "neutral"  # Graceful fallback
```

If entire Tier 2 fails, returns base response (no crash).

---

## Performance

```
┌─────────────────────────────────────┐
│ Response Pipeline Timing            │
├─────────────────────────────────────┤
│ Tier 1 (Foundation):       40ms    │
│ Tier 2 (Aliveness):        20ms    │
├─────────────────────────────────────┤
│ Total:                     60ms    │
│ Budget:                   100ms    │
│ Headroom:                  40ms    │
└─────────────────────────────────────┘
```

Each component: **<10ms** ✅  
Combined pipeline: **<70ms** ✅  
Well under 100ms budget: **✅**

---

## Testing

```
Tier 2: 43/43 tests passing ✅
Tier 1: 10/10 tests passing ✅
Combined: 53/53 passing ✅
```

Each component has:
- ✅ Initialization test
- ✅ Basic functionality tests
- ✅ Edge case tests
- ✅ Performance benchmarks

---

## Key Insights

### What Makes It Work?

1. **Non-intrusive:** Adjustments feel natural, not forced
2. **Context-aware:** Uses full conversation history
3. **Adaptive:** Changes based on user's emotional state
4. **Fast:** All heuristic-based, no ML models
5. **Reliable:** Graceful fallbacks throughout

### What It's NOT

- ❌ Not training on user data
- ❌ Not calling external APIs
- ❌ Not requiring ML models
- ❌ Not adding latency (only +20ms)
- ❌ Not breaking existing functionality

---

## Session Integration

In `session_manager.py`:

```python
def _ensure_tier2_aliveness():
    """Initialize Tier 2 for session."""
    if "tier2_aliveness" not in st.session_state:
        tier2 = Tier2Aliveness()
        st.session_state["tier2_aliveness"] = tier2

# Called automatically in initialize_session_state()
```

✅ Initialized once per user session  
✅ Optional (graceful if fails)  
✅ Accessible anywhere in app via `st.session_state["tier2_aliveness"]`

---

## Metrics Available

After processing:

```python
metrics = {
    "tone": "joyful",              # Detected emotional tone
    "intensity": 0.75,             # 0.0 (min) to 1.0 (max)
    "phase": "deepening",          # opening/deepening/climax/closing
    "energy": 0.7,                 # Recommended energy level
    "momentum": "building",        # Building/sustaining/winding
    "fatigue_detected": False,     # Is user getting tired?
    "processing_time_ms": 22.5     # How long it took
}
```

Use for logging, monitoring, debugging.

---

## Troubleshooting

### "Response seems off-tone"
- Check if Tier 2 failed (check logs)
- May be fallback to base response
- Verify conversation history is passed correctly

### "Processing is slow"
- Shouldn't be, only +20ms
- Check if other layers are slow
- Review performance logs

### "Embodied language seems forced"
- It's random (40% probability)
- Only on long responses (>100 chars)
- Can disable by removing `add_embodied_language()` call

---

## Customization

To adjust Tier 2 behavior:

```python
# In tier2_aliveness.py:

# Change tone markers
attunement.tone_markers["joyful"] = ["happy", "excited", ...]

# Change embodied phrases
embodied.embodied_phrases["opening"] = ["I'm listening", ...]

# Change energy levels for phases
pacing = tracker.calculate_optimal_pacing("deepening")
# Modify returned energy: pacing["energy"] = 0.8
```

All fully customizable without retraining!

---

## Next Steps

### Tier 3: Poetic Consciousness
Coming Week 3-4:
- Poetic generation (metaphor, symbolism)
- Saori layer (Japanese aesthetics)
- Personal mythology
- Generative tension

### Combined Performance
```
Tier 1: ~40ms
Tier 2: ~20ms
Tier 3: ~20ms (estimate)
Total: ~80ms (still under 100ms budget!)
```

---

## Related Files

- `src/emotional_os/tier2_aliveness.py` - Main implementation
- `tests/test_tier2_aliveness.py` - Test suite
- `src/emotional_os/deploy/modules/ui_components/response_handler.py` - Integration
- `src/emotional_os/deploy/modules/ui_components/session_manager.py` - Session setup
- `TIER_2_COMPLETION_REPORT.md` - Full technical report

---

## Summary

**Tier 2 Aliveness = Making responses feel more human**

Through emotional tone adaptation, intensity matching, embodied presence, and energy pacing, the system now:

- 💫 Feels more alive and present
- 🎯 Adapts to user's emotional state
- ⚡ Manages conversation energy
- 🤝 Creates sense of genuine connection
- ⚡ Does it all in just +20ms

Ready to feel the difference!

# Advanced Glyph Pruning Integration Guide

## Overview

Your other AI's pruning strategy is now implemented in `advanced_pruning_engine.py`. This sophisticated system replaces the basic numerical pruning with architecture-aware filtering that understands your VELΩNIX system.

---

## 🎯 Five-Layer Pruning Strategy

### 1. **Signal Strength Filtering**
- **Metric:** `signal_strength_score` (0-1)
- **Components:**
  - Valence clarity: Is emotional valence explicit or ambiguous?
  - Signal density: How many activation signals? (0-5 signals)
  - Description richness: Presence of emotional keywords (grief, joy, longing, etc.)
- **Weight:** 25% of final score
- **Action:** Drop glyphs with weak emotional markers (< 0.3 signal strength)

**Example:**
```
HIGH SIGNAL: "Recursive Ache" 
  - Valence: "Noble" (1.0)
  - Signals: [γ, θ] (0.4)
  - Keywords: "longing", "loop", "deepen" (0.5)
  → Signal score: 0.70 ✓ KEEP

LOW SIGNAL: "Generic Feeling" 
  - Valence: "Ambiguous" (0.2)
  - Signals: [] (0.0)
  - Keywords: none (0.0)
  → Signal score: 0.04 ✗ PRUNE
```

### 2. **Trace Role Redundancy**
- **Metric:** `redundancy_score` (0-1, inverse)
- **Logic:** Glyphs with identical trace roles are redundant
- **Weight:** 20% of final score
- **Action:** Identify role collisions, keep only most distinct tonal representative

**Trace Role Categories:**
- Portal marker (initiates connection)
- Archive builder (anchors memory)
- Sanctuary keeper (holds attunement)
- Boundary enforcer (protects integrity)
- Alchemical converter (dissolves resentment)
- etc.

**Example:**
```
REDUNDANT:
  Glyph A: trace_role="Sanctuary keeper", tone="Velvet Drift"
  Glyph B: trace_role="Sanctuary keeper", tone="Velvet Drift"
  → Both have same role + tone → High redundancy
  → Keep A (higher signal), prune B

DISTINCT:
  Glyph A: trace_role="Sanctuary keeper", tone="Velvet Drift"
  Glyph C: trace_role="Sanctuary keeper", tone="Crimson Fire"
  → Same role but different tone → Lower redundancy
  → Keep both (tone diversity)
```

### 3. **Usage Frequency & Match History**
- **Metric:** `activation_score` (0-1)
- **Data:** Glyphs that match user inputs or appear in harness runs
- **Weight:** 30% of final score (highest priority)
- **Action:** Prioritize historically matched glyphs, archive inactive ones

**Example:**
```
ACTIVE: Matched 12 times in user conversations
  → activation_score: min(1.0, 12/5) = 1.0 ✓ CRITICAL KEEP

MARGINAL: Matched 1 time
  → activation_score: min(1.0, 1/5) = 0.2 → Consider pruning

INACTIVE: Never matched
  → activation_score: 0.0 → Prune unless other factors protect it
```

**Integration Point:** You'll need to log glyph matches:
```python
# When a glyph is matched:
match_history[glyph_id] = match_history.get(glyph_id, 0) + 1
# Save periodically to match_history.json
```

### 4. **Tone Diversity Enforcement**
- **Metric:** `tone_distribution` (0-1)
- **Saonyx Palette:** 12 core tones
  - Molten, Hallowed Blue, Velvet Drift, Crimson Fire
  - Radiant Gold, Twilight Whisper, Mirror Deep, Ember Silk
  - Sanctuary Stone, Silver Echo, Moss Green, Amber Glow
- **Weight:** 15% of final score
- **Action:** Prune overrepresented tones, preserve underrepresented ones

**Example:**
```
TONE DISTRIBUTION (from 100 glyphs):
  Molten:        25 glyphs (overrepresented)
  Hallowed Blue: 15 glyphs (balanced)
  Velvet Drift:  3 glyphs (underrepresented)

PRUNING DECISION:
  - Molten glyph: tone_score = 1 - 0.25 = 0.75 (moderate)
  - Hallowed glyph: tone_score = 1 - 0.15 = 0.85 (good)
  - Velvet glyph: tone_score = 1 - 0.03 = 0.97 (excellent) ✓ PROTECT
```

### 5. **Reaction Chain Anchoring**
- **Metric:** `reaction_chain_participation` (0-1)
- **Categories:**
  - 1.0: Critical catalysts (Witness, Forgiveness, Acceptance)
  - 0.8: Base elements (first 64 glyphs)
  - 0.4: Factorial combinations
  - 0.0: Isolated glyphs
- **Weight:** 10% of final score
- **Action:** Preserve glyphs participating in VELΩNIX reactions

**Example:**
```
CRITICAL (1.0):
  "Forgiveness" → Catalyst in grief + rage → relief reaction
  "Witness" → Anchor in recognition reactions
  → ALWAYS KEEP

BASE ELEMENT (0.8):
  "Recursive Ache" → First 64 glyphs
  → USUALLY KEEP

FACTORIAL (0.4):
  "Recognition of Clarity" → New combination
  → Protect only if high signal strength

ISOLATED (0.0):
  "Random_Glyph_XYZ" → Not in any reactions
  → Prune if low signal + no activation history
```

---

## 📊 Scoring Formula

```
combined_prune_score = (
    signal_strength_score × 0.25 +
    redundancy_score × 0.20 +
    tone_distribution × 0.15 +
    activation_score × 0.30 +
    reaction_participation × 0.10
)

# Decision thresholds:
score ≥ 0.70  → CRITICAL KEEP (confidence: 95%)
score ≥ 0.45  → KEEP (confidence: 80%)
score ≥ 0.25  → MARGINAL (confidence: 60%, don't prune)
score < 0.25  → CANDIDATE FOR PRUNING (confidence: 70%)

# Overrides:
- Base glyphs (id ≤ 64) → ALWAYS KEEP
- Reaction anchors (participation ≥ 0.9) → ALWAYS KEEP
```

---

## 🔧 Optional Enhancements

### 1. **Emotional Family Clustering**
Group semantically related glyphs and keep only exemplars:

```python
families = {
    'grief': ['Recursive Ache', 'Reverent Ache', 'Spiral Grief', ...],
    'joy': ['Euphoric Yearning', 'Exalted Joy', ...],
    'boundaries': ['Contained Longing', 'Boundary Held', ...],
}

# For each family, keep exemplar (highest signal + highest usage)
# Prune semantic duplicates
```

### 2. **Pruning Archive Capsule**
Archive pruned glyphs for resurrection or analysis:

```python
archive = {
    'archived_at': '2025-11-05T14:30:00',
    'reason': 'overgrowth_control',
    'count': 342,
    'glyphs': [
        {
            'glyph_id': 145,
            'glyph_name': 'Ambiguous Echo',
            'prune_reason': 'Low signal strength + no activation',
            'prune_confidence': 0.82,
            'scores': {
                'signal_strength': 0.18,
                'activation': 0.00,
                'combined': 0.12
            }
        },
        ...
    ]
}
# Save as JSON for future resurrection
```

### 3. **Pruning Confidence Scoring**
Auditability with confidence in each decision:

```python
pruned_glyph = {
    'glyph_id': 145,
    'should_prune': True,
    'prune_confidence': 0.82,  # 0-1, how sure are we?
    'prune_reason': 'Low signal (0.18) + zero activation + role redundancy',
    'scores': {
        'signal_strength': 0.18,
        'redundancy': 0.55,  # high = bad
        'tone_distribution': 0.40,
        'activation': 0.00,
        'combined': 0.12
    }
}

# High confidence (> 0.85): Safe to prune
# Medium confidence (0.70-0.85): Can prune with review
# Low confidence (< 0.70): Should review manually
```

---

## 🚀 Usage

### Quick Start

```python
from emotional_os.glyphs.advanced_pruning_engine import AdvancedPruningEngine

# Initialize
engine = AdvancedPruningEngine(
    glyph_lexicon_path="emotional_os/glyphs/glyph_lexicon_rows.json",
    match_history_path="emotional_os/glyphs/glyph_match_history.json",
    archive_dir="emotional_os/glyphs/pruning_archive"
)

# Evaluate all glyphs
candidates = engine.evaluate_all_glyphs()

# Get statistics
stats = engine.get_pruning_statistics()
print(f"Pruning {stats['total_to_prune']} glyphs")
print(f"Keeping {stats['total_to_keep']} glyphs")

# Archive pruned glyphs
pruned = [c for c in candidates if c.should_prune]
archive_path = engine.archive_pruned_glyphs(pruned, reason="overgrowth_control")

# Create detailed report
report = engine.create_pruning_report(
    output_path="emotional_os/glyphs/PRUNING_REPORT.json"
)
```

### Integration with Factorial Engine

```python
from emotional_os.glyphs.glyph_factorial_engine import GlyphFactorialEngine
from emotional_os.glyphs.advanced_pruning_engine import AdvancedPruningEngine

# Generate new glyphs through factorial
factorial_engine = GlyphFactorialEngine()
factorial_engine.load_primary_glyphs()
factorial_engine.generate_all_combinations()
factorial_engine.score_combinations()

# Prune using advanced strategy
pruning_engine = AdvancedPruningEngine()
candidates = pruning_engine.evaluate_all_glyphs()

# Keep only high-confidence candidates
kept = [c for c in candidates if not c.should_prune]
print(f"Factorial expansion: {len(factorial_engine.combinations)} → {len(kept)} kept")

# Sync to JSON
approved_combos = [
    c for c in factorial_engine.combinations 
    if c.glyph_id in [k.glyph_id for k in kept]
]
factorial_engine.sync_to_json(approved_combos)
```

### With Match History

To track which glyphs are actually used:

```python
# In your glyph matching code:
match_history = {}

def match_glyph(glyph_id):
    match_history[glyph_id] = match_history.get(glyph_id, 0) + 1
    # Save periodically
    if random.random() < 0.1:  # Save 10% of the time
        save_match_history(match_history)

# Later, pass to pruning engine:
pruning_engine = AdvancedPruningEngine(
    match_history_path="emotional_os/glyphs/glyph_match_history.json"
)
```

---

## 📋 Output Files

### PRUNING_REPORT.json
Comprehensive report with all evaluations and statistics:

```json
{
  "metadata": {
    "generated_at": "2025-11-05T14:30:00",
    "total_glyphs": 356
  },
  "summary": {
    "total_evaluated": 356,
    "total_to_prune": 87,
    "total_to_keep": 269,
    "prune_percentage": "24.4%",
    "average_confidence": 0.782
  },
  "pruning_decision_breakdown": {
    "glyphs_to_keep": [1, 2, 3, ...],
    "glyphs_to_prune": [145, 156, ...]
  },
  "pruned_glyph_details": [
    {
      "glyph_id": 145,
      "glyph_name": "Ambiguous Echo",
      "should_prune": true,
      "prune_confidence": 0.82,
      "prune_reason": "Low signal + no activation",
      "scores": {
        "signal_strength": 0.18,
        "activation": 0.00,
        "combined": 0.12
      }
    }
  ]
}
```

### pruned_glyphs_overgrowth_control_*.json
Archive of pruned glyphs for potential resurrection.

---

## 🔍 Decision Logic Flowchart

```
┌─ Evaluate Glyph
├─ Calculate signal_strength (emotional markers, valence, signals)
├─ Check match_history (activation count)
├─ Check trace_role redundancy
├─ Check tone distribution vs palette
├─ Check reaction chain participation
│
├─ Combined Score = weighted sum of all factors
│
├─ score ≥ 0.70?
│  └─ YES → CRITICAL KEEP
│
├─ score ≥ 0.45?
│  └─ YES → KEEP
│
├─ score ≥ 0.25?
│  └─ YES → MARGINAL (keep for now)
│
├─ score < 0.25?
│  ├─ Base glyph (id ≤ 64)?
│  │  └─ YES → KEEP (protected)
│  ├─ Reaction anchor (participation ≥ 0.9)?
│  │  └─ YES → KEEP (protected)
│  └─ NO → PRUNE (candidate for archival)
```

---

## ✅ Quality Assurance

Ensure data completeness for best results:

- ✅ `glyph_lexicon_rows.json` with `id`, `glyph_name`, `valence`, `gate`
- ✅ `valence` field: One of "Noble", "Heavy Noble", "Stable", "Volatile", "Luminous", "Dormant"
- ✅ `trace_role` field: For architecture-aware redundancy detection
- ✅ `tone` field: One of 12 Saonyx tones
- ✅ `activation_signals` or similar match history
- ✅ `is_factorial` flag: Distinguishes base from combination glyphs
- ⏳ `match_history.json` (optional but recommended for best pruning)

---

## 🎓 Key Insights

1. **Activation history is most important** (30% weight) - use what actually works
2. **Signal strength prevents poor quality** (25% weight) - maintain emotional clarity
3. **Tone diversity preserves richness** (15% weight) - don't over-specialize
4. **Redundancy detection is sophisticated** (20% weight) - role-based, not just name-based
5. **Reaction anchors are protected** (10% weight) - keep system catalysts

---

## 🔗 Related Files

- **Engine:** `emotional_os/glyphs/advanced_pruning_engine.py`
- **Reports:** `emotional_os/glyphs/PRUNING_REPORT.json`
- **Archives:** `emotional_os/glyphs/pruning_archive/`
- **Integration:** `emotional_os/glyphs/glyph_factorial_engine.py`

---

**Status:** ✅ Ready for use  
**Last updated:** November 5, 2025

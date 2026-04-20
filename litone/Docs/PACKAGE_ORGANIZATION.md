# LiToneCheck Package Organization

## Folder Structure

```
litone/
│
├── 📄 Core Modules (at root)
│   ├── __init__.py                  (Package entry point - v1.1.0)
│   ├── core.py                      (Main API - detect_tone, shift_tone, etc.)
│   ├── constants.py                 (Legal tones, signals, patterns)
│   ├── enhanced_affect_parser.py    (NLP: NRC, TextBlob, spaCy)
│   ├── tone_analysis_composer.py    (Tone analysis + transformations)
│   └── tone_signal_parser.py        (Pattern-based signal detection - α-Ω)
│
├── 📚 Docs/ (Documentation)
│   ├── SETUP_AND_VERIFICATION.md    (Quick start guide & test results)
│   ├── INTEGRATION_GUIDE.md         (Detailed usage guide with examples)
│   └── MODULE_INTEGRATION_SUMMARY.md (Technical architecture summary)
│
├── 🧪 Tests/ (Test Suite)
│   └── test_litone_integration.py   (6 test categories - all passing)
│
└── 🎨 Applications (at root)
    ├── litone/litone_app_v2.py             (Main Streamlit UI)
    └── litone_client.py             (Client utilities)
```

## Module Purposes at a Glance

| Module | Purpose | Status |
|--------|---------|--------|
| `constants.py` | Legal tone names, signals (α-Ω), patterns | ✅ Active |
| `enhanced_affect_parser.py` | Multi-method emotion/affect analysis | ✅ Active |
| `tone_analysis_composer.py` | Tone characteristics + transformation guidance | ✅ Active |
| `tone_signal_parser.py` | Lightweight signal detection (300 lines, no DB) | ✅ Active |
| `core.py` | Main API integrating all components | ✅ Active |

## Key Integrations

### 1. Enhanced Affect Parser
- **Multi-method approach:** NRC Lexicon + TextBlob + spaCy
- **Outputs:** emotion, valence, arousal, dominance, confidence
- **Used by:** core.detect_tone() strategy chain

### 2. Tone Analysis Composer
- **Analysis:** Identifies tone strengths, issues, recipient insights
- **Guidance:** Suggests transformations with difficulty levels
- **Adapted from:** Emotional OS dynamic_response_composer (chat → legal)

### 3. Tone Signal Parser  
- **Pattern matching:** Detects 7 core signals (α-Ω)
- **No database:** Pure regex patterns (fast & lightweight)
- **Alternative to:** 2400+ line signal_parser.py from emotional_os

### 4. Constants
- **Tone palette:** 5 tones (Very Formal → Empathetic) with emojis
- **Signal definitions:** 7 signals with descriptions
- **Pattern libraries:** Strong/moderate/weak patterns per signal

## How to Use

### Example 1: Basic Tone Detection
```python
from litone import detect_tone

analysis = detect_tone("This shall be binding.")
print(analysis['tone'])        # Very Formal
print(analysis['confidence'])  # 0.XX
```

### Example 2: Signal Detection
```python
from litone.tone_signal_parser import create_tone_signal_parser

parser = create_tone_signal_parser()
signals = parser.analyze_text("I understand your concerns.")
print(signals.primary_signal_name)  # γ (Longing/Understanding)
```

### Example 3: Affect Analysis
```python
from litone.enhanced_affect_parser import create_enhanced_affect_parser

parser = create_enhanced_affect_parser()
affect = parser.analyze("This is concerning.")
print(affect.primary_emotion)  # fear (from concern keywords)
```

## Why This Organization?

✅ **Self-contained:** All litone code in one folder ✅ **Organized:** Docs and Tests in clear
subfolders ✅ **Lightweight:** Signal parser doesn't require external database ✅ **Integrated:**
core.py uses all components seamlessly ✅ **Documented:** Multiple guides at different detail levels
✅ **Tested:** 6 test categories, all passing ✅ **Backward compatible:** Existing code unchanged ✅
**Production ready:** No synthetic scaffolding

## Access Documentation

- **Quick Start:** `Docs/SETUP_AND_VERIFICATION.md`
- **Detailed Guide:** `Docs/INTEGRATION_GUIDE.md`
- **Architecture:** `Docs/MODULE_INTEGRATION_SUMMARY.md`

## Run Tests

```bash
cd d:\saoriverse-console
py -3.12 -c "import sys; sys.path.insert(0, '.'); from litone.Tests.test_litone_integration import *"
```

**Result:** All tests ✅ passing

---

**Package Version:** 1.1.0
**Status:** Production Ready

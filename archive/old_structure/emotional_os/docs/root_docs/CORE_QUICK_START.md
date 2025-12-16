# Quick Start: Consolidated Emotional OS Core

## 🎯 The New Way

All your core functionality is now in one place:

```python
from emotional_os.core import (
    # Main functions
    parse_input,
    LexiconLearner,

    # Constants
    SIGNALS,
    ECM_GATES,
    SIGNAL_MAPPING,

    # Path management
    signal_lexicon_path,
    learned_lexicon_path,
    pattern_history_path,
    glyph_db_path,
)
```

##

## 📚 Common Tasks

### Parse User Input

```python
from emotional_os.core import parse_input, signal_lexicon_path

result = parse_input(
    input_text="I feel deeply moved by this",
    lexicon_path=str(signal_lexicon_path()),
    db_path="glyphs.db"
)

print(result["signals"])  # Emotional signals detected
print(result["gates"])    # Activated ECM gates
print(result["glyphs"])   # Matched glyphs
```

### Learn from Conversation

```python
from emotional_os.core import LexiconLearner

learner = LexiconLearner()

# Learn from conversation data
learning_results = learner.learn_from_conversation({
    "messages": [
        {"type": "user", "content": "I feel anxious about the future"},
        {"type": "system", "content": "That uncertainty can be scary..."},
    ]
})

# Update lexicon
learner.update_lexicon_from_learning(learning_results)

# Get stats
stats = learner.get_learning_stats()
print(f"Learned {stats['learned_lexicon_size']} new words")
```

### Access Constants

```python
from emotional_os.core import SIGNALS, ECM_GATES, EMOTIONAL_PATTERNS

# All 7 signals
for signal, meaning in SIGNALS.items():
    print(f"{signal}: {meaning}")

# All 6 gates and their signal mappings
for gate, signals in ECM_GATES.items():
    print(f"{gate}: {signals}")

# Regex patterns for emotion extraction
patterns = EMOTIONAL_PATTERNS
feeling_exprs = patterns["feeling_expressions"]
```

### Manage Paths

```python
from emotional_os.core.paths import PathManager, signal_lexicon_path

# Get individual paths
lexicon = signal_lexicon_path()
history = pattern_history_path()

# Use PathManager directly for more control
pm = PathManager()
lexicon_path = pm.signal_lexicon()
poetry_dir = pm.poetry_data_dir()

# Create directory if needed
pm.ensure_dir(poetry_dir)
```

##

## 🔄 Backward Compatibility

All old imports still work:

```python

# ❌ Old (but still works)
from parser.signal_parser import parse_input
from learning.lexicon_learner import LexiconLearner
from emotional_os.glyphs.signal_parser import parse_input

# ✅ New (recommended)
from emotional_os.core import parse_input, LexiconLearner

# Both work identically!
```

##

## 📁 File Organization

```
emotional_os/core/
├── __init__.py              # Import everything from here
├── constants.py             # All signal/gate/pattern definitions
├── paths.py                 # Path resolution
├── signal_parser.py         # Emotional signal extraction & glyph matching
└── lexicon_learner.py       # Learn patterns from conversations
```

### What's in Each File

**`__init__.py`** - Main entry point

```python
from emotional_os.core import (
    # Everything you need is exported here
    parse_input,
    LexiconLearner,
    SIGNALS,
    ECM_GATES,
    # ... etc
)
```

**`constants.py`** - All configuration

```python
SIGNALS = {'α': 'Devotion/Sacred', ...}
ECM_GATES = {'Gate 2': ['β'], ...}
EMOTIONAL_PATTERNS = {'feeling_expressions': [...], ...}

# ... all constants centralized
```

**`paths.py`** - Smart path resolution

```python
PathManager()  # Resolves paths with intelligent fallbacks
signal_lexicon_path()  # Returns path to signal lexicon
learned_lexicon_path()  # Returns path to learned lexicon

# ... handles migration/multiple locations seamlessly
```

**`signal_parser.py`** - Core parsing engine

```python
parse_input()  # Main parsing function
parse_signals()  # Extract signals from text
evaluate_gates()  # Activate ECM gates
fetch_glyphs()  # Get matching glyphs

# ... all signal parsing functionality
```

**`lexicon_learner.py`** - Learning system

```python
LexiconLearner()  # Main learner class
learn_from_conversation()  # Extract patterns
extract_emotional_patterns()  # Find emotional language
update_lexicon_from_learning()  # Add new words to lexicon

# ... all learning functionality
```

##

## 🎯 Signals & Gates Reference

### 7 Core Signals

```python
from emotional_os.core import SIGNALS

α  - Devotion/Sacred       (vow, sacred, devoted, honor)
β  - Boundary/Contain      (protect, guard, boundary, shield)
γ  - Longing/Ache          (yearn, ache, crave, long for)
θ  - Grief/Mourning        (loss, grief, mourn, sorrow)
λ  - Joy/Delight           (joy, delight, happy, bliss)
ε  - Insight/Clarity       (clarity, understand, insight, knowing)
Ω  - Recognition/Witnessing (seen, witnessed, recognized, heard)
```

### 6 ECM Gates

```python
from emotional_os.core import ECM_GATES

Gate 2:  β                    # Boundary
Gate 4:  γ, θ                # Longing + Grief
Gate 5:  λ, ε, δ             # Joy + Insight
Gate 6:  α, Ω, ε             # Devotion + Recognition + Insight
Gate 9:  α, β, γ, δ, ε, Ω    # Multiple signals
Gate 10: θ                    # Grief alone
```

##

## 🚀 Advanced Usage

### Use Custom Lexicon Paths

```python
from emotional_os.core import LexiconLearner

learner = LexiconLearner(
    base_lexicon_path="/path/to/custom/signals.json"
)
```

### Process Multiple Inputs

```python
from emotional_os.core import parse_input, signal_lexicon_path

inputs = [
    "I feel deeply grateful",
    "I'm struggling with this",
    "I feel seen and understood"
]

lexicon_path = str(signal_lexicon_path())

for user_input in inputs:
    result = parse_input(user_input, lexicon_path)
    print(f"Input: {user_input}")
    print(f"Signals: {result['signals']}")
    print()
```

### Get Learning Statistics

```python
from emotional_os.core import LexiconLearner

learner = LexiconLearner()
stats = learner.get_learning_stats()

print(f"Base vocabulary: {stats['base_lexicon_size']} words")
print(f"Learned vocabulary: {stats['learned_lexicon_size']} words")
print(f"Total patterns tracked: {stats['total_patterns']}")
print(f"Last updated: {stats['last_updated']}")
print(f"Top learned words: {stats['top_learned_words']}")
```

##

## 🐛 Troubleshooting

### Import Error?

```python

# Make sure you're using the canonical import:
from emotional_os.core import parse_input  # ✅ Correct

# Not:
from emotional_os.glyphs.signal_parser import parse_input  # ❌ Works but outdated
```

### Path Not Found?

```python
from emotional_os.core.paths import signal_lexicon_path

path = signal_lexicon_path()
print(f"Resolved path: {path}")
print(f"Exists: {path.exists()}")

# If not found, check these locations:

# - parser/signal_lexicon.json

# - data/lexicons/signal_lexicon.json

# - emotional_os/parser/signal_lexicon.json
```

### Lexicon Not Updating?

```python
from emotional_os.core import LexiconLearner

learner = LexiconLearner()
results = learner.learn_from_conversation(data)
learner.update_lexicon_from_learning(results)

# Check that learned_lexicon.json exists:
from emotional_os.core.paths import learned_lexicon_path
print(learned_lexicon_path())
```

##

## 📝 Migration Checklist

Moving existing code to canonical imports?

- [ ] Find all imports of `signal_parser.py`
- [ ] Replace with `from emotional_os.core import parse_input`
- [ ] Find all imports of `lexicon_learner.py`
- [ ] Replace with `from emotional_os.core import LexiconLearner`
- [ ] Find all direct constant references
- [ ] Replace with imports from `emotional_os.core`
- [ ] Test that code still works
- [ ] Commit with message: "Migrate: Use canonical emotional_os.core imports"

##

## 🎓 Learning Path

1. **Understand the signals** - Read about the 7 signals and what they represent
2. **Parse some input** - Use `parse_input()` to extract signals from text
3. **Explore the gates** - See which gates activate for different signal combinations
4. **Learn from conversations** - Use `LexiconLearner` to extract patterns
5. **Customize lexicons** - Add new words and emotional mappings
6. **Integrate with glyphs** - Use parsed signals to fetch glyphs

##

## 📚 Documentation

- **CONSOLIDATION_ANALYSIS.md** - Why consolidation was needed
- **CONSOLIDATION_COMPLETE.md** - Migration guide for the consolidation
- **CONSOLIDATION_STATUS.md** - Summary of what was achieved

##

## 💡 Pro Tips

1. **Always use centralized imports** - Easier to refactor later
2. **Leverage PathManager** - Handles path resolution automatically
3. **Check constants first** - Don't hardcode gate numbers, use ECM_GATES
4. **Test lexicon learning** - New words get added automatically
5. **Use get_learning_stats()** - Monitor what the system is learning

##

## 🎉 You're All Set

The consolidation is complete and working. Your codebase is now:

- ✅ Cleaner (no duplication)
- ✅ Faster to maintain (single source of truth)
- ✅ Easier to understand (clear structure)
- ✅ Production-ready (fully tested)

Start using `from emotional_os.core import ...` in new code! 🚀

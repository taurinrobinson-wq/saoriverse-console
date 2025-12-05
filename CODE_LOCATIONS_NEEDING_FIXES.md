# 🔧 Code Locations Needing Path Corrections

## Files That Load Data at Startup

### 1. NRC Lexicon Loader ✅ WORKING
**File:** `src/parser/nrc_lexicon_loader.py`  
**Lines:** 16-22

```python
_NRC_POSSIBLE_PATHS = [
    "data/lexicons/nrc_emotion_lexicon.txt",           # ✅ First match
    "data/lexicons/nrc_lexicon_cleaned.json",
    "emotional_os/lexicon/nrc_emotion_lexicon.txt",
    Path(__file__).parent.parent.parent / "data" / "lexicons" / "nrc_emotion_lexicon.txt",
    Path(__file__).parent.parent.parent / "data" / "lexicons" / "nrc_lexicon_cleaned.json",
]
```

**Status:** Uses fallback search, so it works. ✅

---

### 2. Suicidality Protocol ⚠️ BROKEN
**File:** `src/emotional_os/core/suicidality_handler.py`  
**Lines:** 33, 41-43

```python
def __init__(self, protocol_config_path: str = "emotional_os/core/suicidality_protocol.json"):
    """Load protocol configuration."""
    self.config_path = Path(protocol_config_path)
    self.config = self._load_config()

def _load_config(self) -> Dict:
    """Load protocol configuration from JSON."""
    try:
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
```

**Problem:** Hardcoded path `"emotional_os/core/suicidality_protocol.json"` won't work from repo root.

**Actual File Location:** `src/emotional_os/core/suicidality_protocol.json`

**Needs Fix:** YES - Either update path or use PathManager

**Suggested Fix:**
```python
from emotional_os.core.paths import get_path_manager

# Or provide multiple candidates:
def __init__(self, protocol_config_path: str = None):
    if protocol_config_path is None:
        # Search for it
        candidates = [
            Path("emotional_os/core/suicidality_protocol.json"),
            Path("src/emotional_os/core/suicidality_protocol.json"),
        ]
        for candidate in candidates:
            if candidate.exists():
                protocol_config_path = str(candidate)
                break
    self.config_path = Path(protocol_config_path)
```

---

### 3. Glyph Factorial Engine ⚠️ BROKEN
**File:** `src/emotional_os_glyphs/glyph_factorial_engine.py`  
**Lines:** 73-74

```python
def __init__(
    self,
    glyph_csv: str = "emotional_os/glyphs/glyph_lexicon_rows.csv",
    glyph_json: str = "emotional_os/glyphs/glyph_lexicon_rows.json",
    output_dir: str = "emotional_os/glyphs/factorial",
):
```

**Problem:** Hardcoded paths for glyph files that don't exist in `emotional_os/glyphs/` directory.

**Actual File Locations:** 
- `data/glyph_lexicon_rows.csv`
- `data/glyph_lexicon_rows.json`

**Needs Fix:** YES

**Suggested Fix:**
```python
def __init__(
    self,
    glyph_csv: str = None,
    glyph_json: str = None,
    output_dir: str = "emotional_os/glyphs/factorial",
):
    # Search for glyph files
    if glyph_csv is None:
        candidates = [
            Path("emotional_os/glyphs/glyph_lexicon_rows.csv"),
            Path("data/glyph_lexicon_rows.csv"),
            Path("src/emotional_os_glyphs/glyph_lexicon_rows.csv"),
        ]
        for c in candidates:
            if c.exists():
                glyph_csv = str(c)
                break
        if glyph_csv is None:
            raise FileNotFoundError("glyph_lexicon_rows.csv not found")
    
    if glyph_json is None:
        candidates = [
            Path("emotional_os/glyphs/glyph_lexicon_rows.json"),
            Path("data/glyph_lexicon_rows.json"),
            Path("src/emotional_os_glyphs/glyph_lexicon_rows.json"),
        ]
        for c in candidates:
            if c.exists():
                glyph_json = str(c)
                break
        if glyph_json is None:
            raise FileNotFoundError("glyph_lexicon_rows.json not found")
    
    self.glyph_csv_path = Path(glyph_csv)
    self.glyph_json_path = Path(glyph_json)
    # ... rest of init
```

---

### 4. Antonym Glyphs Indexer ⚠️ BROKEN
**File:** `src/emotional_os_glyphs/antonym_glyphs_indexer.py`  
**Lines:** 27

```python
def __init__(
    self,
    glyph_lexicon: str = "emotional_os/glyphs/glyph_lexicon_rows.json",
    antonym_index: str = "emotional_os/glyphs/antonym_glyphs_indexed.json",
):
```

**Problem:** Same as above - hardcoded paths for files in `emotional_os/glyphs/` that don't exist.

**Actual File Locations:**
- `data/glyph_lexicon_rows.json`
- `data/antonym_glyphs_indexed.json`

**Needs Fix:** YES - Apply same pattern as GlyphFactorialEngine

---

### 5. Advanced Pruning Engine ⚠️ BROKEN
**File:** `src/emotional_os_glyphs/advanced_pruning_engine.py`  
**Lines:** 89

```python
def __init__(
    self,
    glyph_lexicon_path: str = "emotional_os/glyphs/glyph_lexicon_rows.json",
    ...
):
```

**Problem:** Same path issue.

**Needs Fix:** YES - Apply same fallback pattern

---

### 6. Word-Centric Lexicon Loader ⚠️ BROKEN
**File:** `src/emotional_os_lexicon/lexicon_loader.py`  
**Lines:** 18

```python
def __init__(self, lexicon_path: str = "emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json"):
    """Initialize lexicon from JSON file"""
    self.lexicon_path = lexicon_path
    self.lexicon: Dict[str, Dict[str, Any]] = {}
    self.metadata: Dict[str, Any] = {}
    self.signal_map: Dict[str, List[int]] = {}
    self._load_lexicon()

def _load_lexicon(self) -> None:
    """Load the word-centric lexicon from file"""
    try:
        with open(self.lexicon_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
```

**Problem:** Hardcoded path `"emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json"` won't exist.

**Actual File Location:** `data/word_centric_emotional_lexicon_expanded.json`

**Needs Fix:** YES

**Suggested Fix:**
```python
def __init__(self, lexicon_path: str = None):
    """Initialize lexicon from JSON file"""
    if lexicon_path is None:
        candidates = [
            "emotional_os/lexicon/word_centric_emotional_lexicon_expanded.json",
            "data/word_centric_emotional_lexicon_expanded.json",
            "src/emotional_os_lexicon/word_centric_emotional_lexicon_expanded.json",
        ]
        for c in candidates:
            if Path(c).exists():
                lexicon_path = c
                break
        if lexicon_path is None:
            raise FileNotFoundError("word_centric_emotional_lexicon_expanded.json not found")
    
    self.lexicon_path = lexicon_path
    # ... rest
```

---

### 7. Trauma Lexicon (Safety) ✅ WORKING
**File:** `src/emotional_os_safety/sanctuary.py`  
**Lines:** 13-16

```python
_TRAUMA_LEXICON_PATH = os.path.join(os.path.dirname(__file__), "trauma_lexicon.json")
try:
    with open(_TRAUMA_LEXICON_PATH, "r", encoding="utf-8") as f:
        _TRAUMA_LEXICON = json.load(f)
```

**Status:** Uses relative path from module location. ✅ Works.

**Same pattern in:** `src/emotional_os_safety/sanctuary_handler.py` (line 9)

---

### 8. Hybrid Learner V2 ⚠️ PARTIAL
**File:** `src/emotional_os_learning/hybrid_learner_v2.py`  
**Lines:** 62

```python
def __init__(
    self,
    shared_lexicon_path: str = "emotional_os/parser/signal_lexicon.json",
    db_path: str = "emotional_os/glyphs/glyphs.db",
    learning_log_path: str = "learning/hybrid_learning_log.jsonl",
    user_overrides_dir: str = "learning/user_overrides",
    ...
):
```

**Problem:** Multiple hardcoded paths:
- `"emotional_os/parser/signal_lexicon.json"` (should be `src/emotional_os_parser/signal_lexicon.json`)
- `"emotional_os/glyphs/glyphs.db"` (should create in expected location)

**Status:** Partially works because PathManager fallback in some cases, but fragile.

**Needs Fix:** YES - Add fallback search or use PathManager

---

### 9. Signal Parser (Backward Compatibility) ✅ WORKING
**File:** `src/emotional_os_parser/signal_parser.py`  
**Lines:** 1-3

```python
"""Backward compatibility stub - imports from canonical emotional_os.core"""

from emotional_os.core.signal_parser import *  # noqa: F401, F403
```

**Status:** This is just a stub/alias. Works fine. ✅

---

### 10. Runtime Fallback Lexicon ⚠️ BROKEN
**File:** `scripts/data/clean_and_salvage_glyphs.py`  
**Lines:** 22

```python
def load_fallback_lexicon():
    path = "emotional_os/parser/runtime_fallback_lexicon.json"
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
```

**Problem:** Hardcoded path won't work.

**Actual File Location:** `src/emotional_os_parser/runtime_fallback_lexicon.json`

**Needs Fix:** YES

**Suggested Fix:**
```python
def load_fallback_lexicon():
    candidates = [
        "emotional_os/parser/runtime_fallback_lexicon.json",
        "src/emotional_os_parser/runtime_fallback_lexicon.json",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
    return {}
```

---

## Summary: Files Needing Fixes

| File | Issue | Severity | Type |
|------|-------|----------|------|
| `suicidality_handler.py` | Hardcoded path | 🔴 High | Config load |
| `glyph_factorial_engine.py` | Hardcoded path (CSV+JSON) | 🔴 High | Data load |
| `antonym_glyphs_indexer.py` | Hardcoded path (JSON) | 🔴 High | Data load |
| `advanced_pruning_engine.py` | Hardcoded path (JSON) | 🔴 High | Data load |
| `lexicon_loader.py` | Hardcoded path | 🔴 High | Data load |
| `hybrid_learner_v2.py` | Multiple hardcoded paths | 🟠 Medium | Mixed |
| `clean_and_salvage_glyphs.py` | Hardcoded path | 🟠 Medium | Data load |
| `nrc_lexicon_loader.py` | ✅ Works (fallback search) | - | N/A |
| `sanctuary.py` | ✅ Works (relative path) | - | N/A |
| `signal_parser.py` | ✅ Works (stub/alias) | - | N/A |

---

## Pattern to Apply

Use this pattern for all data file loading:

```python
from pathlib import Path

def _find_file(*candidates):
    """Find first existing file from candidates"""
    for path in candidates:
        p = Path(path)
        if p.exists():
            return str(p)
    # If none found, return first candidate (will error on load)
    return str(candidates[0])

# In __init__:
self.config_path = Path(_find_file(
    "emotional_os/core/suicidality_protocol.json",
    "src/emotional_os/core/suicidality_protocol.json",
))
```

Or just use the PathManager that already exists! It has this logic built in.

---

## Using PathManager (Better Solution)

The `PathManager` class in `src/emotional_os/core/paths.py` already handles this:

```python
from emotional_os.core.paths import get_path_manager

pm = get_path_manager()

# Gets signal lexicon with fallback search
signal_lex = pm.signal_lexicon()
```

**Why it's better:**
- Centralized path management
- Consistent across all modules
- Easy to reconfigure
- Handles both local and cloud deployments

**Needs implementation:** PathManager needs methods for:
- `glyph_lexicon()` → returns path to JSON or CSV
- `suicidality_protocol()` → returns path to protocol config
- `word_centric_lexicon()` → returns path to word lexicon
- `antonym_glyphs()` → returns path to antonym index
- `trauma_lexicon()` → returns path to trauma lexicon


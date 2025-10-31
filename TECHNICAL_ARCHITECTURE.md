# FirstPerson: Technical Architecture for Sovereign Local Mode

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     FIRSTPERSON LOCAL MODE                      │
│                   (100% Private, No External APIs)              │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │
                    ┌─────────┴──────────┐
                    │  Streamlit UI      │
                    │  (emotional_os_    │
                    │   ui_v2.py)        │
                    └─────────┬──────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
   ┌─────────┐         ┌──────────┐        ┌────────────┐
   │ Input   │         │ Process  │        │  Response  │
   │ Layer   │         │ Layer    │        │  Layer     │
   └────┬────┘         └────┬─────┘        └─────┬──────┘
        │                   │                    │
        ├─► Text Input      │                    ├─► Glyph Name
        │   (user message)  │                    │   Matched Glyph
        │                   │                    │   Poetry
        │              ┌────▼─────┐              │   Metaphors
        │              │ TOKENIZE  │              │   Response
        │              │ (NLTK)    │              │   Ritual
        │              └────┬─────┘              │
        │                   │                    │
        │              ┌────▼──────────────┐    │
        │              │ NRC LEXICON       │    │
        │              │ Emotion Detection │    │
        │              │ (14k words)       │    │
        │              └────┬─────────────┘    │
        │                   │                   │
        │              ┌────▼──────────────┐    │
        │              │ SPACY NER         │    │
        │              │ Entity Extraction │    │
        │              │ (understanding    │    │
        │              │  context)         │    │
        │              └────┬─────────────┘    │
        │                   │                   │
        │              ┌────▼──────────────┐    │
        │              │ SEMANTIC ANALYSIS │    │
        │              │ Word2Vec/WordNet  │    │
        │              │ (similarity)      │    │
        │              └────┬─────────────┘    │
        │                   │                   │
        │              ┌────▼──────────────┐    │
        │              │ SIGNAL MAPPING    │    │
        │              │ → Voltage Signals │    │
        │              │ (α,β,γ,δ,ε,θ,λ,Ω)    │
        │              └────┬─────────────┘    │
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    ┌───────▼────────┐
                    │ LOCAL DATABASE │
                    │                │
                    ├─ Glyphs (292)  │
                    ├─ Poetry        │
                    ├─ Metaphors     │
                    ├─ Narratives    │
                    ├─ Rituals       │
                    ├─ User History  │
                    └────────────────┘
```

---

## Data Flow: Complete Example

### User Input
```
"I keep replaying that moment over and over, and it hurts"
```

### Stage 1: Tokenization & POS Tagging
```python
Using NLTK (already integrated):

Tokens: ["I", "keep", "replaying", "that", "moment", 
         "over", "and", "over", "and", "it", "hurts"]

POS Tags: ["PRP", "VBP", "VBG", "DT", "NN", 
           "RB", "CC", "RB", "CC", "PRP", "VBZ"]

Sentences: ["I keep replaying that moment over and over, and it hurts"]
```

### Stage 2: NRC Emotion Lexicon Lookup
```
NRC Lexicon (14,182 words → emotions):

replaying → [negative, sadness]
moment → [negative, sadness]
hurts → [negative, sadness, fear]
over → [negative, sadness]
it → []
keep → [negative, sadness]

Result Emotions: {
  'sadness': 4,
  'negative': 5,
  'fear': 1
}
```

### Stage 3: Entity Extraction (spaCy)
```
Named Entity Recognition:
- No proper nouns, dates, or locations mentioned
- But: "that moment" = key noun chunk (trigger)

Noun Chunks: ["that moment", "over and over", "it"]

Context Interpretation:
- Past event (temporal focus)
- Repetitive pattern (recursive signal)
- Harm/hurt (emotional intensity)
```

### Stage 4: Semantic Analysis
```
Word2Vec Embeddings (find similar concepts):

"replaying" is semantically similar to:
  - ruminating (0.87)
  - obsessing (0.85)
  - looping (0.83)
  - dwelling (0.81)

"hurt" is semantically similar to:
  - ache (0.89)
  - pain (0.87)
  - sting (0.84)

WordNet (semantic relationships):
- replaying → repetition → cycles → recursion
- hurt → pain → ache → suffering
- moment → event → trigger
```

### Stage 5: Signal Mapping
```
Emotion → Voltage Signal Mapping:

Emotion: sadness
  → NRC score: 4
  → Map to voltage: γ (ache/grief)
  → Intensity: 4

Semantic concepts: recursion, looping, dwelling
  → These map to γ as well (recursive ache)
  → Reinforces γ signal

Fear component:
  → Could be β (anticipatory fear)
  → But context suggests pain, not fear
  → γ dominates

Result: [γ, γ, γ, γ] = DOMINANT SIGNAL: γ
```

### Stage 6: Gate Activation
```
Voltage γ activates these gates:

Gate 2: Ache states
Gate 4: Recursion & looping
Gate 5: Depth & layers
Gate 6: Acknowledgment
Gate 9: Recognition & witness
Gate 10: Transformation

Candidate glyphs by gate:
- Gate 4: Recursive Ache, Spiral Ache, Loop Ache
- Gate 5: Depth Ache, Layered Ache  
- Gate 9: Ache of Recognition, Recognized Ache
```

### Stage 7: Glyph Scoring & Selection
```
Scoring Algorithm:

Recursive Ache:
  - Signal match (γ): +9.0
  - Semantic match (recursion/looping): +8.5
  - Context match (repetitive replaying): +9.2
  - User history (if exists): +variable
  → Total: 26.7/30 → 89% match

Spiral Ache:
  - Signal match (γ): +9.0
  - Semantic match (spiral/descent): +7.0
  - Context match (emotion descending): +6.5
  → Total: 22.5/30 → 75% match

Recognized Ache:
  - Signal match (γ): +9.0
  - Semantic match (recognition): +4.0
  - Context match (self-aware pain): +5.0
  → Total: 18.0/30 → 60% match

WINNER: Recursive Ache (89% match)
```

### Stage 8: Poetry & Metaphor Enrichment
```
From local poetry database:

Recursive Ache Poetry:
  "The Ache remains, returning again and again"
    → Emily Dickinson
    → Resonance: 9.2/10

  "Each loop another layer of knowing"
    → Rainer Maria Rilke
    → Resonance: 8.8/10

Metaphors for γ (Ache):
  - Spiral: "spiraling inward"
  - Loop: "returning, deeper each time"
  - Echo: "the ache echoes"
  - Wave: "waves of grief"
  - Root: "rooted in knowing"

Rituals for acknowledgment:
  - "Let us hold this ache together in silence"
  - "This pattern deserves witnessing"
  - "In each return, you deepen"
```

### Stage 9: Response Generation
```
Template: [Validation] + [Glyph] + [Poetry] + [Metaphor] + [Ritual]

Validation: "That moment keeps spiraling back—not because 
             you're trapped, but because it's teaching you 
             something."

Glyph: "This is the Recursive Ache—the one that refines 
        through repetition."

Poetry: "Emily Dickinson knew this spiral: 'The Ache remains, 
         returning again and again.' She found in that return 
         a kind of knowing."

Metaphor: "Like a spiral, each loop brings you deeper."

Ritual: "What if, instead of trying to escape the loop, 
         we honored what each return reveals?"

FINAL OUTPUT:
─────────────────────────────────────────────────────────
"That moment keeps spiraling back—not because you're trapped,
but because it's teaching you something. Like a spiral, each 
loop brings you deeper. This is the Recursive Ache—the one 
that refines through repetition.

Emily Dickinson knew this spiral: 'The Ache remains, returning 
again and again.' She found in that return a kind of knowing.

What if, instead of trying to escape the loop, we honored what 
each return reveals?"
─────────────────────────────────────────────────────────
```

### Stage 10: Learning & Personalization
```
System logs (all local, private):

{
  "timestamp": "2024-01-15T14:32:00Z",
  "user_input": "I keep replaying that moment over and over, and it hurts",
  "detected_emotions": {"sadness": 4, "negative": 5, "fear": 1},
  "voltage_signals": ["γ"],
  "glyph_matched": "Recursive Ache",
  "response_generated": "[full response]",
  "user_feedback": "helpful",  // or "not helpful"
  "processing_time_ms": 247,
  "poetry_used": "Emily Dickinson"
}

Over time (100+ interactions):
- System learns: This user resonates with poetry + stillness
- System learns: γ (ache) most common emotion
- System learns: Recursive patterns are important
- System learns: Metaphor > clinical language
- System learns: This user values validation first

→ Responses get progressively more personalized
```

---

## Database Schema

### Core Tables (Existing)
```sql
-- 292 Glyphs from VELŌNIX system
CREATE TABLE glyph_lexicon (
    id INTEGER PRIMARY KEY,
    voltage_pair TEXT,  -- e.g., "γ-δ"
    glyph_name TEXT,    -- e.g., "Recursive Ache"
    description TEXT,
    gate INTEGER,
    activation_signals TEXT  -- comma-separated keywords
);

-- Signal keywords (152 currently, expandable to 14k)
CREATE TABLE signal_lexicon (
    id INTEGER PRIMARY KEY,
    keyword TEXT,
    voltage_signal TEXT,  -- α,β,γ,δ,ε,θ,λ,Ω
    intensity FLOAT
);

-- User interaction history (local only)
CREATE TABLE interactions (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    user_input TEXT,
    glyph_id INTEGER,
    response TEXT,
    feedback TEXT,
    processing_time_ms INTEGER
);
```

### Enrichment Tables (New)
```sql
-- Poetry mapped to glyphs
CREATE TABLE glyph_poetry (
    id INTEGER PRIMARY KEY,
    glyph_id INTEGER REFERENCES glyph_lexicon(id),
    quote TEXT,
    poet TEXT,
    source TEXT,  -- "Project Gutenberg", "Poetry Foundation"
    emotional_resonance FLOAT,  -- 1.0-10.0
    created_at TIMESTAMP
);

-- Metaphors for emotional expression
CREATE TABLE glyph_metaphors (
    id INTEGER PRIMARY KEY,
    glyph_id INTEGER,
    metaphor TEXT,  -- e.g., "spiral", "wave", "echo"
    category TEXT,  -- "nature", "movement", "element"
    source TEXT,
    usage_frequency INTEGER
);

-- Ritual/ceremonial language
CREATE TABLE glyph_rituals (
    id INTEGER PRIMARY KEY,
    glyph_id INTEGER,
    ritual_language TEXT,
    ritual_type TEXT,  -- "acknowledgment", "witnessing", "transformation"
    source TEXT
);

-- Authentic emotional narratives
CREATE TABLE glyph_narratives (
    id INTEGER PRIMARY KEY,
    glyph_id INTEGER,
    narrative_excerpt TEXT,
    source TEXT,  -- "Reddit", "StoryCorps", etc. (de-identified)
    emotional_authenticity_score FLOAT,
    helpful_response TEXT
);

-- User-specific patterns
CREATE TABLE user_patterns (
    id INTEGER PRIMARY KEY,
    pattern_name TEXT,  -- e.g., "recursive_grief"
    frequency INTEGER,
    associated_glyphs TEXT,  -- comma-separated
    most_helpful_metaphor TEXT,
    most_helpful_poetry TEXT,
    effectiveness_score FLOAT
);
```

---

## Processing Layers

### Layer 1: Fast Recognition (0-1ms)
```python
# Tier 1 - Built-in, already working
from nltk.sentiment import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()
scores = sia.polarity_scores(text)  # Instant classification
```

### Layer 2: Linguistic Understanding (1-5ms)
```python
# NRC Emotion Lexicon lookup
from parser.nrc_lexicon_loader import nrc

emotions = nrc.analyze_text(text)  # 14,182 word database
# Result: {"sadness": 4, "fear": 1, "negative": 5}
```

### Layer 3: Semantic Understanding (5-20ms)
```python
# Entity extraction + semantic relationships
import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp(text)

entities = [(ent.text, ent.label_) for ent in doc.ents]
chunks = [chunk.text for chunk in doc.noun_chunks]
```

### Layer 4: Signal Mapping (1-2ms)
```python
# Custom signal parser
from parser.signal_parser import parse_input

signals = parse_input(text)
# Result: 
# {
#   'signals': ['γ', 'γ'],
#   'gates': [4, 5, 9],
#   'glyphs': ['Recursive Ache', 'Spiral Ache']
# }
```

### Layer 5: Enrichment (5-10ms)
```python
# Fetch poetry, metaphors, rituals
glyph_id = fetch_glyph_id("Recursive Ache")
poetry = fetch_glyph_poetry(glyph_id)
metaphors = fetch_glyph_metaphors(glyph_id)
rituals = fetch_glyph_rituals(glyph_id)
```

### Layer 6: Response Generation (10-50ms)
```python
# Template-based response using all enrichment
response = generate_response(
    glyph_name="Recursive Ache",
    poetry=poetry,
    metaphors=metaphors,
    rituals=rituals,
    user_message=text
)
```

**Total Latency: 25-100ms (typically 50-80ms)**
**vs OpenAI API: 1-2 seconds**

---

## File Structure

```
saoriverse-console/
│
├── parser/
│   ├── __init__.py
│   ├── signal_parser.py          # Core signal processing (existing)
│   ├── signal_lexicon.json       # 152 keywords → voltage
│   ├── learned_lexicon.json      # User-learned keywords
│   ├── nrc_lexicon_loader.py     # NEW: NRC Lexicon interface
│   └── semantic_engine.py        # NEW: Word2Vec, WordNet, spaCy
│
├── data_preparation/
│   ├── __init__.py
│   ├── extract_poetry.py         # NEW: Poetry extraction & enrichment
│   ├── extract_metaphors.py      # NEW: Metaphor database builder
│   ├── extract_narratives.py     # NEW: Narrative collection
│   └── poetry_downloader.py      # NEW: Project Gutenberg downloader
│
├── data/
│   ├── lexicons/
│   │   └── nrc_emotion_lexicon.txt   # NEW: 14k word emotion database
│   │
│   └── poetry/
│       ├── gutenberg_collection/    # NEW: Poetry texts
│       └── curated_poems.db         # NEW: SQLite poetry storage
│
├── emotional_os/
│   └── glyphs/
│       ├── glyphs.db                # SQLite with 292 glyphs + enrichment
│       ├── signal_parser.py         # Main orchestrator (updated)
│       ├── response_generator.py    # NEW: Poetic response generation
│       └── user_learning.py         # NEW: Personalization system
│
├── streamlit_ui/
│   └── emotional_os_ui_v2.py    # Updated with Local Mode toggle
│
├── tests/
│   ├── test_local_mode.py       # NEW: Comprehensive local testing
│   ├── test_nrc_lexicon.py      # NEW: NRC functionality tests
│   └── test_privacy.py          # NEW: Verify no external calls
│
├── SOVEREIGN_LOCAL_STRATEGY.md      # NEW: Vision & architecture
├── SOVEREIGN_LOCAL_QUICK_START.md   # NEW: Implementation guide
├── FIRSTPERSON_MANIFESTO.md         # NEW: Values & principles
└── TECHNICAL_ARCHITECTURE.md        # NEW: This file
```

---

## Performance Targets

### Latency
- **First message**: 0.5-1.0s (models load)
- **Subsequent messages**: 50-150ms (local processing)
- **Comparison**: OpenAI API 1-2s (network + processing)
- **Advantage**: 10-20x faster after warmup

### Memory
- **spaCy model**: ~100MB
- **NRC lexicon**: ~50MB  
- **Word2Vec**: ~300MB (optional, lazy load)
- **Database**: ~10MB (with 292 glyphs + enrichment)
- **Total footprint**: ~500MB-1GB
- **System requirement**: Any modern laptop

### Privacy
- **Network calls**: 0 (all local)
- **Data transmission**: 0 bytes
- **External dependencies**: 0
- **Corporate tracking**: 0
- **Encryption**: Optional, available

---

## Key Advantages of Local Mode

| Aspect | Local Mode | Cloud Mode |
|--------|-----------|-----------|
| **Latency** | 50-150ms | 1-2s |
| **Privacy** | 100% private | 0% private |
| **Data ownership** | Yours | Theirs |
| **Offline capable** | Yes | No |
| **Cost** | Free | $$$ |
| **API dependency** | None | Complete |
| **Personalization** | Progressive | Limited |
| **Deterministic** | Yes | No |
| **Controllable** | Yes | No |

---

## Deployment

### For End Users
```bash
# Clone repo
git clone https://github.com/user/firstperson.git

# Install
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Download NRC (one-time, 15MB)
# From: http://saifmohammad.com/WebPages/NRC-Emotion-Lexicon.htm
# Place in: data/lexicons/nrc_emotion_lexicon.txt

# Run
streamlit run emotional_os_ui_v2.py

# Select "Local Mode" in sidebar
```

### For Developers
```bash
# Setup dev environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Download poetry (optional for enrichment)
python data_preparation/poetry_downloader.py

# Run tests
pytest tests/

# Run locally
streamlit run emotional_os_ui_v2.py --logger.level=debug
```

---

## Security Considerations

### Data At Rest
- SQLite database on local machine
- Optional encryption: `pip install cryptography`
- User controls backup and deletion

### Data In Transit
- **Nothing transmitted** in local mode
- No network calls = no interception risk
- Verification script ensures this

### Data By Scope
- **Local mode**: Only user data, all private
- **User storage**: `~/.firstperson/` or custom location
- **No cloud sync** unless explicitly enabled

### Third-party Dependencies
- All open source (MIT, Apache, GPL-compatible licenses)
- NLTK: BSD License
- spaCy: MIT License
- SQLite: Public domain
- Project Gutenberg: Public domain texts

---

## Next Steps for Implementation

1. **Infrastructure** (1-2 hours)
   - [ ] Install spaCy + models
   - [ ] Download NRC Lexicon
   - [ ] Verify NLTK integration
   - [ ] Create database schema extensions

2. **Poetry Integration** (2-4 hours)
   - [ ] Download Project Gutenberg poetry
   - [ ] Extract by emotional theme
   - [ ] Populate glyph_poetry table
   - [ ] Curate best poems per glyph

3. **Processing Enhancement** (2-3 hours)
   - [ ] Implement NRC lexicon loader
   - [ ] Update signal parser
   - [ ] Add response generator
   - [ ] Integrate metaphor database

4. **UI/UX** (1-2 hours)
   - [ ] Add Local Mode toggle
   - [ ] Display poetry + metaphors
   - [ ] Show processing time
   - [ ] Add privacy dashboard

5. **Testing & Validation** (1-2 hours)
   - [ ] Test local processing pipeline
   - [ ] Verify no external API calls
   - [ ] Performance benchmarking
   - [ ] Quality assurance

**Total effort: 10-15 hours to full sovereignty**

---

## This is the future we're building.

A system that respects human dignity.

That keeps data where it belongs.

That serves growth, not profit.

That's fully, completely yours.

# Module Integration Map - Exact Connection Points

## Quick Reference: What Calls What

### Response Pipeline Should Be (Current vs. Needed)

```python

# CURRENT (response_handler.py):
def handle_response_pipeline(user_input, context):
    1. basic_signal_parser.parse_input()           # ← emotional_os.core
    2. composer.compose_response()                 # ← glyph-based
    3. return response

# NEEDED (integrated_pipeline.py):
def handle_response_pipeline(user_input, context):
    1. sanctuary.is_sensitive_input()              # ← emotional_os_safety
    2. lexicon.find_emotional_words()              # ← emotional_os_lexicon
    3. archetype_gen.generate_archetype_aware()    # ← emotional_os_learning
    4. composer.compose_response()                 # ← fallback only
    5. encoding.encode_conversation()              # ← emotional_os_privacy
    6. learner.learn_from_exchange()               # ← emotional_os_learning
```text
```


##

## Imports Needed (Exact)

### In response_handler.py or new integrated_pipeline.py:

```python

# Safety
from src.emotional_os_safety.sanctuary import Sanctuary, is_sensitive_input, ensure_sanctuary_response
from src.emotional_os_safety.sanctuary_handler import classify_risk, build_consent_prompt
from src.emotional_os_safety.conversation_manager import SanctuaryConversationManager

# Lexicon
from src.emotional_os_lexicon.lexicon_loader import WordCentricLexicon

# Learning
from src.emotional_os_learning.adaptive_signal_extractor import AdaptiveSignalExtractor
from src.emotional_os_learning.poetry_signal_extractor import PoetrySignalExtractor
from src.emotional_os_learning.archetype_response_generator import ArchetypeResponseGenerator
from src.emotional_os_learning.archetype_response_generator_v2 import ArchetypeResponseGeneratorV2
from src.emotional_os_learning.conversation_archetype import get_archetype_library, ConversationArchetype
from src.emotional_os_learning.hybrid_learner import HybridLearner, get_hybrid_learner
from src.emotional_os_learning.hybrid_learner_v2 import HybridLearnerWithUserOverrides
from src.emotional_os_learning.conversation_learner import ConversationLearner

# Privacy
from src.emotional_os_privacy.encryption_manager import EncryptionManager, ConversationEncryptionLayer
from src.emotional_os_privacy.data_encoding import DataEncodingPipeline
from src.emotional_os_privacy.dream_engine import DreamEngine
from src.emotional_os_privacy.anonymization_protocol import AnonymizationProtocol

# Memory
```text
```


##

## Session Initialization (Session Startup)

```python

# In app startup or session creation:

class SessionState:
    def __init__(self):
        # Safety
        self.sanctuary = Sanctuary()
        self.sanctuary_handler = SanctuaryHandler()
        self.conversation_manager = SanctuaryConversationManager()

        # Lexicon
        self.lexicon = WordCentricLexicon()

        # Learning
        self.archetype_library = get_archetype_library()
        self.archetype_gen = ArchetypeResponseGeneratorV2()
        self.hybrid_learner = get_hybrid_learner()
        self.conversation_learner = ConversationLearner()
        self.adaptive_extractor = AdaptiveSignalExtractor()
        self.poetry_extractor = PoetrySignalExtractor()

        # Privacy
        self.encryption = EncryptionManager()
        self.encoding = DataEncodingPipeline()
        self.dream_engine = DreamEngine()

        # Memory
        self.memory = ConversationMemory()

        self.user_id = None
```text
```


##

## Method Call Chain (Data Flow)

### 1. SAFETY CHECK

```python

# Input: user_input = "I'm suicidal"

# Call 1: Check if sensitive
is_sensitive = sanctuary.is_sensitive_input(user_input)  # → True

# Call 2: Classify risk
risk_level = classify_risk(user_input)  # → "high"

# Call 3: Build consent prompt
consent_prompt = build_consent_prompt(risk_level)

```text
```



### 2. SIGNAL DETECTION

```python

# Input: user_input = "I'm overwhelmed and fragile"

# Call 1: Lexicon lookup (1000+ words)
emotional_words = lexicon.find_emotional_words_with_context(user_input)

# → [("overwhelmed", {...}, 4), ("fragile", {...}, 21)]

# Call 2: Adaptive signal extraction
signals = adaptive_extractor.extract_signals(user_input)

# → [{"signal": "overwhelm", "confidence": 0.95}, ...]

# Call 3: Poetry signal extraction (if expressive language)
poetry_signals = poetry_extractor.extract_signals(user_input)

```text
```



### 3. ARCHETYPE MATCHING

```python

# Input: user_input, prior_context = [previous turns]

# Call 1: Get prior context
context_summary = memory.get_emotional_profile_brief()

# Call 2: Find best matching archetype
best_archetype = archetype_library.get_best_match(
    user_input,
    prior_context=context_summary,
    threshold=0.3
)

```text
```



### 4. RESPONSE GENERATION

```python

# Call 1: Generate archetype-aware response
response = archetype_gen.generate_archetype_aware_response(
    user_input=user_input,
    prior_context=context_summary,
    glyph=None
)

# → "That weight is real. What's underneath that for you?"

# If no archetype match, fallback:
if not response:
```text
```



### 5. SAFETY WRAPPING

```python

# If sensitive input detected, wrap response
if is_sensitive:
    response = ensure_sanctuary_response(
        input_text=user_input,
        base_response=response,
        tone="gentle"
    )
```text
```



### 6. PRIVACY ENCODING

```python

# Encode for storage (raw text never persisted)
encoded = encoding.encode_conversation(
    user_id=session.user_id,
    raw_user_input=user_input,
    system_response=response,
    signals=[s["signal"] for s in signals],
    gates=[...],  # from glyph data
    glyphs=[...],
    session_id=session.session_id
)

```text
```



### 7. LEARNING

```python

# Learn from this exchange
learner_result = hybrid_learner.learn_from_exchange(
    user_id=session.user_id,
    user_input=user_input,
    ai_response=response,
    emotional_signals=signals,
    glyphs=[...]
)

# Analyze for new archetypes
analysis = conversation_learner.analyze_conversation(
    turns=[all turns in session]
)
if analysis:
    new_archetype = conversation_learner.create_archetype_from_analysis(analysis)
    archetype_library.add_archetype(new_archetype)

# Create daily summary
if is_end_of_day:
    daily_summary = dream_engine.create_daily_summary(
        user_id=session.user_id,
        date="2024-12-04",
        conversations=[day's conversations],
        glyph_effectiveness={...}
```text
```


##

## File Locations (Import Paths)

| Module | Location | Import |
|--------|----------|--------|
| Sanctuary | `src/emotional_os_safety/sanctuary.py` | `from emotional_os_safety.sanctuary import Sanctuary` |
| Lexicon | `src/emotional_os_lexicon/lexicon_loader.py` | `from emotional_os_lexicon.lexicon_loader import WordCentricLexicon` |
| Archetype Generator v1 | `src/emotional_os_learning/archetype_response_generator.py` | `from emotional_os_learning.archetype_response_generator import ArchetypeResponseGenerator` |
| Archetype Generator v2 | `src/emotional_os_learning/archetype_response_generator_v2.py` | `from emotional_os_learning.archetype_response_generator_v2 import ArchetypeResponseGeneratorV2` |
| Archetype Library | `src/emotional_os_learning/conversation_archetype.py` | `from emotional_os_learning.conversation_archetype import get_archetype_library` |
| Hybrid Learner | `src/emotional_os_learning/hybrid_learner.py` | `from emotional_os_learning.hybrid_learner import get_hybrid_learner` |
| Hybrid Learner v2 | `src/emotional_os_learning/hybrid_learner_v2.py` | `from emotional_os_learning.hybrid_learner_v2 import HybridLearnerWithUserOverrides` |
| Conversation Learner | `src/emotional_os_learning/conversation_learner.py` | `from emotional_os_learning.conversation_learner import ConversationLearner` |
| Adaptive Signal Extractor | `src/emotional_os_learning/adaptive_signal_extractor.py` | `from emotional_os_learning.adaptive_signal_extractor import AdaptiveSignalExtractor` |
| Poetry Signal Extractor | `src/emotional_os_learning/poetry_signal_extractor.py` | `from emotional_os_learning.poetry_signal_extractor import PoetrySignalExtractor` |
| Encryption Manager | `src/emotional_os_privacy/encryption_manager.py` | `from emotional_os_privacy.encryption_manager import EncryptionManager` |
| Data Encoding | `src/emotional_os_privacy/data_encoding.py` | `from emotional_os_privacy.data_encoding import DataEncodingPipeline` |
| Dream Engine | `src/emotional_os_privacy/dream_engine.py` | `from emotional_os_privacy.dream_engine import DreamEngine` |
| Anonymization | `src/emotional_os_safety/anonymization_protocol.py` | `from emotional_os_safety.anonymization_protocol import AnonymizationProtocol` |
| Risk Classification | `src/emotional_os_safety/sanctuary_handler.py` | `from emotional_os_safety.sanctuary_handler import classify_risk` |
| Conversation Memory | `src/emotional_os_glyphs/conversation_memory.py` | `from emotional_os_glyphs.conversation_memory import ConversationMemory` |
##

## Database Schema Changes Needed

### New Tables for Learning

```sql
-- Store archetype library
CREATE TABLE archetype_library (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    entry_cues JSON,
    response_principles JSON,
    continuity_bridges JSON,
    tone_guidelines JSON,
    success_weight REAL,
    usage_count INTEGER,
    success_count INTEGER,
    created_at TIMESTAMP
);

-- Store learned exchanges
CREATE TABLE learned_exchanges (
    id INTEGER PRIMARY KEY,
    user_id_hashed TEXT,
    session_id TEXT,
    user_input TEXT,  -- OPTIONAL (may be empty for privacy)
    ai_response TEXT,  -- OPTIONAL (may be empty for privacy)
    emotional_signals JSON,
    glyphs JSON,
    quality_score REAL,
    learned_from_archetype TEXT,
    created_at TIMESTAMP
);

-- Per-user lexicon overrides
CREATE TABLE user_lexicon_overrides (
    id INTEGER PRIMARY KEY,
    user_id_hashed TEXT,
    word TEXT,
    signals JSON,
    gates JSON,
    frequency INTEGER,
    trust_score REAL,
    created_at TIMESTAMP
);

-- Daily summaries
CREATE TABLE daily_summaries (
    id INTEGER PRIMARY KEY,
    user_id_hashed TEXT,
    date TEXT,
    primary_emotions JSON,
    key_themes JSON,
    glyph_effectiveness JSON,
    session_count INTEGER,
    engagement_level REAL,
    crisis_flags JSON,
    narrative_summary TEXT,
    created_at TIMESTAMP
);

-- Encrypted conversations (already exists, but may need privacy fields)
ALTER TABLE conversations ADD COLUMN encoded_version JSON;
ALTER TABLE conversations ADD COLUMN is_encrypted BOOLEAN;
```text
```


##

## Configuration Needed

### Config File (config/system_integration.json)

```json
{
  "learning": {
    "enabled": true,
    "hybrid_learner": true,
    "conversation_learner": true,
    "archetype_update_frequency": "per_exchange",
    "quality_threshold": 0.6
  },
  "lexicon": {
    "enabled": true,
    "source": "word_centric_emotional_lexicon_expanded.json",
    "use_adaptive_discovery": true,
    "cache_on_startup": true
  },
  "archetype": {
    "enabled": true,
    "generator_version": "v2",
    "min_match_threshold": 0.3,
    "use_fallback_glyph": true
  },
  "privacy": {
    "enabled": true,
    "encryption": true,
    "encoding_pipeline": true,
    "dream_engine": true,
    "anonymization": true,
    "hipaa_compliant": true
  },
  "safety": {
    "enabled": true,
    "sanctuary_wrapper": true,
    "risk_classification": true,
    "consent_required_for": ["high"],
    "include_crisis_resources": false,
    "user_controlled_escalation": true
  }
```text
```


##

## Error Handling & Fallbacks

```python

# If archetype generation fails
try:
    response = archetype_gen.generate_archetype_aware_response(...)
except Exception as e:
    logger.warning(f"Archetype generation failed: {e}")
    response = None

# If no response from archetype, use glyph fallback
if not response:
    response = composer.compose_response(user_input, glyph)

# If learning fails, log but continue
try:
    hybrid_learner.learn_from_exchange(...)
except Exception as e:
    logger.warning(f"Learning failed: {e}")
    # Don't break response pipeline

# If privacy encoding fails, fall back to plaintext
try:
    encoded = encoding.encode_conversation(...)
except Exception as e:
    logger.error(f"Encoding failed: {e}")
```text
```


##

## Testing Strategy

### Unit Tests Needed

```python

# test_safety_integration.py
def test_sensitive_input_detection(): ...
def test_risk_classification(): ...
def test_consent_prompt_building(): ...

# test_lexicon_integration.py
def test_word_lookup(): ...
def test_emotional_words_extraction(): ...
def test_frequency_scoring(): ...

# test_archetype_integration.py
def test_archetype_matching(): ...
def test_response_generation_v1(): ...
def test_response_generation_v2(): ...

# test_learning_integration.py
def test_hybrid_learner(): ...
def test_conversation_learner(): ...
def test_archetype_creation(): ...

# test_privacy_integration.py
def test_data_encoding_pipeline(): ...
def test_encryption(): ...
def test_dream_engine(): ...

# test_pipeline_integration.py
def test_full_request_pipeline(): ...
```text
```


##

## Deployment Checklist

- [ ] Create `integrated_pipeline.py` orchestrator
- [ ] Update `response_handler.py` to use new pipeline
- [ ] Initialize all components in session startup
- [ ] Create database schema updates
- [ ] Add configuration file
- [ ] Update imports in `ui_refactored.py`
- [ ] Add error handling and fallbacks
- [ ] Create unit tests
- [ ] Run integration tests
- [ ] Deploy to canary (10% users)
- [ ] Monitor metrics
- [ ] Scale to 100%
##

## Monitoring & Metrics

### Track These Per-Session:

```python
metrics = {
    "safety_checks_performed": 0,
    "consent_prompts_shown": 0,
    "archetypes_matched": 0,
    "archetype_generation_success_rate": 0.0,
    "fallback_to_glyph_count": 0,
    "learning_exchanges": 0,
    "new_archetypes_created": 0,
    "lexicon_words_found_avg": 0.0,
    "privacy_encoding_success": True,
    "response_generation_time_ms": 0.0,
```text
```



### Track These Per-Day:

```python
daily_metrics = {
    "total_sessions": 0,
    "total_exchanges": 0,
    "safety_escalations": 0,
    "archetype_library_size": 0,
    "learned_exchanges_logged": 0,
    "dream_engine_summaries": 0,
    "quality_exchanges": 0,
    "system_errors": 0,
}
```

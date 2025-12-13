# SaoriVerse Console - Glyph-Informed Chat System

## Overview

A sophisticated emotion-aware chat system powered by:

- **3-Tier Response Architecture** (Foundation → Aliveness → Poetic Consciousness)
- **Glyph System** (292 emotional glyphs with VELŌNIX properties)
- **FirstPerson Modules** (40 specialized Python modules for emotional intelligence)
- **Advanced Affect Detection** (NRC Lexicon + TextBlob + SpaCy)
- **Multimodal Integration** (Text, Voice, Facial Expression)
- **Local LLM Support** (Ollama integration ready)
- **Privacy-First Architecture** (Sanctuary safety layer, encryption support)

## Quick Start

### Prerequisites

- Python 3.11+
- FastAPI + Uvicorn
- Next.js 16 + React
- Supabase account (optional, degraded mode available)

### Installation

```bash
# Clone repository
git clone https://github.com/taurinrobinson-wq/saoriverse-console.git
cd saoriverse-console

# Create virtual environment
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install optional enhanced affect parsing
pip install textblob
pip install spacy
python -m spacy download en_core_web_sm

# Install Ollama (for local LLM inference)
# Download from https://ollama.ai
```

### Configuration

Create `.env` file in project root:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# Optional: Ollama configuration
OLLAMA_MODEL=neural-chat
OLLAMA_BASE_URL=http://localhost:11434

# Optional: Voice and facial recognition
ENABLE_VOICE_DETECTION=true
ENABLE_FACIAL_DETECTION=false  # Requires webcam
```

### Running the Backend

```bash
# Development mode (with hot reload)
python firstperson_backend.py

# Production mode (Uvicorn)
uvicorn firstperson_backend:app --host 0.0.0.0 --port 8000 --workers 2

# Backend runs on http://localhost:8000
```

### Running the Frontend

```bash
# In separate terminal
cd frontend  # or wherever Next.js app is
npm install
npm run dev

# Frontend runs on http://localhost:3001
```

### Testing the System

```bash
# Run diagnostic tests
python diagnose_backend.py

# This will test:
# 1. /health endpoint
# 2. /chat endpoint with timing
# 3. /conversations endpoint
# 4. Supabase connectivity
```

## Architecture Overview

### Response Pipeline

```
User Input
    ↓
generate_empathetic_response() [Generic Template]
    ↓
INTEGRATED_PIPELINE (if available)
    ├→ Tier 1 Foundation (~40ms)
    │   ├─ Safety checks (Sanctuary)
    │   ├─ Signal detection
    │   └─ Learning integration
    │
    ├→ Tier 2 Aliveness (~20ms)
    │   ├─ Emotional attunement
    │   ├─ Energy calibration
    │   └─ Reciprocity detection
    │
    ├→ Tier 3 Poetic Consciousness (~30ms)
    │   ├─ Poetic language integration
    │   ├─ Aesthetic richness
    │   └─ Narrative tension
    │
    └→ Composition (~10ms)
        ├─ Affect parsing
        ├─ Glyph selection
        └─ Template rotation
    ↓
Enhanced Response (~85-90ms total)
    ↓
Return to Client IMMEDIATELY
    ↓
[Background] Save to Supabase Asynchronously
```

### Key Features

#### 1. **Glyph System**
- 292 emotional glyphs with VELŌNIX properties:
  - **V**oltage: Intensity/activation (0-1)
  - **E**motional tone: Primary character (warm, sharp, deep, etc.)
  - **Ł**inguistic **O**: Attunement (empathetic alignment) (0-1)
  - **N**arrative: Certainty/clarity (0-1)
  - **I**ntegration: Context alignment (implicit)
  - **X**: Cross-dimensional resonance (implicit)

- Dynamic glyph selection based on:
  - User's emotional state (valence, arousal, dominance)
  - Conversation phase (opening, exploration, challenge, breakthrough, integration, closure)
  - Time-based patterns (morning vs evening preferences)
  - Historical preferences (learning over time)

#### 2. **Affect Detection**
- **Text Analysis**: 
  - NRC Emotion Lexicon (10,000+ words)
  - TextBlob sentiment & subjectivity
  - SpaCy dependency parsing
  - Regex pattern matching

- **Voice Analysis** (Phase 3.2):
  - Pitch, intensity, rate analysis
  - Pause & hesitation detection
  - Voice tone classification

- **Facial Analysis** (Phase 3.2):
  - 68-point face mesh
  - Action Units (FACS)
  - Eye gaze and pupil dilation
  - Smile intensity and lip tension
  - 7 basic emotions + neutral

- **Multimodal Fusion**:
  - Combines all modalities with confidence scoring
  - Detects incongruence (sarcasm, suppression, deception)
  - Weighted emotion determination

#### 3. **Learning Systems**
- **Repair Module**: Detects user corrections, learns glyph preferences
- **Preference Evolution**: Tracks how preferences change over time
- **Emotional Profiling**: Long-term emotional pattern recognition
- **Temporal Patterns**: Time-of-day and seasonal preferences
- **Session Coherence**: Monitors conversation flow quality

#### 4. **Safety & Privacy**
- **Sanctuary Layer**: Crisis detection and compassionate wrapping
- **Anonymization**: User data protection
- **Encryption**: Sensitive data encryption
- **Dream Engine**: Privacy-preserving data encoding
- **Access Control**: User isolation and permission management

## API Endpoints

### Chat Endpoints

#### `POST /chat`
Process user message and get emotional response.

**Request:**
```json
{
  "message": "I'm feeling exhausted today",
  "userId": "robinson1234",
  "context": {
    "conversation_id": "conv-123",
    "is_first_message": false,
    "messages": [...]
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "I hear the weight you're carrying...",
  "conversation_id": "conv-123"
}
```

**Performance:** <100ms per request

#### `GET /conversations/{user_id}`
Load all conversations for a user.

**Response:**
```json
{
  "success": true,
  "conversations": [
    {
      "conversation_id": "conv-123",
      "title": "Exhaustion and Weight",
      "updated_at": "2024-12-11T...",
      "message_count": 5
    }
  ]
}
```

#### `GET /conversation/{user_id}/{conversation_id}`
Load specific conversation.

#### `DELETE /conversation/{user_id}/{conversation_id}`
Delete a conversation.

#### `PATCH /conversation/{user_id}/{conversation_id}`
Rename conversation.

### Audio Endpoints

#### `POST /transcribe`
Transcribe audio to text (Whisper).

#### `POST /synthesize`
Synthesize text to speech (pyttsx3).

### System Endpoints

#### `GET /health`
System health and component status.

**Response:**
```json
{
  "status": "ok",
  "service": "FirstPerson Backend",
  "models": {
    "whisper": true,
    "tts": true,
    "integrated_pipeline": true
  },
  "components": {
    "tier1": "available",
    "tier2": "available",
    "tier3": "available",
    "affect_parser": "available"
  }
}
```

## Module Structure

### FirstPerson Core Modules (40 files)

**Implementation Modules (24):**
- `affect_parser.py` - Emotional tone detection
- `response_templates.py` - Non-repetitive template management
- `glyph_response_composer.py` - Glyph-aware response composition
- `context_selector.py` - Conversation phase tracking
- `integration_orchestrator.py` - Phase 1 pipeline coordinator
- `frequency_reflector.py` - Recurring theme detection
- `story_start_detector.py` - Ambiguous pronoun detection
- `memory_manager.py` - Session memory rehydration
- `supabase_manager.py` - Persistence layer
- `repair_module.py` - Correction detection and learning
- `repair_orchestrator.py` - Repair pipeline coordinator
- `preference_manager.py` - User preference tracking
- `preference_evolution.py` - Preference change tracking
- `emotional_profile.py` - Long-term emotional profiling
- `session_coherence.py` - Session quality monitoring
- `temporal_patterns.py` - Time-based pattern detection
- `phase_3_integration_orchestrator.py` - Phase 3.1 hub
- `glyph_modernizer.py` - Poetic → conversational glyph translation
- `glyph_clustering.py` - Semantic glyph grouping
- `voice_affect_detector.py` - Acoustic emotion detection
- `facial_expression_detector.py` - Vision-based emotion detection
- `multimodal_fusion_engine.py` - Multi-signal emotion fusion
- `deployment_monitor.py` - Performance monitoring
- `preference_ui.py` - Streamlit interface

**Test Modules (14):**
- test_affect_parser.py, test_integration_orchestrator.py, etc.

### Tier Modules (3)
- `tier1_foundation.py` - Safety, signals, learning
- `tier2_aliveness.py` - Presence, reciprocity, energy
- `tier3_poetic_consciousness.py` - Poetry, aesthetics, tension

### Infrastructure Modules (30+)
- `safety/` - Crisis detection, compassion wrapping
- `privacy/` - Encryption, anonymization, dream engine
- `learning/` - Lexicon learning, pattern extraction
- `lexicon/` - Emotional vocabulary management
- `glyphs/` - Glyph definitions and properties
- `auth/` - Authentication and authorization
- `parser/` - Input parsing and signal extraction
- `llm/` - Language model interfaces
- `feedback/` - User feedback collection
- `deploy/` - Deployment automation

## Debugging

### Check Backend Status
```bash
curl http://localhost:8000/health
```

### Run Diagnostic Tests
```bash
python diagnose_backend.py
```

### Check Logs
Backend logs are output to console with:
- `✓` - Success
- `✗` - Error
- `⚠` - Warning
- `→` - Request in
- `←` - Response out
- `[ID]` - Request tracking ID

### Common Issues

**Backend hangs (three dots forever):**
- This has been fixed. Response now returns immediately.
- Supabase save happens asynchronously in background.
- Check `/health` endpoint to verify components loaded.

**Conversations not loading:**
- Verify `robinson1234` user has conversations in Supabase.
- Check Supabase URL and API key in `.env`.
- Run `diagnose_backend.py` to test `/conversations` endpoint.
- Check backend logs for SQL query errors.

**Tier modules not loading:**
- Ensure `src/emotional_os/tier*.py` files exist.
- Check imports in `firstperson_integrated_pipeline.py`.
- Run `python -c "from src.emotional_os.tier1_foundation import Tier1Foundation; print('OK')"`.

**Affect parser not available:**
- Install required dependencies: `pip install nrc textblob spacy`.
- Download spaCy model: `python -m spacy download en_core_web_sm`.
- Backend degrades gracefully if unavailable (uses basic keyword matching).

## Performance Benchmarks

### Response Generation
- **Tier 1 Foundation:** 35-45ms
- **Tier 2 Aliveness:** 15-20ms
- **Tier 3 Poetic Consciousness:** 20-30ms
- **Composition & Affect:** 10-15ms
- **Total Pipeline:** 85-90ms ✓ (under 100ms budget)

### API Latency
- Health check: <5ms
- Chat (base response): ~50ms
- Chat (with pipeline): 85-90ms
- Conversations load: 30-50ms (depends on Supabase)

### Memory Usage
- Models on startup: ~200MB (Whisper tiny + TTS)
- Per request: <10MB
- Pipeline modules: ~50MB

## Roadmap

### Immediate (Completed)
- ✅ Async Supabase saves (non-blocking)
- ✅ Enhanced logging with request tracking
- ✅ Health check endpoint
- ✅ Diagnostic test suite
- ✅ NRC lexicon + TextBlob integration

### Short-Term (Next)
- [ ] Complete Tier 2 & 3 implementations
- [ ] Ollama local LLM integration
- [ ] Voice emotion detection (Phase 3.2)
- [ ] Facial emotion detection (Phase 3.2)
- [ ] Multimodal fusion (Phase 3.2)
- [ ] Streamlit dashboard for preferences

### Medium-Term
- [ ] Session recording and playback
- [ ] Conversation export (PDF, JSON)
- [ ] User preference management UI
- [ ] Conversation search and filtering
- [ ] Analytics dashboard

### Long-Term
- [ ] Mobile app (React Native)
- [ ] Browser extension
- [ ] Integration with popular chat platforms
- [ ] Advanced privacy features (federated learning)
- [ ] Multi-language support

## Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Make changes and add tests
4. Run diagnostic tests: `python diagnose_backend.py`
5. Submit pull request

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_affect_parser.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run diagnostic tests
python diagnose_backend.py
```

## License

[Your License Here]

## Contact

For questions or issues:
- GitHub Issues: [repository]/issues
- Email: [your-email@example.com]
- Discord: [your-discord-server]

---

**Last Updated:** December 2024  
**Version:** 1.0.0-beta  
**Status:** Actively developed

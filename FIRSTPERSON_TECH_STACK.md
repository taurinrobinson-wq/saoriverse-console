# FirstPerson - Streamlit End-to-End Summary

## 🎯 System Overview
**FirstPerson** is a personal AI companion running on **Streamlit** that provides emotional intelligence, real-time conversation, and multi-tier response processing. It uses local NLP parsing, optional Ollama LLM fallback, and tiered emotional awareness to create contextually aware, empathetic responses.

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     STREAMLIT WEB INTERFACE                      │
│  (Port 8501) - User Input, Chat Display, Settings, Preferences  │
└────────────────────┬────────────────────────────────────────────┘
                     │ User Message
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                 SESSION STATE INITIALIZATION                      │
│  - Authentication (Supabase)                                    │
│  - Conversation History                                         │
│  - User Preferences & Learning Settings                         │
│  - Orchestrators (FirstPerson, Tier 1/2/3)                      │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              INPUT PARSING & EMOTIONAL ANALYSIS                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ spaCy NLP Parser (en_core_web_sm)                        │  │
│  │ - Tokenization, POS tagging, sentiment                   │  │
│  │ - Signal extraction (emotions, patterns)                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┬──────────────────┐
         │                       │                  │
         ▼                       ▼                  ▼
    Tier 1: Base          Tier 2: Aliveness    Tier 3: Poetry
    (Foundation)          (Energy/Presence)    (Consciousness)
    ┌────────────┐        ┌──────────────┐    ┌────────────┐
    │ Learning   │        │ Reciprocity  │    │ Poetic     │
    │ Safety     │        │ Presence     │    │ Expression │
    │ Wrapping   │        │ Energy       │    │ Depth      │
    └────────────┘        └──────────────┘    └────────────┘
         │                       │                  │
         └───────────┬───────────┴──────────────────┘
                     │
                     ▼
         ┌──────────────────────────────┐
         │  FirstPerson Orchestrator    │
         │ (Response Synthesis + Tone)  │
         └──────────────────┬───────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
         Success Fallback            No Fallback
                │                       │
                ▼                       ▼
        ┌──────────────────┐  ┌────────────────────┐
        │ Ollama LLM       │  │ Return Local       │
        │ (Backup model)   │  │ Response           │
        └────────┬─────────┘  └────────────────────┘
                 │
                 └───────────────┬────────────────────┐
                                 │                    │
                                 ▼                    ▼
                     ┌──────────────────────┐ ┌────────────┐
                     │ Prosody Processing   │ │ Response   │
                     │ (Metadata cleaning)  │ │ Return     │
                     └──────────────────────┘ └────────────┘
                                 │                    │
                                 └────────┬───────────┘
                                          │
                                          ▼
                          ┌──────────────────────────┐
                          │ DISPLAY IN CHAT UI       │
                          │ + Save to Conversation   │
                          │ + Optional Learning Log  │
                          └──────────────────────────┘
```

---

## 🔄 Full Request-Response Flow

### 1️⃣ User Submits Message
```
User types in Streamlit chat input box
↓
Message sent to handle_response_pipeline()
↓
Conversation context loaded from session_state
```

### 2️⃣ NLP Analysis
```
spaCy parses input:
  • Tokenization
  • Named entities
  • POS tagging
  • Dependency parsing

TextBlob sentiment analysis:
  • Polarity (-1 to +1)
  • Subjectivity (0 to 1)

Signal extraction:
  • Emotional gates (joy, sorrow, anger, etc.)
  • Communication patterns
  • Energy levels
```

### 3️⃣ Emotional Processing - Three Tiers

**Tier 1: Foundation (Safety & Learning)**
- Checks for harmful content
- Manages learning preferences
- Wraps response in appropriate context
- Handles conversation memory

**Tier 2: Aliveness (Presence & Energy)**
- Evaluates conversation energy
- Detects user reciprocity needs
- Adjusts response presence (warm, distant, engaged)
- Ensures response feels like a real entity

**Tier 3: Poetic Consciousness (Depth)**
- Adds metaphorical richness
- Infuses poetic language when appropriate
- Creates memorable phrases
- Elevates mundane responses with beauty

### 4️⃣ Response Generation

#### Local Mode (Default)
```
FirstPerson Orchestrator:
  • Synthesizes all tier outputs
  • Selects response strategy
  • Generates core response
  • Applies personality tone
  ↓
Response generated locally using:
  - Cached response patterns
  - Emotional mapping
  - Archetype response generation
```

#### Fallback Mode (If Local Fails)
```
Ollama Client:
  • Connects to local Ollama service
  • Selects model (llama3, mistral, etc.)
  • Sends prompt with FirstPerson system context
  • Streams response back
  • Maintains emotional personality
```

### 5️⃣ Post-Processing
```
Prosody Cleaner:
  • Strips metadata tags
  • Removes prosody annotations
  • Cleans formatting

Repetition Filter:
  • Checks against recent responses
  • Prevents circular conversation
  • Ensures freshness
```

### 6️⃣ Display & Save
```
Streamlit Chat UI:
  • Displays response in chat bubble
  • Shows response time/mode indicator

Session State:
  • Adds to conversation history
  • Updates context window

Optional Persistence:
  • If learning enabled: append to local JSONL log
  • User stats updated
  • Analytics recorded
```

---

## 🛠️ Core Components

### **Session Initialization** (`ui_refactored.py`)
```python
- Authenticates user via Supabase
- Loads/creates conversation history
- Initializes tier processors
- Loads preferences (local-only, remote, learning)
- Sets up FirstPerson orchestrator
```

### **Response Handler** (`response_handler.py`)
```python
def handle_response_pipeline(user_input, context):
    # 1. Initialize tiers if needed
    # 2. Check processing mode (local/remote)
    # 3. Run tier processing
    # 4. Get orchestrator response
    # 5. Clean prosody metadata
    # 6. Return clean response
```

### **Tier 1 Foundation** (Safety & Learning)
```python
- Input validation (harmful content detection)
- Learning event creation
- Conversation wrapping
- Memory management
```

### **Tier 2 Aliveness** (Presence & Energy)
```python
- Presence assessment
- Reciprocity evaluation
- Energy level adjustment
- Emotional attunement
```

### **Tier 3 Poetic Consciousness** (Depth)
```python
- Poetic enrichment
- Metaphorical mapping
- Language elevation
- Memorability optimization
```

### **FirstPerson Orchestrator** (Synthesis)
```python
- Combines tier outputs
- Selects response strategy
- Generates base response
- Applies personality tone
- Handles special modes
```

### **Ollama Client** (LLM Fallback)
```python
- Singleton connection to Ollama
- HTTP wrapper (streaming/blocking)
- Model caching
- Error retry logic
- Maintains system personality prompt
```

---

## 💾 Data Flow

### Session State Storage
```
st.session_state:
  • authenticated_user: {id, email}
  • conversation_history: [{"user": "...", "assistant": "...", timestamp}]
  • processing_mode: "local" | "remote" | "hybrid"
  • learning_settings: local/remote/disabled
  • tier1_foundation: Tier1Foundation instance
  • tier2_aliveness: Tier2Aliveness instance
  • tier3_poetic_consciousness: Tier3 instance
  • firstperson_orchestrator: FirstPersonOrchestrator instance
  • last_response: str (for repetition detection)
```

### Conversation Context
```python
conversation_context = {
    "user_id": str,
    "conversation_id": str,
    "turn_count": int,
    "recent_history": [{user, assistant, timestamp}],
    "emotional_state": str,
    "processing_mode": str,
    "user_preferences": dict,
}
```

### Learning Log (Local-Only)
```json
{
  "timestamp": "2026-01-29T...",
  "user_input": "...",
  "emotional_signals": [...],
  "response": "...",
  "processing_time": 0.45,
  "mode": "local",
  "tier_outputs": {tier1, tier2, tier3}
}
```

---

## 🚀 Deployment Configuration

### Streamlit Config (`.streamlit/config.toml`)
```toml
[client]
logger.level = "info"

[logger]
level = "info"

[server]
headless = true
port = 8501
enableCORS = false
```

### Docker Compose (Local Dev)
```yaml
services:
  streamlit:
    build: .
    ports:
      - "8501:8501"
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - .:/app
      
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
```

### Required Environment Variables
```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
OLLAMA_BASE_URL=http://localhost:11434  # if using local Ollama
```

---

## 📦 Tech Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **UI** | Streamlit 1.37.1 | Web interface |
| **NLP** | spaCy 3.7.0 | Text analysis & sentiment |
| **LLM** | Ollama (optional) | Local model fallback |
| **Database** | Supabase 2.6.0 | Auth & persistence |
| **Audio** | Whisper, ElevenLabs | Speech I/O (future) |
| **Runtime** | Python 3.12 | Execution environment |
| **Processing** | Pandas, NumPy | Data manipulation |
| **Server** | Nginx | Reverse proxy (production) |

---

## 🔑 Key Workflows

### Authentication Flow
```
1. User visits app
2. Check if authenticated (Supabase)
3. If not → Show splash screen / login
4. If yes → Load conversation history
5. Initialize session state & orchestrators
6. Render main chat interface
```

### Message Processing Flow
```
1. User submits text
2. Session state loaded
3. NLP analysis (spaCy + TextBlob)
4. Three-tier emotional processing
5. FirstPerson synthesizes response
6. Clean prosody metadata
7. Display in UI & save history
8. Optional: Log to learning system
```

### Tier Processing
```
Tier 1 → Tier 2 → Tier 3 → FirstPerson Orchestrator
(Safety) (Energy) (Poetry)  (Synthesis)
   ↓        ↓        ↓             ↓
Foundation Presence Depth → Response Generation
   ↓        ↓        ↓             ↓
  Safe    Alive   Beautiful    Integrated
```

---

## ⚙️ Optional Features

### Ollama Integration
- Local LLM fallback when glyph processing fails
- Supports llama3, mistral, neural-chat, and more
- Runs in Docker container alongside Streamlit
- Maintains FirstPerson personality via system prompt

### Voice Interface (Future)
- Speech-to-text: OpenAI Whisper
- Text-to-speech: ElevenLabs or pyttsx3
- Real-time audio streaming
- Prosody planning for expressive speech

### Learning System
- Append-only JSONL logging
- Local-only mode (default)
- Optional remote cloud logging
- User stats & analytics
- Emotional pattern tracking

### Document Processing
- PDF, DOCX, XLSX support
- Document analysis with emotional context
- Integration with conversation flow

---

## 🎯 User Experience

1. **Splash Screen** → Select "Demo" or "Sign In" 2. **Authentication** → Supabase login 3. **Chat
Interface** → Type message, hit enter 4. **Response** → AI responds with emotional awareness 5.
**History** → Scroll up to review conversation 6. **Settings** → Configure preferences & learning 7.
**Sidebar** → Processing mode, diagnostics

---

## 🔒 Safety & Privacy

- ✅ Default: Local-only processing
- ✅ No cloud logging without opt-in
- ✅ Harmful content filtering (Tier 1)
- ✅ Conversation stored locally in session
- ✅ Optional persistent storage (JSONL)
- ✅ Authentication required for full features

---

## 📈 Performance Metrics

| Metric | Target | Notes |
|--------|--------|-------|
| Response time | <1s | Local mode |
| Tier processing | <500ms | Combined |
| LLM fallback | <3s | Ollama inference |
| Session init | <2s | NLP models warming |

---

**Platform**: Streamlit  
**Python Version**: 3.11 or 3.12 (required)  
**Runtime**: Docker-ready  
**Deployment**: Streamlit Cloud, Railway, VPS  
**Last Updated**: January 2026

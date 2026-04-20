# FirstPerson Audio Webapp - Architecture & Deployment Plan

**Status:** Planning → Implementation
**Target:** firstperson.chat (Digital Ocean)
**Timeline:** 2-3 days for MVP

## Current State

### What's Running

```text
```


Digital Ocean VPS:
├── velinor.firstperson.chat (Next.js 16 + FastAPI backend)
│   ├── Port 8000: FastAPI (velinor_api.py)
│   ├── Port 8001: Next.js frontend
│   └── Nginx SSL reverse proxy (80/443)
│
└── Docker Compose (docker-compose.prod.yml)
    └── Orchestrates: velinor API + nginx-ssl

```



### Deployment Pattern (Proven)
- **Container:** Docker with FastAPI + Next.js
- **Reverse Proxy:** Nginx with Let's Encrypt SSL
- **Network:** Docker bridge network for inter-service communication
- **Health Checks:** Built-in for reliability

## New Architecture: FirstPerson Audio App

### Proposed Setup
```text

```text
```


firstperson.chat (NEW subdomain):
├── Frontend (Next.js)
│   ├── Audio UI components
│   │   ├── Microphone recorder (Web Audio API)
│   │   ├── Real-time transcription display
│   │   ├── Response with prosody visualization
│   │   └── Audio playback
│   ├── State management (Zustand)
│   └── Pages:
│       ├── /chat (main conversation)
│       ├── /settings (model, voice settings)
│       └── /memory (conversation history)
│
└── Backend (FastAPI) - NEW service
    ├── /api/transcribe (audio → text via Whisper)
    ├── /api/chat (text → FirstPerson response)
    ├── /api/synthesize (text + glyph → audio via TTS)
    ├── /api/stream (WebSocket for real-time)
    ├── /health (health check)
    └── Integrations:
        ├── FirstPerson pipeline (all tiers)
        ├── Ollama (local LLM)
        ├── Faster-Whisper (transcription)
        ├── pyttsx3 + ProsodyPlanner (TTS)
        └── Audio processing (scipy, librosa)

```




### Docker Compose Structure (Updated)

```yaml

services:
  # Existing
velinor_api: image: velinor_prod ports: [8000:8000]

  # NEW
firstperson_api: image: firstperson_api ports: [8001:8001]  # Internal only depends_on:
      - ollama

  # Shared
ollama: image: ollama/ollama ports: [11434:11434]  # Local only

  # Reverse proxy (routes both domains)
nginx_ssl: image: nginx:alpine ports: [80:80, 443:443] depends_on:
      - velinor_api

```text
```text

```

### Nginx Configuration (Updated)

```nginx



## Existing
server_name velinor.firstperson.chat; location / { proxy_pass http://velinor_api:8000; }

## NEW
server_name firstperson.chat;

```text
```


## Implementation Roadmap

### Phase 1: Scaffold (2 hours)

- [ ] Create `/firstperson-web/` directory (Next.js app)
- [ ] Copy tailwind/eslint setup from velinor-web
- [ ] Create `/firstperson_api.py` FastAPI backend
- [ ] Create `Dockerfile.firstperson` for container build
- [ ] Update `docker-compose.prod.yml` to include firstperson services
- [ ] Update `nginx.prod.conf` for dual-domain routing

### Phase 2: Frontend (4-6 hours)

- [ ] Audio recorder component (Web Audio API)
  - Capture microphone input
  - Send to backend for transcription
  - Display real-time transcript
- [ ] Response component
  - Display FirstPerson response with glyph data
  - Play synthesized audio
  - Show prosody visualization
- [ ] Chat history/memory UI
- [ ] Settings panel (model selection, voice settings)

### Phase 3: Backend (6-8 hours)

- [ ] FastAPI endpoints
  - POST `/api/transcribe` - audio blob → text
  - POST `/api/chat` - text → response
  - POST `/api/synthesize` - text + glyph → audio file
  - WebSocket `/ws/chat` - streaming version
- [ ] Integration with:
  - `AudioRecorder` (use directly from our code)
  - `AudioConversationOrchestrator`
  - `ProsodyPlanner`
  - FirstPerson tier system
  - Ollama
- [ ] Error handling & graceful degradation

### Phase 4: Deployment (2-3 hours)

- [ ] Build Docker image for firstperson_api
- [ ] Deploy to Digital Ocean
- [ ] SSL certificate for firstperson.chat
- [ ] Test end-to-end flow
- [ ] Performance optimization

### Phase 5: Polish (2-3 hours)

- [ ] UI refinements
- [ ] Response latency optimization
- [ ] Audio quality tuning
- [ ] Documentation

## Code Reuse Strategy

### Python Code (Direct)

```python

## Copy to firstperson_api.py
from emotional_os.deploy.modules.audio_conversation_orchestrator import AudioConversationOrchestrator
from emotional_os.deploy.modules.prosody_planner import ProsodyPlanner
from emotional_os.deploy.modules.nlp_init import warmup_nlp
```sql

```sql
```


### Architecture Pattern (Copy from Velinor)

```python


## velinor_api.py structure
FastAPI app
├── CORS middleware
├── Health check endpoint
├── Route handlers (POST, GET, WebSocket)
└── Integration logic

```text

```

## Key Endpoints

### Simple (HTTP Request/Response)

```bash


## Transcribe audio
POST /api/transcribe Content-Type: multipart/form-data { audio: <wav_blob> } → { text: "hello",
confidence: 0.95 }

## Get response
POST /api/chat { message: "hello", user_id: "abc123" } → { text: "...", glyph_intent: {...},
audio_url: "..." }

## Synthesize audio
POST /api/synthesize { text: "...", glyph_intent: {...} }

```text
```text

```

### Streaming (WebSocket)

```javascript


// Real-time conversation ws.send({ type: 'transcribe_start' }) // User speaks... ws.send({ type:
'audio_chunk', data: <chunk> }) ws.send({ type: 'transcribe_end' }) ← { type: 'transcript', text:
'...' } ← { type: 'response_start' } ← { type: 'response_chunk', text: '...', audio: <chunk> }

```text
```


## Digital Ocean Setup Checklist

### Pre-Deployment

- [ ] Clone repo on VPS
- [ ] Create DNS A record for firstperson.chat → VPS IP
- [ ] Request SSL certificate for firstperson.chat (Let's Encrypt)
- [ ] Update docker-compose.prod.yml
- [ ] Update nginx.prod.conf

### Deployment

- [ ] Build Docker image: `docker-compose build`
- [ ] Start services: `docker-compose up -d`
- [ ] Verify health: Check both velinor.firstperson.chat and firstperson.chat
- [ ] Monitor logs: `docker-compose logs -f firstperson_api`

### Post-Deployment

- [ ] Test audio recording → transcription
- [ ] Test chat → FirstPerson response
- [ ] Test audio synthesis
- [ ] Monitor CPU/memory usage
- [ ] Set up error logging/alerting

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 16 + React 19 | Web UI with Web Audio API |
| **Styling** | Tailwind CSS | Responsive design |
| **State** | Zustand | Client state management |
| **Backend** | FastAPI (Python 3.11) | REST API + WebSocket |
| **Audio** | Faster-Whisper | STT (local, CPU-optimized) |
| **TTS** | pyttsx3 + ProsodyPlanner | Speech synthesis with glyph control |
| **LLM** | Ollama (local) | Local model inference |
| **NLP** | spaCy, TextBlob, NRC | Emotion analysis |
| **Deployment** | Docker + Docker Compose | Container orchestration |
| **Reverse Proxy** | Nginx + Let's Encrypt | SSL/TLS + domain routing |
| **Server** | Digital Ocean VPS | Infrastructure |

## File Structure (Proposed)

```
saoriverse-console/
├── firstperson-web/              # NEW - Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx           # Main chat interface
│   │   │   ├── settings/
│   │   │   ├── memory/
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   │   ├── AudioRecorder.tsx
│   │   │   ├── ResponseDisplay.tsx
│   │   │   ├── ProsodyVisualizer.tsx
│   │   │   └── ChatHistory.tsx
│   │   └── lib/
│   │       ├── api.ts             # API client
│   │       └── store.ts           # Zustand store
│   ├── package.json
│   └── next.config.ts
│
├── firstperson_api.py             # NEW - FastAPI backend
├── Dockerfile.firstperson         # NEW - Container image
├── docker-compose.prod.yml        # UPDATED - includes firstperson services
├── nginx.prod.conf                # UPDATED - dual domain routing
└── [existing files]
```


## Next Steps

1. **Get Digital Ocean details from you:**
   - Current VPS specs (CPU, RAM, storage)
   - Current domain setup
   - SSL certificate status

2. **Scaffold the app:**
   - Create firstperson-web directory
   - Create firstperson_api.py
   - Update Docker configs

3. **Implement frontend:**
   - Audio recorder UI
   - Real-time transcription display
   - Response rendering with prosody

4. **Implement backend:**
   - Integrate AudioConversationOrchestrator
   - Wire up FirstPerson pipeline
   - Add error handling

5. **Deploy & test**

##

**Benefits of this approach:**

- ✅ Proper audio I/O (no Streamlit limitations)
- ✅ Real-time WebSocket support
- ✅ Production-grade architecture
- ✅ Reuses 80% of audio code we built
- ✅ Reuses Velinor deployment pattern
- ✅ Scales with your Digital Ocean infrastructure
- ✅ Professional user experience

**Ready to start Phase 1?**

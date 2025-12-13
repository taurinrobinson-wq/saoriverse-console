# FirstPerson Audio Webapp - Phase 1 Complete ✅

## What You Now Have

```
✅ NextJS Frontend (firstperson-web/)
   ├── Landing page with feature overview
   ├── Audio chat interface
   ├── Zustand state management
   ├── API client with types
   └── Audio recorder component

✅ FastAPI Backend (firstperson_api.py)
   ├── /api/transcribe - audio → text
   ├── /api/chat - text → response + glyph
   ├── /api/synthesize - text + glyph → audio
   ├── /ws/chat - WebSocket streaming
   └── /health - health check

✅ Architecture Plan (FIRSTPERSON_AUDIO_WEBAPP_ARCHITECTURE.md)
   ├── Deployment diagrams
   ├── Technology stack
   └── Implementation roadmap
```

---

## Next Steps: Phase 2-4 Implementation

### Quick Links
- **Architecture:** [FIRSTPERSON_AUDIO_WEBAPP_ARCHITECTURE.md](./FIRSTPERSON_AUDIO_WEBAPP_ARCHITECTURE.md)
- **Frontend Code:** [firstperson-web/](./firstperson-web/)
- **Backend Code:** [firstperson_api.py](./firstperson_api.py)

### Immediate Actions

#### 1. Install Dependencies (Local Dev)
```bash
# Frontend
cd firstperson-web
npm install

# Backend
pip install fastapi uvicorn python-multipart faster-whisper pyttsx3
```

#### 2. Start Local Development
```bash
# Terminal 1: Frontend (port 3001)
cd firstperson-web
npm run dev

# Terminal 2: Backend (port 8001)
python firstperson_api.py

# Terminal 3: Ollama (port 11434)
ollama serve

# Visit: http://localhost:3001
```

#### 3. Test the Flow
1. Go to http://localhost:3001
2. Click "Start Conversation"
3. Click "Start Recording"
4. Speak: "Hello FirstPerson"
5. Should see:
   - ✅ Transcript of what you said
   - ✅ FirstPerson response
   - ✅ Emotional intent (glyph data)
   - ✅ Audio playback

### Phase 2: Frontend Completion (4-6 hours)

**What's Missing:**
- Settings page (model selection, voice settings)
- Memory/conversation history
- Prosody visualization
- Better error handling

**Files to Create:**
```
firstperson-web/src/
├── app/
│   ├── settings/page.tsx       # NEW
│   ├── memory/page.tsx         # NEW
│   └── error.tsx               # NEW
└── components/
    ├── ProsodyVisualizer.tsx   # NEW
    └── ChatHistory.tsx         # NEW
```

### Phase 3: Backend Integration (6-8 hours)

**Currently using mock FirstPerson:**
- Replace with real FirstPersonOrchestrator
- Integrate memory layer
- Proper glyph extraction
- Error handling for missing dependencies

**Key Files to Check:**
```
src/emotional_os/
├── core/firstperson/           # Main orchestrator
├── deploy/modules/
│   ├── audio_conversation_orchestrator.py
│   ├── prosody_planner.py
│   └── nlp_init.py
```

### Phase 4: Docker & Deployment (2-3 hours)

**When ready for Digital Ocean:**

1. **Create Dockerfile for FirstPerson**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8001
CMD ["python", "firstperson_api.py"]
```

2. **Update docker-compose.prod.yml**
```yaml
firstperson_api:
  build:
    context: .
    dockerfile: Dockerfile
  ports: [8001:8001]
  depends_on: [ollama]
```

3. **Update nginx.prod.conf**
```nginx
server_name firstperson.chat;
location / {
  proxy_pass http://firstperson_api:8001;
}
```

4. **Deploy**
```bash
ssh user@vps
cd /path/to/saoriverse-console
git pull
docker-compose build
docker-compose up -d
```

---

## Architecture Decision Points

### Frontend Port
- **Currently:** 3001 (local dev)
- **For Docker:** Next.js runs on same container, served through nginx

### API Communication
- **Local:** http://localhost:8001/api
- **Production:** https://firstperson.chat/api (through nginx proxy)

### Audio Handling
- **Recording:** Browser Web Audio API (client-side)
- **Transcription:** Faster-Whisper (server-side, CPU-optimized)
- **Synthesis:** pyttsx3 (server-side, offline TTS)
- **Streaming:** Optional WebSocket for real-time responses

---

## Testing Checklist

### Unit Tests
- [ ] Audio recorder component captures audio
- [ ] API client makes correct requests
- [ ] Backend endpoints return expected formats

### Integration Tests
- [ ] Full flow: record → transcribe → chat → synthesize
- [ ] Error handling: missing audio, API failure, etc.
- [ ] Multiple concurrent conversations

### UI/UX Tests
- [ ] Recording starts/stops cleanly
- [ ] Transcripts display correctly
- [ ] Audio playback works
- [ ] Settings persist
- [ ] Mobile-friendly responsive layout

### Performance Tests
- [ ] <100ms latency for transcription start
- [ ] <500ms latency for FirstPerson response
- [ ] <2s latency for audio synthesis
- [ ] CPU/memory usage reasonable

---

## Common Issues & Solutions

### Audio Recording Not Working
```
Check browser console for permission error:
NotAllowedError: Permission denied
→ User must grant microphone access
```

### Transcription Timeout
```
FastAPI default timeout is 30s
If running on slow machine, increase in firstperson_api.py:
app = FastAPI(..., request_timeout=60)
```

### Memory Usage High
```
Faster-Whisper uses significant RAM
On 2GB VPS, use "tiny" model instead of "base":
model = WhisperModel("tiny")
```

### CORS Errors
```
Frontend can't reach backend
Check:
- Backend running on correct port
- CORS origins configured in FastAPI
- Nginx proxy headers set correctly
```

---

## File Organization

```
saoriverse-console/
│
├── firstperson-web/                # Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx            # Home
│   │   │   ├── chat/page.tsx       # Main chat
│   │   │   ├── settings/page.tsx   # NEW
│   │   │   └── memory/page.tsx     # NEW
│   │   ├── components/
│   │   │   ├── AudioRecorder.tsx
│   │   │   ├── ResponseDisplay.tsx
│   │   │   ├── ProsodyVisualizer.tsx # NEW
│   │   │   └── ChatHistory.tsx     # NEW
│   │   └── lib/
│   │       ├── api.ts              # API client
│   │       └── store.ts            # Zustand
│   ├── package.json
│   ├── next.config.ts
│   └── tsconfig.json
│
├── firstperson_api.py              # FastAPI backend
│
├── Dockerfile.firstperson          # NEW for Docker
├── docker-compose.prod.yml         # UPDATED
├── nginx.prod.conf                 # UPDATED
│
├── src/                            # Existing
│   ├── emotional_os/
│   ├── firstperson/
│   └── parser/
│
└── [documentation files]
```

---

## Git Workflow

All work committed to `main`:
```bash
git add firstperson-web/ firstperson_api.py
git commit -m "Phase 2: [feature]"
git push origin main
```

---

## Success Criteria

### MVP (Minimum Viable Product)
- [x] Scaffold frontend & backend
- [ ] Audio recording → transcription works
- [ ] Transcription → FirstPerson response works
- [ ] Response → audio playback works
- [ ] Deploy to Digital Ocean

### Phase 2 (Polish)
- [ ] Settings page fully functional
- [ ] Conversation history saved
- [ ] Prosody visualization
- [ ] Better error messages

### Phase 3 (Production)
- [ ] Full FirstPerson integration (all tiers)
- [ ] Performance optimized
- [ ] Mobile responsive
- [ ] User authentication (optional)

---

## Ready to Code?

**Start with Phase 2 Frontend:**

1. Add `settings/page.tsx` with:
   - Model selector (orca-mini, llama3, etc.)
   - Voice settings sliders (pitch, rate, volume)
   - Save to localStorage

2. Add `ProsodyVisualizer.tsx` to show:
   - Voltage/tone/certainty on chart
   - Energy level bar
   - Visual feedback for emotion

3. Add `ChatHistory.tsx` to display:
   - Previous messages
   - Load/save conversations
   - Delete history option

**Estimated time:** 4-6 hours  
**Then:** Backend integration (6-8 hours)  
**Finally:** Deployment (2-3 hours)

---

**Total to Production:** ~15-20 hours  
**Total to MVP:** ~8-10 hours

You're ready! 🚀

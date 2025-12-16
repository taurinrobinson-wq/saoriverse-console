# Ollama Integration - Quick Reference

## TL;DR - Get Started in 3 Steps

```bash

# 1. Start services
docker-compose -f docker-compose.local.yml up -d

# 2. Pull a model (llama3 recommended, ~4.7GB)
docker-compose -f docker-compose.local.yml exec ollama ollama pull llama3

# 3. Open Streamlit

```text
```



## Architecture

```
Streamlit App (port 8501)
    ↓
FirstPerson Response Pipeline
    ├─ Local Glyph Parsing (primary)
    └─ Ollama Fallback (local LLM if glyph fails)
    ↓
Tier Processing (learning, aliveness, poetry)
    ↓
```text
```



## Key Files

| File | Purpose |
|------|---------|
| `docker-compose.local.yml` | Docker Compose with Streamlit + Ollama |
| `Dockerfile.streamlit` | Streamlit container image |
| `src/emotional_os/deploy/modules/ollama_client.py` | OllamaClient HTTP wrapper (347 lines) |
| `src/emotional_os/deploy/modules/ui_components/response_handler.py` | `_get_ollama_fallback_response()` integration |
| `src/emotional_os/deploy/modules/ui_components/session_manager.py` | `_ensure_ollama_client()` initialization |
| `OLLAMA_INTEGRATION_GUIDE.md` | Full documentation + troubleshooting |
| `test_ollama_integration.py` | Automated integration tests |

## Ollama Client API

```python
from src.emotional_os.deploy.modules.ollama_client import get_ollama_client_singleton

client = get_ollama_client_singleton()

# Check if available
if client.is_available():
    print("✅ Ollama running")

# Get models
models = client.get_available_models()
print(f"Available models: {models}")

# Generate response
response = client.generate(
    prompt="Why is the sky blue?",
    model="llama3",
    temperature=0.7,
    num_predict=512
)
print(response)

# Generate with conversation context
response = client.generate_with_context(
    user_input="I'm feeling overwhelmed",
    conversation_history=[
        {"role": "user", "content": "I've been stressed"},
        {"role": "assistant", "content": "That sounds challenging"},
    ],
    model="llama3"
)
```text
```



## Docker Commands

```bash

# Start services
docker-compose -f docker-compose.local.yml up -d

# Stop services
docker-compose -f docker-compose.local.yml down

# View logs
docker-compose -f docker-compose.local.yml logs -f streamlit
docker-compose -f docker-compose.local.yml logs -f ollama

# Check status
docker-compose -f docker-compose.local.yml ps

# Pull a model
docker-compose -f docker-compose.local.yml exec ollama ollama pull llama3
docker-compose -f docker-compose.local.yml exec ollama ollama pull mistral
docker-compose -f docker-compose.local.yml exec ollama ollama pull orca-mini

# List models
docker-compose -f docker-compose.local.yml exec ollama ollama list

# Remove container but keep data
docker-compose -f docker-compose.local.yml rm

# Full cleanup (removes models!)
```text
```



## Environment Variables

```bash

# Ollama base URL (auto-configured in Docker)
OLLAMA_BASE_URL=http://ollama:11434

# Local development (laptop, desktop)
```text
```



## Model Guide

```
orca-mini   → Smallest (1.3GB), fastest, fair quality - TRY THIS FIRST
neural-chat → Medium (4.1GB), good for chat
mistral     → Medium (4.1GB), well-rounded
```text
```



## Common Tasks

### Test Ollama directly (curl)

```bash

# Check health
curl http://localhost:11434/api/tags

# Generate response
curl -X POST http://localhost:11434/api/generate \
```text
```



### Run integration tests

```bash
```text
```



Expected: All 5 checks pass ✅

### Debug in Streamlit

```python
import streamlit as st

# Check session state
st.write("Ollama Available:", st.session_state.get("ollama_available"))
st.write("Models:", st.session_state.get("ollama_models"))

# Test generation
from src.emotional_os.deploy.modules.ollama_client import get_ollama_client_singleton
client = get_ollama_client_singleton()
response = client.generate("Test", model="llama3")
```text
```



### View service logs in real-time

```bash

# Ollama service
docker-compose -f docker-compose.local.yml logs -f ollama

# Streamlit service
docker-compose -f docker-compose.local.yml logs -f streamlit

# Both
```text
```



## Fallback Flow

```
User message arrives
    ↓
Try local Glyph parsing
    ├─ Success (has voltage_response) → Use + Tier processing → Display
    └─ Fail (empty/null) ↓
    ↓
Try FirstPerson orchestrator
    ├─ Success → Use + Tier processing → Display
    └─ Fail ↓
    ↓
Try Ollama fallback
    ├─ Available → HTTP call + Tier processing → Display
    └─ Unavailable ↓
    ↓
```text
```



## Performance Notes

- **llama3 on 1 vCPU**: 10-30s per response (slow but works)
- **llama3 on 4 vCPU**: 2-5s per response (reasonable)
- **orca-mini on 1 vCPU**: 3-5s per response (acceptable)
- **With GPU**: <1s per response (ideal)

## Files Created

```
docker-compose.local.yml          (72 lines)
Dockerfile.streamlit               (29 lines)
ollama_client.py                   (347 lines)
OLLAMA_INTEGRATION_GUIDE.md        (550+ lines)
OLLAMA_INTEGRATION_IMPLEMENTATION.md (400+ lines)
```text
```



## Files Modified

```
response_handler.py                (Added import + function)
session_manager.py                 (Added init function)
ui_refactored.py                   (Already imports everything)
```text
```



## Verification Checklist

- [ ] `docker-compose.local.yml` exists
- [ ] `Dockerfile.streamlit` exists
- [ ] `ollama_client.py` exists in `src/emotional_os/deploy/modules/`
- [ ] `response_handler.py` imports ollama_client
- [ ] `session_manager.py` calls `_ensure_ollama_client()`
- [ ] `test_ollama_integration.py` runs without errors
- [ ] Streamlit starts: `docker-compose -f docker-compose.local.yml up -d`
- [ ] Model pulls: `docker-compose -f docker-compose.local.yml exec ollama ollama pull llama3`
- [ ] http://localhost:8501 accessible
- [ ] Chat works in Streamlit

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Ollama not available" | `docker-compose -f docker-compose.local.yml up -d` |
| "No models" | `docker-compose -f docker-compose.local.yml exec ollama ollama pull llama3` |
| Slow responses | Use smaller model or check CPU usage |
| Port conflict | Change port in docker-compose.local.yml |
| Out of disk | `docker system prune` or remove models |
| Container won't start | Check logs: `docker-compose logs` |

## Integration Points

### Where Ollama is Called

```python

# 1. Session initialization
src/emotional_os/deploy/modules/ui_components/session_manager.py
    → _ensure_ollama_client()
    → stores in st.session_state["ollama_client"]

# 2. Response generation (fallback)
src/emotional_os/deploy/modules/ui_components/response_handler.py
    → _get_ollama_fallback_response()
    → called when glyph processing fails

# 3. Direct client usage (testing)
from src.emotional_os.deploy.modules.ollama_client import get_ollama_client_singleton
```



## What's Different from Velinor Deployment

| Aspect | Velinor (VPS) | FirstPerson (Local) |
|--------|---------------|-------------------|
| Deployment | DigitalOcean Droplet | Docker Compose locally |
| LLM | FirstPerson local processing | FirstPerson + Ollama fallback |
| Network | Public internet (https://velinor.firstperson.chat) | localhost:8501 |
| Ports | 80, 443 (nginx proxy) | 8501 (Streamlit) |
| CPU | 1 vCPU (constrained) | Your laptop (flexible) |
| Performance | Fast for game, okay for AI | Depends on hardware |

## Next Steps

1. **Test Locally**: Run docker-compose.local.yml
2. **Pull Model**: Get llama3 or orca-mini
3. **Chat**: Open http://localhost:8501 and converse
4. **Monitor**: Watch logs to see Ollama being called
5. **Tune**: Adjust system prompt or model parameters
6. **Share**: Share responses and feedback

## Resources

- **Full Guide**: `OLLAMA_INTEGRATION_GUIDE.md`
- **Implementation Details**: `OLLAMA_INTEGRATION_IMPLEMENTATION.md`
- **Ollama Repo**: https://github.com/ollama/ollama
- **Docker Docs**: https://docs.docker.com/compose/
- **FirstPerson**: See `LEARNING_QUICK_REFERENCE.md`
##

**Updated**: 2025 | **Status**: ✅ Ready to Use

# Ollama Integration Guide

FirstPerson Streamlit app now integrates with Ollama for local LLM inference. This allows running
AI-powered conversations entirely on your local machine without external API dependencies.

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- ~5-13GB disk space (for LLM models)
- Reasonable CPU/RAM (Ollama works but is slow on weak hardware)

### Launch with Ollama

```bash

# From repository root
docker-compose -f docker-compose.local.yml up -d

# Streamlit available at: http://localhost:8501

```text

```text
```


### Pull a Language Model

```bash


# List what's available
docker-compose -f docker-compose.local.yml exec ollama ollama list

# Pull llama3 (recommended, ~4.7GB)
docker-compose -f docker-compose.local.yml exec ollama ollama pull llama3

# Or try other models
docker-compose -f docker-compose.local.yml exec ollama ollama pull mistral      # ~4.1GB
docker-compose -f docker-compose.local.yml exec ollama ollama pull neural-chat  # ~4.1GB

```text

```

### Test Ollama Directly

```bash


# Check service health
curl http://localhost:11434/api/tags

# Generate a response (replace llama3 with your model)
curl -X POST http://localhost:11434/api/generate -d '{ "model": "llama3", "prompt": "Why is the sky
blue?", "stream": false

```text
```text

```

## Architecture

### Services (docker-compose.local.yml)

**`streamlit` service:**

- Builds from current Dockerfile.streamlit
- Runs FirstPerson Streamlit app on port 8501
- Environment variable: `OLLAMA_BASE_URL=http://ollama:11434`
- Auto-restarts on failure
- Health check via Streamlit endpoint

**`ollama` service:**

- Official Ollama Docker image
- API endpoint on port 11434
- Models stored in persistent volume `ollama_data`
- Health check via `/api/tags` endpoint

**Network:**

- Both services on `firstperson_network` bridge
- Streamlit can reach Ollama via hostname `ollama`

### Code Integration

#### 1. Ollama Client (`ollama_client.py`)

Location: `src/emotional_os/deploy/modules/ollama_client.py`

Core class: `OllamaClient`

- HTTP interface to Ollama `/api/generate` endpoint
- Blocking and streaming generation modes
- Model availability detection
- Error handling and fallbacks
- Context-aware generation with conversation history

Key methods:

```python


ollama = get_ollama_client_singleton() ollama.is_available()                                    #
Check if service running ollama.get_available_models()                            # List pulled
models ollama.generate(prompt, model="llama3")                  # Generate response

```text
```


#### 2. Response Handler Integration (`response_handler.py`)

Location: `src/emotional_os/deploy/modules/ui_components/response_handler.py`

New function: `_get_ollama_fallback_response(user_input, conversation_context)`

- Triggered when FirstPerson processing fails or returns empty response
- Uses Ollama for local LLM inference
- Maintains conversational coherence via system prompt
- Graceful fallback if Ollama unavailable

System prompt sets FirstPerson personality:

```
You are FirstPerson, a warm, empathetic AI companion for personal growth.
```text

```text
```


#### 3. Session State (`session_manager.py`)

Location: `src/emotional_os/deploy/modules/ui_components/session_manager.py`

New initialization: `_ensure_ollama_client()`

- Called during `initialize_session_state()`
- Sets up singleton OllamaClient
- Stores availability and model list in session state
- Available as:
  - `st.session_state["ollama_client"]` - Client instance
  - `st.session_state["ollama_available"]` - Boolean availability
  - `st.session_state["ollama_models"]` - List of available models

## Processing Pipeline

```

User Input
    ↓
Local Glyph Parsing (signal_parser.py)
    ├─→ Success: Use glyph + Tier processing
    └─→ Fail/Empty: Drop to Ollama fallback
    ↓
Ollama Fallback (_get_ollama_fallback_response)
    ├─→ Ollama available: HTTP POST to /api/generate
    │   - Uses conversation context as system prompt
    │   - Maintains personality + emotional awareness
    └─→ Ollama unavailable: Generic fallback response
    ↓
Tier 1 Foundation (learning, safety)
    ↓
Tier 2 Aliveness (emotional tuning)
    ↓
Tier 3 Poetic Consciousness (optional metaphor)
    ↓
Strip prosody metadata + prevent repetition
    ↓

```text

```

## Model Recommendations

### For FirstPerson Conversations

| Model | Size | Speed | Quality | Notes |
|-------|------|-------|---------|-------|
| llama3 | 4.7GB | Slow | Excellent | Default choice, best for conversations |
| mistral | 4.1GB | Medium | Good | Balanced performance/quality |
| neural-chat | 4.1GB | Medium | Good | Optimized for chat |
| orca-mini | 1.3GB | Fast | Fair | Best for resource-constrained setups |

### Recommended for Local Dev

- Start with **orca-mini** for fast iteration
- Upgrade to **llama3** for production-quality responses

## Configuration

### Environment Variables

In docker-compose or .env:

```bash


# Base URL for Ollama API (auto-configured in container)
OLLAMA_BASE_URL=http://ollama:11434

# Streamlit logging
STREAMLIT_LOGGER_LEVEL=info

# Optional: GPU acceleration (requires nvidia-docker)

```text
```text

```

### Customizing System Prompt

Edit `_get_ollama_fallback_response()` in `response_handler.py`:

```python


system_prompt = """You are FirstPerson, a warm, empathetic AI companion... [customize personality
and behavior here]

```text
```


## Troubleshooting

### "Ollama service not available"

```bash

# Check if container is running
docker-compose -f docker-compose.local.yml ps

# Check logs
docker-compose -f docker-compose.local.yml logs ollama

# Ensure network exists
docker network ls | grep firstperson_network

# Restart services
```text

```text
```


### "No models available"

```bash


# Pull a model
docker-compose -f docker-compose.local.yml exec ollama ollama pull llama3

# Verify

```text

```

### Slow responses

- **Cause**: CPU-only inference on weak hardware
- **Solution**:
  - Use smaller model (orca-mini)
  - Increase num_predict timeout in ollama_client.py
  - Consider GPU acceleration setup

### Out of memory/disk

```bash


# Clean up old containers/images
docker-compose -f docker-compose.local.yml down docker system prune -a

# Remove model data if needed (warning: deletes models)

```text
```text

```

## Production Considerations

### For Self-Hosted VPS (like Velinor deployment)

- **CPU Limitation**: 1 vCPU Droplets can run Ollama but response times will be 10-30s
- **Recommendation**: Use FirstPerson's local processing as primary, Ollama as optional fallback
- **Better Option**: Keep Ollama on local dev machine, use FirstPerson pipeline in production

### GPU Acceleration (Local Dev)

For NVIDIA GPU support, uncomment in docker-compose.local.yml:

```yaml


deploy: resources: reservations: devices:
        - driver: nvidia
count: 1

```bash
```


Requires: `nvidia-docker` installed and NVIDIA GPU available.

## API Reference

### OllamaClient Methods

```python

# Health check
client.is_available() -> bool

# Model management
models = client.get_available_models() -> list[str]
client.pull_model("llama3") -> bool

# Generation (blocking)
response = client.generate(
    prompt="Why is the sky blue?",
    model="llama3",
    temperature=0.7,
    num_predict=512
) -> str

# Generation with context (for conversations)
response = client.generate_with_context(
    user_input="I'm feeling overwhelmed",
    conversation_history=[
        {"role": "user", "content": "I've been stressed at work"},
        {"role": "assistant", "content": "That sounds challenging..."},
    ],
    model="llama3"
) -> str

# Health status
```text

```text
```


### Environment Detection

Ollama base URL is auto-detected:

- **Docker Compose**: Uses `http://ollama:11434` (container hostname)
- **Local dev**: Falls back to `http://localhost:11434`
- **Override**: Set `OLLAMA_BASE_URL` environment variable

## Development

### Testing Ollama Integration

```python


# In Python REPL or notebook
from src.emotional_os.deploy.modules.ollama_client import get_ollama_client_singleton

client = get_ollama_client_singleton()
print(client.is_available())
print(client.get_available_models())
response = client.generate("Hello! How can I help?", model="llama3")

```text

```

### Debugging Responses

Enable debug logging:

```python

import logging logging.basicConfig(level=logging.DEBUG)

```text
```text

```

Check session state in Streamlit:

```python


import streamlit as st st.write("Ollama Available:", st.session_state.get("ollama_available"))
st.write("Models:", st.session_state.get("ollama_models"))

```

## Contributing

To improve Ollama integration:

1. Test with different models and conversation styles
2. Tune system prompt for better FirstPerson personality
3. Optimize context window for longer conversations
4. Add model-specific parameter tuning
5. Submit PRs to `src/emotional_os/deploy/modules/ollama_client.py`

##

**Last Updated**: 2025
**Ollama Docs**: <https://github.com/ollama/ollama>
**FirstPerson Version**: Modularized UI system with Tier processing

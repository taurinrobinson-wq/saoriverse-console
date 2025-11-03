# Local LLM Setup Guide - 100% Private

This guide sets up a completely local language model for nuanced emotional responses. **Zero external API calls. Zero data leaving your machine.**

## Quick Start (5 minutes)

### 1. Install Ollama (One-time)

Choose your OS:

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
- Download from https://ollama.ai/download/windows
- Run the installer

### 2. Download a Model (5-10 minutes)

Models are downloaded **once** and stored locally (~4-13GB depending on size).

```bash
# Recommended: Fast + good quality (4GB)
ollama pull mistral

# Alternative options:
ollama pull neural-chat    # Chat-optimized (4GB)
ollama pull llama2         # Solid all-around (4GB)
ollama pull orca-2-7b      # Best at following instructions (4GB)
ollama pull llama2:13b     # More nuanced but slower (8GB)
```

After `ollama pull`, the model is **permanently stored** in `~/.ollama/models/`.

### 3. Start Ollama Server

```bash
# In a terminal (keep it running)
ollama serve
```

You'll see:
```
2025-11-03 14:23:45 "Ollama Server Running on 127.0.0.1:11434"
```

### 4. Test in Another Terminal

```bash
cd /workspaces/saoriverse-console
python emotional_os/llm/test_ollama.py
```

You should see:
```
✓ Ollama is running!
✓ Model loaded: mistral
```

---

## How It Works (Technically)

### Architecture

```
Your App (signal_parser.py)
    ↓
ollama_composer.py (local wrapper)
    ↓
Ollama Server (localhost:11434)
    ↓
Model weights (~/.ollama/models/mistral/)
    ↓
CPU/GPU on YOUR machine
    ↓
Response generated locally
```

**Key point:** Everything stays on your machine. No cloud calls, no API keys, no data transmission.

### Storage Location

```bash
# See all your downloaded models
ls ~/.ollama/models/blobs/

# Each model is just a file (not connected to internet)
# Mistral: ~4GB
# Llama2-13B: ~8GB
# etc.
```

### Disk Space

- **Mistral (recommended):** 4GB minimum, runs smoothly
- **Llama2-13B:** 8GB minimum, more nuanced responses
- **Neural-Chat:** 4GB, optimized for conversation

---

## Integration with Your System

### Option 1: Drop-in Replacement (Easiest)

Replace your `DynamicResponseComposer` with LLM:

```python
# In signal_parser.py

from emotional_os.llm.ollama_composer import get_ollama_composer

def generate_contextual_response(signals, input_text, glyph=None):
    composer = get_ollama_composer()
    
    response = composer.compose_response(
        user_input=input_text,
        emotional_signals=signals,
        glyph_context=glyph
    )
    
    return response
```

### Option 2: Hybrid (Recommended)

- Use **glyph system** for fast initial categorization
- Use **LLM** for nuanced response composition
- Fallback to templates if Ollama is down

```python
def generate_response(input_text, signals, glyph):
    try:
        # Try LLM first (more nuanced)
        composer = get_ollama_composer()
        if composer.is_available:
            return composer.compose_response(
                user_input=input_text,
                emotional_signals=signals,
                glyph_context=glyph
            )
    except Exception:
        pass
    
    # Fallback to existing system
    return _fallback_dynamic_response(input_text, signals, glyph)
```

---

## Privacy & Security

### ✅ What You Get

- **No external API calls** - Ollama never calls home
- **No API keys** - Nothing to expose
- **Local data only** - All conversation data stays on your machine
- **Auditable** - You can inspect what's being sent (nothing!)
- **Compliant** - No cloud services means no terms-of-service issues
- **Fast** - No network latency

### ✅ Verification

Monitor network traffic:

```bash
# macOS/Linux: See if ollama talks to the internet
sudo tcpdump -i any -n "port 11434 or (host ollama.ai)" | grep -v "127.0.0.1"

# Should show nothing (or only localhost)
```

Or use Little Snitch (macOS) / ZoneAlarm (Windows) / Gufw (Linux) to block network access to Ollama.

---

## Model Comparison

| Model | Size | Speed | Quality | Privacy | Best For |
|-------|------|-------|---------|---------|----------|
| **Mistral-7B** | 4GB | Fast (~1-2s) | Excellent | ✅ Local | **Recommended** |
| **Neural-Chat** | 4GB | Fast (~1-2s) | Very Good | ✅ Local | Chat-focused |
| **Llama2-7B** | 4GB | Medium (~2-3s) | Good | ✅ Local | General |
| **Llama2-13B** | 8GB | Medium (~3-4s) | Excellent | ✅ Local | Best quality |
| **Orca-2-7B** | 4GB | Medium (~2-3s) | Very Good | ✅ Local | Instruction-following |

**Recommendation:** Start with **Mistral**. If you want more nuance, upgrade to **Llama2-13B**.

---

## Troubleshooting

### "Connection refused" error

```bash
# Make sure Ollama server is running:
ollama serve

# In another terminal, verify:
curl http://localhost:11434/api/tags
```

### Model not found error

```bash
# List installed models:
ollama list

# Download missing model:
ollama pull mistral
```

### Slow responses

- First response: 5-10s (normal, loading model into memory)
- Subsequent responses: 1-3s (depending on model and hardware)
- To improve: Use GPU acceleration (requires CUDA/Metal support)

### High memory usage

- Mistral-7B: ~8GB RAM
- Llama2-13B: ~16GB RAM

If too slow, use smaller model or enable GPU support.

---

## Advanced: GPU Acceleration

Make responses **4-10x faster** with GPU:

### NVIDIA GPUs (CUDA)

```bash
# Ollama automatically detects NVIDIA GPUs
# Just install NVIDIA drivers

ollama serve  # Will use GPU automatically
```

### Apple Silicon (M1/M2/M3)

```bash
# Ollama automatically uses Metal acceleration
ollama serve  # Will use GPU automatically
```

### AMD GPUs (ROCm)

```bash
# Install ROCm drivers, then:
CUDA_VISIBLE_DEVICES=0 ollama serve
```

---

## Cost Comparison

| Approach | One-time Cost | Monthly Cost | Privacy | Nuance |
|----------|--------------|-------------|---------|--------|
| **Local Ollama** | $0 | $0 | ✅ 100% Local | 😊 Good |
| **OpenAI API** | $0 | $5-50 | ❌ Cloud | 😊 Excellent |
| **Claude API** | $0 | $5-50 | ❌ Cloud | 😊 Excellent |
| **Your gates system** | $0 | $0 | ✅ 100% Local | ⚠️ Limited |

**You get the best of both:** No cost, complete privacy, AND good nuance.

---

## Next Steps

1. ✅ Install Ollama
2. ✅ Download a model
3. ✅ Run `ollama serve`
4. ✅ Test: `python emotional_os/llm/test_ollama.py`
5. ⏭️ Integrate with signal_parser (instructions coming)

---

## Questions?

**Q: Can I change models later?**
Yes! `ollama pull other-model` and update the config.

**Q: Will this affect my existing glyph system?**
No! The LLM composer is optional and can work alongside your glyphs.

**Q: How do I delete a model?**
```bash
ollama rm mistral
# Also deletes from ~/.ollama/models/
```

**Q: Can I use Ollama in production?**
Yes! It's stable and production-ready. See https://github.com/ollama/ollama for production deployments.

---

**Summary:** You now have local, private, nuanced AI responses. No cloud calls. No API keys. No data leaving your machine. ✨

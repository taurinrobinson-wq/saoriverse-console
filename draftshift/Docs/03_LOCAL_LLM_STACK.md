# Local LLM Stack: Selection & Integration Guide

## 🖥️ Why Local LLMs Instead of Cloud APIs?

### Cost
- **Cloud APIs** (OpenAI, Anthropic, etc.): $0.01-$0.10 per 1,000 tokens.
- **Local LLMs**: Free after initial setup; no per-token billing.
- **Savings at scale**: 1,000 daily drafts = $10-100/day on cloud → $0/day locally.

### Privacy
- **Cloud APIs**: Your correspondence is sent to external servers.
- **Local LLMs**: All processing stays on-device; attorney-client privilege preserved.
- **Compliance**: No risk of inadvertent GDPR/bar association violations.

### Control
- **Cloud APIs**: Dependent on external service uptime and rate limits.
- **Local LLMs**: You control the model, hardware, and deployment.
- **Customization**: Fine-tune models for legal terminology and civility scoring.

---

## 🤖 Local LLM Options Comparison

### Option 1: **GPT4All** ⭐ RECOMMENDED FOR MVP
- **Installation**: Single-click installer, no Docker.
- **Models**: Pre-quantized Llama 2, Mistral, Phi-3 models.
- **Python Integration**: Native Python bindings; easy to embed in Streamlit.
- **Hardware**: Runs on CPU-only machines; 4-8GB RAM sufficient.
- **Use Case**: Perfect for DraftShift MVP rapid iteration.

**Pros:**
- Simplest setup; ideal for testing.
- Python API: `from gpt4all import GPT4All; model = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf")`.
- Active community and documentation.

**Cons:**
- Limited model variety compared to others.
- Performance depends on CPU; slower than GPU-accelerated options.

**For DraftShift**: Use GPT4All for Streamlit prototype. Proven to work with transformation tasks.

---

### Option 2: **LM Studio** 🎨 RECOMMENDED FOR DEVELOPMENT
- **Installation**: Desktop app (macOS, Windows, Linux).
- **Models**: GUI to download GGUF models from Hugging Face.
- **API**: Exposes OpenAI-compatible API on `localhost:1234`.
- **Use Case**: Best for development, testing, and model experimentation.

**Pros:**
- Beautiful UI for model management.
- OpenAI-compatible API makes integration straightforward.
- Easy model swapping without code changes.
- Great for debugging and prompt refinement.

**Cons:**
- Requires desktop app (not headless-friendly for production).
- Slightly more overhead than KoboldCPP.

**For DraftShift**: Use LM Studio during development and model selection phase. Once you've chosen a model, deploy with KoboldCPP or GPT4All.

---

### Option 3: **text-generation-webui** 🔬 FOR EXPERIMENTATION
- **Installation**: Docker or direct Python (git clone).
- **Flexibility**: Supports multiple backends (Transformers, ExLlama, GPTQ, AWQ).
- **Model Support**: Massive range of community models.
- **Customization**: Fine-tuning support, LoRA adapters, quantization.
- **Use Case**: Advanced users who want full control over inference pipeline.

**Pros:**
- Most flexible; supports cutting-edge models and techniques.
- Community-driven; constant updates.
- Built-in chat, API, and notebook interfaces.

**Cons:**
- Steeper learning curve.
- Setup more complex than GPT4All or LM Studio.
- Overkill for MVP unless you need specific features.

**For DraftShift**: Skip for MVP. Consider for Phase 2 if you want to experiment with fine-tuned legal models or exotic quantization formats.

---

### Option 4: **KoboldCPP** ⚡ RECOMMENDED FOR PRODUCTION
- **Installation**: Single binary; minimal dependencies.
- **Backend**: Efficient C++ implementation for GGUF models.
- **Performance**: Fastest CPU inference available.
- **Headless**: Pure CLI; no GUI (deploy as background service).
- **Use Case**: Production deployment, lean runtime, optimal performance.

**Pros:**
- Fastest local inference (CPU or GPU via Vulkan/CUDA).
- Minimal memory footprint.
- Zero external dependencies; single executable.
- Perfect for deploying to user machines or cloud VMs.

**Cons:**
- No GUI; CLI-based configuration.
- Steeper learning curve for setup.

**For DraftShift**: Use KoboldCPP for Phase 2 production deployment. Migrating from GPT4All to KoboldCPP is straightforward API-wise.

---

### Option 5: **AnythingLLM** 📄 FOR DOCUMENT ANALYSIS
- **Installation**: Desktop app or Docker.
- **Focus**: Document upload, RAG (Retrieval-Augmented Generation), multi-document analysis.
- **Use Case**: Analyze archives of correspondence, generate compliance reports.
- **Privacy**: Local-first option available; no cloud required.

**Pros:**
- Built for document workflows; not just chat.
- RAG support for correspondence archives.
- Dashboard export for compliance reports.

**Cons:**
- Heavier than other options; requires more resources.
- Not ideal for real-time inline transformation (slow for per-draft analysis).

**For DraftShift**: Use AnythingLLM later (Phase 3) for correspondence archive analysis and historical compliance reporting. Not essential for MVP.

---

## 🎯 Recommended Stack by Phase

### Phase 1: MVP (Months 1-3)
**Goal**: Prove civility scoring + transformation concept with Streamlit prototype.

**Stack:**
- **Analysis**: spaCy + TextBlob + NRC Lexicon (already working).
- **Transformation LLM**: GPT4All with Mistral-7B-Instruct (quantized).
- **Frontend**: Streamlit (rapid iteration).
- **Deployment**: Local user machines.

**Installation:**
```bash
pip install gpt4all streamlit
```

**Usage Example:**
```python
from gpt4all import GPT4All
model = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf")
result = model.generate("Rewrite this civilly: We strongly object...")
```

---

### Phase 2: Beta (Months 4-6)
**Goal**: Production-ready backend, explore model optimization.

**Stack:**
- **Analysis**: Same (spaCy + TextBlob + NRC).
- **Transformation LLM**: Switch to KoboldCPP backend; experiment with Llama 3 and other models.
- **Frontend**: FastAPI backend + React frontend.
- **Deployment**: User machines or small cloud VMs.

**Setup:**
1. Switch from GPT4All to KoboldCPP CLI.
2. Expose API on `localhost:5001`.
3. FastAPI calls KoboldCPP endpoint for transformations.

---

### Phase 3: Scale (Months 7+)
**Goal**: Enterprise deployment with advanced features.

**Stack:**
- **Analysis**: Same.
- **Transformation LLM**: KoboldCPP + optional fine-tuned civility model.
- **Frontend**: Full HTML/JS with Electron or PWA.
- **Advanced Features**: AnythingLLM for archive analysis; correspondence history.
- **Deployment**: Cloud or on-premises; enterprise customers.

---

## 💻 Integration: How It Works in DraftShift

### Current State (Already Working)
```python
# Analysis layer (ready)
from draftshift import core
from draftshift.tone_signal_parser import create_tone_signal_parser

analysis = core.detect_tone("Your correspondence here")
# Returns: tone, confidence, signals, emotions
```

### Phase 1 Addition: LLM Integration
```python
from gpt4all import GPT4All
from draftshift import core

# Load analysis (existing)
analysis = core.detect_tone(text)

# Load LLM (new)
llm = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf", device='cpu')

# Transform if civility score < threshold
if analysis['civility_score'] < 70:
    prompt = f"""Rewrite the following legal correspondence to be more civil 
    while maintaining assertiveness. Keep the core message but soften aggressive phrasing.
    
    Original: {text}
    
    Rewrite:"""
    
    rewrite = llm.generate(prompt, max_tokens=500)
    print(rewrite)
```

### API Integration (Phase 2)
```python
# FastAPI endpoint that calls KoboldCPP
@app.post("/analyze")
def analyze_draft(request: DraftRequest):
    # Existing analysis
    analysis = core.detect_tone(request.text)
    
    # LLM transformation via KoboldCPP
    if analysis['civility_score'] < 70:
        prompt = build_transformation_prompt(request.text, request.mode)
        response = requests.post("http://localhost:5001/api/generate", json={
            "prompt": prompt,
            "max_tokens": 500,
            "temperature": 0.7
        })
        rewrite = response.json()['results'][0]['text']
    else:
        rewrite = None
    
    return {
        "analysis": analysis,
        "suggested_rewrite": rewrite,
        "glyphs": glyph_map(analysis)
    }
```

---

## 🚀 Quick Start: GPT4All Setup

### Installation
```bash
# 1. Install Python package
pip install gpt4all streamlit

# 2. Download model (will auto-download on first use, or manually)
python -c "from gpt4all import GPT4All; GPT4All('mistral-7b-instruct-v0.1.Q4_0.gguf')"
```

### Verify
```bash
python -c "
from gpt4all import GPT4All
model = GPT4All('mistral-7b-instruct-v0.1.Q4_0.gguf')
result = model.generate('Civility means:', max_tokens=20)
print(result)
"
```

### In Streamlit
```python
import streamlit as st
from gpt4all import GPT4All

st.title("DraftShift - Civility Analyzer")

text = st.text_area("Enter correspondence:")
mode = st.selectbox("Mode", ["civility", "litigation", "client-friendly"])

if st.button("Transform"):
    model = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf")
    prompt = f"Rewrite in {mode} tone: {text}"
    result = model.generate(prompt, max_tokens=500)
    st.write("Suggested rewrite:")
    st.text(result)
```

---

## 🔄 Migration Path: GPT4All → KoboldCPP

### Why Migrate?
- **Performance**: KoboldCPP is 2-3x faster than GPT4All on CPU.
- **Flexibility**: Support for quantization techniques, custom models.
- **Scalability**: KoboldCPP handles higher concurrency.

### How to Migrate
1. **Phase 1**: Use GPT4All in Streamlit (testing phase).
2. **Phase 2 Start**: Install KoboldCPP; start it as a background service.
3. **Switch API Calls**: Change from `GPT4All().generate()` to HTTP POST to KoboldCPP endpoint.
4. **No UI Changes**: Frontend remains the same.

### Code Before (GPT4All)
```python
from gpt4all import GPT4All
model = GPT4All("mistral-7b-instruct-v0.1.Q4_0.gguf")
result = model.generate(prompt, max_tokens=500)
```

### Code After (KoboldCPP)
```python
import requests
response = requests.post("http://localhost:5001/api/generate", json={
    "prompt": prompt,
    "max_tokens": 500,
    "temperature": 0.7
})
result = response.json()['results'][0]['text']
```

---

## 📊 Hardware Recommendations

### Minimum (MVP Testing)
- **CPU**: Dual-core (Intel i5 / Apple M1 or better)
- **RAM**: 4GB
- **Disk**: 8GB free
- **Models**: Mistral 7B Q4 quantized (best performance/quality ratio)

### Recommended (Production)
- **CPU**: Quad-core or GPU (RTX 3060 or better if available)
- **RAM**: 8GB+
- **Disk**: 16GB free
- **Models**: Llama 3 8B Q5 or Mistral 7B Q5

### Enterprise Scale
- **Hardware**: GPU cluster (RTX 4090s or H100s)
- **Deployment**: Kubernetes + LM deployment framework
- **Models**: Fine-tuned civility models; optional larger models (13B+)

---

## 🎓 Recommended Reading

1. **GGUF Format**: https://github.com/ggerganov/ggml/blob/master/gguf.md
2. **Mistral 7B Instruct**: https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2
3. **Quantization Techniques**: https://huggingface.co/docs/transformers/quantization
4. **KoboldCPP Docs**: https://github.com/LostRuins/koboldcpp

---

This stack provides **maximum flexibility**, **zero cloud costs**, and **full privacy control**—exactly what DraftShift needs to serve attorneys ethically and effectively.

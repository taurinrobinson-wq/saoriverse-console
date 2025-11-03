# Running Saoriverse Console Locally on Mac

## Prerequisites

✅ Ollama installed on external hard drive and running (`ollama serve`)
✅ Repository cloned or accessible on your Mac

## Quick Start

### 1. Clone/Open the Repository

On your Mac, open Terminal and navigate to where you want the project:

```bash
# If you haven't cloned it yet:
git clone https://github.com/taurinrobinson-wq/saoriverse-console.git
cd saoriverse-console
```

### 2. Set Up Python Environment

```bash
# Create a virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run with Ollama Integration

Since Ollama is already running on your Mac (via `ollama serve`), just run:

```bash
streamlit run app.py
```

**That's it!** The app will automatically connect to Ollama at `http://localhost:11434`

### How It Works

- **Ollama**: Running on your Mac via `OLLAMA_HOST=0.0.0.0:11434 ollama serve`
- **Streamlit App**: Runs locally on your Mac, connects to Ollama automatically
- **Everything**: Stays 100% private on your machine

## If You Want to Specify Ollama URL Explicitly

If needed, you can set the environment variable:

```bash
OLLAMA_BASE_URL="http://localhost:11434" streamlit run app.py
```

## Testing Without Ollama

If Ollama stops running, the app automatically falls back to template responses - no errors, just graceful degradation.

## Troubleshooting

**"ModuleNotFoundError" when running streamlit:**
```bash
# Make sure your virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**"Ollama not running" message:**
```bash
# In another Terminal window:
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

**Want to use a different model?**
```bash
# On your Mac, download it
ollama pull llama2
# or
ollama pull neural-chat

# Then restart ollama serve, the app will detect it
```

## File Structure

Key files for local development:
- `app.py` - Main Streamlit app entry point
- `emotional_os/glyphs/signal_parser.py` - Core response generation with LLM integration
- `emotional_os/llm/ollama_composer.py` - Local Ollama interface

---

**That's all you need!** The system is designed to work seamlessly locally with Ollama.

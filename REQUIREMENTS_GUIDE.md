# Requirements Management Guide

## Single Requirements File

All dependencies are now consolidated in **`requirements.txt`** at the root of the project.

### Installation

```bash
# Install all dependencies
pip install -r requirements.txt

# Or use pip-tools for reproducible builds
pip install pip-tools
pip-compile requirements.txt
pip install -r requirements.txt
```

### Post-Installation Setup

Some packages require additional setup:

#### spaCy Language Models
```bash
python -m spacy download en_core_web_sm
```

#### TextBlob Corpora
```bash
python -m textblob.download_corpora
```

#### Faster-Whisper Models
Models are downloaded automatically on first use (~140MB for "base" model).

#### Coqui TTS Models
Models are downloaded automatically on first use (~200MB for English).

### Optional Dependencies

#### GPU Support (NVIDIA CUDA)
If you have CUDA installed, uncomment these lines in `requirements.txt`:
```
torch>=2.0.0
torchaudio>=2.0.0
```

#### Advanced Audio Processing
For noise suppression, uncomment:
```
noisereduce>=2.0.0
```

## Legacy Config Files

The following files in `config/` are now **deprecated** and can be removed:
- `config/requirements.txt`
- `config/requirements-nlp.txt`
- `config/requirements-voice.txt`
- `config/requirements-dev.txt`

All their contents have been consolidated into the root `requirements.txt`.

## Troubleshooting

### Package Not Loaded in Streamlit
If a package shows as "not available" in the Streamlit console:

1. Verify it's installed: `pip list | grep package-name`
2. Check you're using the right Python: `which python` (or `where python` on Windows)
3. Restart Streamlit: Kill the process and run `streamlit run app.py` again
4. Check for virtual environment activation issues

### Python Version Mismatch
Ensure you're using Python 3.9 or higher:
```bash
python --version
```

### Virtual Environment Issues
If using a virtual environment:
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# Then install
pip install -r requirements.txt
```

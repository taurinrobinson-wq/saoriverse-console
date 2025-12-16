# Requirements Management Guide

## Python Version Compatibility

**Recommended:** Python 3.11 or 3.12
**Supported:** Python 3.10+
**NOT supported:** Python 3.9 or earlier, or 3.13 (limited wheel support)

### Why Python 3.11 or 3.12?

- ✅ All packages have pre-built wheels (faster installation)
- ✅ Full support for `spacy`, `TTS`, and audio packages
- ✅ Best performance and stability

### Checking Your Python Version

```bash
```text
```text
```

### Switching Python Versions

If you have multiple Python versions installed:

**Windows (using py launcher):**

```bash


# List installed versions
py --list-paths

# Use Python 3.12 specifically
py -3.12 -m pip install -r requirements.txt

```text
```

**Or use pyenv/conda:**

```bash

# With pyenv
pyenv install 3.12.0 pyenv local 3.12.0

# With conda
conda create -n firstperson python=3.12 conda activate firstperson
```text
```text
```

## Single Requirements File

All dependencies are now consolidated in **`requirements.txt`** at the root of the project.

### Installation

```bash


# Install all dependencies
pip install -r requirements.txt

# Or use pip-tools for reproducible builds
pip install pip-tools pip-compile requirements.txt

```text
```

### Post-Installation Setup

Some packages require additional setup:

#### spaCy Language Models

```bash
```text
```text
```

#### TextBlob Corpora

```bash

```text
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
```text
```text
```

#### Advanced Audio Processing

For noise suppression, uncomment:

```

```text
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

1. **Check Python version:** `python --version` (should be 3.11 or 3.12)
2. **Verify installation:** `pip list | grep package-name`
3. **Reinstall:** `pip install --force-reinstall -r requirements.txt` 4. **Restart Streamlit:** Kill
the process and run `streamlit run app.py` again

### "No module named X"

This usually means the package isn't installed in your Python environment.

1. Check which Python Streamlit is using (shown in the sidebar) 2. Install directly in that
environment: `python -m pip install -r requirements.txt` 3. Restart Streamlit

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

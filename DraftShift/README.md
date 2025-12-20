# DraftShift - Interactive Tone Shifter for Legal Correspondence

## 🚀 Quick Start

### Prerequisites

1. Python 3.11+ (tested with 3.12)
2. Required dependencies (install with pip)

### Installation

```bash
# From the repository root directory
cd /path/to/saoriverse-console

# Install dependencies
pip install streamlit python-dotenv textblob spacy

# Download optional NLP models (recommended)
python -m spacy download en_core_web_sm
python -m textblob.download_corpora
```

### Running the App

#### Option 1: From Repository Root (Recommended)
```bash
cd /path/to/saoriverse-console
streamlit run DraftShift/app.py
```

#### Option 2: From DraftShift Directory
```bash
cd /path/to/saoriverse-console/DraftShift
streamlit run app.py
```

The app will automatically:
- Add the parent directory to Python path for imports
- Load the `.env` file from the repository root if available
- Work with or without optional dependencies

### 🔧 Configuration

#### Environment Variables (Optional)

Create a `LiToneCheck.env` file in the repository root with:

```env
# Optional: Enable debug logging
DEBUG_DRAFTSHIFT=true

# Optional: Sapling API for advanced grammar checking
SAPLING_API_KEY=your_api_key_here
```

#### Debug Mode

Set `DEBUG_DRAFTSHIFT=true` in your environment or `.env` file to see:
- Python path information
- Import attempt details
- .env file loading status

Example:
```bash
export DEBUG_DRAFTSHIFT=true
streamlit run DraftShift/app.py
```

### 📦 Dependencies

**Required:**
- `streamlit` - Web interface
- `python-dotenv` - Environment variable loading
- `textblob` - Sentiment analysis
- `spacy` - NLP processing

**Optional but Recommended:**
- `en_core_web_sm` - spaCy English model
- NLTK corpora (downloaded via textblob)

### 🛠️ Troubleshooting

#### Import Errors

If you see `ModuleNotFoundError` for DraftShift modules:

1. **Check your current directory:**
   ```bash
   pwd
   ```
   Make sure you're in the repository root or DraftShift directory.

2. **Verify Python path:**
   The app automatically adds the parent directory to `sys.path`, but you can debug with:
   ```bash
   DEBUG_DRAFTSHIFT=true streamlit run DraftShift/app.py
   ```

3. **Check package structure:**
   Ensure `DraftShift/__init__.py` exists.

#### Missing Optional Dependencies

The app gracefully handles missing optional dependencies:
- **Signal Parser**: Shows "⚠️ Not available (optional)" if `src.emotional_os.core.signal_parser` is missing
- **Sapling API**: Shows "❌ Not configured" if API key is not set
- **spaCy/TextBlob**: Will show tool status in the sidebar

### 🎯 Features

- **Tone Detection**: Automatically detect the tone of legal correspondence
- **Tone Transformation**: Shift text to different tones (Very Formal, Formal, Neutral, Friendly, Empathetic)
- **Civility Scoring**: Score documents for civility and professionalism (0-100)
- **Risk Alerts**: Identify potentially problematic language with severity levels
- **Sentence Analysis**: Detailed breakdown of each sentence's tone and structure

### 📖 Documentation

For more detailed documentation, see:
- `Docs/SETUP_AND_VERIFICATION.md` - Setup and verification guide
- `Docs/INTEGRATION_GUIDE.md` - Module integration details
- `Docs/00_INDEX.md` - Complete documentation index

### ✅ Verification

Test that the app is working:

1. **Test imports:**
   ```bash
   python -c "from DraftShift.core import detect_tone; print('✅ Imports work')"
   ```

2. **Start the app:**
   ```bash
   streamlit run DraftShift/app.py
   ```

3. **Use the app:**
   - Paste or type legal correspondence in the text area
   - Click "🔄 Analyze & Transform"
   - View transformed text and analysis

### 🐛 Known Issues

- Signal parser from `src.emotional_os.core` is an optional dependency and may not be available
- Some NLP tools require additional downloads (spaCy model, NLTK corpora)

### 📝 License

Part of the Saoriverse Console project.

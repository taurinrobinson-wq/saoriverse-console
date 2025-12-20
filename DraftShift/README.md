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

**✅ FIXED**: The app now automatically handles module import path issues!

The app startup will display diagnostic information including:
- Current working directory
- Script location
- Repository root path
- Python sys.path entries

If you see `ModuleNotFoundError` for DraftShift modules, the app will show:
- Detailed error information
- Diagnostic information about your environment
- Step-by-step troubleshooting guide

**To enable additional debug output:**
```bash
export DEBUG_DRAFTSHIFT=true
streamlit run DraftShift/app.py
```

**Verification:**
Run the verification script to test your setup:
```bash
# From repository root
python DraftShift/Tests/verify_setup.py

# From DraftShift directory
cd DraftShift
python Tests/verify_setup.py
```

Both should work correctly thanks to automatic path configuration.

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

1. **Quick verification (recommended):**
   ```bash
   # From repository root
   python DraftShift/Tests/verify_setup.py
   ```
   
   Or from DraftShift directory:
   ```bash
   cd DraftShift
   python Tests/verify_setup.py
   ```

2. **Test imports (optional):**
   ```bash
   # From repository root
   cd /path/to/saoriverse-console
   python -c "import sys; from pathlib import Path; sys.path.insert(0, '.'); from DraftShift.core import detect_tone; print('✅ Imports work')"
   ```

3. **Start the app:**
   ```bash
   streamlit run DraftShift/app.py
   ```
   
   The app will display startup diagnostics showing:
   - ✅ Path configuration
   - ✅ Module import status
   - ✅ Available NLP tools

4. **Use the app:**
   - Paste or type legal correspondence in the text area
   - Click "🔄 Analyze & Transform"
   - View transformed text and analysis

### 🐛 Known Issues

- Signal parser from `src.emotional_os.core` is an optional dependency and may not be available
- Some NLP tools require additional downloads (spaCy model, NLTK corpora)

### 📝 License

Part of the Saoriverse Console project.

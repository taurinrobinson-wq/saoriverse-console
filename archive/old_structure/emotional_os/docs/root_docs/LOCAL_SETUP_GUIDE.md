# Running Saoriverse Console Locally on Mac

## Prerequisites

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


### 3. Run the App

```bash
streamlit run app.py
```


**That's it!** The app runs locally with built-in response generation.

### How It Works

- **Streamlit App**: Runs locally on your Mac
- **Everything**: Stays 100% private on your machine

## Troubleshooting

**"ModuleNotFoundError" when running streamlit:**

```bash

# Make sure your virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```


## File Structure

Key files for local development:

- `app.py` - Main Streamlit app entry point
- `emotional_os/glyphs/signal_parser.py` - Core response generation

##

**That's all you need!** The system is designed to work seamlessly locally.

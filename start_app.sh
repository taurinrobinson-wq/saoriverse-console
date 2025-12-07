#!/bin/bash
# Start FirstPerson Streamlit app with proper environment setup
# Uses Python 3.11 from the workspace venv for consistency

set -e

cd /workspaces/saoriverse-console

# Explicitly use the workspace venv (Python 3.11)
VENV_PATH="/workspaces/saoriverse-console/.venv"
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Virtual environment not found at $VENV_PATH"
    echo "Creating it now with Python 3.11..."
    python3.11 -m venv "$VENV_PATH"
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Verify Python version
PYTHON_VERSION=$($VENV_PATH/bin/python3 --version 2>&1 | awk '{print $2}')
echo "✓ Using Python $PYTHON_VERSION from $VENV_PATH"

# Ensure .streamlit directory exists
mkdir -p .streamlit

# Create a minimal streamlit config if it doesn't exist
if [ ! -f .streamlit/config.toml ]; then
    cat > .streamlit/config.toml << 'EOF'
[client]
showErrorDetails = true
showWarningOnDirectExecution = false

[logger]
level = "info"

[server]
headless = true
port = 8501
enableXsrfProtection = true
maxUploadSize = 200
EOF
fi

# Set environment variables
export PYTHONUNBUFFERED=1
export STREAMLIT_SERVER_HEADLESS=true

# Run the app with explicit port and timeout settings
streamlit run app.py \
  --server.port=8501 \
  --server.address=0.0.0.0 \
  --logger.level=info \
  --client.showErrorDetails=true

#!/bin/bash
# Start FirstPerson Streamlit app with proper environment setup

set -e

cd /workspaces/saoriverse-console

# Activate virtual environment
source .venv/bin/activate

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

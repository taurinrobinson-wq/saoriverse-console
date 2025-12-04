#!/bin/bash
# FirstPerson Local Mode Setup Script
# Sets up paths and runs the system from external drive
# 
# Usage: ./setup_external.sh
# Or with custom external drive path: ./setup_external.sh /path/to/external/drive

set -e

# Default paths
EXTERNAL_DRIVE="/Volumes/My Passport for Mac"
FIRSTPERSON_PATH="$EXTERNAL_DRIVE/FirstPerson"
LOCAL_PROJECT="/Users/taurinrobinson/saoriverse-console"

# Allow custom external drive path
if [ ! -z "$1" ]; then
    EXTERNAL_DRIVE="$1"
    FIRSTPERSON_PATH="$EXTERNAL_DRIVE/FirstPerson"
fi

echo "🏛️  FIRSTPERSON LOCAL MODE - EXTERNAL DRIVE SETUP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if external drive is mounted
if [ ! -d "$EXTERNAL_DRIVE" ]; then
    echo "❌ External drive not found at: $EXTERNAL_DRIVE"
    echo "Please mount your external drive and try again."
    exit 1
fi

echo "✓ External drive found: $EXTERNAL_DRIVE"

# Check if FirstPerson is on external drive
if [ ! -d "$FIRSTPERSON_PATH" ]; then
    echo "❌ FirstPerson not found at: $FIRSTPERSON_PATH"
    echo "Run setup during installation or check path."
    exit 1
fi

echo "✓ FirstPerson system found on external drive"

# Verify symlinks are in place
if [ ! -L "$LOCAL_PROJECT/.venv" ]; then
    echo "⚠️  Venv symlink missing, creating..."
    cd "$LOCAL_PROJECT"
    ln -s "$FIRSTPERSON_PATH/venv" .venv
    echo "✓ Venv symlink created"
fi

if [ ! -L "$LOCAL_PROJECT/data" ]; then
    echo "⚠️  Data symlink missing, creating..."
    cd "$LOCAL_PROJECT"
    ln -s "$FIRSTPERSON_PATH/data" data
    echo "✓ Data symlink created"
fi

echo "✓ All symlinks verified"
echo ""

# Show status
echo "📊 SYSTEM STATUS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Local project:    $LOCAL_PROJECT"
echo "External storage: $FIRSTPERSON_PATH"
echo "Virtual env:      $FIRSTPERSON_PATH/venv"
echo "Data storage:     $FIRSTPERSON_PATH/data"
echo ""

# Show venv info
PYTHON_PATH="$FIRSTPERSON_PATH/venv/bin/python"
if [ -f "$PYTHON_PATH" ]; then
    PYTHON_VERSION=$($PYTHON_PATH --version)
    echo "✓ Python ready: $PYTHON_VERSION"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start FirstPerson:"
echo "   cd $LOCAL_PROJECT"
echo "   .venv/bin/streamlit run main_v2.py  # (ARCHIVED: emotional_os_ui_v2.py)"
echo ""
echo "🧪 To run tests:"
echo "   cd $LOCAL_PROJECT"
echo "   .venv/bin/python test_local_mode.py"
echo ""

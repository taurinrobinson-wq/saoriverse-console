#!/bin/bash
# Velinor Game - Quick Setup (macOS/Linux)

set -e

echo "🎮 Velinor Game Setup"
echo "===================="
echo ""

# Check Python
echo "✓ Checking Python..."
python3 --version

# Create virtual environment
echo "✓ Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "✓ Installing dependencies..."
pip install --upgrade pip
pip install streamlit pillow

# Verify installation
echo "✓ Verifying installation..."
streamlit version

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the game:"
echo "  1. source venv/bin/activate"
echo "  2. streamlit run velinor_app.py"
echo ""

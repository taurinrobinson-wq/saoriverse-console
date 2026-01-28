#!/bin/bash
# Setup DraftShift Web UI for local development

echo "🚀 Setting up DraftShift Web UI..."

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+"
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✓ Node.js $(node --version)"
echo "✓ Python $(python3 --version)"

# Install Node dependencies
echo ""
echo "📦 Installing Node dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ npm install failed"
    exit 1
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install -r ../requirements-backend.txt

if [ $? -ne 0 ]; then
    echo "⚠️  pip install had issues (may be ok if dependencies already installed)"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo ""
echo "Terminal 1 - Start React dev server:"
echo "  npm run dev"
echo ""
echo "Terminal 2 - Start FastAPI backend:"
echo "  python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Then open browser to http://localhost:5173"
echo ""

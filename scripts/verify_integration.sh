#!/bin/bash
# Integration Verification Checklist
# Run this to verify dynamic glyph evolution is properly integrated

set -e

echo "🔍 DYNAMIC GLYPH EVOLUTION - INTEGRATION VERIFICATION"
echo "============================================================"
echo ""

# Check 1: Core files exist
echo "✓ Checking core files..."
files_to_check=(
    "dynamic_glyph_evolution.py"
    "hybrid_processor_with_evolution.py"
    "emotional_os/deploy/modules/ui.py"
    "main_v2.py"
)

for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ MISSING: $file"
    fi
done

echo ""

# Check 2: Integration points in ui.py
echo "✓ Checking ui.py integration..."
if grep -q "create_integrated_processor" "emotional_os/deploy/modules/ui.py"; then
    echo "  ✓ integrated_processor initialization found"
else
    echo "  ✗ integrated_processor initialization NOT found"
fi

if grep -q "DynamicGlyphEvolution\|dynamic.*glyph" "emotional_os/deploy/modules/ui.py"; then
    echo "  ✓ Dynamic glyph processing found"
else
    echo "  ✗ Dynamic glyph processing NOT found"
fi

if grep -q "new_glyphs_this_session" "emotional_os/deploy/modules/ui.py"; then
    echo "  ✓ Session glyph storage found"
else
    echo "  ✗ Session glyph storage NOT found"
fi

echo ""

# Check 3: Integration points in main_v2.py
echo "✓ Checking main_v2.py sidebar..."
if grep -q "Glyphs Discovered\|new_glyphs_this_session" "main_v2.py"; then
    echo "  ✓ Glyph sidebar display found"
else
    echo "  ✗ Glyph sidebar display NOT found"
fi

if grep -q "export.*glyph" "main_v2.py"; then
    echo "  ✓ Glyph export button found"
else
    echo "  ✗ Glyph export button NOT found"
fi

echo ""

# Check 4: Required imports
echo "✓ Checking Python imports..."
if python3 -c "from hybrid_processor_with_evolution import create_integrated_processor" 2>/dev/null; then
    echo "  ✓ hybrid_processor_with_evolution imports successfully"
else
    echo "  ✗ hybrid_processor_with_evolution import FAILED"
fi

if python3 -c "from dynamic_glyph_evolution import DynamicGlyphEvolution" 2>/dev/null; then
    echo "  ✓ dynamic_glyph_evolution imports successfully"
else
    echo "  ✗ dynamic_glyph_evolution import FAILED"
fi

echo ""

# Check 5: Learning directories
echo "✓ Checking directories..."
if [ -d "learning" ]; then
    echo "  ✓ learning/ directory exists"
    if [ -d "learning/user_overrides" ]; then
        echo "    ✓ learning/user_overrides/ exists"
    else
        echo "    ℹ creating learning/user_overrides/"
        mkdir -p "learning/user_overrides"
    fi
    if [ -d "learning/generated_glyphs" ]; then
        echo "    ✓ learning/generated_glyphs/ exists"
    else
        echo "    ℹ creating learning/generated_glyphs/"
        mkdir -p "learning/generated_glyphs"
    fi
else
    echo "  ✗ learning/ directory MISSING - creating..."
    mkdir -p "learning/user_overrides"
    mkdir -p "learning/generated_glyphs"
fi

echo ""

# Check 6: Configuration
echo "✓ Checking configuration..."
if grep -q "min_frequency_for_glyph" "dynamic_glyph_evolution.py"; then
    echo "  ✓ Frequency threshold configurable"
    threshold=$(grep "min_frequency_for_glyph.*300" dynamic_glyph_evolution.py | head -1 || echo "")
    if [ -n "$threshold" ]; then
        echo "    ℹ Default threshold: 300"
    fi
else
    echo "  ✗ Frequency threshold NOT found"
fi

if grep -q "emotion_symbols" "dynamic_glyph_evolution.py"; then
    echo "  ✓ Emotion-symbol mapping found"
else
    echo "  ✗ Emotion-symbol mapping NOT found"
fi

echo ""

# Check 7: Documentation
echo "✓ Checking documentation..."
docs=(
    "DYNAMIC_GLYPH_EVOLUTION_GUIDE.md"
    "INTEGRATION_SUMMARY.md"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        echo "  ✓ $doc"
    else
        echo "  ✗ MISSING: $doc"
    fi
done

echo ""

# Check 8: Data persistence
echo "✓ Checking data persistence setup..."
if grep -q "conversation_glyphs.json" "dynamic_glyph_evolution.py"; then
    echo "  ✓ Glyph registry file path configured"
else
    echo "  ✗ Glyph registry NOT configured"
fi

echo ""
echo "============================================================"
echo "✨ INTEGRATION VERIFICATION COMPLETE"
echo ""
echo "Next steps:"
echo "  1. Run Streamlit: streamlit run main_v2.py"
echo "  2. Set processing mode to 'hybrid'"
echo "  3. Have meaningful conversations"
echo "  4. Watch the 'Glyphs Discovered' sidebar populate"
echo "  5. Check learning/conversation_glyphs.json for persistent data"
echo ""
echo "Detailed docs: INTEGRATION_SUMMARY.md"
echo "Full guide: DYNAMIC_GLYPH_EVOLUTION_GUIDE.md"
echo "============================================================"

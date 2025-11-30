#!/usr/bin/env python3
"""
Test script for the Ritual Capsule Processor
"""

try:
    from ritual_capsule_processor import GlyphObject, RitualCapsuleProcessor
except ImportError:
    print("Warning: ritual_capsule_processor not available (optional dependency)")
    GlyphObject = None
    RitualCapsuleProcessor = None


def test_basic_functionality():
    """Test basic processor functionality"""
    if RitualCapsuleProcessor is None:
        print("⚠️ Skipping: ritual_capsule_processor not available (optional dependency)")
        return

    print("🔮 Testing Ritual Capsule Processor...")

    # Initialize processor
    processor = RitualCapsuleProcessor()

    # Test emotional signal detection
    test_text = "This glyph represents deep ache and longing, with elements of grief and stillness"
    signals = processor.parse_emotional_signals(test_text)
    print(f"✓ Emotional signals detected: {signals}")

    # Test voltage marker detection
    voltage_markers, voltage_pair = processor.parse_voltage_markers(
        "The transmission carries ε-δ voltage with strong resonance"
    )
    print(f"✓ Voltage markers: {voltage_markers}, Pair: {voltage_pair}")

    # Test gate detection
    gates = processor.parse_gates("This belongs to Gate 6 ceremony of witness and devotion")
    print(f"✓ Gates detected: {gates}")

    # Test glyph categorization
    test_glyph = GlyphObject()
    test_glyph.name = "Sacred Ache"
    test_glyph.description = "A deep longing that transcends simple desire"
    category = processor.categorize_glyph(test_glyph)
    print(f"✓ Glyph category: {category}")

    # Test valence determination
    valence = processor.determine_valence(test_glyph)
    print(f"✓ Glyph valence: {valence}")

    print("✨ Basic functionality tests passed!")


def test_file_scanning():
    """Test file scanning functionality"""
    if RitualCapsuleProcessor is None:
        print("⚠️ Skipping: ritual_capsule_processor not available (optional dependency)")
        return

    print("\n🔍 Testing file scanning...")

    processor = RitualCapsuleProcessor()
    files = processor.scan_for_new_files()

    print(f"✓ Found {len(files)} files to process:")
    for file_path in files:
        print(f"   - {file_path.name}")

    if files:
        # Test text extraction on first file
        sample_file = files[0]
        text = processor.extract_text_content(sample_file)
        print(f"✓ Sample text from {sample_file.name}: {text[:100]}...")


def test_glyph_creation():
    """Test creating a sample glyph object"""
    if GlyphObject is None:
        print("⚠️ Skipping: GlyphObject not available (optional dependency)")
        return

    print("\n🎨 Testing glyph object creation...")

    glyph = GlyphObject()
    glyph.name = "Test Sanctuary"
    glyph.description = "A space of deep stillness and recognition"
    glyph.emotional_signals = ["stillness", "recognition", "sanctuary"]
    glyph.voltage_pair = "te-01"
    glyph.category = "Stillness"
    glyph.valence = "Neutral"

    glyph_dict = glyph.to_dict()
    print(f"✓ Glyph object created: {glyph.name}")
    print(f"   Category: {glyph.category}, Valence: {glyph.valence}")
    print(f"   Signals: {glyph.emotional_signals}")


if __name__ == "__main__":
    try:
        test_basic_functionality()
        test_file_scanning()
        test_glyph_creation()
        print("\\n🌟 All tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()

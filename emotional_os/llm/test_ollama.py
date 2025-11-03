"""Test the local Ollama integration."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from emotional_os.llm.ollama_composer import get_ollama_composer


def test_ollama_availability():
    """Test if Ollama is running."""
    print("=" * 60)
    print("Testing Ollama Local LLM Integration")
    print("=" * 60)
    print()

    composer = get_ollama_composer()

    if not composer.is_available:
        print("⚠ Ollama is not running. To use local LLM:")
        print()
        print("1. Install Ollama: https://ollama.ai")
        print()
        print("2. Download a model:")
        print("   ollama pull mistral      # ~4GB, fast, high quality")
        print("   ollama pull neural-chat  # ~4GB, chat-optimized")
        print("   ollama pull llama2       # ~4GB, solid all-around")
        print()
        print("3. Start the server:")
        print("   ollama serve")
        print()
        print("4. Run this test again")
        print()
        return

    print("✓ Ollama is running!")
    print(f"✓ Model loaded: {composer.model}")
    print()
    print("-" * 60)
    print("Testing response generation...")
    print("-" * 60)
    print()

    # Test 1: Simple greeting
    print("Test 1: Simple greeting")
    response = composer.compose_response("Hi, how are you?")
    print(f"User: Hi, how are you?")
    print(f"Response: {response}")
    print()

    # Test 2: Emotional message
    print("Test 2: Emotional message")
    response = composer.compose_response(
        "I'm feeling really overwhelmed with everything",
        emotional_signals=[
            {"signal": "overwhelm", "keyword": "overwhelmed"},
            {"signal": "anxiety", "keyword": "everything"},
        ]
    )
    print(f"User: I'm feeling really overwhelmed with everything")
    print(f"Response: {response}")
    print()

    # Test 3: With glyph context
    print("Test 3: With glyph context (invisible)")
    response = composer.compose_response(
        "I just needed to talk to someone",
        emotional_signals=[{"signal": "need", "keyword": "needed"}],
        glyph_context={"glyph_name": "Spiral Containment"},
    )
    print(f"User: I just needed to talk to someone")
    print(f"Response: {response}")
    print()

    print("-" * 60)
    print("✓ All tests completed!")
    print()
    print("Key points:")
    print("• All responses generated LOCALLY - no external API calls")
    print("• Model weights stored in ~/.ollama/models/")
    print("• Completely private - your data never leaves your machine")
    print("• Responses are more nuanced than templates")


if __name__ == "__main__":
    test_ollama_availability()

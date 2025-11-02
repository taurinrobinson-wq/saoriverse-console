#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python 2.7 compatible test for glyph evolution
"""

import datetime


def test_evolution_trigger():
    """Test if we can simulate evolution trigger"""
    print("=== Testing Evolution Trigger ===")

    # Simulate conversation count at 10 (should trigger evolution)
    conversation_count = 10
    evolution_frequency = 5

    should_evolve = (conversation_count % evolution_frequency == 0)
    print("Conversation count: " + str(conversation_count))
    print("Should evolve: " + str(should_evolve))

    if should_evolve:
        print("✅ Evolution should be triggered!")

        # Create a sample evolution result
        evolution_info = {
            'new_glyphs_count': 2,
            'new_glyphs': [
                {
                    'tag_name': 'test_mixed_anticipation',
                    'glyph': 'Ψ × Ω',
                    'description': 'Mixed excitement and anxiety'
                },
                {
                    'tag_name': 'test_hollow_familiarity',
                    'glyph': 'δ ÷ ε',
                    'description': 'Familiar yet foreign emotional state'
                }
            ]
        }

        # Create evolution message
        evolution_message = "🧬 **Evolution Triggered!** Generated " + str(evolution_info['new_glyphs_count']) + " new glyph(s):\n"
        for glyph in evolution_info['new_glyphs']:
            evolution_message += "• **" + glyph.get('tag_name', 'Unknown') + "** (" + glyph.get('glyph', 'N/A') + ")\n"

        print("\n=== Evolution Message ===")
        print(evolution_message)

        # Test message structure
        evolution_system_message = {
            'type': 'system',
            'content': evolution_message,
            'timestamp': datetime.datetime.now().isoformat(),
            'metadata': {'source': 'evolution_system', 'is_evolution': True}
        }

        print("\n=== Message Metadata ===")
        print("is_evolution: " + str(evolution_system_message['metadata']['is_evolution']))

        return evolution_system_message
    print("❌ Evolution should not trigger")
    return None

if __name__ == "__main__":
    result = test_evolution_trigger()
    if result:
        print("\n🎉 Evolution test successful!")
    else:
        print("\n❌ Evolution test failed")

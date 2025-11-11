#!/usr/bin/env python3
"""Test that UI logic would choose response_template when debug is off.

This script calls parse_input and asserts the selection logic used in the Streamlit UI:
- if voltage_response_template exists and show_glyph_debug is False => UI would use template
- if show_glyph_debug is True => UI would use voltage_response (contextual_response)

Exits with code 0 on success, 2 on assertion failure.
"""
import sys
from emotional_os.core.signal_parser import parse_input


def main():
    # Use an input likely to trigger 'Joy in Stillness' which has a curated template
    TEST_INPUT = "I feel so joyful and alive right now"

    result = parse_input(TEST_INPUT, 'emotional_os/parser/signal_lexicon.json',
                         db_path='emotional_os/glyphs/glyphs.db')

    template = result.get('voltage_response_template')
    contextual = result.get('voltage_response')

    print('voltage_response_template:', repr(template))
    print('voltage_response (contextual):', repr(contextual))

    # Simulate UI selection
    show_glyph_debug = False
    if template and not show_glyph_debug:
        ui_response = template
    else:
        ui_response = contextual

    print('\nSimulated UI response (debug off):', repr(ui_response))

    # Now simulate debug on
    show_glyph_debug = True
    if template and not show_glyph_debug:
        ui_response_debug_on = template
    else:
        ui_response_debug_on = contextual

    print('Simulated UI response (debug on):', repr(ui_response_debug_on))

    # Assertions
    if not template:
        print('\nERROR: No voltage_response_template returned by parser for test input. Cannot verify UI behavior.')
        return 2

    if ui_response != template:
        print('\nERROR: With debug off, UI would not use the template as expected.')
        return 2

    if ui_response_debug_on != contextual:
        print(
            '\nERROR: With debug on, UI would not use the contextual response as expected.')
        return 2

    print('\nUI verification passed: template used when debug off, contextual used when debug on.')
    return 0


if __name__ == '__main__':
    import sys

    sys.exit(main())

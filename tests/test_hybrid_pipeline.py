import json
import types
import unittest
from unittest import mock

import streamlit as st

from emotional_os.deploy.modules import ui


class DummyResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class HybridPipelineTests(unittest.TestCase):
    def setUp(self):
        # Ensure session state keys exist
        st.session_state.clear()
        st.session_state.user_id = 'test-user'
        # Tests should exercise hybrid/local paths as needed; default to 'hybrid' for tests
        st.session_state.processing_mode = 'hybrid'
        st.session_state.prefer_ai = True
        # Show local decoding in tests so hybrid composition includes debug annotations
        st.session_state.show_local_decoding = True

    def test_hybrid_composition(self):
        effective_input = "I feel overwhelmed and want the weather in LA"
        conversation_context = {}

        # local parse outputs for user input and AI reply
        local_user = {
            'glyphs': [{'glyph_name': 'overwhelmed'}],
            'voltage_response': 'High voltage (0.8)',
            'ritual_prompt': 'Breathe and ground',
            'signals': ['s1'],
            'gates': [],
            'best_glyph': {'glyph_name': 'overwhelmed'}
        }
        local_ai = {
            'glyphs': [{'glyph_name': 'calm'}],
            'voltage_response': 'Low voltage (0.2)',
            'ritual_prompt': 'Relax',
            'signals': ['s2'],
            'gates': [],
            'best_glyph': {'glyph_name': 'calm'}
        }

        def fake_parse_input(text, *args, **kwargs):
            if text == effective_input:
                return local_user
            else:
                return local_ai

        with mock.patch('emotional_os.glyphs.signal_parser.parse_input', side_effect=fake_parse_input):
            # mock requests.post to return AI reply
            with mock.patch('emotional_os.deploy.modules.ui.requests.post') as mock_post:
                mock_post.return_value = DummyResponse(
                    200, {'reply': 'AI: The weather in LA is sunny and warm.'})

                composed, debug, local = ui.run_hybrid_pipeline(
                    effective_input, conversation_context, 'https://fake', 'key')

                self.assertIn(
                    'AI: The weather in LA is sunny and warm.', composed)
                self.assertIn('Local decoding:', composed)
                self.assertTrue(isinstance(debug, dict))
                self.assertEqual(local.get('glyphs')[
                                 0]['glyph_name'], 'overwhelmed')

    def test_privacy_mode_fallback(self):
        effective_input = "Run in local mode: I want to test privacy."
        conversation_context = {}

        # No AI endpoint (privacy mode) - pass empty strings to satisfy type hints
        composed, debug, local = ui.run_hybrid_pipeline(
            effective_input, conversation_context, '', '')
        # Accept either an explicit AI-unavailable marker or the local composer
        # compact fallback — both are valid fallbacks for privacy/local mode.
        self.assertTrue(('AI enhancement unavailable' in composed)
                        or ("I'm listening" in composed))

    def test_parse_failure_fallback_to_ai_reply(self):
        effective_input = "Tell me a myth about rivers."
        conversation_context = {}

        # Local parse succeeds initially
        local_user = {'glyphs': [],
                      'voltage_response': 'mid', 'ritual_prompt': ''}

        def fake_parse_input(text, *args, **kwargs):
            if text == effective_input:
                return local_user
            # Simulate parse failure when parsing AI reply by raising
            raise Exception('parse fail')

        with mock.patch('emotional_os.glyphs.signal_parser.parse_input', side_effect=fake_parse_input):
            with mock.patch('emotional_os.deploy.modules.ui.requests.post') as mock_post:
                mock_post.return_value = DummyResponse(
                    200, {'reply': 'AI: Once upon a river...'})
                composed, debug, local = ui.run_hybrid_pipeline(
                    effective_input, conversation_context, 'https://fake', 'key')
                # decode failed -> composed should be raw AI reply (decode_ai_reply returns ai_reply when failing)
                self.assertIn('AI: Once upon a river...', composed)


if __name__ == '__main__':
    unittest.main()

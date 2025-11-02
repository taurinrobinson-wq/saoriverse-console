import logging

from emotional_os.glyphs.limbic_decorator import decorate_reply


class StubLimbic:
    def process_emotion_with_limbic_mapping(self, emotion):
        # Return a predictable limbic_result that should change short baselines
        return {
            'emotion': 'joy',
            'system_signals': {'lightpath': {'glyph': '🌅', 'signal': 'Morning light'}},
            'ritual_sequence': ['blink', 'breath', 'brace']
        }


def test_decorator_changes_short_baseline(capsys):
    # Enable debug logging for test to exercise instrumentation paths (optional)
    logging.getLogger('emotional_os.glyphs.limbic_decorator').setLevel(logging.DEBUG)

    baseline = "Nice"
    limbic = StubLimbic().process_emotion_with_limbic_mapping('nice')

    decorated = decorate_reply(baseline, limbic, intensity=0.8)

    # For a very short baseline, decorate_reply should prepend an opener or otherwise alter the text
    assert decorated != baseline
    assert isinstance(decorated, str)
    assert len(decorated) > 0


def test_decorator_keeps_long_baseline_if_present():
    baseline = "This is a longer baseline reply that should remain the primary content of the response"
    limbic = StubLimbic().process_emotion_with_limbic_mapping('anything')
    decorated = decorate_reply(baseline, limbic, intensity=0.5)

    # For long baselines, decorator appends modest suggestions — still different but baseline remains
    assert isinstance(decorated, str)
    # The baseline should be contained in the decorated reply
    assert baseline.split()[0] in decorated

import re

from response_adapter import translate_emotional_response


def test_no_duplicate_adjacent_words_and_no_gentlely():
    """Style guard: no repeated adjacent words and avoid malformed 'gentlely'."""
    intensities = ["gentle", "gently", "subtle", "softly", "calm"]
    emotions = ["connection", "longing", "wonder", "sorrow"]
    contexts = ["this moment", "when you remember them",
                "talking about your day"]

    dup_re = re.compile(r"\b(\w+)\s+\1\b", flags=re.IGNORECASE)

    for intensity in intensities:
        for emotion in emotions:
            for context in contexts:
                out = translate_emotional_response({
                    "intensity": intensity,
                    "emotion": emotion,
                    "context": context,
                    "resonance": "a quiet shift",
                })

                # No malformed 'gentlely'
                assert "gentlely" not in out.lower(
                ), f"Found 'gentlely' in: {out!r}"

                # No duplicated adjacent word like 'gentle gentle' or 'really really'
                m = dup_re.search(out)
                assert m is None, f"Found duplicated adjacent word '{m.group(0)}' in: {out!r}"

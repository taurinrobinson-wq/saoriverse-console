import importlib.util
import os
import re
import sys

from main_response_engine import process_user_input
from response_adapter import generate_response_from_glyphs

# Ensure repo root is importable
HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


# Conversation (USER lines only) taken from the transcript supplied by the user.
USER_TURNS = [
    "These past few days have been heavy. Winston’s been struggling since the divorce, Jennifer and I share weekends now, but he recently told her he wants to live with me and keeps saying he hates her and Michelle. I watch them at Michelle’s place since it has more space, but I’m just renting a room right now. It’s not really set up for him, just one bed, and it feels awkward.",
    "Thank you for that. Sometimes I just don't know what to do. I want to support him, but I'm in a transition period myself after the divorce. I just started a committed relationship with my girlfriend, Cindy, and she's been wonderful. We started dating in August and have been really bonded.",
    "You say that but I don't know if I have the emotional fortitude to try to hold them both without segmenting my time as it has been with me having at least sunday afternoon and monday through thursday to spend time with her",
    "Yeah I have considered it. The difficulty is translating that into a way that he can comprehend",
    "So it also presents a bit of tension as well, because I have Cindy come to my place sometimes and spend the night, or I spend the night at her apartment. There would be no time for me to really see her if I am with him. He would basically be with me whenever he's not in school which would be all of the times that I could spend time with Cindy. It’s not like I have multiple rooms where I can be with her and he can be in a separate space. And it's not like he would really be able to put up with the fact of not being the center of attention lately.",
    "I have considered it. The difficulty is translating that into a way that he can comprehend",
    "So it also presents a bit of tension as well, because I have Cindy come to my place sometimes and spend the night, or I spend the night at her apartment. There would be no time for me to really see her if I am with him. He would basically be with me whenever he's not in school which would be all of the times that I could spend time with Cindy. It's not like I have multiple rooms where I can be with her and he can be in a separate space. And it's not like he would really be able to put up with the fact of not being the center of attention lately.",
]


def _contains_internal_glyph_labels(text: str) -> bool:
    """Detect likely internal glyph labels or 'resonant glyph' lines.

    Heuristics:
    - presence of the phrase 'Resonant Glyph' or 'Local decoding'
    - presence of visually-odd tokens (contain non-alphanumeric like 'Ω')
    - tokens that contain a Greek letter or a high-frequency uppercase run with non-proper-name shape
    """
    if not text:
        return False
    if "Resonant Glyph" in text or "Local decoding" in text:
        return True
    # Greek letter detection
    if re.search(r"[\u0370-\u03FF]", text):
        return True
    # detect tokens with a mix of uppercase + punctuation uncommon in normal prose
    for tok in re.findall(r"\S+", text):
        # tokens with unusual characters like 'VELΩNIX' or long ALLCAPS sequences
        if re.search(r"[A-Z]{3,}[A-Z0-9_]*", tok) and not re.match(r"[A-Z][a-z]+", tok):
            return True
    return False


def test_replay_conversation_no_glyph_leakage_and_concise_responses():
    """Replay user turns and assert responses do not leak glyph labels and stay concise.

    The test injects an intentionally-odd glyph tag (e.g. 'VELΩNIX') into `local_analysis`
    to simulate the environment where internal glyphs were previously surfaced in the AI output.
    The assertions ensure the user-facing reply does not echo those internal labels and
    that the adapted (scaffolded) response remains reasonably short.
    """
    odd_tag = "VELΩNIX"
    # We'll inject a high-confidence odd glyph into local_analysis for each turn
    for turn in USER_TURNS:
        ctx = {
            "local_analysis": {
                "glyph_overlays_info": [
                    {"tag": odd_tag, "confidence": 0.95},
                    {"tag": "sadness", "confidence": 0.6},
                ]
            }
        }

        resp = process_user_input(turn, ctx)
        assert isinstance(resp, str) and resp.strip() != ""

        # Split adapted portion from raw (main_response_engine returns raw + '\n\n' + adapted)
        parts = resp.split("\n\n")
        adapted = parts[-1] if parts else resp

        # adapted response should not leak internal glyph labels or 'Resonant Glyph' lines
        assert not _contains_internal_glyph_labels(adapted), f"Adapted response leaked glyph labels: {adapted}"

        # also ensure the full response isn't extremely long (sanity cap to encourage concise replies)
        assert len(resp) <= 800, f"Response too long ({len(resp)} chars): {resp[:200]}..."


def test_generate_response_from_weird_glyph_tag_is_safe():
    """Directly test the adapter when given a strange glyph tag; response must not echo the tag."""
    weird_tag = "VELΩNIX"
    out = generate_response_from_glyphs({"glyph_overlays_info": [{"tag": weird_tag, "confidence": 0.95}]})
    assert isinstance(out, str) and out.strip() != ""
    assert weird_tag not in out
    assert "Resonant Glyph" not in out and "Local decoding" not in out

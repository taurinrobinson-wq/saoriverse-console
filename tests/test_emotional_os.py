import re

from src.emotional_os.pun_interjector import PunInterjector
from src.emotional_os.mutual_joy_handler import MutualJoyHandler, EXCL_TEMPLATES
from src.emotional_os.integrator import try_pun, try_mutual_joy


def test_pun_interjector_triggers_on_wordplay():
    pi = PunInterjector(min_turns_between_puns=0)
    context = {
        "user_emotion": "neutral",
        "contains_wordplay": True,
        "safety_tier": 1,
        "recent_pun_turns": 999,
    }
    pun = pi.compose_pun(context)
    assert pun is not None
    rendered = pi.render(pun)
    assert isinstance(rendered, str) and len(rendered) > 0


def test_try_pun_returns_empty_when_disabled():
    # safety tier blocks puns
    context = {"safety_tier": 3, "recent_pun_turns": 999}
    out = try_pun(context)
    assert out == ""


def test_mutual_joy_exclamation_decision():
    mj = MutualJoyHandler(min_turns_between_exclaims=0)
    context = {
        "user_emotion": "lift",
        "safety_tier": 1,
        "long_arc": True,
        "user_words": "tbh it was kind of amazing",
        "turns_since_exclaim": 999,
    }
    assert mj.should_use_exclamation(context) is True
    template = mj.choose_template(context)
    # template should be one of exclamation or period templates; when exclaim allowed,
    # we expect one of the exclamation templates to be possible
    assert isinstance(template, str) and len(template) > 0
    # if exclamation allowed, ensure at least that template is non-empty


def test_try_mutual_joy_returns_string():
    context = {
        "user_emotion": "lift",
        "safety_tier": 1,
        "long_arc": True,
        "user_words": "i'm so happy",
        "turns_since_exclaim": 999,
    }
    out = try_mutual_joy(context)
    assert isinstance(out, str) and len(out) > 0

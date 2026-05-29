"""Lightweight text interpreter adapted from repo keyword models."""

from __future__ import annotations

import re
from typing import Dict, List, Set

from TheModel.core.models import Interpretation, clamp_01


TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z\-']+")
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from", "how", "i", "if",
    "in", "is", "it", "me", "my", "of", "on", "or", "so", "that", "the", "their", "them", "they",
    "this", "to", "was", "we", "with", "you", "your",
}

FEATURE_KEYWORDS: Dict[str, Set[str]] = {
    "social_threat": {"rejected", "abandoned", "ignored", "alone", "excluded", "betrayed", "ghosted"},
    "self_blame": {"fault", "failed", "ashamed", "guilty", "mistake", "regret", "inadequate"},
    "other_blame": {"unfair", "selfish", "hurtful", "wrong", "blame", "ignored"},
    "care": {"understand", "care", "support", "listen", "help", "compassion", "empathy"},
    "rational_control": {"fine", "normal", "logic", "control", "overreacting", "dramatic", "reframe"},
    "identity_pressure": {"worth", "identity", "who", "reputation", "challenge", "questioned"},
    "curiosity": {"why", "how", "learn", "mean", "define", "curious", "understand"},
    "loss": {"lost", "lose", "gone", "ended", "missed", "opportunity", "grief"},
}


def tokenize(text: str) -> List[str]:
    return [match.group(0).lower() for match in TOKEN_PATTERN.finditer(text)]


def extract_features(tokens: List[str]) -> Dict[str, float]:
    token_count = max(1, len(tokens))
    features: Dict[str, float] = {}
    token_set = set(tokens)
    for name, keywords in FEATURE_KEYWORDS.items():
        count = sum(1 for token in token_set if token in keywords)
        features[name] = clamp_01((count / token_count) * 6.0)
    return features


def interpret_text(text: str, known_terms: Set[str]) -> Interpretation:
    tokens = tokenize(text)
    features = extract_features(tokens)
    unknown_terms: List[str] = []
    for token in tokens:
        if token in STOPWORDS or token in known_terms or len(token) < 4:
            continue
        if token not in unknown_terms:
            unknown_terms.append(token)
    return Interpretation(features=features, tokens=tokens, unknown_terms=unknown_terms[:5])
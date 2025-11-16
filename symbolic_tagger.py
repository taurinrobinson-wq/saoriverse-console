"""Assign symbolic tags to user input based on regex/phrase patterns.

Exports:
- tag_input(user_input: str) -> list[str]

This is intentionally simple and regex-driven so it is easy to tune and
auditable by non-technical maintainers.
"""
import re
from difflib import SequenceMatcher
from typing import List, Tuple

# Patterns (regex) for common symbolic tags

# Initiatory: new meetings, openings, sparks, noticing being seen
initiatory_patterns = [
    r"\bI just met\b",
    r"\bI met someone\b",
    r"\bnew connection\b",
    r"\bfirst conversation\b",
    r"\bsomeone who (really )?sees me\b",
    r"\bfelt seen\b",
    r"\bthey see me\b",
    r"\bspark\b",
    r"\bsomething opened\b",
    r"\bthis feels new\b",
]

# Synonym groups: multi-word variants that are emotionally equivalent.
# These are used for fuzzy multi-word matching in addition to regex.
_SYNONYM_GROUPS: List[Tuple[str, List[str]]] = [
    ("felt_seen", [
        "felt seen",
        "they see me",
        "i feel seen",
        "i feel seen by",
        "i feel overwhelmed",
        "i feel swamped",
        "i feel drowning",
        "i feel underwater",
    ]),
    ("new_connection", [
        "new connection",
        "first conversation",
        "just met someone",
        "met someone new",
    ]),
    ("opened", [
        "something opened",
        "what's opening",
        "an opening opened",
        "opening in me",
    ]),
    ("containment", [
        "can you help me hold this",
        "keep this close",
        "don't let this slip away",
        "i need to save this moment",
        "this feels precious",
        "keep this safe",
        "i want to remember",
        "please don't let me forget",
        "this matters to me",
    ]),
    ("legacy_marker", [
        "this left a mark",
        "this became part of me",
        "i carry this forward",
        "this is etched in me",
        "this belongs to my lineage",
        "this changed me",
        "i want to be remembered",
        "i'll never forget",
        "this shaped who i am",
        "this is part of my story",
    ]),
    ("voltage", [
        "i feel flooded",
        "i'm buzzing inside",
        "this hit me hard",
        "i'm lit up",
        "i'm surging with feeling",
        "i feel electric",
        "i'm overwhelmed and excited",
    ]),
]

# Anchoring: ongoing processes, long-term work, relational labor
anchoring_patterns = [
    r"\bworking through\b",
    r"\bwe'?ve been talking\b",
    r"\bwe've been talking\b",
    r"\bfor a while\b",
    r"\bongoing\b",
    r"\bthis relationship has been\b",
    r"\bwe've been together\b",
]

# Voltage surges: high arousal, overwhelm, racing heart, excitement
voltage_surge_patterns = [
    r"\boverwhelmed\b",
    r"\bI'm? spinning\b",
    r"\btoo much\b",
    r"\bcan't breathe\b",
    r"\bheart (is )?racing\b",
    r"\bso excited\b",
    r"\bso happy\b",
    r"\breally excited\b",
]

# Additional voltage surges from user seed list
voltage_surge_patterns += [
    r"\beverything just changed\b",
    r"\bmy heart is racing\b",
    r"\bi can'?t breathe\b",
    r"\bi feel electric\b",
    r"\bi'?m overwhelmed and excited\b",
]

# Containment: explicit requests for holding, slowing, preserving
containment_patterns = [
    r"\bhelp me hold\b",
    r"\bcan you hold\b",
    r"\bhelp me hold this\b",
    r"\bI want to preserve this moment\b",
    r"\bslow this down\b",
    r"\bhold this\b",
    r"\bcan you help me hold this\b",
]

# Additional containment regexes from user seed list
containment_patterns += [
    r"\bcan you hold this\b",
    r"\bkeep this safe\b",
    r"\bi want to remember\b",
    r"\bplease don'?t let me forget\b",
    r"\bthis matters to me\b",
]

legacy_patterns = [
    r"\bimportant\b",
    r"\bremember\b",
    r"\bturning point\b",
]

# Additional legacy regexes from user seed list
legacy_patterns += [
    r"\bi want to be remembered\b",
    r"\bthis changed me\b",
    r"\bi'?ll never forget\b",
    r"\bthis shaped who i am\b",
    r"\bthis is part of my story\b",
]


def tag_input(user_input: str) -> List[str]:
    """Return symbolic tags matched in `user_input`.

    Tags include: 'initiatory_signal', 'anchoring_signal', 'voltage_surge',
    'containment_request', 'legacy_marker'. Defaults to
    'anchoring_signal' if nothing matches.
    """
    text = user_input or ""
    tags: List[str] = []

    # Check each category and append tags for each match so downstream
    # components can reason about multiple simultaneous cues.
    if any(re.search(p, text, re.IGNORECASE) for p in initiatory_patterns):
        tags.append("initiatory_signal")

    if any(re.search(p, text, re.IGNORECASE) for p in anchoring_patterns):
        tags.append("anchoring_signal")

    if any(re.search(p, text, re.IGNORECASE) for p in voltage_surge_patterns):
        tags.append("voltage_surge")

    if any(re.search(p, text, re.IGNORECASE) for p in containment_patterns):
        tags.append("containment_request")

    if any(re.search(p, text, re.IGNORECASE) for p in legacy_patterns):
        tags.append("legacy_marker")

    # Fuzzy multi-word matching: check synonym groups with SequenceMatcher.
    # This helps catch paraphrases and near-matches like "i feel so seen".
    def _fuzzy_group_match(text: str, group_phrases: List[str], thresh: float = 0.73) -> bool:
        for phrase in group_phrases:
            # Use ratio on the phrase vs. any sliding window of same token length
            # Build candidate windows of roughly the phrase length to compare similarity
            p_tokens = phrase.split()
            p_len = max(3, len(p_tokens))
            tokens = text.split()
            for i in range(max(1, len(tokens) - p_len + 1)):
                window = " ".join(tokens[i:i + p_len])
                score = SequenceMatcher(None, window, phrase).ratio()
                if score >= thresh:
                    return True
        return False

    # Map synonym group names to tags so fuzzy matches can produce appropriate
    # symbolic tags (not all synonym groups are initiatory).
    group_tag_map = {
        "felt_seen": "initiatory_signal",
        "opened": "initiatory_signal",
        "new_connection": "initiatory_signal",
        "containment": "containment_request",
        "legacy_marker": "legacy_marker",
        "voltage": "voltage_surge",
    }

    for name, phrases in _SYNONYM_GROUPS:
        if _fuzzy_group_match(text, phrases, thresh=0.73):
            tag = group_tag_map.get(name)
            if tag and tag not in tags:
                tags.append(tag)

    if not tags:
        tags.append("anchoring_signal")

    return tags


def tag_input_with_diagnostics(user_input: str, fuzzy_thresh: float = 0.73) -> dict:
    """Return tags plus diagnostic matches for auditing.

    Returns dict with keys:
    - tags: list[str]
    - matches: list[dict] where each dict contains:
      - category: str (initiatory|anchoring|voltage|containment|legacy|synonym_group)
      - pattern: str (the regex or group phrase)
      - match_type: str ('regex' or 'fuzzy')
      - score: float (1.0 for regex, ratio for fuzzy)
    """
    text = user_input or ""
    tags = []
    matches = []

    def _add_match(category: str, pattern: str, match_type: str, score: float, tag: str):
        matches.append({
            "category": category,
            "pattern": pattern,
            "match_type": match_type,
            "score": float(score),
        })
        if tag not in tags:
            tags.append(tag)

    # Regex categories
    for p in initiatory_patterns:
        if re.search(p, text, re.IGNORECASE):
            _add_match("initiatory", p, "regex", 1.0, "initiatory_signal")

    for p in anchoring_patterns:
        if re.search(p, text, re.IGNORECASE):
            _add_match("anchoring", p, "regex", 1.0, "anchoring_signal")

    for p in voltage_surge_patterns:
        if re.search(p, text, re.IGNORECASE):
            _add_match("voltage", p, "regex", 1.0, "voltage_surge")

    for p in containment_patterns:
        if re.search(p, text, re.IGNORECASE):
            _add_match("containment", p, "regex", 1.0, "containment_request")

    for p in legacy_patterns:
        if re.search(p, text, re.IGNORECASE):
            _add_match("legacy", p, "regex", 1.0, "legacy_marker")

    # Fuzzy synonym groups
    def _fuzzy_group_match_with_score(text: str, group_phrases: List[str], thresh: float):
        best_score = 0.0
        best_phrase = None
        for phrase in group_phrases:
            p_tokens = phrase.split()
            p_len = max(3, len(p_tokens))
            tokens = text.split()
            for i in range(max(1, len(tokens) - p_len + 1)):
                window = " ".join(tokens[i:i + p_len])
                score = SequenceMatcher(None, window, phrase).ratio()
                if score > best_score:
                    best_score = score
                    best_phrase = phrase
        return (best_score >= thresh, best_score, best_phrase)

    # Map synonym group names to tags for diagnostics as well
    group_tag_map = {
        "felt_seen": "initiatory_signal",
        "opened": "initiatory_signal",
        "new_connection": "initiatory_signal",
        "containment": "containment_request",
        "legacy_marker": "legacy_marker",
        "voltage": "voltage_surge",
    }

    for name, phrases in _SYNONYM_GROUPS:
        matched, score, phrase = _fuzzy_group_match_with_score(
            text, phrases, fuzzy_thresh)
        if matched and phrase:
            tag = group_tag_map.get(name, "initiatory_signal")
            _add_match("synonym_group", phrase, "fuzzy", score, tag)

    if not tags:
        tags.append("anchoring_signal")

    return {"tags": tags, "matches": matches}

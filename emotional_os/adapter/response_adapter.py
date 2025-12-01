#!/usr/bin/env python3
"""
Response Adapter

Translate internal system outputs (glyphs, tags, voltages) into
plain-language summaries and short snippet phrases for the composer.

This module MUST NOT expose internal glyph names or system tokens
in user-facing text.
"""
import re
from typing import Any, Dict, List, Optional

STOPWORDS = {
    "in",
    "of",
    "and",
    "the",
    "a",
    "an",
    "to",
    "for",
    "with",
    "on",
    "at",
    "by",
    "from",
    "is",
    "are",
    "that",
    "this",
    "it",
    "as",
    "be",
    "was",
    "were",
}


def _clean_text(s: str) -> str:
    if not s:
        return ""
    tokens = [t.lower() for t in re.findall(r"[a-zA-Z]+", s)]
    meaningful = [t for t in tokens if t and t not in STOPWORDS]
    return " ".join(meaningful)


def _map_glyph_to_phrase(glyph: Dict[str, Any]) -> str:
    """Create a plain-language fragment describing a glyph without using its name.

    Heuristics (in order):
    - use `description` if present (cleaned)
    - otherwise use activation_signals mapped to words
    - otherwise derive from glyph metadata tokens
    - fallback to generic wording
    """
    desc = glyph.get("description") or ""
    if desc and len(desc.strip()) > 3:
        return _clean_text(desc)

    acts = glyph.get("activation_signals") or []
    parts = []
    if isinstance(acts, list):
        for a in acts:
            if isinstance(a, str):
                parts.extend([t for t in re.split(r"[;,\s]+", a) if t])
    elif isinstance(acts, str):
        parts.extend([t for t in re.split(r"[;,\s]+", acts) if t])

    if parts:
        cleaned = [_clean_text(p) for p in parts if _clean_text(p)]
        if cleaned:
            return ", ".join(cleaned[:3])

    name = glyph.get("glyph_name") or glyph.get("name") or ""
    name_tokens = _clean_text(name)
    if name_tokens:
        # convert tokens like "recursive ache" -> "a recurring ache"
        name_tokens = name_tokens.replace("recursive", "recurring")
        return name_tokens

    # Last resort
    return "a feeling that shows up strongly"


def translate_system_output(
    system_output: Dict[str, Any], top_n: int = 5, user_context: Optional[Dict] = None
) -> Dict[str, Any]:
    """Translate raw system output into user-facing pieces.

    Returns:
      {
        'summary': str,
        'snippets': [str],
        'tone': 'initiatory'|'archetypal'|'neutral',
        'invitation': str
      }
    """
    glyphs = system_output.get("glyphs") or []
    glyphs = glyphs[:top_n]

    # Build snippets
    snippets: List[str] = []
    for g in glyphs:
        frag = _map_glyph_to_phrase(g)
        if frag and frag not in snippets:
            # short, friendly phrasing
            snippets.append(f"I notice {frag}.")
        if len(snippets) >= top_n:
            break

    # Determine summary from the top glyph or from extracted emotions
    summary = None
    if glyphs:
        top = glyphs[0]
        summary = _map_glyph_to_phrase(top)

    # Tone heuristic: prefer provided phase tag if present
    tone = system_output.get("phase") or "neutral"
    if tone not in ("initiatory", "archetypal", "neutral"):
        tone = "neutral"

    # Invitation templates
    if tone == "initiatory":
        invitation = "Would you like to explore that a little more?"
    elif tone == "archetypal":
        invitation = "Would you like to hold this and reflect together?"
    else:
        invitation = "Does any of that resonate for you?"

    # Fallback summary
    if not summary:
        summary = "something that matters to you"

    return {
        "summary": summary,
        "snippets": snippets or [f"I notice {summary}."],
        "tone": tone,
        "invitation": invitation,
    }

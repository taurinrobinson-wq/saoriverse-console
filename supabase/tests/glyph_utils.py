"""Utility helpers for testing glyph parsing edge cases.

This mirrors the sanitizer/validation logic used in the TypeScript edge functions
so tests can assert expected behavior without calling external LLMs.
"""

from typing import Any, Dict, List


def normalize_glyphs(raw: Any) -> List[Dict[str, Any]]:
    """Normalize and validate a glyph list produced by an extractor.

    Rules (keeps behavior aligned with server-side):
    - Input may be a dict with key 'glyphs' or a raw list.
    - Each glyph must have a 'name' string; truncate to 80 chars.
    - 'description' is optional; coerce to string and truncate to 300 chars.
    - 'depth' if present should be coerced to int and clamped between 1 and 5.
    - Ignore entries without a valid name.
    """
    out = []
    try:
        glyphs = []
        if isinstance(raw, dict) and "glyphs" in raw:
            glyphs = raw.get("glyphs") or []
        elif isinstance(raw, list):
            glyphs = raw
        else:
            # Unexpected shape
            return []

        for g in glyphs:
            try:
                name = g.get("name") if isinstance(g, dict) else None
                if not name or not isinstance(name, str):
                    continue
                name = name.strip()[:80]

                description = ""
                if isinstance(g.get("description"), str):
                    description = g.get("description")[:300]
                elif g.get("description") is not None:
                    description = str(g.get("description"))[:300]

                depth = None
                if "depth" in g:
                    try:
                        depth = int(g.get("depth"))
                        if depth < 1:
                            depth = 1
                        if depth > 5:
                            depth = 5
                    except Exception:
                        depth = None

                normalized = {
                    "name": name,
                    "description": description,
                }
                if depth is not None:
                    normalized["depth"] = depth

                # optional fields
                for opt in ("response_layer", "glyph_type", "symbolic_pairing"):
                    if isinstance(g.get(opt), str):
                        normalized[opt] = g.get(opt)[:80]

                out.append(normalized)
            except Exception:
                # tolerate individual glyph failures
                continue

        return out
    except Exception:
        return []


def is_valid_glyph_shape(obj: Any) -> bool:
    """Quick check whether an object looks like a glyph list or glyph object."""
    if isinstance(obj, dict) and "glyphs" in obj:
        return isinstance(obj["glyphs"], list)
    if isinstance(obj, list):
        return all(isinstance(i, dict) for i in obj)
    return False

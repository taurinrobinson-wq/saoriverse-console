"""
SVG Loading and Caching Utility.

Handles loading SVG files from static directories with in-memory caching
to avoid repeated disk reads. Sanitizes XML declarations and DOCTYPE.
"""

import os
import logging

logger = logging.getLogger(__name__)

# Simple in-memory cache for inline SVGs
_SVG_CACHE = {}


def load_svg(filename: str) -> str:
    """Load an SVG file from the static graphics folder with caching.

    Attempts to load from package-local path first, then repository root.
    Sanitizes XML declarations and DOCTYPE. Returns empty string on failure.

    Args:
        filename: Name of SVG file in static/graphics/ directory

    Returns:
        SVG markup string, or empty string if file cannot be read
    """
    if filename in _SVG_CACHE:
        return _SVG_CACHE[filename]

    # Try package-local graphics folder first, then repo-root static/graphics
    pkg_path = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                            "static", "graphics", filename)
    repo_path = os.path.join("static", "graphics", filename)
    tried_path = None

    try:
        # Pick the first existing candidate path
        if os.path.exists(pkg_path):
            tried_path = pkg_path
        elif os.path.exists(repo_path):
            tried_path = repo_path
        else:
            tried_path = pkg_path  # will raise when attempting to open

        # Read the SVG file and sanitize/remove XML declaration or DOCTYPE
        with open(tried_path, "r", encoding="utf-8") as f:
            svg = f.read()

        svg = _sanitize_svg(svg)
        _SVG_CACHE[filename] = svg

    except Exception as e:
        logger.debug(f"Could not load SVG {filename}: {e}")
        _SVG_CACHE[filename] = ""

    return _SVG_CACHE.get(filename, "")


def _sanitize_svg(svg: str) -> str:
    """Remove XML declarations and DOCTYPE from SVG content.

    Args:
        svg: Raw SVG markup

    Returns:
        Sanitized SVG markup
    """
    if svg.lstrip().startswith("<?xml"):
        svg = "\n".join(svg.splitlines()[1:])

    if "<!DOCTYPE" in svg:
        parts = svg.split("<!DOCTYPE")
        if len(parts) > 1 and ">" in parts[1]:
            svg = parts[0] + parts[1].split(">", 1)[1]

    return svg


def get_cached_svg(filename: str) -> str:
    """Query SVG from cache without attempting to load from disk.

    Args:
        filename: Name of SVG file

    Returns:
        Cached SVG markup or empty string if not cached
    """
    return _SVG_CACHE.get(filename, "")


def clear_svg_cache() -> None:
    """Clear the SVG cache to free memory."""
    global _SVG_CACHE
    _SVG_CACHE.clear()


def get_cache_stats() -> dict:
    """Get cache statistics for debugging.

    Returns:
        Dictionary with cache size and file count
    """
    return {
        "cached_files": len(_SVG_CACHE),
        "cache_size_bytes": sum(len(v) for v in _SVG_CACHE.values()),
    }

"""
Utility modules for UI components.

Provides SVG loading, CSS injection, and styling utilities.
"""

from .svg_loader import load_svg, get_cached_svg, clear_svg_cache
from .css_injector import inject_css, inject_inline_style
from .styling_utils import (
    inject_defensive_scripts,
    inject_error_overlay,
    inject_container_styles,
    inject_splash_css,
    inject_svg_styling,
    inject_sidebar_constraints,
)

__all__ = [
    "load_svg",
    "get_cached_svg",
    "clear_svg_cache",
    "inject_css",
    "inject_inline_style",
    "inject_defensive_scripts",
    "inject_error_overlay",
    "inject_container_styles",
    "inject_splash_css",
    "inject_svg_styling",
    "inject_sidebar_constraints",
]

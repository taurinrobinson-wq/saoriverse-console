"""
CSS Injection Utility.

Handles CSS file injection, @import inlining, and inline style blocks.
Used for theme management and DOM styling adjustments.
"""

import os
import json
import re
import logging
import streamlit as st

logger = logging.getLogger(__name__)


def inject_css(css_path: str) -> None:
    """Inject a CSS file into the Streamlit app.

    Attempts to read CSS from package-local path first, then falls back
    to repository root. Inlines @import rules to avoid relative import issues.

    Args:
        css_path: Path to CSS file (relative or absolute)
    """
    try:
        # Try package-local path first, then repo-root path
        pkg_path = os.path.join(os.path.dirname(__file__), "..", css_path)
        repo_path = css_path
        chosen = None

        if os.path.exists(pkg_path):
            chosen = pkg_path
        elif os.path.exists(repo_path):
            chosen = repo_path

        if not chosen:
            logger.debug(f"CSS file not found: {css_path}")
            return

        with open(chosen, "r", encoding="utf-8") as f:
            css = f.read()

        # Inline any @import rules that reference local CSS files
        css = _inline_imports(chosen, css)

        # Inject with ID so we can replace/update it later
        _inject_safe_style_block(css)

    except Exception as e:
        logger.debug(f"Error injecting CSS: {e}")


def _inline_imports(base_path: str, css_text: str) -> str:
    """Inline @import url() rules that reference local files.

    Args:
        base_path: Base directory for resolving relative imports
        css_text: CSS content with @import rules

    Returns:
        CSS with @import rules replaced by file contents
    """
    def _repl(m):
        imp = m.group(1).strip("\"'")
        # Resolve relative to base_path
        base_dir = os.path.dirname(base_path)
        candidate = os.path.join(base_dir, imp)

        if os.path.exists(candidate):
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    return "\n" + f.read() + "\n"
            except Exception:
                return ""

        # Try repo-root fallback
        if os.path.exists(imp):
            try:
                with open(imp, "r", encoding="utf-8") as f:
                    return "\n" + f.read() + "\n"
            except Exception:
                return ""

        return ""

    return re.sub(r"@import\s+url\(['\"]?(.*?)['\"]?\);", _repl, css_text)


def _inject_safe_style_block(css: str) -> None:
    """Inject CSS safely using a script that replaces or appends a style element.

    Uses json.dumps to safely encode CSS and avoids DOM-shape races during updates.

    Args:
        css: CSS content to inject
    """
    try:
        # Use json.dumps to safely encode the CSS into a JS string literal
        css_js = json.dumps(css)
        safe_block = (
            "<script>\n"
            "(function(){\n"
            "  try{\n"
            "    var css = " + css_js + ";\n"
            "    var existing = document.getElementById('fp-theme-css');\n"
            "    if(existing){\n"
            "      existing.textContent = css;\n"
            "    } else {\n"
            "      var s = document.createElement('style');\n"
            "      s.id = 'fp-theme-css';\n"
            "      s.textContent = css;\n"
            "      (document.head || document.documentElement).appendChild(s);\n"
            "    }\n"
            "  }catch(e){console.warn('fp-theme-css inject failed', e);}\n"
            "})();\n"
            "</script>"
        )
        st.markdown(safe_block, unsafe_allow_html=True)

    except Exception as e:
        logger.debug(f"Error injecting CSS block: {e}")
        # Fallback to simple style injection
        try:
            safe_block = f'<style id="fp-theme-css">\n{css}\n</style>'
            st.markdown(safe_block, unsafe_allow_html=True)
        except Exception as fallback_e:
            logger.debug(f"Fallback CSS injection also failed: {fallback_e}")


def inject_inline_style(css_rules: str, element_id: str = None) -> None:
    """Inject inline CSS rules as a style block.

    Args:
        css_rules: Raw CSS rules
        element_id: Optional ID for the style element
    """
    try:
        element_id = element_id or "fp-inline-styles"
        safe_block = f'<style id="{element_id}">\n{css_rules}\n</style>'
        st.markdown(safe_block, unsafe_allow_html=True)
    except Exception as e:
        logger.debug(f"Error injecting inline style: {e}")

"""
Glyph Processing and Display Handler.

Extracts, validates, and renders glyph information from signal analysis.
Handles best glyph selection and voltage response generation.
"""

import logging
import streamlit as st

logger = logging.getLogger(__name__)


def extract_glyphs_from_analysis(local_analysis: dict) -> list:
    """Extract glyph list from local analysis.

    Args:
        local_analysis: Analysis dict from signal_parser

    Returns:
        List of glyph dicts
    """
    return local_analysis.get("glyphs", [])


def get_best_glyph(local_analysis: dict) -> dict:
    """Get primary/best glyph from analysis.

    Args:
        local_analysis: Analysis dict from signal_parser

    Returns:
        Best glyph dict or empty dict if none
    """
    return local_analysis.get("best_glyph", {})


def get_voltage_response(local_analysis: dict) -> str:
    """Get voltage response summary from analysis.

    The voltage_response is a text summary of activated glyphs and signals.

    Args:
        local_analysis: Analysis dict from signal_parser

    Returns:
        Voltage response string
    """
    return local_analysis.get("voltage_response", "")


def validate_glyph_data(glyph: dict) -> bool:
    """Validate that a glyph has required fields.

    Args:
        glyph: Glyph dict to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        required_fields = ["glyph_name", "symbol", "core_emotions"]
        return all(field in glyph for field in required_fields)
    except Exception:
        return False


def format_glyph_display(glyph: dict) -> str:
    """Format glyph for UI display.

    Args:
        glyph: Glyph dict

    Returns:
        Formatted display string
    """
    try:
        if not validate_glyph_data(glyph):
            return "Unknown Glyph"

        symbol = glyph.get("symbol", "?")
        name = glyph.get("glyph_name", "Unknown")
        emotions = ", ".join(glyph.get("core_emotions", []))

        return f"{symbol} **{name}** ({emotions})"

    except Exception as e:
        logger.debug(f"Error formatting glyph: {e}")
        return "Unknown Glyph"


def display_glyph_info(glyph: dict, show_details: bool = False):
    """Display glyph information in UI.

    Args:
        glyph: Glyph dict
        show_details: Whether to show extended info
    """
    try:
        if not validate_glyph_data(glyph):
            st.write("Glyph information unavailable")
            return

        formatted = format_glyph_display(glyph)
        st.markdown(f"**Resonant Glyph:** {formatted}")

        if show_details:
            with st.expander("Glyph Details"):
                st.write(f"**Name:** {glyph.get('glyph_name', 'Unknown')}")
                st.write(f"**Symbol:** {glyph.get('symbol', '?')}")
                st.write(
                    f"**Core Emotions:** {', '.join(glyph.get('core_emotions', []))}")

                # Show description if available
                if "description" in glyph:
                    st.write(f"**Description:** {glyph.get('description')}")

                # Show activation factors
                if "activation_factors" in glyph:
                    factors = glyph.get("activation_factors", [])
                    if factors:
                        st.write("**Activation Factors:**")
                        for factor in factors:
                            st.write(f"- {factor}")

    except Exception as e:
        logger.debug(f"Error displaying glyph: {e}")


def display_activated_glyphs(glyphs: list, max_display: int = 5):
    """Display list of activated glyphs.

    Args:
        glyphs: List of glyph dicts
        max_display: Maximum glyphs to display
    """
    try:
        if not glyphs:
            st.write("No glyphs activated in this exchange")
            return

        st.markdown("**Activated Glyphs:**")

        for i, glyph in enumerate(glyphs[:max_display]):
            if validate_glyph_data(glyph):
                formatted = format_glyph_display(glyph)
                st.markdown(f"- {formatted}")

        if len(glyphs) > max_display:
            st.caption(f"... and {len(glyphs) - max_display} more")

    except Exception as e:
        logger.debug(f"Error displaying activated glyphs: {e}")


def get_glyph_summary(glyphs: list) -> str:
    """Get summary of activated glyphs as string.

    Args:
        glyphs: List of glyph dicts

    Returns:
        Summary string like "5 glyphs activated: Joy, Calm, ..."
    """
    try:
        if not glyphs:
            return "No glyphs activated"

        names = [g.get("glyph_name", "Unknown")
                 for g in glyphs if validate_glyph_data(g)]
        count = len(names)

        if count == 0:
            return "No valid glyphs activated"

        display_names = ", ".join(names[:3])
        if count > 3:
            display_names += f", ... ({count - 3} more)"

        return f"{count} glyph(s): {display_names}"

    except Exception:
        return "Glyph summary unavailable"


def extract_debug_info(local_analysis: dict) -> dict:
    """Extract debug/diagnostic information from analysis.

    Args:
        local_analysis: Analysis dict from signal_parser

    Returns:
        Dict with signals, gates, SQL, etc.
    """
    return {
        "signals": local_analysis.get("signals", []),
        "gates": local_analysis.get("gates", []),
        "glyphs": local_analysis.get("glyphs", []),
        "debug_sql": local_analysis.get("debug_sql", ""),
        "debug_glyph_rows": local_analysis.get("debug_glyph_rows", []),
        "ritual_prompt": local_analysis.get("ritual_prompt", ""),
        "voltage_response": local_analysis.get("voltage_response", ""),
    }


def display_debug_panel(debug_info: dict, expanded: bool = False):
    """Display debug information panel.

    Shows signals, glyphs, SQL queries, etc. for developers/testing.

    Args:
        debug_info: Debug dict from extract_debug_info()
        expanded: Whether to start expander in expanded state
    """
    try:
        with st.expander("🔧 Debug: Signal Analysis", expanded=expanded):
            # Signals
            signals = debug_info.get("signals", [])
            if signals:
                st.write(f"**Signals ({len(signals)}):**")
                st.json(signals[:5] if len(signals) > 5 else signals)

            # Glyphs
            glyphs = debug_info.get("glyphs", [])
            if glyphs:
                st.write(f"**Glyphs ({len(glyphs)}):**")
                for glyph in glyphs[:3]:
                    st.write(format_glyph_display(glyph))
                if len(glyphs) > 3:
                    st.caption(f"... and {len(glyphs) - 3} more")

            # SQL if available
            sql = debug_info.get("debug_sql", "")
            if sql:
                st.write("**Query:**")
                st.code(sql, language="sql")

            # Gates
            gates = debug_info.get("gates", [])
            if gates:
                st.write(f"**Gates ({len(gates)}):**")
                st.json(gates[:3])

    except Exception as e:
        logger.debug(f"Error displaying debug panel: {e}")

"""
Phase 2.4: User Preference UI Components
Streamlit-based interface for displaying and managing user glyph preferences.
"""

import streamlit as st
from typing import Optional, List
from datetime import datetime
from emotional_os.core.firstperson.preference_manager import (
    PreferenceManager,
    UserPreferences,
    PreferenceLevel
)


class PreferenceUI:
    """Streamlit UI components for preference management."""

    def __init__(self, preference_manager: PreferenceManager):
        """Initialize UI with a preference manager."""
        self.manager = preference_manager

    def display_user_dashboard(self, user_id: str) -> None:
        """Display comprehensive preference dashboard for a user."""
        prefs = self.manager.get_user_preferences(user_id)

        # Header
        st.markdown("## 📊 Your Glyph Preferences")
        
        # Summary metrics
        summary = self._display_summary_metrics(prefs)

        # Main content tabs
        tab1, tab2, tab3, tab4 = st.tabs(
            ["📈 Overview", "💝 Favorites", "✗ Disliked", "⚙️ Customize"]
        )

        with tab1:
            self._display_overview_tab(prefs)

        with tab2:
            self._display_favorites_tab(prefs)

        with tab3:
            self._display_disliked_tab(prefs)

        with tab4:
            self._display_customize_tab(prefs, user_id)

    def _display_summary_metrics(self, prefs: UserPreferences) -> dict:
        """Display key summary metrics."""
        summary = prefs.get_preference_summary()
        
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Glyphs Tracked",
                summary['total_glyphs_tracked'],
                delta=None,
                delta_color="off"
            )

        with col2:
            st.metric(
                "Average Effectiveness",
                f"{summary['average_effectiveness']:.0%}",
                delta=None,
                delta_color="off"
            )

        with col3:
            st.metric(
                "Total Uses",
                summary['total_uses'],
                delta=None,
                delta_color="off"
            )

        with col4:
            st.metric(
                "Acceptance Rate",
                f"{summary['overall_acceptance_rate']:.0%}",
                delta=None,
                delta_color="off"
            )

        return summary

    def _display_overview_tab(self, prefs: UserPreferences) -> None:
        """Display overview tab with insights and top glyphs."""
        st.subheader("Key Insights")
        
        insights = prefs.get_insights()
        for insight in insights:
            st.info(insight)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🌟 Top Glyphs")
            top = prefs.get_top_glyphs(limit=5)
            if top:
                for glyph, score in top:
                    st.progress(
                        score,
                        text=f"{glyph}: {score:.0%}"
                    )
            else:
                st.info("No glyph data yet. Start using glyphs to build your profile!")

        with col2:
            st.subheader("📊 Effectiveness Distribution")
            effectiveness_scores = [p.effectiveness_score for p in prefs.preferences.values()]
            if effectiveness_scores:
                st.bar_chart(
                    {
                        "Effectiveness": effectiveness_scores,
                    }
                )
            else:
                st.info("No data yet")

    def _display_favorites_tab(self, prefs: UserPreferences) -> None:
        """Display favorite glyphs tab."""
        st.subheader("💝 Your Favorite Glyphs")

        if not prefs.favorite_glyphs:
            st.info("No favorite glyphs yet. Accept responses you love to build favorites!")
            return

        for glyph_name in prefs.favorite_glyphs:
            pref_data = [p for p in prefs.preferences.values() if p.glyph_name == glyph_name]
            if not pref_data:
                continue

            with st.expander(f"🌟 {glyph_name}", expanded=False):
                for pref in pref_data:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Tone", pref.tone)
                    with col2:
                        st.metric("Uses", pref.uses_count)
                    with col3:
                        st.metric("Acceptance", f"{pref.get_acceptance_rate():.0%}")

                    st.progress(
                        pref.effectiveness_score,
                        text=f"Effectiveness: {pref.get_effectiveness_percentage():.1f}%"
                    )

    def _display_disliked_tab(self, prefs: UserPreferences) -> None:
        """Display disliked glyphs tab."""
        st.subheader("✗ Rarely Used Glyphs")

        if not prefs.disliked_glyphs:
            st.success("No disliked glyphs! All your glyphs have good resonance.")
            return

        for glyph_name in prefs.disliked_glyphs:
            pref_data = [p for p in prefs.preferences.values() if p.glyph_name == glyph_name]
            if not pref_data:
                continue

            with st.expander(f"✗ {glyph_name}", expanded=False):
                for pref in pref_data:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Tone", pref.tone)
                    with col2:
                        st.metric("Uses", pref.uses_count)
                    with col3:
                        st.metric("Rejection", f"{pref.get_rejection_rate():.0%}")

                    st.progress(
                        pref.effectiveness_score,
                        text=f"Effectiveness: {pref.get_effectiveness_percentage():.1f}%"
                    )

                st.warning(
                    f"This glyph has low effectiveness. Consider alternatives when this tone appears."
                )

    def _display_customize_tab(self, prefs: UserPreferences, user_id: str) -> None:
        """Display customization tab for manual overrides."""
        st.subheader("⚙️ Customize Your Preferences")

        col1, col2 = st.columns([2, 1])

        with col1:
            tone = st.selectbox(
                "Select a tone to customize:",
                sorted(set(p.tone for p in prefs.preferences.values())) or ["compassionate"]
            )

        with col2:
            if st.button("Add Custom Tone"):
                new_tone = st.text_input("New tone name:")
                if new_tone:
                    tone = new_tone

        # Available glyphs for override
        all_glyphs = sorted(set(p.glyph_name for p in prefs.preferences.values())) or ["warmth"]
        
        current_override = prefs.manual_overrides.get(tone)
        
        st.write(f"**Configure '{tone}' responses:**")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_glyph = st.selectbox(
                "Preferred glyph for this tone:",
                all_glyphs,
                index=all_glyphs.index(current_override) if current_override in all_glyphs else 0,
                key=f"glyph_select_{tone}"
            )

        with col2:
            notes = st.text_input("Notes (optional):", value="", key=f"notes_{tone}")

        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("Save Override", key=f"save_{tone}"):
                self.manager.set_manual_override(user_id, tone, selected_glyph, notes)
                st.success(f"✓ Saved! '{selected_glyph}' will be used for '{tone}' responses.")

        with col2:
            if current_override and st.button("Clear Override", key=f"clear_{tone}"):
                prefs.manual_overrides.pop(tone, None)
                st.success(f"✓ Cleared override for '{tone}'")

        st.divider()

        st.subheader("📋 Current Customizations")
        if prefs.manual_overrides:
            for tone_override, glyph_override in prefs.manual_overrides.items():
                st.info(f"**{tone_override}** → {glyph_override}")
        else:
            st.info("No custom overrides yet. Create your first above!")

    def display_preference_statistics(self, user_id: str) -> None:
        """Display detailed preference statistics."""
        prefs = self.manager.get_user_preferences(user_id)
        
        st.markdown("## 📈 Preference Statistics")

        # Preference level distribution
        level_counts = {}
        for pref in prefs.preferences.values():
            level_name = pref.preference_level.name
            level_counts[level_name] = level_counts.get(level_name, 0) + 1

        if level_counts:
            st.bar_chart(level_counts)

        # Effectiveness distribution
        st.subheader("Effectiveness Distribution")
        effectiveness_ranges = {
            "Excellent (80-100%)": 0,
            "Good (60-80%)": 0,
            "Fair (40-60%)": 0,
            "Poor (0-40%)": 0,
        }

        for pref in prefs.preferences.values():
            score = pref.effectiveness_score
            if score >= 0.8:
                effectiveness_ranges["Excellent (80-100%)"] += 1
            elif score >= 0.6:
                effectiveness_ranges["Good (60-80%)"] += 1
            elif score >= 0.4:
                effectiveness_ranges["Fair (40-60%)"] += 1
            else:
                effectiveness_ranges["Poor (0-40%)"] += 1

        st.bar_chart(effectiveness_ranges)

    def display_export_options(self, user_id: str) -> None:
        """Display preference export options."""
        st.markdown("## 📥 Export Your Data")

        prefs = self.manager.get_user_preferences(user_id)
        json_export = prefs.export_json()

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="Download Preferences (JSON)",
                data=json_export,
                file_name=f"preferences_{user_id}.json",
                mime="application/json",
                key="download_prefs"
            )

        with col2:
            if st.button("Copy to Clipboard"):
                st.code(json_export, language="json")

    def display_mini_summary(self, user_id: str) -> None:
        """Display compact preference summary (for sidebars, etc)."""
        prefs = self.manager.get_user_preferences(user_id)
        summary = prefs.get_preference_summary()

        st.markdown("### Your Profile")
        st.metric("Glyphs", summary['total_glyphs_tracked'])
        st.metric("Effectiveness", f"{summary['average_effectiveness']:.0%}")
        st.metric("Acceptance", f"{summary['overall_acceptance_rate']:.0%}")


def initialize_preference_ui() -> PreferenceUI:
    """Initialize preference UI in Streamlit session state."""
    if "preference_manager" not in st.session_state:
        st.session_state.preference_manager = PreferenceManager()

    if "preference_ui" not in st.session_state:
        st.session_state.preference_ui = PreferenceUI(st.session_state.preference_manager)

    return st.session_state.preference_ui

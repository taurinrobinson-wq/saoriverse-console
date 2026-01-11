"""
Streamlit UI Components
=======================

Clean UI rendering for Velinor prototype:
- Background + NPC overlay rendering
- Dialogue box
- Button grid (2x2 + fifth action button)
- Sidebar with TONE, REMNANTS, Glyphs, Skills
- Scene transitions

All rendering is modular and stateless (takes current_state as argument).
"""

import streamlit as st
from typing import Callable, Optional, Dict, Any, List
import os
from pathlib import Path


class StreamlitUI:
    """Handles all Streamlit UI rendering."""

    def __init__(self):
        self.assets_path = Path(__file__).parent / "assets"
        self.backgrounds_path = self.assets_path / "backgrounds"
        self.npcs_path = self.assets_path / "npcs"
        self.glyphs_path = self.assets_path / "glyphs"

    # ========================================================================
    # SIDEBAR: EMOTIONAL OS DASHBOARD
    # ========================================================================

    def render_sidebar(self, game_state: Any) -> None:
        """Render complete sidebar with TONE, REMNANTS, Glyphs, Skills."""

        st.sidebar.markdown("## 📊 Emotional OS")
        st.sidebar.divider()

        # TONE STATS
        self.render_tone_stats(game_state)

        st.sidebar.divider()

        # REMNANTS TRAITS
        self.render_remnants_traits(game_state)

        st.sidebar.divider()

        # GLYPHS
        self.render_glyphs_panel(game_state)

        st.sidebar.divider()

        # SKILLS
        self.render_skills_panel(game_state)

        st.sidebar.divider()

        # NPC PERCEPTION
        self.render_npc_perception_panel(game_state)

    def render_tone_stats(self, game_state: Any) -> None:
        """Render TONE stats in sidebar."""
        st.sidebar.markdown("### 🎼 TONE")

        tone = game_state.tone.to_dict()

        # Visual bars for each stat
        for stat_name, value in tone.items():
            # Convert from -1.0 to 1.0 to 0 to 100 for progress bar
            normalized = int((value + 1.0) * 50)
            color = "🟢" if value > 0.3 else "🟡" if value > -0.3 else "🔴"
            st.sidebar.markdown(
                f"{color} **{stat_name.replace('_', ' ').title()}**: {value:+.2f}"
            )

    def render_remnants_traits(self, game_state: Any) -> None:
        """Render REMNANTS traits in sidebar."""
        st.sidebar.markdown("### 👁️ REMNANTS")

        traits = game_state.remnants_traits

        for trait_name, value in traits.items():
            normalized = int((value + 1.0) * 50)
            st.sidebar.write(
                f"**{trait_name.replace('_', ' ').title()}**: {value:+.2f}")

    def render_glyphs_panel(self, game_state: Any) -> None:
        """Render glyph list in sidebar."""
        st.sidebar.markdown("### ✨ Glyphs")

        glyphs = game_state.glyphs
        obtained = game_state.get_obtained_glyphs()

        for glyph_name, glyph in glyphs.items():
            if glyph.obtained:
                st.sidebar.markdown(
                    f"🟢 **{glyph_name}** - {glyph.description}")
            else:
                st.sidebar.markdown(f"⚫ ~~{glyph_name}~~ - *locked*")

    def render_skills_panel(self, game_state: Any) -> None:
        """Render skills in sidebar."""
        st.sidebar.markdown("### 🎯 Skills")

        skills = game_state.skills

        for skill_name, skill in skills.items():
            if skill.unlocked:
                st.sidebar.markdown(
                    f"🟢 **{skill_name}** - {skill.description}")
            else:
                st.sidebar.markdown(f"⚫ ~~{skill_name}~~ - *locked*")

    def render_npc_perception_panel(self, game_state: Any) -> None:
        """Render NPC perception in sidebar."""
        st.sidebar.markdown("### 👥 NPC Perception")

        perceptions = game_state.npc_perception

        for npc_name, perception in perceptions.items():
            trust_emoji = "💚" if perception.trust > 0.3 else "❤️" if perception.trust > -0.3 else "💔"
            st.sidebar.markdown(
                f"{trust_emoji} **{npc_name}** ({perception.emotion})\n"
                f"  Trust: {perception.trust:+.2f} | "
                f"Affinity: {perception.affinity:+.2f}"
            )

    # ========================================================================
    # MAIN: SCENE RENDERING
    # ========================================================================

    def render_scene(self, current_state: Dict[str, Any]) -> None:
        """Render background + NPC overlay + dialogue box."""

        # Placeholder for background
        if current_state.get("background_image"):
            st.markdown(f"**📍 Location:** {current_state['background_image']}")

        # Placeholder for NPC overlay
        if current_state.get("npcs"):
            npcs = current_state.get("npcs", [])
            st.markdown(f"**👥 Present:** {', '.join(npcs)}")

        # Main dialogue
        st.markdown("---")

        if current_state.get("main_dialogue"):
            st.markdown(f"*{current_state['main_dialogue']}*")

        # NPC response (if any)
        if current_state.get("npc_dialogue"):
            st.markdown(f"\n**NPC:** {current_state['npc_dialogue']}")

        st.markdown("---")

    # ========================================================================
    # MAIN: BUTTON GRID + FIFTH ACTION
    # ========================================================================

    def render_button_grid(self,
                           current_state: Dict[str, Any],
                           game_state: Any,
                           on_choice: Callable[[int], None],
                           on_glyph_input: Callable[[str], None],
                           on_attack: Callable[[], None],
                           on_special_action: Callable[[str], None]) -> None:
        """Render 2x2 button grid + optional fifth action button."""

        mode = game_state.mode

        if mode == "narrative":
            self._render_narrative_buttons(current_state, on_choice)
        elif mode == "glyph_input":
            self._render_glyph_input_buttons(game_state, on_glyph_input)
        elif mode == "chamber":
            self._render_chamber_buttons(game_state, on_attack)

        # Render optional fifth button
        self._render_special_action_button(
            game_state, current_state, on_special_action)

    def _render_narrative_buttons(self,
                                  current_state: Dict[str, Any],
                                  on_choice: Callable[[int], None]) -> None:
        """Render 4 choice buttons in 2x2 grid."""

        choices = current_state.get("choices", [])

        # If fewer than 4 choices, pad with empties
        while len(choices) < 4:
            choices.append({"text": "", "index": len(choices)})

        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        cols = [col1, col2, col3, col4]

        for i, col in enumerate(cols):
            choice = choices[i] if i < len(choices) else {}
            choice_text = choice.get("text", "")

            if choice_text:
                if col.button(choice_text, key=f"choice_{i}", use_container_width=True):
                    on_choice(i)
            else:
                col.button(
                    f"[Empty]", key=f"choice_{i}", disabled=True, use_container_width=True)

    def _render_glyph_input_buttons(self,
                                    game_state: Any,
                                    on_glyph_input: Callable[[str], None]) -> None:
        """Render glyph selection buttons for chamber door."""

        st.markdown("#### ✨ Select Glyphs to Unlock Chamber")

        usable_glyphs = game_state.get_usable_glyphs()

        # For current glyph page, show 4 glyphs
        start_idx = (game_state.glyph_page - 1) * 4
        page_glyphs = usable_glyphs[start_idx:start_idx + 4]

        # Pad to 4 buttons
        while len(page_glyphs) < 4:
            page_glyphs.append(None)

        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        cols = [col1, col2, col3, col4]

        for i, col in enumerate(cols):
            glyph_name = page_glyphs[i]

            if glyph_name:
                if col.button(glyph_name, key=f"glyph_{i}", use_container_width=True):
                    on_glyph_input(glyph_name)
            else:
                col.button(
                    f"[Empty]", key=f"glyph_{i}", disabled=True, use_container_width=True)

        # Show progress
        st.markdown(
            f"**Glyphs Used This Page:** {game_state.glyphs_used_count} / 4")

        if game_state.glyphs_used_count >= 4:
            if game_state.glyph_page == 1:
                center_col = st.columns([1, 1, 1])[1]
                center_col.button("Next Set ➜", key="next_glyph_set", use_container_width=True,
                                  on_click=lambda: None)  # Will be handled by on_glyph_input logic
            else:
                center_col = st.columns([1, 1, 1])[1]
                center_col.button(
                    "Enter Chamber", key="enter_chamber", use_container_width=True)

    def _render_chamber_buttons(self,
                                game_state: Any,
                                on_attack: Callable[[], None]) -> None:
        """Render chamber fight interface."""

        st.markdown("#### ⚔️ GLYPH BEAST ENCOUNTER")
        st.markdown(f"*The air fractures around you...*")

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            # Show fight progress
            progress = min(1.0, game_state.fight_counter /
                           game_state.fight_max)
            st.progress(
                progress, text=f"{game_state.fight_counter} / {game_state.fight_max} Attacks")

            # Attack button
            if st.button("⚡ Attack", use_container_width=True, key="attack_btn"):
                on_attack()

        if game_state.fight_counter >= game_state.fight_max:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.button("✨ Obtain Glyph", use_container_width=True,
                          key="obtain_glyph_btn")

    def _render_special_action_button(self,
                                      game_state: Any,
                                      current_state: Dict[str, Any],
                                      on_special_action: Callable[[str], None]) -> None:
        """Render optional fifth button for special glyph actions."""

        # Determine if special action is available
        special_action = None
        special_label = ""

        # In narrative mode, check if we can use a glyph on current NPC
        if game_state.mode == "narrative":
            current_npc = current_state.get("npc_name")
            if current_npc and game_state.get_obtained_glyphs():
                # For prototype, just show one glyph action per NPC
                usable = game_state.get_obtained_glyphs()[0]
                special_action = f"use_glyph_{usable}"
                special_label = f"Invoke {usable} Glyph"

        if special_action:
            st.divider()
            center_col = st.columns([1, 1, 1])[1]
            with center_col:
                if st.button(special_label, use_container_width=True, key="special_action_btn"):
                    on_special_action(special_action)

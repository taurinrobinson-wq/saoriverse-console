#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VELΩNIX Streamlit Integration

Provides interactive Streamlit UI components for the VELΩNIX engine.
"""

try:
    import streamlit as st
except ImportError:
    st = None

from typing import Dict, List, Optional

from .velonix_reaction_engine import get_velonix_engine
from .velonix_visualizer import EmotionalArchive, RitualPromptSystem, VelonixVisualizer


def render_velonix_interface():
    """
    Render the full VELΩNIX interface in Streamlit.
    Requires Streamlit to be available.
    """
    if st is None:
        raise ImportError("Streamlit is required for this interface")

    st.set_page_config(page_title="VELΩNIX Emotional Alchemy", layout="wide")

    st.markdown(
        """
    # 🧪 VELΩNIX Emotional Reaction Engine
    
    *Witness the alchemy of emotion. Combine elements to discover transformations.*
    """
    )

    engine = get_velonix_engine()
    visualizer = VelonixVisualizer(engine)

    # Initialize session state
    if "velonix_archive" not in st.session_state:
        st.session_state.velonix_archive = EmotionalArchive()

    if "last_reaction" not in st.session_state:
        st.session_state.last_reaction = None

    # Sidebar: Element selection
    with st.sidebar:
        st.markdown("### 🎭 Emotional Elements")

        elements = engine.list_elements()
        element_options = {f"{e.symbol} — {e.name}": e.symbol for e in sorted(elements, key=lambda x: x.name)}

        st.markdown("**Select Input Elements:**")
        col1, col2 = st.columns(2)

        with col1:
            input1_display = st.selectbox(
                "First Element", options=list(element_options.keys()), key="input1", label_visibility="collapsed"
            )
            input1 = element_options[input1_display]

        with col2:
            input2_display = st.selectbox(
                "Second Element",
                options=list(element_options.keys()),
                key="input2",
                label_visibility="collapsed",
                index=1 if len(element_options) > 1 else 0,
            )
            input2 = element_options[input2_display]

        st.markdown("**Optional Catalyst:**")
        catalyst_options = {"(None)": None, **element_options}
        catalyst_display = st.selectbox(
            "Catalyst Element", options=list(catalyst_options.keys()), key="catalyst", label_visibility="collapsed"
        )
        catalyst = catalyst_options[catalyst_display]

        # User notes
        user_notes = st.text_area(
            "Your Reflection",
            placeholder="What are you noticing about this emotional state?",
            height=100,
            key="user_notes",
        )

        # Execute reaction button
        if st.button("🔮 Execute Reaction", use_container_width=True, key="execute"):
            reaction = engine.react([input1, input2], catalyst=catalyst, verbose=True)

            if reaction:
                st.session_state.last_reaction = {
                    "inputs": [input1, input2],
                    "catalyst": catalyst,
                    "reaction": reaction,
                    "user_notes": user_notes,
                }
                st.success("Reaction completed!")
                st.rerun()
            else:
                st.warning("No reaction found for this combination.")

    # Main area
    if st.session_state.last_reaction:
        reaction_data = st.session_state.last_reaction
        reaction = reaction_data["reaction"]
        result_element = reaction["result_element"]
        input_elements = reaction["inputs"]
        catalyst_element = reaction["catalyst"]

        # Display reaction result
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### ⚗️ Inputs")
            for elem in input_elements:
                st.markdown(f"**{elem.symbol}** — {elem.name}")
                st.caption(f"_{elem.tone}_")

        with col2:
            st.markdown("### ⚡ Result")
            st.markdown(f"## {result_element.symbol}")
            st.markdown(f"### {result_element.name}")
            st.caption(f"_{result_element.tone}_")
            st.caption(f"Role: _{result_element.trace_role}_")

        with col3:
            if catalyst_element:
                st.markdown("### 🔧 Catalyst")
                st.markdown(f"**{catalyst_element.symbol}** — {catalyst_element.name}")
                st.caption(f"_{catalyst_element.tone}_")
            else:
                st.markdown("### 🔧 Catalyst")
                st.info("Spontaneous reaction (no catalyst)")

        # Trace outcome
        st.markdown("---")
        st.markdown("### 📖 Trace Outcome")
        st.markdown(f"_{reaction['trace_outcome']}_")

        # Visualization
        st.markdown("---")
        st.markdown("### 🎨 Visualization")

        svg = visualizer.generate_reaction_visualization(
            inputs=input_elements, result=result_element, catalyst=catalyst_element
        )
        st.components.v1.html(svg, height=400)

        # Ritual prompt
        st.markdown("---")
        st.markdown("### 📿 Integration Ritual")

        ritual = RitualPromptSystem.generate_ritual_prompt(
            result_element=result_element, trace_outcome=reaction["trace_outcome"]
        )

        st.info(f"✨ {ritual['element_name']}")
        st.markdown(f"\n**{ritual['prompt']}**")

        if st.button("📝 Confirm Ritual Engagement", key="confirm_ritual"):
            st.session_state.velonix_archive.log_reaction(
                reaction_result=reaction, ritual_prompt=ritual, user_notes=reaction_data["user_notes"]
            )
            st.success("Ritual recorded in your archive!")

        # Archive section
        st.markdown("---")
        st.markdown("### 📚 Legacy Archive")

        archive_entries = st.session_state.velonix_archive.get_entries(limit=5)

        if archive_entries:
            st.write(f"Total transformations recorded: {len(st.session_state.velonix_archive.entries)}")

            with st.expander("View Recent Entries"):
                for i, entry in enumerate(reversed(archive_entries), 1):
                    with st.container(border=True):
                        if "reaction" in entry and entry["reaction"]:
                            result = entry["reaction"].get("result_element", {})
                            st.caption(f"Entry {i}: {entry.get('timestamp', 'Unknown time')}")
                            st.write(f"Result: **{result.get('name', 'Unknown')}**")
                            if entry.get("user_notes"):
                                st.write(f"Reflection: _{entry['user_notes']}_")

            if st.button("📤 Export Archive", key="export_archive"):
                archive_json = st.session_state.velonix_archive.export_as_json()
                st.download_button(
                    label="Download Archive (JSON)",
                    data=archive_json,
                    file_name="velonix_archive.json",
                    mime="application/json",
                )
        else:
            st.info("No reactions recorded yet in your archive.")

    else:
        # Initial state
        st.markdown(
            """
        ### Welcome to VELΩNIX
        
        The Emotional Reaction Engine models how emotional states combine and transform.
        
        **Steps:**
        1. Select two emotional elements from the sidebar
        2. Optionally choose a catalyst
        3. Add your reflection
        4. Click "Execute Reaction" to discover the transformation
        5. Engage with the ritual to integrate the new state
        
        #### Available Elements
        """
        )

        elements = engine.list_elements()

        cols = st.columns(3)
        for i, element in enumerate(sorted(elements, key=lambda x: x.name)):
            with cols[i % 3]:
                st.markdown(
                    f"""
                **{element.symbol}** — {element.name}
                
                Tone: _{element.tone}_
                
                Role: {element.trace_role}
                """
                )


def render_velonix_element_explorer():
    """Render a simple element explorer component."""
    if st is None:
        raise ImportError("Streamlit is required for this interface")

    st.markdown("### 🔍 Element Explorer")

    engine = get_velonix_engine()
    elements = engine.list_elements()

    selected_symbol = st.selectbox(
        "Select an element:",
        options=[e.symbol for e in sorted(elements, key=lambda x: x.name)],
        format_func=lambda s: f"{s} — {engine.get_element(s).name}",
    )

    element = engine.get_element(selected_symbol)

    if element:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"### {element.name}")
            st.markdown(f"**Symbol:** `{element.symbol}`")
            st.markdown(f"**Tone:** _{element.tone}_")
            st.markdown(f"**Valence:** {element.valence}")
            st.markdown(f"**Reactivity:** {element.reactivity}")
            st.markdown(f"**Trace Role:** {element.trace_role}")
            st.markdown(f"**Relational Function:** {element.relational_function}")

        with col2:
            visualizer = VelonixVisualizer(engine)
            svg = visualizer.generate_svg_element(element, size=150)
            st.components.v1.html(svg, height=300)


def render_reaction_explorer():
    """Render a reaction explorer component."""
    if st is None:
        raise ImportError("Streamlit is required for this interface")

    st.markdown("### ⚗️ Reaction Explorer")

    engine = get_velonix_engine()

    current_elements = st.multiselect(
        "Select your current emotional elements:",
        options=[e.symbol for e in engine.list_elements()],
        format_func=lambda s: f"{s} — {engine.get_element(s).name}",
    )

    if current_elements:
        possible = engine.find_possible_reactions(current_elements)

        if possible:
            st.success(f"Found {len(possible)} possible reaction(s)")

            for reaction in possible:
                with st.container(border=True):
                    inputs = " + ".join([e.name for e in reaction["inputs"]])
                    catalyst = f" (catalyst: {reaction['catalyst'].name})" if reaction["catalyst"] else ""
                    result = reaction["result"].name if reaction["result"] else "Unknown"

                    st.markdown(f"**{inputs}{catalyst}** → **{result}**")
                    st.caption(reaction["trace_outcome"])
        else:
            st.info("No reactions available with these elements.")


if __name__ == "__main__":
    # Run the interface
    render_velonix_interface()

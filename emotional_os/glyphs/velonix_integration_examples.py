#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration example: How to add VELΩNIX to your Streamlit app
"""

import streamlit as st
from emotional_os.glyphs.velonix_reaction_engine import get_velonix_engine
from emotional_os.glyphs.velonix_visualizer import VelonixVisualizer, RitualPromptSystem
from emotional_os.glyphs.velonix_streamlit import (
    render_velonix_interface,
    render_velonix_element_explorer,
    render_reaction_explorer,
)


def integrate_velonix_into_main_app():
    """
    Example: How to integrate VELΩNIX into your existing Streamlit app
    """
    
    # Add to your sidebar
    with st.sidebar:
        st.markdown("---")
        with st.expander("✨ Emotional Alchemy"):
            if st.button("Explore Emotions with VELΩNIX"):
                st.session_state.show_velonix = True
    
    # Show VELΩNIX when requested
    if st.session_state.get('show_velonix', False):
        render_velonix_interface()


def simple_velonix_widget():
    """
    Minimal integration: Quick reaction widget
    """
    st.markdown("### 🧪 Quick Emotional Reaction")
    
    engine = get_velonix_engine()
    visualizer = VelonixVisualizer(engine)
    
    col1, col2 = st.columns(2)
    
    elements = engine.list_elements()
    element_map = {e.name: e.symbol for e in elements}
    
    with col1:
        input1_name = st.selectbox("First Element", sorted(element_map.keys()))
        input1 = element_map[input1_name]
    
    with col2:
        input2_name = st.selectbox("Second Element", sorted(element_map.keys()), index=1)
        input2 = element_map[input2_name]
    
    if st.button("React"):
        reaction = engine.react([input1, input2])
        if reaction:
            st.success(f"Result: {reaction['result_element'].name}")
            st.info(reaction['trace_outcome'])


def velonix_in_conversation_context():
    """
    Advanced: Use VELΩNIX to guide conversation emotional arc
    
    Example: After user shares emotions, suggest emotional alchemy
    """
    
    # Suppose user said something revealing these emotions
    detected_emotions = ["Lg", "Gf"]  # Longing + Grief
    
    engine = get_velonix_engine()
    
    # Find what transformation is possible
    possible = engine.find_possible_reactions(detected_emotions)
    
    if possible:
        st.markdown("### 🌟 Emotional Possibility")
        
        for p in possible:
            with st.container(border=True):
                st.markdown(f"**{p['result'].name}** is possible here")
                st.caption(p['trace_outcome'])
                
                # Suggest ritual
                ritual = RitualPromptSystem.generate_ritual_prompt(p['result'])
                if st.button(f"Explore {p['result'].name}", key=p['result'].symbol):
                    st.info(f"📿 {ritual['prompt']}")


if __name__ == "__main__":
    # Demo the integration examples
    st.set_page_config(page_title="VELΩNIX Integration", layout="wide")
    
    st.title("VELΩNIX Integration Examples")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Full Interface",
        "Quick Widget",
        "Element Explorer",
        "Reaction Explorer"
    ])
    
    with tab1:
        st.markdown("### Full VELΩNIX Interface")
        st.info("This would be the main emotional alchemy interface")
        if st.button("Load Full Interface"):
            render_velonix_interface()
    
    with tab2:
        simple_velonix_widget()
    
    with tab3:
        render_velonix_element_explorer()
    
    with tab4:
        render_reaction_explorer()

"""
Velinor Glyph Console
====================

Comprehensive UI for exploring Velinor's glyph system:
- Core glyphs (Glyph_Organizer.csv) as central dataset
- Related fragments, fusion glyphs, cipher seeds
- Impact analysis and relationship graph
- Cross-dataset search and filtering

Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import networkx as nx
import json
from pathlib import Path
from typing import Dict, List, Any
import plotly.graph_objects as go
import plotly.express as px
from github import Github
from github.GithubException import GithubException
import base64

# Note: Removed AgGrid due to incompatibility between streamlit-aggrid 0.3.3 and pandas 2.x
# Using Streamlit's native st.data_editor() instead for interactive tables
HAS_AGGRID = False

# Import utilities
from utils import (
    match_fragments_to_glyph,
    match_fusion_to_glyph,
    match_cipher_to_glyph,
    compute_tone_impact,
    compute_remnants_impact,
    compute_endgame_dependencies,
    compute_emotional_alignment,
    build_relationship_graph,
    get_graph_stats,
    export_glyph_to_json
)

# ============================================================================
# GITHUB INTEGRATION HELPERS
# ============================================================================

def commit_story_to_repo(filename: str, content: str):
    """
    Commit a story file to the GitHub repository using PyGithub.
    
    Args:
        filename: Name of the file to commit (e.g., "Glyph_of_Memory.json")
        content: JSON string content of the story
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Get GitHub token from Streamlit secrets
        if "GITHUB_TOKEN" not in st.secrets:
            return False, "GitHub token not configured in secrets."
        
        github_token = st.secrets["GITHUB_TOKEN"]
        g = Github(github_token)
        repo = g.get_repo("taurinrobinson-wq/saoriverse-console")
        
        # Build the file path
        path = f"velinor/stories/{filename}"
        
        try:
            # Try to get existing file
            existing = repo.get_contents(path, ref="main")
            # File exists, update it
            repo.update_file(
                path,
                f"Update story for {filename}",
                content,
                existing.sha,
                branch="main"
            )
            return True, f"Story updated: {filename}"
        except GithubException:
            # File doesn't exist, create it
            repo.create_file(
                path,
                f"Add story for {filename}",
                content,
                branch="main"
            )
            return True, f"Story created: {filename}"
    
    except Exception as e:
        return False, f"Error committing to GitHub: {str(e)}"

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Velinor Glyph Console",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    [data-testid="stSidebar"] { width: 300px; }
    .glyph-card { border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin: 8px 0; }
    .impact-panel { background-color: #f0f2f6; padding: 12px; border-radius: 8px; margin: 8px 0; }
    .related-item { font-size: 12px; color: #666; margin: 4px 0; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING (CACHED)
# ============================================================================

@st.cache_data
def load_datasets():
    """Load all four glyph datasets."""
    # Go up one level from velinor/glyph_console to velinor, then navigate to datasets
    base_path = Path(__file__).parent.parent / "markdowngameinstructions" / "glyphs"
    
    try:
        df_core = pd.read_csv(base_path / "Glyph_Organizer.csv")
        df_fragments = pd.read_csv(base_path / "Glyph_Fragments.csv")
        df_transcendence = pd.read_csv(base_path / "Glyph_Transcendence.csv")
        df_cipher = pd.read_csv(base_path / "cipher_seeds.csv")
        
        return df_core, df_fragments, df_transcendence, df_cipher
    except FileNotFoundError as e:
        st.error(f"Could not load datasets: {e}")
        return None, None, None, None


# Load datasets
df_core, df_fragments, df_transcendence, df_cipher = load_datasets()

if df_core is None:
    st.error("Failed to load glyph datasets. Check file paths.")
    st.stop()

# ============================================================================
# SIDEBAR: FILTERS & CONTROLS
# ============================================================================

st.sidebar.title("🔍 Glyph Console")
st.sidebar.divider()

# Core dataset filters
st.sidebar.subheader("Core Glyphs Filter")
categories = sorted(df_core["Category"].unique())
selected_categories = st.sidebar.multiselect(
    "Categories",
    options=categories,
    default=categories,
    key="category_filter"
)

npc_givers = sorted(df_core["NPC Giver"].dropna().unique())
selected_npcs = st.sidebar.multiselect(
    "NPC Givers",
    options=npc_givers,
    key="npc_filter"
)

# Apply filters
filtered_core = df_core[
    (df_core["Category"].isin(selected_categories))
]

if selected_npcs:
    filtered_core = filtered_core[filtered_core["NPC Giver"].isin(selected_npcs)]

st.sidebar.divider()
st.sidebar.subheader("Dataset Stats")
st.sidebar.metric("Core Glyphs", len(df_core))
st.sidebar.metric("Fragments", len(df_fragments))
st.sidebar.metric("Fusion Glyphs", len(df_transcendence))
st.sidebar.metric("Cipher Seeds", len(df_cipher))

st.sidebar.divider()
st.sidebar.subheader("Navigation")
view_mode = st.sidebar.radio(
    "Select View",
    options=["Central View", "Fragments", "Fusion Glyphs", "Cipher Seeds", "Relationship Graph", "Export"],
    key="view_mode"
)

# ============================================================================
# MAIN CONTENT: CENTRAL VIEW (CORE GLYPHS)
# ============================================================================

if view_mode == "Central View":
    st.title("✨ Velinor Glyph Console - Central Registry")
    st.markdown(f"**Viewing {len(filtered_core)} core glyphs**")
    
    # Initialize session state for story builder selection
    if "selected_story_glyph" not in st.session_state:
        st.session_state.selected_story_glyph = None
    if "last_selected_glyph_name" not in st.session_state:
        st.session_state.last_selected_glyph_name = None
    
    # Search box
    search_term = st.text_input(
        "🔎 Search glyphs by name, NPC, or theme",
        key="core_search"
    )
    
    if search_term:
        filtered_core = filtered_core[
            filtered_core.apply(
                lambda row: search_term.lower() in str(row["Glyph"]).lower() or
                           search_term.lower() in str(row["NPC Giver"]).lower() or
                           search_term.lower() in str(row["Theme"]).lower(),
                axis=1
            )
        ]
    
    # Display glyphs as scrollable table with "Open Story" buttons
    st.subheader("Core Glyphs Registry")
    
    # Create table data
    table_data = []
    
    for idx, (_, row) in enumerate(filtered_core.iterrows()):
        table_data.append({
            "Glyph": row["Glyph"],
            "NPC Giver": row["NPC Giver"],
            "Category": row["Category"],
            "Theme": row["Theme"],
            "Location": row["Location"]
        })
    
    # Display interactive grid with clickable glyph names
    if table_data:
        table_df = pd.DataFrame(table_data)
        
        st.markdown("### 📖 Glyph Registry — Click any glyph name to open Story Builder")
        
        # Create scrollable area using columns and divider
        col_widths = [2, 1.5, 1, 2, 2]
        
        # Header
        h_cols = st.columns(col_widths)
        h_cols[0].markdown("**✍️ Glyph**")
        h_cols[1].markdown("**NPC Giver**")
        h_cols[2].markdown("**Category**")
        h_cols[3].markdown("**Theme**")
        h_cols[4].markdown("**Location**")
        
        st.divider()
        
        # Create scrollable area with container
        with st.container(border=True, height=400):
            for idx, (_, row) in enumerate(table_df.iterrows()):
                # Create clickable row
                row_cols = st.columns(col_widths)
                
                # First column: clickable button styled like text
                glyph_full = df_core[df_core["Glyph"] == row["Glyph"]].iloc[0]
                if row_cols[0].button(
                    row['Glyph'],
                    key=f"glyph_{idx}",
                    use_container_width=True
                ):
                    st.session_state.selected_story_glyph = glyph_full
                    st.rerun()
                
                # Other columns: text display
                row_cols[1].write(row['NPC Giver'])
                row_cols[2].write(row['Category'])
                row_cols[3].write(row['Theme'])
                row_cols[4].write(row['Location'])
    
    # =====================================================================
    # Story Builder Modal (appears when a glyph is selected)
    # =====================================================================
    if st.session_state.selected_story_glyph is not None:
        glyph_row = st.session_state.selected_story_glyph
        idx = hash(glyph_row["Glyph"]) % 1000000  # Use hash for consistent key generation
        
        st.divider()
        st.markdown(f"## ✍️ Story Builder: {glyph_row['Glyph']}")
        
        col_close, col_title = st.columns([1, 5])
        with col_close:
            if st.button("❌ Close", key="close_story_builder"):
                st.session_state.selected_story_glyph = None
                st.rerun()
        
        st.divider()
        
        # Two-column layout for story + dialogue
        col_story, col_dialogue = st.columns(2)

        with col_story:
            story_summary = st.text_area(
                "Story Summary",
                placeholder="Describe the narrative context and what the player experiences when encountering this glyph...",
                height=200,
                key=f"story_summary_{idx}"
            )

        with col_dialogue:
            st.markdown("**Dialogue Sequence**")
            st.markdown("*Alternating NPC/Player lines with narrative functions*")

        # Parse NPC names from the NPC Giver column
        def parse_npc_names(npc_giver_string):
            """Parse NPC names from string like 'Ravi and Nima' or 'Ravi, Nima'"""
            if not npc_giver_string or pd.isna(npc_giver_string):
                return []
            
            # Split by "and" or comma
            names = []
            parts = str(npc_giver_string).replace(" and ", ",").split(",")
            for part in parts:
                name = part.strip()
                if name:
                    names.append(name)
            return names

        npc_giver = glyph_row["NPC Giver"]
        parsed_npcs = parse_npc_names(npc_giver)
        
        # Build speaker options: individual NPCs + combined + Player
        speaker_options = parsed_npcs.copy() if parsed_npcs else ["NPC"]
        if len(parsed_npcs) > 1:
            speaker_options.append(" and ".join(parsed_npcs))
        speaker_options.append("Player")

        # Dialogue Sequence Builder
        num_dialogue_turns = int(st.number_input(
            "How many dialogue turns should there be?",
            min_value=1,
            max_value=20,
            value=3,
            key=f"num_dialogue_turns_{idx}"
        ))

        dialogue_sequence = []
        for i in range(num_dialogue_turns):
            st.markdown(f"#### Dialogue Turn {i+1}")
            
            col_speaker, col_line = st.columns([1.5, 3])
            
            with col_speaker:
                speaker = st.selectbox(
                    "Speaker",
                    options=speaker_options,
                    key=f"speaker_{idx}_{i}"
                )
            
            with col_line:
                dialogue_line = st.text_input(
                    f"{speaker}'s line",
                    placeholder=f"What does {speaker} say?",
                    key=f"dialogue_line_{idx}_{i}"
                )
            
            # Narrative function options with human-readable display
            narrative_options = [
                "reveal_emotion",
                "advance_plot",
                "challenge_player",
                "withhold_truth",
                "provide_clue",
                "mask_fear",
                "offer_comfort",
                "escalate_tension",
                "test_player"
            ]
            
            narrative_function = st.selectbox(
                f"Narrative Function {i+1}",
                options=narrative_options,
                format_func=lambda x: x.replace("_", " ").title(),
                key=f"narr_func_{idx}_{i}"
            )
            
            dialogue_sequence.append({
                "speaker": speaker,
                "line": dialogue_line,
                "narrative_function": narrative_function
            })

        st.subheader("Player Choices")

        num_choices = int(st.number_input(
            "How many choices should the player have?",
            min_value=0,
            max_value=10,
            value=2,
            key=f"num_choices_{idx}"
        ))

        choices_list = []
        for i in range(num_choices):
            choice = st.text_input(
                f"Choice {i+1}",
                placeholder=f"Option {i+1} text...",
                key=f"choice_{idx}_{i+1}"
            )
            choices_list.append(choice)

        # =====================================================================
        # Relational Story Fields
        # =====================================================================
        st.subheader("Relational Story Context")
        st.markdown("*Optional: Add deeper narrative context and relationships*")

        col_rel1, col_rel2 = st.columns(2)
        
        with col_rel1:
            location_context = st.text_area(
                "Location Context",
                placeholder="How does this location shape the encounter?",
                height=80,
                key=f"rel_location_{idx}"
            )
            
            npc_significance = st.text_area(
                "NPC Significance",
                placeholder="What is this NPC's deeper role in the world?",
                height=80,
                key=f"rel_npc_sig_{idx}"
            )
            
            historical_context = st.text_area(
                "Historical Context",
                placeholder="What pre-collapse or post-collapse events led to this?",
                height=80,
                key=f"rel_history_{idx}"
            )
            
            collapse_fragment = st.text_area(
                "Collapse Fragment",
                placeholder="How does this glyph relate to the Collapse event?",
                height=80,
                key=f"rel_collapse_{idx}"
            )

        with col_rel2:
            player_development = st.text_area(
                "Player Development",
                placeholder="How does experiencing this glyph change the player?",
                height=80,
                key=f"rel_player_dev_{idx}"
            )
            
            narrative_function_rel = st.text_area(
                "Narrative Function",
                placeholder="What role does this glyph play in the larger story?",
                height=80,
                key=f"rel_narrative_fn_{idx}"
            )
            
            emotional_stakes = st.text_area(
                "Emotional Stakes",
                placeholder="What emotions or conflicts are at play?",
                height=80,
                key=f"rel_emotional_{idx}"
            )
            
            progression = st.text_area(
                "Progression",
                placeholder="How does this lead to the next arc or chamber?",
                height=80,
                key=f"rel_progression_{idx}"
            )

        # Build preview payload
        preview = {
            "glyph": glyph_row["Glyph"],
            "category": glyph_row["Category"],
            "npc": glyph_row["NPC Giver"],
            "theme": glyph_row["Theme"],
            "location": glyph_row["Location"],
            "story_summary": story_summary,
            "dialogue_sequence": [
                {
                    "speaker": turn["speaker"],
                    "line": turn["line"],
                    "narrative_function": turn["narrative_function"]
                }
                for turn in dialogue_sequence
                if turn["line"]
            ],
            "choices": [c for c in choices_list if c],
            "relational_story": {
                "location_context": location_context,
                "npc_significance": npc_significance,
                "historical_context": historical_context,
                "collapse_fragment": collapse_fragment,
                "player_development": player_development,
                "narrative_function": narrative_function_rel,
                "emotional_stakes": emotional_stakes,
                "progression": progression
            }
        }

        st.markdown("### Formatted Dialogue Preview")
        formatted_dialogue = "\n\n".join([
            f'{turn["speaker"]}: "{turn["line"]}"'
            for turn in dialogue_sequence
            if turn["line"]
        ])
        st.code(formatted_dialogue if formatted_dialogue else "(No dialogue entered yet)")

        st.markdown("### Full JSON Preview")
        st.json(preview)

        if st.button("Confirm Story", key=f"confirm_story_{idx}"):
            if not story_summary:
                st.error("Story Summary is required.")
            elif len([c for c in choices_list if c]) == 0:
                st.error("At least one choice is required.")
            elif len([turn for turn in dialogue_sequence if turn["line"]]) == 0:
                st.error("At least one dialogue line is required.")
            else:
                filename = f"{glyph_row['Glyph'].replace(' ', '_')}.json"
                content = json.dumps(preview, indent=2)
                
                with st.spinner(f"Committing {filename} to GitHub..."):
                    success, message = commit_story_to_repo(filename, content)
                
                if success:
                    st.success(f"✓ {message}")
                    st.info(f"Story saved to: `velinor/stories/{filename}`")
                    st.session_state.selected_story_glyph = None
                else:
                    st.error(f"✗ {message}")
    
    else:
        # Show glyph info when hovering/selected through a different mechanism (display a chart here)
        st.markdown("---")
        st.markdown("*Click a button above to open the story builder for a glyph*")
    
    # Glyph selector
    selected_export_glyph = st.selectbox(
        "Select glyph to export",
        options=df_core["Glyph"].tolist(),
        key="export_select"
    )
    
    if selected_export_glyph:
        glyph_row = df_core[df_core["Glyph"] == selected_export_glyph].iloc[0]
        
        # Compute all relationships
        related_fragments = match_fragments_to_glyph(glyph_row, df_fragments)
        related_fusion = match_fusion_to_glyph(glyph_row, df_transcendence)
        related_cipher = match_cipher_to_glyph(glyph_row, df_cipher)
        
        tone_impact = compute_tone_impact(glyph_row, related_fragments)
        remnants_impact = compute_remnants_impact(glyph_row, related_fragments)
        endgame_impact = compute_endgame_dependencies(glyph_row, df_transcendence)
        emotional_alignment = compute_emotional_alignment(glyph_row)
        
        # Build export
        related = {
            "fragments": related_fragments,
            "fusion": related_fusion,
            "cipher": related_cipher,
            "tone_impact": tone_impact,
            "remnants_impact": remnants_impact,
            "endgame_impact": endgame_impact,
            "emotional_alignment": emotional_alignment
        }
        
        export_json = export_glyph_to_json(glyph_row, related)
        
        # Display JSON
        st.subheader("📋 Export Preview")
        st.json(export_json)
        
        # Download button
        st.divider()
        json_str = json.dumps(export_json, indent=2)
        st.download_button(
            label="⬇️ Download as JSON",
            data=json_str,
            file_name=f"{selected_export_glyph.replace(' ', '_')}_export.json",
            mime="application/json",
            key="download_json"
        )
        
        # Export all button
        st.divider()
        st.subheader("📦 Export All Glyphs")
        
        if st.button("Export all core glyphs as JSON Lines"):
            all_exports = []
            for _, glyph in df_core.iterrows():
                frag = match_fragments_to_glyph(glyph, df_fragments)
                fusion = match_fusion_to_glyph(glyph, df_transcendence)
                cipher = match_cipher_to_glyph(glyph, df_cipher)
                
                related = {
                    "fragments": frag,
                    "fusion": fusion,
                    "cipher": cipher,
                    "tone_impact": compute_tone_impact(glyph, frag),
                    "remnants_impact": compute_remnants_impact(glyph, frag),
                    "endgame_impact": compute_endgame_dependencies(glyph, df_transcendence),
                    "emotional_alignment": compute_emotional_alignment(glyph)
                }
                
                all_exports.append(export_glyph_to_json(glyph, related))
            
            # Create JSONL
            jsonl_str = "\n".join([json.dumps(item) for item in all_exports])
            
            st.download_button(
                label="⬇️ Download all glyphs as JSONL",
                data=jsonl_str,
                file_name="all_glyphs_export.jsonl",
                mime="application/jsonl",
                key="download_jsonl"
            )

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
---
**Velinor Glyph Console** | Integrated glyph management system  
Datasets: Core Glyphs | Fragments | Fusion Glyphs | Cipher Seeds
""")

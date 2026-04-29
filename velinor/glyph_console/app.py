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
import os
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
        # Get GitHub token from Streamlit secrets or environment variable
        github_token = None
        
        # Try Streamlit secrets first (for local/Cloud development)
        if "GITHUB_TOKEN" in st.secrets:
            github_token = st.secrets["GITHUB_TOKEN"]
        # Fall back to environment variable (for CI/CD or alternative deployment)
        elif "GITHUB_TOKEN" in os.environ:
            github_token = os.environ["GITHUB_TOKEN"]
        
        if not github_token:
            return False, "GitHub token not configured. Set GITHUB_TOKEN in Streamlit secrets or as environment variable."
        
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


def load_story_from_repo(filename: str):
    """
    Load a story JSON file from the GitHub repository if it exists.

    Args:
        filename: Name of the file to load (e.g., "Glyph_of_Memory.json")

    Returns:
        tuple: (found: bool, data: dict, message: str)
    """
    try:
        github_token = None

        if "GITHUB_TOKEN" in st.secrets:
            github_token = st.secrets["GITHUB_TOKEN"]
        elif "GITHUB_TOKEN" in os.environ:
            github_token = os.environ["GITHUB_TOKEN"]

        if not github_token:
            return False, {}, "GitHub token not configured for story loading."

        g = Github(github_token)
        repo = g.get_repo("taurinrobinson-wq/saoriverse-console")
        path = f"velinor/stories/{filename}"

        try:
            existing = repo.get_contents(path, ref="main")
            content = existing.decoded_content.decode("utf-8")
            data = json.loads(content)
            return True, data, f"Loaded existing story: {filename}"
        except GithubException:
            return False, {}, f"No existing story found for: {filename}"

    except Exception as e:
        return False, {}, f"Error loading story from GitHub: {str(e)}"

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

        # Clean up any duplicate NPC names in the NPC Giver column (e.g. "Rasha & Rasha")
        def dedup_npc_giver(value):
            if not value or pd.isna(value):
                return value
            text = str(value).replace(" & ", ",").replace(" and ", ",")
            parts = [p.strip() for p in text.split(",") if p.strip()]
            seen = set()
            unique = [p for p in parts if not (p in seen or seen.add(p))]
            if len(unique) == 1:
                return unique[0]
            return " & ".join(unique)

        df_core["NPC Giver"] = df_core["NPC Giver"].apply(dedup_npc_giver)

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
        glyph_name = glyph_row["Glyph"]
        story_filename = f"{glyph_name.replace(' ', '_')}.json"

        if "story_cache" not in st.session_state:
            st.session_state.story_cache = {}

        if glyph_name not in st.session_state.story_cache:
            found_story, loaded_data, load_message = load_story_from_repo(story_filename)
            st.session_state.story_cache[glyph_name] = loaded_data if found_story else {}
            st.session_state[f"story_load_message_{idx}"] = load_message

        loaded_story = st.session_state.story_cache.get(glyph_name, {})
        loaded_dialogue_nodes = loaded_story.get("dialogue_nodes", [])

        # Backward compatibility: convert old linear dialogue_sequence into nodes.
        if not loaded_dialogue_nodes and loaded_story.get("dialogue_sequence"):
            legacy_sequence = loaded_story.get("dialogue_sequence", [])
            for i, turn in enumerate(legacy_sequence):
                loaded_dialogue_nodes.append({
                    "node_id": f"{glyph_name.replace(' ', '_').lower()}_{i + 1}",
                    "speaker": turn.get("speaker", "NPC"),
                    "dialogue": turn.get("dialogue", ""),
                    "narrative_function": turn.get("narrative_function"),
                    "player_subtext": turn.get("player_subtext"),
                    "choices": []
                })
        
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
            story_summary_key = f"story_summary_{idx}"
            if story_summary_key not in st.session_state:
                st.session_state[story_summary_key] = loaded_story.get("story_summary", "")

            story_summary = st.text_area(
                "Story Summary",
                placeholder="Describe the narrative context and what the player experiences when encountering this glyph...",
                height=200,
                key=story_summary_key
            )

        with col_dialogue:
            st.markdown("**Dialogue Nodes**")
            st.markdown("*Branching dialogue with node IDs and per-node choices*")

        load_message_key = f"story_load_message_{idx}"
        if load_message_key in st.session_state:
            st.caption(st.session_state[load_message_key])

        # Dialogue Node Builder
        num_nodes_key = f"num_dialogue_nodes_{idx}"
        if num_nodes_key not in st.session_state:
            st.session_state[num_nodes_key] = len(loaded_dialogue_nodes) if loaded_dialogue_nodes else 3

        num_dialogue_nodes = int(st.number_input(
            "How many dialogue nodes should there be?",
            min_value=1,
            max_value=20,
            key=num_nodes_key
        ))

        npc_name = glyph_row["NPC Giver"]
        dialogue_nodes = []
        
        # Parse NPC names from the NPC Giver column
        def parse_npc_names(npc_giver_string):
            """Parse NPC names from string like 'Ravi and Nima', 'Ravi, Nima', or 'Sera the Herb Novice & Korrin the Gossip'"""
            if not npc_giver_string or pd.isna(npc_giver_string):
                return []
            
            # Split by "&", "and", or comma
            names = []
            text = str(npc_giver_string)
            # Replace different separators with comma
            text = text.replace(" & ", ",").replace(" and ", ",")
            parts = text.split(",")
            for part in parts:
                name = part.strip()
                if name:
                    names.append(name)
            # Deduplicate while preserving order
            seen = set()
            names = [n for n in names if not (n in seen or seen.add(n))]
            return names

        parsed_npcs = parse_npc_names(npc_name)
        
        # Build speaker options: only use NPCs explicitly listed in NPC Giver column
        # Never default to other NPCs - only the ones specified for this glyph
        if parsed_npcs:
            speaker_options = parsed_npcs.copy()
            # Only add combined speaker option if there are multiple NPCs
            if len(parsed_npcs) > 1:
                speaker_options.append(" and ".join(parsed_npcs))
        else:
            # Fallback if no NPC specified
            speaker_options = ["NPC"]
        
        # Always add Player as an option
        speaker_options.append("Player")

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

        player_subtext_options = [
            "seeking_safety",
            "testing_boundaries",
            "avoiding_pain",
            "trying_to_impress",
            "hiding_vulnerability",
            "asserting_control",
            "seeking_connection",
            "distrusting_npc",
            "feeling_overwhelmed",
            "masking_confusion",
            "trying_to_please",
            "pushing_back",
            "dissociating",
            "hoping_for_rescue",
            "preparing_to_withdraw"
        ]

        revelation_options = [
            "none",
            "partial_truth",
            "misdirection",
            "full_truth",
            "withheld_key_detail",
            "emotional_disclosure"
        ]
        
        for i in range(num_dialogue_nodes):
            default_node = loaded_dialogue_nodes[i] if i < len(loaded_dialogue_nodes) else {}
            default_node_id = default_node.get("node_id") or f"{glyph_name.replace(' ', '_').lower()}_{i + 1}"

            st.markdown(f"#### Dialogue Node {i+1}")

            node_id_key = f"node_id_{idx}_{i}"
            if node_id_key not in st.session_state:
                st.session_state[node_id_key] = default_node_id

            node_id = st.text_input(
                f"Node ID {i+1}",
                key=node_id_key,
                placeholder="Unique ID (e.g., sera_1)"
            )
            
            col_speaker, col_line = st.columns([1.5, 3])

            default_speaker = default_node.get("speaker", speaker_options[0])
            speaker_index = speaker_options.index(default_speaker) if default_speaker in speaker_options else 0
            
            with col_speaker:
                speaker = st.selectbox(
                    "Speaker",
                    options=speaker_options,
                    index=speaker_index,
                    key=f"speaker_{idx}_{i}"
                )

            default_dialogue = default_node.get("dialogue", "")
            dialogue_key = f"dialogue_line_{idx}_{i}"
            if dialogue_key not in st.session_state:
                st.session_state[dialogue_key] = default_dialogue
            
            with col_line:
                dialogue_line = st.text_input(
                    "Dialogue",
                    placeholder="What does this speaker say?",
                    key=dialogue_key
                )

            if speaker == "Player":
                default_subtext = default_node.get("player_subtext")
                subtext_index = player_subtext_options.index(default_subtext) if default_subtext in player_subtext_options else 0
                player_subtext = st.selectbox(
                    f"Player Subtext {i+1}",
                    options=player_subtext_options,
                    index=subtext_index,
                    format_func=lambda x: x.replace("_", " ").title(),
                    key=f"player_subtext_{idx}_{i}"
                )
                narrative_function = None
            else:
                default_narrative = default_node.get("narrative_function")
                narrative_index = narrative_options.index(default_narrative) if default_narrative in narrative_options else 0
                narrative_function = st.selectbox(
                    f"Narrative Function {i+1}",
                    options=narrative_options,
                    index=narrative_index,
                    format_func=lambda x: x.replace("_", " ").title(),
                    key=f"narr_func_{idx}_{i}"
                )
                player_subtext = None

            st.markdown(f"**Choices For Node {i+1}**")

            default_choices = default_node.get("choices", [])
            num_node_choices_key = f"num_node_choices_{idx}_{i}"
            if num_node_choices_key not in st.session_state:
                st.session_state[num_node_choices_key] = len(default_choices)

            num_node_choices = int(st.number_input(
                f"How many choices from node {i+1}?",
                min_value=0,
                max_value=10,
                key=num_node_choices_key
            ))

            node_choices = []
            for j in range(num_node_choices):
                default_choice = default_choices[j] if j < len(default_choices) else {}
                default_choice_id = default_choice.get("choice_id") or f"{node_id or default_node_id}_c{j + 1}"

                choice_col_1, choice_col_2 = st.columns(2)
                with choice_col_1:
                    choice_id_key = f"choice_id_{idx}_{i}_{j}"
                    if choice_id_key not in st.session_state:
                        st.session_state[choice_id_key] = default_choice_id
                    choice_id = st.text_input(
                        f"Choice ID {i+1}.{j+1}",
                        key=choice_id_key
                    )

                    choice_text_key = f"choice_text_{idx}_{i}_{j}"
                    if choice_text_key not in st.session_state:
                        st.session_state[choice_text_key] = default_choice.get("text", "")
                    choice_text = st.text_input(
                        f"Choice Text {i+1}.{j+1}",
                        key=choice_text_key,
                        placeholder="What option can the player choose?"
                    )

                    choice_subtext_default = default_choice.get("subtext")
                    choice_subtext_index = player_subtext_options.index(choice_subtext_default) if choice_subtext_default in player_subtext_options else 0
                    choice_subtext = st.selectbox(
                        f"Choice Subtext {i+1}.{j+1}",
                        options=player_subtext_options,
                        index=choice_subtext_index,
                        format_func=lambda x: x.replace("_", " ").title(),
                        key=f"choice_subtext_{idx}_{i}_{j}"
                    )

                with choice_col_2:
                    revelation_default = default_choice.get("revelation", "none")
                    revelation_index = revelation_options.index(revelation_default) if revelation_default in revelation_options else 0
                    revelation = st.selectbox(
                        f"Revelation Tag {i+1}.{j+1}",
                        options=revelation_options,
                        index=revelation_index,
                        format_func=lambda x: x.replace("_", " ").title(),
                        key=f"choice_revelation_{idx}_{i}_{j}"
                    )

                    consequence_key = f"choice_consequence_{idx}_{i}_{j}"
                    if consequence_key not in st.session_state:
                        st.session_state[consequence_key] = default_choice.get("consequence", "") or ""
                    consequence = st.text_input(
                        f"Consequence Tag {i+1}.{j+1}",
                        key=consequence_key,
                        placeholder="Optional consequence tag"
                    )

                    next_node_key = f"choice_next_node_{idx}_{i}_{j}"
                    if next_node_key not in st.session_state:
                        st.session_state[next_node_key] = default_choice.get("next_node", "")
                    next_node = st.text_input(
                        f"Next Node {i+1}.{j+1}",
                        key=next_node_key,
                        placeholder="Target node_id"
                    )

                node_choices.append({
                    "choice_id": choice_id,
                    "text": choice_text,
                    "subtext": choice_subtext,
                    "revelation": revelation,
                    "consequence": consequence.strip() if consequence else None,
                    "next_node": next_node
                })

            dialogue_nodes.append({
                "node_id": node_id,
                "speaker": speaker,
                "dialogue": dialogue_line,
                "narrative_function": narrative_function,
                "player_subtext": player_subtext,
                "choices": [
                    choice for choice in node_choices
                    if choice["text"]
                ]
            })

        # =====================================================================
        # Relational Story Fields
        # =====================================================================
        st.subheader("Relational Story Context")
        st.markdown("*Optional: Add deeper narrative context and relationships*")

        col_rel1, col_rel2 = st.columns(2)
        rel_story = loaded_story.get("relational_story", {})
        
        with col_rel1:
            rel_location_key = f"rel_location_{idx}"
            if rel_location_key not in st.session_state:
                st.session_state[rel_location_key] = rel_story.get("location_context", "")
            location_context = st.text_area(
                "Location Context",
                placeholder="How does this location shape the encounter?",
                height=80,
                key=rel_location_key
            )
            
            rel_npc_sig_key = f"rel_npc_sig_{idx}"
            if rel_npc_sig_key not in st.session_state:
                st.session_state[rel_npc_sig_key] = rel_story.get("npc_significance", "")
            npc_significance = st.text_area(
                "NPC Significance",
                placeholder="What is this NPC's deeper role in the world?",
                height=80,
                key=rel_npc_sig_key
            )
            
            rel_history_key = f"rel_history_{idx}"
            if rel_history_key not in st.session_state:
                st.session_state[rel_history_key] = rel_story.get("historical_context", "")
            historical_context = st.text_area(
                "Historical Context",
                placeholder="What pre-collapse or post-collapse events led to this?",
                height=80,
                key=rel_history_key
            )
            
            rel_collapse_key = f"rel_collapse_{idx}"
            if rel_collapse_key not in st.session_state:
                st.session_state[rel_collapse_key] = rel_story.get("collapse_fragment", "")
            collapse_fragment = st.text_area(
                "Collapse Fragment",
                placeholder="How does this glyph relate to the Collapse event?",
                height=80,
                key=rel_collapse_key
            )

        with col_rel2:
            rel_player_dev_key = f"rel_player_dev_{idx}"
            if rel_player_dev_key not in st.session_state:
                st.session_state[rel_player_dev_key] = rel_story.get("player_development", "")
            player_development = st.text_area(
                "Player Development",
                placeholder="How does experiencing this glyph change the player?",
                height=80,
                key=rel_player_dev_key
            )
            
            rel_narr_fn_key = f"rel_narrative_fn_{idx}"
            if rel_narr_fn_key not in st.session_state:
                st.session_state[rel_narr_fn_key] = rel_story.get("narrative_function", "")
            narrative_function_rel = st.text_area(
                "Narrative Function",
                placeholder="What role does this glyph play in the larger story?",
                height=80,
                key=rel_narr_fn_key
            )
            
            rel_emotional_key = f"rel_emotional_{idx}"
            if rel_emotional_key not in st.session_state:
                st.session_state[rel_emotional_key] = rel_story.get("emotional_stakes", "")
            emotional_stakes = st.text_area(
                "Emotional Stakes",
                placeholder="What emotions or conflicts are at play?",
                height=80,
                key=rel_emotional_key
            )
            
            rel_progression_key = f"rel_progression_{idx}"
            if rel_progression_key not in st.session_state:
                st.session_state[rel_progression_key] = rel_story.get("progression", "")
            progression = st.text_area(
                "Progression",
                placeholder="How does this lead to the next arc or chamber?",
                height=80,
                key=rel_progression_key
            )

        # Build preview payload
        preview = {
            "glyph": glyph_row["Glyph"],
            "category": glyph_row["Category"],
            "npc": glyph_row["NPC Giver"],
            "theme": glyph_row["Theme"],
            "location": glyph_row["Location"],
            "story_summary": story_summary,
            "dialogue_nodes": [
                {
                    "node_id": node["node_id"],
                    "speaker": node["speaker"],
                    "dialogue": node["dialogue"],
                    "narrative_function": node["narrative_function"],
                    "player_subtext": node["player_subtext"],
                    "choices": node["choices"]
                }
                for node in dialogue_nodes
                if node["dialogue"]
            ],
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
            f'{node["node_id"]} | {node["speaker"]}: "{node["dialogue"]}" (choices: {len(node["choices"])})'
            for node in preview["dialogue_nodes"]
        ])
        st.code(formatted_dialogue if formatted_dialogue else "(No dialogue entered yet)")

        st.markdown("### Full JSON Preview")
        st.json(preview)

        st.markdown("### Branching Integrity Check")
        preview_nodes = preview.get("dialogue_nodes", [])
        node_ids = [node.get("node_id", "").strip() for node in preview_nodes]
        non_empty_node_ids = [node_id for node_id in node_ids if node_id]
        node_id_set = set(non_empty_node_ids)

        duplicate_node_ids = sorted({node_id for node_id in non_empty_node_ids if non_empty_node_ids.count(node_id) > 1})
        missing_node_id_indices = [i + 1 for i, node_id in enumerate(node_ids) if not node_id]

        edges = []
        dangling_references = set()
        choices_missing_next_node = []

        for node in preview_nodes:
            source_id = (node.get("node_id") or "").strip()
            for choice in node.get("choices", []):
                target_id = (choice.get("next_node") or "").strip()
                choice_id = (choice.get("choice_id") or "").strip()

                if not target_id:
                    if choice.get("text"):
                        choices_missing_next_node.append(choice_id or f"{source_id}:unnamed_choice")
                    continue

                edges.append((source_id, target_id, choice_id))
                if target_id not in node_id_set:
                    dangling_references.add(target_id)

        unreachable_nodes = []
        if non_empty_node_ids:
            graph = nx.DiGraph()
            graph.add_nodes_from(non_empty_node_ids)
            graph.add_edges_from([(src, dst) for src, dst, _ in edges if src and dst and src in node_id_set and dst in node_id_set])

            start_node = non_empty_node_ids[0]
            reachable = {start_node}
            reachable.update(nx.descendants(graph, start_node))
            unreachable_nodes = sorted(node_id for node_id in node_id_set if node_id not in reachable)

            # Visual map of branching nodes and transitions.
            if graph.number_of_nodes() > 0:
                pos = nx.spring_layout(graph, seed=42)

                edge_x = []
                edge_y = []
                for src, dst in graph.edges():
                    x0, y0 = pos[src]
                    x1, y1 = pos[dst]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])

                edge_trace = go.Scatter(
                    x=edge_x,
                    y=edge_y,
                    line={"width": 1, "color": "#888"},
                    hoverinfo="none",
                    mode="lines"
                )

                node_x = []
                node_y = []
                node_text = []
                for node_id in graph.nodes():
                    x, y = pos[node_id]
                    node_x.append(x)
                    node_y.append(y)
                    out_degree = graph.out_degree(node_id)
                    in_degree = graph.in_degree(node_id)
                    node_text.append(f"{node_id}<br>out: {out_degree}, in: {in_degree}")

                node_trace = go.Scatter(
                    x=node_x,
                    y=node_y,
                    mode="markers+text",
                    text=list(graph.nodes()),
                    textposition="top center",
                    hovertext=node_text,
                    hoverinfo="text",
                    marker={"size": 16, "color": "#2E86DE", "line": {"width": 1, "color": "#1B4F72"}}
                )

                fig = go.Figure(data=[edge_trace, node_trace])
                fig.update_layout(
                    showlegend=False,
                    margin={"l": 20, "r": 20, "t": 20, "b": 20},
                    xaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
                    yaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
                    height=380
                )
                st.plotly_chart(fig, use_container_width=True)

        if missing_node_id_indices:
            st.error(f"Missing node_id on node(s): {', '.join(str(i) for i in missing_node_id_indices)}")
        if duplicate_node_ids:
            st.error(f"Duplicate node_id values: {', '.join(duplicate_node_ids)}")
        if dangling_references:
            st.error(f"Choices reference unknown next_node values: {', '.join(sorted(dangling_references))}")
        if unreachable_nodes:
            st.warning(f"Unreachable node(s) from start node: {', '.join(unreachable_nodes)}")
        if choices_missing_next_node:
            st.info(f"Choices missing next_node: {', '.join(choices_missing_next_node)}")

        if not any([missing_node_id_indices, duplicate_node_ids, dangling_references, unreachable_nodes]):
            st.success("Branching structure looks consistent: IDs are unique, references resolve, and all nodes are reachable from the start node.")

        if st.button("Confirm Story", key=f"confirm_story_{idx}"):
            if not story_summary:
                st.error("Story Summary is required.")
            elif len(preview["dialogue_nodes"]) == 0:
                st.error("At least one dialogue turn with content is required.")
            elif missing_node_id_indices or duplicate_node_ids or dangling_references:
                st.error("Fix branching integrity errors before saving (missing/duplicate node IDs or invalid next_node references).")
            else:
                filename = f"{glyph_row['Glyph'].replace(' ', '_')}.json"
                content = json.dumps(preview, indent=2)
                
                with st.spinner(f"Committing {filename} to GitHub..."):
                    success, message = commit_story_to_repo(filename, content)
                
                if success:
                    st.session_state.story_cache[glyph_row["Glyph"]] = preview
                    st.success(f"✓ {message}")
                    st.info(f"Story saved to: `velinor/stories/{filename}`")
                    # Sync export section to this glyph
                    st.session_state.last_edited_glyph = glyph_row["Glyph"]
                    st.session_state.selected_story_glyph = None
                else:
                    st.error(f"✗ {message}")
    
    else:
        # Show glyph info when hovering/selected through a different mechanism (display a chart here)
        st.markdown("---")
        st.markdown("*Click a button above to open the story builder for a glyph*")
    
    # Glyph selector (synced with story builder)
    glyph_options = df_core["Glyph"].tolist()
    
    # 1. SYNC FIRST - Update export selection if a glyph was just edited
    if "last_edited_glyph" in st.session_state:
        if st.session_state.last_edited_glyph in glyph_options:
            st.session_state.export_glyph_selection = st.session_state.last_edited_glyph
        # Clear the flag so it only syncs once
        del st.session_state.last_edited_glyph
    
    # 2. THEN INITIALIZE - Set up export selection state if needed
    if "export_glyph_selection" not in st.session_state:
        st.session_state.export_glyph_selection = glyph_options[0] if glyph_options else None
    
    # 3. VALIDATE - Ensure selection is valid and in options
    if st.session_state.export_glyph_selection not in glyph_options:
        st.session_state.export_glyph_selection = glyph_options[0] if glyph_options else None
    
    # 4. RENDER - Create selectbox with synced glyph
    selected_export_glyph = st.selectbox(
        "Select glyph to export",
        options=glyph_options,
        index=glyph_options.index(st.session_state.export_glyph_selection) if st.session_state.export_glyph_selection in glyph_options else 0,
        key="export_glyph_selection"
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

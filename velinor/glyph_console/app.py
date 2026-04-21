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
    base_path = Path("velinor/markdowngameinstructions/glyphs")
    
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
    
    # Display as searchable table
    st.subheader("Core Glyphs Registry")
    
    # Create display dataframe (simplified columns)
    display_df = filtered_core[["Category", "Glyph", "NPC Giver", "Theme", "Location"]].copy()
    display_df["View Details"] = "➡️"
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400,
        key="core_glyphs_table"
    )
    
    # Glyph detail selector
    st.divider()
    st.subheader("📋 Glyph Details")
    
    glyph_names = ["Select a glyph..."] + filtered_core["Glyph"].tolist()
    selected_glyph = st.selectbox("Choose glyph to view", glyph_names, key="glyph_select")
    
    if selected_glyph != "Select a glyph...":
        glyph_row = df_core[df_core["Glyph"] == selected_glyph].iloc[0]
        
        # Main glyph info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Glyph**: {glyph_row['Glyph']}")
            st.markdown(f"**Category**: `{glyph_row['Category']}`")
        with col2:
            st.markdown(f"**NPC Giver**: {glyph_row['NPC Giver']}")
            st.markdown(f"**Theme**: {glyph_row['Theme']}")
        with col3:
            st.markdown(f"**Location**: {glyph_row['Location']}")
        
        st.divider()
        
        # Storyline
        st.subheader("📖 Storyline")
        st.write(glyph_row["Storyline"])
        
        st.divider()
        
        # Relationships & Impact
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("🔗 Related Content")
            
            # Related fragments
            related_fragments = match_fragments_to_glyph(glyph_row, df_fragments)
            if not related_fragments.empty:
                st.markdown("**Related Fragments**")
                for _, frag in related_fragments.head(3).iterrows():
                    st.markdown(f"""
                    <div class="related-item">
                    • **{frag['Fragment_ID']}** - {frag['NPC_Name']} ({frag['Biome']})
                    </div>
                    """, unsafe_allow_html=True)
            
            # Related fusion glyphs
            related_fusion = match_fusion_to_glyph(glyph_row, df_transcendence)
            if not related_fusion.empty:
                st.markdown("**Leads to Fusion Glyphs**")
                for _, fusion in related_fusion.iterrows():
                    st.markdown(f"""
                    <div class="related-item">
                    • **{fusion['Glyph']}** - {fusion['NPC Receiver']}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Related cipher seeds
            related_cipher = match_cipher_to_glyph(glyph_row, df_cipher)
            if not related_cipher.empty:
                st.markdown("**Related Cipher Seeds**")
                for _, cipher in related_cipher.head(2).iterrows():
                    st.markdown(f"""
                    <div class="related-item">
                    • {cipher['category']} - "{cipher['phrase'][:50]}..."
                    </div>
                    """, unsafe_allow_html=True)
        
        with col_right:
            st.subheader("📊 Impact Analysis")
            
            # Compute impacts
            tone_impact = compute_tone_impact(glyph_row, related_fragments)
            remnants_impact = compute_remnants_impact(glyph_row, related_fragments)
            endgame_impact = compute_endgame_dependencies(glyph_row, df_transcendence)
            emotional_alignment = compute_emotional_alignment(glyph_row)
            
            # TONE Impact
            st.markdown("**TONE Impact**")
            tone_df = pd.DataFrame(
                list(tone_impact.items()),
                columns=["Stat", "Delta"]
            )
            st.dataframe(tone_df, use_container_width=True, hide_index=True)
            
            # REMNANTS Impact
            st.markdown("**REMNANTS Impact**")
            st.markdown(f"• **Primary NPC**: {remnants_impact['npc_name']}")
            st.markdown(f"• **Trust Delta**: +{remnants_impact['trust_delta']:.2f}")
            if remnants_impact['related_npcs']:
                st.markdown(f"• **Related NPCs**: {', '.join(remnants_impact['related_npcs'][:3])}")
            
            # Endgame Impact
            if endgame_impact['contributes_to_fusion']:
                st.markdown("**Endgame Impact**")
                for fusion in endgame_impact['contributes_to_fusion']:
                    st.markdown(f"• Prerequisite for: **{fusion}**")
                if endgame_impact['chamber_type']:
                    st.markdown(f"• Chamber Type: `{endgame_impact['chamber_type']}`")
        
        # Emotional Alignment
        st.divider()
        st.subheader("🎯 Emotional Alignment")
        
        alignment_df = pd.DataFrame(
            list(emotional_alignment.items()),
            columns=["Category", "Alignment"]
        )
        
        fig = px.bar(
            alignment_df,
            x="Category",
            y="Alignment",
            color="Alignment",
            title="Emotional System Alignment",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # =====================================================================
        # ✍️ STORY BUILDER
        # =====================================================================
        st.divider()
        with st.expander("✍️ Story Builder", expanded=True):
            st.markdown("Author the story experience for this glyph encounter.")

            # Two-column layout for story + dialogue
            col_story, col_dialogue = st.columns(2)

            with col_story:
                story_summary = st.text_area(
                    "Story Summary",
                    placeholder="Describe the narrative context and what the player experiences when encountering this glyph...",
                    height=200,
                    key="story_summary"
                )

            with col_dialogue:
                dialogue_text = st.text_area(
                    "Dialogue",
                    placeholder="What does the NPC say? Include key dialogue that conveys the glyph's meaning...",
                    height=200,
                    key="dialogue_text"
                )

            st.subheader("Player Choices")

            num_choices = int(st.number_input(
                "How many choices should the player have?",
                min_value=0,
                max_value=10,
                value=2,
                key="num_choices"
            ))

            choices_list = []
            for i in range(num_choices):
                choice = st.text_input(
                    f"Choice {i+1}",
                    placeholder=f"Option {i+1} text...",
                    key=f"choice_{i+1}"
                )
                choices_list.append(choice)

            # Build preview payload
            preview = {
                "glyph": glyph_row["Glyph"],
                "category": glyph_row["Category"],
                "npc": glyph_row["NPC Giver"],
                "theme": glyph_row["Theme"],
                "location": glyph_row["Location"],
                "story_summary": story_summary,
                "dialogue": dialogue_text,
                "choices": [c for c in choices_list if c],
            }

            st.markdown("### Preview")
            st.json(preview)

            if st.button("Confirm Story", key="confirm_story"):
                if not story_summary or not dialogue_text:
                    st.error("Story Summary and Dialogue are required.")
                elif len([c for c in choices_list if c]) == 0:
                    st.error("At least one choice is required.")
                else:
                    filename = f"{glyph_row['Glyph'].replace(' ', '_')}.json"
                    content = json.dumps(preview, indent=2)
                    
                    with st.spinner(f"Committing {filename} to GitHub..."):
                        success, message = commit_story_to_repo(filename, content)
                    
                    if success:
                        st.success(f"✓ {message}")
                        st.info(f"Story saved to: `velinor/stories/{filename}`")
                    else:
                        st.error(f"✗ {message}")


# ============================================================================
# FRAGMENTS VIEW
# ============================================================================

elif view_mode == "Fragments":
    st.title("🧩 Glyph Fragments")
    st.markdown(f"**{len(df_fragments)} fragments available**")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        frag_biomes = st.multiselect(
            "Biomes",
            options=sorted(df_fragments["Biome"].unique()),
            key="frag_biome_filter"
        )
    with col2:
        frag_npcs = st.multiselect(
            "Fragment NPCs",
            options=sorted(df_fragments["NPC_Name"].unique()),
            key="frag_npc_filter"
        )
    with col3:
        frag_focus = st.text_input("Search emotional focus", key="frag_focus_filter")
    
    # Apply filters
    frag_filtered = df_fragments.copy()
    if frag_biomes:
        frag_filtered = frag_filtered[frag_filtered["Biome"].isin(frag_biomes)]
    if frag_npcs:
        frag_filtered = frag_filtered[frag_filtered["NPC_Name"].isin(frag_npcs)]
    if frag_focus:
        frag_filtered = frag_filtered[
            frag_filtered["Emotional_Focus"].str.contains(frag_focus, case=False, na=False)
        ]
    
    # Display table
    display_frag = frag_filtered[[
        "Fragment_ID", "NPC_Name", "Biome", "Ability_Gained", "Emotional_Focus"
    ]].copy()
    
    st.dataframe(display_frag, use_container_width=True, height=400)
    
    # Fragment detail
    if not frag_filtered.empty:
        st.divider()
        selected_frag_id = st.selectbox(
            "Select fragment for details",
            options=frag_filtered["Fragment_ID"].tolist(),
            key="frag_select"
        )
        
        if selected_frag_id:
            frag_row = df_fragments[df_fragments["Fragment_ID"] == selected_frag_id].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Fragment**: {frag_row['Fragment_ID']}")
                st.markdown(f"**NPC**: {frag_row['NPC_Name']}")
                st.markdown(f"**Archetype**: {frag_row['NPC_Archetype']}")
            with col2:
                st.markdown(f"**Biome**: {frag_row['Biome']}")
                st.markdown(f"**Ability Gained**: {frag_row['Ability_Gained']}")
                st.markdown(f"**Emotional Focus**: {frag_row['Emotional_Focus']}")
            
            st.divider()
            st.subheader("Storyline")
            st.write(frag_row["Storyline"])


# ============================================================================
# FUSION GLYPHS VIEW
# ============================================================================

elif view_mode == "Fusion Glyphs":
    st.title("🔮 Fusion Glyphs (Transcendence)")
    st.markdown(f"**{len(df_transcendence)} fusion glyphs available**")
    
    # Filter by theme
    fusion_themes = st.multiselect(
        "Filter by Theme",
        options=sorted(df_transcendence["Theme"].unique()),
        key="fusion_theme_filter"
    )
    
    fusion_filtered = df_transcendence.copy()
    if fusion_themes:
        fusion_filtered = fusion_filtered[fusion_filtered["Theme"].isin(fusion_themes)]
    
    # Display table
    display_fusion = fusion_filtered[[
        "Category", "Theme", "NPC Receiver", "Glyph", "Location"
    ]].copy()
    
    st.dataframe(display_fusion, use_container_width=True, height=400)
    
    # Fusion detail
    if not fusion_filtered.empty:
        st.divider()
        selected_fusion = st.selectbox(
            "Select fusion glyph for details",
            options=fusion_filtered["Glyph"].tolist(),
            key="fusion_select"
        )
        
        if selected_fusion:
            fusion_row = df_transcendence[df_transcendence["Glyph"] == selected_fusion].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Glyph**: {fusion_row['Glyph']}")
                st.markdown(f"**Theme**: {fusion_row['Theme']}")
                st.markdown(f"**NPC Receiver**: {fusion_row['NPC Receiver']}")
            with col2:
                st.markdown(f"**Location**: {fusion_row['Location']}")
                st.markdown(f"**Category**: {fusion_row['Category']}")
            
            st.divider()
            st.subheader("Storyline & Prerequisites")
            st.write(fusion_row["Storyline"])


# ============================================================================
# CIPHER SEEDS VIEW
# ============================================================================

elif view_mode == "Cipher Seeds":
    st.title("🔐 Cipher Seeds")
    st.markdown(f"**{len(df_cipher)} cipher seeds available**")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        cipher_domains = st.multiselect(
            "Domains",
            options=sorted(df_cipher["domain"].unique()),
            key="cipher_domain_filter"
        )
    with col2:
        cipher_categories = st.multiselect(
            "Categories",
            options=sorted(df_cipher["category"].unique()),
            key="cipher_cat_filter"
        )
    
    cipher_filtered = df_cipher.copy()
    if cipher_domains:
        cipher_filtered = cipher_filtered[cipher_filtered["domain"].isin(cipher_domains)]
    if cipher_categories:
        cipher_filtered = cipher_filtered[cipher_filtered["category"].isin(cipher_categories)]
    
    # Display table
    display_cipher = cipher_filtered[[
        "domain", "category", "phrase", "first_view_display"
    ]].copy()
    
    st.dataframe(display_cipher, use_container_width=True, height=400)
    
    # Cipher detail
    if not cipher_filtered.empty:
        st.divider()
        selected_cipher_idx = st.selectbox(
            "Select cipher seed for details",
            options=range(len(cipher_filtered)),
            format_func=lambda i: cipher_filtered.iloc[i]["phrase"][:50],
            key="cipher_select"
        )
        
        if selected_cipher_idx is not None:
            cipher_row = cipher_filtered.iloc[selected_cipher_idx]
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Domain**: {cipher_row['domain']}")
                st.markdown(f"**Category**: {cipher_row['category']}")
            with col2:
                st.markdown(f"**Display**: `{cipher_row['first_view_display']}`")
            
            st.divider()
            st.subheader("Phrase")
            st.markdown(f"> {cipher_row['phrase']}")
            
            st.subheader("Obfuscation")
            st.code(cipher_row['first_view_obfuscation_numeric'])


# ============================================================================
# RELATIONSHIP GRAPH VIEW
# ============================================================================

elif view_mode == "Relationship Graph":
    st.title("🌐 Relationship Graph")
    
    # Build graph
    with st.spinner("Building relationship graph..."):
        G = build_relationship_graph(df_core, df_fragments, df_transcendence, df_cipher)
        stats = get_graph_stats(G)
    
    # Display stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Nodes", stats["total_nodes"])
    with col2:
        st.metric("Total Edges", stats["total_edges"])
    with col3:
        st.metric("Graph Density", f"{stats['density']:.3f}")
    with col4:
        st.metric("Avg Degree", f"{stats['avg_degree']:.1f}")
    
    st.divider()
    
    # Graph visualization options
    st.subheader("⚙️ Graph Filters")
    
    col1, col2 = st.columns(2)
    with col1:
        node_type_filter = st.multiselect(
            "Node Types to Display",
            options=stats["node_types"],
            default=stats["node_types"]
        )
    with col2:
        min_edges = st.slider("Minimum edges to show node", min_value=0, max_value=10, value=0)
    
    # Filter graph
    G_filtered = G.copy()
    nodes_to_remove = [
        node for node, attr in G_filtered.nodes(data=True)
        if attr.get("node_type") not in node_type_filter
        or G_filtered.degree(node) < min_edges
    ]
    G_filtered.remove_nodes_from(nodes_to_remove)
    
    # Layout and visualization
    st.markdown("""
    **Graph Visualization** (Node size = connections, Color = node type)
    """)
    
    # Create simple network visualization using plotly
    try:
        pos = nx.spring_layout(G_filtered, k=2, iterations=50, seed=42)
        
        # Prepare edges
        edge_x = []
        edge_y = []
        for edge in G_filtered.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            mode='lines',
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            showlegend=False
        )
        
        # Prepare nodes
        node_x = []
        node_y = []
        node_sizes = []
        node_colors = []
        node_labels = []
        
        color_map = {
            "glyph": "blue",
            "npc": "red",
            "category": "green",
            "biome": "orange",
            "theme": "purple",
            "emotion": "pink",
            "cipher": "brown"
        }
        
        for node in G_filtered.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            degree = G_filtered.degree(node)
            node_sizes.append(max(10, degree * 2))
            
            node_type = G_filtered.nodes[node].get("node_type", "unknown")
            node_colors.append(color_map.get(node_type, "gray"))
            
            label = G_filtered.nodes[node].get("label", node)
            node_labels.append(label[:20])
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line_width=2,
                opacity=0.8
            ),
            text=node_labels,
            textposition="top center",
            textfont=dict(size=8),
            hovertext=node_labels,
            hoverinfo="text",
            showlegend=False
        )
        
        fig = go.Figure(data=[edge_trace, node_trace])
        fig.update_layout(
            title="Glyph Relationship Network",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Could not render graph: {e}")


# ============================================================================
# EXPORT VIEW
# ============================================================================

elif view_mode == "Export":
    st.title("📤 Export Glyphs")
    
    st.markdown("""
    Export selected glyphs to JSON format with all relationships and impact data.
    """)
    
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

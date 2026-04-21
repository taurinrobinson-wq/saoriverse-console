"""
Glyph Console Utilities
=======================

Helper functions for cross-dataset matching, impact analysis,
and relationship graph building.
"""

import pandas as pd
import networkx as nx
from typing import List, Dict, Set, Tuple, Any
from collections import defaultdict


def match_fragments_to_glyph(glyph_row: Dict, df_fragments: pd.DataFrame) -> pd.DataFrame:
    """Find fragments related to a given core glyph.
    
    Match by:
    - NPC name (glyph's NPC Giver vs fragment's NPC_Name)
    - Biome (glyph's Location category vs fragment's Biome)
    - Emotional focus (glyph's Theme vs fragment's Emotional_Focus)
    """
    matches = []
    
    npc_giver = str(glyph_row.get("NPC Giver", "")).strip()
    theme = str(glyph_row.get("Theme", "")).strip().lower()
    location = str(glyph_row.get("Location", "")).strip().lower()
    
    # Infer biome from location
    biome_keywords = {
        "desert": ["desert", "sand", "dune", "oasis"],
        "mountain": ["mountain", "peak", "peak", "alpine", "snow"],
        "forest": ["forest", "wood", "tree", "grove"],
        "aquatic": ["aquatic", "water", "sea", "river", "ferry"],
        "market": ["market", "plaza", "stall", "trade"],
        "village": ["village", "shrine", "settlement"]
    }
    
    inferred_biomes = set()
    for biome, keywords in biome_keywords.items():
        if any(kw in location for kw in keywords):
            inferred_biomes.add(biome)
    
    for _, fragment in df_fragments.iterrows():
        score = 0
        
        # NPC match (highest weight)
        if npc_giver and str(fragment.get("NPC_Name", "")).strip() == npc_giver:
            score += 3
        
        # Biome match
        frag_biome = str(fragment.get("Biome", "")).strip().lower()
        if frag_biome in inferred_biomes:
            score += 2
        
        # Emotional focus match
        frag_focus = str(fragment.get("Emotional_Focus", "")).strip().lower()
        if frag_focus and any(word in theme for word in frag_focus.split("/")):
            score += 1
        
        if score > 0:
            matches.append((score, fragment))
    
    # Sort by score descending
    matches.sort(key=lambda x: x[0], reverse=True)
    return pd.DataFrame([m[1] for m in matches])


def match_fusion_to_glyph(glyph_row: Dict, df_transcendence: pd.DataFrame) -> pd.DataFrame:
    """Find fusion glyphs that list this glyph as a prerequisite.
    
    Parse the Storyline field to extract prerequisite glyph names.
    """
    matches = []
    glyph_name = str(glyph_row.get("Glyph", "")).strip()
    
    for _, fusion in df_transcendence.iterrows():
        storyline = str(fusion.get("Storyline", "")).lower()
        
        # Check if this glyph is mentioned as a prerequisite
        if glyph_name.lower() in storyline:
            matches.append(fusion)
    
    return pd.DataFrame(matches)


def match_cipher_to_glyph(glyph_row: Dict, df_cipher: pd.DataFrame) -> pd.DataFrame:
    """Find cipher seeds related to a glyph.
    
    Match by:
    - Theme (glyph's Theme vs cipher's category)
    - Emotional category (from glyph's Theme)
    - NPC (if mentioned in storyline)
    """
    matches = []
    
    theme = str(glyph_row.get("Theme", "")).strip().lower()
    category = str(glyph_row.get("Category", "")).strip().lower()
    npc = str(glyph_row.get("NPC Giver", "")).strip().lower()
    
    for _, cipher in df_cipher.iterrows():
        score = 0
        
        cipher_category = str(cipher.get("category", "")).strip().lower()
        cipher_phrase = str(cipher.get("phrase", "")).strip().lower()
        cipher_domain = str(cipher.get("domain", "")).strip().lower()
        
        # Theme/category match
        if theme in cipher_category or category in cipher_category:
            score += 2
        
        # Emotional resonance (keywords in phrase)
        emotional_keywords = ["memory", "loss", "coherence", "presence", "abandonment", 
                             "legacy", "sovereignty", "witness", "ache", "collapse"]
        for kw in emotional_keywords:
            if kw in theme and kw in cipher_phrase:
                score += 1
        
        # Domain match (Pre-Collapse, Post-Collapse, etc.)
        if "velinor" in npc and "velinor" in cipher_domain.lower():
            score += 1
        
        if score > 0:
            matches.append((score, cipher))
    
    matches.sort(key=lambda x: x[0], reverse=True)
    return pd.DataFrame([m[1] for m in matches])


def compute_tone_impact(glyph_row: Dict, df_fragments: pd.DataFrame = None) -> Dict[str, float]:
    """Compute TONE stat impact based on glyph category and fragments.
    
    Base impact by category:
    - Collapse: -0.2 to -0.05
    - Ache: -0.1 to +0.1
    - Sovereignty: +0.05 to +0.2
    - Presence: +0.1 to +0.3
    - Trust: +0.15 to +0.3
    - Legacy: +0.2 to +0.4
    
    Then apply fragment effects.
    """
    tone_impact = {
        "courage": 0.0,
        "wisdom": 0.0,
        "empathy": 0.0,
        "resolve": 0.0
    }
    
    category = str(glyph_row.get("Category", "")).strip().lower()
    
    # Base category impacts
    category_impacts = {
        "collapse": {"resolve": -0.2, "wisdom": -0.1},
        "ache": {"empathy": -0.05, "courage": -0.1},
        "sovereignty": {"courage": 0.15, "resolve": 0.1},
        "presence": {"empathy": 0.25, "wisdom": 0.15},
        "trust": {"empathy": 0.25, "wisdom": 0.1},
        "legacy": {"wisdom": 0.2, "empathy": 0.15},
        "transcendence": {"empathy": 0.3, "wisdom": 0.25}
    }
    
    for cat, impacts in category_impacts.items():
        if cat in category:
            tone_impact.update(impacts)
    
    # Apply fragment effects if provided
    if df_fragments is not None and not df_fragments.empty:
        for _, fragment in df_fragments.head(3).iterrows():
            # Extract ability gains from fragment
            ability_gained = str(fragment.get("Ability_Gained", "")).lower()
            if "observation" in ability_gained:
                tone_impact["wisdom"] += 0.05
            if "empathy" in ability_gained:
                tone_impact["empathy"] += 0.05
            if "authority" in ability_gained:
                tone_impact["resolve"] += 0.05
            if "resolve" in ability_gained:
                tone_impact["resolve"] += 0.05
    
    return tone_impact


def compute_remnants_impact(glyph_row: Dict, df_fragments: pd.DataFrame = None) -> Dict[str, Any]:
    """Compute REMNANTS NPC impact based on glyph giver and fragments.
    
    Returns:
    - npc_name: Primary NPC giver
    - trust_delta: Change in trust with NPC
    - related_npcs: NPCs affected by fragments
    """
    npc_giver = str(glyph_row.get("NPC Giver", "")).strip()
    
    remnants_impact = {
        "npc_name": npc_giver,
        "trust_delta": 0.15,  # Base trust gain
        "related_npcs": []
    }
    
    # Fragment NPC relationships
    if df_fragments is not None and not df_fragments.empty:
        for _, fragment in df_fragments.iterrows():
            frag_npc = str(fragment.get("NPC_Name", "")).strip()
            if frag_npc and frag_npc != npc_giver:
                remnants_impact["related_npcs"].append(frag_npc)
    
    # Transcendence-specific: receivers instead of givers
    if "transcendence" in str(glyph_row.get("Category", "")).lower():
        remnants_impact["npc_name"] = str(glyph_row.get("NPC Receiver", "")).strip()
        remnants_impact["trust_delta"] = 0.2
    
    return remnants_impact


def compute_endgame_dependencies(glyph_row: Dict, df_transcendence: pd.DataFrame) -> Dict[str, Any]:
    """Compute endgame system impact.
    
    Returns:
    - contributes_to_fusion: List of fusion glyphs this is a prerequisite for
    - affects_saori_arc: Boolean if mentioned in Saori-related content
    - affects_velinor_arc: Boolean if mentioned in Velinor-related content
    - chamber_type: Type of chamber this unlocks
    """
    glyph_name = str(glyph_row.get("Glyph", "")).strip()
    storyline = str(glyph_row.get("Storyline", "")).lower()
    
    endgame_impact = {
        "contributes_to_fusion": [],
        "affects_saori_arc": False,
        "affects_velinor_arc": False,
        "chamber_type": None
    }
    
    # Check fusion prerequisites
    for _, fusion in df_transcendence.iterrows():
        fusion_storyline = str(fusion.get("Storyline", "")).lower()
        if glyph_name.lower() in fusion_storyline:
            endgame_impact["contributes_to_fusion"].append(fusion.get("Glyph", ""))
            
            # Determine chamber type
            location = str(fusion.get("Location", "")).lower()
            if "triglyph" in location:
                endgame_impact["chamber_type"] = "Triglyph Chamber"
            elif "octoglyph" in location:
                endgame_impact["chamber_type"] = "Octoglyph Chamber"
            elif "pentaglyph" in location:
                endgame_impact["chamber_type"] = "Pentaglyph Chamber"
            elif "hexaglyph" in location:
                endgame_impact["chamber_type"] = "Hexaglyph Chamber"
    
    # Check arc relevance
    if "saori" in storyline or "velinor" in storyline:
        if "saori" in storyline:
            endgame_impact["affects_saori_arc"] = True
        if "velinor" in storyline:
            endgame_impact["affects_velinor_arc"] = True
    
    return endgame_impact


def compute_emotional_alignment(glyph_row: Dict) -> Dict[str, float]:
    """Compute emotional alignment scores across Velinor's seven emotional categories.
    
    Returns a dict with scores for each emotional system.
    """
    category = str(glyph_row.get("Category", "")).strip().lower()
    theme = str(glyph_row.get("Theme", "")).strip().lower()
    
    alignment = {
        "collapse": 0.0,
        "ache": 0.0,
        "sovereignty": 0.0,
        "presence": 0.0,
        "trust": 0.0,
        "legacy": 0.0,
        "transcendence": 0.0
    }
    
    # Map category to alignment
    category_map = {
        "collapse": "collapse",
        "ache": "ache",
        "sovereignty": "sovereignty",
        "presence": "presence",
        "trust": "trust",
        "legacy": "legacy",
        "transcendence": "transcendence"
    }
    
    for key, cat in category_map.items():
        if cat in category:
            alignment[key] = 1.0
        elif cat in theme:
            alignment[key] = 0.7
    
    return alignment


def build_relationship_graph(
    df_core: pd.DataFrame,
    df_fragments: pd.DataFrame,
    df_transcendence: pd.DataFrame,
    df_cipher: pd.DataFrame
) -> nx.DiGraph:
    """Build a comprehensive relationship graph connecting all glyphs and related entities.
    
    Nodes:
    - Glyphs (core, fragments, fusion)
    - NPCs
    - Emotional categories
    - Biomes
    - Themes
    
    Edges represent relationships:
    - prerequisite (core → fusion)
    - emotional_alignment (glyph → category)
    - npc_relationship (glyph → npc)
    - biome_relationship (glyph → biome)
    - cipher_echo (glyph → cipher_seed)
    """
    G = nx.DiGraph()
    
    # Add core glyphs
    for _, row in df_core.iterrows():
        glyph_id = f"core:{row['Glyph']}"
        G.add_node(glyph_id, node_type="glyph", category="core", label=row['Glyph'])
        
        # NPC relationship
        npc = str(row.get("NPC Giver", "")).strip()
        if npc:
            npc_id = f"npc:{npc}"
            G.add_node(npc_id, node_type="npc", label=npc)
            G.add_edge(glyph_id, npc_id, relation="given_by")
        
        # Emotional category
        cat = str(row.get("Category", "")).strip()
        if cat:
            cat_id = f"category:{cat}"
            G.add_node(cat_id, node_type="category", label=cat)
            G.add_edge(glyph_id, cat_id, relation="category")
        
        # Biome (extract from location)
        location = str(row.get("Location", "")).strip().lower()
        for biome in ["desert", "mountain", "forest", "aquatic", "market", "village"]:
            if biome in location:
                biome_id = f"biome:{biome}"
                G.add_node(biome_id, node_type="biome", label=biome)
                G.add_edge(glyph_id, biome_id, relation="location")
                break
    
    # Add fusion glyphs and prerequisites
    for _, row in df_transcendence.iterrows():
        fusion_id = f"fusion:{row['Glyph']}"
        G.add_node(fusion_id, node_type="glyph", category="fusion", label=row['Glyph'])
        
        # NPC receiver
        npc = str(row.get("NPC Receiver", "")).strip()
        if npc:
            npc_id = f"npc:{npc}"
            G.add_node(npc_id, node_type="npc", label=npc)
            G.add_edge(fusion_id, npc_id, relation="received_by")
        
        # Category
        theme = str(row.get("Theme", "")).strip()
        if theme:
            theme_id = f"theme:{theme}"
            G.add_node(theme_id, node_type="theme", label=theme)
            G.add_edge(fusion_id, theme_id, relation="theme")
    
    # Add fragments
    for _, row in df_fragments.iterrows():
        frag_id = f"fragment:{row['Fragment_ID']}"
        G.add_node(frag_id, node_type="glyph", category="fragment", label=row['Fragment_ID'])
        
        # NPC
        npc = str(row.get("NPC_Name", "")).strip()
        if npc:
            npc_id = f"npc:{npc}"
            G.add_node(npc_id, node_type="npc", label=npc)
            G.add_edge(frag_id, npc_id, relation="given_by")
        
        # Biome
        biome = str(row.get("Biome", "")).strip().lower()
        if biome:
            biome_id = f"biome:{biome}"
            G.add_node(biome_id, node_type="biome", label=biome)
            G.add_edge(frag_id, biome_id, relation="location")
        
        # Emotional focus
        focus = str(row.get("Emotional_Focus", "")).strip()
        if focus:
            for emotion in focus.split("/"):
                emotion = emotion.strip().lower()
                emotion_id = f"emotion:{emotion}"
                G.add_node(emotion_id, node_type="emotion", label=emotion)
                G.add_edge(frag_id, emotion_id, relation="focus")
    
    # Add cipher seeds
    for _, row in df_cipher.iterrows():
        cipher_id = f"cipher:{row['first_view_display']}"
        G.add_node(cipher_id, node_type="cipher", label=row['first_view_display'][:20])
        
        # Category
        cat = str(row.get("category", "")).strip().lower()
        if cat:
            cat_id = f"category:{cat}"
            G.add_node(cat_id, node_type="category", label=cat)
            G.add_edge(cipher_id, cat_id, relation="category")
    
    return G


def get_graph_stats(G: nx.DiGraph) -> Dict[str, Any]:
    """Compute basic graph statistics."""
    return {
        "total_nodes": G.number_of_nodes(),
        "total_edges": G.number_of_edges(),
        "node_types": list(set(data.get("node_type") for _, data in G.nodes(data=True))),
        "density": nx.density(G),
        "avg_degree": sum(dict(G.degree()).values()) / G.number_of_nodes() if G.number_of_nodes() > 0 else 0
    }


def export_glyph_to_json(glyph_row: Dict, related: Dict) -> Dict[str, Any]:
    """Export a glyph with all related data to JSON format.
    
    Includes:
    - Core glyph fields
    - Related fragments
    - Related fusion glyphs
    - Related cipher seeds
    - Impact analysis (TONE, REMNANTS, endgame)
    """
    export = {
        "glyph": {
            "category": glyph_row.get("Category", ""),
            "name": glyph_row.get("Glyph", ""),
            "npc_giver": glyph_row.get("NPC Giver", ""),
            "location": glyph_row.get("Location", ""),
            "theme": glyph_row.get("Theme", ""),
            "storyline": glyph_row.get("Storyline", "")
        },
        "relationships": {
            "fragments": related.get("fragments", []).to_dict("records") if isinstance(related.get("fragments"), pd.DataFrame) else [],
            "fusion_glyphs": related.get("fusion", []).to_dict("records") if isinstance(related.get("fusion"), pd.DataFrame) else [],
            "cipher_seeds": related.get("cipher", []).to_dict("records") if isinstance(related.get("cipher"), pd.DataFrame) else []
        },
        "impact": {
            "tone": related.get("tone_impact", {}),
            "remnants": related.get("remnants_impact", {}),
            "endgame": related.get("endgame_impact", {}),
            "emotional_alignment": related.get("emotional_alignment", {})
        }
    }
    return export

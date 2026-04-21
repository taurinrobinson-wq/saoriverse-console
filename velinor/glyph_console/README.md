# Velinor Glyph Console

Comprehensive UI for exploring, analyzing, and managing Velinor's complete glyph system.

## Overview

The Glyph Console is a Streamlit-based web application that provides integrated access to four interconnected datasets:

1. **Core Glyphs** (Glyph_Organizer.csv) - Central dataset with ~70 core glyphs
2. **Fragments** (Glyph_Fragments.csv) - Companion fragments that enhance core glyphs
3. **Fusion Glyphs** (Glyph_Transcendence.csv) - Transcendence-tier glyphs created from combinations
4. **Cipher Seeds** (cipher_seeds.csv) - Encrypted wisdom and thematic echoes

## Features

### Central View (Glyph_Organizer)
- **Searchable Registry**: Find glyphs by name, NPC, theme, or category
- **Detailed View**: Full storyline, metadata, and relationships for each glyph
- **Related Content**: Automatically matched fragments, fusion prerequisites, and cipher resonances
- **Impact Analysis**: TONE stat changes, REMNANTS NPC effects, endgame system impacts
- **Emotional Alignment**: Visualization of glyph alignment with Velinor's seven emotional systems

### Fragment Explorer
- View all 36 fragments with their NPCs, biomes, and ability gains
- Filter by biome, NPC, or emotional focus
- Understand how fragments enhance and modify core glyphs

### Fusion Glyph Browser
- Explore 4 transcendence-tier fusion glyphs
- See prerequisites (core glyphs required to unlock each fusion)
- Understand boss mechanics and final choice consequences
- Track NPC receivers and chamber locations

### Cipher Seeds
- Browse all cipher seeds organized by domain and category
- View encrypted phrases and obfuscation patterns
- Understand thematic and emotional resonances

### Relationship Graph
- Network visualization of all glyphs, NPCs, biomes, and categories
- Filter by node type and connectivity
- Explore cross-dataset relationships visually

### Export System
- Export individual glyphs with full relationship data as JSON
- Export all glyphs as JSONL (JSON Lines format)
- Includes all impact analysis and relationship data in export

## Setup

### Prerequisites

```bash
python 3.9+
streamlit >= 1.28.0
pandas >= 1.5.0
networkx >= 3.0
plotly >= 5.0
```

### Installation

1. Install dependencies:

```bash
pip install streamlit pandas networkx plotly
```

2. Verify dataset files exist:

```
velinor/markdowngameinstructions/glyphs/
├── Glyph_Organizer.csv
├── Glyph_Fragments.csv
├── Glyph_Transcendence.csv
└── cipher_seeds.csv
```

### File Structure

```
velinor/glyph_console/
├── __init__.py          # Package initialization
├── app.py               # Main Streamlit application
├── utils.py             # Utility functions (matching, analysis, export)
└── README.md            # This file
```

## Running the Application

From the project root directory:

```bash
# Run the Glyph Console
streamlit run velinor/glyph_console/app.py

# Or with custom settings
streamlit run velinor/glyph_console/app.py --logger.level=debug
```

The app will open at `http://localhost:8501`

## Usage Guide

### Central View

1. **Filter glyphs** using the sidebar:
   - Select categories (Collapse, Ache, Sovereignty, etc.)
   - Select specific NPC givers
   - Search by name/theme

2. **Select a glyph** from the list to view:
   - Full metadata
   - Complete storyline
   - Related fragments (by NPC, biome, emotional focus)
   - Fusion glyphs this contributes to
   - Related cipher seeds
   - TONE impact (stat deltas)
   - REMNANTS impact (NPC relationships)
   - Endgame system impacts
   - Emotional alignment chart

### Fragments Tab

1. Filter fragments by:
   - Biome (Desert, Mountain, Forest, Aquatic, Market, Village)
   - NPC Name
   - Emotional focus keywords

2. Select a fragment to view details and storyline

### Fusion Glyphs Tab

1. Filter by theme (e.g., "coherence of Loss")
2. View each fusion glyph's:
   - Prerequisites (core glyphs required)
   - Location (chamber type and name)
   - NPC receiver
   - Full storyline and boss mechanic
   - Final choice consequences

### Cipher Seeds Tab

1. Filter by domain (Pre-Collapse, Post-Collapse, etc.)
2. Filter by category
3. View encrypted phrases and obfuscation patterns

### Relationship Graph

1. Adjust node type filters to focus on relevant entities
2. Use edge threshold to reduce clutter
3. Hover over nodes to see connections
4. Node size represents number of connections

### Export

1. Select a glyph to export
2. Review the export preview (JSON format)
3. Download as individual JSON file or all glyphs as JSONL

## Data Schema

### Core Glyph Export

```json
{
  "glyph": {
    "category": "Sovereignty",
    "name": "Glyph of Iron Boundary",
    "npc_giver": "Captain Veynar",
    "location": "Trial grounds",
    "theme": "Boundaries, choice, clarity",
    "storyline": "..."
  },
  "relationships": {
    "fragments": [...],
    "fusion_glyphs": [...],
    "cipher_seeds": [...]
  },
  "impact": {
    "tone": {
      "courage": 0.15,
      "wisdom": 0.1,
      "empathy": 0.0,
      "resolve": 0.1
    },
    "remnants": {
      "npc_name": "Captain Veynar",
      "trust_delta": 0.15,
      "related_npcs": [...]
    },
    "endgame": {
      "contributes_to_fusion": [...],
      "affects_saori_arc": false,
      "affects_velinor_arc": true,
      "chamber_type": null
    },
    "emotional_alignment": {
      "collapse": 0.0,
      "ache": 0.0,
      "sovereignty": 1.0,
      "presence": 0.0,
      "trust": 0.0,
      "legacy": 0.0,
      "transcendence": 0.0
    }
  }
}
```

## Utility Functions

### `match_fragments_to_glyph(glyph_row, df_fragments)`
Find fragments related to a glyph by NPC, biome, or emotional focus.

### `match_fusion_to_glyph(glyph_row, df_transcendence)`
Find fusion glyphs that list this glyph as a prerequisite.

### `match_cipher_to_glyph(glyph_row, df_cipher)`
Find cipher seeds related by theme or emotional category.

### `compute_tone_impact(glyph_row, df_fragments)`
Calculate TONE stat changes from glyph category and fragments.

### `compute_remnants_impact(glyph_row, df_fragments)`
Calculate NPC trust effects and related NPC relationships.

### `compute_endgame_dependencies(glyph_row, df_transcendence)`
Determine fusion contributions and story arc impacts.

### `compute_emotional_alignment(glyph_row)`
Score glyph alignment across Velinor's seven emotional systems.

### `build_relationship_graph(df_core, df_fragments, df_transcendence, df_cipher)`
Create networkx graph of all entities and relationships.

### `export_glyph_to_json(glyph_row, related)`
Export glyph with all relationships and impact data.

## Performance Notes

- **Initial load**: ~2-3 seconds (caches datasets)
- **Graph building**: ~5-10 seconds for full graph
- **Filtering**: Instant (dataframe operations)
- **Export**: Instant (all data pre-computed)

## Troubleshooting

### "Could not load datasets" error
- Check file paths in `velinor/markdowngameinstructions/glyphs/`
- Verify all CSV files are present
- Check file permissions

### Graph visualization is slow
- Reduce number of node types in graph filter
- Increase edge threshold to remove low-connection nodes
- Use smaller dataset subset

### Export JSON is incomplete
- Verify all related glyphs/fragments/fusion glyphs exist
- Check for missing columns in CSV files
- Review browser console for errors

## Development

### Adding New Datasets

To integrate additional glyph-related data:

1. Add CSV file to `velinor/markdowngameinstructions/glyphs/`
2. Create load function in `app.py`
3. Add matching function in `utils.py`
4. Create new tab in app.py for the dataset

### Extending Utilities

To add new analysis functions:

1. Add function to `utils.py`
2. Document parameters and return type
3. Call from appropriate view in `app.py`
4. Include in export schema

## Architecture

```
┌─────────────────────────────────────────────┐
│       Velinor Glyph Console App (UI)        │
│  ┌──────────────────────────────────────┐   │
│  │    Central View (Core Glyphs)        │   │
│  ├──────────────────────────────────────┤   │
│  │  - Registry & Search                 │   │
│  │  - Glyph Details & Storyline         │   │
│  │  - Relationships (Fragments, etc)    │   │
│  │  - Impact Analysis                   │   │
│  │  - Emotional Alignment Chart         │   │
│  └──────────────────────────────────────┘   │
│  ┌──────────────────────────────────────┐   │
│  │    Supplementary Tabs                │   │
│  ├──────────────────────────────────────┤   │
│  │  - Fragments Explorer                │   │
│  │  - Fusion Glyphs Browser             │   │
│  │  - Cipher Seeds View                 │   │
│  │  - Relationship Graph                │   │
│  │  - Export System                     │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
         │                    │
         ▼                    ▼
   ┌──────────────┐  ┌──────────────┐
   │  utils.py    │  │  Dataset CSVs │
   ├──────────────┤  ├──────────────┤
   │ - Matching   │  │ - Glyph_Org  │
   │ - Analysis   │  │ - Fragments  │
   │ - Graphs     │  │ - Transcend  │
   │ - Export     │  │ - Cipher     │
   └──────────────┘  └──────────────┘
```

## License

Part of the Saoriverse console project.

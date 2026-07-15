"""
Generate Fast-Travel Data from Overworld Map
Creates JSON configuration for fast-travel UI system in Velinor

This generates:
- Region definitions with travel points
- UI positioning data
- Travel time/distance between regions
"""

import json
import os
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Region:
    """Define a region with its properties."""
    id: str
    name: str
    description: str
    map_x: int
    map_y: int
    climate: str  # temperature/mood
    culture: str  # cultural descriptor
    primary_npc: str  # Main NPC in region
    discovered: bool = False
    accessible: bool = True

# Define all regions in the Velhara overworld
REGIONS = [
    Region(
        id="archive_district",
        name="Archive District",
        description="Ruins of past Velhara - towering structures crumble with age",
        map_x=1100, map_y=180,
        climate="Dry, dusty winds sweep through broken architecture",
        culture="Knowledge keepers preserving fragments of the old world",
        primary_npc="Archivist Malrik"
    ),
    Region(
        id="shrine_ridge",
        name="Shrine Ridge",
        description="Ancient temples cling to northern cliffs - sacred and haunted",
        map_x=550, map_y=120,
        climate="Cool, thin air - whispers carry far",
        culture="Spiritual seekers and memory guardians",
        primary_npc="High Seer Elenya"
    ),
    Region(
        id="market_basin",
        name="Market Basin",
        description="The living heart of Velhara - bustling with survivors and traders",
        map_x=480, map_y=380,
        climate="Variable, sheltered by surrounding structures",
        culture="Pragmatic merchants and organized community",
        primary_npc="Ravi & Nima"
    ),
    Region(
        id="desert_expanse",
        name="Desert & Mountain Expanse",
        description="Vast emptiness where the player begins - sandy dunes meet rocky peaks",
        map_x=280, map_y=380,
        climate="Scorching heat by day, frigid nights",
        culture="Nomadic scavengers and solitary travelers",
        primary_npc="Saori"
    ),
    Region(
        id="harbor_lowlands",
        name="Harbor Air Lowlands",
        description="Flooded coastal areas with makeshift watercraft",
        map_x=1050, map_y=500,
        climate="Humid, salt-laden breezes - oppressive heat",
        culture="Fishers and maritime traders",
        primary_npc="Captain Dalen"
    ),
    Region(
        id="swamp_lowlands",
        name="Swamid Swamps & Lowlands",
        description="Wetlands thick with vegetation and strange sounds",
        map_x=650, map_y=600,
        climate="Damp, murky - mist clings to everything",
        culture="Herbalists and hidden communities",
        primary_npc="Keeper"
    ),
    Region(
        id="buried_archives",
        name="Buried Tomb Archives",
        description="Underground chambers holding secrets of the before-time",
        map_x=200, map_y=550,
        climate="Cool, stable - untouched by surface weather",
        culture="Archaeologists and tomb keepers",
        primary_npc="Tovren"
    ),
    Region(
        id="concourse_ruins",
        name="Concourse Ruins",
        description="Central hub where multiple paths converge",
        map_x=950, map_y=320,
        climate="Variable with wind patterns from multiple directions",
        culture="Crossroads merchants and opportunity seekers",
        primary_npc="Kaelen"
    ),
]

# Define travel routes and times
TRAVEL_ROUTES = [
    {"from": "desert_expanse", "to": "market_basin", "time_minutes": 15, "distance": "Medium"},
    {"from": "market_basin", "to": "archive_district", "time_minutes": 20, "distance": "Far"},
    {"from": "market_basin", "to": "shrine_ridge", "time_minutes": 18, "distance": "Far"},
    {"from": "market_basin", "to": "swamp_lowlands", "time_minutes": 22, "distance": "Very Far"},
    {"from": "market_basin", "to": "harbor_lowlands", "time_minutes": 25, "distance": "Very Far"},
    {"from": "market_basin", "to": "buried_archives", "time_minutes": 20, "distance": "Far"},
    {"from": "concourse_ruins", "to": "archive_district", "time_minutes": 8, "distance": "Close"},
    {"from": "concourse_ruins", "to": "market_basin", "time_minutes": 10, "distance": "Close"},
    {"from": "desert_expanse", "to": "buried_archives", "time_minutes": 12, "distance": "Medium"},
]

def generate_fast_travel_config() -> Dict:
    """Generate complete fast-travel configuration."""
    
    config = {
        "version": "1.0",
        "system": "VelharaFastTravel",
        "map_dimensions": {"width": 4320, "height": 4320},
        "regions": [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "map_position": {"x": r.map_x, "y": r.map_y},
                "atmosphere": {
                    "climate": r.climate,
                    "culture": r.culture,
                },
                "npc": r.primary_npc,
                "discovered": r.discovered,
                "accessible": r.accessible,
                "ui_data": {
                    "label_offset_x": 0,
                    "label_offset_y": -40,
                    "hover_radius": 50,
                    "icon_size": 32,
                }
            }
            for r in REGIONS
        ],
        "travel_system": {
            "enabled": True,
            "routes": TRAVEL_ROUTES,
            "cost_type": "time",
            "fast_travel_unlock": "After discovering first glyph",
        }
    }
    
    return config

def generate_ui_prefab_data() -> Dict:
    """Generate Unity UI prefab data for the map display."""
    
    ui_data = {
        "prefab_name": "OverworldMapUI",
        "canvas_settings": {
            "render_mode": "ScreenSpaceOverlay",
            "scale_mode": "ScaleWithScreenSize",
        },
        "map_container": {
            "image_source": "OverworldMap_Labeled.png",
            "aspect_ratio": "1:1",
            "size": "800x800",
        },
        "region_buttons": [
            {
                "region_id": r.id,
                "button_name": f"Btn_{r.id}",
                "position": {"x": r.map_x / 5.4, "y": r.map_y / 5.4},  # Scale to UI size
                "size": {"width": 60, "height": 60},
                "interaction": {
                    "on_hover": f"ShowRegionInfo_{r.id}",
                    "on_click": f"FastTravelTo_{r.id}",
                },
                "state_colors": {
                    "normal": "#8B7355",
                    "hover": "#D4A574",
                    "disabled": "#5A4A3A",
                    "discovered": "#FFD700",
                }
            }
            for r in REGIONS
        ],
        "info_panel": {
            "display_mode": "OnHover",
            "fade_duration": 0.3,
            "content_fields": [
                "region_name",
                "description",
                "climate",
                "culture",
                "primary_npc",
            ]
        },
        "fast_travel_panel": {
            "display_mode": "OnClick",
            "confirm_button": True,
            "travel_time_display": True,
        }
    }
    
    return ui_data

def save_configs(output_dir: str):
    """Save all generated configurations to JSON files."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save fast-travel config
    fast_travel_path = os.path.join(output_dir, "fast_travel_config.json")
    with open(fast_travel_path, 'w') as f:
        json.dump(generate_fast_travel_config(), f, indent=2)
    print(f"✓ Fast-travel config: {fast_travel_path}")
    
    # Save UI prefab data
    ui_path = os.path.join(output_dir, "overworld_map_ui_prefab.json")
    with open(ui_path, 'w') as f:
        json.dump(generate_ui_prefab_data(), f, indent=2)
    print(f"✓ UI prefab data: {ui_path}")

if __name__ == "__main__":
    output_dir = os.path.join(
        os.path.dirname(__file__),
        "Assets", "Resources", "Config"
    )
    
    try:
        save_configs(output_dir)
        print("\n✓ Fast-travel configuration complete!")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

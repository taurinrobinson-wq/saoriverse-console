"""
Asset Configuration for Velinor Game
=====================================

Maps story passage references to asset files (backgrounds, NPCs).
"""

# Background image mapping
BACKGROUNDS = {
    # Market District
    'market_ruins': 'city_market',
    'market_district': 'city_market',
    
    # Monuments and outdoor areas
    'monuments': 'city_mountains',
    'outdoor': 'city_mountains',
    'mountains': 'city_mountains',
    
    # Archive and buildings
    'archive_ruins': 'forest_city',
    'archive': 'forest_city',
    'city': 'forest_city',
    
    # Underground
    'underground_ruins': 'swamp',
    'underground': 'swamp',
    'sewers': 'swamp',
    'tunnel': 'swamp',
    
    # Bridge
    'bridge_ravine': 'pass',
    'bridge': 'pass',
    'pass': 'pass',
    'ravine': 'pass',
    
    # Forest areas
    'keeper_sanctuary': 'forest',
    'forest': 'forest',
    'forest_clearing': 'forest',
    'woods': 'forest',
    
    # Desert areas
    'desert': 'desert',
    'dunes': 'desert',
    'sand': 'desert',
    'desert_light': 'desert',
    
    # Lake areas
    'lake': 'lake',
    'water': 'lake',
    'echoing_lake': 'lake',
    
    # Swamp areas
    'swamp': 'swamp',
    'wetland': 'swamp',
    'soft_remembrance': 'swamp',
}

# NPC character mapping
NPC_CHARACTERS = {
    'Keeper': 'velinor_eyesclosed',
    'Saori': 'saori',
    'Sanor': 'sanor',
    'Irodora': 'irodora',
    'Tala': 'tala',
    'Safi': 'safi_and_rumi',
    'Rumi': 'safi_and_rumi',
    'Safi and Rumi': 'safi_and_rumi',
    'Velinor': 'velinor_eyesopen',
}

# Title/UI images
UI_IMAGES = {
    'title': 'velinor_title_transparent',
    'logo': 'velinor_title_transparent',
}


def get_background(passage_name: str) -> str:
    """Get background image filename for a passage."""
    return BACKGROUNDS.get(passage_name.lower(), 'city_market')


def get_npc_image(npc_name: str) -> str:
    """Get NPC character image filename."""
    return NPC_CHARACTERS.get(npc_name, npc_name.lower())


def get_ui_image(image_type: str) -> str:
    """Get UI image filename."""
    return UI_IMAGES.get(image_type.lower(), 'velinor_title_transparent')

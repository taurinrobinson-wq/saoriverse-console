"""
Simple mapping from Twine passage names to frontend scene ids.

This allows the backend to return a `scene_id` alongside the Twine-rendered
state so the frontend can choose either the Twine passage UI or the local
scene graph in `velinor-web/src/data/scenes.json`.
"""

SCENE_MAP = {
    # Market / opening
    "market_entry": "velhara_market",
    "ravi_nima_greet": "velhara_market",
    "ravi_nima_observe": "underpass_scene",
    "ravi_nima_callout": "collapse_scene",
    "market_exploration": "velhara_market",

    # Keeper / monuments
    "keeper_dialogue_1": "velhara_market",
    "keeper_guide": "velhara_market",

    # Exploration anchors (best-effort mappings)
    "archive_entrance": "collapse_scene",
    "underground_entrance": "underpass_scene",
    "bridge_crossing": "collapse_scene",

    # Glyph chamber / endings
    "glyph_chamber": "glyph_chamber",
    "ending_fragment": "ending_fragment"
}

def get_scene_id(twine_passage_name: str):
    return SCENE_MAP.get(twine_passage_name)

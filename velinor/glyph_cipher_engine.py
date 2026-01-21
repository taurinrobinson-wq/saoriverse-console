"""
Velinor: Glyph Cipher Integration

This module integrates the cipher system directly with the glyph system.

When a player speaks to an NPC and their emotional state aligns with
a glyph's requirements, they unlock a cipher seed that reveals the 
glyph's emotional truth.

The cipher becomes the mechanical manifestation of emotional gating.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

from velinor.velinor_api import load_seeds, query_gate


@dataclass
class GlyphSeed:
    """A cipher seed that represents one glyph's emotional truth."""
    id: str
    glyph_name: str
    npc: str
    category: str  # Collapse, Sovereignty, Ache, Presence, Joy, Trust, Legacy
    layer_0: str  # Poetic fragment (always accessible)
    layer_1: str  # NPC fragment (always accessible)
    layer_2: str  # Plaintext truth (emotionally gated)
    required_gates: List[str]
    location: str


class GlyphCipherEngine:
    """Manages cipher seeds tied to glyph manifestations."""
    
    def __init__(self):
        """Initialize with seeds from cipher_seeds.json."""
        self.seeds: Dict[str, Dict] = load_seeds()
        
    def get_glyph_by_id(self, seed_id: str) -> Optional[GlyphSeed]:
        """Get a glyph seed by ID."""
        if seed_id not in self.seeds:
            return None
        
        data = self.seeds[seed_id]
        return GlyphSeed(
            id=data["id"],
            glyph_name=data["glyph_name"],
            npc=data["npc"],
            category=data["category"],
            layer_0=data["fragments"]["layer_0"],
            layer_1=data["fragments"]["layer_1"],
            layer_2=data["fragments"]["layer_2"],
            required_gates=data["required_gates"],
            location=data["location"],
        )
    
    def get_glyphs_by_npc(self, npc_name: str) -> List[GlyphSeed]:
        """Get all glyphs a specific NPC gives."""
        glyphs = []
        for seed_data in self.seeds.values():
            if seed_data["npc"].lower() == npc_name.lower():
                glyph = self.get_glyph_by_id(seed_data["id"])
                if glyph:
                    glyphs.append(glyph)
        return glyphs
    
    def get_glyphs_by_category(self, category: str) -> List[GlyphSeed]:
        """Get all glyphs in a category (e.g., Collapse, Trust)."""
        glyphs = []
        for seed_data in self.seeds.values():
            if seed_data["category"].lower() == category.lower():
                glyph = self.get_glyph_by_id(seed_data["id"])
                if glyph:
                    glyphs.append(glyph)
        return glyphs
    
    def unlock_glyph(self, seed_id: str, player_message: str) -> Dict:
        """
        Attempt to unlock a glyph cipher.
        
        Returns the appropriate layer based on player's emotional alignment.
        """
        response = query_gate(seed_id, player_message)
        glyph = self.get_glyph_by_id(seed_id)
        
        if not glyph:
            return {"status": "error", "message": "Glyph not found"}
        
        # Determine which layer to show
        layer = response.get("layer", 0)
        allowed = response.get("allowed", False)
        
        if layer == 0:
            text = glyph.layer_0
            access = "fragment"
        elif layer == 1:
            text = glyph.layer_1
            access = "fragment"
        else:  # layer 2
            if allowed:
                text = glyph.layer_2
                access = "plaintext"
            else:
                text = glyph.layer_1  # Show fragment if not aligned
                access = "locked"
        
        return {
            "status": "ok",
            "glyph_id": seed_id,
            "glyph_name": glyph.glyph_name,
            "npc": glyph.npc,
            "category": glyph.category,
            "access": access,  # "fragment" or "plaintext" or "locked"
            "text": text,
            "required_gates": glyph.required_gates,
            "location": glyph.location,
        }


# Global engine instance
_engine: Optional[GlyphCipherEngine] = None


def get_engine() -> GlyphCipherEngine:
    """Get or create the global glyph cipher engine."""
    global _engine
    if _engine is None:
        _engine = GlyphCipherEngine()
    return _engine

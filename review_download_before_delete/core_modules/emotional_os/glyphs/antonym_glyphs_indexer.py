#!/usr/bin/env python3
"""
Antonym Glyphs Indexed Lookup System

Creates a searchable index of all antonym glyphs mapped by voltage pair,
base emotion, and other attributes for fast lookup during glyph selection.

This enables:
1. Quick lookup of emotional opposites by primary glyph voltage pair
2. Search by emotion name, pairing, or description
3. Context-aware antonym suggestions in the UI
4. Export for UI integration
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


class AntonymGlyphIndexer:
    """Creates and manages indexed lookup of antonym glyphs."""
    
    def __init__(
        self,
        antonym_source: str = "antonym_glyphs.txt",
        glyph_lexicon: str = "emotional_os/glyphs/glyph_lexicon_rows.json"
    ):
        """Initialize the indexer.
        
        Args:
            antonym_source: Path to antonym_glyphs.txt
            glyph_lexicon: Path to primary glyph lexicon JSON
        """
        self.antonym_source = Path(antonym_source)
        self.glyph_lexicon = Path(glyph_lexicon)
        
        # Index structures
        self.antonyms: List[Dict] = []
        self.by_base_emotion: Dict[str, Dict] = {}  # base_emotion -> antonym
        self.by_pairing: Dict[str, Dict] = {}  # voltage_pair -> antonym
        self.by_name: Dict[str, Dict] = {}  # name -> antonym
        self.primary_glyphs: Dict[str, Dict] = {}  # voltage_pair -> primary glyph
        
        # Semantic mappings for discovering opposites
        self.emotional_opposites = {
            # Joy opposites
            "joy": ["grief", "sorrow", "despair", "misery"],
            "happiness": ["sadness", "sorrow", "melancholy"],
            "delight": ["displeasure", "disgust", "aversion"],
            "pleasure": ["pain", "suffering", "discomfort"],
            "comfort": ["discomfort", "unease", "distress"],
            "relief": ["tension", "burden", "pressure"],
            "peace": ["turmoil", "conflict", "strife"],
            "contentment": ["discontent", "dissatisfaction"],
            "fulfillment": ["emptiness", "lack", "deprivation"],
            "satisfaction": ["dissatisfaction", "frustration"],
            "celebration": ["mourning", "lamentation"],
            
            # Sorrow opposites
            "grief": ["joy", "celebration", "rejoicing", "happiness"],
            "sorrow": ["happiness", "joy", "cheer"],
            "sadness": ["happiness", "cheerfulness", "joy"],
            "despair": ["hope", "fulfillment", "joy"],
            "misery": ["comfort", "fulfillment", "bliss"],
            
            # Calm opposites
            "stillness": ["chaos", "turbulence", "agitation"],
            "quiet": ["noise", "chaos", "turmoil"],
            "calm": ["agitation", "disturbance", "turmoil"],
            "peace": ["conflict", "turmoil", "discord"],
            
            # Fear opposites
            "fear": ["courage", "bravery", "confidence"],
            "anxiety": ["peace", "calm", "serenity"],
            "dread": ["anticipation", "hope", "eagerness"],
            "terror": ["safety", "security", "peace"],
            
            # Love opposites
            "love": ["hate", "indifference", "coldness"],
            "affection": ["coldness", "indifference", "detachment"],
            "belonging": ["isolation", "alienation", "rejection"],
            "connection": ["disconnection", "isolation"],
            
            # Strength opposites
            "strength": ["weakness", "fragility", "vulnerability"],
            "power": ["powerlessness", "helplessness"],
            "confidence": ["doubt", "uncertainty", "insecurity"],
            "courage": ["fear", "cowardice", "timidity"],
            
            # Clarity opposites
            "clarity": ["confusion", "obscurity", "uncertainty"],
            "understanding": ["confusion", "bewilderment"],
            "insight": ["blindness", "ignorance", "confusion"],
            "wisdom": ["foolishness", "ignorance", "stupidity"],
            
            # Openness opposites
            "openness": ["closure", "reservation", "guardedness"],
            "receptivity": ["resistance", "closure"],
            "trust": ["distrust", "suspicion", "doubt"],
            "vulnerability": ["protection", "guardedness"],
            
            # Authenticity opposites
            "authenticity": ["falseness", "pretense", "inauthenticity"],
            "truth": ["falsehood", "deception", "illusion"],
            "sincerity": ["insincerity", "pretense", "dishonesty"],
            
            # Connection opposites
            "intimacy": ["distance", "coldness", "alienation"],
            "presence": ["absence", "distraction"],
            "attunement": ["discord", "misalignment"],
        }
    
    def load_antonyms(self) -> bool:
        """Load antonym glyphs from source file.
        
        Returns:
            bool: True if loaded successfully
        """
        try:
            if not self.antonym_source.exists():
                print(f"✗ Antonym glyphs file not found: {self.antonym_source}")
                return False
            
            with open(self.antonym_source, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract JSON array
            json_start = content.find('[')
            if json_start == -1:
                print("✗ Invalid antonym glyphs file format")
                return False
            
            data = json.loads(content[json_start:])
            
            self.antonyms = []
            for item in data:
                if isinstance(item, dict):
                    self.antonyms.append(item)
                    
                    # Index by base emotion
                    base_emotion = item.get("Base Emotion", "")
                    if base_emotion:
                        self.by_base_emotion[base_emotion.lower()] = item
                    
                    # Index by pairing
                    pairing = item.get("Pairing", "")
                    if pairing:
                        self.by_pairing[pairing] = item
                    
                    # Index by name
                    name = item.get("Name", "")
                    if name:
                        self.by_name[name.lower()] = item
            
            print(f"✓ Loaded {len(self.antonyms)} antonym glyphs")
            return True
            
        except Exception as e:
            print(f"✗ Error loading antonym glyphs: {e}")
            return False
    
    def load_primary_glyphs(self) -> bool:
        """Load primary glyphs for comparison.
        
        Returns:
            bool: True if loaded successfully
        """
        try:
            if not self.glyph_lexicon.exists():
                print(f"✗ Glyph lexicon not found: {self.glyph_lexicon}")
                return False
            
            with open(self.glyph_lexicon, 'r', encoding='utf-8') as f:
                glyphs = json.load(f)
            
            for glyph in glyphs:
                if isinstance(glyph, dict):
                    voltage_pair = glyph.get("voltage_pair", "")
                    if voltage_pair:
                        self.primary_glyphs[voltage_pair] = glyph
            
            print(f"✓ Loaded {len(self.primary_glyphs)} primary glyphs")
            return True
            
        except Exception as e:
            print(f"✗ Error loading primary glyphs: {e}")
            return False
    
    def build_indexes(self) -> Dict:
        """Build comprehensive lookup indexes.
        
        Returns:
            dict: Index statistics
        """
        indexes = {
            "total_antonyms": len(self.antonyms),
            "indexed_by_emotion": len(self.by_base_emotion),
            "indexed_by_pairing": len(self.by_pairing),
            "indexed_by_name": len(self.by_name),
            "primary_glyphs": len(self.primary_glyphs),
        }
        
        print(f"\n✓ Built indexes:")
        print(f"  - {indexes['indexed_by_emotion']} by base emotion")
        print(f"  - {indexes['indexed_by_pairing']} by voltage pairing")
        print(f"  - {indexes['indexed_by_name']} by glyph name")
        
        return indexes
    
    def find_antonym_by_voltage_pair(self, voltage_pair: str) -> Optional[Dict]:
        """Find antonym by voltage pair.
        
        Args:
            voltage_pair: Voltage pair like "γ × γ"
            
        Returns:
            dict: Antonym glyph if found
        """
        return self.by_pairing.get(voltage_pair)
    
    def find_antonym_by_emotion(self, emotion: str) -> Optional[Dict]:
        """Find antonym by base emotion name.
        
        Args:
            emotion: Emotion name
            
        Returns:
            dict: Antonym glyph if found
        """
        return self.by_base_emotion.get(emotion.lower())
    
    def search_antonyms(self, query: str) -> List[Dict]:
        """Search antonym glyphs by any text field.
        
        Args:
            query: Search string
            
        Returns:
            List of matching antonyms
        """
        query_lower = query.lower()
        results = []
        
        for antonym in self.antonyms:
            base_emotion = antonym.get("Base Emotion", "").lower()
            name = antonym.get("Name", "").lower()
            description = antonym.get("Description", "").lower()
            pairing = antonym.get("Pairing", "")
            
            if (query_lower in base_emotion or
                query_lower in name or
                query_lower in description or
                query_lower in pairing):
                results.append(antonym)
        
        return results
    
    def get_opposite_pair(self, primary_voltage_pair: str) -> Optional[Dict]:
        """Get the opposite pair for a primary glyph by voltage pair.
        
        Args:
            primary_voltage_pair: Voltage pair of primary glyph
            
        Returns:
            dict: Antonym glyph if emotional opposite exists
        """
        primary_glyph = self.primary_glyphs.get(primary_voltage_pair)
        if not primary_glyph:
            return None
        
        # Get primary glyph name
        primary_name = primary_glyph.get("glyph_name", "").lower()
        
        # Check each antonym for emotional opposite
        for antonym in self.antonyms:
            base_emotion = antonym.get("Base Emotion", "").lower()
            
            # Check if this base emotion is an opposite of the primary
            for emotion, opposites in self.emotional_opposites.items():
                if emotion.lower() == base_emotion:
                    # Found a potential opposite
                    # Match against primary glyph name
                    if any(opp.lower() in primary_name for opp in opposites):
                        return antonym
        
        return None
    
    def suggest_antonyms_for_glyph(self, primary_voltage_pair: str, limit: int = 5) -> List[Dict]:
        """Suggest antonym glyphs for a primary glyph.
        
        Args:
            primary_voltage_pair: Voltage pair of primary glyph
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested antonym glyphs
        """
        primary_glyph = self.primary_glyphs.get(primary_voltage_pair)
        if not primary_glyph:
            return []
        
        primary_name = primary_glyph.get("glyph_name", "")
        primary_desc = primary_glyph.get("description", "").lower()
        
        suggestions = []
        
        # Strategy 1: Look for emotional opposites in the description
        for antonym in self.antonyms:
            base_emotion = antonym.get("Base Emotion", "").lower()
            
            # Check if any opposite keywords appear in descriptions
            for emotion, opposites in self.emotional_opposites.items():
                if emotion.lower() in primary_desc:
                    if base_emotion in opposites:
                        suggestions.append(antonym)
                        break
        
        # Strategy 2: If no suggestions yet, return first N antonyms
        if not suggestions:
            suggestions = self.antonyms[:limit]
        
        return suggestions[:limit]
    
    def export_indexes(self, output_path: str = "antonym_glyphs_indexed.json") -> bool:
        """Export all indexes to JSON for system integration.
        
        Args:
            output_path: Output file path
            
        Returns:
            bool: True if export successful
        """
        try:
            export_data = {
                "metadata": {
                    "total_antonym_glyphs": len(self.antonyms),
                    "total_primary_glyphs": len(self.primary_glyphs),
                    "description": "Indexed antonym glyphs for fast lookup"
                },
                "antonym_glyphs": self.antonyms,
                "indexes": {
                    "by_base_emotion": self.by_base_emotion,
                    "by_pairing": self.by_pairing,
                    "by_name": self.by_name,
                }
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Exported indexed antonym glyphs to {output_path}")
            return True
            
        except Exception as e:
            print(f"✗ Error exporting indexes: {e}")
            return False
    
    def print_summary(self):
        """Print a summary of the indexed antonym glyphs."""
        print("\n" + "=" * 80)
        print("ANTONYM GLYPHS INDEXED LOOKUP - SUMMARY")
        print("=" * 80)
        print(f"✓ Total antonym glyphs: {len(self.antonyms)}")
        print(f"✓ Indexed by base emotion: {len(self.by_base_emotion)}")
        print(f"✓ Indexed by voltage pairing: {len(self.by_pairing)}")
        print(f"✓ Indexed by glyph name: {len(self.by_name)}")
        print(f"✓ Primary glyphs available: {len(self.primary_glyphs)}")
        
        print("\n" + "─" * 80)
        print("SAMPLE INDEXED ANTONYMS (first 5 by emotion)")
        print("─" * 80)
        
        for i, (emotion, antonym) in enumerate(list(self.by_base_emotion.items())[:5], 1):
            print(f"\n{i}. {emotion.upper()}")
            print(f"   Pairing: {antonym.get('Pairing')}")
            print(f"   Name: {antonym.get('Name')}")
            print(f"   Description: {antonym.get('Description')[:70]}...")
        
        print("\n" + "=" * 80)


def main():
    """Test the indexer."""
    indexer = AntonymGlyphIndexer()
    
    if not indexer.load_antonyms():
        print("✗ Failed to load antonym glyphs")
        return
    
    if not indexer.load_primary_glyphs():
        print("✗ Failed to load primary glyphs")
        return
    
    indexer.build_indexes()
    indexer.print_summary()
    
    # Test searches
    print("\n" + "─" * 80)
    print("SEARCH TESTS")
    print("─" * 80)
    
    test_searches = ["comfort", "joy", "grief", "peace"]
    for query in test_searches:
        results = indexer.search_antonyms(query)
        print(f"\n🔍 Search for '{query}': {len(results)} result(s)")
        if results:
            for r in results[:2]:
                print(f"   - {r.get('Base Emotion')}: {r.get('Name')}")
    
    # Export indexes
    print("\n" + "─" * 80)
    if indexer.export_indexes():
        print("✓ Successfully exported indexed antonym glyphs")
    
    print("\n✓ Indexing complete!")


if __name__ == "__main__":
    main()

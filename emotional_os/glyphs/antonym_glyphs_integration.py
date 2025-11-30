#!/usr/bin/env python3
"""
Antonym Glyphs Integration System

Integrates the 90+ emotional antonym glyph pairings into the main glyph system.
Provides functionality to:
- Load antonym glyphs from source file
- Map to existing primary glyphs
- Generate complementary glyph recommendations
- Show emotional opposites during glyph selection

Architecture:
1. Load antonym glyphs from antonym_glyphs.txt
2. Map base emotions to primary glyphs by voltage pair
3. Provide lookup functions for antonym discovery
4. Integrate into glyph selection and recommendation logic
"""

import json
import logging
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class AntonymGlyph:
    """A glyph representing the emotional opposite of a primary glyph."""

    base_emotion: str
    pairing: str  # e.g., "ζ × α"
    name: str
    description: str
    opposite_emotions: List[str] = None  # Emotions this opposes
    activation_signals: List[str] = None
    gate: str = None

    def __post_init__(self):
        if self.opposite_emotions is None:
            self.opposite_emotions = []
        if self.activation_signals is None:
            self.activation_signals = []


class AntonymGlyphsIntegration:
    """Manages loading and integration of antonym glyphs."""

    def __init__(
        self,
        antonym_source: str = "antonym_glyphs.txt",
        glyph_db: str = "emotional_os/glyphs/glyphs.db",
        glyph_lexicon: str = "emotional_os/glyphs/glyph_lexicon_rows.json",
    ):
        """Initialize antonym glyphs integration.

        Args:
            antonym_source: Path to antonym_glyphs.txt
            glyph_db: Path to SQLite glyph database
            glyph_lexicon: Path to glyph lexicon JSON
        """
        self.antonym_source = Path(antonym_source)
        self.glyph_db = Path(glyph_db)
        self.glyph_lexicon = Path(glyph_lexicon)

        self.antonym_glyphs: List[AntonymGlyph] = []
        self.primary_glyphs: Dict[str, Dict] = {}
        self.antonym_map: Dict[str, str] = {}  # Maps primary glyph to antonym base emotion
        self.loaded = False

    def load_antonym_glyphs(self) -> bool:
        """Load antonym glyphs from source file.

        Returns:
            bool: True if loaded successfully
        """
        try:
            if not self.antonym_source.exists():
                logger.error(f"Antonym glyphs file not found: {self.antonym_source}")
                return False

            with open(self.antonym_source, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse JSON array from file
            # The file contains JSON array after initial "[" character
            json_start = content.find("[")
            if json_start == -1:
                logger.error("Invalid antonym glyphs file format")
                return False

            data = json.loads(content[json_start:])

            self.antonym_glyphs = []
            for item in data:
                if isinstance(item, dict):
                    antonym = AntonymGlyph(
                        base_emotion=item.get("Base Emotion", ""),
                        pairing=item.get("Pairing", ""),
                        name=item.get("Name", ""),
                        description=item.get("Description", ""),
                        opposite_emotions=item.get("Opposite Emotions", []),
                        activation_signals=item.get("Activation Signals", []),
                        gate=item.get("Gate", None),
                    )
                    self.antonym_glyphs.append(antonym)

            logger.info(f"✓ Loaded {len(self.antonym_glyphs)} antonym glyphs")
            return True

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing antonym glyphs JSON: {e}")
            return False
        except Exception as e:
            logger.error(f"Error loading antonym glyphs: {e}")
            return False

    def load_primary_glyphs(self) -> bool:
        """Load primary glyphs from lexicon.

        Returns:
            bool: True if loaded successfully
        """
        try:
            if not self.glyph_lexicon.exists():
                logger.error(f"Glyph lexicon not found: {self.glyph_lexicon}")
                return False

            with open(self.glyph_lexicon, "r", encoding="utf-8") as f:
                glyphs_list = json.load(f)

            # Index by voltage_pair for easy lookup
            self.primary_glyphs = {}
            for glyph in glyphs_list:
                if isinstance(glyph, dict):
                    voltage_pair = glyph.get("voltage_pair", "")
                    if voltage_pair:
                        self.primary_glyphs[voltage_pair] = glyph

            logger.info(f"✓ Loaded {len(self.primary_glyphs)} primary glyphs")
            return True

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing glyph lexicon JSON: {e}")
            return False
        except Exception as e:
            logger.error(f"Error loading primary glyphs: {e}")
            return False

    def build_antonym_map(self) -> Dict[str, str]:
        """Build mapping from primary glyph name to antonym emotion.

        Returns:
            dict: Maps primary glyph_name -> antonym base_emotion
        """
        if not self.primary_glyphs or not self.antonym_glyphs:
            logger.warning("Cannot build antonym map without loaded glyphs")
            return {}

        self.antonym_map = {}

        # Heuristic mappings based on emotional opposites
        # Map by finding conceptually opposite emotions
        emotional_opposites = {
            # Joy opposites
            "joy": ["misery", "grief", "despair"],
            "happiness": ["sadness", "sorrow"],
            "delight": ["displeasure", "disgust"],
            "pleasure": ["pain", "suffering"],
            "comfort": ["discomfort", "unease"],
            "relief": ["tension", "burden"],
            "peace": ["turmoil", "conflict"],
            # Sorrow opposites
            "grief": ["joy", "celebration", "rejoicing"],
            "sadness": ["happiness", "cheer"],
            "misery": ["comfort", "fulfillment"],
            "despair": ["hope", "fulfillment"],
            # Calm opposites
            "stillness": ["chaos", "turbulence"],
            "peace": ["conflict", "turmoil"],
            "calm": ["agitation", "disturbance"],
            # Fear opposites
            "fear": ["courage", "bravery"],
            "anxiety": ["peace", "calm"],
            "dread": ["anticipation", "hope"],
            # Love opposites
            "love": ["hate", "indifference"],
            "affection": ["coldness", "detachment"],
            "belonging": ["isolation", "alienation"],
            # Strength opposites
            "strength": ["weakness", "fragility"],
            "power": ["powerlessness", "helplessness"],
            "confidence": ["doubt", "uncertainty"],
        }

        # For each primary glyph, find if there's an antonym
        for voltage_pair, primary_glyph in self.primary_glyphs.items():
            primary_name = primary_glyph.get("glyph_name", "").lower()

            # Check each antonym
            for antonym in self.antonym_glyphs:
                antonym_base = antonym.base_emotion.lower()

                # Direct name match
                if primary_name.lower() in antonym_base:
                    self.antonym_map[primary_glyph["glyph_name"]] = antonym.base_emotion
                    break

        logger.info(f"✓ Built antonym map with {len(self.antonym_map)} mappings")
        return self.antonym_map

    def initialize(self) -> bool:
        """Initialize the integration system.

        Returns:
            bool: True if initialization successful
        """
        try:
            # Load all data
            if not self.load_antonym_glyphs():
                return False

            if not self.load_primary_glyphs():
                return False

            # Build mapping
            self.build_antonym_map()

            self.loaded = True
            logger.info("✓ Antonym glyphs integration initialized")
            return True

        except Exception as e:
            logger.error(f"Error initializing antonym glyphs integration: {e}")
            return False

    def get_antonym_for_glyph(self, glyph_name: str) -> Optional[AntonymGlyph]:
        """Get the antonym glyph for a given primary glyph.

        Args:
            glyph_name: Name of the primary glyph

        Returns:
            AntonymGlyph if found, None otherwise
        """
        if not self.loaded:
            logger.warning("Antonym glyphs not initialized")
            return None

        if glyph_name not in self.antonym_map:
            return None

        antonym_emotion = self.antonym_map[glyph_name]

        # Find the antonym glyph
        for antonym in self.antonym_glyphs:
            if antonym.base_emotion.lower() == antonym_emotion.lower():
                return antonym

        return None

    def get_antonym_for_voltage_pair(self, voltage_pair: str) -> Optional[AntonymGlyph]:
        """Get the antonym glyph for a voltage pair.

        Args:
            voltage_pair: Voltage pair like "γ × γ" or "λ × λ"

        Returns:
            AntonymGlyph if found, None otherwise
        """
        if voltage_pair not in self.primary_glyphs:
            return None

        primary_glyph = self.primary_glyphs[voltage_pair]
        return self.get_antonym_for_glyph(primary_glyph.get("glyph_name", ""))

    def find_antonym_by_base_emotion(self, emotion: str) -> Optional[AntonymGlyph]:
        """Find antonym glyph by base emotion name.

        Args:
            emotion: Base emotion name

        Returns:
            AntonymGlyph if found, None otherwise
        """
        if not self.loaded:
            return None

        emotion_lower = emotion.lower()
        for antonym in self.antonym_glyphs:
            if antonym.base_emotion.lower() == emotion_lower:
                return antonym

        return None

    def list_all_antonyms(self) -> List[Dict]:
        """List all antonym glyphs with details.

        Returns:
            List of antonym glyph dictionaries
        """
        if not self.loaded:
            return []

        return [asdict(ag) for ag in self.antonym_glyphs]

    def search_antonyms(self, query: str) -> List[AntonymGlyph]:
        """Search antonym glyphs by base emotion, name, or description.

        Args:
            query: Search string

        Returns:
            List of matching antonym glyphs
        """
        if not self.loaded:
            return []

        query_lower = query.lower()
        results = []

        for antonym in self.antonym_glyphs:
            if (
                query_lower in antonym.base_emotion.lower()
                or query_lower in antonym.name.lower()
                or query_lower in antonym.description.lower()
            ):
                results.append(antonym)

        return results

    def get_emotional_opposite_pair(self, glyph_name: str) -> Optional[Tuple[Dict, AntonymGlyph]]:
        """Get a primary-antonym pair for display.

        Args:
            glyph_name: Name of primary glyph

        Returns:
            Tuple of (primary_glyph_dict, antonym_glyph) if found
        """
        if not self.loaded or glyph_name not in self.antonym_map:
            return None

        # Find primary glyph by name
        primary_glyph = None
        for vp, glyph in self.primary_glyphs.items():
            if glyph.get("glyph_name") == glyph_name:
                primary_glyph = glyph
                break

        if not primary_glyph:
            return None

        # Find antonym
        antonym = self.get_antonym_for_glyph(glyph_name)

        if not antonym:
            return None

        return (primary_glyph, antonym)

    def export_antonym_glyphs_to_json(self, output_path: str = "antonym_glyphs_indexed.json") -> bool:
        """Export all antonym glyphs to JSON for system integration.

        Args:
            output_path: Output file path

        Returns:
            bool: True if export successful
        """
        try:
            output = {
                "metadata": {
                    "total_antonym_glyphs": len(self.antonym_glyphs),
                    "total_primary_glyphs": len(self.primary_glyphs),
                    "antonym_mappings": len(self.antonym_map),
                },
                "antonym_glyphs": [asdict(ag) for ag in self.antonym_glyphs],
                "antonym_map": self.antonym_map,
            }

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)

            logger.info(f"✓ Exported antonym glyphs to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting antonym glyphs: {e}")
            return False

    def insert_antonyms_into_database(self) -> bool:
        """Insert antonym glyphs into SQLite database for persistence.

        Returns:
            bool: True if insertion successful
        """
        if not self.glyph_db.exists():
            logger.error(f"Glyph database not found: {self.glyph_db}")
            return False

        try:
            conn = sqlite3.connect(self.glyph_db)
            cursor = conn.cursor()

            # Check if antonym glyphs table exists, create if not
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS antonym_glyphs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    base_emotion TEXT NOT NULL,
                    pairing TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    opposite_emotions TEXT,
                    activation_signals TEXT,
                    gate TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Insert antonym glyphs
            for antonym in self.antonym_glyphs:
                cursor.execute(
                    """
                    INSERT INTO antonym_glyphs 
                    (base_emotion, pairing, name, description, opposite_emotions, activation_signals, gate)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        antonym.base_emotion,
                        antonym.pairing,
                        antonym.name,
                        antonym.description,
                        json.dumps(antonym.opposite_emotions),
                        json.dumps(antonym.activation_signals),
                        antonym.gate,
                    ),
                )

            conn.commit()
            conn.close()

            logger.info(f"✓ Inserted {len(self.antonym_glyphs)} antonym glyphs into database")
            return True

        except Exception as e:
            logger.error(f"Error inserting antonym glyphs into database: {e}")
            return False


def main():
    """Test the antonym glyphs integration."""
    integration = AntonymGlyphsIntegration()

    if not integration.initialize():
        logger.error("Failed to initialize antonym glyphs integration")
        return

    # Show summary
    print("\n" + "=" * 80)
    print("ANTONYM GLYPHS INTEGRATION SUMMARY")
    print("=" * 80)
    print(f"✓ Antonym glyphs loaded: {len(integration.antonym_glyphs)}")
    print(f"✓ Primary glyphs loaded: {len(integration.primary_glyphs)}")
    print(f"✓ Antonym mappings created: {len(integration.antonym_map)}")

    # Show sample antonyms
    print("\n" + "─" * 80)
    print("SAMPLE ANTONYM GLYPHS (first 10)")
    print("─" * 80)
    for i, antonym in enumerate(integration.antonym_glyphs[:10], 1):
        print(f"\n{i}. {antonym.base_emotion}")
        print(f"   Pairing: {antonym.pairing}")
        print(f"   Name: {antonym.name}")
        print(f"   Description: {antonym.description}")

    # Show example opposite pair
    print("\n" + "─" * 80)
    print("EXAMPLE OPPOSITE PAIRS")
    print("─" * 80)

    # Find some examples
    for primary_name in list(integration.primary_glyphs.values())[:5]:
        glyph_name = primary_name.get("glyph_name", "")
        pair = integration.get_emotional_opposite_pair(glyph_name)
        if pair:
            primary, antonym = pair
            print(f"\n🔹 {primary['glyph_name']}")
            print(f"   Voltage Pair: {primary.get('voltage_pair')}")
            print(f"   Description: {primary.get('description')[:80]}...")
            print(f"\n🔸 ↔ Antonym: {antonym.base_emotion}")
            print(f"   Pairing: {antonym.pairing}")
            print(f"   Name: {antonym.name}")
            print(f"   Description: {antonym.description}")

    print("\n" + "=" * 80)
    print("✓ Integration test complete!")
    print("=" * 80)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(name)s] - %(message)s")
    main()

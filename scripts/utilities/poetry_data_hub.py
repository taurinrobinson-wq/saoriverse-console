#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Poetry Data Integration Hub

Makes cleaned, validated poetry text available to all processing modes:
- Signal extraction
- Lexicon learning
- Glyph generation
- User interactions
- Ritual processing

Provides unified interface for:
1. Clean poetry data
2. Metadata about each collection
3. Processing status tracking
4. Quality metrics
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class PoetryDataHub:
    """Unified hub for poetry data access across all processing modes."""

    def __init__(self, data_dir: str = "poetry_data"):
        """
        Initialize poetry data hub.

        Args:
            data_dir: Root directory for poetry data storage
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Subdirectories
        self.raw_dir = self.data_dir / "raw"
        self.clean_dir = self.data_dir / "clean"
        self.validated_dir = self.data_dir / "validated"
        self.metadata_dir = self.data_dir / "metadata"
        self.cache_dir = self.data_dir / "cache"

        for d in [self.raw_dir, self.clean_dir, self.validated_dir, self.metadata_dir, self.cache_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self.db_path = self.data_dir / "poetry_index.db"
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database for metadata."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Poetry collections table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                gutenberg_id INTEGER,
                poet TEXT,
                period TEXT,
                description TEXT,
                raw_path TEXT,
                clean_path TEXT,
                validated_path TEXT,
                status TEXT,
                raw_bytes INTEGER,
                clean_bytes INTEGER,
                word_count INTEGER,
                line_count INTEGER,
                created_at TIMESTAMP,
                cleaned_at TIMESTAMP,
                validated_at TIMESTAMP
            )
        """
        )

        # Processing log table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS processing_log (
                id INTEGER PRIMARY KEY,
                collection_name TEXT,
                process_type TEXT,
                status TEXT,
                details TEXT,
                timestamp TIMESTAMP,
                FOREIGN KEY(collection_name) REFERENCES collections(name)
            )
        """
        )

        # Quality metrics table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS quality_metrics (
                id INTEGER PRIMARY KEY,
                collection_name TEXT,
                artifacts_removed INTEGER,
                fragmented_lines_fixed INTEGER,
                encoding_issues_fixed INTEGER,
                completeness_score REAL,
                usability_score REAL,
                validated_at TIMESTAMP,
                FOREIGN KEY(collection_name) REFERENCES collections(name)
            )
        """
        )

        conn.commit()
        conn.close()

    def register_collection(
        self, name: str, gutenberg_id: int, poet: str, period: str = None, description: str = None, raw_path: str = None
    ) -> bool:
        """
        Register a poetry collection.

        Args:
            name: Collection identifier
            gutenberg_id: Project Gutenberg ID
            poet: Author name
            period: Time period
            description: Collection description
            raw_path: Path to raw downloaded file

        Returns:
            Success
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO collections
                (name, gutenberg_id, poet, period, description, raw_path, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (name, gutenberg_id, poet, period, description, raw_path, "registered", datetime.now()),
            )

            conn.commit()
            logger.info(f"✓ Registered collection: {name} by {poet}")
            return True

        except sqlite3.IntegrityError:
            logger.warning(f"Collection already registered: {name}")
            return False

        finally:
            conn.close()

    def store_clean_text(self, collection_name: str, text: str, metrics: Dict = None) -> Path:
        """
        Store cleaned poetry text.

        Args:
            collection_name: Collection identifier
            text: Cleaned text
            metrics: Cleaning metrics

        Returns:
            Path to saved file
        """
        # Save cleaned text
        clean_path = self.clean_dir / f"{collection_name}_clean.txt"

        with open(clean_path, "w", encoding="utf-8") as f:
            f.write(text)

        word_count = len(text.split())
        line_count = len(text.split("\n"))

        # Update database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE collections
            SET clean_path = ?, clean_bytes = ?, word_count = ?, line_count = ?, 
                status = 'cleaned', cleaned_at = ?
            WHERE name = ?
        """,
            (str(clean_path), len(text), word_count, line_count, datetime.now(), collection_name),
        )

        # Store quality metrics
        if metrics:
            cursor.execute(
                """
                INSERT INTO quality_metrics
                (collection_name, artifacts_removed, fragmented_lines_fixed, 
                 encoding_issues_fixed, validated_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    collection_name,
                    metrics.get("artifacts_removed", 0),
                    metrics.get("fragmented_lines_fixed", 0),
                    metrics.get("encoding_issues_fixed", 0),
                    datetime.now(),
                ),
            )

        conn.commit()
        conn.close()

        logger.info(f"✓ Stored clean text: {collection_name} ({word_count} words)")
        return clean_path

    def mark_validated(
        self, collection_name: str, completeness_score: float = 1.0, usability_score: float = 1.0
    ) -> bool:
        """
        Mark collection as validated.

        Args:
            collection_name: Collection identifier
            completeness_score: 0.0-1.0 score
            usability_score: 0.0-1.0 score

        Returns:
            Success
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Move file to validated directory
        clean_path = self.clean_dir / f"{collection_name}_clean.txt"
        if clean_path.exists():
            validated_path = self.validated_dir / f"{collection_name}.txt"
            clean_path.rename(validated_path)

        # Update database
        cursor.execute(
            """
            UPDATE collections
            SET validated_path = ?, status = 'validated', validated_at = ?
            WHERE name = ?
        """,
            (str(validated_path) if clean_path.exists() else None, datetime.now(), collection_name),
        )

        cursor.execute(
            """
            UPDATE quality_metrics
            SET completeness_score = ?, usability_score = ?, validated_at = ?
            WHERE collection_name = ?
        """,
            (completeness_score, usability_score, datetime.now(), collection_name),
        )

        conn.commit()
        conn.close()

        logger.info(f"✓ Marked as validated: {collection_name}")
        return True

    def get_collection(self, collection_name: str) -> Dict:
        """
        Get collection metadata and paths.

        Args:
            collection_name: Collection identifier

        Returns:
            Collection dict with paths and metadata
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT name, gutenberg_id, poet, period, description, 
                   raw_path, clean_path, validated_path, status,
                   raw_bytes, clean_bytes, word_count, line_count,
                   created_at, cleaned_at, validated_at
            FROM collections
            WHERE name = ?
        """,
            (collection_name,),
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            "name": row[0],
            "gutenberg_id": row[1],
            "poet": row[2],
            "period": row[3],
            "description": row[4],
            "raw_path": row[5],
            "clean_path": row[6],
            "validated_path": row[7],
            "status": row[8],
            "raw_bytes": row[9],
            "clean_bytes": row[10],
            "word_count": row[11],
            "line_count": row[12],
            "created_at": row[13],
            "cleaned_at": row[14],
            "validated_at": row[15],
        }

    def get_clean_text(self, collection_name: str) -> Optional[str]:
        """
        Get cleaned, validated poetry text.

        Args:
            collection_name: Collection identifier

        Returns:
            Clean text or None
        """
        collection = self.get_collection(collection_name)
        if not collection:
            return None

        # Try validated path first, then clean path
        for path_key in ["validated_path", "clean_path"]:
            path_str = collection.get(path_key)
            if path_str:
                path = Path(path_str)
                if path.exists():
                    with open(path, "r", encoding="utf-8") as f:
                        return f.read()

        return None

    def get_all_collections(self, status: str = None) -> List[Dict]:
        """
        Get all registered collections.

        Args:
            status: Filter by status ('validated', 'cleaned', 'registered')

        Returns:
            List of collection dicts
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if status:
            cursor.execute("SELECT * FROM collections WHERE status = ?", (status,))
        else:
            cursor.execute("SELECT * FROM collections")

        rows = cursor.fetchall()
        conn.close()

        collections = []
        for row in rows:
            collections.append(
                {
                    "name": row[1],
                    "gutenberg_id": row[2],
                    "poet": row[3],
                    "period": row[4],
                    "status": row[8],
                    "word_count": row[11],
                    "line_count": row[12],
                }
            )

        return collections

    def get_hub_status(self) -> Dict:
        """
        Get overall hub status and statistics.

        Returns:
            Status dict
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM collections")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM collections WHERE status = 'validated'")
        validated = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM collections WHERE status = 'cleaned'")
        cleaned = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(word_count) FROM collections")
        total_words = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(clean_bytes) FROM collections")
        total_bytes = cursor.fetchone()[0] or 0

        conn.close()

        return {
            "total_collections": total,
            "validated": validated,
            "cleaned": cleaned,
            "registered_only": total - validated - cleaned,
            "total_words": total_words,
            "total_bytes": total_bytes,
            "validated_percent": (validated / total * 100) if total > 0 else 0,
        }

    def export_for_processing(self, output_dir: str = None) -> Dict:
        """
        Export all clean, validated poetry for processing.

        Args:
            output_dir: Directory to export to

        Returns:
            Export manifest
        """
        output_path = Path(output_dir) if output_dir else self.data_dir / "export"
        output_path.mkdir(parents=True, exist_ok=True)

        collections = self.get_all_collections(status="validated")

        manifest = {
            "exported_at": datetime.now().isoformat(),
            "collections": [],
            "statistics": {
                "total_collections": 0,
                "total_words": 0,
                "total_bytes": 0,
            },
        }

        for coll in collections:
            collection_name = coll["name"]
            text = self.get_clean_text(collection_name)

            if text:
                # Export individual file
                export_file = output_path / f"{collection_name}.txt"
                with open(export_file, "w", encoding="utf-8") as f:
                    f.write(text)

                manifest["collections"].append(
                    {
                        "name": collection_name,
                        "poet": coll["poet"],
                        "file": str(export_file),
                        "words": coll["word_count"],
                    }
                )

                manifest["statistics"]["total_collections"] += 1
                manifest["statistics"]["total_words"] += coll["word_count"]
                manifest["statistics"]["total_bytes"] += len(text)

        # Export manifest
        manifest_file = output_path / "manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"✓ Exported {manifest['statistics']['total_collections']} collections")
        logger.info(f"  Total words: {manifest['statistics']['total_words']:,}")
        logger.info(f"  Manifest: {manifest_file}")

        return manifest

    def log_processing(self, collection_name: str, process_type: str, status: str, details: str = None):
        """Log processing event."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO processing_log (collection_name, process_type, status, details, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """,
            (collection_name, process_type, status, details, datetime.now()),
        )

        conn.commit()
        conn.close()


class ProcessingModeAdapter:
    """Adapt clean poetry data for specific processing modes."""

    def __init__(self, hub: PoetryDataHub):
        """Initialize adapter."""
        self.hub = hub

    def for_signal_extraction(self) -> Dict[str, str]:
        """
        Get poetry formatted for signal extraction.

        Returns:
            Dict: {collection_name: clean_text}
        """
        collections = self.hub.get_all_collections(status="validated")

        data = {}
        for coll in collections:
            text = self.hub.get_clean_text(coll["name"])
            if text:
                data[coll["name"]] = text

        logger.info(f"✓ Loaded {len(data)} collections for signal extraction")
        return data

    def for_lexicon_learning(self) -> Dict[str, str]:
        """
        Get poetry formatted for lexicon learning.

        Same as signal extraction - clean text is universal.
        """
        return self.for_signal_extraction()

    def for_glyph_generation(self) -> List[Tuple[str, str]]:
        """
        Get poetry formatted for glyph generation.

        Returns:
            List: [(collection_name, text), ...]
        """
        collections = self.hub.get_all_collections(status="validated")

        data = []
        for coll in collections:
            text = self.hub.get_clean_text(coll["name"])
            if text:
                data.append((coll["name"], text))

        logger.info(f"✓ Loaded {len(data)} collections for glyph generation")
        return data

    def for_ritual_processing(self) -> Dict[str, str]:
        """
        Get poetry formatted for ritual processing.

        Ensures text is complete and emotionally coherent.
        """
        return self.for_signal_extraction()


def main():
    """Example usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Poetry data integration hub")
    parser.add_argument("--register", action="store_true", help="Register collections")
    parser.add_argument("--status", action="store_true", help="Show hub status")
    parser.add_argument("--export", type=str, help="Export validated collections")

    args = parser.parse_args()

    hub = PoetryDataHub("poetry_data")

    if args.status:
        status = hub.get_hub_status()
        print("\n" + "=" * 60)
        print("POETRY DATA HUB STATUS")
        print("=" * 60)
        print(f"Total collections: {status['total_collections']}")
        print(f"Validated: {status['validated']} ({status['validated_percent']:.1f}%)")
        print(f"Cleaned: {status['cleaned']}")
        print(f"Total words: {status['total_words']:,}")
        print(f"Total bytes: {status['total_bytes']:,}")
        print("=" * 60)

    elif args.export:
        manifest = hub.export_for_processing(args.export)
        print(f"\n✓ Exported to: {args.export}")
        print(f"  Collections: {manifest['statistics']['total_collections']}")
        print(f"  Words: {manifest['statistics']['total_words']:,}")


if __name__ == "__main__":
    main()

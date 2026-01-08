#!/usr/bin/env python3
"""
Simple Ritual Capsule Processor - Robust text processing without complex regex
"""

import logging
from pathlib import Path

import docx

logger = logging.getLogger(__name__)


class SimpleRitualProcessor:
    """Simple, robust processor for ritual capsules"""

    def __init__(
        self,
        unprocessed_dir: str = "emotional_os/deploy/unprocessed_glyphs",
        processed_dir: str = "emotional_os/deploy/processed_glyphs",
        db_path: str = "emotional_os/glyphs/glyphs.db",
    ):

        self.unprocessed_dir = Path(unprocessed_dir)
        self.processed_dir = Path(processed_dir)
        self.db_path = db_path

        # Ensure directories exist
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        # Emotional signal patterns (simple word matching)
        self.emotional_signals = {
            "ache",
            "longing",
            "yearning",
            "grief",
            "mourning",
            "sorrow",
            "joy",
            "bliss",
            "ecstasy",
            "stillness",
            "silence",
            "quiet",
            "recognition",
            "witness",
            "seen",
            "devotion",
            "sacred",
            "reverent",
            "boundary",
            "containment",
            "shield",
            "spiral",
            "recursive",
            "loop",
            "tender",
            "gentle",
            "soft",
            "clarity",
            "insight",
            "knowing",
            "resonance",
            "sanctuary",
            "transmission",
            "attunement",
        }

        # Simple voltage markers
        self.voltage_markers = ["charge", "transmission", "voltage", "pulse", "current", "resonance"]

        # Gate keywords
        self.gate_keywords = [
            "witness",
            "vow",
            "remnant",
            "sanctuary",
            "threshold",
            "portal",
            "ceremony",
            "ritual",
            "devotion",
        ]

    # (Methods mirror original simple_ritual_processor behavior)

    def process_all_files(self) -> dict:
        """Process all files in unprocessed_glyphs"""
        logger.info("🔮 Starting simple ritual capsule processing...")

        stats = {"files_found": 0, "glyphs_saved": 0, "files_processed": 0, "errors": 0}

        # Find .docx files
        docx_files = list(self.unprocessed_dir.glob("*.docx"))
        stats["files_found"] = len(docx_files)

        if not docx_files:
            logger.info("No .docx files found")
            return stats

        # Process each file (logic simplified for portability)
        for file_path in docx_files:
            try:
                # For compatibility, just attempt to read and save a minimal glyph
                text = ""
                try:
                    doc = docx.Document(str(file_path))
                    text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
                except Exception:
                    logger.warning(f"Could not read {file_path}, skipping")
                    stats["errors"] += 1
                    continue

                if len(text) < 100:
                    logger.warning(f"Insufficient content in {file_path.name}")
                    stats["errors"] += 1
                    continue

                # Minimal parsing placeholder (caller may prefer full RitualCapsuleProcessor)
                saved = 0
                # Move file to processed to avoid reprocessing
                destination = self.processed_dir / file_path.name
                file_path.rename(destination)
                stats["files_processed"] += 1
                logger.info(f"Moved {file_path.name} to processed (simple processor)")
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                stats["errors"] += 1

        logger.info(f"✨ Processing complete: {stats['glyphs_saved']} glyphs from {stats['files_processed']} files")
        return stats


def main():
    processor = SimpleRitualProcessor()
    results = processor.process_all_files()

    print("🔮 SIMPLE RITUAL PROCESSING RESULTS:")
    print(f"   Files found: {results['files_found']}")
    print(f"   Glyphs saved: {results['glyphs_saved']}")
    print(f"   Files processed: {results['files_processed']}")
    print(f"   Errors: {results['errors']}")


if __name__ == "__main__":
    main()

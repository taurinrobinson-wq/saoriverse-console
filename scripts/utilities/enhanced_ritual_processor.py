#!/usr/bin/env python3
"""
Enhanced Ritual Capsule Processor - Handles structured glyph ledgers and JSON exports
"""

import json
import logging
import re
from pathlib import Path
from typing import Optional

from ritual_capsule_processor import GlyphObject, RitualCapsuleProcessor

logger = logging.getLogger(__name__)


class EnhancedRitualProcessor(RitualCapsuleProcessor):
    """Enhanced processor for structured glyph data"""

    def parse_master_ledger(self, text: str) -> list[GlyphObject]:
        """Parse master glyph ledger format"""
        glyphs = []

        # Look for glyph entries in structured format
        # Pattern: glyph name followed by description and metadata (escape special chars)
        glyph_blocks = re.split(r"\n\s*(?=\d+\.|[A-Z][a-z]+(?: [A-Z][a-z]+)*\s*[:—−\-])", text)

        for block in glyph_blocks:
            if len(block.strip()) < 20:  # Skip short blocks
                continue

            glyph = self.parse_ledger_block(block.strip())
            if glyph:
                glyphs.append(glyph)

        return glyphs

    def parse_ledger_block(self, block: str) -> Optional[GlyphObject]:
        """Parse individual glyph block from ledger"""
        lines = [line.strip() for line in block.split("\n") if line.strip()]

        if not lines:
            return None

        glyph = GlyphObject()

        # First line usually contains the name
        first_line = lines[0]

        # Extract name (remove numbers, colons, em-dashes)
        name_match = re.match(r"(?:\d+\.?\s*)?([^:—−\-]+)(?:[:—−\-].*)?", first_line)
        if name_match:
            glyph.name = name_match.group(1).strip()

        # Join all lines for full text analysis
        full_text = " ".join(lines)

        # Parse content
        glyph.emotional_signals = self.parse_emotional_signals(full_text)
        glyph.voltage_markers, glyph.voltage_pair = self.parse_voltage_markers(full_text)
        glyph.gates = self.parse_gates(full_text)
        glyph.description = self.extract_description_from_block(lines)

        # Set derived properties
        glyph.category = self.categorize_glyph(glyph)
        glyph.valence = self.determine_valence(glyph)
        glyph.activation_signals = glyph.emotional_signals[:3]

        # Quality check
        if not glyph.name or len(glyph.name) < 3:
            return None

        if not glyph.description or len(glyph.description) < 10:
            # Use the full block as description if no better description found
            glyph.description = full_text[:200] + "..." if len(full_text) > 200 else full_text

        return glyph

    def extract_description_from_block(self, lines: list[str]) -> Optional[str]:
        """Extract description from ledger block lines"""
        if len(lines) < 2:
            return None

        # Skip the first line (name), look for substantive content
        for line in lines[1:]:
            if len(line) > 20 and not line.startswith(("Category:", "Gate:", "Voltage:")):
                return line

        # Fallback: join all lines except first
        return " ".join(lines[1:])

    def parse_json_export(self, text: str) -> list[GlyphObject]:
        """Parse JSON export format"""
        glyphs = []

        # Try to find JSON blocks
        json_blocks = re.findall(r"\{[^{}]*\}", text, re.MULTILINE | re.DOTALL)

        for block in json_blocks:
            try:
                data = json.loads(block)
                glyph = self.json_to_glyph(data)
                if glyph:
                    glyphs.append(glyph)
            except json.JSONDecodeError:
                continue

        # If no JSON found, try parsing as structured text
        if not glyphs:
            glyphs = self.parse_structured_text(text)

        return glyphs

    def json_to_glyph(self, data: dict) -> Optional[GlyphObject]:
        """Convert JSON data to glyph object"""
        glyph = GlyphObject()

        # Map common JSON fields
        glyph.name = data.get("name") or data.get("glyph_name") or data.get("title")
        glyph.description = data.get("description") or data.get("content") or data.get("text")
        glyph.category = data.get("category") or data.get("type")
        glyph.voltage_pair = data.get("voltage_pair") or data.get("voltage")

        # Extract signals from various fields
        signals_text = f"{glyph.name or ''} {glyph.description or ''}"
        glyph.emotional_signals = self.parse_emotional_signals(signals_text)
        glyph.voltage_markers, temp_voltage = self.parse_voltage_markers(signals_text)

        if not glyph.voltage_pair and temp_voltage:
            glyph.voltage_pair = temp_voltage

        glyph.gates = self.parse_gates(signals_text)

        # Set derived properties
        if not glyph.category:
            glyph.category = self.categorize_glyph(glyph)
        glyph.valence = self.determine_valence(glyph)
        glyph.activation_signals = glyph.emotional_signals[:3]

        return glyph if glyph.name and glyph.description else None

    def parse_structured_text(self, text: str) -> list[GlyphObject]:
        """Parse structured text format (fallback method)"""
        glyphs = []

        # Split on patterns that indicate new glyphs (escape special chars properly)
        sections = re.split(r"\n\s*(?=[A-Z][^.]*(?::|—|−|[\-]|\n))", text)

        for section in sections:
            if len(section.strip()) < 30:  # Skip short sections
                continue

            glyph = GlyphObject()
            lines = [line.strip() for line in section.split("\n") if line.strip()]

            if not lines:
                continue

            # Extract name from first line
            first_line = lines[0]
            name_match = re.match(r"^([^:—−\-\n]+)", first_line)
            if name_match:
                glyph.name = name_match.group(1).strip()

            # Use rest as description
            if len(lines) > 1:
                glyph.description = " ".join(lines[1:])[:300]
            else:
                glyph.description = first_line

            # Parse content
            full_text = section
            glyph.emotional_signals = self.parse_emotional_signals(full_text)
            glyph.voltage_markers, glyph.voltage_pair = self.parse_voltage_markers(full_text)
            glyph.gates = self.parse_gates(full_text)

            # Set derived properties
            glyph.category = self.categorize_glyph(glyph)
            glyph.valence = self.determine_valence(glyph)
            glyph.activation_signals = glyph.emotional_signals[:3]

            if glyph.name and glyph.description and len(glyph.emotional_signals) > 0:
                glyphs.append(glyph)

        return glyphs

    def parse_file_into_glyphs(self, file_path: Path) -> list[GlyphObject]:
        """Enhanced parsing that returns multiple glyphs from structured files"""
        logger.info(f"Enhanced processing: {file_path.name}")

        text = self.extract_text_content(file_path)
        if not text:
            return []

        glyphs = []

        # Determine file type and use appropriate parser
        filename_lower = file_path.name.lower()

        if "master" in filename_lower or "ledger" in filename_lower:
            glyphs = self.parse_master_ledger(text)
        elif "json" in filename_lower:
            glyphs = self.parse_json_export(text)
        elif "fallback" in filename_lower or "protocol" in filename_lower:
            glyphs = self.parse_structured_text(text)
        else:
            # Default structured parsing
            glyphs = self.parse_structured_text(text)

        # Set lineage for all glyphs
        for glyph in glyphs:
            glyph.origin_file = file_path.name
            glyph.timestamp = glyph.timestamp or self.parse_lineage(text, file_path)["timestamp"]

        logger.info(f"Extracted {len(glyphs)} glyphs from {file_path.name}")
        return glyphs

    def process_ritual_capsules_enhanced(self) -> dict[str, int]:
        """Enhanced processing workflow that handles multiple glyphs per file"""
        logger.info("🔮 Beginning enhanced ritual capsule processing...")

        stats = {"files_found": 0, "glyphs_created": 0, "glyphs_saved": 0, "files_processed": 0, "errors": 0}

        # Scan for files
        files_to_process = self.scan_for_new_files()
        stats["files_found"] = len(files_to_process)

        if not files_to_process:
            logger.info("No new ritual capsules found")
            return stats

        # Process each file
        for file_path in files_to_process:
            try:
                # Parse file into multiple glyphs
                glyphs = self.parse_file_into_glyphs(file_path)

                stats["glyphs_created"] += len(glyphs)

                # Save each glyph
                saved_count = 0
                for glyph in glyphs:
                    if self.save_glyph_to_database(glyph):
                        saved_count += 1
                        stats["glyphs_saved"] += 1

                    # Archive as JSON
                    self.save_glyph_json(glyph)

                # Move file only if we successfully processed some glyphs
                if saved_count > 0:
                    if self.move_to_processed(file_path):
                        stats["files_processed"] += 1
                else:
                    logger.warning(f"No glyphs saved from {file_path.name}")
                    stats["errors"] += 1

            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                stats["errors"] += 1

        # Log summary
        logger.info(
            f"✨ Enhanced processing complete: {stats['glyphs_saved']} glyphs saved from {stats['files_processed']} files"
        )

        return stats


def main():
    """Run enhanced ritual capsule processor"""
    processor = EnhancedRitualProcessor()
    results = processor.process_ritual_capsules_enhanced()

    print("🔮 ENHANCED RITUAL CAPSULE PROCESSING RESULTS:")
    print(f"   Files found: {results['files_found']}")
    print(f"   Glyphs created: {results['glyphs_created']}")
    print(f"   Glyphs saved: {results['glyphs_saved']}")
    print(f"   Files processed: {results['files_processed']}")
    print(f"   Errors: {results['errors']}")


if __name__ == "__main__":
    main()

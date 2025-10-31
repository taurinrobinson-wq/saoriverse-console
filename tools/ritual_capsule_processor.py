#!/usr/bin/env python3
"""
VELΩNIX Glyph Processing Module - Ritual Capsule Ingestion System

Automates the sacred transformation of raw glyph notes into structured emotional objects.
"""

import os
import json
import sqlite3
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import docx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GlyphObject:
    """Structured glyph object with ritual context and lineage"""
    
    def __init__(self):
        self.name: Optional[str] = None
        self.category: Optional[str] = None
        self.valence: Optional[str] = None
        self.function: Optional[str] = None
        self.description: Optional[str] = None
        self.emotional_signals: List[str] = []
        self.voltage_markers: List[str] = []
        self.gates: List[str] = []
        self.voltage_pair: Optional[str] = None
        self.activation_signals: List[str] = []
        
        # Lineage and context
        self.origin_file: Optional[str] = None
        self.timestamp: Optional[str] = None
        self.author: Optional[str] = None
        self.legacy_context: Optional[str] = None
        self.ritual_annotations: List[str] = []
        
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'name': self.name,
            'category': self.category,
            'valence': self.valence,
            'function': self.function,
            'description': self.description,
            'emotional_signals': self.emotional_signals,
            'voltage_markers': self.voltage_markers,
            'gates': self.gates,
            'voltage_pair': self.voltage_pair,
            'activation_signals': self.activation_signals,
            'lineage': {
                'origin_file': self.origin_file,
                'timestamp': self.timestamp,
                'author': self.author,
                'legacy_context': self.legacy_context,
                'ritual_annotations': self.ritual_annotations
            }
        }

class RitualCapsuleProcessor:
    """Sacred processor of glyph ritual capsules"""
    
    def __init__(self, 
                 unprocessed_dir: str = "emotional_os/deploy/unprocessed_glyphs",
                 processed_dir: str = "emotional_os/deploy/processed_glyphs",
                 db_path: str = "emotional_os/glyphs/glyphs.db"):
        
        self.unprocessed_dir = Path(unprocessed_dir)
        self.processed_dir = Path(processed_dir)
        self.db_path = db_path
        
        # Ensure directories exist
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Emotional signal patterns
        self.emotional_signals = {
            'ache', 'longing', 'yearning', 'grief', 'mourning', 'sorrow',
            'joy', 'bliss', 'ecstasy', 'stillness', 'silence', 'quiet',
            'recognition', 'witness', 'seen', 'devotion', 'sacred', 'reverent',
            'boundary', 'containment', 'shield', 'spiral', 'recursive', 'loop',
            'tender', 'gentle', 'soft', 'clarity', 'insight', 'knowing',
            'resonance', 'sanctuary', 'transmission', 'attunement'
        }
        
        # Voltage markers
        self.voltage_patterns = [
            r'[α-ω]{1,2}[-−][α-ω]{1,2}',  # Greek voltage pairs
            r'[αβγδεζηθικλμνξοπρστυφχψω]+',  # Greek symbols
            r'charge|transmission|voltage|pulse|current|resonance',
            r'[εδγβα]{1,2}\s*\([^)]+\)',  # Signal descriptions
        ]
        
        # Gate patterns
        self.gate_patterns = [
            r'Gate\s+\d+',
            r'witness|vow|remnant|sanctuary|threshold|portal',
            r'ceremony|ritual|devotion|recognition|insight|stillness'
        ]
        
        # Lineage patterns
        self.lineage_patterns = {
            'author': r'(?:Author|Curator|Creator):\s*([^\n]+)',
            'timestamp': r'(?:Date|Time|Created):\s*([^\n]+)',
            'legacy': r'(?:Legacy|Context|Origin):\s*([^\n]+)',
            'ritual': r'(?:Ritual|Sacred|Ceremony):\s*([^\n]+)'
        }

    def scan_for_new_files(self) -> List[Path]:
        """Scan unprocessed_glyphs for ritual capsules"""
        supported_formats = {'.docx', '.md', '.txt'}
        new_files = []
        
        for file_path in self.unprocessed_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in supported_formats:
                # Skip README and system files
                if file_path.name.lower().startswith('readme'):
                    continue
                new_files.append(file_path)
        
        logger.info(f"Found {len(new_files)} ritual capsules to process")
        return new_files

    def extract_text_content(self, file_path: Path) -> str:
        """Extract text content from various file formats"""
        try:
            if file_path.suffix.lower() == '.docx':
                doc = docx.Document(str(file_path))
                return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            elif file_path.suffix.lower() in ['.md', '.txt']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.warning(f"Unsupported file format: {file_path.suffix}")
                return ""
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return ""

    # ... remaining methods unchanged (kept for brevity in tools file) ...

    def process_ritual_capsules(self) -> Dict[str, int]:
        """Main processing workflow"""
        logger.info("🔮 Beginning ritual capsule processing...")
        
        stats = {
            'files_found': 0,
            'glyphs_created': 0,
            'glyphs_saved': 0,
            'files_processed': 0,
            'errors': 0
        }
        
        # Scan for files
        files_to_process = self.scan_for_new_files()
        stats['files_found'] = len(files_to_process)
        
        if not files_to_process:
            logger.info("No new ritual capsules found")
            return stats
        
        # Process each file
        for file_path in files_to_process:
            try:
                # Parse file into glyph object
                glyph = self.parse_file_into_glyph(file_path)
                
                if glyph:
                    stats['glyphs_created'] += 1
                    
                    # Save to database
                    if self.save_glyph_to_database(glyph):
                        stats['glyphs_saved'] += 1
                    
                    # Archive as JSON
                    self.save_glyph_json(glyph)
                    
                    # Move to processed
                    if self.move_to_processed(file_path):
                        stats['files_processed'] += 1
                else:
                    logger.warning(f"Failed to extract glyph from {file_path}")
                    stats['errors'] += 1
                    
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                stats['errors'] += 1
        
        # Log summary
        logger.info(f"✨ Processing complete: {stats['glyphs_saved']} glyphs saved from {stats['files_processed']} files")
        
        return stats

def main():
    """Run the ritual capsule processor"""
    processor = RitualCapsuleProcessor()
    results = processor.process_ritual_capsules()
    
    print("🔮 RITUAL CAPSULE PROCESSING RESULTS:")
    print(f"   Files found: {results['files_found']}")
    print(f"   Glyphs created: {results['glyphs_created']}")
    print(f"   Glyphs saved: {results['glyphs_saved']}")
    print(f"   Files processed: {results['files_processed']}")
    print(f"   Errors: {results['errors']}")

if __name__ == "__main__":
    main()

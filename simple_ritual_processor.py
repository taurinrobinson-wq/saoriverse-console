#!/usr/bin/env python3
"""
Simple Ritual Capsule Processor - Robust text processing without complex regex
"""

import os
import json
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from tools.simple_ritual_processor import main

if __name__ == '__main__':
    main()
        glyph.voltage_markers = [marker for marker in self.voltage_markers if marker in text_lower]
        
        # Find gates
        glyph.gates = [gate for gate in self.gate_keywords if gate in text_lower]
        
        # Set derived properties
        glyph.category = self.categorize_glyph(glyph)
        glyph.valence = self.determine_valence(glyph)
        glyph.activation_signals = glyph.emotional_signals[:3]
        
        # Create voltage pair if none found
        if not glyph.voltage_pair:
            category_prefix = (glyph.category or 'glyph')[:2].lower()
            glyph.voltage_pair = f"{category_prefix}-{hash(glyph.name or '') % 100:02d}"
        
        # Lineage
        glyph.origin_file = file_name
        glyph.timestamp = datetime.now().isoformat()
        
        # Quality check
        if (glyph.name and len(glyph.name) > 5 and 
            glyph.description and len(glyph.description) > 20 and
            len(glyph.emotional_signals) > 0):
            return glyph
        
        return None
    
    def categorize_glyph(self, glyph: GlyphObject) -> str:
        """Simple categorization based on emotional signals"""
        signals = set(glyph.emotional_signals)
        
        if signals & {'ache', 'longing', 'yearning'}:
            return 'Longing'
        elif signals & {'grief', 'mourning', 'sorrow'}:
            return 'Grief'
        elif signals & {'joy', 'bliss', 'ecstasy'}:
            return 'Joy'
        elif signals & {'stillness', 'silence', 'quiet'}:
            return 'Stillness'
        elif signals & {'recognition', 'witness', 'seen'}:
            return 'Recognition'
        elif signals & {'devotion', 'sacred', 'reverent'}:
            return 'Devotion'
        elif signals & {'boundary', 'containment', 'shield'}:
            return 'Containment'
        else:
            return 'Complex'
    
    def determine_valence(self, glyph: GlyphObject) -> str:
        """Simple valence determination"""
        signals = set(glyph.emotional_signals)
        
        positive = signals & {'joy', 'bliss', 'ecstasy', 'resonance', 'sanctuary'}
        negative = signals & {'grief', 'sorrow', 'ache', 'mourning'}
        neutral = signals & {'stillness', 'quiet', 'witness'}
        
        if positive and not negative:
            return 'Positive'
        elif negative and not positive:
            return 'Negative'
        elif neutral:
            return 'Neutral'
        else:
            return 'Mixed'
    
    def assign_gate(self, glyph: GlyphObject) -> str:
        """Assign gate based on category"""
        gate_mapping = {
            'Containment': 'Gate 2',
            'Longing': 'Gate 4',
            'Grief': 'Gate 4',
            'Joy': 'Gate 5',
            'Stillness': 'Gate 5',
            'Complex': 'Gate 5',
            'Devotion': 'Gate 6',
            'Recognition': 'Gate 9'
        }
        return gate_mapping.get(glyph.category or 'Complex', 'Gate 5')
    
    def save_glyph_to_database(self, glyph: GlyphObject) -> bool:
        """Save glyph to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            gate = self.assign_gate(glyph)
            
            cursor.execute("""
                INSERT INTO glyph_lexicon (voltage_pair, glyph_name, description, gate, activation_signals)
                VALUES (?, ?, ?, ?, ?)
            """, (
                glyph.voltage_pair,
                glyph.name,
                glyph.description,
                gate,
                ','.join(glyph.activation_signals)
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Saved glyph '{glyph.name}' to database ({gate})")
            return True
            
        except Exception as e:
            logger.error(f"Error saving glyph to database: {e}")
            return False
    
    def process_single_file(self, file_path: Path) -> int:
        """Process a single file and return number of glyphs extracted"""
        logger.info(f"Processing: {file_path.name}")
        
        text = self.extract_text_content(file_path)
        if not text or len(text) < 100:
            logger.warning(f"Insufficient content in {file_path.name}")
            return 0
        
        # Find potential glyph blocks
        blocks = self.find_potential_glyphs(text)
        
        if not blocks:
            # If no blocks found, try treating entire text as one glyph
            glyph = self.parse_glyph_from_block(text, file_path.name)
            if glyph and self.save_glyph_to_database(glyph):
                return 1
            return 0
        
        # Process each block
        saved_count = 0
        for block in blocks:
            glyph = self.parse_glyph_from_block(block, file_path.name)
            if glyph and self.save_glyph_to_database(glyph):
                saved_count += 1
        
        return saved_count
    
    def process_all_files(self) -> dict:
        """Process all files in unprocessed_glyphs"""
        logger.info("🔮 Starting simple ritual capsule processing...")
        
        stats = {
            'files_found': 0,
            'glyphs_saved': 0,
            'files_processed': 0,
            'errors': 0
        }
        
        # Find .docx files
        docx_files = list(self.unprocessed_dir.glob("*.docx"))
        stats['files_found'] = len(docx_files)
        
        if not docx_files:
            logger.info("No .docx files found")
            return stats
        
        # Process each file
        for file_path in docx_files:
            try:
                glyphs_count = self.process_single_file(file_path)
                stats['glyphs_saved'] += glyphs_count
                
                if glyphs_count > 0:
                    # Move to processed
                    destination = self.processed_dir / file_path.name
                    file_path.rename(destination)
                    stats['files_processed'] += 1
                    logger.info(f"Moved {file_path.name} to processed ({glyphs_count} glyphs)")
                else:
                    logger.warning(f"No glyphs extracted from {file_path.name}")
                    stats['errors'] += 1
                    
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                stats['errors'] += 1
        
        logger.info(f"✨ Processing complete: {stats['glyphs_saved']} glyphs from {stats['files_processed']} files")
        return stats

def main():
    """Run simple ritual processor"""
    processor = SimpleRitualProcessor()
    results = processor.process_all_files()
    
    print("🔮 SIMPLE RITUAL PROCESSING RESULTS:")
    print(f"   Files found: {results['files_found']}")
    print(f"   Glyphs saved: {results['glyphs_saved']}")
    print(f"   Files processed: {results['files_processed']}")
    print(f"   Errors: {results['errors']}")

if __name__ == "__main__":
    main()
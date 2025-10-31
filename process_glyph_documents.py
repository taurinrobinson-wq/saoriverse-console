#!/usr/bin/env python3
"""
Document Processor for Unprocessed Glyphs
-----------------------------------------
Processes Word documents in unprocessed_glyphs/ to extract glyph information
and integrate it into the emotional OS database.
"""

import os
import json
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import re

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    print("python-docx not available. Install with: pip install python-docx")
    DOCX_AVAILABLE = False

class GlyphDocumentProcessor:
    def __init__(self, 
                 unprocessed_dir="emotional_os/deploy/unprocessed_glyphs",
                 processed_dir="emotional_os/deploy/processed_glyphs", 
                 db_path="emotional_os/glyphs/glyphs.db"):
        self.unprocessed_dir = Path(unprocessed_dir)
        self.processed_dir = Path(processed_dir)
        self.db_path = Path(db_path)
        
        # Ensure directories exist
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
    def process_all_documents(self):
        """Process all unprocessed documents"""
        if not DOCX_AVAILABLE:
            print("Cannot process documents: python-docx not available")
            return
            
        processed_count = 0
        for doc_file in self.unprocessed_dir.glob("*.docx"):
            if doc_file.name.startswith("~$"):  # Skip temp files
                continue
                
            print(f"Processing: {doc_file.name}")
            try:
                glyphs = self.extract_glyphs_from_document(doc_file)
                if glyphs:
                    self.add_glyphs_to_database(glyphs, doc_file.name)
                    self.move_to_processed(doc_file)
                    processed_count += 1
                    print(f"  ✅ Extracted {len(glyphs)} glyphs")
                else:
                    print(f"  ⚠️ No glyphs found")
            except Exception as e:
                print(f"  ❌ Error processing {doc_file.name}: {e}")
                
        print(f"\nProcessed {processed_count} documents")
        
    def extract_glyphs_from_document(self, doc_path: Path) -> List[Dict[str, Any]]:
        """Extract glyph information from a Word document"""
        doc = Document(doc_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        
        glyphs = []
        
        # Look for glyph patterns in the text
        glyph_patterns = [
            # Pattern: "Glyph Name: Description"
            r"([A-Z][a-zA-Z\s]+):\s*([^\n]{20,200})",
            # Pattern: "## Glyph Name" followed by description
            r"##\s*([A-Z][a-zA-Z\s]+)\n([^\n#]{20,200})",
            # Pattern: Bold glyph names (approximated)
            r"\*\*([A-Z][a-zA-Z\s]+)\*\*[:\s]*([^\n*]{20,200})",
        ]
        
        for pattern in glyph_patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            for name, description in matches:
                name = name.strip()
                description = description.strip()
                
                # Skip if too generic or short
                if len(name) < 5 or len(description) < 20:
                    continue
                    
                # Determine gate based on content analysis
                gate = self.determine_gate(description)
                
                glyphs.append({
                    "glyph_name": name,
                    "description": description,
                    "gate": gate,
                    "activation_signals": self.extract_signals(description),
                    "source_document": doc_path.name,
                    "extracted_at": datetime.now().isoformat()
                })
                
        return glyphs
        
    def determine_gate(self, description: str) -> str:
        """Determine which gate a glyph belongs to based on its description"""
        desc_lower = description.lower()
        
        # Gate patterns based on emotional themes
        if any(word in desc_lower for word in ["boundary", "contain", "protect", "shield", "structure"]):
            return "Gate 2"
        elif any(word in desc_lower for word in ["grief", "mourning", "loss", "sorrow", "ache"]):
            return "Gate 4"  
        elif any(word in desc_lower for word in ["joy", "celebration", "bliss", "delight", "fulfillment"]):
            return "Gate 5"
        elif any(word in desc_lower for word in ["devotion", "sacred", "vow", "offering", "prayer"]):
            return "Gate 6"
        elif any(word in desc_lower for word in ["recognition", "seen", "witness", "mirror", "acknowledge"]):
            return "Gate 9"
        elif any(word in desc_lower for word in ["ceremony", "ritual", "sacred", "collapse"]):
            return "Gate 10"
        else:
            return "Gate 5"  # Default
            
    def extract_signals(self, description: str) -> str:
        """Extract activation signals from description"""
        desc_lower = description.lower()
        signals = []
        
        # Map emotional content to signals
        signal_map = {
            "α": ["devotion", "vow", "sacred", "offering", "prayer"],
            "β": ["boundary", "contain", "protect", "structure", "shield"],
            "γ": ["longing", "yearning", "ache", "desire", "want"],
            "δ": ["stillness", "quiet", "pause", "rest", "calm"],
            "ε": ["insight", "clarity", "understanding", "revelation", "truth"],
            "λ": ["joy", "celebration", "delight", "fulfillment", "bliss"],
            "θ": ["grief", "mourning", "loss", "sorrow", "sadness"],
            "Ω": ["recognition", "seen", "witness", "acknowledge", "mirror"]
        }
        
        for signal, keywords in signal_map.items():
            if any(word in desc_lower for word in keywords):
                signals.append(signal)
                
        return ", ".join(signals) if signals else "ε"  # Default to insight
        
    def add_glyphs_to_database(self, glyphs: List[Dict[str, Any]], source_file: str):
        """Add extracted glyphs to the SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for glyph in glyphs:
            try:
                cursor.execute("""
                    INSERT INTO glyph_lexicon (voltage_pair, glyph_name, description, gate, activation_signals)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    f"extracted_{glyph['glyph_name'].lower().replace(' ', '_')}",
                    glyph["glyph_name"],
                    glyph["description"],
                    glyph["gate"], 
                    glyph["activation_signals"]
                ))
            except sqlite3.IntegrityError:
                # Glyph might already exist, skip
                continue
                
        conn.commit()
        conn.close()
        
    def move_to_processed(self, doc_path: Path):
        """Move processed document to processed folder"""
        dest_path = self.processed_dir / doc_path.name
        shutil.move(str(doc_path), str(dest_path))

def main():
    """Main processing function"""
    processor = GlyphDocumentProcessor()
    
    print("🔮 Starting Glyph Document Processing...")
    print(f"📁 Unprocessed: {processor.unprocessed_dir}")
    print(f"📁 Processed: {processor.processed_dir}")
    print(f"🗄️ Database: {processor.db_path}")
    print()
    
    processor.process_all_documents()
    print("\n✨ Processing complete!")

if __name__ == "__main__":
    main()
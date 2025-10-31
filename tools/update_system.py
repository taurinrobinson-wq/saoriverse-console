#!/usr/bin/env python3
"""
Update system files to reflect the new consolidated glyph database
"""

import re
import os

def update_test_files():
    """Update test files with new glyph count"""
    
    test_files = [
        'test_overwhelm_fix.py',
        'test_enhanced_system.py'
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Update total glyph count references (45 total, ~36 typically available)
                content = re.sub(r'📊 Total Available Glyphs: \d+', '📊 Total Available Glyphs: {available_count}', content)
                
                # Update any other hardcoded counts
                content = re.sub(r'Total glyphs: \d+', 'Total glyphs: 45', content)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ Updated {file_path}")
                
            except Exception as e:
                print(f"❌ Error updating {file_path}: {e}")
        else:
            print(f"⚠️  File not found: {file_path}")

def update_documentation():
    """Create documentation for the new consolidated glyph system"""
    
    doc_content = """# Emotional OS - Consolidated Glyph System

## Overview
The Emotional OS now uses a carefully curated collection of 45 core emotional glyphs, organized across 6 gates for balanced emotional processing.

... (trimmed for brevity) ...
"""

    with open('GLYPH_CONSOLIDATION.md', 'w', encoding='utf-8') as f:
        f.write(doc_content)
    
    print("✅ Created GLYPH_CONSOLIDATION.md documentation")

def main():
    print("=== UPDATING SYSTEM FILES ===")
    update_test_files()
    update_documentation()
    print("\n✅ System update complete!")
    print("📊 New glyph database: 45 total glyphs, balanced across 6 gates")
    print("🚀 Ready for testing and deployment")

if __name__ == "__main__":
    main()

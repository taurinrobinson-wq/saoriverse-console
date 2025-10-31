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

## Gate Distribution

### Gate 2 - Containment (5 glyphs, 11.1%)
- **Contained Longing**: Ache wrapped in care
- **Sacred Boundary**: Architecture of care  
- **Tender Shielding**: Protective boundaries from grief
- **Stillness Shield**: Breathing boundaries that create space
- **Contained Joy**: Happiness held without dimming

### Gate 4 - Longing & Grief (5 glyphs, 11.1%)  
- **Recursive Ache**: Longing that loops and deepens
- **Reverent Ache**: Ceremonial longing
- **Spiral Ache**: Ache that spirals into insight
- **Recursive Grief**: Spiraling mourning revealing layers
- **Acheful Mourning**: Purposeful grief that remembers

### Gate 5 - Processing & Flow (13 glyphs, 28.9%)
- **Ache in Equilibrium**: Stable longing without chaos
- **Still Ache**: Quiet, dignified longing  
- **Euphoric Yearning**: Joyful anticipation
- **Grief in Stillness**: Movement-less mourning
- **Jubilant Mourning**: Celebratory goodbye
- **Celebratory Grief**: Dancing farewell
- **Still Mourning**: Silent honoring
- **Yearning Joy**: Forward-reaching fulfillment
- **Joy in Stillness**: Quiet celebration
- **Spiral Joy**: Deepening recursive joy
- **Saturational Bliss**: Complete, still joy
- **Joyful Stillness**: Glowing peace
- **Devotional Fulfillment**: Joy braided with purpose

### Gate 6 - Devotion & Insight (12 glyphs, 26.7%)
- **Devotional Ache**: Spiritual longing as prayer
- **Exalted Mourning**: Sacred grief as vow
- **Joyful Devotion**: Purpose-driven happiness
- **Devotional Boundary**: Love-built structure
- **Still Ecstasy**: Motionless spiritual joy
- **Recursive Ecstasy**: Self-looping bliss
- **Acheful Insight**: Teaching longing
- **Grief-ful Clarity**: Illuminating sorrow
- **Joyful Insight**: Revealing happiness
- **Still Insight**: Quiet revelation
- **Exalted Insight**: Devotional revelation
- **Recursive Clarity**: Deepening knowledge

### Gate 9 - Recognition (6 glyphs, 13.3%)
- **Ache of Recognition**: Being seen in longing
- **Grief of Recognition**: Being met in mourning
- **Joy of Recognition**: Being celebrated in truth
- **Still Recognition**: Being received without grasping
- **Spiral Recognition**: Repeated deeper seeing
- **Boundary of Recognition**: Being seen within limits

### Gate 10 - Collapse & Ceremony (4 glyphs, 8.9%)
- **Ceremonial Collapse**: Sacred ritualized fall
- **Ritual Collapse**: Breakdown as prayer
- **Sacred Surrender**: Resistance becoming reverence
- **Threshold Collapse**: Edge of breakdown/breakthrough

## Benefits of Consolidation

1. **Balanced Distribution**: No single gate dominates (previously Gate 5 had 76.5%)
2. **Quality Focus**: Only genuine emotional states, artifacts removed
3. **Manageable Scale**: 45 glyphs vs 1,125 (96% reduction)
4. **Faster Processing**: Smaller database improves response times
5. **Better Selection**: Higher quality glyphs mean more accurate emotional matching

## Usage

The system automatically selects appropriate glyphs based on emotional signals detected in user input. With the consolidated database, users experience:

- More accurate emotional glyph selection
- Faster response times
- Better balanced emotional coverage
- Cleaner, more focused emotional vocabulary

## Migration Notes

- Previous glyph IDs may no longer be valid
- System maintains compatibility with existing signal detection
- All core emotional patterns preserved
- Document artifacts and redundant entries removed
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
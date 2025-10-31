#!/usr/bin/env python3
"""
Aggressive Glyph Consolidation - Target 200-300 core emotional glyphs
"""

import sqlite3
import json
import re
from collections import defaultdict, Counter

def aggressive_consolidation():
    conn = sqlite3.connect('emotional_os/glyphs/glyphs.db')
    cursor = conn.cursor()
    
    print("=== AGGRESSIVE GLYPH CONSOLIDATION ===")
    
    # Get current glyphs
    cursor.execute("SELECT id, glyph_name, description, gate FROM glyph_lexicon")
    all_glyphs = cursor.fetchall()
    print(f"Current count: {len(all_glyphs)}")
    
    # Target: ~250 high-quality emotional glyphs
    target_count = 250
    target_per_gate = target_count // 6  # ~42 per gate
    
    print(f"Target: {target_count} total glyphs (~{target_per_gate} per gate)")
    
    # Step 1: Identify core emotional categories
    core_emotions = {
        'ache', 'longing', 'yearning',  # Longing family
        'grief', 'mourning', 'sorrow',  # Grief family  
        'joy', 'bliss', 'ecstasy',      # Joy family
        'stillness', 'silence', 'quiet', # Stillness family
        'recognition', 'witness', 'seen', # Recognition family
        'devotion', 'sacred', 'reverent', # Devotion family
        'boundary', 'containment', 'shield', # Boundary family
        'spiral', 'recursive', 'loop',   # Process family
        'tender', 'gentle', 'soft',     # Tenderness family
        'clarity', 'insight', 'knowing' # Clarity family
    }
    
    # Step 2: Quality filter - keep only well-formed emotional glyphs
    quality_glyphs = []
    removed_count = 0
    
    for glyph in all_glyphs:
        id, name, desc, gate = glyph
        
        # Quality criteria
        is_quality = all([
            # Name length reasonable (emotional states, not sentences)
            3 <= len(name.split()) <= 4,
            # Description is substantial but not excessive
            50 <= len(desc) <= 300,
            # Contains core emotional vocabulary
            any(emotion in name.lower() for emotion in core_emotions) or
            any(emotion in desc.lower() for emotion in core_emotions),
            # Not obviously technical/system content
            not any(tech in name.lower() for tech in 
                   ['protocol', 'system', 'processing', 'configuration', 'api', 'deployment']),
            # Not conversation fragments
            not re.search(r"^(I |You |We |It |This |That |The [a-z]+ is)", name),
            # Has proper emotional description pattern
            bool(re.search(r'(that|which|who)\s+(is|are|becomes|flows)', desc.lower())) or
            bool(re.search(r'(joy|grief|ache|longing|stillness|recognition)', desc.lower()))
        ])
        
        if is_quality:
            quality_glyphs.append(glyph)
        else:
            removed_count += 1
    
    print(f"Quality filter: kept {len(quality_glyphs)}, removed {removed_count}")
    
    # Step 3: Balance gates - select best from each gate
    final_glyphs = []
    glyphs_by_gate = defaultdict(list)
    
    for glyph in quality_glyphs:
        glyphs_by_gate[glyph[3]].append(glyph)
    
    for gate, gate_glyphs in glyphs_by_gate.items():
        print(f"\n{gate}: {len(gate_glyphs)} quality glyphs")
        
        # Sort by emotional resonance (prioritize core emotions)
        def emotion_score(glyph):
            id, name, desc, gate = glyph
            score = 0
            name_lower = name.lower()
            desc_lower = desc.lower()
            
            # Core emotional words get high scores
            for emotion in ['ache', 'grief', 'joy', 'longing', 'stillness']:
                if emotion in name_lower:
                    score += 10
                if emotion in desc_lower:
                    score += 5
            
            # Variety bonus (less common emotions)
            rare_emotions = ['ecstasy', 'reverence', 'tenderness', 'clarity', 'recognition']
            for emotion in rare_emotions:
                if emotion in name_lower:
                    score += 8
            
            # Penalize overly complex names
            if len(name.split()) > 3:
                score -= 2
                
            return score
        
        gate_glyphs.sort(key=emotion_score, reverse=True)
        
        # Take top glyphs from each gate (balanced distribution)
        target_for_gate = min(target_per_gate, len(gate_glyphs))
        selected = gate_glyphs[:target_for_gate]
        final_glyphs.extend(selected)
        
        print(f"  Selected top {len(selected)} glyphs")
        for glyph in selected[:5]:  # Show first 5
            print(f"    {glyph[1]}")
        if len(selected) > 5:
            print(f"    ... and {len(selected) - 5} more")
    
    # Step 4: Execute consolidation
    print(f"\n=== EXECUTING CONSOLIDATION ===")
    print(f"Final selection: {len(final_glyphs)} glyphs")
    
    # Get IDs to keep
    keep_ids = [glyph[0] for glyph in final_glyphs]
    
    # Remove all others
    if len(keep_ids) > 0:
        keep_placeholders = ','.join(['?' for _ in keep_ids])
        cursor.execute(f"DELETE FROM glyph_lexicon WHERE id NOT IN ({keep_placeholders})", keep_ids)
        conn.commit()
    
    # Verify results
    cursor.execute("SELECT COUNT(*) FROM glyph_lexicon")
    final_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT gate, COUNT(*) FROM glyph_lexicon GROUP BY gate ORDER BY gate")
    final_distribution = cursor.fetchall()
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"Total glyphs: {final_count}")
    print("Gate distribution:")
    for gate, count in final_distribution:
        percentage = (count / final_count) * 100
        print(f"  {gate}: {count} glyphs ({percentage:.1f}%)")
    
    print(f"\nReduction: {len(all_glyphs)} → {final_count} ({((len(all_glyphs) - final_count) / len(all_glyphs) * 100):.1f}% reduction)")
    
    conn.close()
    return final_count

if __name__ == "__main__":
    aggressive_consolidation()
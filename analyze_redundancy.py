#!/usr/bin/env python3
"""
Detailed glyph redundancy analysis for consolidation
"""

import sqlite3
import re
from collections import defaultdict, Counter
from difflib import SequenceMatcher

def similarity(a, b):
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def analyze_redundancy():
    conn = sqlite3.connect('emotional_os/glyphs/glyphs.db')
    cursor = conn.cursor()
    
    # Get all glyphs
    cursor.execute("SELECT id, glyph_name, description, gate FROM glyph_lexicon")
    glyphs = cursor.fetchall()
    
    print(f"=== GLYPH REDUNDANCY ANALYSIS ===")
    print(f"Total glyphs: {len(glyphs)}")
    
    # Analyze by keywords in names
    keyword_groups = defaultdict(list)
    for glyph in glyphs:
        id, name, desc, gate = glyph
        # Extract key emotional words
        words = name.lower().split()
        for word in words:
            if word in ['ache', 'grief', 'mourning', 'joy', 'yearning', 'longing', 
                       'stillness', 'recognition', 'devotion', 'spiral', 'recursive',
                       'contained', 'boundary', 'ecstasy', 'bliss', 'tender', 'reverent']:
                keyword_groups[word].append((id, name, gate, desc[:50] + "..."))
    
    print(f"\n=== KEYWORD FREQUENCY ANALYSIS ===")
    for keyword, group in sorted(keyword_groups.items(), key=lambda x: len(x[1]), reverse=True):
        if len(group) > 5:  # Only show keywords with many instances
            print(f"\n{keyword.upper()}: {len(group)} glyphs")
            gate_counts = Counter([g[2] for g in group])
            print(f"  Gate distribution: {dict(gate_counts)}")
            
            # Show a few examples
            for i, (id, name, gate, desc) in enumerate(group[:3]):
                print(f"    {name} ({gate}): {desc}")
            if len(group) > 3:
                print(f"    ... and {len(group) - 3} more")
    
    # Find similar names
    print(f"\n=== SIMILAR GLYPH NAMES (>80% similarity) ===")
    similar_pairs = []
    for i, glyph1 in enumerate(glyphs):
        for j, glyph2 in enumerate(glyphs[i+1:], i+1):
            id1, name1, desc1, gate1 = glyph1
            id2, name2, desc2, gate2 = glyph2
            
            sim = similarity(name1, name2)
            if sim > 0.8 and name1 != name2:
                similar_pairs.append((sim, name1, gate1, name2, gate2, desc1[:40], desc2[:40]))
    
    # Sort by similarity
    similar_pairs.sort(reverse=True)
    for sim, name1, gate1, name2, gate2, desc1, desc2 in similar_pairs[:20]:
        print(f"  {sim:.2f}: '{name1}' ({gate1}) vs '{name2}' ({gate2})")
        print(f"       {desc1}... vs {desc2}...")
    
    # Gate distribution analysis
    print(f"\n=== GATE DISTRIBUTION IMBALANCE ===")
    gate_counts = Counter([g[3] for g in glyphs])
    for gate, count in sorted(gate_counts.items()):
        percentage = (count / len(glyphs)) * 100
        print(f"  {gate}: {count} glyphs ({percentage:.1f}%)")
    
    # Find potential consolidation candidates
    print(f"\n=== CONSOLIDATION CANDIDATES ===")
    
    # Group by similar themes and same gate
    consolidation_groups = defaultdict(list)
    for glyph in glyphs:
        id, name, desc, gate = glyph
        # Create a key based on main theme + gate
        name_lower = name.lower()
        if 'ache' in name_lower and 'grief' in name_lower:
            key = f"{gate}_ache_grief"
        elif 'joy' in name_lower and 'stillness' in name_lower:
            key = f"{gate}_joy_stillness"  
        elif 'recognition' in name_lower:
            key = f"{gate}_recognition"
        elif 'mourning' in name_lower:
            key = f"{gate}_mourning"
        elif 'recursive' in name_lower:
            key = f"{gate}_recursive"
        elif 'devotional' in name_lower or 'devotion' in name_lower:
            key = f"{gate}_devotion"
        else:
            continue
            
        consolidation_groups[key].append((id, name, desc[:60] + "..."))
    
    for key, group in consolidation_groups.items():
        if len(group) > 2:  # Groups with 3+ similar glyphs
            gate, theme = key.split('_', 1)
            print(f"\n{theme.upper()} in {gate}: {len(group)} candidates")
            for id, name, desc in group:
                print(f"    {name}: {desc}")
    
    conn.close()

if __name__ == "__main__":
    analyze_redundancy()
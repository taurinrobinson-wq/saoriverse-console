#!/usr/bin/env python3
"""
Analyze glyph database for redundancy and consolidation opportunities
"""

import sqlite3
import json
from collections import defaultdict

def analyze_database():
    conn = sqlite3.connect('emotional_os/glyphs/glyphs.db')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Available tables:")
    for table in tables:
        print(f"  {table[0]}")
    
    if not tables:
        print("No tables found in database!")
        return
    
    # Use the first table found
    table_name = tables[0][0]
    print(f"\nAnalyzing table: {table_name}")
    
    # Get table structure
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print(f"\nColumns in {table_name}:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Get all glyphs
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    column_names = [col[1] for col in columns]
    print(f"\nTotal glyphs: {len(rows)}")
    
    # Analyze by gate if gate column exists
    if 'gate' in column_names:
        gate_idx = column_names.index('gate')
        gate_counts = defaultdict(int)
        for row in rows:
            gate_counts[row[gate_idx]] += 1
        
        print("\nGlyphs per gate:")
        for gate in sorted(gate_counts.keys()):
            print(f"  {gate}: {gate_counts[gate]}")
    
    # Look for similar glyph names
    if 'glyph_name' in column_names:
        name_idx = column_names.index('glyph_name')
        desc_idx = column_names.index('description') if 'description' in column_names else None
        
        print(f"\nFirst 20 glyphs:")
        for i, row in enumerate(rows[:20]):
            name = row[name_idx]
            desc = row[desc_idx][:100] + "..." if desc_idx and len(row[desc_idx]) > 100 else (row[desc_idx] if desc_idx else "No description")
            gate = row[gate_idx] if 'gate' in column_names else "No gate"
            print(f"  {name} ({gate}): {desc}")
    
    conn.close()

if __name__ == "__main__":
    analyze_database()
#!/usr/bin/env python3
"""Check database table structure"""

import sqlite3

def check_tables():
    conn = sqlite3.connect('emotional_os/glyphs/glyphs.db')
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("📋 Available tables:", [t[0] for t in tables])
    
    # Check each table structure
    for table_name in [t[0] for t in tables]:
        print(f"\n🏗️ Structure of {table_name}:")
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  • {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == "__main__":
    check_tables()
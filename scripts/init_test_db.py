#!/usr/bin/env python3
"""
Create a local test SQLite database at emotional_os/glyphs/glyphs.db with minimal
schema and some sample rows so integration tests run deterministically in CI/local.
"""
import os
import sqlite3

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "emotional_os", "glyphs")
DB_DIR = os.path.abspath(DB_DIR)
DB_PATH = os.path.join(DB_DIR, "glyphs.db")

os.makedirs(DB_DIR, exist_ok=True)
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# glyph_lexicon table used by fetch_glyphs and learners
cur.execute(
    """
CREATE TABLE IF NOT EXISTS glyph_lexicon (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    glyph_name TEXT NOT NULL,
    description TEXT,
    gate TEXT
)
"""
)

# glyph_versions etc. used by shared manager
cur.execute(
    """
CREATE TABLE IF NOT EXISTS glyph_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    glyph_name TEXT NOT NULL,
    version_num INTEGER DEFAULT 1,
    description TEXT,
    emotional_signal TEXT,
    gates TEXT,
    created_at TEXT,
    created_by TEXT,
    adoption_count INTEGER DEFAULT 0,
    quality_score REAL DEFAULT 0.5,
    is_active INTEGER DEFAULT 1
)
"""
)

cur.execute(
    """
CREATE TABLE IF NOT EXISTS glyph_consensus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    glyph_name TEXT UNIQUE NOT NULL,
    total_users_adopted INTEGER DEFAULT 0,
    positive_feedback_count INTEGER DEFAULT 0,
    negative_feedback_count INTEGER DEFAULT 0,
    consensus_strength REAL DEFAULT 0.0
)
"""
)

cur.execute(
    """
CREATE TABLE IF NOT EXISTS glyph_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    glyph_name TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    emotional_signal TEXT,
    gates TEXT,
    source_input TEXT,
    created_by TEXT,
    created_at TEXT,
    confidence_score REAL,
    validation_status TEXT DEFAULT 'pending'
)
"""
)

# Insert a few sample shared glyphs
sample_rows = [
    ("Still Recognition", "Being seen without reaction. A gaze that receives.", "Gate 5"),
    ("Still Insight", "Quiet revelation and noticing", "Gate 5"),
    ("Containment Shield", "Creates boundary", "Gate 5"),
    ("Spiral Containment", "Recursive ache that cycles", "Gate 2"),
    ("Overwhelmed", "A sense of being swamped by change", "Gate 4"),
]

# Avoid duplicate inserts
for name, desc, gate in sample_rows:
    cur.execute("SELECT 1 FROM glyph_lexicon WHERE glyph_name = ?", (name,))
    if cur.fetchone() is None:
        cur.execute("INSERT INTO glyph_lexicon (glyph_name, description, gate) VALUES (?, ?, ?)", (name, desc, gate))

conn.commit()
conn.close()
print(f"Created/updated test DB at: {DB_PATH}")

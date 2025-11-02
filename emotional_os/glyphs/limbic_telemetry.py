#!/usr/bin/env python3
# Simple telemetry storage for limbic demo events
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List

DB_PATH = os.path.join(os.path.dirname(__file__), 'telemetry.db')

CREATE_TABLE_SQL = '''
CREATE TABLE IF NOT EXISTS limbic_events (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    user_id TEXT,
    input_text TEXT,
    emotion TEXT,
    enrichment_applied INTEGER,
    ab_group TEXT,
    latency_ms REAL,
    glyphs_generated INTEGER,
    safety_flag INTEGER
)
'''


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(CREATE_TABLE_SQL)
    conn.commit()
    conn.close()


def record_event(event: Dict[str, Any]):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO limbic_events (timestamp, user_id, input_text, emotion, enrichment_applied, ab_group, latency_ms, glyphs_generated, safety_flag)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            event.get('timestamp', datetime.utcnow().isoformat()),
            event.get('user_id', 'unknown'),
            event.get('input_text', ''),
            event.get('emotion', ''),
            1 if event.get('enrichment_applied') else 0,
            event.get('ab_group', ''),
            event.get('latency_ms', 0.0),
            event.get('glyphs_generated', 0),
            1 if event.get('safety_flag') else 0,
        )
    )
    conn.commit()
    conn.close()


def fetch_recent(n: int = 20) -> List[Dict[str, Any]]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp, user_id, input_text, emotion, enrichment_applied, ab_group, latency_ms, glyphs_generated, safety_flag FROM limbic_events ORDER BY id DESC LIMIT ?', (n,))
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            'timestamp': r[0],
            'user_id': r[1],
            'input_text': r[2],
            'emotion': r[3],
            'enrichment_applied': bool(r[4]),
            'ab_group': r[5],
            'latency_ms': r[6],
            'glyphs_generated': r[7],
            'safety_flag': bool(r[8])
        })
    return result

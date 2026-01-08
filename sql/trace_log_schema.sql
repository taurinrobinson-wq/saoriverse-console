CREATE TABLE IF NOT EXISTS trace_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,
  input TEXT NOT NULL,
  signals TEXT,            -- Comma-separated control signals (e.g. "β, γ")
  gates TEXT,              -- Comma-separated activated gates (e.g. "Gate 2, Gate 4")
  glyphs TEXT,             -- Comma-separated activated glyph names
  ritual_prompt TEXT       -- Optional prompt for journaling or invocation
);
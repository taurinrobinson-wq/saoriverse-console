-- Staging table for salvaged glyphs imported from backups or exports
-- This table is intentionally minimal and separate from the canonical
-- `glyph_lexicon` so we can review and reconcile entries before merging.

CREATE TABLE IF NOT EXISTS glyph_lexicon_salvaged (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    glyph_name TEXT NOT NULL,
    description TEXT,
    gate TEXT,
    source_file TEXT,
    imported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    raw_payload TEXT
);

-- Index to help reconciliation queries by glyph_name
CREATE INDEX IF NOT EXISTS idx_glyph_salvaged_name ON glyph_lexicon_salvaged(glyph_name);

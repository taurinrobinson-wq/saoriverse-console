import csv
import json
from collections import Counter

CSV_PATH = "dev_tools/simulate_output.csv"


def safe_get(row, keys):
    for k in keys:
        if k in row:
            return row[k]
    return ""


with open(CSV_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

total = len(rows)
resp_counter = Counter()
matched = 0
glyph_counter = Counter()
debug_sql_count = 0
debug_glyph_rows_count = 0

for r in rows:
    resp = safe_get(r, ["response_source", "responseSource", "response source"]) or ""
    resp_counter[resp] += 1
    best = safe_get(r, ["best_glyph", "bestGlyph", "best glyph"]) or ""
    if best and best.strip().lower() not in ("none", "null", ""):
        matched += 1
        glyph_counter[best.strip()] += 1
    debug_sql = safe_get(r, ["debug_sql", "debugSql", "debug sql"]) or ""
    if debug_sql.strip():
        debug_sql_count += 1
    debug_glyph_rows = safe_get(r, ["debug_glyph_rows", "debugGlyphRows", "debug glyph rows"]) or ""
    if debug_glyph_rows.strip():
        debug_glyph_rows_count += 1

metrics = {
    "total_rows": total,
    "response_source_counts": dict(resp_counter),
    "matched_glyphs": matched,
    "match_rate_pct": round((matched / total * 100) if total else 0, 2),
    "top_glyphs": glyph_counter.most_common(10),
    "debug_sql_count": debug_sql_count,
    "debug_glyph_rows_count": debug_glyph_rows_count,
}

print(json.dumps(metrics, indent=2, ensure_ascii=False))

# also write to a file for later inspection
with open("dev_tools/simulate_metrics_after_runtime_filter.json", "w", encoding="utf-8") as of:
    json.dump(metrics, of, ensure_ascii=False, indent=2)

print("\nWrote dev_tools/simulate_metrics_after_runtime_filter.json")

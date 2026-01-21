import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIG = ROOT / 'Glyph_Organizer.json'
BACKUP = ROOT / 'Glyph_Organizer.json.bak'

print(f"Loading {ORIG}")
with ORIG.open('r', encoding='utf-8') as f:
    data = json.load(f)

# Backup
with BACKUP.open('w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"Backup written to {BACKUP}")

# Function to recursively remove any string items containing '/full-color_glyphs/'
def sanitize(obj):
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        new_list = []
        for item in obj:
            if isinstance(item, str) and '/full-color_glyphs/' in item:
                # skip full-color glyph references
                continue
            new_list.append(sanitize(item))
        return new_list
    return obj

cleaned = sanitize(data)

with ORIG.open('w', encoding='utf-8') as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)

print(f"Sanitized file written to {ORIG}")

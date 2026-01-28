import json
import re
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
INPUT = os.path.join(ROOT, 'sod_pages.json')
OUT_DIR = os.path.join(ROOT, 'sod_sections')

with open(INPUT, 'r', encoding='utf-8') as f:
    pages = json.load(f)

# Build full text with page markers
parts = []
for p in pages:
    parts.append('\n\n===PAGE:%d===\n' % p.get('page'))
    parts.append(p.get('text',''))
full = ''.join(parts)

# Regex for top-level section headers like "I. INTRODUCTION" or "IV. PLAINTIFFS' CLAIMS"
header_re = re.compile(r"\n([IVXLCDM]+)\.\s+([^\n]{1,120})\n")

matches = list(header_re.finditer(full))

if not matches:
    print('No section headers found; aborting.')
    raise SystemExit(1)

os.makedirs(OUT_DIR, exist_ok=True)
sections = []
for i, m in enumerate(matches):
    start = m.start()
    end = matches[i+1].start() if i+1 < len(matches) else len(full)
    rom = m.group(1)
    title = m.group(2).strip()
    body = full[start:end].strip()
    # Find pages included
    pages_in = sorted(set(int(x) for x in re.findall(r'===PAGE:(\d+)===', body)))
    sec_obj = {
        'roman': rom,
        'title': title,
        'pages': pages_in,
        'text': body
    }
    # safe filename
    safe = re.sub(r'[^A-Za-z0-9]+', '_', title).strip('_')[:60]
    filename = f"{i+1:02d}_{rom}_{safe}.json"
    out_path = os.path.join(OUT_DIR, filename)
    with open(out_path, 'w', encoding='utf-8') as out:
        json.dump(sec_obj, out, indent=2, ensure_ascii=False)
    sections.append({'index': i+1, 'roman': rom, 'title': title, 'pages': pages_in, 'file': os.path.relpath(out_path, ROOT)})

# write index
index_path = os.path.join(OUT_DIR, 'index.json')
with open(index_path, 'w', encoding='utf-8') as idxf:
    json.dump({'sections': sections}, idxf, indent=2, ensure_ascii=False)

print(f'WROTE {len(sections)} section files to {OUT_DIR} and index.json')

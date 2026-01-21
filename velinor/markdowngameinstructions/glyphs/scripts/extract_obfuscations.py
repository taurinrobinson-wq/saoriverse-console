import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / 'cipher_seeds.csv'
OUT = ROOT / 'cipher_obfuscations.txt'

with CSV.open('r', encoding='utf-8') as f, OUT.open('w', encoding='utf-8') as o:
    reader = csv.DictReader(f)
    for row in reader:
        val = row.get('first_view_obfuscation_numeric') or row.get('first_view_obfuscation')
        if val:
            o.write(val + '\n')
print(f'Wrote {OUT}')

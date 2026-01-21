from pathlib import Path
p=Path(__file__).resolve().parents[1]/'cipher_obfuscations.txt'
lines=[l for l in p.read_text(encoding='utf-8').splitlines() if l.strip()]
print(len(lines))

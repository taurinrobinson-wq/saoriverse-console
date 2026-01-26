from pathlib import Path
candidates = [Path('velinor/data/FluidR3_GM.sf2'), Path('Offshoots/ToneCore/sf2/FluidR3_GM.sf2')]
for p in candidates:
    if p.exists():
        with p.open('rb') as f:
            header = f.read(12)
        riff = header[0:4].decode('ascii', errors='replace')
        sfbk = header[8:12].decode('ascii', errors='replace')
        print(f"{p} -> riff='{riff}' sfbk='{sfbk}' size={p.stat().st_size}")
    else:
        print(f"{p} -> MISSING")

import pdfplumber
from pathlib import Path

plaintiffs_to_check = [
    'Robert Tavares',
    'Teresa Whetstone', 
    'Vonda Webb',
    'Thomas Stewart'
]

with pdfplumber.open('Law/JustSettlementStatements.pdf') as pdf:
    text = '\n\n'.join([page.extract_text() for page in pdf.pages])

for plaintiff in plaintiffs_to_check:
    idx = text.find(plaintiff)
    if idx >= 0:
        # Find next case anchor
        next_idx = text.find('This Document Relates to Plaintiff:', idx + 1)
        if next_idx < 0:
            next_idx = len(text)
        
        section = text[idx:next_idx]
        
        # Search for "Open" in damages section (usually near end)
        # Look for the damages/values section
        damages_idx = section.find('following values represent')
        if damages_idx >= 0:
            damages_section = section[damages_idx:damages_idx+1500]
            print(f"\n{'='*80}")
            print(f"{plaintiff}")
            print(f"{'='*80}")
            print(damages_section)
        else:
            print(f"\n{plaintiff}: No damages section found")

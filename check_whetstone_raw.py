import pdfplumber
from pathlib import Path

with pdfplumber.open('Law/JustSettlementStatements.pdf') as pdf:
    text = '\n\n'.join([page.extract_text() for page in pdf.pages])

# Find Whetstone section and check length
idx = text.find('Teresa Whetstone')
if idx >= 0:
    # Find next case anchor
    next_idx = text.find('This Document Relates to Plaintiff:', idx + 1)
    if next_idx < 0:
        next_idx = len(text)
    
    whetstone_section = text[idx:next_idx]
    print(f'Whetstone section length: {len(whetstone_section)}')
    print(f'Contains "open abdom": {"open abdom" in whetstone_section.lower()}')
    
    # Search for open in this section
    if 'open' in whetstone_section.lower():
        open_idx = whetstone_section.lower().find('open')
        print(f'Found "open" at offset {open_idx}')
        print(whetstone_section[open_idx:open_idx+200])

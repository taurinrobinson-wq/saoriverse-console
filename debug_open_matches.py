import pdfplumber
from pathlib import Path

plaintiffs_to_check = {
    'Robert Tavares': False,  # Should NOT have open surgery
    'Vonda Webb': False,      # Should NOT have open surgery  
    'Teresa Whetstone': True,  # SHOULD have open surgery
}

with pdfplumber.open('Law/JustSettlementStatements.pdf') as pdf:
    text = '\n\n'.join([page.extract_text() for page in pdf.pages])

for plaintiff, should_have_open in plaintiffs_to_check.items():
    idx = text.find(plaintiff)
    if idx >= 0:
        # Find next case anchor
        next_idx = text.find('This Document Relates to Plaintiff:', idx + 1)
        if next_idx < 0:
            next_idx = len(text)
        
        section = text[idx:next_idx]
        
        # Find all "open" occurrences
        print(f"\n{'='*80}")
        print(f"{plaintiff} - Should have open: {should_have_open}")
        print(f"{'='*80}")
        
        open_idx = 0
        count = 0
        while True:
            open_idx = section.lower().find('open', open_idx)
            if open_idx < 0:
                break
            
            # Show context around each "open"
            context_start = max(0, open_idx - 50)
            context_end = min(len(section), open_idx + 150)
            context = section[context_start:context_end]
            
            print(f"\nOccurrence {count + 1}:")
            print(f"  ...{repr(context)}...")
            
            open_idx += 1
            count += 1

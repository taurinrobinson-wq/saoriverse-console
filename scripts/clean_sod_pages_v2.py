#!/usr/bin/env python3
"""
Better cleaning - remove ALL leading numbers 1-28 and fix formatting
"""

from pathlib import Path
import re

pages_dir = Path(r"d:\saoriverse-console\DraftShift\Docs\BrownVacateMtn\SOD_Pages")
cleaned_dir = Path(r"d:\saoriverse-console\DraftShift\Docs\BrownVacateMtn\SOD_Pages_Cleaned")

cleaned_dir.mkdir(parents=True, exist_ok=True)

page_files = sorted(pages_dir.glob("Page_*.txt"))

for page_file in page_files:
    with open(page_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    page_num = page_file.stem.split('_')[1]
    
    lines = content.split('\n')
    content_lines = []
    found_real_content = False
    
    for line in lines:
        # Skip header/footer markers
        if '===== PAGE' in line or '===== END PAGE' in line:
            continue
        
        # Check if this is a pure line number line (just whitespace and numbers 1-28)
        stripped = line.strip()
        if stripped and re.match(r'^[\d\s]+$', stripped):
            # Check if it's only numbers from the line number section
            nums = re.findall(r'\d+', stripped)
            if all(int(n) <= 28 for n in nums):
                continue
        
        # Once we find actual text content, keep everything
        if stripped and not found_real_content:
            if 'INTRODUCTION' in stripped or 'PROCEDURAL' in stripped or 'EVIDENCE' in stripped or 'BACKGROUND' in stripped:
                found_real_content = True
        
        if found_real_content or (stripped and 'I' in stripped and len(stripped) > 1):
            content_lines.append(line)
    
    cleaned_content = '\n'.join(content_lines).strip()
    
    # Fix OCR issues
    fixes = {
        'withinterruptions': 'with interruptions',
        'Angel_es': 'Angeles',
        'presiding ,': 'presiding,',
        'thereafter ,': 'thereafter,',
        'testimony ,': 'testimony,',
        'Greenfield .': 'Greenfield.',
        'Decision .': 'Decision.',
        '/Cross-comp lainants': '/Cross-complainants',
        'cross-comp laint': 'cross-complaint',
        'defendant s': 'defendants',
        'plaintiff s': 'plaintiffs',
        'white defendant s': 'white defendants',
        'Conversion ;': 'Conversion;',
        'Advantage ;': 'Advantage;',
        'successfu l': 'successful',
        'cross­\nplainant': 'cross-complainant',
    }
    
    for old, new in fixes.items():
        cleaned_content = cleaned_content.replace(old, new)
    
    output_file = cleaned_dir / page_file.name
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print(f"Processed Page {page_num}")

print(f"\nAll 41 pages cleaned and saved to SOD_Pages_Cleaned/")

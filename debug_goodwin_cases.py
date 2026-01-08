import pdfplumber
from pathlib import Path
import sys
sys.path.insert(0, 'tools/SPINE')
from spine_parser import extract_text, split_cases, extract_plaintiff, extract_all_injuries, build_summary

# Test with Goodwin
pdf_path = Path('tools/SPINE/17-cv-02775 - GoodwinConfSettlementStmt.pdf')
text = extract_text(pdf_path)
cases = split_cases(text)

print(f'Number of cases: {len(cases)}')

for i, case_text in enumerate(cases):
    plaintiff = extract_plaintiff(case_text)
    print(f'\nCase {i}: {plaintiff}')
    print(f'  Case text length: {len(case_text)}')
    
    # Show first and last 200 chars
    print(f'  First 200 chars: {repr(case_text[:200])}')
    print(f'  Last 200 chars: {repr(case_text[-200:])}')
    
    # Extract injuries
    inj = extract_all_injuries(case_text)
    summary = build_summary(inj)
    print(f'  Summary: {summary[:150]}...')

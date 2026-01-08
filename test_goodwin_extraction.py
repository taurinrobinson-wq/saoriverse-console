import sys
sys.path.insert(0, 'tools/SPINE')
from spine_parser import extract_text, split_cases, extract_plaintiff, extract_all_injuries
from pathlib import Path

# Test with Goodwin
text = extract_text(Path('tools/SPINE/17-cv-02775 - GoodwinConfSettlementStmt.pdf'))
cases = split_cases(text)

print(f'Found {len(cases)} cases in Goodwin PDF')

for i, case_text in enumerate(cases):
    plaintiff = extract_plaintiff(case_text)
    print(f'Case {i}: {plaintiff}')
    inj = extract_all_injuries(case_text)
    print(f'  retrieval_open: {inj["retrieval_open"]}')
    print(f'  fracture: {inj["fracture"]}')
    print(f'  perforation_grade: {inj["perforation_grade"]}')

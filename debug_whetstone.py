import pdfplumber
from pathlib import Path
import sys
import re
sys.path.insert(0, str(Path(__file__).parent / "tools" / "SPINE"))
from spine_parser import extract_text, split_cases, extract_plaintiff, extract_all_injuries, PATTERNS

# Extract and find Whetstone
text = extract_text(Path("Law/JustSettlementStatements.pdf"))
cases = split_cases(text)

for i, case_text in enumerate(cases):
    plaintiff = extract_plaintiff(case_text)
    if plaintiff and "Whetstone" in plaintiff:
        print(f"Found {plaintiff} at case {i}")
        print("=" * 80)
        
        # Check if open surgery text exists in full case
        if "open" in case_text.lower() and "abdom" in case_text.lower():
            print("✓ Full case text contains 'open' and 'abdom'")
            # Find the section
            idx = case_text.lower().find("open abdom")
            if idx >= 0:
                section = case_text[idx:idx+100]
                print(f"Found at index {idx}: {repr(section)}")
        else:
            print("✗ Full case text does NOT contain 'open abdom'")
        
        print("=" * 80)
        
        # Extract injuries
        injuries = extract_all_injuries(case_text)
        print(f"\nExtracted retrieval_open: {injuries['retrieval_open']}")
        
        # Test pattern directly on case_text
        print("\nTesting PATTERNS directly:")
        if re.search(PATTERNS["retrieval_open"], case_text.lower()):
            print(f"✓ retrieval_open pattern matches")
            m = re.search(PATTERNS["retrieval_open"], case_text.lower())
            print(f"  Matched: {repr(m.group())}")
        else:
            print(f"✗ retrieval_open pattern DOES NOT match")
            print(f"  Pattern: {PATTERNS['retrieval_open']}")
        
        print(f"\nFull injuries dict (non-empty values):")
        for k, v in injuries.items():
            if v not in [False, None, [], 0]:
                print(f"  {k}: {v}")



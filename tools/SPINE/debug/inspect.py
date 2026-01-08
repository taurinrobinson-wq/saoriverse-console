"""Debug utilities for inspecting PDF extraction and pattern matching.

This module provides utilities for inspecting PDF text extraction,
examining specific cases, testing patterns, and validating extraction results.
"""

import pdfplumber
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from spine_parser import extract_text, split_cases, extract_plaintiff, extract_all_injuries, PATTERNS


def inspect_case_section(pdf_path: Path, plaintiff_name: str) -> str:
    """Extract and display the section for a specific plaintiff.
    
    Args:
        pdf_path: Path to PDF file
        plaintiff_name: Name to search for
        
    Returns:
        The case section text
    """
    text = extract_text(pdf_path)
    cases = split_cases(text)
    
    for case_text in cases:
        plaintiff = extract_plaintiff(case_text)
        if plaintiff and plaintiff_name in plaintiff:
            return case_text
    
    return None


def find_pattern_occurrences(pdf_path: Path, plaintiff_name: str, pattern_key: str) -> list:
    """Find all occurrences of a specific pattern for a plaintiff.
    
    Args:
        pdf_path: Path to PDF file
        plaintiff_name: Name to search for
        pattern_key: Key in PATTERNS dict (e.g., 'retrieval_open', 'death')
        
    Returns:
        List of (index, context) tuples for each occurrence
    """
    case_text = inspect_case_section(pdf_path, plaintiff_name)
    if not case_text:
        return []
    
    if pattern_key not in PATTERNS:
        return []
    
    pattern = PATTERNS[pattern_key]
    occurrences = []
    
    for match in re.finditer(pattern, case_text, re.IGNORECASE):
        start = max(0, match.start() - 50)
        end = min(len(case_text), match.end() + 150)
        context = case_text[start:end]
        occurrences.append((match.start(), context))
    
    return occurrences


def inspect_damages_section(pdf_path: Path, plaintiff_name: str) -> str:
    """Extract and display the damages section for a specific plaintiff.
    
    Args:
        pdf_path: Path to PDF file
        plaintiff_name: Name to search for
        
    Returns:
        The damages section text (usually 1500 chars after "following values represent")
    """
    case_text = inspect_case_section(pdf_path, plaintiff_name)
    if not case_text:
        return None
    
    damages_idx = case_text.find("following values represent")
    if damages_idx < 0:
        return None
    
    return case_text[damages_idx:damages_idx+1500]


def test_plaintiff_patterns(pdf_path: Path, plaintiff_name: str) -> dict:
    """Test all patterns for a specific plaintiff and return results.
    
    Args:
        pdf_path: Path to PDF file
        plaintiff_name: Name to search for
        
    Returns:
        Dict with pattern_name: bool for each pattern
    """
    case_text = inspect_case_section(pdf_path, plaintiff_name)
    if not case_text:
        return {}
    
    injuries = extract_all_injuries(case_text)
    return injuries


def compare_plaintiffs(pdf_path: Path, plaintiff_names: list) -> None:
    """Display side-by-side comparison of injury extraction for multiple plaintiffs.
    
    Args:
        pdf_path: Path to PDF file
        plaintiff_names: List of names to compare
    """
    print(f"\n{'='*80}")
    print(f"Comparing {len(plaintiff_names)} plaintiffs")
    print(f"{'='*80}\n")
    
    for name in plaintiff_names:
        injuries = test_plaintiff_patterns(pdf_path, name)
        
        print(f"\n{name}:")
        print(f"  Open surgical retrieval: {injuries.get('retrieval_open', False)}")
        print(f"  Fracture: {injuries.get('fracture', False)}")
        print(f"  Perforation grade: {injuries.get('perforation_grade', 'None')}")
        print(f"  Death: {injuries.get('death', False)}")
        
        # Show pattern occurrences
        for pattern_key in ['retrieval_open', 'death']:
            occurrences = find_pattern_occurrences(pdf_path, name, pattern_key)
            if occurrences:
                print(f"  {pattern_key} occurrences: {len(occurrences)}")
                for i, (idx, context) in enumerate(occurrences, 1):
                    print(f"    [{i}] ...{repr(context[:80])}...")


def validate_extraction_accuracy(pdf_path: Path, test_cases: dict) -> None:
    """Validate extraction against expected results for known test cases.
    
    Args:
        pdf_path: Path to PDF file
        test_cases: Dict of {plaintiff_name: {expected_pattern_key: bool}}
        
    Example:
        test_cases = {
            "Teresa Whetstone": {"retrieval_open": True, "death": False},
            "Robert Tavares": {"retrieval_open": False, "death": False},
        }
    """
    print(f"\n{'='*80}")
    print("EXTRACTION VALIDATION")
    print(f"{'='*80}\n")
    
    passed = 0
    failed = 0
    
    for plaintiff_name, expected in test_cases.items():
        injuries = test_plaintiff_patterns(pdf_path, plaintiff_name)
        
        case_passed = True
        print(f"{plaintiff_name}:")
        
        for pattern_key, expected_value in expected.items():
            actual_value = injuries.get(pattern_key, False)
            match = actual_value == expected_value
            status = "✓" if match else "✗"
            
            print(f"  {status} {pattern_key}: expected {expected_value}, got {actual_value}")
            
            if not match:
                case_passed = False
                failed += 1
            else:
                passed += 1
        
        print()
    
    total = passed + failed
    print(f"\nSummary: {passed}/{total} tests passed")
    if failed == 0:
        print("✓ ALL TESTS PASSED")
    else:
        print(f"✗ {failed} tests failed")


if __name__ == "__main__":
    # Example usage
    pdf_path = Path("Raw_Data_Docs/JustSettlementStatements.pdf")
    
    # Compare specific plaintiffs
    test_names = ["Teresa Whetstone", "Robert Tavares", "Vonda Webb"]
    compare_plaintiffs(pdf_path, test_names)
    
    # Validate against expected results
    test_cases = {
        "Teresa Whetstone": {"retrieval_open": True, "death": False},
        "Robert Tavares": {"retrieval_open": False, "death": False},
        "Vonda Webb": {"retrieval_open": False, "death": False},
    }
    validate_extraction_accuracy(pdf_path, test_cases)

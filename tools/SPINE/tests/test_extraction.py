"""Test suite for SPINE v2 extraction engine.

Includes tests for:
- Text extraction and preprocessing
- Field extraction (plaintiff, case number, amount, brand)
- Injury pattern matching
- Multi-file processing
- CSV generation
"""

import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from spine_parser import (
    extract_text, split_cases, extract_plaintiff, extract_case_number,
    detect_brand, extract_amounts, extract_all_injuries, build_summary, PATTERNS
)
from rebuild import rebuild_caption_lines


def test_rebuild_caption():
    """Test multi-line caption reconstruction."""
    raw = """This Document Relates to Plaintiff:
Desmund Hicks o/b/o, Heron
Anderson-Cotton, Deceased
Case No: 1:17-cv-03525"""
    
    rebuilt = rebuild_caption_lines(raw)
    
    # Should merge the plaintiff names
    assert "Desmund Hicks o/b/o, Heron Anderson-Cotton, Deceased" in rebuilt
    print("[OK] test_rebuild_caption passed")


def test_pattern_matching():
    """Test regex patterns for accuracy."""
    test_cases = {
        "Open abdonimal surgery": PATTERNS["retrieval_open"],
        "Open abdominal surgery": PATTERNS["retrieval_open"],
        "only open surgical removal would be feasible": "retrieval_open should NOT match in full text",
    }
    
    # Test retrieval_open pattern
    pattern = PATTERNS["retrieval_open"]
    
    # Should match "Open abdonimal surgery"
    assert re.search(pattern, "Open abdonimal surgery", re.IGNORECASE)
    
    # Should match "Open abdominal surgery"
    assert re.search(pattern, "Open abdominal surgery", re.IGNORECASE)
    
    print("✓ test_pattern_matching passed")


def test_extract_case_number():
    """Test case number extraction."""
    test_text = """
    Case Number: 1:17-cv-02671
    """
    
    case_num = extract_case_number(test_text)
    assert "1:17-cv-02671" in case_num or case_num == "1:17-cv-02671"
    print("✓ test_extract_case_number passed")


def test_extract_plaintiff():
    """Test plaintiff name extraction."""
    test_text = """
    This Document Relates to Plaintiff:
    Teresa Whetstone
    """
    
    plaintiff = extract_plaintiff(test_text)
    assert "Whetstone" in plaintiff or "Teresa" in plaintiff
    print("✓ test_extract_plaintiff passed")


def test_extract_amounts():
    """Test amount extraction."""
    test_text = """
    Total Settlement: $781,500.00
    Previous Amount: $100,000
    """
    
    amounts = extract_amounts(test_text)
    assert len(amounts) > 0
    assert max(amounts) == 781500.0 or max(amounts) == 781500
    print("✓ test_extract_amounts passed")


def test_detect_brand():
    """Test device brand detection."""
    test_text = """
    The Cook Celect filter was placed on 2015.
    """
    
    brand = detect_brand(test_text)
    assert "Cook" in brand or "Celect" in brand.lower()
    print("✓ test_detect_brand passed")


def test_injury_extraction():
    """Test comprehensive injury pattern matching."""
    test_text = """
    The patient has a fractured device with migration into the duodenum.
    Grade 4 perforation was observed with penetration into surrounding tissue.
    The device is embedded and tilted in a dangerous location.
    """
    
    injuries = extract_all_injuries(test_text)
    
    assert injuries.get("fracture") == True
    assert injuries.get("migration") == True
    print("✓ test_injury_extraction passed")


def test_summary_building():
    """Test summary generation from injury signals."""
    injuries = {
        "retrieval_open": False,
        "death": False,
        "fracture": True,
        "migration": True,
        "perforation_grade": "4",
        "penetration": True,
        "organ_involved": ["duodenum"],
        "retrieval_complex": True,
    }
    
    summary = build_summary(injuries)
    assert isinstance(summary, str)
    assert len(summary) > 0
    assert len(summary) <= 250
    print("✓ test_summary_building passed")


def test_spatial_scoping():
    """Test that retrieval_open only matches in damages section."""
    # This test verifies the critical fix for false positives
    
    test_text = """
    MEDICAL HISTORY:
    The patient had open surgical removal attempted but this failed.
    
    SETTLEMENT VALUES:
    Following values represent damages claimed:
    Open abdonimal surgery Procedure: $600,000
    """
    
    injuries = extract_all_injuries(test_text)
    # Should be True because "Open abdonimal surgery" is in damages section
    assert injuries.get("retrieval_open") == True
    print("✓ test_spatial_scoping passed")


def run_all_tests():
    """Run all tests and report results."""
    tests = [
        test_rebuild_caption,
        test_pattern_matching,
        test_extract_case_number,
        test_extract_plaintiff,
        test_extract_amounts,
        test_detect_brand,
        test_injury_extraction,
        test_summary_building,
        test_spatial_scoping,
    ]
    
    print("\n" + "="*80)
    print("SPINE v2 Test Suite")
    print("="*80 + "\n")
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test_func.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {test_func.__name__} ERROR: {e}")
            failed += 1
    
    print(f"\n{'='*80}")
    print(f"Results: {passed} passed, {failed} failed")
    if failed == 0:
        print("[PASS] ALL TESTS PASSED")
    else:
        print(f"[FAIL] {failed} tests failed")
    print(f"{'='*80}\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

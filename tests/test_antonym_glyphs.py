#!/usr/bin/env python3
"""
Test Suite for Antonym Glyphs Integration

Comprehensive tests for:
- Loading and indexing antonym glyphs
- Searching and lookup functions
- Antonym pair discovery
- UI integration helpers
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from emotional_os.glyphs.antonym_glyphs import (
    get_total_antonym_count,
    find_antonym_by_emotion,
    find_antonym_by_voltage_pair,
    search_antonyms,
    suggest_emotional_opposite,
    list_antonym_emotions,
    list_antonym_pairings,
    format_antonym_for_display,
    get_antonym_metadata
)


class AntonymGlyphsTestSuite:
    """Comprehensive test suite for antonym glyphs."""
    
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []
    
    def test(self, name: str, condition: bool, details: str = "") -> bool:
        """Record a test result.
        
        Args:
            name: Test name
            condition: Test condition (True = pass, False = fail)
            details: Optional details
            
        Returns:
            bool: Test condition
        """
        self.total_tests += 1
        
        if condition:
            self.passed_tests += 1
            status = "✓ PASS"
        else:
            self.failed_tests += 1
            status = "✗ FAIL"
        
        result = {
            "name": name,
            "status": status,
            "details": details
        }
        self.test_results.append(result)
        
        if not condition:
            print(f"\n{status}: {name}")
            if details:
                print(f"  Details: {details}")
        
        return condition
    
    def run_all_tests(self):
        """Run all test suites."""
        print("\n" + "=" * 80)
        print("ANTONYM GLYPHS TEST SUITE")
        print("=" * 80)
        
        self.test_loading()
        self.test_basic_lookups()
        self.test_searches()
        self.test_metadata()
        self.test_ui_integration()
        self.test_data_integrity()
        
        self.print_summary()
    
    def test_loading(self):
        """Test that antonym glyphs load correctly."""
        print("\n[LOADING TESTS]")
        
        total = get_total_antonym_count()
        self.test(
            "Antonym glyphs load",
            total > 0,
            f"Loaded {total} antonym glyphs"
        )
        
        self.test(
            "Expected count range",
            100 <= total <= 150,
            f"Expected ~122, got {total}"
        )
        
        metadata = get_antonym_metadata()
        self.test(
            "Metadata available",
            metadata is not None and len(metadata) > 0,
            f"Metadata: {metadata}"
        )
    
    def test_basic_lookups(self):
        """Test basic lookup functions."""
        print("\n[LOOKUP TESTS]")
        
        # Test emotion lookup
        comfort = find_antonym_by_emotion("comfort")
        self.test(
            "Find by emotion 'comfort'",
            comfort is not None,
            f"Found: {comfort.get('Name') if comfort else 'None'}"
        )
        
        if comfort:
            self.test(
                "Comfort has required fields",
                all(k in comfort for k in ["Base Emotion", "Pairing", "Name", "Description"]),
                f"Fields: {list(comfort.keys())}"
            )
        
        # Test voltage pair lookup
        gamma_pair = find_antonym_by_voltage_pair("γ × γ")
        self.test(
            "Find by voltage pair 'γ × γ'",
            gamma_pair is not None,
            f"Found: {gamma_pair.get('Name') if gamma_pair else 'None'}"
        )
        
        # Test nonexistent emotion
        none_result = find_antonym_by_emotion("nonexistent_emotion_xyz")
        self.test(
            "Nonexistent emotion returns None",
            none_result is None,
            "Correct behavior"
        )
    
    def test_searches(self):
        """Test search functions."""
        print("\n[SEARCH TESTS]")
        
        # Test simple search
        joy_results = search_antonyms("joy")
        self.test(
            "Search for 'joy'",
            len(joy_results) > 0,
            f"Found {len(joy_results)} results"
        )
        
        # Test case-insensitive search
        peace_results = search_antonyms("PEACE")
        self.test(
            "Case-insensitive search",
            len(peace_results) > 0,
            f"Found {len(peace_results)} results for 'PEACE'"
        )
        
        # Test multi-word search
        gentle_results = search_antonyms("gentle")
        self.test(
            "Search for 'gentle'",
            len(gentle_results) > 0,
            f"Found {len(gentle_results)} results"
        )
        
        if gentle_results:
            # Check that search results have the query word
            has_match = any("gentle" in str(r.get("Name", "")).lower() or
                          "gentle" in str(r.get("Description", "")).lower()
                          for r in gentle_results[:3])
            self.test(
                "Search results contain query",
                has_match,
                "Results correctly match search query"
            )
    
    def test_metadata(self):
        """Test metadata access."""
        print("\n[METADATA TESTS]")
        
        emotions = list_antonym_emotions()
        self.test(
            "List emotions",
            len(emotions) > 0,
            f"Found {len(emotions)} unique emotions"
        )
        
        pairings = list_antonym_pairings()
        self.test(
            "List pairings",
            len(pairings) > 0,
            f"Found {len(pairings)} unique pairings"
        )
        
        self.test(
            "Emotions list is sorted",
            emotions == sorted(emotions),
            "Emotions are in alphabetical order"
        )
        
        self.test(
            "Pairings list is sorted",
            pairings == sorted(pairings),
            "Pairings are in sorted order"
        )
    
    def test_ui_integration(self):
        """Test UI integration helpers."""
        print("\n[UI INTEGRATION TESTS]")
        
        # Test formatting
        antonym = find_antonym_by_emotion("comfort")
        if antonym:
            formatted = format_antonym_for_display(antonym)
            self.test(
                "Format for display",
                len(formatted) > 0 and "Comfort" in formatted,
                f"Formatted string length: {len(formatted)}"
            )
            
            self.test(
                "Formatted output contains description",
                "soothed" in formatted.lower(),
                "Description is included in formatted output"
            )
        else:
            self.test("Format for display", False, "Antonym not found")
        
        # Test null formatting
        null_formatted = format_antonym_for_display(None)
        self.test(
            "Format None returns empty",
            null_formatted == "",
            "Handles None gracefully"
        )
    
    def test_data_integrity(self):
        """Test data integrity and consistency."""
        print("\n[DATA INTEGRITY TESTS]")
        
        total = get_total_antonym_count()
        emotions = list_antonym_emotions()
        pairings = list_antonym_pairings()
        
        self.test(
            "All emotions accessible",
            len(emotions) > 0,
            f"Emotion count: {len(emotions)}"
        )
        
        self.test(
            "All pairings accessible",
            len(pairings) > 0,
            f"Pairing count: {len(pairings)}"
        )
        
        # Sample some emotions to ensure they're findable
        sample_emotions = emotions[:5] if emotions else []
        for emotion in sample_emotions:
            antonym = find_antonym_by_emotion(emotion)
            if not antonym:
                self.test(
                    f"Find emotion '{emotion}'",
                    False,
                    f"Listed but not findable"
                )
                break
        else:
            if sample_emotions:
                self.test(
                    "Sample emotions are findable",
                    True,
                    f"Checked {len(sample_emotions)} sample emotions"
                )
        
        # Sample some pairings
        sample_pairings = pairings[:5] if pairings else []
        for pairing in sample_pairings:
            antonym = find_antonym_by_voltage_pair(pairing)
            if not antonym:
                self.test(
                    f"Find pairing '{pairing}'",
                    False,
                    f"Listed but not findable"
                )
                break
        else:
            if sample_pairings:
                self.test(
                    "Sample pairings are findable",
                    True,
                    f"Checked {len(sample_pairings)} sample pairings"
                )
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        print(f"\nTotal Tests: {self.total_tests}")
        print(f"✓ Passed: {self.passed_tests}")
        print(f"✗ Failed: {self.failed_tests}")
        
        if self.failed_tests == 0:
            print(f"\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {self.failed_tests} test(s) failed")
        
        # Show pass rate
        if self.total_tests > 0:
            pass_rate = (self.passed_tests / self.total_tests) * 100
            print(f"Pass Rate: {pass_rate:.1f}%")
        
        return self.failed_tests == 0


def run_integration_tests():
    """Run integration tests with the glyph system."""
    print("\n" + "=" * 80)
    print("INTEGRATION TESTS")
    print("=" * 80)
    
    # Test that antonym glyphs can be searched within expected ranges
    print("\n[EMOTION RANGE TEST]")
    
    test_emotions = [
        ("comfort", True),
        ("joy", True),
        ("peace", True),
        ("strength", True),
        ("nonexistent", False),
    ]
    
    for emotion, should_exist in test_emotions:
        result = find_antonym_by_emotion(emotion)
        exists = result is not None
        
        if exists == should_exist:
            print(f"✓ {emotion}: {'Found' if exists else 'Not found'} (as expected)")
        else:
            print(f"✗ {emotion}: {'Found' if exists else 'Not found'} (unexpected)")
    
    print("\n[PAIRING CONSISTENCY TEST]")
    
    # Verify that common pairings are available
    common_pairings = [
        "γ × γ",  # Recursive Ache
        "λ × λ",  # Saturational Bliss
        "δ × δ",  # Karmic Void
    ]
    
    for pairing in common_pairings:
        result = find_antonym_by_voltage_pair(pairing)
        if result:
            print(f"✓ {pairing}: {result.get('Base Emotion')}")
        else:
            print(f"✗ {pairing}: Not found")


def main():
    """Run all tests."""
    suite = AntonymGlyphsTestSuite()
    suite.run_all_tests()
    
    run_integration_tests()
    
    # Return exit code based on results
    return 0 if suite.failed_tests == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

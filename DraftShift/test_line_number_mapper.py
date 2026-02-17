"""
Test Suite for DraftShift Line Number Mapper
=============================================

Comprehensive tests demonstrating the line number detection and
text-to-line assignment algorithms.
"""

import json
from line_number_mapper import (
    BoundingBox, OCRTextBlock, LineNumberMarker, LineBand,
    LineNumberDetector, LineBandGenerator, TextToLineAssigner,
    PageLineMap, DocumentLineMapper
)


def test_bounding_box():
    """Test BoundingBox creation and properties."""
    print("TEST: BoundingBox Properties")
    print("-" * 50)
    
    bbox = BoundingBox(100, 200, 300, 400)
    
    assert bbox.x1 == 100
    assert bbox.y1 == 200
    assert bbox.x2 == 300
    assert bbox.y2 == 400
    assert bbox.width == 200
    assert bbox.height == 200
    assert bbox.center_x == 200
    assert bbox.center_y == 300
    
    print("✓ BoundingBox properties calculated correctly")
    print(f"  Box: ({bbox.x1}, {bbox.y1}) to ({bbox.x2}, {bbox.y2})")
    print(f"  Width: {bbox.width}, Height: {bbox.height}")
    print(f"  Center: ({bbox.center_x}, {bbox.center_y})")
    print()


def test_line_number_detection():
    """Test detection of printed line numbers from OCR text."""
    print("TEST: Line Number Detection")
    print("-" * 50)
    
    # Create text blocks with line numbers in left margin
    text_blocks = [
        OCRTextBlock("1", BoundingBox(10, 100, 25, 120), 0.99),
        OCRTextBlock("This is the first line", BoundingBox(50, 100, 250, 120), 0.95),
        OCRTextBlock("2", BoundingBox(10, 135, 25, 155), 0.99),
        OCRTextBlock("This is the second line", BoundingBox(50, 135, 280, 155), 0.94),
        OCRTextBlock("3", BoundingBox(10, 170, 25, 190), 0.99),
        OCRTextBlock("This is the third line", BoundingBox(50, 170, 270, 190), 0.96),
    ]
    
    detector = LineNumberDetector()
    markers = detector.detect(text_blocks)
    
    print(f"Detected {len(markers)} line markers:")
    for marker in markers:
        print(f"  Line {marker.line_number} at y={marker.y_position:.1f}")
    
    assert len(markers) == 3
    assert markers[0].line_number == 1
    assert markers[1].line_number == 2
    assert markers[2].line_number == 3
    
    print("✓ All line numbers detected correctly")
    print()


def test_band_generation():
    """Test creation of horizontal bands between line numbers."""
    print("TEST: Line Band Generation")
    print("-" * 50)
    
    # Create markers at regular intervals
    markers = [
        LineNumberMarker(line_number=1, y_position=100, text="1", confidence=0.99),
        LineNumberMarker(line_number=2, y_position=135, text="2", confidence=0.99),
        LineNumberMarker(line_number=3, y_position=170, text="3", confidence=0.99),
        LineNumberMarker(line_number=4, y_position=205, text="4", confidence=0.99),
    ]
    
    band_gen = LineBandGenerator(page_height=1000)
    bands = band_gen.generate(markers)
    
    print(f"Generated {len(bands)} bands:")
    for i, band in enumerate(bands[:5]):  # Show first 5
        print(f"  Band {band.line_number}: y={band.top:.1f} to {band.bottom:.1f}")
    
    assert len(bands) == 28
    assert bands[0].line_number == 1
    assert bands[1].line_number == 2
    
    # Verify bands don't overlap
    for i in range(len(bands) - 1):
        assert bands[i].bottom <= bands[i+1].top, "Bands overlap!"
    
    print("✓ Bands generated correctly with no overlaps")
    print()


def test_text_assignment():
    """Test assigning text blocks to line numbers."""
    print("TEST: Text to Line Assignment")
    print("-" * 50)
    
    # Create bands for lines 1-4
    bands = [
        LineBand(line_number=1, top=100, bottom=135),
        LineBand(line_number=2, top=135, bottom=170),
        LineBand(line_number=3, top=170, bottom=205),
        LineBand(line_number=4, top=205, bottom=240),
    ]
    
    # Create text blocks to assign
    text_blocks = [
        OCRTextBlock("First", BoundingBox(50, 100, 150, 125), 0.95),
        OCRTextBlock("Second", BoundingBox(50, 140, 150, 165), 0.95),
        OCRTextBlock("Third", BoundingBox(50, 175, 150, 200), 0.95),
    ]
    
    assigner = TextToLineAssigner()
    assignment = assigner.assign_with_overlaps(text_blocks, bands)
    
    print("Text assignments:")
    for line_num in sorted(assignment.keys()):
        blocks = assignment[line_num]
        texts = [b.text for b in blocks]
        print(f"  Line {line_num}: {texts}")
    
    assert assignment[1][0].text == "First"
    assert assignment[2][0].text == "Second"
    assert assignment[3][0].text == "Third"
    
    print("✓ Text blocks assigned to correct lines")
    print()


def test_page_mapping():
    """Test single-page line mapping."""
    print("TEST: Single Page Line Mapping")
    print("-" * 50)
    
    # Create a simple page with 5 lines
    text_blocks = [
        OCRTextBlock("1", BoundingBox(10, 100, 25, 120), 0.99),
        OCRTextBlock("The court finds that the defendant...", BoundingBox(50, 100, 500, 120), 0.95),
        OCRTextBlock("2", BoundingBox(10, 135, 25, 155), 0.99),
        OCRTextBlock("was aware of the facts in question.", BoundingBox(50, 135, 400, 155), 0.94),
        OCRTextBlock("3", BoundingBox(10, 170, 25, 190), 0.99),
        OCRTextBlock("This conclusion is supported by evidence.", BoundingBox(50, 170, 450, 190), 0.96),
    ]
    
    # Create page map
    page_map = PageLineMap(page_number=1, page_height=1000, page_width=800)
    page_map.process(text_blocks)
    
    # Extract text for specific lines
    line_1_text = page_map.get_text_for_line(1)
    line_2_text = page_map.get_text_for_line(2)
    line_3_text = page_map.get_text_for_line(3)
    
    print("Extracted text by line:")
    print(f"  Line 1: {line_1_text[:60]}...")
    print(f"  Line 2: {line_2_text[:60]}...")
    print(f"  Line 3: {line_3_text[:60]}...")
    
    assert "defendant" in line_1_text
    assert "aware" in line_2_text
    assert "supported" in line_3_text
    
    print("✓ Page mapping correctly extracts text by line")
    print()


def test_document_mapping():
    """Test multi-page document mapping."""
    print("TEST: Multi-Page Document Mapping")
    print("-" * 50)
    
    mapper = DocumentLineMapper()
    
    # Add page 1
    page_1_blocks = [
        OCRTextBlock("1", BoundingBox(10, 100, 25, 120), 0.99),
        OCRTextBlock("Brown and Norris are co-owners.", BoundingBox(50, 100, 400, 120), 0.95),
    ]
    mapper.add_page(1, 1000, 800, page_1_blocks)
    
    # Add page 2
    page_2_blocks = [
        OCRTextBlock("1", BoundingBox(10, 100, 25, 120), 0.99),
        OCRTextBlock("Pak was responsible for lead generation.", BoundingBox(50, 100, 450, 120), 0.95),
    ]
    mapper.add_page(2, 1000, 800, page_2_blocks)
    
    # Retrieve text
    text_p1_l1 = mapper.get_text_at_location(1, 1)
    text_p2_l1 = mapper.get_text_at_location(2, 1)
    
    print("Document mapping (2 pages):")
    print(f"  Page 1, Line 1: {text_p1_l1[:50]}...")
    print(f"  Page 2, Line 1: {text_p2_l1[:50]}...")
    
    assert len(mapper.pages) == 2
    assert mapper.pages[1] is not None
    assert mapper.pages[2] is not None
    
    print("✓ Document mapping handles multiple pages")
    print()


def test_json_export():
    """Test exporting mapper to JSON format."""
    print("TEST: JSON Export")
    print("-" * 50)
    
    mapper = DocumentLineMapper()
    
    text_blocks = [
        OCRTextBlock("1", BoundingBox(10, 100, 25, 120), 0.99),
        OCRTextBlock("The court finds...", BoundingBox(50, 100, 350, 120), 0.95),
    ]
    mapper.add_page(1, 1000, 800, text_blocks)
    
    json_output = mapper.to_json()
    parsed = json.loads(json_output)
    
    print("JSON structure:")
    print(f"  Pages: {list(parsed.keys())}")
    print(f"  Page 1 data: {list(parsed['1'].keys())}")
    
    assert "1" in parsed
    assert "page_number" in parsed["1"]
    assert "line_maps" in parsed["1"]
    
    print("✓ JSON export valid and well-structured")
    print()


def test_citation_generation():
    """Test generating citations for legal documents."""
    print("TEST: Citation Generation")
    print("-" * 50)
    
    mapper = DocumentLineMapper()
    
    # Create multi-line content for SOD simulation
    text_blocks = [
        OCRTextBlock("1", BoundingBox(10, 100, 25, 120), 0.99),
        OCRTextBlock("Brown received leads from Norris for", BoundingBox(50, 100, 450, 120), 0.95),
        OCRTextBlock("2", BoundingBox(10, 135, 25, 155), 0.99),
        OCRTextBlock("the purpose of generating new business.", BoundingBox(50, 135, 420, 155), 0.94),
    ]
    mapper.add_page(5, 1000, 800, text_blocks)
    
    # Get citations
    citation_p5_l1 = mapper.get_text_at_location(5, 1)
    citation_p5_l2 = mapper.get_text_at_location(5, 2)
    
    print("Citation candidates from document:")
    print(f"  (SOD, p. 5, ln. 1) '{citation_p5_l1}'")
    print(f"  (SOD, p. 5, ln. 2) '{citation_p5_l2}'")
    
    assert "Brown" in citation_p5_l1
    assert "Norris" in citation_p5_l1
    
    print("✓ Citations generated for specific page/line locations")
    print()


def run_all_tests():
    """Run all tests."""
    print("=" * 50)
    print("DraftShift Line Number Mapper - Test Suite")
    print("=" * 50)
    print()
    
    try:
        test_bounding_box()
        test_line_number_detection()
        test_band_generation()
        test_text_assignment()
        test_page_mapping()
        test_document_mapping()
        test_json_export()
        test_citation_generation()
        
        print("=" * 50)
        print("✓ ALL TESTS PASSED")
        print("=" * 50)
        return True
    
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)

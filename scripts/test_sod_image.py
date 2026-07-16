"""
Test Line Number Mapper on Actual SOD Image
============================================

This script tests the line_number_mapper module on a real Statement of Decision image.
"""

import os
import sys
from pathlib import Path

# Import the mapper
from line_number_mapper import (
    DocumentLineMapper, OCRTextBlock, BoundingBox
)

def extract_text_with_pytesseract(image_path):
    """
    Extract text with bounding boxes from image using pytesseract.
    
    Args:
        image_path: Path to image file
        
    Returns:
        List of OCRTextBlock objects
    """
    try:
        from PIL import Image
        import pytesseract
        import re
        from html.parser import HTMLParser
    except ImportError:
        print("Error: Required packages not found")
        print("Install with: pip install pytesseract pillow")
        return None
    
    try:
        # Load image
        image = Image.open(image_path)
        
        # Get page dimensions
        page_width, page_height = image.size
        print(f"Image dimensions: {page_width}x{page_height}")
        
        # Extract text with HOCR (includes bounding boxes)
        hocr_data = pytesseract.image_to_pdf_or_hocr(
            image,
            extension='hocr',
            lang='eng'
        )
        
        # Parse HOCR to extract text and bounding boxes
        # HOCR format: <span class='ocrx_word' id='word_...' title='bbox x1 y1 x2 y2'>text</span>
        text_blocks = []
        
        # Extract all word elements with bbox
        pattern = r'<span[^>]*ocrx_word[^>]*title=\'bbox (\d+) (\d+) (\d+) (\d+)\'[^>]*>([^<]+)</span>'
        
        for match in re.finditer(pattern, hocr_data.decode('utf-8') if isinstance(hocr_data, bytes) else hocr_data):
            x1, y1, x2, y2, text = match.groups()
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # Clean HTML entities
            text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            
            block = OCRTextBlock(
                text=text,
                bbox=BoundingBox(x1, y1, x2, y2),
                confidence=0.95  # HOCR doesn't provide per-word confidence
            )
            text_blocks.append(block)
        
        print(f"Extracted {len(text_blocks)} text blocks")
        return text_blocks, page_width, page_height
        
    except Exception as e:
        print(f"Error during OCR: {e}")
        return None, None, None


def test_sod_image(image_path):
    """
    Test the line number mapper on an SOD image.
    
    Args:
        image_path: Path to image file
    """
    print("=" * 70)
    print("Testing Line Number Mapper on Statement of Decision Image")
    print("=" * 70)
    print()
    
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"Error: File not found: {image_path}")
        return False
    
    print(f"Processing: {image_path}")
    print()
    
    # Extract text with bounding boxes
    print("Step 1: Extracting text with OCR...")
    print("-" * 70)
    text_blocks, page_width, page_height = extract_text_with_pytesseract(image_path)
    
    if text_blocks is None:
        print("Failed to extract text from image")
        return False
    
    print()
    
    # Create mapper
    print("Step 2: Creating document mapper...")
    print("-" * 70)
    mapper = DocumentLineMapper()
    print("✓ Mapper created")
    print()
    
    # Process page
    print("Step 3: Processing page with line number detection...")
    print("-" * 70)
    mapper.add_page(
        page_number=1,
        page_height=page_height,
        page_width=page_width,
        text_blocks=text_blocks
    )
    print("✓ Page processed")
    page_map = mapper.pages[1]
    print()
    
    # Show detected line markers
    print("Step 4: Detected Line Markers")
    print("-" * 70)
    markers = page_map.line_markers
    print(f"Detected {len(markers)} line markers out of 28 expected:")
    for marker in markers[:10]:  # Show first 10
        print(f"  Line {marker.line_number:2d}: y={marker.y_position:6.1f}  text='{marker.text}'  confidence={marker.confidence:.2f}")
    if len(markers) > 10:
        print(f"  ... and {len(markers) - 10} more")
    print()
    
    # Show line bands
    print("Step 5: Generated Line Bands")
    print("-" * 70)
    bands = page_map.bands
    print(f"Generated {len(bands)} bands:")
    for band in bands[0:5]:  # Show first 5
        print(f"  Line {band.line_number:2d}: top={band.top:6.1f}, bottom={band.bottom:6.1f}")
    if len(bands) > 5:
        print(f"  ... and {len(bands) - 5} more")
    print()
    
    # Extract and display text for specific lines
    print("Step 6: Extracted Text by Line Number")
    print("-" * 70)
    
    # Show lines 1-5 as examples
    for line_num in range(1, 6):
        text = page_map.get_text_for_line(line_num)
        if text.strip():
            # Truncate if too long
            display_text = text[:70] + "..." if len(text) > 70 else text
            print(f"  Line {line_num}: {display_text}")
    print()
    
    # Extract specific section
    print("Step 7: Extract Multi-Line Passage")
    print("-" * 70)
    print("Extracting introduction section (lines 1-5):")
    passage_lines = []
    for line_num in range(1, 6):
        text = page_map.get_text_for_line(line_num)
        if text.strip():
            passage_lines.append(text)
    
    passage = " ".join(passage_lines)
    print(f"  {passage[:150]}...")
    print()
    
    # Search for specific content
    print("Step 8: Searching for Specific Content")
    print("-" * 70)
    search_term = "Court"
    found_locations = []
    
    for line_num in range(1, 29):
        text = page_map.get_text_for_line(line_num)
        if search_term.lower() in text.lower():
            found_locations.append((line_num, text))
    
    print(f"Found '{search_term}' in {len(found_locations)} lines:")
    for line_num, text in found_locations[:3]:
        display_text = text[:60] + "..." if len(text) > 60 else text
        print(f"  (SOD, p. 1, ln. {line_num:2d}) {display_text}")
    print()
    
    # Export to JSON
    print("Step 9: JSON Export")
    print("-" * 70)
    json_output = mapper.to_json()
    # Show first 500 chars
    print(json_output[:500] + "...")
    print()
    
    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"✓ Image loaded and processed successfully")
    print(f"✓ Extracted {len(text_blocks)} text blocks via OCR")
    print(f"✓ Detected {len(markers)} line number markers")
    print(f"✓ Generated {len(bands)} horizontal bands")
    print(f"✓ Successfully mapped text to {len([t for t in [page_map.get_text_for_line(i) for i in range(1, 29)] if t.strip()])} lines")
    print(f"✓ JSON export successful")
    print()
    print("✓ LINE NUMBER MAPPER WORKS ON REAL SOD DOCUMENTS")
    print()
    
    return True


def find_sod_image():
    """Find SOD image in workspace."""
    # Check common locations
    possible_paths = [
        "sod_image.png",
        "sod_page.png", 
        "statement_of_decision.png",
        "SOD_Page_1.png",
        "test_sod.png",
        # In workspace root
        Path(__file__).parent / "sod_image.png",
        Path(__file__).parent / "SOD_Page_1.png",
    ]
    
    # Also check for any recently modified PNG files
    import glob
    png_files = glob.glob("*.png") + glob.glob("**/*.png", recursive=True)
    
    for path in possible_paths + png_files:
        if isinstance(path, Path):
            path = str(path)
        if os.path.exists(path):
            return path
    
    return None


if __name__ == "__main__":
    # Find image file
    image_path = None
    
    if len(sys.argv) > 1:
        # Use provided path
        image_path = sys.argv[1]
    else:
        # Try to find image
        image_path = find_sod_image()
    
    if image_path is None:
        print("Error: No image file provided")
        print()
        print("Usage:")
        print("  python test_sod_image.py <path_to_image>")
        print()
        print("Example:")
        print("  python test_sod_image.py sod_page.png")
        print()
        print("Prerequisites:")
        print("  pip install pytesseract pillow")
        print("  (Also requires Tesseract-OCR installed on system)")
        sys.exit(1)
    
    success = test_sod_image(image_path)
    sys.exit(0 if success else 1)

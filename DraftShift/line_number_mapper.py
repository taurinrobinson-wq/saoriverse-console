"""
Line Number Mapping Module for DraftShift
==========================================

Maps OCR'd text blocks to printed line numbers (1-28) on court documents.

Detects line number positions, creates horizontal bands, and assigns text
based on geometric positioning. Returns structured page/line mappings.

Author: DraftShift Architecture
Purpose: Enable precise citation of court documents with line numbers
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import json


@dataclass
class BoundingBox:
    """Represents a rectangular region on a page."""
    x1: float
    y1: float
    x2: float
    y2: float
    
    @property
    def width(self) -> float:
        return self.x2 - self.x1
    
    @property
    def height(self) -> float:
        return self.y2 - self.y1
    
    @property
    def y_center(self) -> float:
        """Vertical midpoint of the bounding box."""
        return (self.y1 + self.y2) / 2
    
    @property
    def x_center(self) -> float:
        """Horizontal midpoint of the bounding box."""
        return (self.x1 + self.x2) / 2


@dataclass
class OCRTextBlock:
    """Represents a text block extracted by OCR with its position."""
    text: str
    bbox: BoundingBox
    confidence: float = 1.0
    
    def __repr__(self):
        return f"OCRTextBlock(text='{self.text[:30]}...', y_center={self.bbox.y_center})"


@dataclass
class LineNumberMarker:
    """Represents a detected printed line number on the page."""
    line_number: int
    y_position: float
    confidence: float = 1.0


@dataclass
class LineBand:
    """Represents a horizontal band corresponding to a line number."""
    line_number: int
    y_top: float
    y_bottom: float
    
    def contains_point(self, y: float) -> bool:
        """Check if a y-coordinate falls within this band."""
        return self.y_top <= y <= self.y_bottom
    
    def distance_to_point(self, y: float) -> float:
        """Calculate distance from a y-coordinate to this band's center."""
        band_center = (self.y_top + self.y_bottom) / 2
        return abs(y - band_center)


class LineNumberDetector:
    """
    Detects printed line numbers (1-28) on a document page.
    
    Strategies:
    1. Direct OCR detection: Look for text that is exactly "1"-"28"
    2. Position-based detection: Filter by left margin x-coordinate
    3. Interpolation: Fill gaps using consistent vertical spacing
    """
    
    def __init__(self, page_height: float, left_margin_threshold: float = 50):
        """
        Args:
            page_height: Height of the page in pixels/points
            left_margin_threshold: Maximum x-coordinate for left-margin numbers
        """
        self.page_height = page_height
        self.left_margin_threshold = left_margin_threshold
    
    def detect(self, text_blocks: List[OCRTextBlock]) -> List[LineNumberMarker]:
        """
        Detect printed line numbers from OCR text blocks.
        
        Args:
            text_blocks: List of OCR'd text blocks with positions
            
        Returns:
            List of detected line number markers, sorted by position
        """
        markers = []
        
        for block in text_blocks:
            # Check if this block is a numeric line number
            try:
                line_num = int(block.text.strip())
            except (ValueError, AttributeError):
                continue
            
            # Must be in valid range (1-28)
            if not (1 <= line_num <= 28):
                continue
            
            # Must be in left margin
            if block.bbox.x_center > self.left_margin_threshold:
                continue
            
            # Record this marker
            markers.append(LineNumberMarker(
                line_number=line_num,
                y_position=block.bbox.y_center,
                confidence=block.confidence
            ))
        
        # Sort by line number
        markers.sort(key=lambda m: m.line_number)
        
        return markers
    
    def interpolate_missing(self, markers: List[LineNumberMarker]) -> List[LineNumberMarker]:
        """
        Fill in any missing line numbers using consistent spacing.
        
        If line numbers 1, 2, 3 are detected, but 5-27 are missing,
        calculate spacing from detected numbers and interpolate.
        
        Args:
            markers: Detected markers (may have gaps)
            
        Returns:
            Complete list of 28 line markers with interpolated positions
        """
        if not markers or len(markers) == 28:
            return markers
        
        # Calculate average spacing from consecutive detected numbers
        spacings = []
        for i in range(1, len(markers)):
            spacing = (markers[i].y_position - markers[i-1].y_position) / \
                     (markers[i].line_number - markers[i-1].line_number)
            spacings.append(spacing)
        
        avg_spacing = sum(spacings) / len(spacings) if spacings else self.page_height / 28
        
        # Build complete list
        complete_markers = []
        
        for line_num in range(1, 29):
            # Check if we have a detected marker for this line
            detected = next((m for m in markers if m.line_number == line_num), None)
            
            if detected:
                complete_markers.append(detected)
            else:
                # Interpolate based on the first detected marker
                if markers:
                    first = markers[0]
                    offset = (line_num - first.line_number) * avg_spacing
                    interpolated_y = first.y_position + offset
                else:
                    # Fallback: distribute evenly
                    interpolated_y = (line_num - 1) * (self.page_height / 28)
                
                complete_markers.append(LineNumberMarker(
                    line_number=line_num,
                    y_position=interpolated_y,
                    confidence=0.0  # Mark as interpolated
                ))
        
        return complete_markers


class LineBandGenerator:
    """
    Creates horizontal bands for each line number.
    
    Each band spans from the midpoint between consecutive line numbers,
    allowing flexible assignment of text to lines.
    """
    
    @staticmethod
    def generate(markers: List[LineNumberMarker]) -> List[LineBand]:
        """
        Create line bands from detected/interpolated line number positions.
        
        Args:
            markers: List of line number markers (should be complete 1-28)
            
        Returns:
            List of 28 LineBand objects
        """
        markers = sorted(markers, key=lambda m: m.line_number)
        bands = []
        
        for i, marker in enumerate(markers):
            # Top boundary: halfway between this and previous marker
            if i > 0:
                y_top = (markers[i-1].y_position + marker.y_position) / 2
            else:
                # First line: starts at calculated top
                spacing = markers[1].y_position - marker.y_position if len(markers) > 1 else 1
                y_top = marker.y_position - (spacing / 2)
            
            # Bottom boundary: halfway between this and next marker
            if i < len(markers) - 1:
                y_bottom = (marker.y_position + markers[i+1].y_position) / 2
            else:
                # Last line: ends at calculated bottom
                spacing = marker.y_position - markers[i-1].y_position if i > 0 else 1
                y_bottom = marker.y_position + (spacing / 2)
            
            bands.append(LineBand(
                line_number=marker.line_number,
                y_top=y_top,
                y_bottom=y_bottom
            ))
        
        return bands


class TextToLineAssigner:
    """
    Assigns OCR text blocks to line numbers based on geometric positioning.
    
    Rules:
    1. If text's y-center falls within a band, assign to that line
    2. If text overlaps multiple bands, assign to closest band
    3. Text on band boundary favors the higher (earlier) line
    """
    
    def __init__(self, bands: List[LineBand]):
        """
        Args:
            bands: List of line bands (typically 28)
        """
        self.bands = sorted(bands, key=lambda b: b.line_number)
    
    def assign(self, text_blocks: List[OCRTextBlock]) -> Dict[int, List[OCRTextBlock]]:
        """
        Assign text blocks to line numbers.
        
        Args:
            text_blocks: OCR'd text blocks with bounding boxes
            
        Returns:
            Dictionary mapping line number -> list of text blocks
        """
        assignments = {band.line_number: [] for band in self.bands}
        
        for block in text_blocks:
            line_num = self._find_best_line(block)
            if line_num:
                assignments[line_num].append(block)
        
        return assignments
    
    def _find_best_line(self, block: OCRTextBlock) -> Optional[int]:
        """
        Find the best-matching line number for a text block.
        
        Args:
            block: Text block with bounding box
            
        Returns:
            Line number (1-28) or None if no match
        """
        y_center = block.bbox.y_center
        
        # Strategy 1: Direct containment
        for band in self.bands:
            if band.contains_point(y_center):
                return band.line_number
        
        # Strategy 2: Closest band (fallback)
        closest_band = min(self.bands, key=lambda b: b.distance_to_point(y_center))
        return closest_band.line_number if closest_band else None
    
    def assign_with_overlaps(self, text_blocks: List[OCRTextBlock]) -> Dict[int, List[OCRTextBlock]]:
        """
        Advanced: Handle text blocks that span multiple lines.
        
        For tall text blocks, assign to the line containing the top of the block,
        then optionally flag for manual review.
        
        Args:
            text_blocks: OCR'd text blocks
            
        Returns:
            Dictionary mapping line number -> list of text blocks
        """
        assignments = {band.line_number: [] for band in self.bands}
        
        for block in text_blocks:
            # Use top of block instead of center for tall blocks
            # This errs on the side of "earlier line" (inclusion)
            y_ref = block.bbox.y1
            
            # Find best matching band
            matching_bands = [b for b in self.bands if b.contains_point(y_ref)]
            
            if matching_bands:
                # Use the earliest (highest) matching band
                line_num = min(matching_bands, key=lambda b: b.line_number).line_number
            else:
                # Fallback to closest
                line_num = min(self.bands, key=lambda b: b.distance_to_point(y_ref)).line_number
            
            assignments[line_num].append(block)
        
        return assignments


class PageLineMap:
    """
    Complete mapping of a single page: line number -> extracted text.
    """
    
    def __init__(self, page_number: int, height: float, width: float):
        self.page_number = page_number
        self.height = height
        self.width = width
        self.lines: Dict[int, str] = {i: "" for i in range(1, 29)}
        self.text_blocks: Dict[int, List[OCRTextBlock]] = {i: [] for i in range(1, 29)}
        self.markers: List[LineNumberMarker] = []
        self.bands: List[LineBand] = []
    
    def populate(self, text_blocks: List[OCRTextBlock]):
        """
        Full pipeline: detect line numbers, create bands, assign text.
        
        Args:
            text_blocks: All OCR'd text blocks from the page
        """
        # Step 1: Detect line number markers
        detector = LineNumberDetector(
            page_height=self.height,
            left_margin_threshold=self.width * 0.15
        )
        self.markers = detector.detect(text_blocks)
        self.markers = detector.interpolate_missing(self.markers)
        
        # Step 2: Generate line bands
        self.bands = LineBandGenerator.generate(self.markers)
        
        # Step 3: Assign text to lines
        assigner = TextToLineAssigner(self.bands)
        self.text_blocks = assigner.assign_with_overlaps(text_blocks)
        
        # Step 4: Convert blocks to concatenated text
        for line_num in range(1, 29):
            blocks = self.text_blocks[line_num]
            texts = [b.text for b in blocks]
            self.lines[line_num] = " ".join(texts)
    
    def to_dict(self) -> Dict:
        """Export as structured dictionary."""
        return {
            "page": self.page_number,
            "height": self.height,
            "width": self.width,
            "lines": self.lines,
            "metadata": {
                "line_markers_detected": len([m for m in self.markers if m.confidence > 0]),
                "line_markers_interpolated": len([m for m in self.markers if m.confidence == 0]),
            }
        }
    
    def to_json(self) -> str:
        """Export as JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def to_citation_format(self) -> str:
        """
        Export in citation-ready format for legal documents.
        
        Example:
            Page 12, Line 5: "Pak purchased leads..."
        """
        lines = [f"PAGE {self.page_number}"]
        lines.append("=" * 50)
        
        for line_num in range(1, 29):
            text = self.lines[line_num]
            if text.strip():
                lines.append(f"Ln. {line_num:2d}: {text}")
        
        return "\n".join(lines)


class DocumentLineMapper:
    """
    Maps an entire document (multiple pages) to line numbers.
    """
    
    def __init__(self):
        self.pages: Dict[int, PageLineMap] = {}
    
    def add_page(self, page_number: int, height: float, width: float, 
                 text_blocks: List[OCRTextBlock]):
        """
        Process and add a page to the document map.
        
        Args:
            page_number: Page number (1-indexed)
            height: Page height
            width: Page width
            text_blocks: All OCR'd text blocks on this page
        """
        page_map = PageLineMap(page_number, height, width)
        page_map.populate(text_blocks)
        self.pages[page_number] = page_map
    
    def get_text_at_location(self, page: int, line: int) -> str:
        """
        Retrieve text at a specific page/line location.
        
        Args:
            page: Page number
            line: Line number (1-28)
            
        Returns:
            Text at that location, or empty string if not found
        """
        if page not in self.pages:
            return ""
        
        return self.pages[page].lines.get(line, "")
    
    def to_dict(self) -> Dict:
        """Export entire document map."""
        return {
            "total_pages": len(self.pages),
            "pages": {
                page_num: page_map.to_dict()
                for page_num, page_map in sorted(self.pages.items())
            }
        }
    
    def to_json(self) -> str:
        """Export as JSON."""
        return json.dumps(self.to_dict(), indent=2)


if __name__ == "__main__":
    # Example usage
    print("DraftShift Line Number Mapping Module")
    print("=" * 50)
    print()
    print("This module provides:")
    print("  • LineNumberDetector: Finds printed line numbers 1-28")
    print("  • LineBandGenerator: Creates horizontal bands for each line")
    print("  • TextToLineAssigner: Maps OCR text to line numbers")
    print("  • PageLineMap: Complete page-level mapping")
    print("  • DocumentLineMapper: Multi-page document mapping")
    print()
    print("See documentation for usage examples.")

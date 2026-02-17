"""
DraftShift Line Number Mapper - Integration Examples
=====================================================

Shows how to integrate the line number mapping module with common OCR engines
and how to use it for real-world document processing.
"""

from line_number_mapper import (
    OCRTextBlock, BoundingBox, DocumentLineMapper
)
from typing import List, Dict, Tuple
import json


class OCREngineAdapter:
    """
    Adapters for converting different OCR engine outputs to DraftShift format.
    
    Supports: Tesseract, AWS Textract, Google Vision, Azure OCR
    """
    
    @staticmethod
    def from_tesseract_hocr(hocr_data: str) -> List[OCRTextBlock]:
        """
        Convert Tesseract HOCR output to OCR text blocks.
        
        HOCR provides bounding boxes and confidence scores.
        
        Args:
            hocr_data: HOCR XML string
            
        Returns:
            List of OCRTextBlock objects
        """
        # This would parse HOCR XML
        # Example: extract bbox and confidence from bbox data
        # bbox '123 456 789 678' -> BoundingBox(123, 456, 789, 678)
        pass
    
    @staticmethod
    def from_textract_response(textract_json: Dict) -> List[OCRTextBlock]:
        """
        Convert AWS Textract JSON response to OCR text blocks.
        
        Args:
            textract_json: Parsed Textract JSON response
            
        Returns:
            List of OCRTextBlock objects
        """
        text_blocks = []
        
        for block in textract_json.get("Blocks", []):
            if block["BlockType"] == "LINE":
                geometry = block.get("Geometry", {})
                bbox_data = geometry.get("BoundingBox", {})
                
                # Textract uses normalized coordinates (0-1)
                # You'd need to denormalize using page dimensions
                text_blocks.append(OCRTextBlock(
                    text=block.get("Text", ""),
                    bbox=BoundingBox(
                        x1=bbox_data.get("Left", 0),
                        y1=bbox_data.get("Top", 0),
                        x2=bbox_data.get("Left", 0) + bbox_data.get("Width", 0),
                        y2=bbox_data.get("Top", 0) + bbox_data.get("Height", 0)
                    ),
                    confidence=block.get("Confidence", 100) / 100
                ))
        
        return text_blocks
    
    @staticmethod
    def from_google_vision(vision_response: Dict) -> List[OCRTextBlock]:
        """
        Convert Google Cloud Vision API response to OCR text blocks.
        
        Args:
            vision_response: Parsed Vision API response
            
        Returns:
            List of OCRTextBlock objects
        """
        text_blocks = []
        
        for page in vision_response.get("fullTextAnnotation", {}).get("pages", []):
            for block in page.get("blocks", []):
                for paragraph in block.get("paragraphs", []):
                    for word in paragraph.get("words", []):
                        # Combine letters into word
                        text = "".join(s.get("text", "") for s in word.get("symbols", []))
                        
                        # Extract bounding box
                        bbox_vertices = word.get("boundingBox", {}).get("vertices", [])
                        if len(bbox_vertices) >= 2:
                            text_blocks.append(OCRTextBlock(
                                text=text,
                                bbox=BoundingBox(
                                    x1=bbox_vertices[0].get("x", 0),
                                    y1=bbox_vertices[0].get("y", 0),
                                    x2=bbox_vertices[2].get("x", 0),
                                    y2=bbox_vertices[2].get("y", 0)
                                ),
                                confidence=word.get("confidence", 1.0)
                            ))
        
        return text_blocks


class DocumentProcessor:
    """
    End-to-end document processing pipeline for DraftShift.
    """
    
    def __init__(self):
        self.mapper = DocumentLineMapper()
    
    def process_ocr_output(self, ocr_results: List[Dict]) -> None:
        """
        Process OCR results for a multi-page document.
        
        Args:
            ocr_results: List of page results, each with page number and text blocks
            
        Example:
            ocr_results = [
                {
                    "page": 1,
                    "height": 1000,
                    "width": 800,
                    "text_blocks": [...]
                },
                ...
            ]
        """
        for page_result in ocr_results:
            page_num = page_result["page"]
            height = page_result["height"]
            width = page_result["width"]
            text_blocks = page_result["text_blocks"]
            
            self.mapper.add_page(page_num, height, width, text_blocks)
    
    def get_citation(self, page: int, line: int) -> str:
        """
        Retrieve text for a specific citation location.
        
        Args:
            page: Page number
            line: Line number (1-28)
            
        Returns:
            Text at location
            
        Example:
            text = processor.get_citation(5, 15)
            # Returns text from page 5, line 15
        """
        return self.mapper.get_text_at_location(page, line)
    
    def export_for_motion(self, output_format: str = "json") -> str:
        """
        Export line-number mapping in format suitable for motion drafting.
        
        Args:
            output_format: "json" or "markdown" or "plaintext"
            
        Returns:
            Formatted output
        """
        if output_format == "json":
            return self.mapper.to_json()
        elif output_format == "plaintext":
            lines = []
            for page_num in sorted(self.mapper.pages.keys()):
                page_map = self.mapper.pages[page_num]
                lines.append(page_map.to_citation_format())
                lines.append("")
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported format: {output_format}")


class CitationHelper:
    """
    Utilities for working with citations in legal documents.
    """
    
    @staticmethod
    def format_citation(page: int, line: int, text: str, doc_name: str = "SOD") -> str:
        """
        Format a citation for use in legal motions.
        
        Args:
            page: Page number
            line: Line number
            text: Text to cite
            doc_name: Document name (default "SOD")
            
        Returns:
            Formatted citation
            
        Example:
            citation = CitationHelper.format_citation(
                page=12,
                line=15,
                text="The court finds that Brown was aware...",
                doc_name="Statement of Decision"
            )
            # Returns: "(Statement of Decision, p. 12, ln. 15) 'The court finds...'"
        """
        # Truncate if too long
        if len(text) > 100:
            text = text[:100] + "..."
        
        return f"({doc_name}, p. {page}, ln. {line}) \"{text}\""
    
    @staticmethod
    def extract_passage(mapper: DocumentLineMapper, 
                       page: int, 
                       start_line: int, 
                       end_line: int) -> str:
        """
        Extract a multi-line passage from a document.
        
        Args:
            mapper: DocumentLineMapper instance
            page: Page number
            start_line: Starting line number
            end_line: Ending line number
            
        Returns:
            Concatenated text from all lines in range
            
        Example:
            passage = CitationHelper.extract_passage(mapper, 5, 10, 20)
            # Returns all text from page 5, lines 10-20
        """
        lines = []
        for line_num in range(start_line, end_line + 1):
            text = mapper.get_text_at_location(page, line_num)
            if text.strip():
                lines.append(text)
        
        return " ".join(lines)


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

def example_usage():
    """
    Example: Process a Statement of Decision and extract citations.
    """
    
    # Step 1: Create a processor
    processor = DocumentProcessor()
    
    # Step 2: Prepare OCR results
    # In real usage, you'd get this from Tesseract, Textract, Vision, etc.
    ocr_results = [
        {
            "page": 1,
            "height": 1000,
            "width": 800,
            "text_blocks": [
                OCRTextBlock(
                    text="I.",
                    bbox=BoundingBox(50, 100, 70, 120),
                    confidence=0.99
                ),
                OCRTextBlock(
                    text="INTRODUCTION",
                    bbox=BoundingBox(80, 100, 180, 120),
                    confidence=0.99
                ),
                OCRTextBlock(
                    text="In this document the Court announces...",
                    bbox=BoundingBox(50, 140, 750, 180),
                    confidence=0.95
                ),
                # ... more blocks
            ]
        },
        # ... more pages
    ]
    
    # Step 3: Process
    processor.process_ocr_output(ocr_results)
    
    # Step 4: Extract citations
    page_1_line_5_text = processor.get_citation(page=1, line=5)
    print(f"Page 1, Line 5: {page_1_line_5_text}")
    
    # Step 5: Format for motion
    citation = CitationHelper.format_citation(
        page=1,
        line=5,
        text=page_1_line_5_text,
        doc_name="Statement of Decision"
    )
    print(f"\nFormatted citation:\n{citation}")
    
    # Step 6: Export
    json_output = processor.export_for_motion("json")
    print(f"\nJSON export:\n{json_output}")


if __name__ == "__main__":
    print("DraftShift Line Number Mapper - Integration Examples")
    print("=" * 50)
    print()
    print("This module provides:")
    print("  • OCREngineAdapter: Convert Textract, Vision, Tesseract output")
    print("  • DocumentProcessor: End-to-end processing pipeline")
    print("  • CitationHelper: Format and extract citations")
    print()
    print("See example_usage() for implementation details.")

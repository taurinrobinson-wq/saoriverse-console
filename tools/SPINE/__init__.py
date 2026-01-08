"""
SPINE v2 - Semantic Parsing & Ingestion Normalization Engine

Cook IVC Filter Settlement Case Document Processing System
"""

__version__ = "2.0.0"
__author__ = "Legal Document Processing Team"

# Core extraction functions
from .spine_parser import (
    extract_text,
    split_cases,
    extract_plaintiff,
    extract_case_number,
    detect_brand,
    extract_amounts,
    extract_all_injuries,
    build_summary,
    process_pdf,
)

# Text rebuilders (submodule)
from . import rebuild

# Debug utilities (submodule)
from . import debug

# Test suite (submodule)
from . import tests

__all__ = [
    'extract_text',
    'split_cases',
    'extract_plaintiff',
    'extract_case_number',
    'detect_brand',
    'extract_amounts',
    'extract_all_injuries',
    'build_summary',
    'process_pdf',
    'rebuild',
    'debug',
    'tests',
]

__all__ = [
    "extract_text",
    "split_cases",
    "extract_plaintiff",
    "extract_case_number",
    "detect_brand",
    "extract_amounts",
    "extract_all_injuries",
    "build_summary",
    "process_pdf",
]

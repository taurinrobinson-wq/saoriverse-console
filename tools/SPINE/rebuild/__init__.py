"""Text reconstruction preprocessors for fragmented PDF text.

This module provides functions to rebuild text fragments that are broken
across lines during PDF extraction (multi-line names, addresses, case numbers, etc.)
"""

from .caption import rebuild_caption_lines
from .case_number import rebuild_case_numbers
from .addresses import rebuild_addresses
from .medical_history import rebuild_medical_history

__all__ = [
    'rebuild_caption_lines',
    'rebuild_case_numbers',
    'rebuild_addresses',
    'rebuild_medical_history',
]

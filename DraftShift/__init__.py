"""
DraftShift — Litigation Document Automation Platform

AI-powered platform for generating California civil pleadings,
motions, oppositions, replies, and declarations with proper formatting,
citation rules, and legal analysis.

Submodules:
    - pleadings: Core pleading classes (Motion, Opposition, Reply, Declaration)
    - formats: YAML configuration files for formatting and citation rules
    - tests: Test fixtures and test suite
"""

__version__ = "0.1.0"
__author__ = "Taurin Robinson"
__license__ = "Proprietary"

# Import pleadings module for direct access
try:
    from .pleadings import (
        BaseDocument,
        DocumentBuilder,
        Motion,
        Opposition,
        Reply,
        Declaration,
        PleadingFactory,
    )
    __all__ = [
        "BaseDocument",
        "DocumentBuilder",
        "Motion",
        "Opposition",
        "Reply",
        "Declaration",
        "PleadingFactory",
    ]
except ImportError:
    __all__ = []

# Make submodules available for explicit import
from . import pleadings, formats, tests

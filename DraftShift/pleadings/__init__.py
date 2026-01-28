"""
DraftShift Pleadings — California Civil Pleading Generator

Core classes and utilities for building California-compliant pleadings.
"""

from .base import BaseDocument
from .builder import DocumentBuilder
from .motion import Motion
from .opposition import Opposition
from .reply import Reply
from .declaration import Declaration
from .pleading_factory import PleadingFactory

__all__ = [
    "BaseDocument",
    "DocumentBuilder",
    "Motion",
    "Opposition",
    "Reply",
    "Declaration",
    "PleadingFactory",
]

__version__ = "0.1.0"

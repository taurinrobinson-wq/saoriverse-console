"""
LimbicAI: Interactive emotional response analyzer grounded in affective neuroscience.

This package provides tools to analyze scenarios for emotional/limbic system activation
and provide evidence-based guidance.
"""

from limbic_ai.models import EmotionalFeatures, LimbicState, LimbicAnalysis
from limbic_ai.analyzer import LimbicAnalyzer
from limbic_ai.nlp_parser import EmotionalFeatureExtractor
from limbic_ai.agent_core import InternalMind, MindState, MindTurn, Goal, get_or_create_mind, reset_mind

__version__ = "0.1.0"
__all__ = [
    "EmotionalFeatures",
    "LimbicState", 
    "LimbicAnalysis",
    "LimbicAnalyzer",
    "EmotionalFeatureExtractor",
    "InternalMind",
    "MindState",
    "MindTurn",
    "Goal",
    "get_or_create_mind",
    "reset_mind",
]

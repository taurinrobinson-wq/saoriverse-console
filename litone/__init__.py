"""DraftShift (formerly LiToneCheck) - Legal Tone Analysis and Transformation

This package provides tools for analyzing and transforming the tone of legal
correspondence. It integrates multiple NLP approaches:

- enhanced_affect_parser: Multi-method emotion/affect analysis (NRC, TextBlob, spaCy)
- tone_analysis_composer: Contextual tone analysis and transformation guidance
- tone_signal_parser: Lightweight tone signal detection (α-Ω signals) - 300 lines, no database
- constants: Tone names, signals, and patterns for legal text
- core: Main tone detection and transformation logic

Quick Start:
    from draftshift import core
    analysis = core.detect_tone("This shall be binding.")
    transformed = core.shift_tone(analysis, target_tone=3)  # Friendly

7 Tone Signals Detected (α-Ω):
    α: Formality/Professional
    β: Boundary/Protective  
    γ: Longing/Understanding
    θ: Concern/Cautionary
    λ: Confidence/Assertiveness
    ε: Clarity/Reasoning
    Ω: Recognition/Acknowledgment

Documentation:
    - Docs/SETUP_AND_VERIFICATION.md     (Quick start & test results)
    - Docs/INTEGRATION_GUIDE.md          (Detailed usage guide)
    - Docs/MODULE_INTEGRATION_SUMMARY.md (Technical architecture)
    - Docs/PACKAGE_ORGANIZATION.md       (Folder structure overview)
    
Tests:
    Run comprehensive test suite with:
    py -3.12 -c "import sys; sys.path.insert(0, '.'); from litone.Tests.test_litone_integration import *"
    
    Current status: 6 test categories - all ✅ passing
"""

"""Backward compatibility shim: re-export DraftShift implementation.

This file allows `import litone` to continue working while the
implementation now lives in the `draftshift` package.
"""

try:
    from draftshift import (
        constants as constants,
        enhanced_affect_parser as enhanced_affect_parser,
        tone_analysis_composer as tone_analysis_composer,
        tone_signal_parser as tone_signal_parser,
        core as core,
    )
    __all__ = [
        "constants",
        "enhanced_affect_parser",
        "tone_analysis_composer",
        "tone_signal_parser",
        "core",
    ]
except Exception:
    # If draftshift isn't importable, keep empty but allow import
    __all__ = []

__version__ = "1.1.0"
__author__ = "DraftShift Migration Shim"

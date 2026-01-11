#!/usr/bin/env python3
"""
Validation script to verify all components are properly installed and configured.
Run this after installation to ensure everything works.
"""

import sys
import os
from pathlib import Path

def check_module(module_name, package_name=None, optional=False):
    """Check if a module can be imported."""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        status = "✓"
        level = "SUCCESS"
    except ImportError as e:
        if optional:
            status = "⚠"
            level = "WARNING"
        else:
            status = "✗"
            level = "ERROR"
        print(f"[{status}] {level:8} {package_name}: {e}")
        return not (not optional)
    
    print(f"[✓] OK       {package_name}")
    return True

def check_file(filepath, description):
    """Check if a file exists."""
    path = Path(filepath)
    if path.exists():
        print(f"[✓] OK       {description}")
        return True
    else:
        print(f"[✗] ERROR    {description}: File not found at {filepath}")
        return False

def check_env_var(var_name, optional=False):
    """Check if environment variable is set."""
    value = os.environ.get(var_name)
    if value:
        # Mask sensitive values
        if "KEY" in var_name or "URL" in var_name:
            masked = value[:5] + "..." if len(value) > 8 else value
        else:
            masked = value
        print(f"[✓] OK       {var_name}: {masked}")
        return True
    elif optional:
        print(f"[⚠] WARNING  {var_name}: Not set (optional)")
        return True
    else:
        print(f"[✗] ERROR    {var_name}: Not configured")
        return False

def main():
    """Run all validation checks."""
    print("=" * 70)
    print("SaoriVerse Console - Installation Validation")
    print("=" * 70)
    
    all_ok = True
    
    # 1. Python version
    print("\n[STEP 1] Python Version")
    print("-" * 70)
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 11):
        print(f"[✓] OK       Python {py_version}")
    else:
        print(f"[✗] ERROR    Python {py_version} (requires 3.11+)")
        all_ok = False
    
    # 2. Core dependencies
    print("\n[STEP 2] Core Dependencies")
    print("-" * 70)
    core_deps = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("requests", "Requests"),
    ]
    for module, name in core_deps:
        if not check_module(module, name):
            all_ok = False
    
    # 3. Speech & Audio
    print("\n[STEP 3] Speech & Audio Processing")
    print("-" * 70)
    audio_deps = [
        ("faster_whisper", "Faster Whisper (STT)"),
        ("pyttsx3", "pyttsx3 (TTS)"),
    ]
    for module, name in audio_deps:
        if not check_module(module, name):
            all_ok = False
    
    # 4. NLP & Affect Detection
    print("\n[STEP 4] NLP & Affect Detection")
    print("-" * 70)
    nlp_deps = [
        ("textblob", "TextBlob", True),
        ("spacy", "SpaCy", True),
        ("nrc", "NRC Lexicon", True),
    ]
    for module, name, optional in nlp_deps:
        if not check_module(module, name, optional=optional):
            if not optional:
                all_ok = False
    
    # 5. Database
    print("\n[STEP 5] Database & Persistence")
    print("-" * 70)
    db_deps = [
        ("supabase", "Supabase Client"),
    ]
    for module, name in db_deps:
        if not check_module(module, name):
            all_ok = False
    
    # 6. File structure
    print("\n[STEP 6] Project Structure")
    print("-" * 70)
    files_to_check = [
        ("firstperson_backend.py", "Backend (firstperson_backend.py)"),
        ("src/emotional_os/tier1_foundation.py", "Tier 1 Foundation"),
        ("src/emotional_os/tier2_aliveness.py", "Tier 2 Aliveness"),
        ("src/emotional_os/tier3_poetic_consciousness.py", "Tier 3 Poetic"),
        ("src/firstperson_integrated_pipeline.py", "Integrated Pipeline"),
        ("src/emotional_os/core/firstperson/affect_parser.py", "Affect Parser"),
    ]
    for filepath, desc in files_to_check:
        if not check_file(filepath, desc):
            all_ok = False
    
    # 7. Environment configuration
    print("\n[STEP 7] Environment Configuration")
    print("-" * 70)
    env_checks = [
        ("SUPABASE_URL", True),
        ("SUPABASE_KEY", True),
        ("OLLAMA_MODEL", True),
    ]
    for var, optional in env_checks:
        if not check_env_var(var, optional=optional):
            if not optional:
                all_ok = False
    
    # 8. Optional components
    print("\n[STEP 8] Optional Components")
    print("-" * 70)
    optional_deps = [
        ("ollama", "Ollama (local LLM)", True),
        ("cv2", "OpenCV (facial detection)", True),
        ("mediapipe", "MediaPipe (face mesh)", True),
        ("librosa", "Librosa (voice analysis)", True),
        ("streamlit", "Streamlit (UI dashboard)", True),
    ]
    for module, name, optional in optional_deps:
        check_module(module, name, optional=optional)
    
    # 9. Summary
    print("\n" + "=" * 70)
    if all_ok:
        print("✓ All required components are installed and configured!")
        print("\nNext steps:")
        print("  1. Download spaCy model: python -m spacy download en_core_web_sm")
        print("  2. Download TextBlob corpora: python -m textblob.download_corpora")
        print("  3. Start backend: python firstperson_backend.py")
        print("  4. Run diagnostics: python diagnose_backend.py")
        print("  5. Start frontend: cd frontend && npm run dev")
        return 0
    else:
        print("✗ Some required components are missing!")
        print("\nRun: pip install -r requirements.txt")
        print("Then: pip install -r requirements-optional.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())

"""
Velinor Game - Root Entry Point
================================
This file serves as the entry point for Streamlit Cloud deployments.
It imports and runs the main game from velinor/velinor_app.py
"""

from velinor_app import main
import sys
from pathlib import Path

# Add velinor directory to path so imports work
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "velinor"))

# Import and run the main app

if __name__ == "__main__":
    main()

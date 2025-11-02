"""Pytest configuration for FirstPerson test suite."""
import sys
import os

# Add project root to path so tests can import modules
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

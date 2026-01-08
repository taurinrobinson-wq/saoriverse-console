#!/usr/bin/env python3
"""
MAIN ENTRY POINT FOR STREAMLIT CLOUD
Authentication System - October 14, 2025
"""

import streamlit as st

# Force immediate display to verify this file is loading
st.write("🚀 MAIN.PY LOADING - Authentication System v2.1")
st.write("📍 Entry point confirmed - Loading authentication...")

try:
    # Import the authentication system
    from auth_emotional_os import main

    st.write("✅ Authentication module imported successfully")

    # Run the main authentication app
    if __name__ == "__main__":
        main()

except ImportError as e:
    st.error(f"❌ Import Error: {e}")
    st.write("Available files in directory:")
    import os

    files = [f for f in os.listdir(".") if f.endswith(".py")]
    st.write(files)

except Exception as e:
    st.error(f"❌ Error loading authentication system: {e}")
    st.write("Falling back to debug mode...")
    st.write("This means the authentication code exists but has an issue.")

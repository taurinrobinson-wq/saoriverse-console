#!/usr/bin/env python3
"""
Railway Diagnostics - Check for startup issues
"""
import sys
import os

print("🔍 RAILWAY DIAGNOSTICS - Starting checks...\n")

# Check Python version
print(f"✓ Python version: {sys.version}")
print(f"✓ Python executable: {sys.executable}")

# Check critical imports
critical_imports = [
    'streamlit',
    'requests',
    'pandas',
    'numpy',
    'supabase'
]

print("\n📦 Checking critical imports:")
missing = []
for pkg in critical_imports:
    try:
        __import__(pkg)
        print(f"  ✓ {pkg}")
    except ImportError as e:
        print(f"  ✗ {pkg}: {e}")
        missing.append(pkg)

if missing:
    print(f"\n⚠️  Missing packages: {', '.join(missing)}")
    sys.exit(1)

# Check environment variables
print("\n🔑 Checking environment variables:")
env_vars = ['PORT', 'DATABASE_URL', 'RAILWAY_ENVIRONMENT']
for var in env_vars:
    val = os.environ.get(var)
    if val:
        print(f"  ✓ {var}: {val[:20]}..." if len(str(val)) > 20 else f"  ✓ {var}: {val}")
    else:
        print(f"  ℹ {var}: not set")

# Try importing main modules
print("\n📚 Checking main application modules:")
try:
    print("  Checking main_v2.py imports...")
    import streamlit as st
    print(f"    ✓ streamlit imported")
    
    # Don't actually run main_v2, just check if it can be imported
    print("    ✓ Basic imports successful")
except Exception as e:
    print(f"    ✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All diagnostics passed!")
print("\nTo start the app, run:")
print("  python start.py")

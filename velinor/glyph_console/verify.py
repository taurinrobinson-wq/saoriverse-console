"""
Glyph Console Verification Script

Verifies that all components are in place and datasets are accessible.
"""

import sys
from pathlib import Path
import pandas as pd

def verify_glyph_console():
    """Verify all Glyph Console components."""
    
    print("=" * 70)
    print("VELINOR GLYPH CONSOLE - VERIFICATION")
    print("=" * 70)
    
    base_path = Path("velinor/glyph_console")
    data_path = Path("velinor/markdowngameinstructions/glyphs")
    
    errors = []
    
    # Check Python files
    print("\n✓ Checking Python modules...")
    required_files = [
        base_path / "__init__.py",
        base_path / "app.py",
        base_path / "utils.py",
        base_path / "README.md",
        base_path / "requirements.txt"
    ]
    
    for f in required_files:
        if f.exists():
            print(f"  ✓ {f.relative_to('.')}")
        else:
            print(f"  ✗ {f.relative_to('.')} [MISSING]")
            errors.append(str(f))
    
    # Check datasets
    print("\n✓ Checking datasets...")
    datasets = {
        "Glyph_Organizer.csv": "Core glyphs",
        "Glyph_Fragments.csv": "Fragments",
        "Glyph_Transcendence.csv": "Fusion glyphs",
        "cipher_seeds.csv": "Cipher seeds"
    }
    
    dataset_info = {}
    for filename, description in datasets.items():
        filepath = data_path / filename
        if filepath.exists():
            df = pd.read_csv(filepath)
            print(f"  ✓ {filename}: {len(df)} rows")
            dataset_info[filename] = len(df)
        else:
            print(f"  ✗ {filename} [MISSING]")
            errors.append(str(filepath))
    
    # Check dependencies
    print("\n✓ Checking Python dependencies...")
    dependencies = ["streamlit", "pandas", "networkx", "plotly"]
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  ✓ {dep}")
        except ImportError:
            print(f"  ✗ {dep} [NOT INSTALLED]")
            errors.append(f"Missing dependency: {dep}")
    
    # Summary
    print("\n" + "=" * 70)
    if errors:
        print("❌ VERIFICATION FAILED")
        print(f"\n{len(errors)} issue(s) found:")
        for error in errors:
            print(f"  • {error}")
        print("\nTo fix:")
        print("  1. Verify CSV files in: velinor/markdowngameinstructions/glyphs/")
        print("  2. Install dependencies: pip install -r velinor/glyph_console/requirements.txt")
        return False
    else:
        print("✅ VERIFICATION PASSED")
        print(f"\nDatasets loaded:")
        for name, count in dataset_info.items():
            print(f"  • {name}: {count}")
        print(f"\nTotal glyph data points: {sum(dataset_info.values())}")
        print("\n📖 Ready to run:")
        print("  streamlit run velinor/glyph_console/app.py")
        print("\n🔗 Open at: http://localhost:8501")
        return True


if __name__ == "__main__":
    success = verify_glyph_console()
    sys.exit(0 if success else 1)

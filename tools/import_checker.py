"""Verify all core imports work correctly."""

import sys
import os

def test_imports():
    """Test that all core imports work."""
    print("\nTesting core imports...")
    
    all_pass = True
    tests = [
        ("src.response_generator", "process_user_input"),
        ("src.signal_parser", "parse_input"),
        ("src.enhanced_response_composer", "DynamicResponseComposer"),
    ]
    
    for module_name, class_or_func in tests:
        try:
            module = __import__(module_name, fromlist=[class_or_func])
            attr = getattr(module, class_or_func, None)
            if attr:
                print("  OK: {}.{}".format(module_name, class_or_func))
            else:
                print("  WARNING: {}.{} not found".format(module_name, class_or_func))
                all_pass = False
        except Exception as e:
            print("  FAIL: {}.{}: {}".format(module_name, class_or_func, str(e)))
            all_pass = False
    
    if all_pass:
        print("\nAll imports successful!\n")
        return True
    else:
        print("\nSome imports failed\n")
        return False

if __name__ == "__main__":
    # Add project root to path
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root)
    
    success = test_imports()
    sys.exit(0 if success else 1)

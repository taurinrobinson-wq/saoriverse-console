#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), '.streamlit'))
print('Python executable:', sys.executable)
print('Python version:', sys.version)
try:
    from pre_run_hook import ensure_spacy_model
except Exception as e:
    print('Failed to import pre_run_hook:', e)
    # Fallback: try direct spacy check
    try:
        import spacy
        try:
            spacy.load('en_core_web_sm')
            print('spaCy model already installed and loads successfully')
            sys.exit(0)
        except Exception as e2:
            print('spaCy model missing or failed to load:', e2)
            import subprocess
            subprocess.check_call([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'])
            print('spaCy model downloaded')
            sys.exit(0)
    except Exception as e3:
        print('spaCy import failed:', e3)
        sys.exit(2)

# Use the hook to ensure model
ok = ensure_spacy_model()
print('ensure_spacy_model returned:', ok)
if ok:
    print('spaCy model ready')
    sys.exit(0)
else:
    print('spaCy model not ready; app will use blank pipeline')
    sys.exit(1)

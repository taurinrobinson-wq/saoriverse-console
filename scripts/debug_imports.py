"""Diagnostic script: attempt to import app modules and print full tracebacks.

Run this on the target host (Streamlit Cloud or your server) before starting Streamlit:

    python3 scripts/debug_imports.py

It will print Python version, sys.path, key package versions, and attempt imports.
It also writes output to debug_imports.log in the current directory.
"""

import sys
import traceback
import platform
from pathlib import Path

log_path = Path('debug_imports.log')
with log_path.open('w', encoding='utf-8') as log:
    def writeln(*parts):
        line = ' '.join(str(p) for p in parts)
        print(line)
        log.write(line + '\n')

    writeln('=== Diagnostic run ===')
    writeln('Platform:', platform.platform())
    writeln('Python:', sys.version.replace('\n', ' '))
    writeln('Executable:', sys.executable)
    writeln('CWD:', Path.cwd())
    writeln('Sys.path:')
    for p in sys.path:
        writeln('  ', p)

    # Try to detect versions of key packages
    try:
        import importlib.metadata as _md

        def pkg_ver(name):
            try:
                return _md.version(name)
            except Exception:
                return '<not-installed>'
    except Exception:
        def pkg_ver(name):
            return '<no-metadata>'

    for pkg in ('streamlit', 'requests'):
        writeln(pkg + ' version:', pkg_ver(pkg))

    writeln('\nAttempting imports...')

    def attempt(name):
        writeln('\n-- import', name)
        try:
            __import__(name)
            writeln('IMPORT_OK', name)
        except Exception as e:
            writeln('IMPORT_FAILED', name, type(e).__name__, str(e))
            writeln('Full traceback:')
            tb = traceback.format_exc()
            for L in tb.splitlines():
                writeln('   ', L)

    # Try main entry and the UI module specifically
    attempt('main_v2')
    attempt('emotional_os.deploy.modules.ui')

    writeln('\nFinished. Detailed log written to', log_path)

print('\nDiagnostic script completed. See debug_imports.log for full output.')

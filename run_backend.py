#!/usr/bin/env python
"""Run the FirstPerson FastAPI backend server."""

import subprocess
import sys
import os

os.chdir(r'd:\saoriverse-console')

# Run uvicorn with proper configuration
subprocess.run([
    sys.executable, '-m', 'uvicorn',
    'firstperson_backend:app',
    '--host', '0.0.0.0',
    '--port', '8000',
    '--workers', '1'
])

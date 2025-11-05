#!/usr/bin/env python3
"""
Simple Railway startup script for FirstPerson Streamlit app
"""
import os
import subprocess
import sys


def main():
    port = os.environ.get('PORT', '8501')
    cmd = [
        sys.executable, '-m', 'streamlit', 'run', 'main_v2.py',
        '--server.port=' + port,
        '--server.address=0.0.0.0',
        '--server.headless=true',
        '--server.enableCORS=false',
        '--server.enableXsrfProtection=false'
    ]

    print(f"Starting Streamlit with command: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == '__main__':
    main()

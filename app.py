#!/usr/bin/env python3
"""
FirstPerson Emotional OS - Railway Deployment Entry Point
This file serves as the main entry point for Railway deployment.
"""

import os
import sys
import subprocess

def main():
    """Main entry point for Railway deployment"""
    # Get the port from environment or default to 8501
    port = os.environ.get('PORT', '8501')
    
    # Set up Streamlit configuration
    os.environ['STREAMLIT_SERVER_PORT'] = port
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
    
    # Run the Streamlit app
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'main_v2.py',
            '--server.port', port,
            '--server.address', '0.0.0.0',
            '--server.headless', 'true',
            '--server.enableCORS', 'false',
            '--server.enableXsrfProtection', 'false'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
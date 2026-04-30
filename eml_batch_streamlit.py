#!/usr/bin/env python3
"""Root launcher for Streamlit Cloud.

This keeps the Streamlit entrypoint at repo root so deployment UIs can use
`eml_batch_streamlit.py` as the main file path.
"""

from scripts.eml_batch_streamlit import main


if __name__ == "__main__":
    main()

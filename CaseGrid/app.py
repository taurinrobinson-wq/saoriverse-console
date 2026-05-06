from __future__ import annotations

import traceback
from pathlib import Path

import streamlit as st

from modules import bard_settlement, eml_converter, medical_analyzer

MODULES = {
    "EML -> PDF Converter": eml_converter,
    "Bard Settlement Processor": bard_settlement,
    "Medical Record Analyzer": medical_analyzer,
}

LOGO_PATH = Path(__file__).resolve().parent / "assets" / "graphics" / "TRLFLogo.svg"


def main() -> None:
    st.set_page_config(page_title="CaseGrid - Modular Legal Workstation", layout="wide")

    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] img {
            margin-bottom: 0.15rem;
        }
        [data-testid="stSidebar"] .cg-title {
            margin: 0.1rem 0 0.2rem 0;
            font-size: 1.4rem;
            font-weight: 700;
            line-height: 1.15;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if LOGO_PATH.exists():
        st.sidebar.image(str(LOGO_PATH), width=300)
    st.sidebar.markdown('<div class="cg-title">CaseGrid</div>', unsafe_allow_html=True)
    st.sidebar.caption("Modular Legal Workstation")

    choice = st.sidebar.selectbox("Select Module", list(MODULES.keys()))
    if choice is None:
        st.info("Select a module from the sidebar.")
        return

    try:
        MODULES[choice].run()
    except Exception as exc:
        st.error(f"Module failed: {exc}")
        st.code(traceback.format_exc())
        return


if __name__ == "__main__":
    main()

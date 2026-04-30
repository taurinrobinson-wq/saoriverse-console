#!/usr/bin/env python3
"""Local Streamlit UI for EML batch processing.

Run:
    streamlit run scripts/eml_batch_streamlit.py
"""

from __future__ import annotations

import io
import tempfile
import zipfile
from datetime import datetime
from email import policy
from email.parser import BytesParser
from pathlib import Path

import streamlit as st

try:
    from scripts.eml_batch_rename_and_pdf import build_new_eml_name, process_email_file, unique_path
except ModuleNotFoundError:
    import sys

    # Fallback 1: add repo root and retry package-style import.
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    try:
        from scripts.eml_batch_rename_and_pdf import build_new_eml_name, process_email_file, unique_path
    except ModuleNotFoundError:
        # Fallback 2: import sibling module directly from scripts/ directory.
        scripts_dir = Path(__file__).resolve().parent
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        from eml_batch_rename_and_pdf import build_new_eml_name, process_email_file, unique_path


def _preview_rows(uploaded_files) -> list[dict]:
    rows: list[dict] = []
    used_names: set[str] = set()

    for upload in uploaded_files:
        try:
            if not upload.name.lower().endswith(".eml"):
                rows.append(
                    {
                        "original_name": upload.name,
                        "proposed_name": "",
                        "status": "error",
                        "error": "Unsupported file type (must be .eml)",
                    }
                )
                continue

            msg = BytesParser(policy=policy.default).parsebytes(upload.getvalue())
            proposed = build_new_eml_name(msg)

            stem = Path(proposed).stem
            suffix = Path(proposed).suffix
            candidate = proposed
            idx = 1
            while candidate in used_names:
                candidate = f"{stem}_{idx}{suffix}"
                idx += 1
            used_names.add(candidate)

            rows.append(
                {
                    "original_name": upload.name,
                    "proposed_name": candidate,
                    "status": "success",
                    "error": "",
                }
            )
        except Exception as ex:
            rows.append(
                {
                    "original_name": upload.name,
                    "proposed_name": "",
                    "status": "error",
                    "error": str(ex),
                }
            )

    return rows


def _build_zip(
    uploaded_files,
    rename_only: bool,
    include_emails: bool,
    include_pdfs: bool,
) -> tuple[bytes, int, int]:
    with tempfile.TemporaryDirectory(prefix="eml_streamlit_") as td:
        root = Path(td)
        input_dir = root / "input"
        output_dir = root / "pdf_output"
        package_dir = root / "package"

        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        package_dir.mkdir(parents=True, exist_ok=True)

        results: list[dict] = []

        for upload in uploaded_files:
            original_name = Path(upload.name).name
            try:
                if not original_name.lower().endswith(".eml"):
                    raise ValueError("Unsupported file type (must be .eml)")

                src_path = unique_path(input_dir / original_name)
                src_path.write_bytes(upload.getvalue())

                renamed_path, pdf_path, notes = process_email_file(
                    src_path,
                    output_dir=output_dir,
                    rename_only=rename_only,
                )

                final_eml = package_dir / renamed_path.name
                if include_emails:
                    renamed_path.replace(final_eml)
                else:
                    renamed_path.unlink(missing_ok=True)

                if pdf_path and pdf_path.exists():
                    if include_pdfs:
                        final_pdf = package_dir / pdf_path.name
                        pdf_path.replace(final_pdf)
                    else:
                        pdf_path.unlink(missing_ok=True)

                results.append(
                    {
                        "original_name": original_name,
                        "renamed_eml": final_eml.name if include_emails else None,
                        "status": "success",
                    }
                )
            except Exception as ex:
                results.append(
                    {
                        "original_name": original_name,
                        "status": "error",
                        "error": str(ex),
                    }
                )

        n_ok = sum(1 for r in results if r["status"] == "success")
        n_err = sum(1 for r in results if r["status"] == "error")

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for item in sorted(package_dir.glob("*")):
                zf.write(item, arcname=item.name)

        return buf.getvalue(), n_ok, n_err


def main() -> None:
    st.set_page_config(page_title="EML Batch Processor", layout="wide")

    st.title("EML Batch Processor")
    st.caption("Local Streamlit app: upload .eml files, preview rename output, and download a processed ZIP.")

    uploaded_files = st.file_uploader(
        "Upload .eml files",
        type=["eml"],
        accept_multiple_files=True,
        help="No browser CORS/HTTPS setup required when running locally.",
    )

    st.write("**Include in download ZIP:**")
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        include_pdfs = st.checkbox("PDFs", value=True)
    with col_opt2:
        include_emails = st.checkbox("Renamed .eml files", value=False)

    if not include_pdfs and not include_emails:
        st.warning("Select at least one output type above.")

    rename_only = not include_pdfs

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Preview Renames", disabled=not uploaded_files):
            rows = _preview_rows(uploaded_files)
            st.session_state["preview_rows"] = rows

    with col2:
        process_disabled = not uploaded_files or (not include_pdfs and not include_emails)
        if st.button("Process Batch", type="primary", disabled=process_disabled):
            with st.spinner("Processing uploaded files..."):
                zip_bytes, n_ok, n_err = _build_zip(
                    uploaded_files,
                    rename_only=rename_only,
                    include_emails=include_emails,
                    include_pdfs=include_pdfs,
                )
                st.session_state["zip_bytes"] = zip_bytes
                st.session_state["process_summary"] = (n_ok, n_err)
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.session_state["zip_name"] = f"processed_eml_batch_{ts}.zip"

    preview_rows = st.session_state.get("preview_rows")
    if preview_rows:
        st.subheader("Preview Results")
        st.dataframe(preview_rows, use_container_width=True)

    zip_bytes = st.session_state.get("zip_bytes")
    zip_name = st.session_state.get("zip_name", "processed_emails.zip")
    process_summary = st.session_state.get("process_summary")

    if process_summary:
        n_ok, n_err = process_summary
        if n_err:
            st.warning(f"Processed {n_ok} file(s) successfully. {n_err} failed.")
        else:
            st.success(f"Processed {n_ok} file(s) successfully.")

    if zip_bytes:
        st.download_button(
            label=f"Download ZIP ({zip_name})",
            data=zip_bytes,
            file_name=zip_name,
            mime="application/zip",
        )


if __name__ == "__main__":
    main()
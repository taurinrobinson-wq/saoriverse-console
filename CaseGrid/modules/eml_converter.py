#!/usr/bin/env python3
from __future__ import annotations

import io
import tempfile
import zipfile
from datetime import datetime
from email import policy
from email.parser import BytesParser
from pathlib import Path
from time import perf_counter
import importlib.util
import sys

import streamlit as st

repo_root = Path(__file__).resolve().parents[2]
scripts_dir = repo_root / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))
module_path = scripts_dir / "eml_batch_rename_and_pdf.py"
spec = importlib.util.spec_from_file_location("eml_batch_rename_and_pdf", module_path)
if spec is None or spec.loader is None:
    raise ModuleNotFoundError(f"Could not load helper module: {module_path}")
_eml_batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_eml_batch)

build_new_eml_name = _eml_batch.build_new_eml_name
process_email_file = _eml_batch.process_email_file
unique_path = _eml_batch.unique_path


_PREFIX = "eml_converter_"


def _k(name: str) -> str:
    return f"{_PREFIX}{name}"


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


def _mime_for_path(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "application/pdf"
    if suffix == ".eml":
        return "message/rfc822"
    return "application/octet-stream"


def _build_download(
    uploaded_files,
    rename_only: bool,
    include_emails: bool,
    include_pdfs: bool,
    exclude_attachments: bool,
) -> tuple[bytes, str, str, bool, int, int]:
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
                    exclude_attachments=exclude_attachments,
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

        packaged_items = sorted(item for item in package_dir.glob("*") if item.is_file())
        if len(packaged_items) == 1:
            single_item = packaged_items[0]
            return (
                single_item.read_bytes(),
                single_item.name,
                _mime_for_path(single_item),
                False,
                n_ok,
                n_err,
            )

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"processed_eml_batch_{ts}.zip"
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for item in packaged_items:
                zf.write(item, arcname=item.name)

        return buf.getvalue(), zip_name, "application/zip", True, n_ok, n_err


def run() -> None:
    if _k("uploader_key") not in st.session_state:
        st.session_state[_k("uploader_key")] = 0

    st.header("EML to PDF Converter")
    st.caption("Upload .eml files, preview rename output, and download processed output.")

    uploaded_files = st.file_uploader(
        "Upload .eml files",
        type=["eml"],
        accept_multiple_files=True,
        help="No browser CORS/HTTPS setup required when running locally.",
        key=f"uploader_{st.session_state[_k('uploader_key')]}",
    )

    st.write("**Include in download ZIP:**")
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        include_pdfs = st.checkbox("Include PDFs in ZIP", value=True, key=_k("include_pdfs"))
        exclude_attachments = st.checkbox(
            "Exclude attachments (email body only)",
            value=False,
            key=_k("exclude_attachments"),
        )
    with col_opt2:
        include_emails = st.checkbox("Renamed .eml files", value=False, key=_k("include_emails"))

    if not include_pdfs and not include_emails:
        st.warning("Select at least one output type above.")

    rename_only = not include_pdfs

    col1, col2, col3 = st.columns(3)

    with col3:
        if st.button("Clear Files", key=_k("clear")):
            st.session_state[_k("uploader_key")] += 1
            st.session_state.pop(_k("preview_rows"), None)
            st.session_state.pop(_k("download_bytes"), None)
            st.session_state.pop(_k("download_name"), None)
            st.session_state.pop(_k("download_mime"), None)
            st.session_state.pop(_k("is_zip"), None)
            st.session_state.pop(_k("process_summary"), None)
            st.session_state.pop(_k("process_timing"), None)
            st.rerun()

    with col1:
        if st.button("Preview Renames", disabled=not uploaded_files, key=_k("preview")):
            rows = _preview_rows(uploaded_files)
            st.session_state[_k("preview_rows")] = rows

    with col2:
        process_disabled = not uploaded_files or (not include_pdfs and not include_emails)
        if st.button("Process Batch", type="primary", disabled=process_disabled, key=_k("process")):
            with st.spinner("Processing uploaded files..."):
                files_to_process = uploaded_files or []
                start = perf_counter()
                download_bytes, download_name, download_mime, is_zip, n_ok, n_err = _build_download(
                    files_to_process,
                    rename_only=rename_only,
                    include_emails=include_emails,
                    include_pdfs=include_pdfs,
                    exclude_attachments=exclude_attachments,
                )
                elapsed_seconds = perf_counter() - start
                processed_count = n_ok + n_err
                total_input_bytes = sum(
                    int(getattr(upload, "size", 0) or len(upload.getvalue())) for upload in files_to_process
                )
                st.session_state[_k("download_bytes")] = download_bytes
                st.session_state[_k("download_name")] = download_name
                st.session_state[_k("download_mime")] = download_mime
                st.session_state[_k("is_zip")] = is_zip
                st.session_state[_k("process_summary")] = (n_ok, n_err)
                st.session_state[_k("process_timing")] = (
                    elapsed_seconds,
                    processed_count,
                    total_input_bytes,
                )

    preview_rows = st.session_state.get(_k("preview_rows"))
    if preview_rows:
        st.subheader("Preview Results")
        st.dataframe(preview_rows, use_container_width=True)

    download_bytes = st.session_state.get(_k("download_bytes"))
    download_name = st.session_state.get(_k("download_name"), "processed_output.zip")
    download_mime = st.session_state.get(_k("download_mime"), "application/zip")
    is_zip = st.session_state.get(_k("is_zip"), True)
    process_summary = st.session_state.get(_k("process_summary"))
    process_timing = st.session_state.get(_k("process_timing"))

    if process_summary:
        n_ok, n_err = process_summary
        if n_err:
            st.warning(f"Processed {n_ok} file(s) successfully. {n_err} failed.")
        else:
            st.success(f"Processed {n_ok} file(s) successfully.")

    if process_timing:
        elapsed_seconds, processed_count, total_input_bytes = process_timing
        rate = processed_count / elapsed_seconds if elapsed_seconds > 0 else 0.0
        total_input_mb = total_input_bytes / (1024 * 1024)
        st.info(
            f"Processing time: {elapsed_seconds:.2f}s for {processed_count} file(s) "
            f"({rate:.2f} files/sec). Total input size: {total_input_mb:.2f} MB."
        )

    if download_bytes:
        label_prefix = "Download ZIP" if is_zip else "Download File"
        st.download_button(
            label=f"{label_prefix} ({download_name})",
            data=download_bytes,
            file_name=download_name,
            mime=download_mime,
            key=_k("download"),
        )

#!/usr/bin/env python3
"""
Upload-based API for batch processing .eml files.

Endpoints:
- GET /health
- POST /api/eml/preview
- POST /api/eml/process

Run:
    uvicorn scripts.eml_batch_api:app --reload --host 0.0.0.0 --port 8000
"""

from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from datetime import datetime
from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import List

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from scripts.eml_batch_rename_and_pdf import build_new_eml_name, process_email_file, unique_path

MAX_FILES_PER_REQUEST = 200

app = FastAPI(
    title="EML Batch Processor API",
    description="Upload .eml files, rename them, and produce combined PDFs with attachment content.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _cleanup_path(path: str) -> None:
    try:
        shutil.rmtree(path, ignore_errors=True)
    except Exception:
        pass


def _validate_uploads(files: List[UploadFile]) -> None:
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded")
    if len(files) > MAX_FILES_PER_REQUEST:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum {MAX_FILES_PER_REQUEST} per request.",
        )


def _safe_upload_name(name: str) -> str:
    base = Path(name or "upload.eml").name
    if not base.lower().endswith(".eml"):
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {name}. Only .eml is supported")
    return base


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "eml-batch-api"}


@app.post("/api/eml/preview")
async def preview_renames(files: List[UploadFile] = File(...)) -> dict:
    _validate_uploads(files)

    results = []
    used_names = set()

    for upload in files:
        try:
            original_name = upload.filename or "unknown.eml"
            _safe_upload_name(original_name)
            contents = await upload.read()
            msg = BytesParser(policy=policy.default).parsebytes(contents)

            proposed = build_new_eml_name(msg)
            stem = Path(proposed).stem
            suffix = Path(proposed).suffix
            candidate = proposed
            idx = 1
            while candidate in used_names:
                candidate = f"{stem}_{idx}{suffix}"
                idx += 1
            used_names.add(candidate)

            results.append(
                {
                    "original_name": original_name,
                    "proposed_name": candidate,
                    "status": "success",
                }
            )
        except HTTPException:
            raise
        except Exception as ex:
            results.append(
                {
                    "original_name": upload.filename or "unknown.eml",
                    "status": "error",
                    "error": str(ex),
                }
            )

    return {
        "total_files": len(files),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "error"),
        "files": results,
    }


@app.post("/api/eml/process")
async def process_eml_batch(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    rename_only: bool = False,
):
    _validate_uploads(files)

    temp_root = tempfile.mkdtemp(prefix="eml_batch_api_")
    temp_root_path = Path(temp_root)
    input_dir = temp_root_path / "input"
    output_dir = temp_root_path / "pdf_output"
    package_dir = temp_root_path / "package"

    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    package_dir.mkdir(parents=True, exist_ok=True)

    processed_results = []

    for upload in files:
        original_name = upload.filename or "unknown.eml"
        try:
            safe_name = _safe_upload_name(original_name)
            payload = await upload.read()

            upload_path = unique_path(input_dir / safe_name)
            upload_path.write_bytes(payload)

            renamed_path, pdf_path, notes = process_email_file(
                upload_path,
                output_dir=output_dir,
                rename_only=rename_only,
            )

            final_eml = package_dir / renamed_path.name
            renamed_path.replace(final_eml)

            pdf_name = None
            if pdf_path and pdf_path.exists():
                final_pdf = package_dir / pdf_path.name
                pdf_path.replace(final_pdf)
                pdf_name = final_pdf.name

            processed_results.append(
                {
                    "original_name": original_name,
                    "renamed_eml": final_eml.name,
                    "pdf": pdf_name,
                    "notes": notes,
                    "status": "success",
                }
            )
        except HTTPException:
            shutil.rmtree(temp_root, ignore_errors=True)
            raise
        except Exception as ex:
            processed_results.append(
                {
                    "original_name": original_name,
                    "status": "error",
                    "error": str(ex),
                }
            )

    manifest = {
        "created_at": datetime.utcnow().isoformat() + "Z",
        "rename_only": rename_only,
        "total_files": len(files),
        "successful": sum(1 for r in processed_results if r["status"] == "success"),
        "failed": sum(1 for r in processed_results if r["status"] == "error"),
        "files": processed_results,
    }

    manifest_path = package_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    zip_path = temp_root_path / f"processed_eml_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for item in sorted(package_dir.glob("*")):
            zf.write(item, arcname=item.name)

    background_tasks.add_task(_cleanup_path, temp_root)

    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=zip_path.name,
    )

"""
DraftShift Renamer - Batch File Rename Service

Web-based litigation file renaming with auto-detection and bulk export.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime
import mimetypes
from typing import List, Dict

from filename_normalizer import FilenameNormalizer

router = APIRouter(prefix="/api/renamer", tags=["renamer"])

# Initialize normalizer
normalizer = FilenameNormalizer()


# ============================================================================
# MODELS & UTILITIES
# ============================================================================

class RenamedFile:
    """Represents a file to be renamed"""
    
    def __init__(self, original_name: str, original_bytes: bytes, filetype: str):
        self.original_name = original_name
        self.original_bytes = original_bytes
        self.filetype = filetype
        self.result = None
        self.error = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        if self.error:
            return {
                "original_name": self.original_name,
                "error": self.error,
                "status": "error"
            }
        
        return {
            "original_name": self.original_name,
            "normalized_filename": self.result.get("normalized_filename"),
            "detected_date": self.result.get("date_used"),
            "detected_slug": self.result.get("slug_used"),
            "date_source": self.result.get("source_of_date"),
            "slug_confidence": self.result.get("slug_confidence"),
            "status": "success"
        }


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/analyze")
async def analyze_files(files: List[UploadFile] = File(...)):
    """
    Analyze multiple files and return proposed renames.
    
    Does NOT rename or download - just preview.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 files per request")
    
    results = []
    
    for file in files:
        try:
            # Read file bytes
            contents = await file.read()
            
            # Get file type
            _, ext = os.path.splitext(file.filename)
            
            # Normalize filename
            result = normalizer.normalize(
                filename_original=file.filename,
                filetype=ext,
                user_provided_date=None,  # Let it auto-detect
                user_provided_slug=None
            )
            
            results.append({
                "original_name": file.filename,
                "normalized_filename": result["normalized_filename"],
                "detected_date": result["date_used"],
                "detected_slug": result["slug_used"],
                "date_source": result["source_of_date"],
                "slug_confidence": result["slug_confidence"],
                "status": "success"
            })
            
        except Exception as e:
            results.append({
                "original_name": file.filename,
                "error": str(e),
                "status": "error"
            })
    
    return {
        "total_files": len(files),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "error"),
        "files": results
    }


@router.post("/rename-and-download")
async def rename_and_download(files: List[UploadFile] = File(...)):
    """
    Analyze files, rename them, and return a ZIP download.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 files per request")
    
    # Create temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        zip_path = temp_path / "renamed_files.zip"
        
        results = []
        
        # Process each file
        for file in files:
            try:
                # Read file bytes
                contents = await file.read()
                
                # Get file type
                _, ext = os.path.splitext(file.filename)
                
                # Normalize filename
                result = normalizer.normalize(
                    filename_original=file.filename,
                    filetype=ext,
                    user_provided_date=None,
                    user_provided_slug=None
                )
                
                # Create normalized filename with extension
                normalized_name = f"{result['normalized_filename']}{ext}"
                normalized_path = temp_path / normalized_name
                
                # Write renamed file to temp directory
                with open(normalized_path, 'wb') as f:
                    f.write(contents)
                
                results.append({
                    "original_name": file.filename,
                    "normalized_filename": normalized_name,
                    "status": "success"
                })
                
            except Exception as e:
                results.append({
                    "original_name": file.filename,
                    "error": str(e),
                    "status": "error"
                })
        
        # Create ZIP file
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in temp_path.glob('*'):
                if file_path.name != "renamed_files.zip":
                    zipf.write(file_path, arcname=file_path.name)
        
        # Return ZIP file
        return FileResponse(
            zip_path,
            media_type='application/zip',
            filename=f"renamed_files_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        )


@router.post("/preview")
async def preview_rename(files: List[UploadFile] = File(...)):
    """
    Preview what files will be renamed to.
    
    Like /analyze but more detailed for UI.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    preview_data = []
    
    for file in files:
        try:
            contents = await file.read()
            _, ext = os.path.splitext(file.filename)
            
            result = normalizer.normalize(
                filename_original=file.filename,
                filetype=ext
            )
            
            preview_data.append({
                "original": file.filename,
                "renamed": f"{result['normalized_filename']}{ext}",
                "date_detected": result["date_used"],
                "type_detected": result["slug_used"],
                "confidence": result["slug_confidence"],
                "date_source": result["source_of_date"]
            })
            
        except Exception as e:
            preview_data.append({
                "original": file.filename,
                "error": str(e)
            })
    
    return {
        "preview": preview_data,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/custom-rename")
async def custom_rename(
    files: List[UploadFile] = File(...),
    overrides: dict = None  # {"original_name": {"date": "YYYY-MM-DD", "slug": "CustomSlug"}}
):
    """
    Rename files with user-provided date/slug overrides.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    overrides = overrides or {}
    results = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        zip_path = temp_path / "renamed_files.zip"
        
        for file in files:
            try:
                contents = await file.read()
                _, ext = os.path.splitext(file.filename)
                
                # Check for overrides
                file_overrides = overrides.get(file.filename, {})
                user_date = None
                user_slug = file_overrides.get("slug")
                
                if file_overrides.get("date"):
                    try:
                        user_date = datetime.fromisoformat(file_overrides["date"])
                    except:
                        pass
                
                # Normalize with overrides
                result = normalizer.normalize(
                    filename_original=file.filename,
                    filetype=ext,
                    user_provided_date=user_date,
                    user_provided_slug=user_slug
                )
                
                # Write file
                normalized_name = f"{result['normalized_filename']}{ext}"
                normalized_path = temp_path / normalized_name
                
                with open(normalized_path, 'wb') as f:
                    f.write(contents)
                
                results.append({
                    "original": file.filename,
                    "renamed": normalized_name,
                    "status": "success"
                })
                
            except Exception as e:
                results.append({
                    "original": file.filename,
                    "error": str(e),
                    "status": "error"
                })
        
        # Create ZIP
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in temp_path.glob('*'):
                if file_path.name != "renamed_files.zip":
                    zipf.write(file_path, arcname=file_path.name)
        
        return FileResponse(
            zip_path,
            media_type='application/zip',
            filename=f"renamed_files_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        )


@router.get("/supported-types")
async def get_supported_types():
    """Get list of supported document types and slugs"""
    return {
        "document_types": list(normalizer.dictionary.keys()),
        "total_types": len(normalizer.dictionary),
        "format": "YYMMDD – Slug"
    }


@router.post("/add-custom-type")
async def add_custom_type(document_type: str, slug: str):
    """Add a custom document type to the normalizer"""
    try:
        normalizer.add_custom_documents({document_type: slug})
        return {
            "success": True,
            "message": f"Added custom type: {document_type} → {slug}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

"""
DraftShift Web API — FastAPI backend for pleading generation.

Runs on Replit at draftshift.replit.dev
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import io
import logging
import base64

from draftshift.pleadings import PleadingFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="DraftShift API",
    description="Generate California civil pleadings from JSON input",
    version="0.1.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize PleadingFactory
CONFIG_PATH = "draftshift/formats/california_civil.yaml"
CITATION_PATH = "draftshift/formats/california_civil_citation.yaml"

try:
    factory = PleadingFactory(CONFIG_PATH, CITATION_PATH)
    logger.info("PleadingFactory initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize PleadingFactory: {e}")
    factory = None


# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "factory_ready": factory is not None,
        "supported_types": ["motion", "opposition", "reply", "declaration"]
    }


@app.post("/api/build")
async def build_pleading(data: dict):
    """
    Build a pleading from JSON data.
    
    Request body:
    {
        "type": "motion|opposition|reply|declaration",
        "attorney": {...},
        "case": {...},
        "title": "...",
        "arguments": [...],
        "pos": {...}
    }
    
    Returns:
    {
        "success": true,
        "filename": "Motion.docx",
        "docx_base64": "..."
    }
    """
    if not factory:
        raise HTTPException(status_code=500, detail="Factory not initialized")
    
    try:
        # Validate input
        if "type" not in data:
            raise ValueError("Missing required field: 'type'")
        
        logger.info(f"Building {data['type']} pleading")
        
        # Create pleading via factory
        pleading = factory.create(data)
        
        # Build document
        pleading.build(data)
        
        # Save to bytes
        output = io.BytesIO()
        pleading.save(output)
        output.seek(0)
        
        # Determine filename
        pleading_type = data["type"].lower()
        filename = f"{pleading_type.capitalize()}.docx"
        
        # Return DOCX as base64 (client can download)
        docx_base64 = base64.b64encode(output.getvalue()).decode()
        
        logger.info(f"Successfully built {filename}")
        
        return {
            "success": True,
            "filename": filename,
            "data": docx_base64
        }
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Build error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Build failed: {str(e)}")


@app.get("/api/fixtures/{fixture_name}")
async def get_fixture(fixture_name: str):
    """
    Get a fixture JSON file for testing.
    
    Available: motion.json, opposition.json, reply.json, declaration.json
    """
    fixture_path = Path("draftshift/tests/fixtures") / fixture_name
    
    if not fixture_path.exists():
        raise HTTPException(status_code=404, detail=f"Fixture not found: {fixture_name}")
    
    try:
        with open(fixture_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading fixture: {e}")
        raise HTTPException(status_code=500, detail="Failed to load fixture")


# ============================================================
# STATIC FILES
# ============================================================

# Serve React frontend from dist folder
try:
    app.mount("/", StaticFiles(directory="draftshift-web/dist", html=True), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import uvicorn
    
    # Run on 0.0.0.0 for Replit
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

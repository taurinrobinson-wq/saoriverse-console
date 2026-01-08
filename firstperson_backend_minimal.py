"""FirstPerson FastAPI Backend - Minimal Working Version"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import uuid
from typing import Optional, List
from datetime import datetime

app = FastAPI(title="FirstPerson Backend", version="2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000", "http://127.0.0.1:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MODELS
# ============================================================================

class ChatRequest(BaseModel):
    message: str
    userId: Optional[str] = "demo_user"
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    success: bool
    message: str
    conversation_id: Optional[str] = None
    glyph_voltage: Optional[str] = None
    error: Optional[str] = None

# ============================================================================
# RESPONSE GENERATION
# ============================================================================

def detect_themes(text: str) -> List[str]:
    """Extract themes from message."""
    text_lower = text.lower()
    themes = []
    
    theme_keywords = {
        "fatigue": ["tired", "exhausted", "exhaustion", "drained", "burnt out"],
        "stress": ["stress", "stressed", "anxious", "anxiety", "pressure", "overwhelm"],
        "work": ["work", "job", "career", "deadline", "attorney", "client", "boss"],
        "hope": ["hope", "hopeful", "positive", "good", "better", "improving"],
        "grief": ["sad", "sadness", "loss", "grief", "mourn", "miss"],
        "confusion": ["confused", "lost", "uncertain", "unclear"],
    }
    
    for theme, keywords in theme_keywords.items():
        if any(kw in text_lower for kw in keywords):
            themes.append(theme)
    
    return themes

def generate_response(user_message: str) -> tuple:
    """Generate contextual response."""
    themes = detect_themes(user_message)
    glyph_voltage = "medium"
    response = ""
    
    if "fatigue" in themes:
        response = "I notice tiredness coming through. That exhaustion is real. How are you caring for yourself in this?"
        glyph_voltage = "low"
    elif "stress" in themes:
        response = "There's real pressure here. Tell me what part feels most overwhelming right now?"
        glyph_voltage = "high"
    elif "hope" in themes:
        response = "There's something hopeful in what you're sharing. What's giving you that sense of possibility?"
        glyph_voltage = "medium"
    elif "work" in themes and "stress" in themes:
        response = "Work stress can be especially heavy. You're carrying something significant. What would help?"
        glyph_voltage = "high"
    else:
        response = f"I hear you saying '{user_message[:50]}...'. Tell me more about that?"
        glyph_voltage = "medium"
    
    return response, glyph_voltage

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health")
async def health():
    """Health check."""
    return {"status": "ok"}

@app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """Chat endpoint."""
    try:
        if not request.message:
            return ChatResponse(success=False, message="", error="No message")
        
        response_text, glyph_voltage = generate_response(request.message)
        conversation_id = request.conversation_id or str(uuid.uuid4())[:8]
        
        return ChatResponse(
            success=True,
            message=response_text,
            conversation_id=conversation_id,
            glyph_voltage=glyph_voltage
        )
    except Exception as e:
        return ChatResponse(
            success=False,
            message="",
            error=str(e)
        )

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """Stub transcribe endpoint."""
    return {"success": True, "text": "transcription pending", "confidence": 0.95}

@app.post("/synthesize")
async def synthesize(request: dict):
    """Stub synthesize endpoint."""
    return {"success": True, "audio_url": "/audio/test.mp3", "text": request.get("text", "")}

@app.get("/conversations/{user_id}")
async def get_conversations(user_id: str):
    """Get conversations."""
    return {"success": True, "conversations": []}

if __name__ == "__main__":
    import uvicorn
    print("Starting FirstPerson Backend (Minimal)...")
    print("Listening on http://0.0.0.0:8001")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")

"""
FastAPI backend for FirstPerson audio conversation web app.
Handles: transcription, chat, audio synthesis, and streaming.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from pathlib import Path
import sys
import io
import logging

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our components
try:
    from emotional_os.deploy.modules.audio_conversation_orchestrator import AudioConversationOrchestrator
    from emotional_os.deploy.modules.prosody_planner import ProsodyPlanner
    from emotional_os.deploy.modules.nlp_init import warmup_nlp
    from firstperson import FirstPersonOrchestrator
    logger.info("✅ Successfully imported audio and FirstPerson modules")
except ImportError as e:
    logger.error(f"❌ Import error: {e}")
    raise

# ============================================================================
# FASTAPI SETUP
# ============================================================================

app = FastAPI(
    title="FirstPerson Audio API",
    description="Real-time audio conversation with emotionally aware AI",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MODELS
# ============================================================================

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    text: str
    glyph_intent: Optional[Dict[str, Any]] = None
    audio_url: Optional[str] = None

class SynthesizeRequest(BaseModel):
    text: str
    glyph_intent: Optional[Dict[str, Any]] = None

class SynthesizeResponse(BaseModel):
    audio_url: str
    prosody_markup: Optional[str] = None

# ============================================================================
# STATE & INITIALIZATION
# ============================================================================

# Global instances
audio_orchestrator = None
prosody_planner = None
firstperson_orchestrator = None
active_sessions = {}

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global audio_orchestrator, prosody_planner, firstperson_orchestrator
    
    logger.info("🚀 Starting FirstPerson API...")
    
    # Warmup NLP
    nlp_status = warmup_nlp()
    logger.info(f"📚 NLP Status: {nlp_status}")
    
    # Initialize components
    try:
        prosody_planner = ProsodyPlanner()
        logger.info("✅ ProsodyPlanner initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize ProsodyPlanner: {e}")
    
    try:
        firstperson_orchestrator = FirstPersonOrchestrator()
        logger.info("✅ FirstPersonOrchestrator initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize FirstPersonOrchestrator: {e}")
    
    try:
        audio_orchestrator = AudioConversationOrchestrator()
        logger.info("✅ AudioConversationOrchestrator initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize AudioConversationOrchestrator: {e}")
    
    logger.info("✅ Startup complete")

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "FirstPerson Audio API",
        "audio_ready": audio_orchestrator is not None,
        "nlp_ready": True,
    }

@app.post("/api/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """Transcribe audio to text using faster-whisper"""
    try:
        # Read audio file
        contents = await audio.read()
        audio_bytes = io.BytesIO(contents)
        
        # Use AudioConversationOrchestrator's transcription if available
        # For now, we'll use faster-whisper directly
        from faster_whisper import WhisperModel
        
        model = WhisperModel("base")  # CPU-optimized
        segments, info = model.transcribe(audio_bytes)
        
        transcript = "".join([segment.text for segment in segments])
        
        return {
            "text": transcript.strip(),
            "confidence": 0.95,  # Placeholder
        }
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat endpoint - integrates FirstPerson + optional audio synthesis"""
    try:
        user_id = request.user_id or str(uuid.uuid4())
        
        # Get FirstPerson response (all tiers: context, memory, emotional response)
        if firstperson_orchestrator is None:
            raise HTTPException(status_code=503, detail="FirstPerson not initialized")
        
        response_data = firstperson_orchestrator.process_message(
            message=request.message,
            user_id=user_id
        )
        
        # Extract response text and glyph intent
        response_text = response_data.get("text", "I'm not sure how to respond.")
        glyph_intent = response_data.get("glyph_intent", {})
        
        # Apply prosody planning if we have glyph intent
        prosodic_text = response_text
        if prosody_planner and glyph_intent:
            prosodic_text = prosody_planner.plan(response_text, glyph_intent)
        
        return ChatResponse(
            text=response_text,
            glyph_intent=glyph_intent,
            audio_url=None,  # Optional: add /api/synthesize to get audio
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/synthesize")
async def synthesize(request: SynthesizeRequest):
    """Synthesize text to speech with prosody from glyph intent"""
    try:
        # Apply prosody
        prosodic_text = request.text
        if prosody_planner and request.glyph_intent:
            prosodic_text = prosody_planner.plan(
                request.text,
                request.glyph_intent
            )
        
        # Synthesize audio
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        
        # Save to temp file
        audio_path = f"/tmp/audio_{uuid.uuid4()}.wav"
        engine.save_to_file(prosodic_text, audio_path)
        engine.runAndWait()
        
        return SynthesizeResponse(
            audio_url=f"/api/audio/{Path(audio_path).name}",
            prosody_markup=prosodic_text if "<prosody" in prosodic_text else None,
        )
    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/audio/{filename}")
async def get_audio(filename: str):
    """Serve generated audio files"""
    try:
        file_path = Path(f"/tmp/{filename}")
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Audio not found")
        return FileResponse(file_path, media_type="audio/wav")
    except Exception as e:
        logger.error(f"Audio retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for streaming conversation"""
    await websocket.accept()
    session_id = str(uuid.uuid4())
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            if data["type"] == "message":
                # Process and send response
                response = firstperson_orchestrator.process_message(
                    message=data["text"],
                    user_id=data.get("user_id", session_id)
                )
                
                await websocket.send_json({
                    "type": "response",
                    "text": response.get("text"),
                    "glyph_intent": response.get("glyph_intent"),
                })
            
            elif data["type"] == "disconnect":
                break
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        if session_id in active_sessions:
            del active_sessions[session_id]

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

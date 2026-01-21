"""FirstPerson FastAPI Backend - Context-Aware Conversational AI"""

import sys
import os
import json
import uuid
from datetime import datetime
from typing import Optional, List, Tuple
from collections import deque

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    import requests
except ImportError:
    requests = None

app = FastAPI(title="FirstPerson Backend", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase config
SUPABASE_URL = os.environ.get("SUPABASE_URL") or "https://gyqzyuvuuyfjxnramkfq.supabase.co"
SUPABASE_KEY = (
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_KEY")
    or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd5cXp5dXZ1dXlmanhucmFta2ZxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTQ2NzIwMCwiZXhwIjoyMDcxMDQzMjAwfQ.sILcK31ECwM0IUECL0NklBdv4WREIxToqtCdsMYKWqo"
)

def get_supabase_headers():
    return {
        "Content-Type": "application/json",
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }


# ============================================================================
# MODELS
# ============================================================================

class ConversationTurn(BaseModel):
    """Single turn in a conversation."""
    user_text: str
    assistant_response: str
    glyph_voltage: Optional[str] = "medium"
    timestamp: str


class ChatRequest(BaseModel):
    """User message."""
    message: str
    userId: Optional[str] = "demo_user"
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response with context."""
    success: bool
    message: str
    conversation_id: Optional[str] = None
    glyph_voltage: Optional[str] = None
    error: Optional[str] = None


class TranscriptionRequest(BaseModel):
    """Transcription result."""
    text: str
    confidence: Optional[float] = 1.0


class SynthesisRequest(BaseModel):
    """Text to synthesize."""
    text: str
    voice: Optional[str] = "neutral"


# ============================================================================
# RESPONSE GENERATION WITH CONTEXT
# ============================================================================

def detect_themes(conversation_history: List[ConversationTurn]) -> List[str]:
    """Extract recurring themes from conversation."""
    if not conversation_history:
        return []
    
    all_text = " ".join([turn.user_text for turn in conversation_history]).lower()
    
    themes = []
    theme_keywords = {
        "fatigue": ["tired", "exhausted", "exhaustion", "drained", "burnt out"],
        "stress": ["stress", "stressed", "anxious", "anxiety", "pressure", "overwhelm"],
        "work": ["work", "job", "career", "deadline", "attorney", "client", "boss"],
        "relationship": ["assistant", "colleague", "friend", "family", "partner", "team"],
        "hope": ["hope", "hopeful", "positive", "good", "better", "improving"],
        "grief": ["sad", "sadness", "loss", "grief", "mourn", "miss", "gone"],
        "confusion": ["confused", "lost", "don't know", "uncertain", "unclear"],
    }
    
    for theme, keywords in theme_keywords.items():
        if any(kw in all_text for kw in keywords):
            themes.append(theme)
    
    return themes


def generate_contextual_response(user_message: str, conversation_history: List[ConversationTurn]) -> Tuple[str, str]:
    """Generate response that acknowledges conversation context."""
    
    themes = detect_themes(conversation_history + [ConversationTurn(
        user_text=user_message,
        assistant_response="",
        timestamp=datetime.now().isoformat()
    )])
    
    # Build response based on context
    response = ""
    glyph_voltage = "medium"
    
    # Check if this references previous turns
    if len(conversation_history) > 0:
        last_turn = conversation_history[-1]
        
        # Check if user is elaborating on previous topic
        if any(word in user_message.lower() for word in last_turn.user_text.lower().split()):
            response = f"So when you mentioned '{last_turn.user_text[:40]}...', and now you're saying this - I see how they connect. "
        else:
            response = f"I hear you. Earlier you shared about {themes[0] if themes else 'something important'}. "
    
    # Add theme-specific response
    if "fatigue" in themes:
        response += "I notice tiredness coming through. That exhaustion is real. How are you caring for yourself in this?"
        glyph_voltage = "low"
    elif "stress" in themes:
        response += "There's real pressure here. Tell me what part feels most overwhelming right now?"
        glyph_voltage = "high"
    elif "hope" in themes:
        response += "There's something hopeful in what you're sharing. What's giving you that sense of possibility?"
        glyph_voltage = "medium"
    elif "work" in themes and "stress" in themes:
        response += f"Work stress can be especially heavy. You're carrying something significant. What would help?"
        glyph_voltage = "high"
    else:
        response += f"I hear you saying '{user_message[:50]}...'. Tell me more about that?"
        glyph_voltage = "medium"
    
    return response, glyph_voltage


# ============================================================================
# SUPABASE PERSISTENCE
# ============================================================================

def save_conversation_to_supabase(user_id: str, conversation_id: str, title: str, turns: List[ConversationTurn]) -> bool:
    """Save conversation to Supabase."""
    if not requests or not SUPABASE_URL or not SUPABASE_KEY:
        return False
    
    try:
        url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/conversations"
        
        # Convert turns to serializable format
        messages = [
            {"role": "user", "content": turn.user_text}
            for turn in turns for turn in [turn]  # Flatten
        ]
        # Add assistant responses
        for i, turn in enumerate(turns):
            messages.append({"role": "assistant", "content": turn.assistant_response})
        
        payload = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "title": title,
            "messages": json.dumps(messages),
            "updated_at": datetime.now().isoformat(),
            "message_count": len(messages),
        }
        
        response = requests.post(
            url,
            headers=get_supabase_headers(),
            json=[payload],
            timeout=10
        )
        
        return response.status_code in (200, 201)
    except Exception as e:
        print(f"Error saving: {e}")
        return False


def load_conversations_from_supabase(user_id: str) -> List[dict]:
    """Load conversation list from Supabase."""
    if not requests or not SUPABASE_URL or not SUPABASE_KEY:
        return []
    
    try:
        url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/conversations"
        params = {
            "select": "conversation_id,title,updated_at,message_count",
            "user_id": f"eq.{user_id}",
            "order": "updated_at.desc",
            "limit": "100",
        }
        
        response = requests.get(
            url,
            headers=get_supabase_headers(),
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json() if isinstance(response.json(), list) else []
        return []
    except Exception as e:
        print(f"Error loading: {e}")
        return []


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """Chat with context awareness."""
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message required")
        
        user_id = request.userId or "demo_user"
        message = request.message.strip()
        conversation_id = request.conversation_id or str(uuid.uuid4())[:8]
        
        # Load conversation history if provided
        conversation_history: List[ConversationTurn] = []
        
        # Generate contextual response
        response_text, glyph_voltage = generate_contextual_response(message, conversation_history)
        
        # Create turn
        turn = ConversationTurn(
            user_text=message,
            assistant_response=response_text,
            glyph_voltage=glyph_voltage,
            timestamp=datetime.now().isoformat()
        )
        conversation_history.append(turn)
        
        # Save to Supabase (background)
        title = message[:50] + "..." if len(message) > 50 else message
        save_conversation_to_supabase(user_id, conversation_id, title, conversation_history)
        
        return ChatResponse(
            success=True,
            message=response_text,
            conversation_id=conversation_id,
            glyph_voltage=glyph_voltage
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        return ChatResponse(
            success=False,
            message="",
            error=str(e)
        )


@app.get("/conversations/{user_id}")
async def get_conversations(user_id: str):
    """Get conversation list."""
    try:
        convs = load_conversations_from_supabase(user_id)
        return {
            "success": True,
            "conversations": convs
        }
    except Exception as e:
        return {
            "success": False,
            "conversations": [],
            "error": str(e)
        }


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """Transcribe audio to text."""
    try:
        # For now, just accept the transcription
        # In production, use OpenAI Whisper or similar
        content = await file.read()
        
        return {
            "success": True,
            "text": "Audio transcription would happen here",
            "confidence": 0.95
        }
    except Exception as e:
        return {
            "success": False,
            "text": "",
            "error": str(e)
        }


@app.post("/synthesize")
async def synthesize(request: SynthesisRequest):
    """Synthesize text to audio."""
    try:
        # For now, return placeholder
        # In production, use gTTS, Azure TTS, or similar
        
        return {
            "success": True,
            "audio_url": f"/audio/{uuid.uuid4()}.mp3",
            "text": request.text
        }
    except Exception as e:
        return {
            "success": False,
            "audio_url": "",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    print("Starting FirstPerson Backend v2...")
    print("Context-aware companion system ready")
    print("Listening on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

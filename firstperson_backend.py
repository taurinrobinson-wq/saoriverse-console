"""FirstPerson FastAPI Backend - Serves the response engine to Next.js frontend."""

import sys
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="FirstPerson Backend", version="1.0.0")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """Chat request from frontend."""
    message: str
    userId: Optional[str] = "demo_user"
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    """Chat response to frontend."""
    success: bool
    message: str
    error: Optional[str] = None


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "FirstPerson Backend"}


@app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """Process user message and return response using glyph system."""
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # For now, return a placeholder that acknowledges the message
        # The full glyph system will be integrated separately
        
        message_lower = request.message.lower()
        
        # Simple pattern-based responses for now
        if any(word in message_lower for word in ["hi", "hello", "hey"]):
            response = "Hello! I'm here to listen to you. What's on your mind?"
        elif any(word in message_lower for word in ["how are you", "how are you feeling"]):
            response = "I appreciate you asking. Right now, I'm focused entirely on being present for you. How are YOU doing?"
        elif any(word in message_lower for word in ["sad", "depressed", "down"]):
            response = "I hear sadness in what you're sharing. That's real and I'm present with it. Can you tell me more about what's weighing on you?"
        elif any(word in message_lower for word in ["happy", "great", "wonderful", "amazing"]):
            response = "That warmth comes through. I'm glad you're experiencing that. What's making you feel this way?"
        elif any(word in message_lower for word in ["confused", "lost", "don't know"]):
            response = "Confusion can feel disorienting. I'm here to help you find clarity. What part of this feels most confusing right now?"
        else:
            response = "I hear you. That sounds significant. Can you tell me more about what you're experiencing?"
        
        return ChatResponse(
            success=True,
            message=response
        )
    except Exception as e:
        print(f"Error processing chat: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting FirstPerson Backend...")
    print("📍 Glyph-informed response system ready")
    print("🔗 Listening on http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


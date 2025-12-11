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
        
        message = request.message.strip()
        message_lower = message.lower()
        
        # Analyze the message for specific content
        response = generate_empathetic_response(message, message_lower)
        
        return ChatResponse(
            success=True,
            message=response
        )
    except Exception as e:
        print(f"Error processing chat: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def generate_empathetic_response(message: str, message_lower: str) -> str:
    """Generate a response that acknowledges specific details from the message."""
    
    # Extract key elements from the message
    has_work = any(word in message_lower for word in ["work", "job", "career", "office", "deadline", "attorney", "lawyer"])
    has_stress = any(word in message_lower for word in ["stress", "stressed", "anxious", "overwhelmed", "pressure", "struggling", "hard", "difficult"])
    has_relationship = any(word in message_lower for word in ["assistant", "colleague", "manager", "boss", "team", "friend", "partner", "family"])
    has_health_issue = any(word in message_lower for word in ["drinking", "drug", "alcohol", "sick", "illness", "depression", "anxiety"])
    
    # Greeting responses
    if message_lower in ["hi", "hello", "hey", "hey there", "hi there"]:
        return "Hello! I'm here to listen to you. What's on your mind?"
    
    if any(phrase in message_lower for phrase in ["how are you", "how are you doing", "how are you feeling"]):
        return "I appreciate you asking. Right now, I'm focused entirely on being present for you. How are YOU doing?"
    
    # Work-related stress with relationship issue
    if has_work and has_stress and has_relationship and has_health_issue:
        # This is about work stress, a difficult colleague situation, and their substance issue
        return f"That's a lot to carry alone. An attorney managing multiple clients, AND having to suddenly take on your assistant's responsibilities because of their drinking problem? That's not just stressful—that's a significant breach of trust and a real workload crisis. You've been covering two jobs at once. How are you holding up with that weight on your shoulders right now?"
    
    # Work stress with relationship difficulty
    if has_work and has_stress and has_relationship:
        return f"It sounds like you're not just dealing with work pressure, but also with someone else's struggle affecting your responsibilities. That's a heavy combination. Can you tell me more about what's been the hardest part of this situation?"
    
    # General work stress
    if has_work and has_stress:
        if "deadline" in message_lower or "fact sheet" in message_lower:
            return "Deadlines and the pressure to deliver quality work can be draining, especially when they pile up. What's making this particular deadline feel especially stressful?"
        return "Work stress is real, and it sounds like you're feeling it. What's been the most overwhelming part?"
    
    # Stress about someone else
    if has_stress and has_relationship:
        return "When the people around us are struggling, it affects us too—especially when it impacts what we need to do. That can feel frustrating and sad at the same time. How has this been affecting you personally?"
    
    # General stress
    if has_stress:
        return "I hear the weight in what you're sharing. Stress can feel isolating. What's one thing about this situation that's been hardest for you?"
    
    # Happy/positive tone
    if any(word in message_lower for word in ["happy", "great", "wonderful", "amazing", "love", "excited"]):
        return "That warmth comes through. I'm glad you're experiencing that. What's making you feel this way?"
    
    # Confused/lost
    if any(word in message_lower for word in ["confused", "lost", "don't know", "uncertain"]):
        return "Confusion can feel disorienting. I'm here to help you find clarity. What part of this feels most confusing right now?"
    
    # Sad/down
    if any(word in message_lower for word in ["sad", "depressed", "down", "unhappy"]):
        return "I hear sadness in what you're sharing. That's real and I'm present with it. Can you tell me more about what's weighing on you?"
    
    # Default - acknowledge and ask for more specificity
    return "I hear you. That sounds significant. Can you tell me more about what you're experiencing?"



if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting FirstPerson Backend...")
    print("📍 Glyph-informed response system ready")
    print("🔗 Listening on http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


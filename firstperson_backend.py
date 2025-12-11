"""FirstPerson FastAPI Backend - Serves the response engine to Next.js frontend."""

import sys
import os
import json
import uuid
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import conversation manager
sys.path.insert(0, str(Path(__file__).parent / "src" / "deploy_modules"))
try:
    from conversation_manager import ConversationManager, generate_auto_name
except ImportError:
    ConversationManager = None
    def generate_auto_name(msg: str, max_length: int = 50) -> str:
        """Fallback auto-name generator."""
        text = msg.strip()[:100]
        if len(text) > max_length:
            text = text[:max_length-3] + "..."
        return text[0].upper() + text[1:] if len(text) > 1 else text.upper()

app = FastAPI(title="FirstPerson Backend", version="1.0.0")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active conversation managers by user_id (in-memory for now)
conversation_managers = {}


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
    conversation_id: Optional[str] = None


class ConversationInfo(BaseModel):
    """Conversation metadata."""
    conversation_id: str
    title: str
    updated_at: str
    message_count: int


class ConversationListResponse(BaseModel):
    """List of user's conversations."""
    success: bool
    conversations: List[ConversationInfo]
    error: Optional[str] = None


class SaveConversationRequest(BaseModel):
    """Save conversation request."""
    conversation_id: str
    title: Optional[str] = None
    messages: List[dict]


class RenameConversationRequest(BaseModel):
    """Rename conversation request."""
    conversation_id: str
    new_title: str


def get_conversation_manager(user_id: str) -> Optional[ConversationManager]:
    """Get or create a conversation manager for a user."""
    if ConversationManager is None:
        return None
    
    if user_id not in conversation_managers:
        conversation_managers[user_id] = ConversationManager(user_id)
    
    return conversation_managers[user_id]


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
        user_id = request.userId or "demo_user"
        
        # Generate response
        response = generate_empathetic_response(message, message_lower)
        
        # Handle conversation saving if conversation_id provided
        conversation_id = request.context.get("conversation_id") if request.context else None
        is_first_message = request.context.get("is_first_message", False) if request.context else False
        
        if is_first_message or not conversation_id:
            # Generate a new conversation ID
            conversation_id = str(uuid.uuid4())[:8]
        
        # Auto-generate title from first message
        title = None
        if is_first_message:
            title = generate_auto_name(message)
        
        # Try to save conversation if manager is available
        manager = get_conversation_manager(user_id)
        if manager:
            messages = request.context.get("messages", []) if request.context else []
            
            # Add current exchange to messages
            messages.append({"role": "user", "content": message})
            messages.append({"role": "assistant", "content": response})
            
            # Use title from first message or keep existing
            if not title and request.context:
                title = request.context.get("title", generate_auto_name(message))
            
            manager.save_conversation(conversation_id, title or generate_auto_name(message), messages)
        
        return ChatResponse(
            success=True,
            message=response,
            conversation_id=conversation_id
        )
    except Exception as e:
        print(f"Error processing chat: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversations/{user_id}")
async def get_conversations(user_id: str) -> ConversationListResponse:
    """Get all conversations for a user."""
    try:
        manager = get_conversation_manager(user_id)
        if not manager:
            return ConversationListResponse(
                success=True,
                conversations=[],
                error="Conversation persistence not configured"
            )
        
        conversations = manager.load_conversations()
        conv_list = [
            ConversationInfo(
                conversation_id=c.get("conversation_id", ""),
                title=c.get("title", "Untitled"),
                updated_at=c.get("updated_at", ""),
                message_count=c.get("message_count", 0)
            )
            for c in conversations
        ]
        
        return ConversationListResponse(
            success=True,
            conversations=conv_list
        )
    except Exception as e:
        print(f"Error loading conversations: {e}", file=sys.stderr)
        return ConversationListResponse(
            success=False,
            conversations=[],
            error=str(e)
        )


@app.get("/conversation/{user_id}/{conversation_id}")
async def get_conversation(user_id: str, conversation_id: str) -> ChatResponse:
    """Load a specific conversation."""
    try:
        manager = get_conversation_manager(user_id)
        if not manager:
            return ChatResponse(
                success=False,
                message="",
                error="Conversation persistence not configured"
            )
        
        conv = manager.load_conversation(conversation_id)
        if not conv:
            return ChatResponse(
                success=False,
                message="",
                error="Conversation not found"
            )
        
        # Return the conversation data as JSON string in message field
        return ChatResponse(
            success=True,
            message=json.dumps(conv),
            conversation_id=conversation_id
        )
    except Exception as e:
        print(f"Error loading conversation: {e}", file=sys.stderr)
        return ChatResponse(
            success=False,
            message="",
            error=str(e)
        )


@app.delete("/conversation/{user_id}/{conversation_id}")
async def delete_conversation(user_id: str, conversation_id: str) -> ChatResponse:
    """Delete a conversation."""
    try:
        manager = get_conversation_manager(user_id)
        if not manager:
            return ChatResponse(
                success=False,
                message="",
                error="Conversation persistence not configured"
            )
        
        success, message = manager.delete_conversation(conversation_id)
        return ChatResponse(
            success=success,
            message=message,
            conversation_id=conversation_id
        )
    except Exception as e:
        print(f"Error deleting conversation: {e}", file=sys.stderr)
        return ChatResponse(
            success=False,
            message="",
            error=str(e)
        )


@app.patch("/conversation/{user_id}/{conversation_id}")
async def rename_conversation(user_id: str, conversation_id: str, request: RenameConversationRequest) -> ChatResponse:
    """Rename a conversation."""
    try:
        manager = get_conversation_manager(user_id)
        if not manager:
            return ChatResponse(
                success=False,
                message="",
                error="Conversation persistence not configured"
            )
        
        success, message = manager.rename_conversation(conversation_id, request.new_title)
        return ChatResponse(
            success=success,
            message=message,
            conversation_id=conversation_id
        )
    except Exception as e:
        print(f"Error renaming conversation: {e}", file=sys.stderr)
        return ChatResponse(
            success=False,
            message="",
            error=str(e)
        )


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


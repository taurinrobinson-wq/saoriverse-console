"""FirstPerson Flask Backend - Simple, stable alternative to FastAPI for Windows."""

import sys
import os
import json
import threading
import tempfile
from pathlib import Path
from datetime import datetime
from io import BytesIO

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequest

# Global models
WHISPER_MODEL = None
TTS_ENGINE = None
_tts_lock = threading.Lock()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def init_models():
    """Initialize AI models."""
    global WHISPER_MODEL, TTS_ENGINE
    
    # Initialize Whisper
    try:
        from faster_whisper import WhisperModel
        print("Loading Whisper model...")
        WHISPER_MODEL = WhisperModel("tiny", device="cpu", compute_type="int8")
        print("✓ Whisper model initialized (tiny)")
    except ImportError:
        print("⚠ faster-whisper not installed. Install with: pip install faster-whisper")
    except Exception as e:
        print(f"⚠ Whisper init failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Initialize pyttsx3 - use lazy loading instead
    # pyttsx3 has threading issues on Windows, so we'll initialize it lazily in the endpoint
    try:
        import pyttsx3
        # Just test import
        print("✓ pyttsx3 available for lazy initialization")
    except ImportError:
        print("⚠ pyttsx3 not installed. Install with: pip install pyttsx3")


def generate_empathetic_response(message: str, messages: list = None) -> dict:
    """Generate response using glyph-informed empathy system."""
    if messages is None:
        messages = []
    
    glyph_intent = {
        "primary": "attunement",
        "emotional_tone": "empathetic",
        "quality": "present"
    }
    
    # Simple response generation with glyph awareness
    if any(word in message.lower() for word in ["sad", "upset", "hurt", "pain"]):
        glyph_intent["tone"] = "validation"
        response_text = (
            f"I hear that you're feeling hurt: '{message}'. That kind of pain matters. "
            "What would be most helpful for you right now?"
        )
        glyph_intent["attunement"] = "compassion"
    elif any(word in message.lower() for word in ["happy", "great", "excited", "good"]):
        glyph_intent["tone"] = "celebration"
        response_text = (
            f"That joy you're expressing - '{message}' - is worth holding onto. "
            "Tell me more about what's making you feel this way."
        )
        glyph_intent["attunement"] = "appreciation"
    elif any(word in message.lower() for word in ["confused", "unsure", "lost", "help"]):
        glyph_intent["tone"] = "guidance"
        response_text = (
            f"You're reaching for clarity: '{message}'. That takes courage. "
            "What aspect feels most unclear right now?"
        )
        glyph_intent["attunement"] = "guidance"
    else:
        glyph_intent["tone"] = "neutral"
        response_text = (
            f"I hear you saying: '{message}'. That's significant enough to bring here. "
            "Can you tell me more about what's behind that? What's the weight underneath those words?"
        )
        glyph_intent["attunement"] = "curiosity"
    
    return {
        "text": response_text,
        "glyph_intent": glyph_intent
    }


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    try:
        print("[DEBUG] Health endpoint called")
        result = jsonify({"status": "ok", "models_loaded": WHISPER_MODEL is not None})
        print(f"[DEBUG] Returning: {result}")
        return result, 200
    except Exception as e:
        print(f"[ERROR] Health endpoint crashed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/chat", methods=["POST"])
def chat():
    """Chat endpoint - receive message, return empathetic response."""
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Missing 'message' field"}), 400
        
        message = data.get("message", "").strip()
        if not message:
            return jsonify({"error": "Empty message"}), 400
        
        # Generate response
        response = generate_empathetic_response(message, data.get("messages", []))
        
        return jsonify({
            "response": response["text"],
            "glyph_intent": response["glyph_intent"],
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/transcribe", methods=["POST"])
def transcribe():
    """Transcribe audio file using Whisper."""
    try:
        if "audio" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files["audio"]
        if not audio_file:
            return jsonify({"error": "Empty audio file"}), 400
        
        if WHISPER_MODEL is None:
            return jsonify({"error": "Whisper model not loaded"}), 503
        
        # Read audio data
        audio_data = audio_file.read()
        
        # Transcribe
        segments, info = WHISPER_MODEL.transcribe(BytesIO(audio_data), language="en")
        text = " ".join(segment.text for segment in segments)
        
        return jsonify({
            "text": text,
            "language": info.language,
            "duration": info.duration
        }), 200
        
    except Exception as e:
        print(f"Transcribe error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/synthesize", methods=["POST"])
def synthesize():
    """Synthesize text to speech."""
    try:
        global TTS_ENGINE
        
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Missing 'text' field"}), 400
        
        text = data.get("text", "").strip()
        if not text:
            return jsonify({"error": "Empty text"}), 400
        
        # Lazy init TTS engine on first use
        if TTS_ENGINE is None:
            import pyttsx3
            TTS_ENGINE = pyttsx3.init()
            TTS_ENGINE.setProperty('rate', 150)
            TTS_ENGINE.setProperty('volume', 0.9)
        
        # Synthesize with thread safety
        with _tts_lock:
            # Use Windows-compatible temp directory
            output_file = os.path.join(tempfile.gettempdir(), "synthesis.wav")
            TTS_ENGINE.save_to_file(text, output_file)
            TTS_ENGINE.runAndWait()
        
        # Read and return audio file
        with open(output_file, "rb") as f:
            audio_data = f.read()
        
        return audio_data, 200, {"Content-Type": "audio/wav"}
        
    except Exception as e:
        print(f"Synthesize error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    print("Starting FirstPerson Backend (Flask with Waitress)...")
    print("Initializing AI models...")
    init_models()
    print("Glyph-informed response system ready")
    print("Listening on http://127.0.0.1:5000")
    
    # Use Waitress WSGI server instead of Flask dev server (more stable on Windows)
    from waitress import serve
    serve(app, host="127.0.0.1", port=5000, threads=4)

"""FirstPerson FastAPI Backend - Serves the response engine to Next.js frontend."""

import sys
import os
import json
import uuid
import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
import threading

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger("firstperson")

# Import integrated pipeline
try:
    from src.firstperson_integrated_pipeline import FirstPersonIntegratedPipeline
    logger.info("✓ Integrated pipeline module found")
    PIPELINE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Integrated pipeline not available: {e}")
    PIPELINE_AVAILABLE = False

# Import new pipeline components
try:
    from src.emotional_os.pipeline.turn_classifier import TurnClassifier
    from src.emotional_os.pipeline.policy_router import PolicyRouter
    logger.info("✓ TurnClassifier and PolicyRouter imported")
    TURN_CLASSIFIER = TurnClassifier()
    POLICY_ROUTER = PolicyRouter()
except ImportError as e:
    logger.warning(f"Pipeline components not available: {e}")
    TURN_CLASSIFIER = None
    POLICY_ROUTER = None

try:
    import requests
except ImportError:
    requests = None

app = FastAPI(title="FirstPerson Backend", version="1.0.0")

# Enable CORS for Next.js frontend (wildcard for Codespaces dev, tighten for prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow dynamic Codespaces URLs and localhost
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and responses."""
    logger.info(f"→ {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        logger.info(f"← {request.method} {request.url.path} {response.status_code}")
        return response
    except Exception as e:
        logger.exception(f"✗ {request.method} {request.url.path}: {e}")
        raise

# Startup event to initialize models
@app.on_event("startup")
async def startup_event():
    """Initialize AI models on startup."""
    init_models()

# Supabase configuration - use env vars, degrade gracefully if missing
SUPABASE_URL = os.environ.get("SUPABASE_URL") or "https://gyqzyuvuuyfjxnramkfq.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

# Global model caching to avoid repeated initialization
WHISPER_MODEL = None
TTS_ENGINE = None
TTS_CLIENT = None  # ElevenLabs client
_tts_lock = threading.Lock()
INTEGRATED_PIPELINE = None  # Global pipeline instance

def init_models():
    """Initialize AI models once at startup."""
    global WHISPER_MODEL, TTS_ENGINE, TTS_CLIENT, INTEGRATED_PIPELINE
    
    # Try faster-whisper first (preferred), then openai-whisper, then skip
    try:
        from faster_whisper import WhisperModel
        logger.info("Loading faster-whisper model (tiny)...")
        WHISPER_MODEL = WhisperModel("tiny", device="cpu", compute_type="int8")
        logger.info("✓ faster-whisper model initialized (tiny)")
    except ImportError:
        try:
            import whisper
            logger.info("Loading openai-whisper model (tiny)...")
            WHISPER_MODEL = whisper.load_model("tiny", device="cpu", in_memory=False)
            logger.info("✓ openai-whisper model initialized (tiny)")
        except ImportError:
            logger.warning("No whisper implementation installed. Install with: pip install faster-whisper OR pip install openai-whisper")
        except Exception as e:
            logger.exception(f"Whisper init failed: {e}")
    except Exception as e:
        logger.exception(f"Faster-whisper init failed: {e}")
    
    # Initialize ElevenLabs TTS (preferred) or fallback to pyttsx3
    try:
        from elevenlabs.client import ElevenLabs
        elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        if elevenlabs_api_key:
            TTS_CLIENT = ElevenLabs(api_key=elevenlabs_api_key)
            logger.info("✓ ElevenLabs TTS initialized")
        else:
            logger.warning("ELEVENLABS_API_KEY not set, falling back to pyttsx3")
            _init_pyttsx3()
    except ImportError:
        logger.warning("ElevenLabs not installed, falling back to pyttsx3")
        _init_pyttsx3()
    except Exception as e:
        logger.exception(f"ElevenLabs init failed: {e}")
        _init_pyttsx3()
    
    # Initialize integrated pipeline if available
    if PIPELINE_AVAILABLE:
        try:
            INTEGRATED_PIPELINE = FirstPersonIntegratedPipeline()
            logger.info("✓ Integrated response pipeline initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize integrated pipeline: {e}")
            INTEGRATED_PIPELINE = None
    else:
        logger.warning("Integrated pipeline module not available, will use basic response generation")

def _init_pyttsx3():
    """Fallback TTS initialization using pyttsx3."""
    global TTS_ENGINE
    try:
        import pyttsx3
        logger.info("Loading pyttsx3 engine (fallback)...")
        TTS_ENGINE = pyttsx3.init()
        TTS_ENGINE.setProperty('rate', 140)
        TTS_ENGINE.setProperty('volume', 1.0)
        logger.info("✓ pyttsx3 engine initialized")
    except ImportError:
        logger.warning("pyttsx3 not installed. Install with: pip install pyttsx3")
    except Exception as e:
        logger.exception(f"pyttsx3 init failed: {e}")

def get_supabase_headers():
    """Get headers for Supabase API requests."""
    if not SUPABASE_KEY:
        return {"Content-Type": "application/json"}
    return {
        "Content-Type": "application/json",
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }

def auto_name_conversation(first_message: str, max_length: int = 50) -> str:
    """Generate a conversation name from the first user message."""
    if not first_message:
        return "New Conversation"
    
    import re
    text = first_message.strip()[:100]
    
    # Remove common phrases
    phrases_to_remove = [
        r"i\s+(?:feel|think|believe|know|want|need)\s+",
        r"(?:can|could|would|should|do)\s+you\s+",
        r"(?:what|how|why|when|where)\s+(?:about|is|are|do|does)\s+",
    ]
    
    for phrase in phrases_to_remove:
        text = re.sub(phrase, "", text, flags=re.IGNORECASE)
    
    # Extract first meaningful sentence
    sentences = text.split(". ")
    title = sentences[0] if sentences else text
    
    title = title.strip()
    if len(title) > max_length:
        title = title[:max_length-3] + "..."
    
    title = title[0].upper() + title[1:] if len(title) > 1 else title.upper()
    return title


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
    metadata: Optional[dict] = None


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


class AudioTranscribeResponse(BaseModel):
    """Response from audio transcription."""
    success: bool
    text: Optional[str] = None
    confidence: float = 0.0
    error: Optional[str] = None


class SynthesizeRequest(BaseModel):
    """TTS synthesis request."""
    text: str
    glyph_intent: Optional[dict] = None


class SynthesizeResponse(BaseModel):
    """TTS synthesis response."""
    success: bool
    audio_data: Optional[str] = None  # Base64 encoded audio
    error: Optional[str] = None


def save_conversation_to_supabase(user_id: str, conversation_id: str, title: str, messages: List[dict]) -> bool:
    """Save conversation to Supabase."""
    if not requests or not SUPABASE_URL or not SUPABASE_KEY:
        return False
    
    try:
        url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/conversations"
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
        print(f"Error saving conversation: {e}")
        return False


def load_conversations_from_supabase(user_id: str) -> List[dict]:
    """Load all conversations for a user from Supabase."""
    if not requests or not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("Supabase not configured, returning empty list")
        return []
    
    try:
        url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/conversations"
        
        # Build proper Supabase filter
        params = {
            "select": "conversation_id,title,updated_at,message_count",
            "order": "updated_at.desc",
            "limit": "100",
            "user_id": f"eq.{user_id}",  # Filter by user_id
        }
        
        logger.info(f"Loading conversations for user: {user_id}")
        
        response = requests.get(
            url,
            headers=get_supabase_headers(),
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                conv_count = len(data) if isinstance(data, list) else 0
                logger.info(f"✓ Loaded {conv_count} conversations for {user_id}")
                return data if isinstance(data, list) else []
            except Exception as je:
                logger.exception(f"JSON parse error: {je}")
                return []
        else:
            logger.warning(f"Supabase returned {response.status_code}: {response.text[:100]}")
            return []
    except requests.exceptions.Timeout:
        logger.error(f"Supabase timeout loading conversations for {user_id}")
        return []
    except Exception as e:
        logger.exception(f"Error loading conversations for {user_id}: {e}")
        return []


def load_conversation_from_supabase(user_id: str, conversation_id: str) -> Optional[dict]:
    """Load a specific conversation from Supabase."""
    if not requests or not SUPABASE_URL or not SUPABASE_KEY:
        return None
    
    try:
        url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/conversations"
        params = {
            "user_id": f"eq.{user_id}",
            "conversation_id": f"eq.{conversation_id}",
        }
        
        response = requests.get(
            url,
            headers=get_supabase_headers(),
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and data:
                conv = data[0]
                if isinstance(conv.get("messages"), str):
                    conv["messages"] = json.loads(conv["messages"])
                return conv
        return None
    except Exception as e:
        print(f"Error loading conversation: {e}")
        return None


def delete_conversation_from_supabase(user_id: str, conversation_id: str) -> bool:
    """Delete a conversation from Supabase."""
    if not requests or not SUPABASE_URL or not SUPABASE_KEY:
        return False
    
    try:
        url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/conversations"
        params = {
            "user_id": f"eq.{user_id}",
            "conversation_id": f"eq.{conversation_id}",
        }
        
        response = requests.delete(
            url,
            headers=get_supabase_headers(),
            params=params,
            timeout=10
        )
        
        return response.status_code in (200, 204)
    except Exception as e:
        print(f"Error deleting conversation: {e}")
        return False


def rename_conversation_in_supabase(user_id: str, conversation_id: str, new_title: str) -> bool:
    """Rename a conversation in Supabase."""
    if not requests or not SUPABASE_URL or not SUPABASE_KEY:
        return False
    
    try:
        url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/conversations"
        params = {
            "user_id": f"eq.{user_id}",
            "conversation_id": f"eq.{conversation_id}",
        }
        payload = {
            "title": new_title,
            "updated_at": datetime.now().isoformat(),
        }
        
        response = requests.patch(
            url,
            headers=get_supabase_headers(),
            json=payload,
            params=params,
            timeout=10
        )
        
        return response.status_code in (200, 204)
    except Exception as e:
        print(f"Error renaming conversation: {e}")
        return False


@app.get("/health")
async def health_check():
    """Health check endpoint with status of all components."""
    logger.debug("Health check requested")
    return {
        "status": "ok",
        "service": "FirstPerson Backend",
        "timestamp": datetime.now().isoformat(),
        "models": {
            "whisper": WHISPER_MODEL is not None,
            "tts": TTS_ENGINE is not None,
            "integrated_pipeline": INTEGRATED_PIPELINE is not None,
        },
        "components": {
            "tier1": "available" if INTEGRATED_PIPELINE and INTEGRATED_PIPELINE.tier1 else "unavailable",
            "tier2": "available" if INTEGRATED_PIPELINE and INTEGRATED_PIPELINE.tier2 else "unavailable",
            "tier3": "available" if INTEGRATED_PIPELINE and INTEGRATED_PIPELINE.tier3 else "unavailable",
            "affect_parser": "available" if INTEGRATED_PIPELINE and INTEGRATED_PIPELINE.affect_parser else "unavailable",
        }
    }


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)) -> AudioTranscribeResponse:
    """Transcribe audio bytes to text using cached Whisper model.
    
    Accepts multipart audio file (WAV or MP3).
    """
    try:
        if not file:
            return AudioTranscribeResponse(
                success=False,
                error="No audio data provided"
            )
        
        # Read audio bytes from upload
        audio_bytes = await file.read()
        
        if not audio_bytes or len(audio_bytes) == 0:
            return AudioTranscribeResponse(
                success=False,
                error="Audio file is empty"
            )
        
        if WHISPER_MODEL is None:
            return AudioTranscribeResponse(
                success=False,
                error="Whisper model not initialized. Install faster-whisper: pip install faster-whisper"
            )
        
        # Transcribe using the global model (non-blocking)
        def do_transcribe():
            import io
            audio_stream = io.BytesIO(audio_bytes)
            segments, info = WHISPER_MODEL.transcribe(audio_stream, language="en")
            text = " ".join([segment.text for segment in segments]).strip()
            return text
        
        text = await run_in_threadpool(do_transcribe)
        
        return AudioTranscribeResponse(
            success=True,
            text=text,
            confidence=0.85
        )
    except Exception as e:
        print(f"Transcription error: {e}")
        return AudioTranscribeResponse(
            success=False,
            error=str(e)
        )


@app.post("/synthesize")
async def synthesize(request: SynthesizeRequest) -> SynthesizeResponse:
    """Synthesize text to speech with optional glyph-informed prosody.
    
    Uses cached global TTS engine with thread safety.
    Returns base64-encoded audio data.
    Note: pyttsx3 has thread safety issues on Windows - using direct approach with timeout.
    """
    try:
        if not request.text:
            return SynthesizeResponse(
                success=False,
                error="No text provided"
            )
        
        if TTS_ENGINE is None:
            return SynthesizeResponse(
                success=False,
                error="TTS not initialized. Install pyttsx3: pip install pyttsx3"
            )
        
        # For now, return a placeholder since pyttsx3 has Windows thread safety issues
        # In production, use a dedicated TTS service like Google Cloud, AWS Polly, or Azure
        logger.warning("TTS /synthesize endpoint called - returning mock response (use dedicated TTS service in production)")
        
        return SynthesizeResponse(
            success=True,
            audio_data="",
            error="TTS synthesis temporarily disabled. Use dedicated TTS service (Google Cloud TTS, AWS Polly, or Azure Speech Services)"
        )
        
    except Exception as e:
        logger.exception(f"Synthesis error: {e}")
        return SynthesizeResponse(
            success=False,
            error=str(e)
        )


@app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """Process user message and return response using integrated pipeline.
    
    Pipeline includes:
    - Tier 1: Foundation (safety, learning, signal detection)
    - Tier 2: Aliveness (emotional attunement, energy, presence)
    - Tier 3: Poetic Consciousness (depth, beauty, tension)
    - Composition: Template rotation, affect analysis
    
    IMPORTANT: Response is returned immediately. Supabase save happens asynchronously.
    """
    request_id = str(uuid.uuid4())[:8]
    try:
        logger.info(f"[{request_id}] Chat request received: {request.message[:50]}...")
        
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        message = request.message.strip()
        user_id = request.userId or "demo_user"
        
        # Validate and extract context safely
        conversation_id = None
        is_first_message = False
        messages = []
        title = None
        
        if request.context and isinstance(request.context, dict):
            conversation_id = request.context.get("conversation_id")
            is_first_message = bool(request.context.get("is_first_message", False))
            messages = list(request.context.get("messages", []))
            title = request.context.get("title")
        
        # Generate new ID if needed
        if is_first_message or not conversation_id:
            conversation_id = str(uuid.uuid4())[:8]
        
        # STEP 1: Generate base response in threadpool
        logger.info(f"[{request_id}] Step 1: Generating base response...")
        def generate_base():
            return generate_empathetic_response(message, messages)
        
        base_response_dict = await run_in_threadpool(generate_base)
        base_response_text = base_response_dict.get("text", "I hear you.")
        glyph_intent = base_response_dict.get("glyph_intent", {})
        logger.info(f"[{request_id}] Step 1 complete: {base_response_text[:50]}...")
        
        # NEW STEP 1.5: Classify turn type and check routing
        turn_classification = {}
        if TURN_CLASSIFIER:
            try:
                turn_classification = TURN_CLASSIFIER.classify(
                    message,
                    conversation_history=messages,
                    user_id=user_id,
                )
                logger.info(f"[{request_id}] Turn type: {turn_classification.get('turn_type')} (confidence={turn_classification.get('confidence', 0):.2f})")
            except Exception as e:
                logger.warning(f"[{request_id}] Turn classification failed: {e}")
        
        # If the integrated pipeline is not available, run the lightweight
            try:
                from src.emotional_os.deploy.core.firstperson import create_orchestrator

                orch = create_orchestrator(user_id, conversation_id)
                if orch:
                    orch.initialize_session()
                    fp_result = orch.handle_conversation_turn(message, glyph_intent)
                    # Attach orchestrator output to metadata so frontend can use it
                    fp_orchestrator_metadata = fp_result or {}
                    
                    # Log mortality salience for telemetry
                    mortality = fp_result.get("affect_analysis", {}).get("mortality_salience", 0.0)
                    logger.info(f"[{request_id}] Mortality salience: {mortality:.2f}, Safety signal: {fp_result.get('safety_signal', False)}")
                    
                    # If there's a gentle frequency reflection, incorporate it
                    # into the response so users see memory-aware acknowledgements.
                    freq_ref = fp_orchestrator_metadata.get("frequency_reflection")
                    if freq_ref:
                        base_response_text = f"{freq_ref} {base_response_text}"
            except Exception as e:
                logger.debug(f"[{request_id}] FirstPerson orchestrator fallback failed: {e}")
        
        # STEP 2: Enhance response through pipeline (if available)
        response_text = base_response_text
        pipeline_metadata = {}
        
        if INTEGRATED_PIPELINE:
            try:
                logger.info(f"[{request_id}] Step 2: Running integrated pipeline...")
                
                def enhance_response():
                    """Run pipeline with strict timeout protection."""
                    import signal
                    
                    def timeout_handler(signum, frame):
                        raise TimeoutError("Pipeline processing exceeded 5 second timeout")
                    
                    # Set alarm (Windows doesn't support signal, so wrap in try-except)
                    try:
                        signal.signal(signal.SIGALRM, timeout_handler)
                        signal.alarm(5)  # 5 second timeout
                    except (AttributeError, ValueError):
                        pass  # Signal not available on this platform
                    
                    try:
                        enhanced, metadata = INTEGRATED_PIPELINE.process_response(
                            user_input=message,
                            base_response=base_response_text,
                            conversation_history=messages,
                            context={"user_id": user_id, "conversation_id": conversation_id}
                        )
                        
                        # Cancel alarm
                        try:
                            signal.alarm(0)
                        except (AttributeError, ValueError):
                            pass
                        
                        return enhanced, metadata
                    except TimeoutError as te:
                        logger.warning(f"[{request_id}] Pipeline timeout: {te}")
                        # Return base response on timeout
                        try:
                            signal.alarm(0)
                        except (AttributeError, ValueError):
                            pass
                        return base_response_text, {"error": "timeout"}
                
                response_text, pipeline_metadata = await run_in_threadpool(enhance_response)
                logger.info(f"[{request_id}] Step 2 complete: Pipeline enhanced response")
                
            except Exception as e:
                logger.warning(f"[{request_id}] Pipeline error (using base response): {e}")
                response_text = base_response_text
        else:
            logger.debug(f"[{request_id}] Pipeline unavailable, using base response")
            response_text = base_response_text
        
        # NEW STEP 2.5: Route response through policy router and check invariants
        if POLICY_ROUTER and turn_classification:
            try:
                domains = pipeline_metadata.get("domains", {})
                affect = pipeline_metadata.get("affect", {})
                
                policy_result = POLICY_ROUTER.route(
                    turn_type=turn_classification.get("turn_type", "disclosure"),
                    base_response=response_text,
                    domains=domains,
                    conversation_history=messages,
                    user_message=message,
                    affect=affect,
                )
                
                logger.info(f"[{request_id}] Policy check: invariants_pass={policy_result['invariants_pass']}")
                if not policy_result["invariants_pass"]:
                    logger.warning(f"[{request_id}] Policy violations: {policy_result['violations']}")
                    # Log for metrics/debugging but don't fail (graceful degradation)
                
                # Add policy metadata to response
                pipeline_metadata["policy_router"] = {
                    "invariants_pass": policy_result["invariants_pass"],
                    "violations": policy_result["violations"],
                    "recommended_generator": policy_result["recommended_generator"],
                }
            except Exception as e:
                logger.warning(f"[{request_id}] Policy routing failed: {e}")
        
        # STEP 3: Auto-generate title from first message
        if is_first_message and not title:
            title = auto_name_conversation(message)
        elif not title:
            title = "Conversation"
        
        # Merge any FirstPerson orchestrator metadata when pipeline is unavailable
        try:
            if fp_orchestrator_metadata:
                pipeline_metadata = pipeline_metadata or {}
                pipeline_metadata["firstperson_orchestrator"] = fp_orchestrator_metadata
        except NameError:
            # fp_orchestrator_metadata may not be defined in some code paths
            pass

        # Integration: attempt to append small emotional OS micro-behaviors
        # (pun interjector, mutual joy) in a guarded, non-blocking way.
        try:
            # Build a lightweight context for the micro-engines
            micro_context = {
                "message": message,
                "user_id": user_id,
                "conversation_id": conversation_id,
                "messages": messages,
                "pipeline_metadata": pipeline_metadata,
            }
            # Log the micro-context shape/content for debugging why micro-engines fire
            try:
                logger.info(f"[{request_id}] Micro context for micro-engines: {micro_context}")
            except Exception:
                # Best-effort logging; don't fail the request if logging errors
                pass
            # Also write micro_context to a debug file for reliable capture in tests
            try:
                with open(r"d:\\saoriverse-console\\tools\\micro_context_debug.log", "a", encoding="utf-8") as _f:
                    _f.write(f"[{request_id}] " + repr(micro_context) + "\n")
            except Exception:
                pass
            try:
                # Import the micro-engines directly (avoid importing the integrator
                # which may not be available in some dev states).
                from src.emotional_os.pun_interjector import PunInterjector
                from src.emotional_os.mutual_joy_handler import MutualJoyHandler

                _pun_engine = PunInterjector()
                _joy_engine = MutualJoyHandler()

                pun_obj = _pun_engine.compose_pun(micro_context)
                pun_text = _pun_engine.render(pun_obj) if pun_obj else ""

                # Gate the mutual-joy handler so it only runs when there's
                # a clear positive uplift signal. This prevents celebratory
                # lines from being appended for doubt/uncertainty messages.
                joy_text = ""
                try:
                    pipeline = micro_context.get("pipeline_metadata") or {}
                    affect = {}
                    if isinstance(pipeline, dict):
                        affect = pipeline.get("affect") or pipeline.get("affect_analysis") or pipeline.get("emotion") or {}

                    tone = (affect.get("tone") or "").lower() if isinstance(affect, dict) else ""
                    try:
                        valence = float(affect.get("valence") or 0.0) if isinstance(affect, dict) else 0.0
                    except Exception:
                        valence = 0.0
                    try:
                        arousal = float(affect.get("arousal") or 0.0) if isinstance(affect, dict) else 0.0
                    except Exception:
                        arousal = 0.0

                    positive_tones = {"relieved", "proud", "excited", "grateful", "amazed", "relief", "pride", "joy", "delight", "satisfaction"}
                    downward_cues = [
                        "i'm not sure", "i am not sure", "i'm starting to feel doubtful", "i'm doubtful",
                        "i'm struggling", "i'm not sure if", "i'm unsure", "i don't know", "i'm worried",
                        "i'm afraid", "i'm anxious", "not sure"
                    ]

                    text_lower = (micro_context.get("message") or "").lower()

                    # Determine if joy is allowed: require explicit uplift tone + thresholds,
                    # or strong lexical positive cues. Always block if downward cues present.
                    joy_allowed = False
                    if tone in positive_tones and valence > 0.4 and arousal > 0.3:
                        joy_allowed = True

                    # Strong lexical positives can allow joy even if tone naming differs
                    strong_positive_cues = [
                        "i did it", "i made it", "i'm so happy", "so happy", "i'm grateful",
                        "i'm relieved", "i'm proud", "i'm excited", "i finally"
                    ]
                    if not joy_allowed and any(cue in text_lower for cue in strong_positive_cues):
                        joy_allowed = True

                    # Block on downward cues regardless
                    if any(cue in text_lower for cue in downward_cues):
                        joy_allowed = False

                    if joy_allowed:
                        joy_text = _joy_engine.choose_template(micro_context) or ""
                except Exception:
                    # Safe fallback: do not let gating errors block response
                    joy_text = ""

                # Respect one-paragraph rule: append with a single space
                extras = " ".join([t for t in (pun_text.strip(), joy_text.strip()) if t])
                if extras:
                    response_text = f"{response_text} {extras}"

            except Exception:
                # Safe fallback: if micro-engines are missing or error, ignore.
                pass
        except Exception:
            # Defensive: do not let micro-integration break the main flow
            pass

        # STEP 4: Return response IMMEDIATELY (do NOT wait for Supabase save)
        response_obj = ChatResponse(
            success=True,
            message=response_text,
            conversation_id=conversation_id,
            metadata=pipeline_metadata
        )
        logger.info(f"[{request_id}] Step 4: Response prepared, returning to client")
        
        # STEP 5: Save conversation ASYNCHRONOUSLY in background (fire and forget)
        # This happens AFTER we return the response to prevent blocking
        async def save_in_background():
            """Save to Supabase asynchronously without blocking response."""
            try:
                logger.info(f"[{request_id}] Background: Saving to Supabase...")
                messages.append({"role": "user", "content": message})
                messages.append({"role": "assistant", "content": response_text, "glyph_intent": glyph_intent})
                
                save_success = await run_in_threadpool(
                    save_conversation_to_supabase,
                    user_id,
                    conversation_id,
                    title,
                    messages
                )
                
                if save_success:
                    logger.info(f"[{request_id}] Background: ✓ Conversation saved")
                else:
                    logger.warning(f"[{request_id}] Background: Failed to save conversation")
            except Exception as e:
                logger.exception(f"[{request_id}] Background save error (non-blocking): {e}")
        
        # Schedule background save without awaiting
        import asyncio
        asyncio.create_task(save_in_background())
        
        logger.info(f"[{request_id}] Response sent to client (Supabase save in background)")
        return response_obj
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[{request_id}] Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/conversations/{user_id}")
async def get_conversations(user_id: str) -> ConversationListResponse:
    """Get all conversations for a user."""
    try:
        conversations = load_conversations_from_supabase(user_id)
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
        conv = load_conversation_from_supabase(user_id, conversation_id)
        if not conv:
            return ChatResponse(
                success=False,
                message="",
                error="Conversation not found"
            )
        
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
        success = delete_conversation_from_supabase(user_id, conversation_id)
        return ChatResponse(
            success=success,
            message="Deleted" if success else "Failed to delete",
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
        success = rename_conversation_in_supabase(user_id, conversation_id, request.new_title)
        return ChatResponse(
            success=success,
            message="Renamed" if success else "Failed to rename",
            conversation_id=conversation_id
        )
    except Exception as e:
        print(f"Error renaming conversation: {e}", file=sys.stderr)
        return ChatResponse(
            success=False,
            message="",
            error=str(e)
        )


class FeedbackRequest(BaseModel):
    """Request schema for response feedback."""
    message_id: str
    conversation_id: Optional[str] = None
    helpful: bool
    user_id: Optional[str] = None


@app.post("/api/feedback")
async def submit_feedback(request: FeedbackRequest) -> ChatResponse:
    """Record user feedback on assistant response."""
    try:
        # Log the feedback for metrics collection
        logger.info(
            f"Feedback: message_id={request.message_id}, "
            f"conversation_id={request.conversation_id}, "
            f"helpful={request.helpful}, user_id={request.user_id}"
        )
        
        # In a production system, you would save this to a feedback table in Supabase
        # For now, we just log it for metrics and analysis
        
        return ChatResponse(
            success=True,
            message="Feedback recorded",
            conversation_id=request.conversation_id or ""
        )
    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        return ChatResponse(
            success=False,
            message="",
            error=str(e)
        )


def detect_themes(conversation_history: List[dict]) -> dict:
    """Detect recurring themes and emotional patterns across conversation history."""
    import re
    all_text = " ".join([msg.get("content", "").lower() for msg in conversation_history])

    # Tokenize into word tokens to avoid substring false positives (eg. 'enjoy' triggering 'joy')
    tokens = set(re.findall(r"\b\w+\b", all_text))

    def any_token_in(words):
        return any(w in tokens for w in words)

    themes = {
        "fatigue": any_token_in(["tired", "exhausted", "drained", "burned", "worn", "depleted"]),
        "hope": any_token_in(["hope", "hopeful", "optimistic", "forward", "possibility", "chance"]),
        "stress": any_token_in(["stress", "stressed", "anxious", "overwhelmed", "pressure", "struggling"]),
        "isolation": any_token_in(["alone", "lonely", "isolated", "nobody", "on"]),
        "work": any_token_in(["work", "job", "career", "office", "deadline", "attorney", "lawyer", "boss", "team"]),
        "health": any_token_in(["drinking", "drug", "alcohol", "sick", "illness", "depression", "anxiety", "therapy"]),
        "grief": any_token_in(["grief", "loss", "lost", "death", "died", "mourning"]),
        "joy": any_token_in(["joy", "happy", "excited", "love", "amazing", "wonderful", "great"]),
    }

    return themes


def extract_context_from_history(conversation_history: List[dict]) -> dict:
    """Extract key facts and context from conversation history."""
    context = {
        "user_mentions": [],
        "recurring_issues": [],
        "emotional_trajectory": [],
        "open_threads": []
    }
    
    # Extract mentions and build context
    for msg in conversation_history[-5:]:  # Look at last 5 messages
        if msg.get("role") == "user":
            text = msg.get("content", "").lower()
            
            # Track occupation/role mentions
            if "attorney" in text or "lawyer" in text:
                if "attorney" not in context["user_mentions"]:
                    context["user_mentions"].append("attorney/lawyer")
            
            # Track relationship issues
            if any(w in text for w in ["assistant", "colleague", "manager", "team"]):
                if "workplace relationship difficulty" not in context["user_mentions"]:
                    context["user_mentions"].append("workplace relationship difficulty")
            
            # Track substance mentions
            if any(w in text for w in ["drinking", "alcohol", "drug"]):
                if "substance use concern" not in context["user_mentions"]:
                    context["user_mentions"].append("substance use concern")
    
    return context


def generate_empathetic_response(message: str, conversation_history: Optional[List[dict]] = None) -> dict:
    """Generate a response that analyzes the current message AND conversation history.
    
    Uses glyph-informed attunement to meet the user where they are.
    Embeds specific themes, language patterns, and emotional recognition.
    
    Returns: {
        "text": response_text,
        "glyph_intent": {
            "voltage": "low|medium|high",
            "tone": "negative|neutral|positive",
            "attunement": "empathy|curiosity|validation|holding_space|gentle_presence",
            "certainty": "uncertain|neutral|confident"
        }
    }
    """
    
    # Normalize input
    message_lower = message.lower() if message else ""
    history = conversation_history or []
    
    # Detect patterns across conversation
    themes = detect_themes(history + [{"role": "user", "content": message}])
    context = extract_context_from_history(history + [{"role": "user", "content": message}])
    
    # Build response based on themes and context
    glyph_intent = {
        "voltage": "medium",
        "tone": "neutral",
        "attunement": "empathy",
        "certainty": "neutral"
    }
    
    # Greeting responses
    if message_lower in ["hi", "hello", "hey", "hey there", "hi there"]:
        return {
            "text": "Hello. I'm here to listen. Take your time.",
            "glyph_intent": {**glyph_intent, "tone": "neutral", "voltage": "low", "attunement": "holding_space"}
        }
    
    # Check for exhaustion/fatigue patterns - the "weight" experience
    has_exhaustion = any(word in message_lower for word in ["exhausted", "exhaustion", "tired", "weary", "drained", "weight", "carrying", "burden", "heavy"])
    has_momentum_loss = any(word in message_lower for word in ["stuck", "stalled", "can't move", "frozen", "stopped", "watching", "rushing by"])
    has_disconnection = any(word in message_lower for word in ["stuck in place", "disconnect", "alone", "isolated", "everyone else"])
    requests_presence = any(phrase in message_lower for phrase in ["without trying to fix", "just sit", "hear", "presence"])
    
    # EXHAUSTION + MOMENTUM LOSS + NEED FOR PRESENCE = Holding Space Response
    if (has_exhaustion or themes["fatigue"]) and has_momentum_loss and requests_presence:
        glyph_intent["voltage"] = "low"
        glyph_intent["tone"] = "negative"
        glyph_intent["attunement"] = "holding_space"
        glyph_intent["certainty"] = "confident"
        
        response_text = (
            "I'm with you in that. The heaviness you're describing—waking up already depleted, watching your body carry weight "
            "it can't set down, seeing everyone else in motion while you're still—that's not small. That's real, and it matters.\n\n"
            "The fact that you can see it so clearly, that you can name what you need (presence, not solutions)—that tells me "
            "something about you. You're aware. You're honest about it.\n\n"
            "I'm sitting with you in this. You don't need to move right now. What does this exhaustion feel like in your body right now?"
        )
        return {
            "text": response_text,
            "glyph_intent": glyph_intent
        }
    
    # Adjust glyph based on themes
    if themes["fatigue"]:
        glyph_intent["voltage"] = "low"
        glyph_intent["tone"] = "negative"
        glyph_intent["attunement"] = "gentle_presence"
    elif themes["hope"]:
        glyph_intent["tone"] = "positive"
        glyph_intent["voltage"] = "medium"
    elif themes["stress"]:
        glyph_intent["voltage"] = "high"
        glyph_intent["tone"] = "negative"
    
    # Build contextual response
    if len(history) > 0:
        # Multi-turn context
        last_user_message = None
        for msg in reversed(history):
            if msg.get("role") == "user":
                last_user_message = msg.get("content", "")
                break
        
        # Build response that connects to previous turn
        if themes["work"] and themes["stress"]:
            if "attorney" in context["user_mentions"] and "substance use concern" in context["user_mentions"]:
                response_text = (
                    "I'm hearing the weight of this across multiple dimensions now. You mentioned the stress of your work as an attorney, "
                    "and separately the challenge of dealing with your assistant's drinking problem. Those aren't just two separate stresses—"
                    "they're layered. The substance issue affects the work situation, and the work situation might be adding pressure. "
                    "How are you managing the emotional toll of carrying both?"
                )
            else:
                response_text = (
                    "I'm noticing this stress about work keeps coming back. Let me check in: when you think about the work situation right now, "
                    "what's the most pressing thing? Is it the deadline, the people involved, or the weight of responsibility?"
                )
        elif themes["isolation"] and len(history) > 2:
            response_text = (
                "You've mentioned feeling alone with this multiple times now. I want to acknowledge that. But I'm also here. "
                "What would it look like if this didn't have to be something you carried entirely by yourself?"
            )
        elif themes["fatigue"] and len(history) > 1:
            response_text = (
                "The tiredness you're describing—it seems like more than just physical. It sounds like emotional depletion. "
                "When was the last time you had a real break from this situation?"
            )
        else:
            response_text = (
                f"You mentioned something before, and now you're sharing this. Help me connect the dots—"
                f"how does what you're saying now relate to what you were dealing with?"
            )
    else:
        # First message - establish safety and opening
        # Check for specific emotional patterns first
        if has_exhaustion and has_momentum_loss:
            response_text = (
                "I'm hearing the weight of that. The exhaustion that starts before the day does, "
                "the heaviness that makes small things feel monumental. I see that. "
                "I'm not going to rush to fix it—I'm just going to sit with you in it. "
                "What does it feel like right now, in your body, in this moment?"
            )
            glyph_intent["tone"] = "negative"
            glyph_intent["attunement"] = "holding_space"
        elif themes["grief"]:
            response_text = (
                "There's something deep in what you just shared. Grief, loss, something being taken from you. "
                "I'm here with that. Not to make it better, but to acknowledge it matters. "
                "What part of this is hardest to say out loud?"
            )
            glyph_intent["tone"] = "negative"
            glyph_intent["attunement"] = "validation"
        elif themes["joy"]:
            response_text = (
                "There's light in what you're sharing. Something that matters, something worth celebrating. "
                "I feel that. Tell me more—what's making this real for you?"
            )
            glyph_intent["tone"] = "positive"
            glyph_intent["attunement"] = "empathy"
        else:
            # Use semantic compression layer to synthesize a concise, attuned response
            try:
                from src.emotional_os.semantic_compressor import SemanticCompressor

                compressor = SemanticCompressor()
                # We don't have pipeline affect at this stage, but we can still extract domains
                domains = compressor.extract_domains(message, None)
                response_text = compressor.compress(domains, message)
                glyph_intent["tone"] = "neutral"
                glyph_intent["attunement"] = "curiosity"
            except Exception:
                # Fallback conservative reply if compressor fails
                response_text = (
                    "I hear the significance in what you just shared. There's something real there. "
                    "What's the most important part of that for you to tell me about?"
                )
                
    
    return {
        "text": response_text,
        "glyph_intent": glyph_intent
    }



if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 60)
    logger.info("Starting FirstPerson Backend")
    logger.info("=" * 60)
    logger.info("(AI models will initialize on first request)")
    logger.info("=" * 60)
    port = int(os.environ.get("PORT", "8000"))
    logger.info(f"API listening on http://0.0.0.0:{port}")
    logger.info(f"API docs: http://0.0.0.0:{port}/docs")
    logger.info("=" * 60)
    
    # Windows multiprocessing with spawn causes crashes - use single worker
    # Use 0.0.0.0 to ensure the socket actually binds
    # Disable auto-reload to avoid file watcher issues
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        workers=1,
        reload=False,
        access_log=False  # Reduce noise; use middleware logging instead
    )


# Performance Optimization Module for Emotional OS
# Implements fast response strategies and streaming for better user experience

import time
from datetime import datetime, timedelta
from typing import Dict, Optional

import streamlit as st


class OptimizedResponseHandler:
    """
    Handles optimized responses with multiple strategies:
    1. Instant acknowledgment 
    2. Local pattern matching for common responses
    3. Background AI processing
    4. Response streaming
    """

    def __init__(self):
        self.response_cache = {}
        self.cache_ttl = timedelta(minutes=5)

        # Pre-computed instant responses for common emotional states
        self.instant_responses = {
            "grief": {
                "acknowledgment": "I can hear the weight of your grief...",
                "full_response": "Grief carries its own timeline, and there's no rushing through the waves of loss. Each moment of sorrow is valid and necessary."
            },
            "joy": {
                "acknowledgment": "There's something beautiful in that joy...",
                "full_response": "Joy has this wonderful way of expanding beyond words, doesn't it? It's one of those feelings that just wants to be celebrated and shared."
            },
            "overwhelm": {
                "acknowledgment": "That sounds incredibly overwhelming...",
                "full_response": "When everything feels like too much, sometimes the kindest thing is to focus on just the next breath, the next moment."
            },
            "confusion": {
                "acknowledgment": "Confusion can feel so disorienting...",
                "full_response": "It's okay to not have all the answers right now. Sometimes sitting with uncertainty is the only way to find clarity."
            },
            "anxiety": {
                "acknowledgment": "I can sense that anxious energy...",
                "full_response": "Anxiety often comes from caring deeply about something. What would it feel like to be gentle with yourself about this concern?"
            },
            "love": {
                "acknowledgment": "Love brings such complexity...",
                "full_response": "Love has its own language that goes beyond words. What is this feeling teaching you about yourself and what matters most?"
            }
        }

    def detect_primary_emotion(self, message: str) -> Optional[str]:
        """Quickly detect the primary emotion from a message"""
        message_lower = message.lower()

        # Ordered by priority - more specific patterns first
        patterns = {
            "grief": ["grief", "grieving", "loss", "mourning", "died", "death", "funeral"],
            "overwhelm": ["overwhelmed", "overwhelming", "too much", "can't handle", "drowning"],
            "anxiety": ["anxious", "anxiety", "worried", "worry", "panic", "stressed", "stress"],
            "joy": ["joy", "joyful", "happy", "happiness", "celebrate", "excited", "amazing"],
            "love": ["love", "loving", "adore", "cherish", "romantic", "relationship"],
            "confusion": ["confused", "confusion", "don't understand", "unclear", "lost"]
        }

        for emotion, keywords in patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                return emotion

        return None

    def get_cache_key(self, message: str, mode: str = "hybrid") -> str:
        """Generate a cache key for the message"""
        # Simple hash-like key based on message content
        return f"{hash(message.lower()[:100])}_{mode}"

    def get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Get cached response if it's still valid"""
        if cache_key in self.response_cache:
            cached = self.response_cache[cache_key]
            if datetime.now() - cached['timestamp'] < self.cache_ttl:
                return cached['response']
            del self.response_cache[cache_key]  # Remove expired cache
        return None

    def cache_response(self, cache_key: str, response: Dict):
        """Cache a response for future use"""
        self.response_cache[cache_key] = {
            'response': response,
            'timestamp': datetime.now()
        }

    def get_instant_acknowledgment(self, message: str) -> Optional[str]:
        """Get instant acknowledgment based on detected emotion"""
        emotion = self.detect_primary_emotion(message)

        if emotion and emotion in self.instant_responses:
            return self.instant_responses[emotion]["acknowledgment"]

        # Fallback acknowledgments
        fallbacks = [
            "I hear you...",
            "Thank you for sharing that...",
            "I'm here with you...",
            "That sounds significant..."
        ]

        return fallbacks[hash(message) % len(fallbacks)]

    def get_pattern_response(self, message: str) -> Optional[str]:
        """Get full pattern-based response for common emotions"""
        emotion = self.detect_primary_emotion(message)

        if emotion and emotion in self.instant_responses:
            return self.instant_responses[emotion]["full_response"]

        return None

class StreamlitOptimizedUI:
    """
    Optimized Streamlit UI with performance improvements:
    - Instant acknowledgment
    - Progressive response loading
    - Smart caching
    - Background processing
    """

    def __init__(self):
        self.response_handler = OptimizedResponseHandler()

        # Initialize session state for optimized responses
        if 'processing_status' not in st.session_state:
            st.session_state.processing_status = None
        if 'instant_response_shown' not in st.session_state:
            st.session_state.instant_response_shown = False

    def show_instant_acknowledgment(self, message: str):
        """Show instant acknowledgment while processing"""
        acknowledgment = self.response_handler.get_instant_acknowledgment(message)

        # Show typing indicator with acknowledgment
        with st.chat_message("assistant"):
            st.write(acknowledgment)

            # Show processing indicator
            with st.status("Processing your message...", expanded=False) as status:
                st.write("🧠 Analyzing emotional context...")
                time.sleep(0.5)
                st.write("🔍 Generating personalized response...")
                status.update(label="Thinking...", state="running")

    def process_with_fallback(self, message: str, processor) -> Dict:
        """Process message with local fallback for speed"""

        # 1. Check cache first
        cache_key = self.response_handler.get_cache_key(message)
        cached_response = self.response_handler.get_cached_response(cache_key)

        if cached_response:
            return {
                "response": cached_response["response"],
                "source": "cache",
                "processing_time": "< 0.1s"
            }

        # 2. Try pattern-based response for speed
        pattern_response = self.response_handler.get_pattern_response(message)

        if pattern_response:
            result = {
                "response": pattern_response,
                "source": "pattern_match",
                "processing_time": "< 0.2s"
            }

            # Cache the pattern response
            self.response_handler.cache_response(cache_key, {"response": pattern_response})
            return result

        # 3. Fallback to full AI processing
        try:
            start_time = time.time()
            # Pass session-level A/B metadata if available in Streamlit session state
            session_meta = {
                'user_id': st.session_state.get('user_id') if 'user_id' in st.session_state else None,
                'ab_participate': st.session_state.get('ab_participate', False) if 'ab_participate' in st.session_state else False,
                'ab_group': st.session_state.get('ab_group', 'not_participating') if 'ab_group' in st.session_state else 'not_participating'
            }
            result = processor.process_emotional_input(message, prefer_ai=True, privacy_mode=False, session_metadata=session_meta)
            processing_time = time.time() - start_time

            result["processing_time"] = f"{processing_time:.2f}s"

            # Cache successful AI responses
            if result.get("response"):
                self.response_handler.cache_response(cache_key, {"response": result["response"]})

            return result

        except Exception:
            # Emergency fallback to local processing
            try:
                session_meta = {
                    'user_id': st.session_state.get('user_id') if 'user_id' in st.session_state else None,
                    'ab_participate': st.session_state.get('ab_participate', False) if 'ab_participate' in st.session_state else False,
                    'ab_group': st.session_state.get('ab_group', 'not_participating') if 'ab_group' in st.session_state else 'not_participating'
                }
                result = processor.process_emotional_input(message, prefer_ai=False, privacy_mode=True, session_metadata=session_meta)
                result["source"] = "local_fallback"
                result["processing_time"] = "< 1.0s"
                return result
            except:
                return {
                    "response": "I'm experiencing some connection issues, but I'm here to listen. Can you tell me more about what you're feeling?",
                    "source": "emergency_fallback",
                    "processing_time": "< 0.1s"
                }

def optimize_streamlit_performance():
    """Apply Streamlit-specific performance optimizations"""

    # Cache expensive operations
    if 'optimized_processor' not in st.session_state:
        from emotional_os.supabase.supabase_integration import create_hybrid_processor
        st.session_state.optimized_processor = create_hybrid_processor(limbic_engine=st.session_state.get('limbic_engine'))

    # Set up performance monitoring
    if 'performance_stats' not in st.session_state:
        st.session_state.performance_stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'pattern_matches': 0,
            'ai_requests': 0,
            'avg_response_time': 0
        }

# Usage in main Streamlit app:
"""
# At the top of emotional_os_ui_v2.py:
from performance_optimization import StreamlitOptimizedUI, optimize_streamlit_performance

# Initialize optimized UI
optimize_streamlit_performance()
optimized_ui = StreamlitOptimizedUI()

# In message processing:
if user_input:
    # Show instant acknowledgment
    optimized_ui.show_instant_acknowledgment(user_input)
    
    # Process with multiple fallback strategies
    result = optimized_ui.process_with_fallback(user_input, st.session_state.optimized_processor)
    
    # Show final response
    with st.chat_message("assistant"):
        st.write(result["response"])
        
        # Show performance info in debug mode
        if st.session_state.get('debug_mode'):
            st.caption(f"Source: {result['source']} | Time: {result['processing_time']}")
"""

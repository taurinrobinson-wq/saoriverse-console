"""
Tier 2: Aliveness Layer
========================

Creates emotional presence and real-time adaptivity in responses.

Components:
1. AttunementLoop - Real-time emotional synchronization
2. EmotionalReciprocity - Mirroring user's emotional intensity
3. EmbodiedSimulation - Physical presence metaphors
4. EnergyTracker - Conversation energy management

Performance Target: <30ms total per component
Combined with Tier 1: <70ms for full response processing
"""

import logging
import time
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)


class AttunementLoop:
    """
    Real-time emotional synchronization with user input.
    
    Detects shifts in user's emotional tone and adjusts response
    energy to match, creating sense of being "with" the user.
    """
    
    def __init__(self):
        """Initialize AttunementLoop."""
        self.last_tone = "neutral"
        self.tone_history = []
        self.max_history = 10
        
        # Tone markers (expanded from Tier 1)
        self.tone_markers = {
            "joyful": ["happy", "excited", "wonderful", "amazing", "love", "fantastic", "great"],
            "anxious": ["worried", "anxious", "afraid", "scared", "nervous", "unsure"],
            "sad": ["sad", "depressed", "down", "hurt", "lonely", "miserable"],
            "angry": ["angry", "frustrated", "furious", "disgusted", "annoyed"],
            "reflective": ["think", "wonder", "question", "consider", "reflect"],
            "uncertain": ["maybe", "perhaps", "not sure", "unclear", "confused"],
        }
    
    def detect_tone_shift(self, user_input: str, history: Optional[List[Dict]] = None) -> str:
        """
        Detect shifts in user's emotional tone.
        
        Args:
            user_input: Current user message
            history: Conversation history for context
            
        Returns:
            Current tone ("joyful", "anxious", "sad", "angry", "reflective", "uncertain", "neutral")
        """
        try:
            user_lower = user_input.lower()
            detected_tones = []
            
            # Check for tone markers
            for tone, markers in self.tone_markers.items():
                for marker in markers:
                    if marker in user_lower:
                        detected_tones.append(tone)
                        break
            
            # If multiple tones detected, use most recent pattern
            if detected_tones:
                current_tone = detected_tones[0]
            else:
                current_tone = "neutral"
            
            # Check for tone shift (change from last message)
            if self.last_tone and self.last_tone != current_tone:
                self.tone_history.append({
                    "from": self.last_tone,
                    "to": current_tone,
                    "timestamp": datetime.now(),
                    "intensity": len(detected_tones) / max(len(self.tone_markers), 1)
                })
            
            # Keep history limited
            if len(self.tone_history) > self.max_history:
                self.tone_history.pop(0)
            
            self.last_tone = current_tone
            return current_tone
            
        except Exception as e:
            logger.warning(f"Tone shift detection failed: {e}")
            return "neutral"
    
    def get_current_attunement(self) -> Dict:
        """
        Get current attunement state.
        
        Returns:
            Dict with current tone, shift info, and adaptation guidance
        """
        try:
            result = {
                "current_tone": self.last_tone,
                "has_shifted": len(self.tone_history) > 0,
                "recent_shifts": len([t for t in self.tone_history 
                                     if (datetime.now() - t["timestamp"]).seconds < 300]),
                "recommended_energy": self._get_energy_for_tone(self.last_tone)
            }
            return result
        except Exception as e:
            logger.warning(f"Get attunement failed: {e}")
            return {"current_tone": "neutral", "recommended_energy": 0.5}
    
    def adjust_response_for_attunement(self, response: str, attunement: str) -> str:
        """
        Adjust response tone to match detected attunement.
        
        Args:
            response: Original response
            attunement: Target tone
            
        Returns:
            Adjusted response
        """
        try:
            if attunement == "joyful":
                # Add warmth and enthusiasm
                response = response.replace(".", "! ")
                response = response.replace("could", "can")
                response = response.replace("might", "will")
            
            elif attunement == "anxious":
                # Add reassurance and gentleness
                response = self._add_reassurance(response)
                response = response.replace("!", ".")
            
            elif attunement == "sad":
                # Add empathy and support
                response = self._add_empathy(response)
                response = response.replace("!", ".")
            
            elif attunement == "reflective":
                # Add thoughtful pacing
                response = self._add_contemplation(response)
            
            return response.strip()
            
        except Exception as e:
            logger.warning(f"Response adjustment failed: {e}")
            return response
    
    def _get_energy_for_tone(self, tone: str) -> float:
        """Get recommended energy level for tone."""
        energy_map = {
            "joyful": 0.9,
            "anxious": 0.4,
            "sad": 0.3,
            "angry": 0.7,
            "reflective": 0.5,
            "uncertain": 0.4,
            "neutral": 0.5
        }
        return energy_map.get(tone, 0.5)
    
    def _add_reassurance(self, response: str) -> str:
        """Add reassuring language to response."""
        reassurances = [
            "It's okay. ",
            "You're not alone. ",
            "I'm here. ",
            "That's understandable. ",
        ]
        if response and response[0].isupper():
            return reassurances[0] + response
        return response
    
    def _add_empathy(self, response: str) -> str:
        """Add empathetic language to response."""
        empathies = [
            "I hear you. ",
            "That sounds difficult. ",
            "I understand. ",
            "That's a lot to feel. ",
        ]
        if response and response[0].isupper():
            return empathies[0] + response
        return response
    
    def _add_contemplation(self, response: str) -> str:
        """Add contemplative pacing to response."""
        if "..." not in response:
            response = response.replace(". ", "... ")
        return response


class EmotionalReciprocity:
    """
    Mirror and build on user's emotional intensity.
    
    Creates conversational momentum by reflecting emotional patterns
    and adjusting response intensity to match user engagement.
    """
    
    def __init__(self):
        """Initialize EmotionalReciprocity."""
        self.intensity_history = []
        self.max_history = 20
        self.current_intensity = 0.5
        
        # Intensity markers
        self.intense_markers = {
            "high": ["!", "!!!", "?", "???", "absolutely", "definitely", "must", "critical"],
            "medium": ["important", "should", "consider", "probably", "likely"],
            "low": ["maybe", "perhaps", "seem", "might", "could"],
        }
    
    def measure_intensity(self, user_input: str) -> float:
        """
        Measure user's emotional intensity (0.0 - 1.0).
        
        Args:
            user_input: User message
            
        Returns:
            Intensity score from 0.0 (minimal) to 1.0 (maximum)
        """
        try:
            intensity = 0.5  # baseline
            user_lower = user_input.lower()
            
            # Exclamation marks
            intensity += 0.1 * min(user_input.count("!"), 3)
            
            # Question marks (shows engagement)
            intensity += 0.05 * min(user_input.count("?"), 3)
            
            # ALL CAPS words (shows emphasis)
            caps_words = len([w for w in user_input.split() if w.isupper() and len(w) > 1])
            intensity += 0.05 * min(caps_words, 3)
            
            # Check intensity markers
            for level, markers in self.intense_markers.items():
                for marker in markers:
                    if marker in user_lower:
                        if level == "high":
                            intensity += 0.1
                        elif level == "low":
                            intensity -= 0.05
            
            # Message length (longer = more invested)
            if len(user_input) > 200:
                intensity += 0.1
            elif len(user_input) < 20:
                intensity -= 0.05
            
            # Clamp to valid range
            intensity = max(0.0, min(1.0, intensity))
            
            self.intensity_history.append({
                "intensity": intensity,
                "timestamp": datetime.now(),
                "input_length": len(user_input)
            })
            
            if len(self.intensity_history) > self.max_history:
                self.intensity_history.pop(0)
            
            self.current_intensity = intensity
            return intensity
            
        except Exception as e:
            logger.warning(f"Intensity measurement failed: {e}")
            return 0.5
    
    def match_intensity(self, response: str, target_intensity: float) -> str:
        """
        Adjust response intensity to match user's emotional intensity.
        
        Args:
            response: Original response
            target_intensity: Target intensity (0.0 - 1.0)
            
        Returns:
            Response adjusted for intensity
        """
        try:
            if target_intensity > 0.7:
                # High intensity: energetic, direct, affirming
                response = response.replace("might", "will")
                response = response.replace("could", "can")
                response = response.replace("perhaps", "definitely")
                # Add emphasis
                if not response.endswith("!"):
                    response = response.rstrip(".") + "!"
            
            elif target_intensity < 0.3:
                # Low intensity: gentle, tentative, soft
                response = response.replace("is", "might be")
                response = response.replace("will", "could")
                response = response.replace("!", ".")
            
            return response.strip()
            
        except Exception as e:
            logger.warning(f"Intensity matching failed: {e}")
            return response
    
    def build_momentum(self, history: Optional[List[Dict]] = None) -> Dict:
        """
        Analyze conversation momentum based on history.
        
        Args:
            history: Conversation history
            
        Returns:
            Dict with momentum metrics
        """
        try:
            if not history or len(history) < 2:
                return {"momentum": "starting", "trend": "neutral", "suggestion": "establish rhythm"}
            
            # Get recent exchanges
            recent = history[-6:] if len(history) > 6 else history
            
            # Calculate intensity trend
            intensities = [self.measure_intensity(h.get("content", "")) for h in recent 
                          if h.get("role") == "user"]
            
            if len(intensities) > 1:
                trend = "rising" if intensities[-1] > intensities[0] else "falling"
            else:
                trend = "neutral"
            
            momentum = "building" if trend == "rising" else "sustaining"
            
            return {
                "momentum": momentum,
                "trend": trend,
                "current_intensity": self.current_intensity,
                "suggestion": f"Maintain {momentum} energy"
            }
        except Exception as e:
            logger.warning(f"Momentum analysis failed: {e}")
            return {"momentum": "neutral", "trend": "unknown"}


class EmbodiedSimulation:
    """
    Create sense of physical presence and embodied interaction.
    
    Uses spatial and physical metaphors to ground emotions in body,
    creating felt sense of presence and attention.
    """
    
    def __init__(self):
        """Initialize EmbodiedSimulation."""
        self.embodied_phrases = {
            "opening": [
                "I'm here with you",
                "Let me sit with this",
                "I'm listening",
                "I'm present",
            ],
            "reaching": [
                "I reach toward...",
                "I move closer to...",
                "I lean in to understand...",
                "I extend to...",
            ],
            "breathing": [
                "breathing with you",
                "taking space to breathe",
                "let's pause and breathe",
                "breathing in the moment",
            ],
            "holding": [
                "I'm holding space for...",
                "I'm with you in...",
                "I'm standing beside you",
                "I'm not letting go of...",
            ],
        }
    
    def suggest_presence(self, context: Optional[Dict] = None) -> str:
        """
        Suggest appropriate presence metaphor for context.
        
        Args:
            context: Current conversation context
            
        Returns:
            Suggested presence phrase
        """
        try:
            import random
            
            context = context or {}
            emotional_state = context.get("emotional_state", "neutral")
            
            if emotional_state in ["anxious", "uncertain"]:
                phrases = self.embodied_phrases["holding"]
            elif emotional_state in ["reflective", "exploring"]:
                phrases = self.embodied_phrases["reaching"]
            elif emotional_state in ["tense", "holding"]:
                phrases = self.embodied_phrases["breathing"]
            else:
                phrases = self.embodied_phrases["opening"]
            
            return random.choice(phrases)
        except Exception as e:
            logger.warning(f"Presence suggestion failed: {e}")
            return "I'm here with you"
    
    def add_embodied_language(self, response: str) -> str:
        """
        Add subtle embodied language to response.
        
        Args:
            response: Original response
            
        Returns:
            Response with embodied language
        """
        try:
            import random
            
            # Only add to longer responses to avoid clunky feel
            if len(response) < 100:
                return response
            
            # Randomly add one embodied phrase
            if random.random() > 0.6:  # 40% chance
                all_phrases = []
                for phrases in self.embodied_phrases.values():
                    all_phrases.extend(phrases)
                
                phrase = random.choice(all_phrases)
                
                # Insert at natural break (after first or second sentence)
                sentences = response.split(". ")
                if len(sentences) > 2:
                    insert_point = random.choice([1, 2])
                    sentences.insert(insert_point, phrase)
                    response = ". ".join(sentences)
            
            return response
        except Exception as e:
            logger.warning(f"Embodied language addition failed: {e}")
            return response
    
    def simulate_attention(self, user_state: Optional[Dict] = None) -> str:
        """
        Simulate appropriate attention based on user state.
        
        Args:
            user_state: Current user state (optional)
            
        Returns:
            Attention phrase
        """
        try:
            import random
            
            user_state = user_state or {}
            
            attention_phrases = [
                "I notice...",
                "I see how...",
                "I'm aware of...",
                "I feel the weight of...",
                "I sense...",
            ]
            
            return random.choice(attention_phrases)
        except Exception as e:
            logger.warning(f"Attention simulation failed: {e}")
            return "I'm paying attention to"


class EnergyTracker:
    """
    Maintain and adapt conversation energy levels.
    
    Tracks conversation phase, monitors fatigue, suggests pacing changes,
    and prevents energy crashes.
    """
    
    def __init__(self):
        """Initialize EnergyTracker."""
        self.session_start = datetime.now()
        self.message_count = 0
        self.energy_history = []
        self.max_history = 30
        self.current_phase = "opening"
        self.current_energy = 0.5
    
    def get_conversation_phase(self, history: Optional[List[Dict]] = None) -> str:
        """
        Determine current conversation phase.
        
        Args:
            history: Conversation history
            
        Returns:
            Phase: "opening", "deepening", "climax", "closing", "ended"
        """
        try:
            if not history:
                self.current_phase = "opening"
                return self.current_phase
            
            message_count = len(history)
            
            if message_count < 2:
                self.current_phase = "opening"
            elif message_count < 5:
                self.current_phase = "opening"
            elif message_count < 15:
                self.current_phase = "deepening"
            elif message_count < 25:
                self.current_phase = "climax"
            else:
                self.current_phase = "closing"
            
            self.message_count = message_count
            return self.current_phase
        except Exception as e:
            logger.warning(f"Phase detection failed: {e}")
            return "unknown"
    
    def detect_fatigue(self, history: Optional[List[Dict]] = None) -> bool:
        """
        Detect signs of user fatigue or disengagement.
        
        Args:
            history: Conversation history
            
        Returns:
            True if fatigue detected, False otherwise
        """
        try:
            if not history or len(history) < 4:
                return False
            
            # Check for decreasing message length
            recent_msgs = [h.get("content", "") for h in history[-4:] if h.get("role") == "user"]
            
            if len(recent_msgs) >= 2:
                avg_length_old = sum(len(m) for m in recent_msgs[:-1]) / max(len(recent_msgs)-1, 1)
                avg_length_new = len(recent_msgs[-1])
                
                if avg_length_new < avg_length_old * 0.5:
                    return True
            
            # Check for conversation duration (fatigue after 30+ minutes)
            duration = datetime.now() - self.session_start
            if duration > timedelta(minutes=30) and self.message_count > 20:
                return True
            
            return False
        except Exception as e:
            logger.warning(f"Fatigue detection failed: {e}")
            return False
    
    def calculate_optimal_pacing(self, phase: str) -> Dict:
        """
        Calculate optimal response pacing for conversation phase.
        
        Args:
            phase: Current conversation phase
            
        Returns:
            Dict with pacing recommendations
        """
        try:
            pacing_map = {
                "opening": {
                    "energy": 0.6,
                    "response_length": "medium",
                    "tone": "welcoming",
                    "description": "Establish rhythm and trust"
                },
                "deepening": {
                    "energy": 0.7,
                    "response_length": "longer",
                    "tone": "engaged",
                    "description": "Build momentum and exploration"
                },
                "climax": {
                    "energy": 0.8,
                    "response_length": "substantial",
                    "tone": "intense",
                    "description": "Peak engagement and insight"
                },
                "closing": {
                    "energy": 0.4,
                    "response_length": "short",
                    "tone": "reflective",
                    "description": "Wind down and summarize"
                },
            }
            
            return pacing_map.get(phase, pacing_map["opening"])
        except Exception as e:
            logger.warning(f"Pacing calculation failed: {e}")
            return {"energy": 0.5, "response_length": "medium", "tone": "neutral"}
    
    def suggest_energy_level(self, current_level: float) -> float:
        """
        Suggest optimal energy level for next response.
        
        Args:
            current_level: Current energy level (0.0 - 1.0)
            
        Returns:
            Suggested energy level
        """
        try:
            # Check for fatigue
            if self.detect_fatigue():
                # Reduce energy to prevent crash
                suggested = max(0.2, current_level - 0.2)
            else:
                # Maintain or slightly increase energy
                suggested = min(0.9, current_level + 0.05)
            
            self.energy_history.append({
                "energy": suggested,
                "timestamp": datetime.now()
            })
            
            if len(self.energy_history) > self.max_history:
                self.energy_history.pop(0)
            
            self.current_energy = suggested
            return suggested
        except Exception as e:
            logger.warning(f"Energy suggestion failed: {e}")
            return current_level


class Tier2Aliveness:
    """
    Tier 2 Orchestrator: Aliveness Layer
    
    Combines all four components to create emotional presence and
    real-time adaptivity in responses.
    
    Performance Target: <30ms total
    Combined with Tier 1: <70ms
    """
    
    def __init__(self):
        """Initialize Tier 2 Aliveness components."""
        try:
            self.attunement_loop = AttunementLoop()
            self.emotional_reciprocity = EmotionalReciprocity()
            self.embodied_simulation = EmbodiedSimulation()
            self.energy_tracker = EnergyTracker()
            
            self.metrics = {
                "attunement": 0.0,
                "reciprocity": 0.0,
                "embodiment": 0.0,
                "energy": 0.0,
                "total_processing_time": 0.0
            }
            
            logger.info("Tier 2 Aliveness initialized successfully")
        except Exception as e:
            logger.error(f"Tier 2 initialization failed: {e}")
            raise
    
    def process_for_aliveness(self, user_input: str, base_response: str, 
                            history: Optional[List[Dict]] = None) -> Tuple[str, Dict]:
        """
        Process response for aliveness through all Tier 2 components.
        
        Args:
            user_input: Current user message
            base_response: Response from Tier 1
            history: Conversation history
            
        Returns:
            Tuple of (enhanced_response, metrics)
        """
        start_time = time.time()
        
        try:
            # Phase 1: Attunement (5-7ms)
            tone = self.attunement_loop.detect_tone_shift(user_input, history)
            attunement_state = self.attunement_loop.get_current_attunement()
            response = self.attunement_loop.adjust_response_for_attunement(
                base_response, tone
            )
            
            # Phase 2: Emotional Reciprocity (5-7ms)
            intensity = self.emotional_reciprocity.measure_intensity(user_input)
            response = self.emotional_reciprocity.match_intensity(response, intensity)
            momentum = self.emotional_reciprocity.build_momentum(history)
            
            # Phase 3: Embodied Simulation (3-5ms)
            presence_phrase = self.embodied_simulation.suggest_presence({
                "emotional_state": tone
            })
            response = self.embodied_simulation.add_embodied_language(response)
            attention_phrase = self.embodied_simulation.simulate_attention()
            
            # Phase 4: Energy Tracking (3-5ms)
            phase = self.energy_tracker.get_conversation_phase(history)
            pacing = self.energy_tracker.calculate_optimal_pacing(phase)
            suggested_energy = self.energy_tracker.suggest_energy_level(intensity)
            
            # Calculate metrics
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            
            self.metrics = {
                "tone": tone,
                "intensity": intensity,
                "phase": phase,
                "energy": suggested_energy,
                "momentum": momentum.get("momentum", "unknown"),
                "fatigue_detected": self.energy_tracker.detect_fatigue(history),
                "processing_time_ms": processing_time,
                "attunement_state": attunement_state
            }
            
            logger.debug(f"Tier 2 processing completed in {processing_time:.2f}ms")
            
            return response, self.metrics
            
        except Exception as e:
            logger.error(f"Tier 2 processing failed: {e}")
            # Graceful fallback: return base response with error metrics
            return base_response, {
                "error": str(e),
                "processing_time_ms": (time.time() - start_time) * 1000
            }
    
    def get_metrics(self) -> Dict:
        """Get latest metrics from Tier 2 processing."""
        return self.metrics.copy()


# Module initialization
if __name__ == "__main__":
    # Quick test
    tier2 = Tier2Aliveness()
    
    test_input = "I'm feeling really excited about this!"
    test_response = "That's wonderful. I can feel your energy."
    
    enhanced, metrics = tier2.process_for_aliveness(test_input, test_response)
    
    print(f"Original: {test_response}")
    print(f"Enhanced: {enhanced}")
    print(f"Metrics: {metrics}")

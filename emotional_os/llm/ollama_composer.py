"""
Local LLM Response Composer using Ollama

Generates nuanced emotional responses using a locally-run language model.
100% private - no external API calls. Model stored in ~/.ollama/models/
"""

import json
import os
import sys
import urllib.request
import urllib.error
from typing import Dict, List, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class OllamaComposer:
    """Compose responses using locally-running Ollama model."""

    def __init__(
        self,
        model: str = "mistral",
        ollama_base_url: Optional[str] = None,
        temperature: float = 0.7,
        timeout: int = 30,
        fallback_to_template: bool = True
    ):
        """
        Initialize Ollama composer.

        Args:
            model: Model name (must be installed via `ollama pull <model>`)
            ollama_base_url: URL where Ollama server is running (defaults to env var or localhost)
            temperature: Creativity level (0.0-1.0, higher = more creative)
            timeout: Seconds to wait for response
            fallback_to_template: If Ollama fails, fall back to template responses
        """
        self.model = model
        
        # Use provided URL, environment variable, or default to localhost
        if ollama_base_url is None:
            ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        self.ollama_base_url = ollama_base_url
        self.temperature = temperature
        self.timeout = timeout
        self.fallback_to_template = fallback_to_template
        self.is_available = False

        # Check if Ollama is running
        self._check_availability()

    def _check_availability(self) -> bool:
        """Check if Ollama server is running and model is available."""
        try:
            with urllib.request.urlopen(
                f"{self.ollama_base_url}/api/tags",
                timeout=5
            ) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    models = data.get("models", [])
                    model_names = [m.get("name", "").split(":")[0] for m in models]
                    self.is_available = self.model in model_names
                    if self.is_available:
                        print(f"✓ Ollama available with {self.model} model")
                    else:
                        print(f"✗ Model '{self.model}' not found. Available: {model_names}")
                    return self.is_available
        except urllib.error.URLError:
            print(f"✗ Ollama not running at {self.ollama_base_url}")
            print("  Start with: ollama serve")
        except Exception as e:
            print(f"✗ Error checking Ollama: {e}")

        self.is_available = False
        return False

    def compose_response(
        self,
        user_input: str,
        emotional_signals: Optional[List[Dict]] = None,
        glyph_context: Optional[Dict] = None,
        conversation_history: Optional[List] = None,
        system_prompt: Optional[str] = None,
        response_style: str = "Balanced",
    ) -> str:
        """
        Generate a nuanced emotional response using the local LLM.

        Args:
            user_input: What the user said
            emotional_signals: List of detected emotions [{"signal": "grief", "keyword": "loss"}]
            glyph_context: Glyph that matched (used invisibly for calibration)
            conversation_history: Prior messages for context
            system_prompt: Custom system prompt
            response_style: "Brief", "Balanced", or "Thoughtful"

        Returns:
            Generated response (or fallback if LLM unavailable)
        """
        if not self.is_available:
            return self._fallback_response(user_input, emotional_signals)

        # Build the prompt
        prompt = self._build_prompt(
            user_input=user_input,
            emotional_signals=emotional_signals,
            glyph_context=glyph_context,
            conversation_history=conversation_history,
            system_prompt=system_prompt,
            response_style=response_style,
        )

        # Call Ollama locally
        try:
            payload = json.dumps({
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "top_p": 0.9,
                    "num_predict": 50,  # Reduced to force brevity
                }
            }).encode('utf-8')

            req = urllib.request.Request(
                f"{self.ollama_base_url}/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"}
            )

            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode())
                    generated_text = result.get("response", "").strip()
                    if generated_text:
                        return generated_text

        except urllib.error.URLError as e:
            if "timed out" in str(e):
                print(f"⚠ Ollama timeout (>{self.timeout}s)")
            else:
                print("⚠ Ollama connection lost")
        except Exception as e:
            print(f"⚠ Ollama error: {e}")

        # Fall back to template response
        if self.fallback_to_template:
            return self._fallback_response(user_input, emotional_signals)
        else:
            return "I'm here with you. Let me listen more carefully."

    def _build_prompt(
        self,
        user_input: str,
        emotional_signals: Optional[List[Dict]] = None,
        glyph_context: Optional[Dict] = None,
        conversation_history: Optional[List] = None,
        system_prompt: Optional[str] = None,
        response_style: str = "Balanced",
    ) -> str:
        """Build the prompt for the LLM."""

        if system_prompt is None:
            system_prompt = self._default_system_prompt(response_style)

        # Build context
        context_lines = []

        if emotional_signals:
            emotions = ", ".join([s.get("signal", "unknown") for s in emotional_signals[:3]])
            context_lines.append(f"Emotional landscape: {emotions}")

        if glyph_context:
            glyph_name = glyph_context.get("glyph_name", "")
            if glyph_name:
                context_lines.append(f"Resonates with: {glyph_name}")

        context = "\n".join(context_lines) if context_lines else ""

        # Build the full prompt
        full_prompt = f"""{system_prompt}

{f"Context: {context}" if context else ""}

User: {user_input}

Response:"""

        return full_prompt

    def _default_system_prompt(self, response_style: str = "Balanced") -> str:
        """Default system prompt for emotionally attuned responses."""
        
        if response_style == "Brief":
            return """Keep responses to ONE sentence max. Be direct and warm.
Example: "I'm here." or "Tell me more." or "That matters."
Never add questions at the end. Stop after your first thought."""
        
        elif response_style == "Thoughtful":
            return """Respond in 2-3 sentences. Be warm, specific, and reflective.
Acknowledge what they said, show you understand, maybe ask gently.
Stay genuine and intimate without being presumptuous."""
        
        else:  # Balanced (default)
            return """Respond in 1-2 sentences. Warm and genuine.
Acknowledge them. Be direct but caring. No prescriptions."""

    def _fallback_response(self, user_input: str, emotional_signals: Optional[List[Dict]] = None) -> str:
        """Fallback responses when Ollama is unavailable."""
        # Very brief fallback responses
        brief_responses = [
            "I'm here.",
            "Tell me more.",
            "I'm listening.",
            "That matters.",
            "Go on.",
            "I see.",
        ]
        
        if not emotional_signals:
            import random
            return random.choice(brief_responses)

        signal = emotional_signals[0].get("signal", "unknown").lower()

        responses = {
            "grief": "I'm here with you.",
            "joy": "I can feel that.",
            "anxiety": "That's real.",
            "anger": "I hear you.",
            "love": "That's beautiful.",
            "confusion": "Let's sit with it.",
            "exhaustion": "You're carrying a lot.",
        }

        return responses.get(signal, "I'm here.")


# Singleton instance
_ollama_composer = None


def get_ollama_composer(
    model: str = "mistral",
    fallback_to_template: bool = True,
) -> OllamaComposer:
    """Get or create the Ollama composer singleton."""
    global _ollama_composer
    if _ollama_composer is None:
        _ollama_composer = OllamaComposer(
            model=model,
            fallback_to_template=fallback_to_template
        )
    return _ollama_composer

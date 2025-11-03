"""
Local LLM Response Composer using Ollama

Generates nuanced emotional responses using a locally-run language model.
100% private - no external API calls. Model stored in ~/.ollama/models/
"""

import json
import os
import requests
import sys
from typing import Dict, List, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class OllamaComposer:
    """Compose responses using locally-running Ollama model."""

    def __init__(
        self,
        model: str = "mistral",
        ollama_base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        timeout: int = 30,
        fallback_to_template: bool = True
    ):
        """
        Initialize Ollama composer.

        Args:
            model: Model name (must be installed via `ollama pull <model>`)
            ollama_base_url: URL where Ollama server is running
            temperature: Creativity level (0.0-1.0, higher = more creative)
            timeout: Seconds to wait for response
            fallback_to_template: If Ollama fails, fall back to template responses
        """
        self.model = model
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
            response = requests.get(
                f"{self.ollama_base_url}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "").split(":")[0] for m in models]
                self.is_available = self.model in model_names
                if self.is_available:
                    print(f"✓ Ollama available with {self.model} model")
                else:
                    print(f"✗ Model '{self.model}' not found. Available: {model_names}")
                return self.is_available
        except requests.exceptions.ConnectionError:
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
    ) -> str:
        """
        Generate a nuanced emotional response using the local LLM.

        Args:
            user_input: What the user said
            emotional_signals: List of detected emotions [{"signal": "grief", "keyword": "loss"}]
            glyph_context: Glyph that matched (used invisibly for calibration)
            conversation_history: Prior messages for context
            system_prompt: Custom system prompt

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
        )

        # Call Ollama locally
        try:
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "top_p": 0.9,
                        "num_predict": 200,  # Max tokens
                    }
                },
                timeout=self.timeout,
            )

            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "").strip()
                if generated_text:
                    return generated_text

        except requests.exceptions.Timeout:
            print(f"⚠ Ollama timeout (>{self.timeout}s)")
        except requests.exceptions.ConnectionError:
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
    ) -> str:
        """Build the prompt for the LLM."""

        if system_prompt is None:
            system_prompt = self._default_system_prompt()

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

    def _default_system_prompt(self) -> str:
        """Default system prompt for emotionally attuned responses."""
        return """You are a deeply empathetic presence. Your responses are:
- Concise (2-3 sentences max)
- Specific to what the person actually said
- Warm but authentic, never generic
- Focused on witnessing and understanding
- Never prescriptive or dismissive
- Personal and intimate without being presumptuous

Respond naturally, like a trusted friend who truly listens."""

    def _fallback_response(self, user_input: str, emotional_signals: Optional[List[Dict]] = None) -> str:
        """Fallback responses when Ollama is unavailable."""
        if not emotional_signals:
            return "I'm here. Tell me what's on your mind."

        signal = emotional_signals[0].get("signal", "unknown").lower()

        responses = {
            "grief": "What you're carrying matters. I'm here to witness it.",
            "joy": "I can feel the light in what you're saying. Tell me more.",
            "anxiety": "That uncertainty is real. You don't have to hold it alone.",
            "anger": "That fire in you—it's pointing to something true. What is it?",
            "love": "That care you have—it's profound. How does it feel?",
            "confusion": "The not-knowing is real. Let's sit with it together.",
            "exhaustion": "You're carrying something heavy. What would help right now?",
        }

        return responses.get(signal, "I'm here. What do you need to express?")


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

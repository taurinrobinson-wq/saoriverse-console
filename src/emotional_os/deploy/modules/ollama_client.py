"""
Ollama LLM Client Integration.

Provides HTTP interface to local Ollama LLM service for FirstPerson Streamlit app.
Handles model selection, response streaming, error recovery, and fallback modes.
"""

import os
import requests
import logging
import json
from typing import Optional, Dict, Any, Iterator
import time

logger = logging.getLogger(__name__)


class OllamaClient:
    """HTTP client for Ollama local LLM service."""

    def __init__(self, base_url: Optional[str] = None):
        """Initialize Ollama client.

        Args:
            base_url: Ollama API endpoint (default: http://ollama:11434 for Docker,
                     http://localhost:11434 for local)
        """
        self.base_url = base_url or os.getenv(
            "OLLAMA_BASE_URL", "http://localhost:11434"
        ).rstrip("/")
        self.api_endpoint = f"{self.base_url}/api"
        self.timeout = 30  # seconds for connection
        self.read_timeout = 300  # seconds for full response
        self.available_models = None
        self.last_check_time = 0
        self.model_cache_ttl = 60  # refresh model list every 60 seconds

    def is_available(self) -> bool:
        """Check if Ollama service is running and responding.

        Returns:
            True if Ollama is accessible, False otherwise
        """
        try:
            response = requests.get(
                f"{self.api_endpoint}/tags",
                timeout=self.timeout,
            )
            return response.status_code == 200
        except (requests.ConnectionError, requests.Timeout, Exception) as e:
            logger.debug(f"Ollama not available: {e}")
            return False

    def get_available_models(self, force_refresh: bool = False) -> list:
        """Get list of available models on Ollama server.

        Args:
            force_refresh: Bypass cache and fetch fresh list

        Returns:
            List of model names (e.g., ['llama3', 'mistral', 'neural-chat'])
        """
        # Use cache if available and not expired
        now = time.time()
        if (
            self.available_models is not None
            and not force_refresh
            and (now - self.last_check_time) < self.model_cache_ttl
        ):
            return self.available_models

        try:
            response = requests.get(
                f"{self.api_endpoint}/tags",
                timeout=self.timeout,
            )
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                model_names = [m.get("name", m) for m in models]
                self.available_models = model_names
                self.last_check_time = now
                logger.info(f"Found {len(model_names)} Ollama models: {model_names}")
                return model_names
            else:
                logger.warning(
                    f"Failed to fetch models: HTTP {response.status_code}"
                )
                return []
        except Exception as e:
            logger.error(f"Error fetching available models: {e}")
            return []

    def generate(
        self,
        prompt: str,
        model: str = "llama3",
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 40,
        num_predict: int = 512,
        stream: bool = False,
        system: Optional[str] = None,
    ) -> str:
        """Generate response from Ollama model.

        Args:
            prompt: Input text for model
            model: Model name (e.g., 'llama3', 'mistral', 'neural-chat')
            temperature: Creativity/randomness (0-1, default 0.7)
            top_p: Nucleus sampling parameter (0-1, default 0.9)
            top_k: Top-K sampling parameter (default 40)
            num_predict: Max tokens to generate (default 512)
            stream: Whether to stream response tokens
            system: Optional system prompt to set context/personality

        Returns:
            Generated text response
        """
        if not self.is_available():
            raise ConnectionError(
                f"Ollama service not available at {self.base_url}. "
                "Make sure Ollama is running (docker-compose up)"
            )

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "num_predict": num_predict,
        }

        if system:
            payload["system"] = system

        try:
            if stream:
                return self._generate_streaming(payload)
            else:
                return self._generate_blocking(payload)
        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise

    def _generate_blocking(self, payload: Dict[str, Any]) -> str:
        """Blocking (non-streaming) generation.

        Args:
            payload: Request payload for Ollama API

        Returns:
            Full generated response text
        """
        response = requests.post(
            f"{self.api_endpoint}/generate",
            json=payload,
            timeout=self.read_timeout,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Ollama generation failed: HTTP {response.status_code}. "
                f"Response: {response.text[:200]}"
            )

        data = response.json()
        return data.get("response", "").strip()

    def _generate_streaming(self, payload: Dict[str, Any]) -> str:
        """Streaming generation - collect tokens as they arrive.

        Args:
            payload: Request payload for Ollama API

        Returns:
            Full generated response text (collected from stream)
        """
        response_text = ""
        try:
            response = requests.post(
                f"{self.api_endpoint}/generate",
                json=payload,
                stream=True,
                timeout=self.read_timeout,
            )

            if response.status_code != 200:
                raise RuntimeError(
                    f"Ollama streaming failed: HTTP {response.status_code}"
                )

            # Collect tokens from stream
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("response", "")
                        response_text += token
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse streaming chunk: {line}")
                        continue

            return response_text.strip()

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            raise

    def generate_with_context(
        self,
        user_input: str,
        conversation_history: list,
        model: str = "llama3",
        system_prompt: Optional[str] = None,
        max_history: int = 10,
    ) -> str:
        """Generate response with conversation context.

        Formats conversation history into context for better coherence.

        Args:
            user_input: Current user message
            conversation_history: List of previous exchanges (dicts with 'role' and 'content')
            model: Model name
            system_prompt: Optional system prompt for personality
            max_history: Max previous exchanges to include

        Returns:
            Generated response
        """
        # Build context from conversation history
        context = self._build_context_from_history(
            conversation_history[-max_history:], system_prompt
        )

        # Append current user input
        prompt = f"{context}\nUser: {user_input}\nAssistant:"

        return self.generate(
            prompt=prompt,
            model=model,
            system=system_prompt,
            temperature=0.7,
            num_predict=512,
        )

    def _build_context_from_history(
        self, history: list, system_prompt: Optional[str] = None
    ) -> str:
        """Build context string from conversation history.

        Args:
            history: List of exchanges
            system_prompt: Optional system context

        Returns:
            Formatted context string
        """
        context = ""

        if system_prompt:
            context += f"System: {system_prompt}\n\n"

        for exchange in history:
            role = exchange.get("role", "Unknown")
            content = exchange.get("content", "")
            if role.lower() == "user":
                context += f"User: {content}\n"
            elif role.lower() in ["assistant", "ai", "response"]:
                context += f"Assistant: {content}\n"

        return context.strip()

    def pull_model(self, model: str) -> bool:
        """Pull/download a model from Ollama registry.

        Args:
            model: Model name (e.g., 'llama3', 'mistral')

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Pulling model: {model}...")
            response = requests.post(
                f"{self.api_endpoint}/pull",
                json={"name": model},
                timeout=600,  # Long timeout for large downloads
            )

            if response.status_code == 200:
                logger.info(f"Successfully pulled model: {model}")
                return True
            else:
                logger.error(f"Failed to pull model: HTTP {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """Get health status of Ollama service.

        Returns:
            Dict with service status, available models, and diagnostics
        """
        return {
            "available": self.is_available(),
            "base_url": self.base_url,
            "models": self.get_available_models(),
            "timestamp": time.time(),
        }


def get_ollama_client(base_url: Optional[str] = None) -> OllamaClient:
    """Factory function to get Ollama client instance.

    Args:
        base_url: Optional override for Ollama endpoint

    Returns:
        OllamaClient instance
    """
    return OllamaClient(base_url=base_url)


# Singleton for convenience in Streamlit apps
_client_instance = None


def get_ollama_client_singleton(base_url: Optional[str] = None) -> OllamaClient:
    """Get or create singleton Ollama client for Streamlit caching.

    Args:
        base_url: Optional override for Ollama endpoint

    Returns:
        Cached OllamaClient instance
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = OllamaClient(base_url=base_url)
    return _client_instance

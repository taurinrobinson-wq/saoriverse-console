"""
LLM Transformer Module for DraftShift - Phase 1.1

Integrates GPT4All (Mistral 7B) for generating civility-enhanced rewrites.
Provides async/threaded transformation of sentences with tone adjustment.

Features:
- Local LLM inference (no API calls, full privacy)
- GPT4All Mistral 7B quantized model
- Sentence-level transformation
- Configurable tone guidance
- Fallback to rule-based transformation if LLM unavailable
"""

import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
import os

logger = logging.getLogger(__name__)

# Try to import GPT4All - graceful fallback if not available
try:
    from gpt4all import GPT4All
    HAS_GPT4ALL = True
    GPT4ALL_AVAILABLE = True
except ImportError:
    HAS_GPT4ALL = False
    GPT4ALL_AVAILABLE = False
    logger.warning("GPT4All not installed. Install with: pip install gpt4all")


class LLMTransformer:
    """
    Manages GPT4All model loading and inference for civility transformation.
    
    Attributes:
        model (GPT4All): The loaded GPT4All model instance
        model_name (str): Name of the model (default: "Mistral7B")
        model_loaded (bool): Whether model loaded successfully
        fallback_mode (bool): Whether using fallback rule-based transformation
    """
    
    def __init__(
        self, 
        model_name: str = "mistral-7b-instruct-v0.1.Q4_0.gguf",
        model_path: Optional[str] = None,
        auto_load: bool = True
    ):
        """
        Initialize LLM Transformer.
        
        Args:
            model_name: GPT4All model filename or ID
            model_path: Optional custom path to model directory
            auto_load: Whether to load model immediately
        """
        self.model_name = model_name
        self.model_path = model_path
        self.model = None
        self.model_loaded = False
        self.fallback_mode = False
        
        if auto_load and HAS_GPT4ALL:
            self.load_model()
        elif not HAS_GPT4ALL:
            logger.warning("GPT4All not available - running in fallback mode")
            self.fallback_mode = True
    
    def load_model(self) -> bool:
        """
        Load GPT4All model into memory.
        
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        if not HAS_GPT4ALL:
            logger.warning("GPT4All not installed. Install with: pip install gpt4all")
            self.fallback_mode = True
            return False
        
        try:
            logger.info(f"Loading GPT4All model: {self.model_name}")
            
            # Create GPT4All instance with model path if provided
            if self.model_path:
                self.model = GPT4All(
                    self.model_name,
                    model_path=self.model_path,
                    allow_download=False  # Prevent automatic downloads in production
                )
            else:
                self.model = GPT4All(
                    self.model_name,
                    allow_download=True  # Allow download for first-time setup
                )
            
            self.model_loaded = True
            logger.info(f"✅ Model loaded successfully: {self.model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load GPT4All model: {e}")
            logger.warning("Falling back to rule-based transformation")
            self.fallback_mode = True
            self.model_loaded = False
            return False
    
    def unload_model(self):
        """Unload model from memory to free resources."""
        if self.model:
            try:
                # GPT4All doesn't have explicit unload, but we can release reference
                self.model = None
                self.model_loaded = False
                logger.info("Model unloaded from memory")
            except Exception as e:
                logger.error(f"Error unloading model: {e}")
    
    def transform_sentence(
        self, 
        sentence: str, 
        target_tone: str,
        include_original: bool = True
    ) -> Dict[str, Any]:
        """
        Transform a single sentence using LLM or fallback rules.
        
        Args:
            sentence: Original sentence to transform
            target_tone: Target tone (e.g., "formal", "neutral", "friendly")
            include_original: Whether to include original in response
        
        Returns:
            Dictionary with:
                - 'original': Original sentence
                - 'transformed': Transformed sentence
                - 'method': 'llm' or 'fallback'
                - 'tone': Target tone used
                - 'confidence': Confidence score (0-1)
        """
        if not sentence or not sentence.strip():
            return {
                'original': sentence,
                'transformed': sentence,
                'method': 'skip',
                'tone': target_tone,
                'confidence': 1.0
            }
        
        if self.fallback_mode or not self.model_loaded:
            return self._fallback_transform(sentence, target_tone)
        
        try:
            return self._llm_transform(sentence, target_tone)
        except Exception as e:
            logger.warning(f"LLM transform failed, using fallback: {e}")
            return self._fallback_transform(sentence, target_tone)
    
    def _llm_transform(
        self, 
        sentence: str, 
        target_tone: str
    ) -> Dict[str, Any]:
        """
        Transform using GPT4All LLM.
        
        Args:
            sentence: Sentence to transform
            target_tone: Target tone
        
        Returns:
            Transformation result dictionary
        """
        if not self.model:
            return self._fallback_transform(sentence, target_tone)
        
        # Craft prompt for LLM
        tone_description = {
            "very_formal": "extremely formal, professional, and serious",
            "formal": "formal and professional",
            "neutral": "neutral and objective",
            "friendly": "friendly and approachable",
            "empathetic": "empathetic and understanding",
        }.get(target_tone.lower(), "neutral")
        
        prompt = f"""Transform this sentence to be more {tone_description} while preserving the core meaning. Respond with ONLY the transformed sentence, no explanation.

Original: {sentence}
Transformed:"""
        
        try:
            # Generate transformation
            response = self.model.generate(
                prompt,
                max_tokens=150,
                temp=0.7,
                top_p=0.9,
            )
            
            # Clean up response
            transformed = response.strip()
            
            # Remove common artifacts
            if transformed.startswith("Transformed:"):
                transformed = transformed[len("Transformed:"):].strip()
            
            # Ensure we have a result
            if not transformed or transformed == sentence:
                return self._fallback_transform(sentence, target_tone)
            
            return {
                'original': sentence,
                'transformed': transformed,
                'method': 'llm',
                'tone': target_tone,
                'confidence': 0.85  # LLM-generated, good confidence
            }
            
        except Exception as e:
            logger.warning(f"LLM generation failed: {e}")
            return self._fallback_transform(sentence, target_tone)
    
    def _fallback_transform(
        self, 
        sentence: str, 
        target_tone: str
    ) -> Dict[str, Any]:
        """
        Fallback rule-based transformation.
        Uses heuristics and existing draftshift tone_signal_parser.
        
        Args:
            sentence: Sentence to transform
            target_tone: Target tone
        
        Returns:
            Transformation result dictionary
        """
        # Simple heuristic transformations
        transformed = sentence
        confidence = 0.6  # Lower confidence for rule-based
        
        tone_lower = target_tone.lower()
        
        # Apply tone-specific transformations
        if tone_lower in ["very_formal", "formal"]:
            # Add formality markers
            if "hey" in transformed.lower():
                transformed = transformed.replace("hey", "greetings")
            if "thanks" in transformed.lower():
                transformed = transformed.replace("thanks", "thank you")
            if "gonna" in transformed.lower():
                transformed = transformed.replace("gonna", "will")
            if "wanna" in transformed.lower():
                transformed = transformed.replace("wanna", "wish to")
            if "can't" in transformed.lower():
                transformed = transformed.replace("can't", "cannot")
            if "don't" in transformed.lower():
                transformed = transformed.replace("don't", "do not")
            confidence = 0.65
        
        elif tone_lower == "friendly":
            # Add warm language
            if not any(word in transformed.lower() for word in ["please", "thank you", "appreciate"]):
                # Could add friendly markers (simplified here)
                pass
            confidence = 0.60
        
        elif tone_lower == "empathetic":
            # Add understanding language
            if not any(word in transformed.lower() for word in ["understand", "appreciate", "recognize"]):
                # Could add empathy markers (simplified here)
                pass
            confidence = 0.60
        
        return {
            'original': sentence,
            'transformed': transformed,
            'method': 'fallback',
            'tone': target_tone,
            'confidence': confidence
        }
    
    def transform_batch(
        self, 
        sentences: List[str], 
        target_tone: str
    ) -> List[Dict[str, Any]]:
        """
        Transform multiple sentences.
        
        Args:
            sentences: List of sentences to transform
            target_tone: Target tone for all sentences
        
        Returns:
            List of transformation results
        """
        results = []
        for sentence in sentences:
            result = self.transform_sentence(sentence, target_tone)
            results.append(result)
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current transformer status.
        
        Returns:
            Status dictionary with loaded/fallback info
        """
        return {
            'llm_available': HAS_GPT4ALL,
            'model_loaded': self.model_loaded,
            'fallback_mode': self.fallback_mode,
            'model_name': self.model_name,
            'method': 'llm' if self.model_loaded else 'fallback'
        }


# Module-level singleton for ease of use
_transformer_instance: Optional[LLMTransformer] = None


def get_transformer(
    model_name: str = "mistral-7b-instruct-v0.1.Q4_0.gguf",
    force_reload: bool = False
) -> LLMTransformer:
    """
    Get or create LLM transformer singleton.
    
    Args:
        model_name: GPT4All model name
        force_reload: Force reload even if already loaded
    
    Returns:
        LLMTransformer instance
    """
    global _transformer_instance
    
    if force_reload:
        if _transformer_instance:
            _transformer_instance.unload_model()
        _transformer_instance = None
    
    if _transformer_instance is None:
        _transformer_instance = LLMTransformer(model_name=model_name)
    
    return _transformer_instance


def transform_text(
    text: str,
    target_tone: str,
    model_name: str = "mistral-7b-instruct-v0.1.Q4_0.gguf"
) -> Dict[str, Any]:
    """
    Convenience function to transform text without managing transformer instance.
    
    Args:
        text: Text to transform
        target_tone: Target tone
        model_name: GPT4All model name
    
    Returns:
        Transformation result with sentences list
    """
    from DraftShift.core import split_sentences
    
    transformer = get_transformer(model_name)
    sentences = split_sentences(text)
    results = transformer.transform_batch(sentences, target_tone)
    
    return {
        'sentences': results,
        'original_text': text,
        'transformed_text': ' '.join([r['transformed'] for r in results]),
        'status': transformer.get_status()
    }

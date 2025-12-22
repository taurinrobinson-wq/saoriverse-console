from typing import Optional, Dict, Any
import os
import traceback


class EngineAdapter:
    """Adapter between the API and the local Emotional OS engines.

    Provides `process(text, user_id, signals)` which returns a structured dict
    with keys `response`, `state`, and `meta`. Falls back safely on exceptions.
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or os.environ.get("EMOTIONAL_OS_STORAGE_PATH")

    def _normalize_signals(self, overrides: Optional[Dict[str, float]]) -> Dict[str, float]:
        defaults = {
            "positive": 0.0,
            "negative": 0.0,
            "trust": 0.0,
            "intimacy": 0.0,
            "connection": 0.0,
            "emotional_intensity": 0.5,
            "context_familiarity": 0.5,
        }

        if not overrides:
            return defaults

        mapping = {
            "warmth": "positive",
            "assertiveness": "pride",
            "playfulness": "playfulness",
            "formality": "formality",
        }

        for k, v in (overrides or {}).items():
            try:
                val = float(v)
            except Exception:
                continue
            if k in mapping:
                defaults[mapping[k]] = max(0.0, min(1.0, val))
            else:
                defaults[k] = max(0.0, min(1.0, val))

        return defaults

    def process(self, text: str, user_id: str, signals: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        try:
            from src.emotional_os.core.feeling_system import get_feeling_system
            from src.emotional_os.core.poetic_engine import get_poetic_engine

            fs = get_feeling_system(storage_path=self.storage_path)
            poetic = get_poetic_engine(storage_path=self.storage_path)

            emotional_signals = self._normalize_signals(signals)

            result = fs.process_interaction(
                user_id=user_id,
                interaction_text=text,
                emotional_signals=emotional_signals,
                context={},
            )

            detected = result.get("synthesized_state") if isinstance(result, dict) else {}
            poetic_out = poetic.update_from_interaction(
                user_input=text,
                detected_emotions=detected or {},
                user_id=user_id,
            )

            emotional_resp = result.get("emotional_response", {}) if isinstance(result, dict) else {}
            dominant = emotional_resp.get("dominant_emotion", "neutral")
            intensity = emotional_resp.get("intensity", 0.3)

            response_text = poetic_out.get("poem_rendered") or poetic_out.get("poem_state", "")
            style = "poetic"
            modulation = {"temperature": 0.5, "imagery": 0.5, "cadence": 0.5}

            state_traits = {
                "warmth": float(emotional_signals.get("positive", 0.0)),
                "assertiveness": float(emotional_signals.get("pride", 0.0)) if isinstance(emotional_signals.get("pride", 0.0), (int, float)) else 0.0,
                "playfulness": float(emotional_signals.get("playfulness", 0.0)) if isinstance(emotional_signals.get("playfulness", 0.0), (int, float)) else 0.0,
                "formality": float(emotional_signals.get("formality", 0.0)) if isinstance(emotional_signals.get("formality", 0.0), (int, float)) else 0.0,
            }

            memory_block = {
                "recent_inputs": [result.get("interaction_summary", text)][:10],
                "recent_outputs": [response_text][:10],
            }

            return {
                "response": {"text": response_text, "style": style, "poetic_modulation": modulation},
                "state": {"mood": dominant, "intensity": float(intensity), "traits": state_traits, "memory": memory_block},
                "meta": {"user_id": user_id, "timestamp": result.get("timestamp") if isinstance(result, dict) else None, "engine_version": "0.1.0"},
            }
        except Exception:
            traceback.print_exc()
            return {
                "response": {"text": "The emotional engine encountered an issue, but I'm still here.", "style": "fallback", "poetic_modulation": {"temperature": 0.3, "imagery": 0.1, "cadence": 0.2}},
                "state": {"mood": "uncertain", "intensity": 0.1, "traits": {}, "memory": {}},
                "meta": {"user_id": user_id, "timestamp": None, "engine_version": "0.1.0"},
            }

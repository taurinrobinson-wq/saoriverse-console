"""Remote parser client for ML engine.

Attempts to call the ML API to perform Emotional OS parsing/glyph selection.
Uses env `EMOTIONAL_OS_ML_URL` (e.g. http://ml:8000) and optional `EMOTIONAL_OS_API_KEY`.
"""
import os
import requests
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


def remote_parse_input(text: str, conversation_context: Optional[Dict] = None, timeout: float = 5.0) -> Optional[Dict]:
    """Call ML API to get parsing/response info.

    Tries `/v1/demo` if API key present (returns structured response), otherwise tries `/infer`.
    Returns dict similar to local `parse_input` when possible, or None on failure.
    """
    base = os.getenv("EMOTIONAL_OS_ML_URL") or os.getenv("EMOTIONAL_OS_API_URL")
    if not base:
        logger.debug("remote_parse_input: no EMOTIONAL_OS_ML_URL configured")
        return None

    api_key = os.getenv("EMOTIONAL_OS_API_KEY")
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key

    # Attempt parse endpoint first (returns full parse_input structure)
    try:
        parse_url = base.rstrip("/") + "/v1/parse"
        payload = {"text": text, "user_id": (conversation_context or {}).get("user_id", "ui-anon")}
        r = requests.post(parse_url, json=payload, headers=headers, timeout=timeout)
        if r.status_code == 200:
            data = r.json()
            # If the parse endpoint returned an error wrapper, treat as failure
            if isinstance(data, dict) and data.get("error"):
                logger.debug("remote_parse_input /v1/parse returned error: %s", data.get("error"))
            else:
                # Expect the full parse_output dict (voltage_response, best_glyph, glyphs, etc.)
                return data
    except Exception as e:
        logger.debug(f"remote_parse_input /v1/parse failed: {e}")

    # Fallback: try /infer
    try:
        infer_url = base.rstrip("/") + "/infer"
        r = requests.post(infer_url, json={"text": text, "user_id": (conversation_context or {}).get("user_id", "ui-anon")}, headers=headers, timeout=timeout)
        if r.status_code == 200:
            data = r.json()
            # /infer returns {"response": "..."}
            resp_text = data.get("response") if isinstance(data.get("response"), str) else ""
            return {
                "input": text,
                "voltage_response": resp_text,
                "response_source": "remote_infer",
                "best_glyph": None,
                "glyphs": [],
            }
    except Exception as e:
        logger.debug(f"remote_parse_input /infer failed: {e}")

    return None

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json
import os
from typing import Optional, Dict, List
import logging

from velinor.config import get_cipher_key
from emotional_os.core.signal_parser import (
    load_signal_map,
    parse_signals,
    convert_signal_names_to_codes,
    evaluate_gates,
)
from emotional_os.core import constants as e_constants

logger = logging.getLogger(__name__)

app = FastAPI(title="Velinor Cipher API")

SEEDS_PATH = Path("velinor/cipher_seeds.json")

# Cache seeds in memory for fast lookup
_seeds_cache: Optional[Dict] = None


def load_seeds() -> Dict:
    """Load seeds from JSON, with in-memory caching."""
    global _seeds_cache
    if _seeds_cache is not None:
        return _seeds_cache

    path = Path(SEEDS_PATH) if not isinstance(SEEDS_PATH, Path) else SEEDS_PATH
    if not path.exists():
        _seeds_cache = {}
        return _seeds_cache

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Index seeds by id for O(1) lookup
    _seeds_cache = {seed["id"]: seed for seed in data.get("seeds", [])}
    logger.info(f"Loaded {len(_seeds_cache)} seeds from {path}")
    return _seeds_cache


def query_gate(seed_id: str, player_state: Optional[str] = None) -> Dict:
    """Query gate status for a seed given player state (micro-loop interface).

    This is the high-level interface used by the micro-loop prototype.
    It looks up the seed, evaluates gates, and returns a response dict.

    Args:
        seed_id: the seed ID (e.g., "velinor-0-001")
        player_state: the player's message text

    Returns:
        dict with layer, allowed, text keys
    """
    seeds = load_seeds()
    if seed_id not in seeds:
        return {"layer": 0, "allowed": False, "text": "[Seed not found]"}

    seed = seeds[seed_id]
    layer = seed.get("layer", 0)
    phrase_text = seed.get("phrase", "")
    required_gates = seed.get("required_gates", [])

    # Convert string player_state to dict format expected by check_gate
    player_state_dict = {"message": player_state} if isinstance(player_state, str) else (player_state or {})

    # Evaluate gate
    gates_ok = check_gate(
        player_state=player_state_dict,
        required_gates=required_gates,
        layer=layer,
    )

    return {
        "layer": layer,
        "allowed": gates_ok,
        "text": phrase_text if gates_ok else None,
    }


def check_gate(
    player_state: Optional[Dict] = None,
    required_gates: Optional[List[str]] = None,
    layer: int = 0,
) -> bool:
    """Evaluate if player has the emotional gates required to see this phrase.

    Args:
        player_state: dict with 'message' or 'pipeline_metadata.gates'
        required_gates: list of gate names from the seed
        layer: 0=fragment, 1=fragment, 2=plaintext

    Returns:
        True if allowed, False if locked
    """
    if not required_gates or len(required_gates) == 0:
        # No gates required -> fragment is always allowed
        return True

    # Layers 0-1 (fragments) are always allowed
    if layer in (0, 1):
        return True

    # Layer 2 (plaintext) requires gate match
    try:
        signal_map = load_signal_map(e_constants.DEFAULT_LEXICON_BASE)
    except Exception:
        signal_map = {}

    # Derive activated gates from player text
    activated_gates = []
    try:
        player_state = player_state or {}
        text = player_state.get("last_message") or player_state.get("message") or ""
        if text:
            signals = parse_signals(text, signal_map)
            signals = convert_signal_names_to_codes(signals)
            activated_gates = evaluate_gates(signals)
    except Exception as e:
        logger.debug(f"Could not derive gates from player state: {e}")

    # If any required gate is in activated gates -> allow
    if any(g in activated_gates for g in required_gates):
        return True

    return False


class ConsentModel(BaseModel):
    """Consent override for plaintext access."""
    allow_plaintext: bool = False


class DecodeRequest(BaseModel):
    """Request to decode a cipher seed."""
    seed_id: str
    player_state: Optional[Dict] = None
    consent: Optional[ConsentModel] = None


class DecodeResponse(BaseModel):
    """Response with decoded seed."""
    status: str  # "ok" or "denied"
    layer: int
    allowed: bool
    text: Optional[str] = None


@app.post("/decode-seed", response_model=DecodeResponse)
def decode_seed(req: DecodeRequest):
    """Decode a cipher seed with emotional gate checking.

    Query the player's emotional state (via their last message),
    check if they have the gates required for this phrase,
    and return the decoded text if allowed.

    Args:
        seed_id: unique ID for the seed (e.g., "velinor-0-001")
        player_state: optional dict with player message or pipeline metadata
        consent: optional consent override

    Returns:
        DecodeResponse with layer, allowed status, and text (if allowed)
    """
    seeds = load_seeds()

    if req.seed_id not in seeds:
        raise HTTPException(status_code=404, detail=f"Seed '{req.seed_id}' not found")

    seed = seeds[req.seed_id]
    layer = seed.get("layer", 0)
    phrase_text = seed.get("phrase", "")
    required_gates = seed.get("required_gates", [])

    # Check consent override
    consent_flag = req.consent and req.consent.allow_plaintext
    if consent_flag:
        # Consent grants immediate access to plaintext
        return DecodeResponse(
            status="ok",
            layer=layer,
            allowed=True,
            text=phrase_text,
        )

    # Check emotional gates
    gates_ok = check_gate(
        player_state=req.player_state,
        required_gates=required_gates,
        layer=layer,
    )

    if gates_ok:
        return DecodeResponse(
            status="ok",
            layer=layer,
            allowed=True,
            text=phrase_text,
        )

    # Not allowed -> return locked response
    return DecodeResponse(
        status="denied",
        layer=layer,
        allowed=False,
        text=None,
    )

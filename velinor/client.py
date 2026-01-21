"""Client helper for requesting plaintext from Velinor cipher API."""
from typing import Optional, Dict, Any
import requests


class VelinorClient:
    """Client for the Velinor cipher API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize client pointing to Velinor API.

        Args:
            base_url: base URL of the API (default: localhost:8000)
        """
        self.base_url = base_url.rstrip("/")

    def request_plaintext(
        self,
        seed_id: str,
        player_state: Optional[Dict[str, Any]] = None,
        allow_plaintext: bool = False,
    ) -> Dict[str, Any]:
        """Request plaintext from a cipher seed.

        Args:
            seed_id: unique ID for the seed (e.g., "velinor-0-001")
            player_state: optional dict with player's last message or metadata
            allow_plaintext: if True, override gates with consent

        Returns:
            dict with keys:
                - status: "ok" or "denied"
                - layer: 0, 1, or 2
                - allowed: bool
                - text: str or None
        """
        payload = {
            "seed_id": seed_id,
            "player_state": player_state or {},
            "consent": {"allow_plaintext": allow_plaintext},
        }

        try:
            resp = requests.post(f"{self.base_url}/decode-seed", json=payload)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"status": "error", "error": str(e), "allowed": False}

    def handle_response(self, resp: Dict[str, Any]) -> str:
        """Format API response for UI display.

        Args:
            resp: response from request_plaintext()

        Returns:
            formatted string for UI
        """
        status = resp.get("status", "error")

        if status == "error":
            return f"❌ Error: {resp.get('error', 'Unknown error')}"

        if not resp.get("allowed"):
            layer = resp.get("layer", "?")
            return f"🔐 Locked (Layer {layer} — requires emotional alignment)"

        text = resp.get("text", "[empty]")
        layer = resp.get("layer", "?")
        layer_names = {0: "Fragment", 1: "Deep Fragment", 2: "Plaintext"}
        layer_name = layer_names.get(layer, "Unknown")

        return f"✨ {layer_name}:\n{text}"


# Singleton client instance
_client: Optional[VelinorClient] = None


def get_client(base_url: str = "http://localhost:8000") -> VelinorClient:
    """Get or create the global Velinor client.

    Args:
        base_url: base URL for the API

    Returns:
        VelinorClient instance
    """
    global _client
    if _client is None:
        _client = VelinorClient(base_url)
    return _client


def request_plaintext(
    seed_id: str,
    player_state: Optional[Dict[str, Any]] = None,
    allow_plaintext: bool = False,
) -> Dict[str, Any]:
    """Request plaintext from a cipher seed (raw response).

    Args:
        seed_id: unique ID for the seed
        player_state: optional player state dict
        allow_plaintext: consent override flag

    Returns:
        raw API response dict
    """
    client = get_client()
    return client.request_plaintext(seed_id, player_state, allow_plaintext)


def request_plaintext_formatted(
    seed_id: str,
    player_state: Optional[Dict[str, Any]] = None,
    allow_plaintext: bool = False,
) -> str:
    """Request plaintext and get formatted response string.

    Args:
        seed_id: unique ID for the seed
        player_state: optional player state dict
        allow_plaintext: consent override flag

    Returns:
        formatted string for UI display
    """
    resp = request_plaintext(seed_id, player_state, allow_plaintext)
    client = get_client()
    return client.handle_response(resp)

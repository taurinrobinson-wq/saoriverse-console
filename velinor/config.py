import os
import hmac
import hashlib
from typing import Optional


def get_cipher_key() -> bytes:
    key = os.environ.get("CIPHER_KEY")
    if not key:
        raise EnvironmentError("CIPHER_KEY not set in environment")
    # Accept hex first
    try:
        return bytes.fromhex(key)
    except Exception:
        return key.encode("utf-8")


def hmac_sha256(key: bytes, message: bytes) -> bytes:
    return hmac.new(key, message, hashlib.sha256).digest()


def bytes_to_tokens(b: bytes, count: int) -> list:
    # Map each byte to 01..26
    tokens = []
    for i in range(min(count, len(b))):
        tokens.append(f"{(b[i] % 26) + 1:02d}")
    # pad if needed
    while len(tokens) < count:
        tokens.append("01")
    return tokens

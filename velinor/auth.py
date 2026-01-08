"""Simple local auth + persistence using SQLite.

Features:
- SQLite DB at `velinor_auth.db` with `users` and `profiles` tables
- Password hashing with PBKDF2-HMAC-SHA256 (no external deps)
- HMAC-signed tokens using `SECRET_KEY` env var
- Helper functions: create_user, authenticate_user, create_access_token, verify_token, save_profile, load_profile
"""
from __future__ import annotations
import sqlite3
from pathlib import Path
import os
import json
import hashlib
import hmac
import base64
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

DB_PATH = Path(__file__).parent / "velinor_auth.db"
SECRET_KEY = os.environ.get("VELINOR_SECRET_KEY", None) or base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()


def _get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            profile_json TEXT,
            updated_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def _hash_password(password: str, salt: Optional[bytes] = None) -> (str, str):
    if salt is None:
        salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_000)
    return base64.b64encode(dk).decode(), base64.b64encode(salt).decode()


def create_user(username: str, password: str) -> Dict[str, Any]:
    init_db()
    pw_hash, salt = _hash_password(password)
    conn = _get_conn()
    cur = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    try:
        cur.execute("INSERT INTO users (username, password_hash, salt, created_at) VALUES (?, ?, ?, ?)",
                    (username, pw_hash, salt, now))
        conn.commit()
        user_id = cur.lastrowid
        return {"id": user_id, "username": username}
    except sqlite3.IntegrityError:
        raise ValueError("username_taken")
    finally:
        conn.close()


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    init_db()
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    init_db()
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    user = get_user_by_username(username)
    if not user:
        return None
    stored_hash = user['password_hash']
    salt = base64.b64decode(user['salt'])
    attempt_hash, _ = _hash_password(password, salt)
    if hmac.compare_digest(attempt_hash, stored_hash):
        return user
    return None


def _sign(payload_b64: str) -> str:
    sig = hmac.new(SECRET_KEY.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(sig).decode()


def create_access_token(user_id: int, expires_minutes: int = 60 * 24 * 7) -> str:
    exp = int((datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)).timestamp())
    payload = json.dumps({"user_id": user_id, "exp": exp}, separators=(',', ':'))
    payload_b64 = base64.urlsafe_b64encode(payload.encode('utf-8')).decode()
    sig = _sign(payload_b64)
    return f"{payload_b64}.{sig}"


def verify_token(token: str) -> Optional[int]:
    try:
        payload_b64, sig = token.split('.')
        expected = _sign(payload_b64)
        if not hmac.compare_digest(expected, sig):
            return None
        payload_json = base64.urlsafe_b64decode(payload_b64.encode('utf-8')).decode('utf-8')
        payload = json.loads(payload_json)
        if int(payload.get('exp', 0)) < int(datetime.now(timezone.utc).timestamp()):
            return None
        return int(payload.get('user_id'))
    except Exception:
        return None


def save_profile(user_id: int, profile: Dict[str, Any]) -> None:
    init_db()
    conn = _get_conn()
    cur = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cur.execute("REPLACE INTO profiles (user_id, profile_json, updated_at) VALUES (?, ?, ?)",
                (user_id, json.dumps(profile), now))
    conn.commit()
    conn.close()


def load_profile(user_id: int) -> Optional[Dict[str, Any]]:
    init_db()
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT profile_json FROM profiles WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    try:
        return json.loads(row['profile_json'])
    except Exception:
        return None


# Initialize DB on import
init_db()

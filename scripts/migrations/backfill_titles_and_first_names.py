"""
Backfill migration for conversations and conversation_messages.

Usage:
    python3 backfill_titles_and_first_names.py [--apply]

By default runs in dry-run mode and prints what would be changed.
Pass `--apply` to actually PATCH rows in Supabase.

The script expects the environment variables:
  SUPABASE_URL
  SUPABASE_SERVICE_ROLE_KEY (preferred) or SUPABASE_KEY

It will:
 - Find conversations where `title` is NULL or empty and set `title` to `auto_name` or generated name.
 - Find conversation_messages where `first_name` is NULL/empty and set it to a best-effort value
   (profile first_name if available, otherwise username, otherwise 'Friend').

This is best-effort and safe to run multiple times; all updates are idempotent.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

import requests

# Minimal imports from project to use name generation
try:
    from emotional_os.deploy.modules.conversation_manager import generate_auto_name
except Exception:

    def generate_auto_name(first_message: str, first_name: Optional[str] = None, max_length: int = 50) -> str:
        # Fallback simple generator
        if not first_message:
            return "New Conversation"
        title = first_message.strip().split("\n")[0][:max_length]
        if first_name:
            fn = str(first_name).split()[0]
            return f"{fn}'s {title}"
        return title


logger = logging.getLogger("backfill")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("SUPABASE_BASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY/SUPABASE_KEY environment variables.")
    sys.exit(1)

HEADERS = {
    "Content-Type": "application/json",
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Prefer": "return=representation",
}

BASE = SUPABASE_URL.rstrip("/")

# Helper functions


def _get_conversations_missing_title(limit: int = 200) -> List[Dict[str, Any]]:
    """Return conversations where title is NULL or empty string."""
    url = f"{BASE}/rest/v1/conversations"
    # PostgREST filter: or=(title.is.null,title.eq.'')  (note quotes required)
    params = {
        "select": "conversation_id,user_id,auto_name,first_message,title",
        "or": "(title.is.null,title.eq.'')",
        "limit": str(limit),
    }
    resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
    if resp.status_code != 200:
        logger.error("Failed to query conversations (HTTP %s): %s", resp.status_code, resp.text)
        return []
    return resp.json()


def _get_messages_missing_first_name(limit: int = 500) -> List[Dict[str, Any]]:
    url = f"{BASE}/rest/v1/conversation_messages"
    params = {
        "select": "id,conversation_id,user_id,role,message,first_name",
        "or": "(first_name.is.null,first_name.eq.'')",
        "limit": str(limit),
    }
    resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
    if resp.status_code != 200:
        logger.error("Failed to query messages (HTTP %s): %s", resp.status_code, resp.text)
        return []
    return resp.json()


def _try_fetch_profile_first_name(user_id: str) -> Optional[str]:
    """Best-effort: look for a `profiles` table with a first_name or a users table.
    Returns first_name or username if found."""
    # Try common profiles table (id=eq.user_id)
    profiles_url = f"{BASE}/rest/v1/profiles"
    params = {"select": "first_name,username", "id": f"eq.{user_id}", "limit": "1"}
    try:
        r = requests.get(profiles_url, headers=HEADERS, params=params, timeout=8)
        if r.status_code == 200:
            rows = r.json()
            if rows:
                row = rows[0]
                if row.get("first_name"):
                    return row.get("first_name")
                if row.get("username"):
                    return row.get("username")
    except Exception:
        pass

    # Try a users table keyed by user_id
    users_url = f"{BASE}/rest/v1/users"
    params = {"select": "first_name,username", "user_id": f"eq.{user_id}", "limit": "1"}
    try:
        r = requests.get(users_url, headers=HEADERS, params=params, timeout=8)
        if r.status_code == 200:
            rows = r.json()
            if rows:
                row = rows[0]
                if row.get("first_name"):
                    return row.get("first_name")
                if row.get("username"):
                    return row.get("username")
    except Exception:
        pass

    return None


def _patch_conversation_title(conversation_id: str, new_title: str, apply: bool = False) -> bool:
    url = f"{BASE}/rest/v1/conversations"
    params = {"conversation_id": f"eq.{conversation_id}"}
    payload = {"title": new_title, "updated_at": __import__("datetime").datetime.now().isoformat()}
    if not apply:
        logger.info("DRY-RUN: would PATCH conversation %s -> title=%s", conversation_id, new_title)
        return True
    r = requests.patch(url, headers=HEADERS, params=params, json=payload, timeout=10)
    if r.status_code in (200, 204):
        logger.info("Patched conversation %s", conversation_id)
        return True
    logger.error("Failed to patch conversation %s (HTTP %s): %s", conversation_id, r.status_code, r.text)
    return False


def _patch_message_first_name(message_id: Any, new_first_name: str, apply: bool = False) -> bool:
    url = f"{BASE}/rest/v1/conversation_messages"
    params = {"id": f"eq.{message_id}"}
    payload = {"first_name": new_first_name, "timestamp": __import__("datetime").datetime.now().isoformat()}
    if not apply:
        logger.info("DRY-RUN: would PATCH message %s -> first_name=%s", message_id, new_first_name)
        return True
    r = requests.patch(url, headers=HEADERS, params=params, json=payload, timeout=10)
    if r.status_code in (200, 204):
        logger.info("Patched message %s", message_id)
        return True
    logger.error("Failed to patch message %s (HTTP %s): %s", message_id, r.status_code, r.text)
    return False


def main(argv: List[str]):
    parser = argparse.ArgumentParser(description="Backfill conversation titles and message first_names")
    parser.add_argument("--apply", action="store_true", help="Actually write changes. Default is dry-run.")
    args = parser.parse_args(argv)

    apply = args.apply
    logger.info("Starting backfill (apply=%s)", apply)

    # Backfill conversation titles
    convs = _get_conversations_missing_title(limit=500)
    logger.info("Found %d conversations with missing titles", len(convs))
    conv_updates = 0
    for conv in convs:
        conv_id = conv.get("conversation_id")
        auto = conv.get("auto_name")
        first_msg = conv.get("first_message") or ""
        user_id = conv.get("user_id")
        # Try to fetch user's first name for nicer prefixing
        user_first = None
        if user_id:
            user_first = _try_fetch_profile_first_name(user_id)
        new_title = auto or generate_auto_name(first_msg, user_first)
        if new_title:
            ok = _patch_conversation_title(conv_id, new_title, apply=apply)
            if ok:
                conv_updates += 1

    logger.info("Conversations updated: %d", conv_updates)

    # Backfill message first_name
    msgs = _get_messages_missing_first_name(limit=1000)
    logger.info("Found %d messages missing first_name", len(msgs))
    msg_updates = 0
    for m in msgs:
        mid = m.get("id") or m.get("message_id") or m.get("conversation_message_id")
        uid = m.get("user_id")
        if not mid:
            continue
        # best-effort fetch
        candidate = None
        if uid:
            candidate = _try_fetch_profile_first_name(uid)
        if not candidate:
            candidate = "Friend"
        ok = _patch_message_first_name(mid, candidate, apply=apply)
        if ok:
            msg_updates += 1

    logger.info("Messages updated: %d", msg_updates)
    logger.info("Backfill finished. (apply=%s)", apply)


if __name__ == "__main__":
    main(sys.argv[1:])

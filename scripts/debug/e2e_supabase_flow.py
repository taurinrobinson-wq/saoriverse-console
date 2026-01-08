#!/usr/bin/env python3
"""
End-to-end Supabase flow for local testing.

Steps:
- Create a test user via Supabase Admin API (/auth/v1/admin/users)
- Save a conversation with multiple messages via ConversationManager
- Load conversations and a single conversation to verify persistence
- Re-instantiate manager to simulate a refresh and re-load
- Cleanup: delete conversation and test user

Requires environment variables:
- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY

Run:
  python3 scripts/e2e_supabase_flow.py

Be careful: this will create and delete a user in your Supabase project.
"""

import importlib.util
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone

try:
    import requests
except Exception:
    print("requests library required")
    sys.exit(1)

# Ensure repository root is on sys.path so package imports resolve when running
# this script directly (e.g., `python3 scripts/e2e_supabase_flow.py`).
sys.path.insert(0, os.getcwd())

# Import ConversationManager by file path to avoid package-import issues
cm_path = os.path.join(os.getcwd(), "emotional_os", "deploy", "modules", "conversation_manager.py")
spec = importlib.util.spec_from_file_location("conversation_manager", cm_path)
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
ConversationManager = cm.ConversationManager

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SERVICE_KEY:
    print("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in the environment")
    sys.exit(2)

headers = {"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}", "Content-Type": "application/json"}


def create_user(email, password="TestPass123!"):
    url = f"{SUPABASE_URL}/auth/v1/admin/users"
    payload = {
        "email": email,
        "password": password,
        # optional: set email_confirm to true to bypass verification
        "email_confirm": True,
    }
    r = requests.post(url, headers=headers, json=payload, timeout=15)
    print("create_user status:", r.status_code)
    try:
        print(r.text)
    except Exception:
        pass
    if r.status_code in (200, 201):
        return r.json()
    else:
        return None


def delete_user(user_id):
    url = f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}"
    r = requests.delete(url, headers=headers, timeout=15)
    print("delete_user status:", r.status_code)
    try:
        print(r.text)
    except Exception:
        pass
    return r.status_code in (200, 204)


def main():
    test_email = f"e2e-test+{int(time.time())}@example.com"
    print("Creating test user:", test_email)
    user = create_user(test_email)
    if not user:
        print("Failed to create user; aborting")
        sys.exit(3)
    user_id = user.get("id")
    print("Created user id:", user_id)

    # Instantiate ConversationManager with the created user id
    mgr = ConversationManager(user_id)

    conv_id = str(uuid.uuid4())
    messages = []

    # Simulate sending 3 messages sequentially and saving after each
    for i, text in enumerate(
        [
            "I feel anxious about the new project.",
            "Yesterday's meeting raised many concerns for me.",
            "But I'm trying to focus on small wins and progress.",
        ],
        start=1,
    ):
        msg = {
            "user": text,
            "assistant": f"Test assistant reply for message {i}",
            "role": "user" if i % 2 == 1 else "assistant",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        messages.append(msg)
        ok, res_msg = mgr.save_conversation(conv_id, f"E2E test conv {conv_id[:8]}", messages, processing_mode="local")
        print(f"Saved after msg {i}:", ok, res_msg)
        time.sleep(0.5)

    print("\nListing conversations:")
    convs = mgr.load_conversations()
    print("count:", len(convs))
    try:
        print(json.dumps(convs, indent=2, default=str))
    except Exception:
        print(convs)

    print("\nLoading conversation by id:")
    loaded = mgr.load_conversation(conv_id)
    if loaded:
        print("loaded keys:", list(loaded.keys()))
        try:
            print(json.dumps(loaded, indent=2, default=str))
        except Exception:
            print(loaded)
    else:
        print("load_conversation returned None")

    print("\nSimulating refresh by creating a new ConversationManager instance")
    mgr2 = ConversationManager(user_id)
    convs2 = mgr2.load_conversations()
    print("post-refresh count:", len(convs2))

    found = any(c.get("conversation_id") == conv_id for c in convs2)
    print("Conversation present after refresh?", found)

    # Cleanup: delete conversation and user
    print("\nDeleting conversation...")
    ok_del = mgr.delete_conversation(conv_id)
    print("delete conversation ok?", ok_del)

    print("Deleting test user...")
    ok_user = delete_user(user_id)
    print("delete user ok?", ok_user)

    print("\nE2E flow complete")


if __name__ == "__main__":
    main()

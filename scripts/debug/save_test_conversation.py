#!/usr/bin/env python3
"""
Small helper to save/load a test conversation using ConversationManager.
Run after exporting SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or via st.secrets).

Usage:
  export SUPABASE_URL="https://<project>.supabase.co"
  export SUPABASE_SERVICE_ROLE_KEY="<service-role-key>"
  python3 scripts/save_test_conversation.py --user-id <user-id>

If your user id is a UUID (preferred), use that. If you are testing demo mode, use the demo placeholder id printed in the UI when `FP_DEBUG_UI=1`.
"""

import argparse
import json
import os
import uuid
from datetime import datetime, timezone

from emotional_os.deploy.modules.conversation_manager import ConversationManager


def main():
    parser = argparse.ArgumentParser(description="Save & load a test conversation via ConversationManager")
    parser.add_argument("--user-id", required=True, help="User id to use when saving the conversation (string or UUID)")
    parser.add_argument("--conv-id", default=None, help="Optional conversation id (defaults to random uuid)")
    args = parser.parse_args()

    user_id = args.user_id
    conv_id = args.conv_id or str(uuid.uuid4())

    print(
        f"Using SUPABASE_URL={os.environ.get('SUPABASE_URL')} (masked) and service role key present? {'YES' if os.environ.get('SUPABASE_SERVICE_ROLE_KEY') else 'NO'}"
    )

    mgr = ConversationManager(user_id)

    # Build a small messages array consistent with the UI shape
    messages = [
        {
            "user": "Test user message: I'm running an end-to-end persistence check.",
            "assistant": "Thanks for sharing. This is a test conversation saved to Supabase.",
            "role": "user",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    ]

    title = "E2E test conversation"

    print("Saving conversation...")
    ok, msg = mgr.save_conversation(conv_id, title, messages, processing_mode="local")
    print("save:", ok, msg)

    print("Listing conversations for user...")
    convs = mgr.load_conversations()
    print("found:", len(convs))
    if convs:
        try:
            print(json.dumps(convs, indent=2, default=str))
        except Exception:
            print(convs)

    print("Loading single conversation by id...")
    loaded = mgr.load_conversation(conv_id)
    if not loaded:
        print("ERROR: load_conversation returned None")
    else:
        print("Loaded conversation:")
        try:
            print(json.dumps(loaded, indent=2, default=str))
        except Exception:
            print(loaded)

    # Optionally delete the conversation to clean up
    do_delete = os.environ.get("FP_TEST_CLEANUP", "0") == "1"
    if do_delete:
        print("Deleting conversation (cleanup)...")
        ok, msg = mgr.delete_conversation(conv_id)
        print("delete:", ok, msg)


if __name__ == "__main__":
    main()

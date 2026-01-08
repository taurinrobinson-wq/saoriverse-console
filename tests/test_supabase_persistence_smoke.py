import json
import types
import uuid
from datetime import datetime

import streamlit as st

from emotional_os.deploy.modules.conversation_manager import ConversationManager


class FakeResponse:
    def __init__(self, status_code=200, data=None):
        self.status_code = status_code
        self._data = data or {}

    def json(self):
        return self._data


class FakeRequests:
    def __init__(self):
        self._store = {}

    def post(self, url, headers=None, json=None, timeout=None):
        # Simulate upsert to /rest/v1/conversations
        if "/rest/v1/conversations" in url:
            # json is expected to be a list with a single payload
            payload = json[0] if isinstance(json, list) and json else json
            cid = payload.get("conversation_id") or str(uuid.uuid4())
            key = (payload.get("user_id"), cid)
            # store messages as JSON string as real DB would
            stored = payload.copy()
            stored["messages"] = payload.get("messages")
            self._store[key] = stored
            return FakeResponse(status_code=201, data={"success": True})
        if "/rest/v1/user_preferences" in url:
            return FakeResponse(status_code=201, data={"success": True})
        return FakeResponse(status_code=404, data={"error": "not found"})

    def get(self, url, headers=None, params=None, timeout=None):
        # list conversations
        if "/rest/v1/conversations" in url:
            user_id = None
            if params and "user_id" in params:
                # param like 'eq.userid'
                user_id = params.get("user_id").replace("eq.", "")
            # collect stored items for this user
            out = []
            for (uid, cid), row in self._store.items():
                if uid == user_id:
                    out.append(
                        {
                            "conversation_id": cid,
                            "title": row.get("title"),
                            "updated_at": row.get("updated_at"),
                            "message_count": row.get("message_count"),
                            "processing_mode": row.get("processing_mode", "local"),
                            "messages": row.get("messages"),
                        }
                    )
            return FakeResponse(status_code=200, data=out)
        if "/rest/v1/user_preferences" in url:
            return FakeResponse(status_code=200, data=[{"persist_history": True, "persist_confirmed": False}])
        return FakeResponse(status_code=404, data={})

    def delete(self, url, headers=None, params=None, timeout=None):
        # naive delete implementation
        if "/rest/v1/conversations" in url and params:
            conv = params.get("conversation_id")
            user = params.get("user_id")
            # parse eq.xxx
            if conv and user:
                cid = conv.replace("eq.", "")
                uid = user.replace("eq.", "")
                key = (uid, cid)
                if key in self._store:
                    del self._store[key]
                    return FakeResponse(status_code=204, data={})
                return FakeResponse(status_code=404, data={})
        return FakeResponse(status_code=400, data={})


def test_conversation_save_and_load(monkeypatch):
    # Arrange: create a ConversationManager with fake supabase URL/key
    user_id = "test-user-1234"
    mgr = ConversationManager(user_id, supabase_url="http://example.test", supabase_key="fake-key")

    fake_requests = FakeRequests()
    # Patch the requests module used inside the conversation_manager
    monkeypatch.setattr("emotional_os.deploy.modules.conversation_manager.requests", fake_requests)

    # Create a fake conversation
    conv_id = str(uuid.uuid4())
    messages = [{"user": "I feel anxious about the meeting", "assistant": "I hear you."}]
    title = "Anxious about meeting"

    # Act: save conversation
    success, msg = mgr.save_conversation(conv_id, title, messages, processing_mode="local")

    # Assert save succeeded
    assert success is True
    assert "saved" in msg.lower()

    # Act: load list of conversations
    conversations = mgr.load_conversations()
    assert isinstance(conversations, list)
    assert len(conversations) == 1
    conv = conversations[0]
    assert conv["conversation_id"] == conv_id
    assert conv["title"] == title

    # Act: load the single conversation
    loaded = mgr.load_conversation(conv_id)
    assert loaded is not None
    assert isinstance(loaded.get("messages"), list)
    assert loaded["messages"][0]["user"] == messages[0]["user"]

    # Delete the conversation
    ok, _ = mgr.delete_conversation(conv_id)
    assert ok is True

    # Ensure deletion removed it
    conversations_after = mgr.load_conversations()
    assert conversations_after == []

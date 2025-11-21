import json
import types

import pytest


def test_save_conversation_with_non_uuid_user_id_returns_helpful_error(monkeypatch):
    """
    Ensure that when the Supabase REST API returns a UUID parsing error
    (because `user_id` was not a UUID), the ConversationManager.save_conversation
    surface a helpful error message that includes the response body.
    """
    # Import here to ensure the module uses the test's monkeypatches
    from emotional_os.deploy.modules import conversation_manager

    # Create a dummy response object to simulate Supabase returning a 400
    class DummyResponse:
        status_code = 400

        def __init__(self, text):
            self.text = text

        def json(self):
            return json.loads(self.text)

    # Simulate the specific Postgres error returned by Supabase for UUID parse
    dummy_body = json.dumps({
        "code": "22P02",
        "message": "invalid input syntax for type uuid: \"debug_user\"",
    })

    def dummy_post(url, headers=None, json=None, timeout=None):
        return DummyResponse(dummy_body)

    # Ensure the ConversationManager sees our dummy `requests.post`
    monkeypatch.setattr(conversation_manager, 'requests',
                        types.SimpleNamespace(post=dummy_post))

    # Instantiate manager with a non-UUID user_id
    mgr = conversation_manager.ConversationManager(
        user_id='debug_user', supabase_url='https://example.supabase.co', supabase_key='fake')

    # Force writes-enabled so the code attempts the POST
    monkeypatch.setattr(mgr, '_writes_enabled', lambda: True)

    ok, msg = mgr.save_conversation(
        'cid-debug', 'Title', [{'user': 'u', 'assistant': 'a'}])

    assert ok is False
    # The manager should include the response body (or at least the uuid error text)
    assert 'invalid input syntax' in msg or 'uuid' in msg.lower()

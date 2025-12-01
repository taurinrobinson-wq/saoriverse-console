import os
import sys


class FakeResp:
    def __init__(self, status_code, json_data=None):
        self.status_code = status_code
        self._json = json_data if json_data is not None else []

    def json(self):
        return self._json


class FakeRequests:
    def __init__(self):
        # simple in-memory store keyed by user_id
        self.storage = {}

    def post(self, url, headers=None, json=None, timeout=None):
        try:
            # Expect json to be a list with one payload
            payload = json[0]
            uid = payload.get("user_id")
            # Store the payload (simulate upsert)
            self.storage[uid] = payload
            return FakeResp(201, [payload])
        except Exception:
            return FakeResp(400, [])

    def get(self, url, headers=None, params=None, timeout=None):
        # params expected to include 'user_id' like 'eq.<id>'
        user_id_param = (params or {}).get("user_id", "")
        uid = user_id_param.split("eq.")[-1] if "eq." in user_id_param else user_id_param
        if uid in self.storage:
            return FakeResp(200, [self.storage[uid]])
        return FakeResp(200, [])


def test_save_and_load_user_preferences(monkeypatch):
    # make repo root importable
    sys.path.insert(0, os.getcwd())

    import emotional_os.deploy.modules.conversation_manager as cm
    from emotional_os.deploy.modules.conversation_manager import ConversationManager

    fake = FakeRequests()
    monkeypatch.setattr(cm, "requests", fake)

    mgr = ConversationManager(user_id="test_user", supabase_url="https://example.supabase.co", supabase_key="testkey")

    success, msg = mgr.save_user_preferences({"persist_history": True, "persist_confirmed": True})
    assert success is True

    prefs = mgr.load_user_preferences()
    assert prefs.get("persist_history") is True
    assert prefs.get("persist_confirmed") is True


def test_load_missing_preferences(monkeypatch):
    sys.path.insert(0, os.getcwd())
    import emotional_os.deploy.modules.conversation_manager as cm
    from emotional_os.deploy.modules.conversation_manager import ConversationManager

    fake = FakeRequests()
    monkeypatch.setattr(cm, "requests", fake)

    mgr = ConversationManager(
        user_id="no_such_user", supabase_url="https://example.supabase.co", supabase_key="testkey"
    )
    prefs = mgr.load_user_preferences()
    assert prefs == {}

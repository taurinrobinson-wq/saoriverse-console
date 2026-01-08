import base64
import datetime
import json
import urllib.error
import urllib.request

s = {
    "username": "localtester",
    "user_id": "localtester",
    "created": datetime.datetime.now().isoformat(),
    "expires": (datetime.datetime.now() + datetime.timedelta(days=2)).isoformat(),
}

token = base64.b64encode(json.dumps(s).encode()).decode()

body = json.dumps(
    {
        "conversation_id": "test-conv-1",
        "title": "Local test",
        "user_id": "localtester",
        "messages": [{"role": "user", "text": "hello"}],
    }
).encode()

req = urllib.request.Request(
    "http://127.0.0.1:18081/api/save_conversation",
    data=body,
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=10) as r:
        print("STATUS", r.status)
        print("BODY", r.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP", e.code)
    try:
        print("BODY", e.read().decode())
    except Exception:
        pass
except Exception as e:
    print("ERR", e)

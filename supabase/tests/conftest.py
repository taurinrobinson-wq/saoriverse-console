import pytest
import os
import time
import uuid
import json
import base64
import hmac
import hashlib
import requests


def _b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("utf-8")


def _sign_jwt_hs256(header: dict, payload: dict, secret: str) -> str:
    unsigned = _b64u(json.dumps(header).encode()) + "." + \
        _b64u(json.dumps(payload).encode())
    sig = hmac.new(secret.encode(), unsigned.encode(), hashlib.sha256).digest()
    return unsigned + "." + _b64u(sig)


def _create_admin_user(supabase_url: str, service_key: str, email: str, password: str) -> dict:
    url = f"{supabase_url}/auth/v1/admin/users"
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
    }
    payload = {"email": email, "password": password, "email_confirm": True}
    r = requests.post(url, headers=headers, json=payload, timeout=15)
    try:
        return r.json()
    except Exception:
        return {"error": True, "status_code": r.status_code, "text": r.text}


# At import time, ensure a TEST_ACCESS_TOKEN is available for tests.
TEST_ACCESS_TOKEN = os.environ.get("TEST_ACCESS_TOKEN")
if not TEST_ACCESS_TOKEN:
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get(
        "PROJECT_SERVICE_ROLE_KEY")
    PUBLISHABLE = os.environ.get(
        "SUPABASE_PUBLISHABLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
    JWT_SECRET = os.environ.get("PROJECT_JWT_SECRET")

    if SERVICE_KEY and SUPABASE_URL:
        # create a test admin user
        email = f"pytests_{uuid.uuid4().hex[:8]}@example.com"
        password = "P@ssw0rdTest"
        resp = _create_admin_user(SUPABASE_URL, SERVICE_KEY, email, password)
        user_id = resp.get("id") or resp.get("user_id") or resp.get("id")

        # Try password grant (may fail if email provider disabled)
        token = None
        try:
            token_url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
            r = requests.post(token_url, headers={"apikey": PUBLISHABLE, "Content-Type": "application/json"}, json={
                              "email": email, "password": password}, timeout=10)
            j = r.json()
            token = j.get("access_token")
        except Exception:
            token = None

        # If password grant failed, but we have the JWT secret, sign a token for the created user
        if not token and JWT_SECRET and user_id:
            header = {"alg": "HS256", "typ": "JWT"}
            now = int(time.time())
            payload = {"iss": "supabase", "sub": user_id,
                       "aud": "authenticated", "iat": now, "exp": now + 86400}
            try:
                token = _sign_jwt_hs256(header, payload, JWT_SECRET)
            except Exception:
                token = None

        if token:
            os.environ["TEST_ACCESS_TOKEN"] = token
            os.environ["SUPABASE_ANON_KEY"] = token


def pytest_configure(config):
    # Ensure tests that import environment pick up the TEST_ACCESS_TOKEN if present
    token = os.environ.get("TEST_ACCESS_TOKEN")
    if token:
        os.environ["SUPABASE_ANON_KEY"] = token


class _DummyResponse:
    def __init__(self, status_code=200, data=None):
        self.status_code = status_code
        self._data = data or {}

    @property
    def text(self):
        try:
            return json.dumps(self._data)
        except Exception:
            return str(self._data)

    def json(self):
        return self._data


@pytest.fixture(autouse=True)
def stub_supabase_functions(monkeypatch):
    """Autouse fixture that stubs external Supabase Function calls to avoid
    relying on network during unit tests. Tests that explicitly patch
    `requests.post` will override this fixture.
    """
    import requests as _requests

    real_post = _requests.post

    def _fake_post(url, *args, **kwargs):
        # Normalize url
        u = str(url)
        # auth-manager
        if '/functions/v1/auth-manager' in u:
            body = kwargs.get('json') or {}
            action = body.get('action') if isinstance(body, dict) else None
            if action == 'create_user':
                user = {
                    'id': f"{uuid.uuid4()}",
                    'username': body.get('username'),
                    'email': body.get('email')
                }
                return _DummyResponse(200, {'success': True, 'user': user})
            if action == 'authenticate':
                return _DummyResponse(200, {'authenticated': True, 'access_token': os.environ.get('TEST_ACCESS_TOKEN', 'test_access_token')})
            return _DummyResponse(200, {'ok': True})

        # saori-fixed and authenticated-saori functions
        if '/functions/v1/saori-fixed' in u or '/functions/v1/authenticated-saori' in u:
            # Inspect headers for tokens (X-Custom-Token or Authorization) and fall back to SUPABASE_ANON_KEY
            headers = kwargs.get('headers') or {}
            token = None
            xcustom = headers.get(
                'X-Custom-Token') or headers.get('x-custom-token')
            if isinstance(xcustom, str) and xcustom.lower().startswith('bearer '):
                token = xcustom.split(None, 1)[1]
            auth = headers.get('Authorization') or headers.get('authorization')
            if not token and isinstance(auth, str) and auth.lower().startswith('bearer '):
                token = auth.split(None, 1)[1]

            has_platform_key = bool(os.environ.get(
                'SUPABASE_ANON_KEY') or os.environ.get('SUPABASE_PUBLISHABLE_KEY'))

            # authenticated-saori should return a log with user id when a test token/user is present
            if '/functions/v1/authenticated-saori' in u:
                if token and token in (os.environ.get('TEST_CUSTOM_TOKEN'), os.environ.get('TEST_ACCESS_TOKEN')):
                    return _DummyResponse(200, {'reply': 'Test reply', 'log': {'user_id': os.environ.get('TEST_USER_ID')}})
                if has_platform_key:
                    return _DummyResponse(200, {'reply': 'Test reply', 'log': {'user_id': os.environ.get('TEST_USER_ID')}})
                return _DummyResponse(200, {'reply': 'Authentication failed - this is a test'})

            # saori-fixed: accept platform key or test access token
            if token and token in (os.environ.get('TEST_ACCESS_TOKEN'), os.environ.get('TEST_CUSTOM_TOKEN')):
                return _DummyResponse(200, {'reply': 'Test reply'})
            if has_platform_key:
                return _DummyResponse(200, {'reply': 'Test reply'})
            return _DummyResponse(200, {'reply': 'Authentication failed - this is a test'})

        # Default: fall back to real post for other urls
        try:
            return real_post(url, *args, **kwargs)
        except Exception:
            return _DummyResponse(502, {'error': 'network unavailable in test'})

    monkeypatch.setattr(_requests, 'post', _fake_post)

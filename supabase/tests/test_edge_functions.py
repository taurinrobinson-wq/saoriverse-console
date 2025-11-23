import os
import time
import uuid
import requests
from dotenv import load_dotenv


load_dotenv(dotenv_path=os.path.join(
    os.path.dirname(__file__), '..', '..', '.env'))


def get_env(key: str):
    return os.environ.get(key)


def headers_anon():
    key = os.environ.get('SUPABASE_ANON_KEY')
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {key}' if key else None,
        'apikey': key
    }


def random_username():
    return f"test_user_{uuid.uuid4().hex[:8]}"


def test_create_and_authenticate_user():
    """Create a user via auth-manager and authenticate to retrieve a custom token."""
    assert get_env(
        'SUPABASE_AUTH_URL'), "SUPABASE_AUTH_URL must be set in .env"

    username = random_username()
    payload = {
        'action': 'create_user',
        'username': username,
        'password': 'P@ssw0rdTest',
        'email': f'{username}@example.com',
        'first_name': 'Test',
        'last_name': 'Harness',
        'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }

    r = requests.post(get_env('SUPABASE_AUTH_URL'), json=payload,
                      headers=headers_anon(), timeout=15)
    assert r.status_code == 200, r.text
    resp = r.json()
    assert resp.get('success') is True and resp.get(
        'user') and resp['user'].get('id')
    user_id = resp['user']['id']

    # Authenticate
    r2 = requests.post(get_env('SUPABASE_AUTH_URL'), json={
                       'action': 'authenticate', 'username': username, 'password': 'P@ssw0rdTest'}, headers=headers_anon(), timeout=15)
    assert r2.status_code == 200, r2.text
    ar = r2.json()
    assert ar.get('authenticated') is True
    assert ar.get('access_token')

    # Save token for subsequent tests in env (temporary, only for this process)
    os.environ['TEST_CUSTOM_TOKEN'] = ar['access_token']
    os.environ['TEST_USER_ID'] = user_id


def test_saori_fixed_anonymous():
    """Call saori-fixed as anonymous (platform anon key) and expect a reply."""
    assert get_env(
        'SUPABASE_FUNCTION_URL'), "SUPABASE_FUNCTION_URL must be set in .env"

    # The saori-fixed function is at /saori-fixed; build URL from SUPABASE_URL if needed
    sup_url = get_env('SUPABASE_URL')
    url = f"{sup_url}/functions/v1/saori-fixed"
    r = requests.post(url, json={'message': 'hello test',
                      'mode': 'quick'}, headers=headers_anon(), timeout=20)
    assert r.status_code == 200, r.text
    j = r.json()
    assert 'reply' in j and isinstance(j['reply'], str)


def test_authenticated_saori_with_custom_token():
    """Call authenticated-saori using the custom token in X-Custom-Token and platform apikey in Authorization."""
    token = os.environ.get('TEST_CUSTOM_TOKEN')
    user_id = os.environ.get('TEST_USER_ID')
    assert token, 'TEST_CUSTOM_TOKEN not set; run test_create_and_authenticate_user first or run whole suite'
    url = f"{get_env('SUPABASE_URL')}/functions/v1/authenticated-saori"
    headers = headers_anon()
    headers['X-Custom-Token'] = f'Bearer {token}'

    r = requests.post(url, json={'message': 'I feel anxious',
                      'mode': 'quick', 'user_id': user_id}, headers=headers, timeout=20)
    assert r.status_code == 200, r.text
    j = r.json()
    assert 'reply' in j
    assert j.get('log', {}).get('user_id') == user_id

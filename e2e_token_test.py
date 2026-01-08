import requests
import sqlite3
from pathlib import Path
import json

BASE = "http://localhost:8000"
user = {"username": "e2e_test_user4", "password": "e2e_pass4"}

# Register
try:
    r = requests.post(f"{BASE}/api/auth/register", json=user, timeout=5)
    print('register status', r.status_code, r.text)
except Exception as e:
    print('register error', e)

# Login
r = requests.post(f"{BASE}/api/auth/login", json=user, timeout=5)
print('login status', r.status_code, r.text)
if r.status_code != 200:
    raise SystemExit('login failed')

token = r.json().get('access_token')
print('token length', len(token))
headers = {'Authorization': f'Bearer {token}'}

# Start game
r = requests.post(f"{BASE}/api/game/start", json={'player_name': 'TokenPlayer4'}, headers=headers, timeout=5)
print('start status', r.status_code)
print(json.dumps(r.json(), indent=2))
session = r.json().get('session_id')

# Take first action
r = requests.post(f"{BASE}/api/game/{session}/action", json={'choice_index': 0}, headers=headers, timeout=5)
print('action status', r.status_code)
print(json.dumps(r.json(), indent=2))

# Save session
r = requests.post(f"{BASE}/api/game/{session}/save", headers=headers, timeout=5)
print('save status', r.status_code, r.text)

# Inspect DB
p = Path('velinor') / 'velinor_auth.db'
if not p.exists():
    p = Path('velinor_auth.db')
print('DB path', p)
if p.exists():
    conn = sqlite3.connect(str(p))
    cur = conn.cursor()
    cur.execute('SELECT u.id, u.username, p.profile_json FROM users u LEFT JOIN profiles p ON u.id=p.user_id WHERE u.username=?', (user['username'],))
    row = cur.fetchone()
    print('db row', row)
    conn.close()
else:
    print('auth DB not found')

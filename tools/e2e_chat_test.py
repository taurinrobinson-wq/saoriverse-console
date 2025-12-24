import sys, json, urllib.request, urllib.error

url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8001/chat'
message_arg = sys.argv[2] if len(sys.argv) > 2 else "I'm starting to feel doubtful"
payload = {"message": message_arg, "userId": "e2e_tester", "context": {}}
req = urllib.request.Request(url, json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(resp.read().decode())
except urllib.error.HTTPError as e:
    try:
        body = e.read().decode()
    except Exception:
        body = ''
    print(f'HTTP_ERROR {e.code} {body}')
except Exception as e:
    print('ERROR', str(e))

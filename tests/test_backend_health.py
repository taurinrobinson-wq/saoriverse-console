#!/usr/bin/env python
"""Lightweight backend health check - no external dependencies."""

import http.client
import json
import sys
from time import sleep

def check_health(host="127.0.0.1", port=8000, timeout=5):
    """Test backend health endpoint."""
    try:
        conn = http.client.HTTPConnection(host, port, timeout=timeout)
        conn.request("GET", "/health")
        resp = conn.getresponse()
        body = resp.read().decode()
        conn.close()
        
        if resp.status == 200:
            data = json.loads(body)
            print(f"✅ Backend is HEALTHY")
            print(f"   Status: {data.get('status')}")
            print(f"   Whisper loaded: {data.get('models', {}).get('whisper')}")
            print(f"   TTS loaded: {data.get('models', {}).get('tts')}")
            return True
        else:
            print(f"❌ Backend returned status {resp.status}")
            print(f"   Response: {body}")
            return False
    except ConnectionRefusedError:
        print(f"❌ Backend is DOWN (connection refused on {host}:{port})")
        return False
    except Exception as e:
        print(f"❌ Error checking backend: {e}")
        return False

if __name__ == "__main__":
    success = check_health()
    sys.exit(0 if success else 1)

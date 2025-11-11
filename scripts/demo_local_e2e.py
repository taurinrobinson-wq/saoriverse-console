#!/usr/bin/env python3
"""Local end-to-end demo for limbic cue injection.

Starts a tiny HTTP server that simulates the `saori-fixed` endpoint. Then
creates an `EnhancedSaoriverse` client and calls `.chat()` twice: once
without a limbic engine and once with `LimbicIntegrationEngine()` so you can
see the difference when limbic cues are injected into the generation payload.
"""
from enhanced_conversation_demo import EnhancedSaoriverse
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import os
import sys
import time

# Ensure repo root is on sys.path so imports from project root work when running from scripts/
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


try:
    from emotional_os.glyphs.limbic_integration import LimbicIntegrationEngine
except Exception:
    LimbicIntegrationEngine = None


class EchoHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', '0'))
        body = self.rfile.read(length).decode('utf-8') if length else '{}'
        try:
            data = json.loads(body)
        except Exception:
            data = {'raw': body}

    # Simulate generator: if limbic present, include the limbic emotion in reply
    reply = "I hear you — tell me more when you're ready."
      limbic_used = False
       if isinstance(data, dict) and data.get('limbic'):
            limbic = data['limbic']
            emotion = limbic.get('emotion', 'unknown')
            reply = f"[LIMBIC USED: emotion={emotion}] I hear you and I'm reflecting that feeling back to you."
            limbic_used = True

        resp = {
            'reply': reply,
            'parsed_glyphs': [],
            'limbic_decorated': limbic_used
        }

        self._set_headers()
        self.wfile.write(json.dumps(resp).encode('utf-8'))


def run_server(port=8000):
    server = HTTPServer(('127.0.0.1', port), EchoHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def main():
    port = 8000
    server = run_server(port)
    time.sleep(0.1)

    SUPABASE_FUNCTION_URL = f'http://127.0.0.1:{port}/'
    SUPABASE_ANON_KEY = 'demo-key'

    # Client without limbic engine
    client_no_limbic = EnhancedSaoriverse(
        SUPABASE_FUNCTION_URL, SUPABASE_ANON_KEY, enable_evolution=False, limbic_engine=None)

    user_message = "I felt my chest tighten when I saw her walk away"
    print('\n--- Baseline generation (no limbic) ---')
    resp1 = client_no_limbic.chat(user_message)
    print('Reply:', resp1.get('reply'))
    print('limbic_decorated flag:', resp1.get('limbic_decorated'))

    # Client with limbic engine
    limbic_engine = LimbicIntegrationEngine() if LimbicIntegrationEngine else None
    client_with_limbic = EnhancedSaoriverse(
        SUPABASE_FUNCTION_URL, SUPABASE_ANON_KEY, enable_evolution=False, limbic_engine=limbic_engine)

    print('\n--- Generation with limbic engine (injected cues) ---')
    resp2 = client_with_limbic.chat(user_message)
    print('Reply:', resp2.get('reply'))
    print('limbic_decorated flag:', resp2.get('limbic_decorated'))

    # If decoration still applies client-side, show decorated output
    if limbic_engine and not resp2.get('limbic_decorated'):
        print('\n--- Post-hoc decoration applied ---')
        print('Reply after decoration:', resp2.get('reply'))

    # Shutdown
    server.shutdown()


if __name__ == '__main__':
    main()

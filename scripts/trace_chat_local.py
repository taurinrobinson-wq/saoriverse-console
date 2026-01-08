#!/usr/bin/env python3
"""
Local trace runner for the FastAPI chat handler. This script mocks the external Saori function
to simulate different responses (normal, slow, error) and calls the `chat` coroutine directly.

It writes results to stdout and shows the last lines of the debug log created by the app.
"""
import asyncio
import importlib.util
import json
import os
import sys
import time
from unittest.mock import patch

sys.path.insert(0, os.path.abspath("emotional_os/portal"))
sys.path.insert(0, os.path.abspath("emotional_os/deploy"))
sys.path.insert(0, os.path.abspath("."))

# Import fastapi_app by path to avoid packaging/import issues in this script
spec = importlib.util.spec_from_file_location(
    "fastapi_app", os.path.join(os.path.abspath("emotional_os/deploy"), "fastapi_app.py")
)
fastapi_app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fastapi_app)
ChatRequest = fastapi_app.ChatRequest
chat = fastapi_app.chat
# Make sure local modules (deploy and portal) are importable when running this script
sys.path.insert(0, os.path.abspath("emotional_os/portal"))
sys.path.insert(0, os.path.abspath("emotional_os/deploy"))
sys.path.insert(0, os.path.abspath("."))


class FakeResponse:
    def __init__(self, status_code=200, body=None, delay=0):
        self.status_code = status_code
        self._body = body or {}
        self._delay = delay

    def json(self):
        if self._delay:
            time.sleep(self._delay)
        return self._body


def make_fake_post(body, status=200, delay=0):
    def _post(url, headers=None, json=None, timeout=None):
        return FakeResponse(status_code=status, body=body, delay=delay)

    return _post


async def run_scenarios():
    scenarios = [
        ("short_routine", "Hi, what's the weather like today?"),
        ("short_emotional", "I'm feeling really down and overwhelmed."),
        (
            "long_emotional",
            """
I don't know where to begin. Lately I've been feeling this persistent ache—like a low hum under everything.
It started after the move and I can't sleep. I tried talking to friends but it's hard to explain. I feel guilty
and ashamed and also oddly numb. Sometimes I cry and don't understand why."
""",
        ),
        ("slow_response", "Tell me a joke."),
        ("error_response", "Cause an error please"),
    ]

    for name, message in scenarios:
        print(f"--- Running scenario: {name}")

        if name == "short_routine":
            fake = make_fake_post({"reply": "It's sunny and 72F.", "glyph": {}, "processing_time": 0.12}, status=200)
        elif name == "short_emotional":
            fake = make_fake_post(
                {
                    "reply": "I'm sorry you're feeling that way. I hear you — tell me more when you're ready.",
                    "glyph": {"tag_name": "sad"},
                    "processing_time": 0.45,
                },
                status=200,
            )
        elif name == "long_emotional":
            fake = make_fake_post(
                {
                    "reply": "That sounds heavy — thank you for sharing. Let's unpack that together.",
                    "glyph": {"tag_name": "ache"},
                    "processing_time": 1.3,
                },
                status=200,
                delay=0.5,
            )
        elif name == "slow_response":
            fake = make_fake_post(
                {
                    "reply": "Why did the chicken cross the road? To get to the other side!",
                    "glyph": {},
                    "processing_time": 2.5,
                },
                status=200,
                delay=2,
            )
        else:  # error_response

            def _err(url, headers=None, json=None, timeout=None):
                raise RuntimeError("simulated network error")

            fake = _err

        with patch("requests.post", new=fake):
            req = ChatRequest(message=message, mode="local", user_id="test-user-123")
            try:
                result = await chat(req)
                print("Result:", json.dumps(result, indent=2))
            except Exception as e:
                print("Handler raised exception:", e)

        # show last few lines of the debug log
        try:
            with open("/workspaces/saoriverse-console/debug_chat.log", "r", encoding="utf-8") as fh:
                lines = fh.readlines()[-5:]
                print("\nLast log lines:")
                for l in lines:
                    print(l.strip())
        except FileNotFoundError:
            print("\nNo debug log yet.")

        print("\n")


def main():
    asyncio.run(run_scenarios())


if __name__ == "__main__":
    main()

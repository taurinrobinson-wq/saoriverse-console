#!/usr/bin/env python
"""Quick test of the chat endpoint"""
import asyncio
from emotional_os.deploy.fastapi_app import app
from emotional_os.deploy.fastapi_app import ChatRequest
import sys
import json
sys.path.insert(0, '/workspaces/saoriverse-console')


# Test creating a ChatRequest
chat_data = ChatRequest(message="Hello", mode="local", user_id="test")
print(f"✓ ChatRequest created: {chat_data}")

# Test importing the chat handler


async def test_endpoint():
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.post("/api/chat", json={
        "message": "Hello there",
        "mode": "local",
        "user_id": "test"
    })
    print(f"✓ Status: {response.status_code}")
    print(f"✓ Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_endpoint())

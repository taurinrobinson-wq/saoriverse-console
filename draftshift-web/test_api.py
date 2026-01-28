#!/usr/bin/env python3
"""
Simple test script to verify the DraftShift API is working
"""
import requests
import json
import time

# Wait for server to be ready
time.sleep(2)

BASE_URL = "http://localhost:8000"

print("Testing DraftShift Web API...")
print("=" * 50)

# Test 1: Health check
try:
    print("\n1. Testing /api/health endpoint...")
    response = requests.get(f"{BASE_URL}/api/health", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    if response.status_code == 200:
        print("   ✅ Health check passed!")
    else:
        print("   ❌ Health check failed!")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Build a simple pleading
try:
    print("\n2. Testing /api/build endpoint...")
    payload = {
        "type": "motion",
        "attorney": {"name": "John Doe", "firm": "Doe & Associates"},
        "case": {"number": "2024-001", "court": "California Superior Court"},
        "title": "Motion to Dismiss",
        "arguments": ["First argument", "Second argument"],
        "position": {}
    }
    
    response = requests.post(
        f"{BASE_URL}/api/build",
        json=payload,
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Success: {result.get('success')}")
        print(f"   Filename: {result.get('filename')}")
        if 'data' in result:
            print(f"   DOCX size: {len(result['data'])} bytes")
        print("   ✅ Build endpoint working!")
    else:
        print(f"   Response: {response.text}")
        print("   ❌ Build endpoint failed!")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Get fixtures
try:
    print("\n3. Testing /api/fixtures endpoint...")
    response = requests.get(
        f"{BASE_URL}/api/fixtures/motion.json",
        timeout=5
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        fixture = response.json()
        print(f"   Type: {fixture.get('type')}")
        print("   ✅ Fixtures endpoint working!")
    else:
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 50)
print("Testing complete!")

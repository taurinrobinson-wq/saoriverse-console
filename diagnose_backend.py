#!/usr/bin/env python3
"""
Diagnostic script to test backend endpoints and identify hanging issues.

Tests:
1. Health check
2. /chat endpoint with timing
3. Supabase conversation loading
4. Pipeline performance profiling
"""

import json
import time
import requests
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_USER_ID = "robinson1234"

def log(msg, level="INFO"):
    """Print timestamped log message."""
    timestamp = datetime.now().isoformat(timespec='milliseconds')
    print(f"[{timestamp}] {level:8} {msg}", flush=True)

def test_health():
    """Test /health endpoint."""
    log("Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        log(f"✓ Health check passed: {response.status_code}")
        return True
    except requests.exceptions.Timeout:
        log("✗ Health check TIMEOUT", "ERROR")
        return False
    except Exception as e:
        log(f"✗ Health check failed: {e}", "ERROR")
        return False

def test_chat():
    """Test /chat endpoint with detailed timing."""
    log("Testing /chat endpoint...")
    
    payload = {
        "message": "I'm feeling exhausted today, like I'm carrying something heavy",
        "userId": TEST_USER_ID,
        "context": {
            "conversation_id": "test-conv-1",
            "is_first_message": True,
            "messages": []
        }
    }
    
    try:
        log(f"Sending chat request: {payload['message'][:50]}...")
        start_time = time.perf_counter()
        
        # Use longer timeout to diagnose hanging
        response = requests.post(
            f"{BASE_URL}/chat",
            json=payload,
            timeout=30,  # 30 second timeout
            stream=False
        )
        
        elapsed = time.perf_counter() - start_time
        
        if response.status_code == 200:
            data = response.json()
            log(f"✓ Chat response received in {elapsed:.2f}s")
            log(f"  Message: {data.get('message', '')[:100]}...")
            return True, elapsed
        else:
            log(f"✗ Chat endpoint returned {response.status_code}: {response.text[:100]}", "ERROR")
            return False, elapsed
            
    except requests.exceptions.Timeout:
        log(f"✗ Chat endpoint TIMEOUT after 30s", "ERROR")
        return False, 30.0
    except Exception as e:
        log(f"✗ Chat request failed: {e}", "ERROR")
        return False, 0.0

def test_conversations():
    """Test /conversations endpoint."""
    log(f"Testing /conversations endpoint for user {TEST_USER_ID}...")
    
    try:
        start_time = time.perf_counter()
        response = requests.get(
            f"{BASE_URL}/conversations/{TEST_USER_ID}",
            timeout=10
        )
        elapsed = time.perf_counter() - start_time
        
        if response.status_code == 200:
            data = response.json()
            conv_count = len(data.get('conversations', []))
            log(f"✓ Loaded {conv_count} conversations in {elapsed:.2f}s")
            if conv_count > 0:
                log(f"  First conversation: {data['conversations'][0]}")
            return True, conv_count
        else:
            log(f"✗ Conversations endpoint returned {response.status_code}", "ERROR")
            return False, 0
            
    except requests.exceptions.Timeout:
        log(f"✗ Conversations endpoint TIMEOUT", "ERROR")
        return False, 0
    except Exception as e:
        log(f"✗ Conversations request failed: {e}", "ERROR")
        return False, 0

def main():
    """Run all diagnostic tests."""
    log("=" * 60)
    log("Backend Diagnostic Test Suite")
    log("=" * 60)
    
    results = {
        "health": False,
        "chat": (False, 0.0),
        "conversations": (False, 0)
    }
    
    # Test 1: Health
    log("\n[TEST 1] Health Check")
    log("-" * 40)
    results["health"] = test_health()
    
    if not results["health"]:
        log("\n✗ Backend is not responding. Make sure it's running:", "ERROR")
        log("  python firstperson_backend.py", "ERROR")
        return False
    
    # Test 2: Chat
    log("\n[TEST 2] Chat Endpoint")
    log("-" * 40)
    time.sleep(1)  # Wait between tests
    results["chat"] = test_chat()
    
    if not results["chat"][0]:
        log("\n✗ Chat endpoint failed or timed out", "ERROR")
        log("  This indicates the pipeline or Supabase is hanging", "ERROR")
    elif results["chat"][1] > 5:
        log("\n⚠ Chat response was SLOW (>5s)", "WARN")
        log("  Pipeline or Supabase needs optimization", "WARN")
    
    # Test 3: Conversations (only if chat worked)
    if results["chat"][0]:
        log("\n[TEST 3] Conversations Loading")
        log("-" * 40)
        time.sleep(1)
        results["conversations"] = test_conversations()
        
        if results["conversations"][1] == 0:
            log(f"\n⚠ No conversations found for {TEST_USER_ID}", "WARN")
            log("  This is the issue reported - conversations not loading", "WARN")
    
    # Summary
    log("\n" + "=" * 60)
    log("Test Summary")
    log("=" * 60)
    log(f"Health:        {'✓ PASS' if results['health'] else '✗ FAIL'}")
    log(f"Chat:          {'✓ PASS' if results['chat'][0] else '✗ FAIL'} ({results['chat'][1]:.2f}s)")
    log(f"Conversations: {'✓ PASS' if results['conversations'][0] else '✗ FAIL'} ({results['conversations'][1]} found)")
    
    # Recommendations
    log("\nRecommendations:")
    if not results["health"]:
        log("  1. Start the backend: python firstperson_backend.py")
    if not results["chat"][0]:
        log("  2. Check backend logs for errors during /chat processing")
        log("  3. Check if Tier1/Tier2/Tier3 are timing out")
        log("  4. Check if Supabase save is blocking")
    if results["conversations"][1] == 0:
        log("  3. Verify robinson1234 conversations exist in Supabase")
        log("  4. Check /conversations endpoint SQL query and filtering")
    
    return all([results["health"], results["chat"][0], results["conversations"][0]])

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

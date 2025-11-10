#!/usr/bin/env python3
"""
URGENT: Quick deployment validation script
Run immediately after deploying optimized edge function
"""

import time

import requests

from emotional_os.deploy.config import SUPABASE_ANON_KEY, SUPABASE_URL


def test_optimized_deployment():
    url = f"{SUPABASE_URL}/functions/v1/saori-fixed"
    headers = {
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }

    # Test messages in order of expected speed
    tests = [
        ("I'm feeling overwhelmed", "Should be <1s with quick response"),
        ("Joy is bubbling up", "Should be <1s with quick response"),
        ("Complex existential thoughts about meaning", "Should be <3s with optimization")
    ]

    print("TESTING OPTIMIZED EDGE FUNCTION")
    print("=" * 50)

    for message, expectation in tests:
        print(f"\nTesting: {message}")
        print(f"Expected: {expectation}")

        start = time.time()
        try:
            response = requests.post(url, headers=headers, json={
                "message": message,
                "mode": "hybrid"
            }, timeout=30)

            elapsed = time.time() - start

            if response.status_code == 200:
                if elapsed < 2.0:
                    status = "SUCCESS"
                elif elapsed < 5.0:
                    status = "IMPROVED"
                else:
                    status = "STILL SLOW"

                print(f"RESULT: {status} - {elapsed:.2f}s")

                # Show response preview
                data = response.json()
                reply = data.get("reply", "")[:100]
                print(f"Response: {reply}...")

            else:
                print(f"ERROR: {response.status_code}")

        except Exception as e:
            elapsed = time.time() - start
            print(f"FAILED: {elapsed:.2f}s - {e}")

        time.sleep(1)  # Brief pause between tests

    print("\n" + "=" * 50)
    print("If you see SUCCESS/IMPROVED results, the optimization worked!")
    print("If still slow, check edge function deployment or try again in 1-2 minutes")

if __name__ == "__main__":
    test_optimized_deployment()

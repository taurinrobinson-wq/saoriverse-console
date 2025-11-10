#!/usr/bin/env python3
"""
Quick deployment verification - run after re-deploying optimized code
"""
import time

import requests

from emotional_os.deploy.config import SUPABASE_ANON_KEY, SUPABASE_URL


def quick_test():
    url = f"{SUPABASE_URL}/functions/v1/saori-fixed"
    headers = {
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }

    print("TESTING RE-DEPLOYMENT...")
    start = time.time()

    try:
        response = requests.post(url, headers=headers, json={
            "message": "grief",
            "mode": "quick"
        }, timeout=15)

        elapsed = time.time() - start

        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "")

            print(f"Time: {elapsed:.2f}s")
            print(f"Reply: {reply}")

            # Success indicators
            if elapsed < 2.0:
                print("SUCCESS: Fast response!")
            if "timeline" in reply.lower() or len(reply) < 200:
                print("SUCCESS: Optimized response style!")
            if "sacred" in reply.lower() or len(reply) > 400:
                print("FAILED: Still old mythic style")

        else:
            print(f"ERROR: {response.status_code}")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    quick_test()

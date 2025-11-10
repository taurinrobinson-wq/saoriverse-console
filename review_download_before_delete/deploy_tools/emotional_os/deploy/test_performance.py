#!/usr/bin/env python3
"""
Performance Test Script for Optimized Edge Function
Tests response times and validates caching behavior
"""

import statistics
import time

import requests

from emotional_os.deploy.config import SUPABASE_ANON_KEY, SUPABASE_URL


class PerformanceTester:
    def __init__(self):
        self.url = f"{SUPABASE_URL}/functions/v1/saori-fixed"
        self.headers = {
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json"
        }
        self.results = []

    def test_message(self, message, expected_speed="normal"):
        """Test a single message and measure response time"""
        print(f"\n🧪 Testing: {message[:60]}...")

        start_time = time.time()
        try:
            response = requests.post(self.url, headers=self.headers, json={
                "message": message,
                "mode": "hybrid"
            }, timeout=30)

            response_time = time.time() - start_time
            success = response.status_code == 200

            if success:
                data = response.json()
                reply_preview = data.get("reply", "")[:100] + "..." if len(data.get("reply", "")) > 100 else data.get("reply", "")

                print(f"✅ {response_time:.2f}s | {reply_preview}")

                # Check for cache/quick response indicators
                source = "unknown"
                if response_time < 0.5:
                    source = "likely_cached"
                elif response_time < 1.0:
                    source = "quick_response"
                elif response_time < 2.0:
                    source = "optimized"
                else:
                    source = "full_processing"

            else:
                print(f"❌ {response_time:.2f}s | Error: {response.status_code}")
                reply_preview = f"HTTP {response.status_code}"
                source = "error"

            self.results.append({
                "message": message,
                "response_time": response_time,
                "success": success,
                "expected_speed": expected_speed,
                "actual_source": source,
                "reply_preview": reply_preview
            })

            return response_time, success

        except Exception as e:
            response_time = time.time() - start_time
            print(f"💥 {response_time:.2f}s | Exception: {str(e)}")

            self.results.append({
                "message": message,
                "response_time": response_time,
                "success": False,
                "expected_speed": expected_speed,
                "actual_source": "error",
                "reply_preview": str(e)
            })

            return response_time, False

    def run_comprehensive_test(self):
        """Run a comprehensive performance test suite"""
        print("🚀 Starting Performance Test Suite")
        print("=" * 60)

        # Test cases organized by expected performance
        test_cases = [
            # Quick responses (should be <1s with optimization)
            ("I'm feeling overwhelmed by everything", "quick"),
            ("Joy is bubbling up inside me today", "quick"),
            ("I'm struggling with grief from my loss", "quick"),
            ("Anxiety is taking over my thoughts", "quick"),
            ("I'm so confused about everything", "quick"),

            # Pattern matches (should be 1-2s)
            ("Love feels complicated right now", "medium"),
            ("Celebrating this amazing moment", "medium"),
            ("Processing some difficult emotions", "medium"),

            # Complex processing (should be <3s with optimization)
            ("I'm experiencing a complex mix of existential dread and hopeful anticipation about the uncertain future while simultaneously grappling with philosophical questions about the nature of consciousness and meaning", "complex"),
            ("Tell me about the intricate relationship between temporal awareness and emotional processing in the context of grief work", "complex"),

            # Cache test (repeat a message)
            ("I'm feeling overwhelmed by everything", "cached"),  # Repeat first message
        ]

        for message, expected_speed in test_cases:
            self.test_message(message, expected_speed)
            time.sleep(1)  # Brief pause between requests

        self.analyze_results()

    def analyze_results(self):
        """Analyze and report test results"""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE ANALYSIS")
        print("=" * 60)

        successful_tests = [r for r in self.results if r["success"]]
        failed_tests = [r for r in self.results if not r["success"]]

        if not successful_tests:
            print("❌ All tests failed!")
            return

        # Response time statistics
        times = [r["response_time"] for r in successful_tests]

        print("\n🎯 Response Time Summary:")
        print(f"   Total Tests: {len(self.results)}")
        print(f"   Successful: {len(successful_tests)}")
        print(f"   Failed: {len(failed_tests)}")
        print(f"   Success Rate: {len(successful_tests)/len(self.results)*100:.1f}%")

        print("\n⚡ Speed Metrics:")
        print(f"   Average: {statistics.mean(times):.2f}s")
        print(f"   Median: {statistics.median(times):.2f}s")
        print(f"   Min: {min(times):.2f}s")
        print(f"   Max: {max(times):.2f}s")

        # Performance categories
        fast_responses = len([t for t in times if t < 1.0])
        medium_responses = len([t for t in times if 1.0 <= t < 2.0])
        slow_responses = len([t for t in times if t >= 2.0])

        print("\n📈 Performance Distribution:")
        print(f"   Fast (<1s): {fast_responses} ({fast_responses/len(times)*100:.1f}%)")
        print(f"   Medium (1-2s): {medium_responses} ({medium_responses/len(times)*100:.1f}%)")
        print(f"   Slow (2s+): {slow_responses} ({slow_responses/len(times)*100:.1f}%)")

        # Optimization assessment
        print("\n🎯 Optimization Assessment:")
        baseline_time = 9.48  # Original baseline
        avg_improvement = baseline_time - statistics.mean(times)
        improvement_percent = (avg_improvement / baseline_time) * 100

        print(f"   Baseline (original): {baseline_time}s")
        print(f"   Current average: {statistics.mean(times):.2f}s")
        print(f"   Improvement: {avg_improvement:.2f}s ({improvement_percent:.1f}% faster)")

        if statistics.mean(times) < 2.0:
            print("   ✅ Target achieved! (<2s average)")
        else:
            print("   ⚠️  Target not yet achieved (>2s average)")

        # Detailed results
        print("\n📋 Detailed Results:")
        for i, result in enumerate(self.results, 1):
            status = "✅" if result["success"] else "❌"
            message_preview = result["message"][:50] + "..." if len(result["message"]) > 50 else result["message"]
            print(f"   {i:2d}. {status} {result['response_time']:5.2f}s | {result['actual_source']:12} | {message_preview}")

    def test_cache_behavior(self):
        """Test caching behavior specifically"""
        print("\n🔄 Testing Cache Behavior")
        print("-" * 40)

        test_message = "I'm feeling overwhelmed by everything"

        # First request (should populate cache)
        time1, success1 = self.test_message(test_message, "initial")
        time.sleep(1)

        # Second request (should hit cache)
        time2, success2 = self.test_message(test_message, "cached")

        if success1 and success2:
            speedup = time1 - time2
            if time2 < time1 * 0.8:  # At least 20% faster
                print(f"✅ Cache working! Speedup: {speedup:.2f}s ({speedup/time1*100:.1f}% faster)")
            else:
                print(f"⚠️  Cache may not be working. Difference: {speedup:.2f}s")
        else:
            print("❌ Cache test failed due to errors")

def main():
    """Main test execution"""
    tester = PerformanceTester()

    print("🧪 Emotional OS Performance Test Suite")
    print("Testing optimized edge function performance...")
    print(f"Target URL: {tester.url}")
    print()

    try:
        # Run comprehensive test
        tester.run_comprehensive_test()

        # Test caching specifically
        tester.test_cache_behavior()

        print("\n🏁 Testing Complete!")
        print("\nNext steps:")
        print("1. Review results above")
        print("2. If performance is good, deploy client-side optimizations")
        print("3. If performance is poor, check edge function deployment")

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Test suite failed: {e}")

if __name__ == "__main__":
    main()

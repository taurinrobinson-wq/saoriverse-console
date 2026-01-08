"""
train_emotion_model.py

Privacy-first emotion learning system.
Analyzes emotion metadata logs from Supabase and updates per-user thresholds.
This enables the frontend detector to become smarter and more efficient over time.

Usage:
  python train_emotion_model.py [--user_id USER_ID] [--days DAYS]

Environment Variables:
  SUPABASE_URL: Supabase project URL
  SUPABASE_SERVICE_ROLE_KEY: Supabase service role key (keep private)
"""

import os
import sys
import datetime
import argparse
from typing import Optional, Dict, List, Tuple
from collections import defaultdict

import numpy as np


def get_supabase_client():
    """Initialize Supabase client using environment variables."""
    try:
        from supabase import create_client, Client
    except ImportError:
        print("Error: supabase-py not installed. Install with: pip install supabase")
        sys.exit(1)

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables required")
        sys.exit(1)

    return create_client(url, key)


def fetch_emotion_logs(
    supabase, user_id: str, days: int = 30
) -> List[Dict]:
    """
    Fetch emotion logs for a user over the last N days.
    
    Returns:
        List of emotion log entries from Supabase
    """
    since = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)).isoformat()

    try:
        response = (
            supabase.table("emotions_log")
            .select("*")
            .gte("timestamp", since)
            .eq("user_id", user_id)
            .execute()
        )
        return response.data if response.data else []
    except Exception as e:
        print(f"Error fetching emotion logs: {e}")
        return []


def analyze_emotion_patterns(logs: List[Dict]) -> Tuple[Dict, Dict, int]:
    """
    Analyze emotion frequency and confidence patterns.
    
    Args:
        logs: List of emotion log entries
        
    Returns:
        Tuple of (emotion_counts, avg_confidence, total_detections)
    """
    emotion_counts = defaultdict(int)
    confidence_scores: Dict[str, List[float]] = defaultdict(list)
    total_detections = len(logs)

    for entry in logs:
        emotion = entry.get("emotion", "unknown")
        confidence = float(entry.get("confidence", 0))

        emotion_counts[emotion] += 1
        confidence_scores[emotion].append(confidence)

    # Calculate average confidence per emotion
    avg_confidence = {}
    for emotion, scores in confidence_scores.items():
        avg_confidence[emotion] = float(np.mean(scores))

    return dict(emotion_counts), avg_confidence, total_detections


def calculate_adaptive_thresholds(
    avg_confidence: Dict[str, float], min_threshold: float = 0.4
) -> Dict[str, float]:
    """
    Calculate adaptive thresholds based on user-specific emotion patterns.
    
    Lower thresholds for emotions the user exhibits frequently (higher confidence).
    Keep higher thresholds for rare emotions to avoid false positives.
    
    Args:
        avg_confidence: Average confidence per emotion
        min_threshold: Minimum threshold floor (0.4 = 40% confidence)
        
    Returns:
        Dict mapping emotion to adaptive threshold
    """
    thresholds = {}
    
    for emotion, avg_conf in avg_confidence.items():
        # If user shows this emotion with high confidence, lower the threshold
        # Formula: threshold = avg_confidence * 0.9 (keep 90% of observed confidence)
        # But floor at min_threshold to avoid false positives
        threshold = max(min_threshold, avg_conf * 0.9)
        threshold = min(threshold, 0.95)  # Cap at 95%
        thresholds[emotion] = round(threshold, 2)

    return thresholds


def update_thresholds_in_database(
    supabase, user_id: str, thresholds: Dict[str, float]
) -> bool:
    """
    Update emotion thresholds in Supabase emotion_thresholds table.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        for emotion, threshold in thresholds.items():
            supabase.table("emotion_thresholds").upsert(
                {
                    "user_id": user_id,
                    "emotion": emotion,
                    "threshold": threshold,
                    "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                },
                onConflict="user_id,emotion",
            ).execute()

        return True
    except Exception as e:
        print(f"Error updating thresholds in database: {e}")
        return False


def train_user_model(
    supabase, user_id: str, days: int = 30, verbose: bool = True
) -> bool:
    """
    Main training loop for a single user.
    
    Fetches emotion logs, analyzes patterns, calculates adaptive thresholds,
    and updates them in Supabase.
    
    Returns:
        True if training succeeded, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"Training emotion model for user: {user_id}")
    print(f"Period: last {days} days")
    print(f"{'='*60}\n")

    # Fetch logs
    logs = fetch_emotion_logs(supabase, user_id, days=days)

    if not logs:
        print(f"⚠️  No emotion logs found for {user_id} in the last {days} days")
        return False

    print(f"✓ Fetched {len(logs)} emotion log entries")

    # Analyze patterns
    counts, avg_conf, total = analyze_emotion_patterns(logs)

    if verbose:
        print(f"\nEmotion Frequency:")
        for emotion, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            print(f"  {emotion:12} {count:4} detections ({percentage:5.1f}%)")

        print(f"\nAverage Confidence:")
        for emotion, conf in sorted(avg_conf.items(), key=lambda x: x[1], reverse=True):
            print(f"  {emotion:12} {conf:.3f}")

    # Calculate adaptive thresholds
    thresholds = calculate_adaptive_thresholds(avg_conf)

    if verbose:
        print(f"\nAdaptive Thresholds (per-user):")
        for emotion, threshold in sorted(thresholds.items(), key=lambda x: x[1], reverse=True):
            print(f"  {emotion:12} {threshold:.2f} (confidence floor)")

    # Update database
    success = update_thresholds_in_database(supabase, user_id, thresholds)

    if success:
        print(f"\n✓ Updated {len(thresholds)} emotion thresholds in database")
        print(f"✓ Training complete for {user_id}\n")
    else:
        print(f"\n✗ Failed to update thresholds in database\n")

    return success


def train_all_users(supabase, days: int = 30) -> int:
    """
    Train models for all users with recent emotion logs.
    
    Returns:
        Number of users trained
    """
    try:
        # Get distinct users from emotions_log
        response = (
            supabase.table("emotions_log")
            .select("user_id")
            .order("user_id")
            .execute()
        )

        if not response.data:
            print("No emotion logs found")
            return 0

        # Get unique users
        user_ids = list(set(entry.get("user_id") for entry in response.data))

        print(f"\nFound {len(user_ids)} users with emotion logs\n")

        trained = 0
        for user_id in user_ids:
            if train_user_model(supabase, user_id, days=days, verbose=False):
                trained += 1

        return trained

    except Exception as e:
        print(f"Error training all users: {e}")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Train emotion detection models using Supabase logs"
    )
    parser.add_argument(
        "--user_id",
        type=str,
        default=None,
        help="Train specific user (if not provided, trains all users)",
    )
    parser.add_argument(
        "--days", type=int, default=30, help="Number of days to analyze (default: 30)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Train all users (equivalent to --user_id=all)",
    )

    args = parser.parse_args()

    supabase = get_supabase_client()

    if args.user_id:
        # Train specific user
        success = train_user_model(supabase, args.user_id, days=args.days)
        sys.exit(0 if success else 1)

    elif args.all:
        # Train all users
        trained = train_all_users(supabase, days=args.days)
        print(f"\nTrained {trained} user(s)")
        sys.exit(0)

    else:
        # No arguments - show help
        parser.print_help()
        print(
            "\nExample usage:"
            "\n  python train_emotion_model.py --user_id user_123"
            "\n  python train_emotion_model.py --all --days 30"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()

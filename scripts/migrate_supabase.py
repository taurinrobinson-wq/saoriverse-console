#!/usr/bin/env python3
"""
Supabase Database Migration Script

Applies the conversations table schema to Supabase.
This sets up persistent conversation storage.
"""

import json
import sys
from pathlib import Path

import requests


def run_sql_migration(supabase_url: str, service_key: str, sql_file: str) -> bool:
    """Execute SQL migration against Supabase using the admin API."""

    # Read SQL file
    sql_path = Path(sql_file)
    if not sql_path.exists():
        print(f"❌ SQL file not found: {sql_file}")
        return False

    sql_content = sql_path.read_text()
    print(f"📄 Loaded SQL from: {sql_file}")
    print(f"📊 SQL size: {len(sql_content)} bytes")

    # Split SQL into individual statements
    statements = [s.strip() for s in sql_content.split(";") if s.strip()]
    print(f"📋 Found {len(statements)} SQL statements")

    # Execute each statement using the REST API with service role key
    # The REST API doesn't directly execute arbitrary SQL, so we need to use the pg_exec endpoint
    # Alternative: use Supabase Admin API or CLI

    print("\n⚠️  NOTE: Direct SQL execution via REST API requires service role key.")
    print("📌 For safety, you should run this in Supabase SQL Editor:\n")
    print("=" * 70)
    print(sql_content)
    print("=" * 70)

    return True


def verify_tables(supabase_url: str, anon_key: str) -> dict:
    """Verify that conversation tables were created."""

    headers = {
        "Content-Type": "application/json",
        "apikey": anon_key,
        "Authorization": f"Bearer {anon_key}",
    }

    result = {"conversations_exists": False, "conversation_metadata_exists": False, "errors": []}

    # Check conversations table
    try:
        response = requests.get(f"{supabase_url}/rest/v1/conversations?limit=1", headers=headers, timeout=10)
        if response.status_code == 200:
            result["conversations_exists"] = True
            print("✅ conversations table EXISTS")
        elif response.status_code == 404:
            print("❌ conversations table DOES NOT EXIST")
        else:
            result["errors"].append(f"Conversations query returned {response.status_code}")
    except Exception as e:
        result["errors"].append(f"Conversations check failed: {e}")

    # Check conversation_metadata table
    try:
        response = requests.get(f"{supabase_url}/rest/v1/conversation_metadata?limit=1", headers=headers, timeout=10)
        if response.status_code == 200:
            result["conversation_metadata_exists"] = True
            print("✅ conversation_metadata table EXISTS")
        elif response.status_code == 404:
            print("❌ conversation_metadata table DOES NOT EXIST")
        else:
            result["errors"].append(f"Metadata query returned {response.status_code}")
    except Exception as e:
        result["errors"].append(f"Metadata check failed: {e}")

    return result


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    # Try to load from streamlit secrets
    try:
        import streamlit as st

        if hasattr(st, "secrets"):
            supabase_url = st.secrets.get("supabase", {}).get("url")
            service_key = st.secrets.get("supabase", {}).get("service_role_key")
            anon_key = st.secrets.get("supabase", {}).get("key")
    except:
        supabase_url = os.getenv("SUPABASE_URL")
        service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        anon_key = os.getenv("SUPABASE_ANON_KEY")

    # Fallback to hardcoded from secrets.toml
    if not supabase_url:
        supabase_url = "https://gyqzyuvuuyfjxnramkfq.supabase.co"
        service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd5cXp5dXZ1dXlmanhucmFta2ZxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTQ2NzIwMCwiZXhwIjoyMDcxMDQzMjAwfQ.sILcK31ECwM0IUECL0NklBdv4WREIxToqtCdsMYKWqo"
        anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd5cXp5dXZ1dXlmanhucmFta2ZxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU0NjcyMDAsImV4cCI6MjA3MTA0MzIwMH0.4SpC34q7lcURBX4hujkTGqICdSM6ZWASCENnRs5rkS8"

    print("🔧 Supabase Database Migration Script")
    print("=" * 70)
    print(f"🌐 Supabase URL: {supabase_url}")
    print()

    # Show the SQL that needs to be run
    sql_file = "sql/conversations_table.sql"
    print(f"\n📝 Migration file: {sql_file}")
    print("=" * 70)

    run_sql_migration(supabase_url, service_key, sql_file)

    print("\n" + "=" * 70)
    print("\n⚙️  NEXT STEPS:")
    print("1. Copy the SQL above")
    print("2. Go to https://app.supabase.com/project/gyqzyuvuuyfjxnramkfq/sql/new")
    print("3. Paste the SQL into the SQL editor")
    print("4. Click 'Run'")
    print("5. Then run this script again to verify:")
    print(f"   python3 {__file__} --verify")

    # Check if --verify flag is passed
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        print("\n" + "=" * 70)
        print("🔍 Verifying tables...")
        result = verify_tables(supabase_url, anon_key)

        if result["conversations_exists"] and result["conversation_metadata_exists"]:
            print("\n✅ All tables created successfully!")
            sys.exit(0)
        else:
            print("\n❌ Some tables are missing. Run the SQL first.")
            if result["errors"]:
                print("Errors:")
                for error in result["errors"]:
                    print(f"  - {error}")
            sys.exit(1)

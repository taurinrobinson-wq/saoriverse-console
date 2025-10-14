# Quick Manual Deployment Guide

## Deploy Authentication Functions via Supabase Web Interface

### Step 1: Database Setup
1. Go to https://supabase.com/dashboard
2. Open your project: gyqzyuvuuyfjxnramkfq
3. Navigate to **SQL Editor**
4. Click **New Query**
5. Copy and paste the entire content from `database_schema.sql`
6. Click **Run** to execute

### Step 2: Deploy auth-manager Function
1. In Supabase dashboard, go to **Edge Functions**
2. Click **Create Function**
3. Function name: `auth-manager`
4. Copy the entire content from `auth_edge_function.ts`
5. Click **Deploy**

### Step 3: Deploy authenticated-saori Function
1. Click **Create Function** again
2. Function name: `authenticated-saori`  
3. Copy the entire content from `authenticated_edge_function.ts`
4. Click **Deploy**

### Step 4: Test Registration
After both functions are deployed:
1. Refresh your Streamlit app
2. Try creating account with:
   - Username: taurinrobinson
   - Email: taurinrobinson@gmail.com
   - Password: (your choice)

## Quick Test URLs
After deployment, these should work:
- Auth: https://gyqzyuvuuyfjxnramkfq.supabase.co/functions/v1/auth-manager
- Processing: https://gyqzyuvuuyfjxnramkfq.supabase.co/functions/v1/authenticated-saori

## If Still Having Issues
1. Check function logs in Supabase dashboard
2. Verify database schema was applied
3. Confirm both edge functions are deployed and active
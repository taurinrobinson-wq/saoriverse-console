🚀 FirstPerson Railway Deployment Setup

## Step 1: Set Environment Variables in Railway

You need to set these 4 environment variables in Railway with your actual Supabase values:

1. SUPABASE_URL - Your Supabase project URL
2. SUPABASE_KEY - Your Supabase anon key
3. SUPABASE_AUTH_URL - Your auth function URL
4. CURRENT_SAORI_URL - Your Saori AI function URL

## Step 2: Run These Commands

Copy and paste each command, replacing the placeholder values with your actual credentials:

```powershell

# Set your Supabase URL (looks like: https://abcdefgh.supabase.co)
railway variables set SUPABASE_URL="your_actual_supabase_url_here"

# Set your Supabase anon key (long string starting with eyJ...)
railway variables set SUPABASE_KEY="your_actual_supabase_anon_key_here"

# Set your auth function URL (usually: your_supabase_url/functions/v1/auth-manager)
railway variables set SUPABASE_AUTH_URL="your_supabase_url/functions/v1/auth-manager"

# Set your Saori AI function URL (usually: your_supabase_url/functions/v1/saori-fixed)
railway variables set CURRENT_SAORI_URL="your_supabase_url/functions/v1/saori-fixed"
```



## Step 3: Deploy Your Application

After setting the environment variables:

```powershell
railway up
```



## Step 4: Add Your Custom Domain

1. Go to https://railway.com/project/0b1980c1-3144-4369-9b61-778c89a66727
2. Click Settings → Domains
3. Add custom domain: firstperson.chat
4. Update your DNS records as instructed by Railway
##

## Where to Find Your Credentials

Your Supabase credentials are stored in your Streamlit secrets. You can find them:

1. **In your Streamlit Cloud dashboard**: Go to your app settings → Secrets
2. **In local .streamlit/secrets.toml file** (if you have one)
3. **In your Supabase dashboard**:
   - URL: Project Settings → API → Project URL
   - Key: Project Settings → API → Project API keys → anon public

The format in secrets looks like:

```toml
[supabase]
url = "https://yourproject.supabase.co"
key = "eyJ..."
auth_function_url = "https://yourproject.supabase.co/functions/v1/auth-manager"
current_saori_url = "https://yourproject.supabase.co/functions/v1/saori-fixed"
```


##

Ready to set up your environment variables? 🎯

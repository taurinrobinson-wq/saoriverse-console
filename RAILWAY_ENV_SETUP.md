# Railway Environment Variables Guide
# Set these in your Railway project dashboard under "Variables"

# Required Supabase Configuration
SUPABASE_URL=your-supabase-url-here
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
SUPABASE_FUNCTION_URL=https://your-project.supabase.co/functions/v1/saori-fixed

# Optional Configuration
DEFAULT_PROCESSING_MODE=hybrid
PRIVACY_MODE=false
PREFER_AI=true
USE_LOCAL_FALLBACK=true

# If using OpenAI directly (optional)
# OPENAI_API_KEY=your-openai-api-key-here

# Railway will automatically set PORT variable - don't override it
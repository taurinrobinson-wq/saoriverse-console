# SSH Deployment Script for FirstPerson on cPanel
# Use these commands in your SSH terminal

# Server Details:
# Server IP: 162.0.215.74
# Username: firscius
# SSH Port: 21098

# Connect via SSH:
# ssh -p 21098 firscius@162.0.215.74

# Once connected, run these commands:

# 1. Navigate to your repository
cd /home/firscius/firstperson-app

# 2. Pull latest changes
git pull origin main

# 3. Copy files to public directory
cp -r * /home/firscius/public_html/

# 4. Set proper permissions
chmod 755 /home/firscius/public_html/*.py
chmod +x /home/firscius/public_html/startup.sh

# 5. Install Python dependencies
cd /home/firscius/public_html
python3 -m pip install --user fastapi uvicorn jinja2 python-multipart requests gunicorn

# 6. Create environment file
cat > .env << 'EOF'
SUPABASE_URL=https://gyqzyuvuuyfjxnramkfq.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd5cXp5dXZ1dXlmanhucmFta2ZxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU0NjcyMDAsImV4cCI6MjA3MTA0MzIwMH0.4SpC34q7lcURBX4hujkTGqICdSM6ZWASCENnRs5rkS8
SUPABASE_FUNCTION_URL=https://gyqzyuvuuyfjxnramkfq.supabase.co/functions/v1/saori-fixed
SECRET_KEY=firstperson-secret-key-2025
DEBUG=False
EOF

# 7. Test the application
python3 -c "import fastapi_app; print('✅ FastAPI app imported successfully')"

# 8. Create a simple index.php to redirect to Python app (if needed)
cat > index.php << 'EOF'
<?php
// Redirect to Python FastAPI application
header("Location: /cgi-bin/fastapi_wrapper.py");
exit();
?>
EOF
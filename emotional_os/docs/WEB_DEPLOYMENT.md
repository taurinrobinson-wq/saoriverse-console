# FirstPerson.chat Deployment Guide

## 🌐 Moving from Streamlit to firstperson.chat

Congratulations on securing the firstperson.chat domain! Here's how to deploy your FirstPerson AI Companion to your own professional domain.

## 📁 Files Created

Your new web application includes:
- `fastapi_app.py` - Main FastAPI backend server
- `templates/index.html` - Landing page with authentication
- `templates/chat.html` - Main chat application
- `static/graphics/` - Your FirstPerson logo and assets
- `web_requirements.txt` - Python dependencies

## 🚀 Deployment Options

### Option 1: Railway (Recommended - Easy & Free)

1. **Sign up at Railway.app**
   - Connect your GitHub account
   - Free tier includes 512MB RAM, $5/month credit

2. **Deploy Steps:**
   ```bash
   # Create new GitHub repo for web app
   git init
   git add .
   git commit -m "Initial FirstPerson web app"
   git remote add origin https://github.com/yourusername/firstperson-web
   git push -u origin main
   ```

3. **Railway Configuration:**
   - Create new project from GitHub repo
   - Set environment variables:
     - `SUPABASE_URL` = your Supabase URL
     - `SUPABASE_KEY` = your Supabase anon key
     - `SECRET_KEY` = generate with `python -c "import secrets; print(secrets.token_hex(32))"`
   - Railway will auto-deploy FastAPI app

4. **Custom Domain:**
   - In Railway dashboard: Settings → Domains
   - Add custom domain: firstperson.chat
   - Update DNS: CNAME record pointing to Railway domain

### Option 2: Vercel (Next.js Alternative)

If you prefer a more modern stack:

1. **Convert to Next.js:**
   ```bash
   npx create-next-app@latest firstperson-chat
   cd firstperson-chat
   ```

2. **Deploy:**
   - Push to GitHub
   - Connect Vercel to repo
   - Add environment variables
   - Set custom domain in Vercel dashboard

### Option 3: DigitalOcean App Platform

1. **Create Droplet:**
   - $5/month basic droplet
   - Ubuntu 22.04

2. **Setup:**
   ```bash
   # Install dependencies
   sudo apt update
   sudo apt install python3-pip nginx certbot python3-certbot-nginx
   
   # Clone your repo
   git clone https://github.com/yourusername/firstperson-web
   cd firstperson-web
   
   # Install Python packages
   pip3 install -r web_requirements.txt
   
   # Create .env file with your credentials
   cp env_template.txt .env
   # Edit .env with your actual values
   
   # Run with systemd service
   sudo nano /etc/systemd/system/firstperson.service
   ```

3. **Nginx Configuration:**
   ```nginx
   server {
       listen 80;
       server_name firstperson.chat;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **SSL Certificate:**
   ```bash
   sudo certbot --nginx -d firstperson.chat
   ```

## 🛠️ Local Development

Test your web app locally before deploying:

```bash
# Install dependencies
pip install -r web_requirements.txt

# Create .env file
cp env_template.txt .env
# Edit .env with your Supabase credentials

# Run development server
python fastapi_app.py
```

Visit http://localhost:8000 to test your app.

## 📊 Benefits of Custom Domain

✅ **Professional branding** - firstperson.chat looks much more credible
✅ **Better SEO** - Google prefers custom domains
✅ **No platform limitations** - Full control over features
✅ **SSL certificate** - Secure HTTPS connection
✅ **Email integration** - Can set up support@firstperson.chat
✅ **Scalability** - Can handle more users than Streamlit

## 🔧 Environment Variables

Make sure to set these in your deployment platform:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here
SECRET_KEY=generated_32_character_hex_string
```

## 📈 Next Steps

1. **Deploy to your chosen platform**
2. **Configure firstperson.chat DNS**
3. **Test authentication and chat functionality**
4. **Add Google Analytics for user tracking**
5. **Set up monitoring and error tracking**
6. **Create admin panel at admin.firstperson.chat**

## 🎯 Recommended: Railway Deployment

For the fastest setup, I recommend Railway:
- One-click deployment from GitHub
- Automatic HTTPS
- Easy custom domain setup
- Great for small to medium traffic
- Built-in database options if needed

Would you like me to help you deploy to Railway or another platform?
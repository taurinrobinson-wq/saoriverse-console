# FirstPerson Deployment to firstperson.chat

## Quick Deploy with Railway (Recommended)

### 1. Install Railway CLI

```powershell
npm install -g @railway/cli
```


### 2. Login to Railway

```powershell
railway login
```


### 3. Initialize Project

```powershell
cd "C:\Users\Admin\OneDrive\Desktop\Emotional OS"
railway init

# Project name: firstperson-chat
```


### 4. Set Environment Variables

```powershell
railway variables set SUPABASE_URL="your_supabase_url"
railway variables set SUPABASE_KEY="your_supabase_key"
railway variables set SUPABASE_AUTH_URL="your_auth_function_url"
railway variables set CURRENT_SAORI_URL="your_saori_url"
```


### 5. Deploy

```powershell
railway up
```


### 6. Add Custom Domain

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click your project → Settings → Domains
3. Add custom domain: `firstperson.chat`
4. Update DNS at your domain registrar:
   - **Type**: CNAME
   - **Name**: @ (root domain) or www
   - **Value**: [Railway will provide this]

##

## Alternative: Deploy with Vercel

### 1. Install Vercel CLI

```powershell
npm install -g vercel
```


### 2. Deploy

```powershell
vercel --prod
```


### 3. Add Domain

```powershell
vercel domains add firstperson.chat
```


##

## What's Been Prepared

✅ **FastAPI Application**: Complete web server ready for production
✅ **Professional Templates**: Clean, responsive HTML/CSS interface
✅ **Railway Config**: Optimized for easy deployment
✅ **Requirements**: All Python dependencies specified
✅ **Health Checks**: Built-in monitoring endpoints
✅ **Static Assets**: FirstPerson logo and graphics ready

## Files Created for Deployment

- `fastapi_app.py` - Main web server
- `requirements.txt` - Python dependencies
- `railway.json` - Railway configuration
- `Procfile` - Process definition
- `templates/` - HTML templates
- `static/graphics/` - Assets and logos

## Environment Variables Needed

Your Supabase configuration from `main_v2.py`:

- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SUPABASE_AUTH_URL` (auth function endpoint)
- `CURRENT_SAORI_URL` (AI processing endpoint)

## Next Steps

1. Choose Railway or Vercel for hosting
2. Set up your environment variables
3. Deploy the application
4. Configure firstperson.chat DNS
5. Your professional AI companion will be live! 🚀

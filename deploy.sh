#!/bin/bash
# FirstPerson Deployment Script

echo "🚀 FirstPerson Deployment to firstperson.chat"
echo "=============================================="

echo "📦 Step 1: Install Railway CLI"
echo "Run: npm install -g @railway/cli"
echo ""

echo "🔐 Step 2: Login to Railway"  
echo "Run: railway login"
echo ""

echo "📁 Step 3: Initialize Railway Project"
echo "Run: railway init"
echo "Project name: firstperson-chat"
echo ""

echo "⚙️ Step 4: Set Environment Variables"
echo "railway variables set SUPABASE_URL=your_supabase_url"
echo "railway variables set SUPABASE_KEY=your_supabase_key"
echo "railway variables set SUPABASE_AUTH_URL=your_auth_function_url"
echo "railway variables set CURRENT_SAORI_URL=your_saori_url"
echo ""

echo "🌐 Step 5: Deploy Application"
echo "Run: railway up"
echo ""

echo "🔗 Step 6: Add Custom Domain"
echo "1. Go to Railway dashboard"
echo "2. Click on your project -> Settings -> Domains"  
echo "3. Add custom domain: firstperson.chat"
echo "4. Update DNS at your domain registrar:"
echo "   - Type: CNAME"
echo "   - Name: @ (or www)"
echo "   - Value: [provided by Railway]"
echo ""

echo "✅ Your FirstPerson app will be live at https://firstperson.chat"
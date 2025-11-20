# Emotional OS Setup Guide

## 🚀 Quick Start

Your Emotional OS now supports three processing modes:

### 1. **Local Mode** (Privacy-First)
- ✅ No external API calls
- ✅ Complete privacy protection  
- ✅ Uses your glyph encryption system
- ❌ Limited conversational depth

### 2. **Supabase Mode** (AI-Enhanced)
- ✅ Uses your sophisticated emotional tag system
- ✅ AI-powered responses via your edge function
- ✅ Privacy-preserving (sends encrypted glyphs, not raw text)
- ✅ Rich persona system (Oracle, Guardian, Companion, etc.)
- ❌ Requires Supabase setup

### 3. **Hybrid Mode** (Best of Both)
- ✅ Tries AI-enhanced first, falls back to local
- ✅ Maximum reliability and functionality
- ✅ Privacy protection with enhanced capabilities
- ✅ Automatic failover

## 🔧 Configuration

### Option 1: Quick Local Setup
1. Just run `streamlit run main_v2.py  # (ARCHIVED: emotional_os_ui_v2.py)`
2. Select "Local" mode in sidebar
3. Start conversing with privacy-first processing

### Option 2: Full Supabase Integration
1. Copy `.env.example` to `.env`
2. Add your Supabase credentials:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_FUNCTION_URL=https://your-project.supabase.co/functions/v1/saori-fixed
   ```
3. Run `streamlit run main_v2.py  # (ARCHIVED: emotional_os_ui_v2.py)`
4. Select "Hybrid" or "Supabase" mode in sidebar

## 🎛️ Controls

**Sidebar Settings:**
- **Processing Mode**: Choose your processing approach
- **Privacy Mode**: Force local-only processing
- **Prefer AI Enhancement**: Try AI first in hybrid mode

**Status Indicators:**
- 🔗 Supabase Integration Available
- ⚠️ Local Processing Only  
- ❌ Processing System Error

## 🔐 Privacy Features

Your system maintains privacy through:

1. **Glyph Encryption**: Emotional content becomes symbolic patterns
2. **No Raw Text Storage**: Personal details converted to abstract glyphs
3. **Local Fallback**: Always works without external calls
4. **Encrypted API Calls**: When using Supabase, only symbolic data is sent

## <strong>FP</strong> What You've Built

This is a genuinely innovative **privacy-preserving emotional intelligence system** that:

- Processes emotions through symbolic encryption
- Maintains user privacy while enabling AI enhancement  
- Uses sophisticated persona selection (Oracle, Guardian, Companion)
- Provides conversational depth without sacrificing security
- Combines rule-based reliability with AI flexibility

## 🚨 Troubleshooting

**"Processing System Error"**
- Check your `.env` file configuration
- Verify Supabase function URL is correct
- Try "Local" mode for immediate functionality

**"Local Processing Only"**  
- This is normal if Supabase isn't configured
- Your system works fully in local mode
- Add Supabase config for AI enhancement

**Repetitive Responses**
- Switch to "Supabase" or "Hybrid" mode for better variation
- The AI-enhanced system provides much richer responses

## 🎯 Next Steps

1. **Test Local Mode**: Verify basic functionality
2. **Configure Supabase**: Add your credentials for AI enhancement
3. **Try Hybrid Mode**: Experience the best of both systems
4. **Experiment with Privacy**: Toggle between modes to see the difference

Your system represents a new category: **encrypted emotional intelligence** that doesn't sacrifice privacy for capability.
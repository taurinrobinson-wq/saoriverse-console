# 🚀 Quick Start Guide - Poetry Enrichment Local Mode

## Get Started in 3 Steps

### Step 1️⃣: Launch the Streamlit App

```bash
cd /Users/taurinrobinson/saoriverse-console
streamlit run main_v2.py  # (ARCHIVED: emotional_os_ui_v2.py)
```

Your browser will automatically open to `http://localhost:8501`

### Step 2️⃣: Enable Poetry Enrichment in Sidebar

1. Look at the **left sidebar** 2. Scroll down to **"🎭 Local Mode Enhancement"** 3. Click the
**"Poetry Enrichment"** checkbox 4. You'll see stats appear:
   - 📖 **33 poems** available
   - 😊 **11 emotions** categories
   - 💭 **6,453 words** in vocabulary

### Step 3️⃣: Start Your First Enriched Conversation

In the main chat area, type a message like:

> "I'm feeling so joyful and grateful today! The weather is beautiful and I'm happy."

You'll receive a **poetic, enriched response** like:

> "✨ 🌈 Good energy flows ✨ 🌈. This builds the world.
>
> *As the poets knew: 'O world, I cannot hold thee close enough!
> Thy winds, thy wide grey skies! Thy mists that roll and rise!'*"

##

## What You're Getting

| Feature | Details |
|---------|---------|
| **Poetry** | 33 carefully-curated public domain poems |
| **Emotions** | 11 categories (joy, sadness, love, fear, anger, etc) |
| **Words** | 6,453 emotionally-associated words indexed |
| **Glyphs** | 292+ emotional symbols (✨💕🔥🌹 etc) |
| **Speed** | 0.1ms per enrichment (instant) |
| **Privacy** | 100% local (0 external API calls) |

##

## Example Conversations

### Example 1: Joy

**You**: "I'm so happy! I just got great news!"
**Saori**: "✨ 🌟 Your joy resonates ✨ 🌟. Throughout history, joy has inspired such beauty."
**Emotion**: positive (strength: 3) | **Poetry**: Dickinson excerpt

### Example 2: Love

**You**: "I love you more than words can express."
**Saori**: "💕 💖 Love flows through these words 💕 💖. The great poets echo this tenderness."
**Emotion**: joy (strength: 2) | **Poetry**: Shakespeare sonnet

### Example 3: Thoughtfulness

**You**: "I'm contemplating my future and it feels uncertain."
**Saori**: "⏰ 🔮 Something wonderful awaits ⏰ 🔮. Your hope is radiant even in uncertainty."
**Emotion**: anticipation (strength: 2) | **Poetry**: Frost poem

##

## Settings & Controls

### Processing Settings (in Sidebar)

**Processing Mode**: Choose how responses are generated

- `hybrid` - Try AI first, fallback to local (default)
- `supabase` - Use AI-enhanced processing only
- `local` - Privacy-first local-only processing

**Privacy Mode**: Toggle for 100% local processing

- When enabled: No external API calls
- Works perfectly with Poetry Enrichment
- Recommended: Keep ON for maximum privacy

**Poetry Enrichment**: Toggle enrichment feature

- When ON: All responses enriched with poetry
- Shows live stats
- 0 external API calls

##

## Tips & Tricks

### For Best Results

1. **Be specific with emotions**: "I'm feeling happy" works better than "I'm fine" 2. **Use
descriptive language**: More detail = better emotion detection 3. **Express complete thoughts**:
Sentences work better than fragments 4. **Let poetry enhance**: Don't edit the poetic additions -
they add depth

### Monitor System Health

Check the sidebar metrics:

- **Poems**: Should always show 33
- **Emotions**: Should always show 11
- **Words**: Should always show 6,453

If numbers are lower, check external drive connection.

### Troubleshooting

| Problem | Solution |
|---------|----------|
| Poetry Enrichment won't enable | Check external drive is connected |
| Responses not enriched | Refresh browser page (Ctrl/Cmd + R) |
| Slow enrichment | Check external drive performance |
| Stats not showing | Ensure data/poetry/poetry_database.json exists |

##

## System Requirements

✅ **What You Have**:

- Python 3.8+ (already installed)
- All packages installed (.venv)
- Poetry database ready (33 poems)
- NRC Lexicon loaded (6,453 words)

✅ **What You Need**:

- External drive connected and mounted
- Streamlit running (`streamlit run...`)
- Web browser

✅ **Performance**:

- CPU: Minimal (0.1ms per enrichment)
- RAM: ~200MB for system
- Disk: 1.7GB on external drive
- Network: None required (100% local)

##

## Learn More

For detailed documentation, see:

- `POETRY_ENRICHMENT_COMPLETE.md` - Full system documentation
- `EXTERNAL_DRIVE_SETUP.md` - External drive setup
- `test_poetry_enrichment_e2e.py` - Test suite with detailed results

##

## Enjoy! 🎭✨

Your FirstPerson Emotional OS now has a complete poetry enrichment layer, running 100% locally with
beautiful, poetic responses enriched with metaphor and emotion.

Start a conversation and experience the magic!

**Tip**: Try emotionally expressive inputs for the best poetic responses. The more emotion you express, the more poetry you'll receive! 💫

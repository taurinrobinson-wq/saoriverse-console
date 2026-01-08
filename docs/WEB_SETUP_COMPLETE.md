# ✅ Velinor Web Development - Setup Complete

## What Was Done

I've set up your Next.js web version to run **directly on your Mac without Docker**. No container
management needed!

### Installation Summary

- ✅ Installed Node.js 20.11.0 via nvm (Node Version Manager)
- ✅ Installed npm dependencies (368 packages)
- ✅ Verified Next.js dev server works
- ✅ Created startup scripts for easy launching

##

## 🚀 How to Start Developing

### Option 1: Frontend Only (Quickest)

```bash
cd /Volumes/My\ Passport\ for\ Mac/saoriverse-console
```text

```text
```


Then visit: **<http://localhost:3000>**

### Option 2: Full Stack (Frontend + Backend)

```bash

cd /Volumes/My\ Passport\ for\ Mac/saoriverse-console

```text

```

This starts:

- Frontend: **<http://localhost:3000>**
- Backend API: **<http://localhost:8000>**
- API Docs: **<http://localhost:8000/docs>**

##

## 📁 What You Have

### Frontend (Next.js)

- Located in: `/velinor-web/`
- Framework: Next.js 16 with React 19 + TypeScript
- Styling: Tailwind CSS v4
- State Management: Zustand (installed)
- HTTP Client: Axios (installed)
- Dev Server Port: 3000

### Backend (FastAPI)

- Located in: `velinor_api.py` (root)
- Status: Ready to wire up to frontend
- Endpoints: Session management, actions, save/load
- API Port: 8000
- Docs available at `/docs`

### Game Assets

All graphics have been replicated to `/velinor-web/public/assets/`:

- **Backgrounds**: 15+ images (1200×675, 16:9 format)
- **NPC Portraits**: 7 character images
- **UI Assets**: Velinor title images

##

## 🎮 Current Web Version State

### What's Working

- ✅ Homepage with "Start New Game" button
- ✅ Input form for player name
- ✅ Navigation routing ready
- ✅ All assets available
- ✅ TypeScript configuration
- ✅ Hot module reloading (auto-refresh on save)

### What Needs Development

⏳ **Game Scene Component** - Display story text, choices, NPC dialogue
⏳ **Backend Connection** - Wire frontend to FastAPI endpoints
⏳ **Choice System** - Process player choices and send to backend
⏳ **NPC Display** - Show portraits and responses
⏳ **Game State** - Display stats, location, inventory
⏳ **Glyph System** - Visual representation of emotional glyphs

##

## 💡 Development Tips

### File Structure

```

velinor-web/
├── src/
│   ├── app/              # Next.js pages/routes
│   │   ├── page.tsx      # Homepage (you're here)
│   │   ├── game/[sessionId]/page.tsx  # Game page (needs work)
│   │   └── layout.tsx
│   ├── components/       # Reusable React components
│   │   └── GameScene.tsx # Main game component (empty, ready for you)
│   └── styles/
├── public/assets/        # All game graphics

```text
```text

```

### Hot Reload

Save a file → Browser auto-refreshes. No manual reload needed!

### Common Commands

```bash


cd velinor-web

# Start dev (port 3000)
npm run dev

# Build for production
npm run build

# Check TypeScript errors
npm run lint

# Run production server

```text
```


##

## 🔌 Connecting Frontend to Backend

The FastAPI backend is ready with these endpoints:

```python
POST   /sessions                    # Create new game
GET    /sessions/{id}               # Get game state
POST   /sessions/{id}/actions       # Process player action
POST   /sessions/{id}/save          # Save game
```sql

```sql
```


Example call from Next.js:

```typescript

import axios from 'axios';

const startGame = async (playerName: string) => {
  const response = await axios.post('http://localhost:8000/sessions', {
    player_name: playerName,
    player_backstory: 'Wanderer seeking truth'
  });
  return response.data; // { session_id, initial_state, ... }

```text

```

##

## 📚 Reference Files

For understanding the game logic:

- **Orchestrator** (core game logic): `/velinor/engine/orchestrator.py`
- **Story structure**: `/velinor/stories/sample_story.json`
- **Streamlit reference** (what web version should replicate): `/velinor_app.py`
- **FastAPI backend** (endpoints to call): `/velinor_api.py`

##

## ⚡ Next Immediate Steps

1. **Run the dev server**: `./RUN_WEB_DEV.sh`
2. **View the homepage** at <http://localhost:3000>
3. **Examine the code** in `velinor-web/src/`
4. **Implement GameScene.tsx** with:
   - Story text display
   - Background image
   - NPC portrait
   - Choice buttons
   - Free text input
5. **Wire to backend** by calling FastAPI endpoints

##

## 🆘 Troubleshooting

### Node version error?

```bash

export NVM_DIR="$HOME/.nvm" source "$NVM_DIR/nvm.sh"

```text
```text

```

### Port 3000 in use?

```bash



# Kill it
lsof -i :3000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Or use different port

```bash
```


### Can't find node/npm?

Make sure the startup script sources nvm properly. Run manually:

```bash
bash -c 'export NVM_DIR="$HOME/.nvm" && source "$NVM_DIR/nvm.sh" && nvm use 20.11.0 && cd velinor-web && npm run dev'
```


##

## 📖 Read More

For detailed development guide, see: **VELINOR_WEB_DEV_GUIDE.md**

##

## ✨ You're Ready

Your Next.js web game is running and ready for development. The whole stack (frontend + backend) is
available for iteration without needing Docker. Start the servers and begin building! 🚀

Questions? Check the game logic files and the comprehensive dev guide.

Happy coding! 🎮

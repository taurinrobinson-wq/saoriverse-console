# Velinor Web Game - Local Development Setup

## ✅ Setup Complete!

Your Next.js web version of Velinor is now ready for local development on your Mac **without Docker**.

### 🚀 Quick Start

The easiest way to start developing:

```bash

# Navigate to your project
cd "/Volumes/My Passport for Mac/saoriverse-console"

# Run the dev server
./RUN_WEB_DEV.sh
```



Or manually:

```bash
cd velinor-web
npm run dev
```



The dev server will start at **http://localhost:3000**
##

## 🛠️ What Was Installed

- **Node.js 20.11.0** - JavaScript runtime (installed via nvm)
- **npm 10.2.4** - Package manager
- **Next.js 16.0.8** - React framework with Turbopack
- **368 npm packages** - All dependencies for the web game
##

## 📁 Project Structure

```
velinor-web/
├── src/
│   ├── app/
│   │   ├── page.tsx          # Homepage (currently static)
│   │   ├── game/
│   │   │   └── [sessionId]/
│   │   │       └── page.tsx  # Game session page (needs implementation)
│   │   └── layout.tsx
│   ├── components/
│   │   └── GameScene.tsx     # Game rendering component (needs implementation)
│   └── hooks/               # Custom React hooks (add here)
├── public/
│   └── assets/
│       ├── backgrounds/     # All 15+ game backgrounds (replicated from Streamlit)
│       ├── npcs/           # All 7 NPC character portraits
│       └── ui/             # UI assets
├── styles/
│   └── globals.css         # Global Tailwind CSS
├── package.json
├── next.config.ts
├── tsconfig.json
└── tailwind.config.ts
```


##

## 🎮 Current State

### What's Ready
✅ Next.js project structure
✅ TypeScript configuration
✅ Tailwind CSS for styling
✅ All graphics assets (backgrounds, NPCs)
✅ Zustand for state management (installed)
✅ Axios for API calls (installed)

### What Needs Development
⏳ Connect to FastAPI backend (`velinor_api.py`)
⏳ Wire game logic from Python orchestrator to React components
⏳ Implement GameScene component with choice UI
⏳ Build game session management
⏳ Integrate FirstPerson emotional analysis
⏳ Create NPC dialogue UI
⏳ Build save/load functionality
##

## 📝 Development Tips

### Hot Reload
The dev server automatically reloads when you save files—just edit and refresh!

### File Locations
- **React components**: `/src/components/`
- **Page routes**: `/src/app/`
- **Game assets**: `/public/assets/`
- **Styling**: `/src/styles/` and inline with Tailwind

### Common Commands

```bash

# Start dev server (3000)
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```



### Tailwind CSS
Styling uses Tailwind CSS v4. Add classes directly to JSX elements:

```tsx
<div className="bg-slate-900 text-white p-8 rounded-lg">
  <h1 className="text-3xl font-bold">Game Title</h1>
</div>
```


##

## 🔌 Connecting to the Python Backend

The FastAPI backend is in `velinor_api.py` (295 lines). To use it:

1. **Start the FastAPI server in a separate terminal:**
   ```bash
   cd /Volumes/My\ Passport\ for\ Mac/saoriverse-console
   python velinor_api.py
   ```
   It will run on `http://localhost:8000`

2. **In Next.js, use axios to call it:**
   ```typescript
   import axios from 'axios';

   const response = await axios.post('http://localhost:8000/sessions', {
     player_name: 'Saori',
     player_backstory: 'A wanderer...'
   });
   ```

3. **Available endpoints:**
   - `POST /sessions` - Create new game session
   - `GET /sessions/{session_id}` - Get session state
   - `POST /sessions/{session_id}/actions` - Process player action
   - `POST /sessions/{session_id}/save` - Save game
   - `GET /sessions/{session_id}/load` - Load game
##

## 🎨 Design References

### Color Scheme (from Streamlit version)
- Primary: `#ff6b9d` (pink)
- Background: `#ffffff` (white)
- Text: `#333333` (dark gray)
- Success: `#2ecc71` (green)
- Failure: `#e74c3c` (red)

### Image Sizes
- Backgrounds: 1200×675 (16:9 landscape)
- NPC portraits: Variable (use `object-cover`)
- Container max-width: 1200px
##

## 🐛 Troubleshooting

### "Node version not found"

```bash

# Make sure nvm is loaded
export NVM_DIR="$HOME/.nvm"
source "$NVM_DIR/nvm.sh"
nvm use 20.11.0
```



### Port 3000 already in use

```bash

# Kill the existing process
lsof -i :3000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Or use a different port
PORT=3001 npm run dev
```



### TypeScript errors
- Check `/src/components/` for component exports
- Ensure all imports use `.tsx` for components
- Run `npm run lint` to see all issues
##

## 📚 Next Steps for Development

### Priority 1: Basic Game Flow (1-2 hours)
1. Implement `GameScene.tsx` to display the story text
2. Create choice button UI
3. Wire up choice clicks to backend

### Priority 2: NPC System (1-2 hours)
1. Display NPC portraits and backgrounds
2. Show dialogue text from orchestrator
3. Add emotion-aware response styling

### Priority 3: Game State (1 hour)
1. Implement session creation flow
2. Add player stats display
3. Show location/context information

### Priority 4: Glyph System (1-2 hours)
1. Create glyph collection UI
2. Show emotional analysis from FirstPerson
3. Build glyph visualization
##

## 💡 Code Examples

### Display a background image

```tsx
<img
  src="/assets/backgrounds/city_market(16-9).png"
  alt="Market Ruins"
  className="w-full h-96 object-cover rounded-lg"
/>
```



### Show NPC portrait

```tsx
<img
  src="/assets/npcs/keeper.png"
  alt="Keeper"
  className="h-96 object-contain"
/>
```



### Create choice buttons

```tsx
{choices.map((choice) => (
  <button
    key={choice.id}
    onClick={() => handleChoice(choice)}
    className="w-full bg-pink-500 hover:bg-pink-600 text-white p-4 rounded mb-2"
  >
    {choice.text}
  </button>
))}
```



### Call the backend

```typescript
const makeAction = async (input: string) => {
  try {
    const response = await axios.post(
      `http://localhost:8000/sessions/${sessionId}/actions`,
      { player_input: input },
      { headers: { 'Content-Type': 'application/json' } }
    );
    console.log('Game response:', response.data);
  } catch (error) {
    console.error('Error:', error);
  }
};
```


##

## 📞 Need Help?

Check these files for reference:
- **Python game logic**: `/Volumes/My Passport for Mac/saoriverse-console/velinor/engine/orchestrator.py`
- **Story structure**: `/Volumes/My Passport for Mac/saoriverse-console/velinor/stories/sample_story.json`
- **Streamlit UI reference**: `/Volumes/My Passport for Mac/saoriverse-console/velinor_app.py`
- **FastAPI endpoints**: `/Volumes/My Passport for Mac/saoriverse-console/velinor_api.py`
##

## 🎯 You're all set!

Start the dev server with `./RUN_WEB_DEV.sh` and begin developing the web version. You can iterate quickly without Docker, and all game logic from the Streamlit version is available via the FastAPI backend.

Happy coding! 🚀

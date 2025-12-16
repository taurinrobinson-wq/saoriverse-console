# Velinor Web Stack - Quick Reference

## What You Now Have

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | FastAPI + Python | Game engine API, state management |
| Frontend | Next.js + React/TypeScript | UI with full overlay control |
| Deployment | Railway | Automatic CI/CD |
| Game Engine | Velinor (Twine/Python) | Narrative logic, dice rolls, NPC dialogue |
##

## Local Development Commands

```bash

# Start Backend (Terminal 1)
cd /path/to/saoriverse-console
python velinor_api.py

# → http://localhost:8000 (Swagger docs at /docs)

# Start Frontend (Terminal 2)
cd velinor-web
npm run dev

```text
```text
```


##

## Files Created

| File | Purpose |
|------|---------|
| `velinor_api.py` | FastAPI backend - wraps Velinor engine |
| `frontend_lib_api.ts` | API client for Next.js |
| `frontend_GameScene.tsx` | Main scene renderer with overlays |
| `NEXTJS_FRONTEND_SETUP.md` | Detailed Next.js setup guide |
| `RAILWAY_DEPLOYMENT.md` | Railway deployment instructions |
| `VELINOR_WEB_MIGRATION.md` | Complete step-by-step migration guide |
##

## Setup Checklist

### One-Time Setup
- [ ] Run `npx create-next-app@latest velinor-web --typescript --tailwind --eslint --no-git`
- [ ] Copy `frontend_lib_api.ts` → `velinor-web/lib/api.ts`
- [ ] Copy `frontend_GameScene.tsx` → `velinor-web/components/GameScene.tsx`
- [ ] Create page files (splash + game scene)
- [ ] Copy game assets to `velinor-web/public/assets/`
- [ ] Test locally

### Deployment
- [ ] `git add .` && `git commit -m "..."` && `git push origin main`
- [ ] Railway auto-deploys (~3-5 minutes)
- [ ] Visit your Railway domain
##

## Game Flow

```

┌─────────────────┐
│  Splash Screen  │  (Enter player name)
└────────┬────────┘
         │ "Start New Game"
         ▼
┌─────────────────┐
│  Game Scene #1  │  (Market entrance)
│  - Background   │
│  - Narration    │
│  - Choices      │
└────────┬────────┘
         │ (player chooses)
         ▼
┌─────────────────┐
│  Game Scene #2  │  (NPC encounter)
│  + Overlay      │
│  + Glyph        │
└────────┬────────┘
         │ ...continues

```text
```



##

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/game/start` | Create new session & get initial state |
| POST | `/api/game/{id}/action` | Process player choice or input |
| GET | `/api/game/{id}` | Get current game state |
| POST | `/api/game/{id}/save` | Save progress |
| POST | `/api/game/{id}/load` | Load saved game |
| DELETE | `/api/game/{id}` | End session |
##

## Environment Variables

### Development (`.env.local`)

```
```text
```text
```



### Production (Railway Dashboard)

```

NEXT_PUBLIC_API_URL=https://<your-railway-domain>.up.railway.app

```


##

## Styling

All components use inline styles for portability. To customize:

**Colors:**
- Primary: `#3a6df0` (blue)
- Success: `#4aa96c` (green)
- Dark bg: `#191b1e`

**Positioning:**
- Use `position: absolute` for overlays
- Use `position: relative` for containers
- Use flexbox for layouts
##

## Troubleshooting

**API returns 404**
→ Check `NEXT_PUBLIC_API_URL` matches Railway domain

**Images not loading**
→ Ensure assets are in `velinor-web/public/assets/`

**Frontend can't connect to backend**
→ Backend might be slow to start. Check Railway logs.

**CORS errors**
→ Already handled in `velinor_api.py`. For production, restrict to your domain.
##

## Key Advantages Over Streamlit

✅ Full Z-index control for overlays
✅ Smooth animations & transitions
✅ Mobile responsive
✅ Better performance
✅ Easy to customize styling
✅ Full React ecosystem available
##

## Resources

- [Next.js Docs](https://nextjs.org/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Railway Docs](https://docs.railway.app/)
- [Velinor Engine](./velinor/TWINE_INTEGRATION_GUIDE.md)
##

**Ready to deploy?**

Follow the 6 phases in `VELINOR_WEB_MIGRATION.md`

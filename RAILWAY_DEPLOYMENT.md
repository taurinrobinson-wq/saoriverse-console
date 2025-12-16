# Railway Deployment - FastAPI Backend + Next.js Frontend

## Architecture

- **Backend**: FastAPI (Python) on Railway at `/api`
- **Frontend**: Next.js (Node.js) on Railway at `/`
- **Communication**: Frontend calls backend API

## Prerequisites

- Railway account (already set up)
- GitHub repo with changes pushed
- Node.js 18+ and Python 3.12+

## Step 1: Install Backend Dependencies

```bash
pip install fastapi uvicorn pydantic
```



Update `requirements.txt`:

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
```



## Step 2: Update Procfile for Dual Services

Update your `Procfile` to run both backend and frontend:

```procfile

# Backend API
api: cd . && python -m uvicorn velinor_api:app --host 0.0.0.0 --port 8000

# Frontend (after Next.js is set up)
web: cd velinor-web && npm run start
```



## Step 3: Set Up Next.js Frontend

```bash
npx create-next-app@latest velinor-web --typescript --tailwind --eslint
cd velinor-web
npm install axios zustand
```



Copy the frontend files:
- `lib/api.ts` → `velinor-web/lib/api.ts`
- `components/GameScene.tsx` → `velinor-web/components/GameScene.tsx`
- Update `app/page.tsx` with splash screen and game scene logic

## Step 4: Environment Variables (Railway)

In Railway dashboard, set:

```
NEXT_PUBLIC_API_URL=https://<your-railway-domain>.up.railway.app/api
```



## Step 5: Deploy to Railway

```bash

# Add Procfile changes
git add Procfile requirements.txt

# Add frontend
git add velinor-web/

# Commit and push
git commit -m "feat: Add FastAPI backend and Next.js frontend for Velinor"
git push origin main

# Railway auto-deploys (~3-5 minutes)

# Visit: https://<your-railway-domain>.up.railway.app
```



## Step 6: Test

1. Open https://<your-railway-domain>.up.railway.app
2. Enter player name
3. Click "Start New Game"
4. Verify API calls succeed (check browser Network tab)

## Troubleshooting

### API calls return 404

Make sure `NEXT_PUBLIC_API_URL` matches your Railway domain exactly.

### Frontend can't find images

Ensure images are in `velinor-web/public/assets/`:

```
velinor-web/public/assets/
├── backgrounds/
├── overlays/
└── npcs/
```



### Slow startup

Railway might be cold-starting both services. Give it 1-2 minutes first.

### CORS errors

Already enabled in `velinor_api.py`:

```python
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```



For production, restrict to your domain.

## Local Development

Terminal 1 - Backend:

```bash
python velinor_api.py

# http://localhost:8000

# Swagger docs: http://localhost:8000/docs
```



Terminal 2 - Frontend:

```bash
cd velinor-web
npm run dev

# http://localhost:3000
```



## File Structure

```
saoriverse-console/
├── velinor/                    # Game engine
│   ├── engine/
│   ├── stories/
│   └── assets/
├── velinor_api.py              # FastAPI backend
├── velinor_app.py              # Old Streamlit (keep or delete)
├── Procfile                    # Railway config (updated)
├── requirements.txt            # Python deps
└── velinor-web/                # Next.js frontend
    ├── app/
    ├── components/
    ├── lib/
    ├── public/
    │   └── assets/             # Copy game assets here
    ├── package.json
    └── tsconfig.json
```



## Next Steps

1. Create `velinor-web/app/page.tsx` with splash screen
2. Create `velinor-web/app/game/[sessionId]/page.tsx` for gameplay
3. Add background images to `velinor-web/public/assets/backgrounds/`
4. Add overlay images to `velinor-web/public/assets/overlays/`
5. Test locally, then push to Railway
##

**Your Railway domain** will be auto-generated. Once set, bookmark it!

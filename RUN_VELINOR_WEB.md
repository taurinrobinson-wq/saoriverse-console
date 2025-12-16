# Running Velinor Web Stack Locally

This is the quickest way to run the full Velinor game with the web stack (FastAPI backend + Next.js frontend).

## Prerequisites

- Python 3.12+
- Node.js 18+
- FastAPI and dependencies installed in Python
- Next.js dependencies installed

## Terminal 1: Start Backend (FastAPI)

```bash
cd d:\saoriverse-console
```text
```text
```



Expected output:

```

```text
```




The API will be available at:
- Health check: `http://localhost:8000/`
- API docs: `http://localhost:8000/docs`

## Terminal 2: Start Frontend (Next.js)

```bash
cd d:\saoriverse-console\velinor-web
```text
```text
```



Expected output:

```

> velinor-web@0.1.0 dev
> next dev

  ▲ Next.js 14.x.x

```text
```




## Open in Browser

Navigate to `http://localhost:3000`

You should see:
1. Splash screen with "Velinor" title and "Start New Game" button
2. Enter a player name (or use default)
3. Click "Start New Game"
4. The game scene loads with background, narration, and interactive choices

## Troubleshooting

**"Failed to start game. Is the API running on http://localhost:8000?"**
- Make sure Terminal 1 is running `python velinor_api.py`
- Check that `velinor_api.py` starts without errors

**"Cannot find module '@/lib/api'"**
- Verify `velinor-web/lib/api.ts` exists
- Verify `velinor-web/components/GameScene.tsx` exists
- Run `npm install` if needed

**Game shows "Loading game... (Did you start a game first?)"**
- This is normal on the game page before state loads
- Check browser console for errors
- Verify API is responding at `http://localhost:8000/docs`

**Linting warnings about inline styles**
- These are informational only, not breaking
- Code will still run and render correctly
- Can be fixed later by moving styles to CSS file

## Environment Configuration

The frontend looks for the API at the URL in `.env.local`:

```
```text
```text
```



For production deployment, change this to your Railway domain.

## Next: Deploy to Railway

Once working locally:

```bash

git add .
git commit -m "Velinor web stack complete"
git push origin main

```



Railway auto-deploys on push.

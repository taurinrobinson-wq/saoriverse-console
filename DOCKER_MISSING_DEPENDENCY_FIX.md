# Docker Build Fix - Missing Supabase Dependency

## Problem
```
Module not found: Can't resolve '@supabase/supabase-js'
```

## Root Cause
The new API route files import from `@supabase/supabase-js`, but the package wasn't listed in `firstperson-web/package.json`.

## Solution Applied ✅

### 1. Updated `firstperson-web/package.json`
Added missing dependencies:
```json
{
  "dependencies": {
    // ... existing dependencies
    "@supabase/supabase-js": "^2.38.0",
    "face-api.js": "^0.22.2"
  }
}
```

### 2. Updated Dockerfiles
Changed from `npm ci` (uses package-lock.json) to `npm install` (installs all dependencies):
```dockerfile
COPY firstperson-web/package*.json ./
RUN npm install --legacy-peer-deps
```

Updated files:
- ✅ `Dockerfile.firstperson`
- ✅ `Dockerfile.firstperson.resilient`

## Why This Happened
- Created new API routes that depend on Supabase
- Forgot to add the dependency to package.json
- `npm ci` uses locked versions from package-lock.json
- `npm install` reads package.json and installs everything

## Try Building Now

### Windows PowerShell:
```powershell
cd d:\saoriverse-console
docker build -f Dockerfile.firstperson -t firstperson:latest .
```

### macOS/Linux:
```bash
cd d/saoriverse-console
docker build -f Dockerfile.firstperson -t firstperson:latest .
```

## Expected Output
Build should now complete successfully with:
```
✅ Successfully tagged firstperson:latest
```

## If Still Failing

**Option 1: Clean build**
```bash
docker system prune -a
docker build -f Dockerfile.firstperson -t firstperson:latest --no-cache .
```

**Option 2: Use resilient build**
```bash
docker build -f Dockerfile.firstperson.resilient -t firstperson:latest .
```

**Option 3: Manually install deps first (local testing)**
```bash
cd firstperson-web
npm install
cd ..
docker build -f Dockerfile.firstperson -t firstperson:latest .
```

## Verify Success

Once build completes:
```bash
# Test the image
docker run --rm firstperson:latest node -e "require('@supabase/supabase-js'); console.log('✅ Supabase loaded')"

# Run container
docker run -p 8000:8000 -p 3001:3001 firstperson:latest
```

## Files Modified
- ✅ `firstperson-web/package.json` — Added @supabase/supabase-js and face-api.js
- ✅ `Dockerfile.firstperson` — Changed npm ci to npm install
- ✅ `Dockerfile.firstperson.resilient` — Changed npm ci to npm install

---

**Status:** Ready to rebuild 🚀

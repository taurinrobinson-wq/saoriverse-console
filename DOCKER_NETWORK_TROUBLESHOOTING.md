# Docker Network Issues - Troubleshooting Guide

## Problem: Network Error During pip Install

```
WARNING: Attempting to resume incomplete download (10.4 MB/16.6 MB)
ERROR: Download failed after 6 attempts because not enough bytes were received
```

## Root Cause
The Docker container is experiencing network connectivity issues while downloading Python packages (numpy) from PyPI.

---

## Solution 1: Updated Dockerfile (Recommended)

The Dockerfile has been updated with network resilience:

```dockerfile
ENV PIP_RETRIES=5 \
    PIP_TIMEOUT=120 \
    PIP_DEFAULT_TIMEOUT=120

RUN pip install --no-cache-dir \
                --default-timeout=120 \
                --retries 5 \
                -r requirements-backend.txt
```

**What this does:**
- Increases timeout from default 15s to 120s
- Increases retry attempts to 5
- Disables pip cache (force fresh downloads)
- Uses stable numpy version (2.1.2)

---

## Solution 2: Build with Network Options

### Option A: Use Resilient Dockerfile
```bash
# Windows PowerShell
docker build -f Dockerfile.firstperson.resilient -t firstperson:latest .

# macOS/Linux
docker build -f Dockerfile.firstperson.resilient -t firstperson:latest .
```

### Option B: Override pip arguments during build
```bash
# Windows
docker build `
  -f Dockerfile.firstperson `
  -t firstperson:latest `
  --build-arg PIP_TIMEOUT=180 `
  --build-arg PIP_RETRIES=10 `
  .

# macOS/Linux
docker build \
  -f Dockerfile.firstperson \
  -t firstperson:latest \
  --build-arg PIP_TIMEOUT=180 \
  --build-arg PIP_RETRIES=10 \
  .
```

### Option C: Rebuild without cache
```bash
# Windows
docker build -f Dockerfile.firstperson -t firstperson:latest --no-cache .

# macOS/Linux
docker build -f Dockerfile.firstperson -t firstperson:latest --no-cache .
```

---

## Solution 3: Check Docker Network Configuration

### Verify Docker has network access
```bash
# Windows PowerShell
docker run --rm alpine ping -c 4 8.8.8.8

# macOS/Linux
docker run --rm alpine ping -c 4 8.8.8.8
```

**Expected output:**
```
PING 8.8.8.8 (8.8.8.8): 56 data bytes
64 bytes from 8.8.8.8: seq=0 ttl=119 time=15.384 ms
...
```

If ping fails, Docker doesn't have network access.

---

## Solution 4: If Network is Unstable

### Pre-download packages on host machine
```bash
# Create requirements file with specific versions
pip download -r requirements-backend.txt -d ./wheels/

# Then modify Dockerfile to use local wheels
COPY wheels/ /tmp/wheels/
RUN pip install --no-index --find-links=/tmp/wheels/ -r requirements-backend.txt
```

### Or use a local PyPI mirror
```dockerfile
RUN pip install -i https://pypi.org/simple/ \
    --default-timeout=120 \
    --retries 5 \
    -r requirements-backend.txt
```

---

## Solution 5: Simplify Dependencies

If network is still problematic, reduce dependencies:

**Current requirements-backend.txt:**
```
fastapi==0.104.1
uvicorn==0.24.0
supabase==2.6.0
requests==2.32.3
openai-whisper>=20230314      # Heavy dependency
elevenlabs>=0.2.10
soundfile>=0.12.0
librosa>=0.10.0               # Pulls numpy, scipy, etc.
numpy==2.1.2
pytest==9.0.2
```

**Minimal production version:**
```
# Core
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.12.5

# Database
supabase==2.6.0
requests==2.32.3

# Audio (optional, can be added later)
# openai-whisper>=20230314
# elevenlabs>=0.2.10

# Development only
pytest==9.0.2
```

---

## Testing After Build

Once Docker builds successfully, test it:

```bash
# Test 1: Image exists
docker images | grep firstperson

# Test 2: Run basic Python check
docker run --rm firstperson:latest python -c "import fastapi; print('✅ FastAPI working')"

# Test 3: Check if backend starts
docker run --rm -p 8000:8000 firstperson:latest &
sleep 10
curl http://localhost:8000/health

# Test 4: Full container run
docker run -p 8000:8000 -p 3001:3001 firstperson:latest
```

---

## Environment-Specific Troubleshooting

### If using Docker Desktop on Windows

1. **Ensure Docker Desktop is running**
   - Check taskbar icon (whale icon)
   - Or run: `docker ps` to verify

2. **Check WSL2 configuration**
   - Docker Desktop → Settings → Resources → WSL Integration
   - Enable "Ubuntu" or your WSL distro

3. **Reset Docker network**
   ```powershell
   docker system prune -a
   # Then rebuild
   ```

4. **Check DNS resolution**
   ```powershell
   docker run --rm alpine nslookup files.pythonhosted.org
   ```

### If using Docker on Linux

```bash
# Check network
docker network ls
docker network inspect bridge

# If no network, restart Docker daemon
sudo systemctl restart docker
```

### If using Docker on Mac

```bash
# Reset Docker
# Click Docker menu → Troubleshoot → Reset Docker Desktop
# Or:
docker system prune -a
docker restart
```

---

## Recommended Fix (What We Did)

1. ✅ Updated `requirements-backend.txt` with stable `numpy==2.1.2`
2. ✅ Updated `Dockerfile.firstperson` with:
   - `--default-timeout=60` (increased from 15s)
   - `--retries 5` (increased from 1)
   - `PIP_DEFAULT_TIMEOUT=60` environment variable
3. ✅ Created `Dockerfile.firstperson.resilient` with even more robust settings
4. ✅ Created test scripts (`test-docker-build.sh`, `test-docker-build.ps1`)

---

## Next Steps

### Try Building Now

**Windows (PowerShell):**
```powershell
cd d:\saoriverse-console
.\test-docker-build.ps1
```

**macOS/Linux:**
```bash
cd d/saoriverse-console
bash test-docker-build.sh
```

### If Still Having Issues

Try the resilient version:
```bash
docker build -f Dockerfile.firstperson.resilient -t firstperson:latest .
```

### If Network Remains Unstable

1. Check your ISP/router stability
2. Try building on a different network (mobile hotspot, cafe WiFi)
3. Pre-download packages: `pip download -r requirements-backend.txt -d ./wheels/`
4. Simplify requirements to essentials only
5. Contact Docker support (cloud/networking issue)

---

## Key Config Parameters

| Parameter | Current Value | Max Safe Value | Notes |
|-----------|---------------|-----------------|-------|
| PIP_TIMEOUT | 60s | 300s | Timeout per package |
| PIP_RETRIES | 5 | 10 | Retry attempts |
| PIP_NO_CACHE | true | true | Force fresh downloads |
| Numpy version | 2.1.2 | 2.3.5 | Avoid newer unstable |

---

## Summary

**What was fixed:**
- ✅ Updated numpy to stable version (2.1.2)
- ✅ Added pip retry configuration (5 retries, 60s timeout)
- ✅ Created resilient Dockerfile variant
- ✅ Added test scripts for validation

**What to try next:**
1. Run `test-docker-build.ps1` (Windows) or `test-docker-build.sh` (Linux)
2. If it fails, try `Dockerfile.firstperson.resilient`
3. If still failing, check Docker network connectivity

**Expected result:**
- Image builds successfully in 5-10 minutes
- Can run container: `docker run -p 8000:8000 firstperson:latest`
- Can test health: `curl http://localhost:8000/health`

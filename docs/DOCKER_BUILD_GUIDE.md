# Docker Build Guide - FirstPerson System

## 🚀 Quick Start

### Step 1: Pre-Flight Check

```powershell

# Windows PowerShell
python check-docker-requirements.py

# macOS/Linux
```text
```text
```



Expected output: All checks ✅

### Step 2: Build Docker Image

**Option A: Standard Build** (Recommended - uses updated robust config)

```powershell


# Windows PowerShell
docker build -f Dockerfile.firstperson -t firstperson:latest .

# macOS/Linux

```text
```




**Option B: Resilient Build** (If Option A times out)

```powershell

# Windows PowerShell
docker build -f Dockerfile.firstperson.resilient -t firstperson:latest .

# macOS/Linux
```text
```text
```



**Option C: Automated Test** (Validates build)

```powershell


# Windows PowerShell
.\test-docker-build.ps1

# macOS/Linux

```text
```




### Step 3: Verify Build Success

```bash

# Check image was created
docker images | grep firstperson

# Test FastAPI import
docker run --rm firstperson:latest python -c "import fastapi; print('✅ OK')"

# Test health endpoint
docker run -d -p 8000:8000 --name firstperson-test firstperson:latest
sleep 5
curl http://localhost:8000/health
docker stop firstperson-test
```text
```text
```



Expected: `{"status":"healthy"}`
##

## 📊 Build Information

| Component | Version | Status |
|-----------|---------|--------|
| Python | 3.12-slim | ✅ |
| FastAPI | 0.104.1 | ✅ |
| Numpy | 2.1.2 | ✅ Stable |
| OpenAI-Whisper | Latest | ✅ |
| ElevenLabs | Latest | ✅ |
| Node | 20-alpine | ✅ Frontend |
| Nginx | Latest | ✅ Reverse proxy |
##

## ⚙️ Build Configuration

### Timeouts & Retries

```

PIP_TIMEOUT: 60 seconds (was 15s)
PIP_RETRIES: 5 attempts (was 1)

```text
```




### Optimization

```
--no-cache-dir: Saves disk space
--retries 5: Handles network hiccups
```text
```text
```


##

## 🐛 Troubleshooting

### Error: "Name or service not known"
**Cause:** Docker cannot reach PyPI
**Fix:**
1. Check network: `docker run --rm alpine ping 8.8.8.8`
2. Use resilient build: `docker build -f Dockerfile.firstperson.resilient -t firstperson:latest .`
3. Increase timeout: `docker build ... --build-arg PIP_TIMEOUT=180 .`

### Error: "Connection broken"
**Cause:** Network interrupted during download
**Fix:** Automatic retry is enabled (will retry 5 times)
- If still failing, try building on different network
- Or pre-download packages locally

### Error: "Dockerfile not found"
**Cause:** Wrong working directory or filename
**Fix:**

```bash


# Verify you're in correct directory
pwd  # or cd d:\saoriverse-console

# Verify Dockerfile exists
ls Dockerfile.firstperson

# Rebuild with explicit path

```text
```




### Build takes too long
**Normal:** 5-10 minutes for first build
**If >20 minutes:** Network issues, try resilient build
##

## 📦 Files Updated/Created

### Updated
- ✅ `requirements-backend.txt` — Pinned numpy to 2.1.2
- ✅ `Dockerfile.firstperson` — Added timeout/retry config

### Created
- ✅ `Dockerfile.firstperson.resilient` — Extra robust version
- ✅ `test-docker-build.ps1` — Windows test script
- ✅ `test-docker-build.sh` — Linux test script
- ✅ `check-docker-requirements.py` — Pre-flight checker
- ✅ `DOCKER_NETWORK_TROUBLESHOOTING.md` — Complete guide
- ✅ `DOCKER_FIX_SUMMARY.md` — Quick summary
- ✅ This file — Build guide
##

## 🎯 Success Indicators

### Build Succeeded ✅

```
Successfully tagged firstperson:latest
```text
```text
```



### Container Runs ✅

```bash

docker run -p 8000:8000 -p 3001:3001 firstperson:latest

# No errors, container starts

```text
```




### Frontend Loads ✅

```
curl http://localhost:3001

```text
```text
```


##

## 🚢 Deployment After Build

### 1. Tag for Registry

```bash

docker tag firstperson:latest your-registry/firstperson:v1.0.0

```text
```




### 2. Push to Registry

```bash
docker push your-registry/firstperson:v1.0.0
```text
```text
```



### 3. Deploy to Server

```bash


# On your DigitalOcean droplet (161.35.227.49)
ssh -i ~/.ssh/velinor root@161.35.227.49

# Pull and run
docker pull your-registry/firstperson:latest
docker run -d \
  -p 8000:8000 \
  -p 3001:3001 \
  -e ELEVENLABS_API_KEY=sk_... \
  -e SUPABASE_URL=https://... \

```text
```



##

## 📋 Checklist

Pre-build:
- [ ] `check-docker-requirements.py` passes all checks
- [ ] All required files exist
- [ ] Docker is installed and running
- [ ] Internet connectivity verified

Build:
- [ ] Standard build OR Resilient build completes
- [ ] No errors in build output
- [ ] Image created: `docker images | grep firstperson`

Post-build:
- [ ] FastAPI import works: `docker run --rm firstperson:latest python -c "import fastapi"`
- [ ] Health check responds: `curl http://localhost:8000/health`
- [ ] Container can start: `docker run ... firstperson:latest`
##

## 🔄 Rebuild Without Cache

If you need to force a clean rebuild:

```powershell

# Windows PowerShell
docker system prune -a  # Remove all images/containers
docker build --no-cache -f Dockerfile.firstperson -t firstperson:latest .

# macOS/Linux
docker system prune -a
docker build --no-cache -f Dockerfile.firstperson -t firstperson:latest .
```




**Warning:** This will remove all Docker images/containers!
##

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Pre-flight check | `python check-docker-requirements.py` |
| Build standard | `docker build -f Dockerfile.firstperson -t firstperson:latest .` |
| Build resilient | `docker build -f Dockerfile.firstperson.resilient -t firstperson:latest .` |
| Test build | `.\test-docker-build.ps1` (Windows) |
| List images | `docker images \| grep firstperson` |
| Run container | `docker run -p 8000:8000 -p 3001:3001 firstperson:latest` |
| Check logs | `docker logs <container-id>` |
| Stop container | `docker stop <container-id>` |
| Remove image | `docker rmi firstperson:latest` |
##

## ✅ Current Status

**Fixed Issues:**
- ✅ Network timeout during numpy download
- ✅ Pip retry configuration added
- ✅ Stable numpy version (2.1.2) specified
- ✅ Resilient Dockerfile created
- ✅ Test scripts provided
- ✅ Troubleshooting guide available

**Ready to:** Build Docker image with confidence 🚀
##

**Next Step:** Run `python check-docker-requirements.py` to verify everything is in place, then build!

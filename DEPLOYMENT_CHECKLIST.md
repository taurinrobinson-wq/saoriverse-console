# FirstPerson.Chat Deployment Checklist

## ✅ Completed

### Local Development
- [x] Backend (firstperson_backend.py) fully functional and tested
- [x] 3-tier glyph-informed response pipeline working
- [x] Backend running on http://127.0.0.1:8000
- [x] Health endpoint responding
- [x] Chat endpoint responding with intelligent responses

### Docker & Deployment Files
- [x] Dockerfile.firstperson created (multi-stage build)
- [x] docker-compose.prod.all.yml created (both Velinor + FirstPerson)
- [x] nginx.prod.firstperson.conf created (reverse proxy for both services)
- [x] entrypoint.firstperson.sh created (service startup script)
- [x] deploy.sh created (automated deployment script)
- [x] RUN_DEPLOYMENT.sh created (one-liner for droplet)
- [x] All files pushed to GitHub main branch

### DNS Configuration
- [x] Root domain (@) pointing to 161.35.227.49
- [x] www subdomain pointing to 161.35.227.49
- [x] velinor subdomain pointing to 161.35.227.49

---

## ⏳ Next Steps (Your Action Required)

### Step 1: Wait for DNS Propagation
- DNS changes can take 5-15 minutes to propagate globally
- Check propagation: `nslookup firstperson.chat`
- You should see it resolving to 161.35.227.49

### Step 2: Run Deployment on Droplet

**Option A: DigitalOcean Console (Recommended)**
1. Go to DigitalOcean Dashboard
2. Click your droplet (161.35.227.49)
3. Click "Console" button
4. Copy and paste this:
```bash
bash <(curl -s https://raw.githubusercontent.com/taurinrobinson-wq/saoriverse-console/main/deploy.sh)
```
5. Let it run (5-15 minutes)

**Option B: SSH (if keys set up)**
```bash
ssh root@161.35.227.49
bash <(curl -s https://raw.githubusercontent.com/taurinrobinson-wq/saoriverse-console/main/deploy.sh)
```

### Step 3: Verify Deployment (After DNS Propagates)

```bash
# Check containers are running
curl -s https://firstperson.chat/health | jq .

# Check both services
curl -s https://velinor.firstperson.chat/health | jq .

# Visit in browser
https://firstperson.chat
https://velinor.firstperson.chat
```

---

## 📊 What Gets Deployed

Your DigitalOcean droplet (161.35.227.49) will run:

```
┌─────────────────────────────────────────────────┐
│      DigitalOcean Droplet (161.35.227.49)       │
├─────────────────────────────────────────────────┤
│                                                 │
│  Docker Container: velinor_prod                 │
│  ├─ Port 8000 (internally)                      │
│  └─ Accessible at velinor.firstperson.chat      │
│                                                 │
│  Docker Container: firstperson_prod             │
│  ├─ Port 8000 (FastAPI backend)                 │
│  ├─ Port 3001 (Next.js frontend)                │
│  └─ Accessible at firstperson.chat              │
│                                                 │
│  Nginx Reverse Proxy                            │
│  ├─ Port 80 (HTTP → HTTPS redirect)             │
│  ├─ Port 443 (HTTPS with SSL/TLS)               │
│  └─ Routes traffic based on domain              │
│                                                 │
│  Certbot (Let's Encrypt SSL)                    │
│  ├─ Certificate for firstperson.chat            │
│  ├─ Certificate for velinor.firstperson.chat    │
│  └─ Auto-renewal setup                          │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 🔍 Useful Commands (On Your Droplet)

```bash
# Check all containers
docker ps

# View logs
docker-compose -f docker-compose.prod.all.yml logs -f

# View specific service logs
docker-compose -f docker-compose.prod.all.yml logs -f firstperson
docker-compose -f docker-compose.prod.all.yml logs -f velinor
docker-compose -f docker-compose.prod.all.yml logs -f nginx-ssl

# Restart a service
docker-compose -f docker-compose.prod.all.yml restart firstperson

# Pull latest code and redeploy
cd /root/saoriverse-console
git pull origin main
docker-compose -f docker-compose.prod.all.yml down
docker-compose -f docker-compose.prod.all.yml up -d --build

# Check SSL certificate status
certbot certificates

# Renew SSL manually (runs automatically)
certbot renew
```

---

## 🐛 Troubleshooting

### "Connection refused" when accessing firstperson.chat
- **Cause**: DNS hasn't propagated yet
- **Fix**: Wait 5-15 minutes and try again
- **Check**: `nslookup firstperson.chat` should show 161.35.227.49

### Container exits immediately
- **Check logs**: `docker-compose -f docker-compose.prod.all.yml logs firstperson`
- **Rebuild**: `docker-compose -f docker-compose.prod.all.yml up -d --build`

### SSL certificate not working
- **Check**: `certbot certificates` on droplet
- **Regenerate**: `certbot renew --force-renewal`

### Port 443 already in use
- Kill existing: `docker stop nginx_ssl_proxy && docker rm nginx_ssl_proxy`
- Restart: `docker-compose -f docker-compose.prod.all.yml up -d nginx-ssl`

---

## 📝 Quick Reference

| Service | URL | Port (Internal) | Status |
|---------|-----|-----------------|--------|
| FirstPerson Frontend | https://firstperson.chat | 3001 | Ready |
| FirstPerson Backend API | https://firstperson.chat/api | 8000 | Ready |
| Velinor | https://velinor.firstperson.chat | 8000 | Ready |
| Nginx Reverse Proxy | Port 80/443 (HTTPS) | 80/443 | Ready |

---

## 🎯 Expected Timeline

1. **Now**: DNS changes made ✅
2. **5-15 min**: DNS propagates
3. **Run deploy script** in droplet console
4. **5-10 min**: Docker downloads images and builds containers
5. **1-2 min**: SSL certificates generated
6. **Total time**: ~20-30 minutes until fully live

---

## ✨ Success Indicators

When everything is working:
- ✓ `docker ps` shows 3 containers running
- ✓ `curl https://firstperson.chat/health` returns JSON
- ✓ `curl https://velinor.firstperson.chat/health` returns JSON
- ✓ Browser shows firstperson.chat with UI loading
- ✓ Chat endpoint responds to POST requests

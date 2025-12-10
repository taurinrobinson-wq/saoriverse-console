# ✅ Velinor VPS Migration Checklist

Use this checklist to track your migration from Railway to DigitalOcean.

---

## Phase 1: Local Validation ✅ COMPLETE

- [x] Docker image builds successfully
- [x] Services start in correct sequence (Next.js → FastAPI → Nginx)
- [x] Health checks pass for all services
- [x] Frontend loads at localhost:8080
- [x] API endpoints respond correctly
- [x] Button styling updated (green/gold theme)
- [x] Local docker-compose.yml working

---

## Phase 2: Production Files Ready ✅ COMPLETE

- [x] docker-compose.prod.yml created with health checks
- [x] nginx.prod.conf created with SSL/TLS support
- [x] entrypoint.sh properly orchestrates services
- [x] Port separation: Next.js (3000), FastAPI (8001), Nginx (8000)
- [x] DEPLOYMENT_VPS.md guide created
- [x] VPS_QUICK_START.md quick reference created
- [x] .github/workflows/deploy.yml GitHub Actions workflow created

---

## Phase 3: DigitalOcean Setup

### Account & Droplet Creation
- [ ] Create DigitalOcean account
- [ ] Generate SSH key: `ssh-keygen -t ed25519 -f ~/.ssh/velinor`
- [ ] Create Droplet (Ubuntu 22.04, $6/month plan)
- [ ] Add SSH public key to Droplet during creation
- [ ] **Save Droplet IP address**: `_________________`

### DNS Configuration (Namecheap)
- [ ] Log into Namecheap account
- [ ] Go to firstperson.chat → Advanced DNS
- [ ] Add A Record: `velinor` → `[Droplet IP]`
- [ ] Save DNS record
- [ ] Wait 5-10 minutes for propagation
- [ ] Verify DNS: `nslookup velinor.firstperson.chat`

### VPS Initial Setup
- [ ] SSH into Droplet: `ssh root@[DROPLET_IP]`
- [ ] Update system packages: `apt-get update && apt-get upgrade -y`
- [ ] Install Docker
- [ ] Install Docker Compose
- [ ] Install certbot
- [ ] Create /opt/velinor directory

### Velinor Deployment
- [ ] Clone repository to /opt/velinor
- [ ] Build Docker image: `docker compose -f docker-compose.prod.yml build`
- [ ] Start containers: `docker compose -f docker-compose.prod.yml up -d`
- [ ] Verify containers running: `docker compose -f docker-compose.prod.yml ps`

### SSL Certificate Setup
- [ ] Install Let's Encrypt certificate
- [ ] Certificate path: `/etc/letsencrypt/live/velinor.firstperson.chat/`
- [ ] Restart nginx: `docker compose -f docker-compose.prod.yml restart nginx-ssl`
- [ ] Verify SSL: `curl -I https://velinor.firstperson.chat`

---

## Phase 4: Testing & Validation

### Endpoint Tests
- [ ] HTTP redirect: `curl -i http://velinor.firstperson.chat` (should be 301)
- [ ] HTTPS works: `curl https://velinor.firstperson.chat`
- [ ] Health check: `curl https://velinor.firstperson.chat/health`
- [ ] Frontend loads: `https://velinor.firstperson.chat` in browser
- [ ] Game is playable
- [ ] Buttons styled with green/gold theme

### Service Health
- [ ] Next.js running: `docker compose -f docker-compose.prod.yml logs velinor | grep "compiled"` 
- [ ] FastAPI running: `docker compose -f docker-compose.prod.yml logs velinor | grep "Application startup complete"`
- [ ] Nginx running: `docker compose -f docker-compose.prod.yml logs nginx-ssl | grep "listening on"`

---

## Phase 5: Auto-Deploy Setup (Optional)

### Deploy Key Generation
- [ ] SSH into VPS: `ssh root@[DROPLET_IP]`
- [ ] Generate deploy key: `ssh-keygen -t ed25519 -f /root/.ssh/velinor_deploy -C "velinor-deploy" -N ""`
- [ ] Copy public key: `cat /root/.ssh/velinor_deploy.pub`

### GitHub Deploy Key
- [ ] Go to GitHub repo → Settings → Deploy Keys
- [ ] Add deploy key with public key from above
- [ ] ✅ Enable "Allow write access"

### GitHub Secrets
- [ ] Go to GitHub repo → Settings → Secrets and variables → Actions
- [ ] Add `VPS_HOST`: `[DROPLET_IP]`
- [ ] Add `VPS_SSH_KEY`: `/root/.ssh/velinor_deploy` (private key content)

### Deploy Script
- [ ] Create `/opt/velinor/deploy.sh` on VPS
- [ ] Make executable: `chmod +x /opt/velinor/deploy.sh`
- [ ] Test manually: `/opt/velinor/deploy.sh`
- [ ] Workflow file exists: `.github/workflows/deploy.yml`

### Test Auto-Deploy
- [ ] Make a small change to code on local machine
- [ ] Push to main: `git push origin main`
- [ ] GitHub Actions workflow triggers automatically
- [ ] Wait for deployment to complete
- [ ] Verify change is live at `https://velinor.firstperson.chat`

---

## Phase 6: Post-Deployment

### Monitoring & Maintenance
- [ ] Monitor logs regularly: `docker compose -f docker-compose.prod.yml logs -f`
- [ ] Set up SSL renewal reminder (auto-renews but good to track)
- [ ] Document Droplet IP in secure location
- [ ] Document SSH key location on local machine
- [ ] Create backups of configuration files

### Documentation
- [ ] Share DEPLOYMENT_VPS.md with team members
- [ ] Share VPS_QUICK_START.md for quick reference
- [ ] Document any custom configurations made
- [ ] Note any DNS or domain specifics for future reference

### Railway Cleanup (Optional)
- [ ] Delete Railway project if no longer needed
- [ ] Cancel Railway subscription if auto-renewing
- [ ] Export any important logs for archival

---

## Phase 7: Ongoing Operations

### Weekly
- [ ] Check container health: `docker compose -f docker-compose.prod.yml ps`
- [ ] Review error logs if any

### Monthly
- [ ] Update system packages on VPS: `apt-get update && apt-get upgrade`
- [ ] Test SSL certificate renewal process
- [ ] Verify auto-deploy is working (make test push if needed)

### Quarterly
- [ ] Review resource usage (DigitalOcean dashboard)
- [ ] Consider upgrading Droplet if needed
- [ ] Review security settings and updates

### Annually
- [ ] Renew domain registration
- [ ] Review costs and plan
- [ ] Consider backup Droplet setup

---

## 📊 Completion Summary

**Total Phases**: 7  
**Current Phase**: Phase 3 (You are here after setup)

**Estimated Time**:
- Phase 1: ✅ Already done (local validation)
- Phase 2: ✅ Already done (files created)
- Phase 3: ~15 minutes (VPS setup)
- Phase 4: ~5 minutes (testing)
- Phase 5: ~10 minutes (auto-deploy, optional)
- Phase 6-7: Ongoing

**Total First-Time Setup**: ~30-45 minutes

---

## 🆘 If Something Goes Wrong

### Container won't start
```bash
# Check logs
docker compose -f docker-compose.prod.yml logs velinor

# Restart containers
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

### SSL certificate issues
```bash
# Check if cert exists
ls /etc/letsencrypt/live/velinor.firstperson.chat/

# Re-issue certificate
certbot certonly --force-renewal --standalone -d velinor.firstperson.chat
```

### Auto-deploy not working
```bash
# Check deploy key
cat /root/.ssh/velinor_deploy.pub

# Verify GitHub has the key
# Check GitHub Actions logs for error details

# Test deploy script manually
/opt/velinor/deploy.sh
```

### DNS not working
```bash
# Check DNS propagation
nslookup velinor.firstperson.chat

# Check Namecheap DNS settings are saved
# Wait additional 5-10 minutes

# Flush local DNS cache
# macOS: dscacheutil -flushcache
# Windows: ipconfig /flushdns
# Linux: sudo systemctl restart systemd-resolved
```

---

## ✨ Success Criteria

Your migration is **complete and successful** when:

✅ You can visit **https://velinor.firstperson.chat** in any browser  
✅ Game loads and plays normally  
✅ Buttons display with green/gold theme  
✅ All API endpoints respond correctly  
✅ SSL certificate is valid (no browser warnings)  
✅ Containers auto-restart on crash  
✅ Auto-deploy works (optional but recommended)  
✅ Railway project is decommissioned  

---

**Good luck! 🚀 You've got this!**

# 📟 Velinor VPS - Quick Reference Card

Print this and keep it handy! 📋

##

## 🎯 Your Deployment Path

```text
```


LOCAL MACHINE ↓ git push GITHUB (main branch) ↓ auto-trigger GITHUB ACTIONS (deploy.yml) ↓ SSH
execute DIGITALOCEAN VPS (123.45.67.89) ↓ docker compose DOCKER CONTAINERS
    ├─ Next.js (port 3000)
    ├─ FastAPI (port 8001)
    └─ Nginx (port 8000)
↓ INTERNET PUBLIC <https://velinor.firstperson.chat> ✨

```


##

## 🚀 Quick Setup Commands

### Droplet Creation (DigitalOcean)

```bash



## SSH Key Generation
ssh-keygen -t ed25519 -f ~/.ssh/velinor

## Then create Droplet:

## Image: Ubuntu 22.04 LTS

## Plan: Basic $6/month

## SSH Key: Paste ~/.ssh/velinor.pub

## Hostname: velinor-server

```text
```


### DNS Setup (Namecheap)

```
A Record:
  Host: velinor
  Value: [YOUR_DROPLET_IP]
```text

```text
```


### VPS Setup (One-liner)

```bash

ssh root@[DROPLET_IP]

## Then paste the full script from VPS_QUICK_START.md Step 4

## It will:

## - Install Docker, Docker Compose, Certbot

## - Clone your repo

## - Build and start containers

## - Issue SSL certificate

```text

```

### Test Deployment

```bash


## From local machine
curl https://velinor.firstperson.chat

## Should show HTML

curl https://velinor.firstperson.chat/health

## Should show JSON

## Visit in browser
https://velinor.firstperson.chat

```text
```text

```

##

## 📊 Port Reference

| Service | Internal Port | External Port | Purpose |
|---------|---------------|---------------|---------|
| Next.js (Frontend) | 3000 | (proxied) | User interface |
| FastAPI (Backend) | 8001 | (proxied) | Game API |
| Nginx (Reverse Proxy) | 8000 | 8080 local / 443 prod | Public entry point |
| Let's Encrypt | (socket) | 80 / 443 | SSL termination |

**Important**:

- Port 8000 is what's exposed from container
- On DigitalOcean: 80→443 via nginx, 443→services
- Local docker: map 8080→8000

##

## 🔑 SSH Commands Cheat Sheet

```bash



## SSH into VPS
ssh root@YOUR_DROPLET_IP

## SSH into container
docker exec -it velinor_prod bash

## View logs
docker compose -f docker-compose.prod.yml logs -f

## Restart services
docker compose -f docker-compose.prod.yml restart

## Stop services
docker compose -f docker-compose.prod.yml down

## Start services
docker compose -f docker-compose.prod.yml up -d

## Check status
docker compose -f docker-compose.prod.yml ps

## Manual deploy

```text
```


##

## 🌐 DNS & Domain Reference

| Item | Value | Where |
|------|-------|-------|
| Registrar | Namecheap | firstperson.chat |
| Subdomain | velinor | velinor.firstperson.chat |
| A Record Value | YOUR_DROPLET_IP | Namecheap DNS |
| SSL Provider | Let's Encrypt | certbot on VPS |
| SSL Auto-Renew | Yes | certbot renewal service |

##

## 📁 File Structure (What to Keep)

```
Your VPS (/opt/velinor):
├── docker-compose.prod.yml    ← Orchestration config
├── nginx.prod.conf            ← Reverse proxy config
├── entrypoint.sh              ← Service startup script
├── Dockerfile                 ← Container definition
├── .github/
│   └── workflows/
│       └── deploy.yml         ← Auto-deploy config
├── velinor/                   ← Backend code
├── velinor-web/               ← Frontend code
├── requirements-game.txt      ← Python dependencies
```text

```text
```


##

## 🆘 Emergency Commands

### Container crashed? Restart it

```bash

```text

```

### Docker network issue? Reset

```bash

docker compose -f docker-compose.prod.yml down

```text
```text

```

### Nginx won't start? Check config

```bash


```text
```


### SSL cert expired? Renew now

```bash
certbot renew --force-renewal
```text

```text
```


### Check if DNS is working

```bash

nslookup velinor.firstperson.chat

```text

```

### Check SSL certificate

```bash

curl -I https://velinor.firstperson.chat

```text
```text

```

##

## 📊 Monitoring Checklist

**Daily** (automated):

- [ ] Containers auto-restart if crashed
- [ ] SSL certificate renewed automatically (if expiring soon)

**Weekly** (manual):

```bash


docker compose -f docker-compose.prod.yml ps

```text
```


**Monthly**:

```bash

## Update packages
apt-get update && apt-get upgrade -y

## Test deploy script
```text

```text
```


##

## 🎬 Common Deployment Workflow

### Scenario 1: Make code changes

```bash


## Local machine
cd ~/saoriverse-console
git add .
git commit -m "feat: my change"
git push origin main

## GitHub Actions auto-triggers

## VPS automatically updates within 5-10 minutes

```sql

```

### Scenario 2: Update configuration

```bash


## Edit docker-compose.prod.yml or nginx.prod.conf locally
git add docker-compose.prod.yml nginx.prod.conf git commit -m "chore: update config" git push origin
main

```text
```text

```

### Scenario 3: Manual emergency fix

```bash



## SSH to VPS
ssh root@[DROPLET_IP]

## Make fix
cd /opt/velinor nano docker-compose.prod.yml  # or edit any file

## Manually redeploy
docker compose -f docker-compose.prod.yml down

```text
```


##

## 💡 Pro Tips

✨ **Tip 1**: Keep SSH key safe

```bash

## NEVER share /root/.ssh/velinor_deploy (private key)

## It's what gives GitHub permission to deploy
```text

```text
```


✨ **Tip 2**: Set up DigitalOcean Cloud Firewall

```

Inbound Rules (Allow):
  - SSH (22) from your IP
  - HTTP (80) from Everywhere
  - HTTPS (443) from Everywhere

```text

```

✨ **Tip 3**: Monitor with DigitalOcean Dashboard

- CPU usage (should be < 30% idle)
- Memory usage (2GB total, usually 70-80% used)
- Bandwidth (track for growth)
- Droplet health checks

✨ **Tip 4**: Keep deploy script fresh

```bash


## On VPS, regularly verify deploy.sh exists and works
/opt/velinor/deploy.sh --dry-run  # Test without deploying

```

##

## 🎯 Success Checklist

- [ ] Droplet created ($6/month)
- [ ] DNS record added (velinor.firstperson.chat)
- [ ] SSH into VPS works
- [ ] Docker & Docker Compose installed
- [ ] Repository cloned to /opt/velinor
- [ ] Docker image built
- [ ] Containers running
- [ ] SSL certificate issued
- [ ] <https://velinor.firstperson.chat> loads
- [ ] Game is playable
- [ ] Auto-deploy configured (optional)
- [ ] Railway decommissioned

**If all checked**: You're done! 🎉

##

## 📞 Help Resources

| Problem | Solution | File |
|---------|----------|------|
| "How do I set up?" | Full guide | DEPLOYMENT_VPS.md |
| "Quick copy-paste?" | Commands only | VPS_QUICK_START.md |
| "What's my status?" | Track progress | VPS_MIGRATION_CHECKLIST.md |
| "Push to GitHub?" | Git commands | PUSH_TO_GITHUB.md |
| "Overall summary?" | Big picture | VPS_MIGRATION_SUMMARY.md |

##

## 🚀 Estimated Costs (12 months)

| Item | Monthly | Yearly |
|------|---------|--------|
| DigitalOcean Droplet | $6 | $72 |
| Domain renewal | ~$0.75 | $9 |
| Backups (optional) | $0-1 | $0-12 |
| **Total** | **~$7** | **~$82** |

**vs Railway**: $5-50+/month with downtime 😞
**vs Heroku**: Shutdown 😞
**vs AWS**: Complex setup, $10+/month 😕
**DigitalOcean**: Simple, $6/month, rock solid ✨

## **Print this card | Keep it safe | Refer to it often**

*Last Updated: Now*
*Deployment Status: Ready to Launch 🚀*
*Velinor Status: Waiting for your command ⚔️*

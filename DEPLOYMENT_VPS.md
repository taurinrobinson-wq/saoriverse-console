# 🚀 Velinor Deployment Guide - DigitalOcean VPS

This guide walks you through deploying Velinor to a DigitalOcean VPS with SSL, proper nginx routing, and auto-restart capabilities.

---

## 📋 Prerequisites

- DigitalOcean account (sign up at https://digitalocean.com)
- Namecheap DNS access for `firstperson.chat`
- SSH key pair (generate with `ssh-keygen -t ed25519`)
- GitHub repository with this code pushed

---

## 🖥️ Step 1: Create DigitalOcean Droplet

### Option A: Via DigitalOcean Web Dashboard (Easiest)

1. Log into DigitalOcean → **Create** → **Droplets**
2. **Choose Image**: Ubuntu 22.04 LTS
3. **Choose Plan**: Basic (Shared CPU), $6/month (1 vCPU, 2GB RAM, 50GB SSD)
4. **Region**: Choose closest to you (NYC, SFO, etc.)
5. **Authentication**: Add your SSH public key
   - If you don't have one: `ssh-keygen -t ed25519 -f ~/.ssh/velinor -C "velinor@firstperson"`
   - Copy content of `~/.ssh/velinor.pub` into the SSH key field
6. **Hostname**: `velinor-server`
7. Click **Create Droplet**

**Save your Droplet IP** (e.g., `123.45.67.89`)

---

## 🌐 Step 2: Configure DNS (Namecheap)

1. Log into Namecheap → Manage `firstperson.chat`
2. Go to **Advanced DNS**
3. Find the **A Record** section
4. Add a new A Record:
   - **Host**: `velinor`
   - **Value**: Your Droplet IP (e.g., `123.45.67.89`)
   - **TTL**: 30 min (Automatic)
5. Click **Save**

Wait 5-10 minutes for DNS to propagate. Test with:
```bash
nslookup velinor.firstperson.chat
```

---

## 🔧 Step 3: Initial VPS Setup

SSH into your droplet:
```bash
ssh root@YOUR_DROPLET_IP
# Example: ssh root@123.45.67.89
```

Run these commands on the VPS:

```bash
# Update system packages
apt-get update && apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Install Docker Compose
apt-get install -y docker-compose-plugin

# Verify installation
docker --version
docker compose version

# Add current user to docker group (optional, for non-root docker commands)
usermod -aG docker $USER
```

---

## 📦 Step 4: Clone and Deploy Velinor

Still on the VPS:

```bash
# Clone your repository
cd /opt
git clone https://github.com/YOUR_USERNAME/saoriverse-console.git velinor
cd velinor

# Build the Docker image (this takes ~2-3 minutes)
docker compose -f docker-compose.prod.yml build

# Start the containers
docker compose -f docker-compose.prod.yml up -d

# Verify containers are running
docker compose -f docker-compose.prod.yml ps
```

You should see:
- `velinor_prod` - Running
- `nginx_ssl_proxy` - Running

---

## 🔒 Step 5: Set Up SSL Certificate

Still on the VPS:

```bash
# Install certbot (Let's Encrypt)
apt-get install -y certbot python3-certbot-nginx

# Issue SSL certificate
certbot certonly --standalone \
  -d velinor.firstperson.chat \
  --email your-email@example.com \
  --agree-tos \
  --non-interactive

# Verify certificate was created
ls -la /etc/letsencrypt/live/velinor.firstperson.chat/
```

Then restart nginx to use the certificate:
```bash
docker compose -f docker-compose.prod.yml restart nginx-ssl
```

---

## ✅ Step 6: Test Deployment

From your local machine:

```bash
# Test HTTP redirect to HTTPS
curl -i http://velinor.firstperson.chat
# Should return 301 redirect to HTTPS

# Test HTTPS (with SSL)
curl https://velinor.firstperson.chat
# Should return HTML from Velinor

# Check health endpoint
curl https://velinor.firstperson.chat/health
# Should return JSON response
```

Visit **https://velinor.firstperson.chat** in your browser - you should see the Velinor game with the mystical green/gold buttons! 🎮

---

## 🔄 Step 7: Auto-Deploy on Git Push (Optional but Recommended)

To automatically deploy when you push to GitHub:

### 7a. Create Deploy Key

On the VPS:
```bash
ssh-keygen -t ed25519 -f /root/.ssh/velinor_deploy -C "velinor-deploy" -N ""
cat /root/.ssh/velinor_deploy.pub
```

Copy the output.

### 7b. Add to GitHub

1. Go to your GitHub repo → **Settings** → **Deploy Keys**
2. Click **Add deploy key**
3. **Title**: `Velinor VPS Deploy`
4. **Key**: Paste the public key from above
5. ✅ Check **Allow write access**
6. Click **Add key**

### 7c. Create Deploy Script

On the VPS, create `/opt/velinor/deploy.sh`:

```bash
#!/bin/bash
set -e

echo "[$(date)] Starting Velinor deployment..."

cd /opt/velinor

# Pull latest code
git pull origin main

# Rebuild Docker image
echo "Building Docker image..."
docker compose -f docker-compose.prod.yml build

# Restart containers
echo "Restarting containers..."
docker compose -f docker-compose.prod.yml up -d

# Wait for health check
echo "Waiting for services to be healthy..."
sleep 10

# Verify
if docker compose -f docker-compose.prod.yml ps | grep -q "velinor_prod.*running"; then
  echo "[$(date)] ✅ Deployment successful!"
else
  echo "[$(date)] ❌ Deployment failed!"
  exit 1
fi
```

Make it executable:
```bash
chmod +x /opt/velinor/deploy.sh
```

### 7d. Create GitHub Actions Workflow

In your repo, create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to VPS

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VPS_HOST }}
          username: root
          key: ${{ secrets.VPS_SSH_KEY }}
          script: /opt/velinor/deploy.sh
```

### 7e. Add Secrets to GitHub

1. Go to repo → **Settings** → **Secrets and variables** → **Actions**
2. Add two secrets:
   - **VPS_HOST**: Your Droplet IP (e.g., `123.45.67.89`)
   - **VPS_SSH_KEY**: Content of `/root/.ssh/velinor_deploy` (private key)

Now every time you `git push origin main`, your VPS automatically deploys! 🚀

---

## 📊 Maintenance

### Check Logs

```bash
# Container logs
docker compose -f docker-compose.prod.yml logs -f velinor

# Nginx logs
docker compose -f docker-compose.prod.yml logs -f nginx-ssl

# SSH in for direct inspection
ssh root@YOUR_DROPLET_IP
docker exec -it velinor_prod bash
```

### Renew SSL Certificate

Let's Encrypt certificates expire after 90 days. Certbot auto-renews, but to manually force:

```bash
certbot renew --force-renewal
docker compose -f docker-compose.prod.yml restart nginx-ssl
```

### Update Velinor

```bash
cd /opt/velinor
git pull origin main
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

### Stop Services

```bash
cd /opt/velinor
docker compose -f docker-compose.prod.yml down
```

---

## 🆘 Troubleshooting

### "Connection refused"
- Check if containers are running: `docker compose -f docker-compose.prod.yml ps`
- Check logs: `docker compose -f docker-compose.prod.yml logs`

### DNS not working
- Wait 10 minutes after setting DNS record
- Test: `nslookup velinor.firstperson.chat`

### SSL certificate not found
- Verify certbot created it: `ls /etc/letsencrypt/live/velinor.firstperson.chat/`
- If missing, re-run certbot from Step 5

### Nginx not proxying correctly
- Verify velinor container is healthy: `docker compose -f docker-compose.prod.yml ps`
- Check nginx config: `docker exec nginx_ssl_proxy cat /etc/nginx/nginx.conf`

---

## 💰 Cost Breakdown

- **DigitalOcean Droplet**: $6/month
- **Domain** (firstperson.chat): ~$9/year (already have)
- **SSL Certificate**: FREE (Let's Encrypt)

**Total: ~$0.50/month for Velinor** (vs. Railway's variable, buggy pricing)

---

## 🎉 You're Done!

Your Velinor game is now live at **https://velinor.firstperson.chat** with:
- ✅ Production-grade Docker setup
- ✅ SSL/HTTPS encryption
- ✅ Automatic restart on crash
- ✅ Auto-deploy on GitHub push
- ✅ Full SSH access for debugging
- ✅ 99.9% uptime reliability

Enjoy! 🚀

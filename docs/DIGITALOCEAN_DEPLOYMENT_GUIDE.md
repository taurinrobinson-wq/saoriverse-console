# DigitalOcean Deployment Guide (IP: 161.35.227.49)

This is your complete step-by-step guide to deploy the FirstPerson web application on your DigitalOcean droplet running Ubuntu.
##

## Prerequisites

✓ Ubuntu 22.04 LTS or later on your DigitalOcean droplet (161.35.227.49)
✓ SSH access to your droplet
✓ GitHub repository cloned locally
##

## Quick Start (5 minutes)

### Step 1: Connect to Your Droplet

```bash
ssh root@161.35.227.49

# If using SSH key, it may be automatic

```text
```



### Step 2: Run the Automated Setup Script

```bash

# Clone the repo
git clone https://github.com/taurinrobinson-wq/saoriverse-console.git
cd saoriverse-console

# Make the setup script executable
chmod +x docker-setup.sh

# Run it
```text
```



This script will:
- ✓ Install Docker & Docker Compose
- ✓ Clone your repository
- ✓ Create .env file
- ✓ Build Docker images
- ✓ Start all containers
- ✓ Verify everything is working

### Step 3: Verify Deployment

```bash

# Check running containers
docker compose ps

# Test the API
curl http://161.35.227.49:8000/health

# Test the frontend
```text
```


##

## Detailed Setup (If You Prefer Manual Installation)

### Install Docker Manually

```bash

# Update system
sudo apt update
sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
    https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Allow running docker without sudo (optional)
sudo usermod -aG docker $USER
newgrp docker

# Verify
```text
```



### Clone & Configure Your Project

```bash

# Clone repository
git clone https://github.com/taurinrobinson-wq/saoriverse-console.git
cd saoriverse-console

# Copy example environment file
cp .env.example .env

# Edit with your settings (if needed)
nano .env

# Key variables to check:

# - API_URL=http://161.35.227.49:8000

# - FRONTEND_URL=http://161.35.227.49

```text
```



### Build and Start Services

```bash

# Build Docker images
docker compose build

# Start containers in background
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f

# View just backend logs
docker compose logs -f backend

# View just frontend logs
```text
```


##

## Access Your Application

Once everything is running:

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://161.35.227.49:3000 | React/Expo web app |
| API Backend | http://161.35.227.49:8000 | FastAPI server |
| Nginx Proxy | http://161.35.227.49:80 | Reverse proxy |
| Health Check | http://161.35.227.49:8000/health | API health status |
##

## Common Operations

### View Logs

```bash

# All services
docker compose logs

# Specific service
docker compose logs backend
docker compose logs frontend
docker compose logs nginx

# Follow logs in real-time
docker compose logs -f

# Last 100 lines
docker compose logs --tail 100

# Last 100 lines, following
```text
```



### Stop Services

```bash

# Stop without removing
docker compose stop

# Restart
docker compose restart

# Remove everything (data persists in volumes)
docker compose down

# Remove everything including volumes (WARNING: deletes data)
```text
```



### Restart Individual Services

```bash

# Restart backend
docker compose restart backend

# Restart frontend
docker compose restart frontend

# Restart nginx
```text
```



### Execute Commands in Containers

```bash

# Get a shell in the backend container
docker compose exec backend bash

# Run a Python command in backend
docker compose exec backend python -c "import sys; print(sys.version)"

# Get a shell in the frontend container
```text
```



### View Resource Usage

```bash

# Overall Docker stats
docker stats

# Space usage
docker system df

# Prune unused images/containers
```text
```


##

## Update Your Application

### Deploy New Code

```bash

# Pull latest changes
git pull origin main

# Rebuild images
docker compose build

# Restart with new code
docker compose up -d

# Verify
```sql
```



### Update Specific Service

```bash

# Just rebuild and restart backend
docker compose up -d --build backend

# Just rebuild and restart frontend
```text
```


##

## Troubleshooting

### Service Won't Start

```bash

# Check logs first
docker compose logs backend

# Rebuild from scratch
docker compose down
docker compose build --no-cache
docker compose up -d

# Check if ports are already in use
sudo lsof -i :8000
sudo lsof -i :3000
```text
```



### Out of Disk Space

```bash

# Check usage
docker system df

# Clean up everything unused
docker system prune -a

# Remove specific image
```text
```



### Network Issues

```bash

# Check networks
docker network ls

# Inspect network
docker network inspect saoriverse-console_saoriverse

# Restart network
docker compose down
```sql
```



### Can't Connect to Backend from Frontend

```bash

# Check if backend is healthy
docker compose ps

# Status should be "Up (healthy)"

# Test backend from inside frontend container
docker compose exec frontend curl http://backend:8000/health

# Check environment variable in frontend
docker compose exec frontend env | grep API_URL

```text
```


##

## Backup & Recovery

### Backup Your Data

```bash

# Backup database and files
docker compose exec backend tar -czf /app/backup.tar.gz data_local/

# Copy to your machine
docker cp saoriverse-backend:/app/backup.tar.gz ./backup.tar.gz

# Or use rsync
```sql
```



### Restore from Backup

```bash

# Copy backup to container
docker cp backup.tar.gz saoriverse-backend:/app/

# Extract
docker compose exec backend tar -xzf /app/backup.tar.gz

# Restart
```text
```


##

## SSL/HTTPS Setup (Optional)

### Using Let's Encrypt

```bash

# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate (stops nginx temporarily)
docker compose stop nginx
sudo certbot certonly --standalone -d 161.35.227.49

# Update nginx.conf with SSL directives

# Then restart nginx
```sql
```



### Update nginx.conf for HTTPS

Add to your nginx.conf:

```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/161.35.227.49/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/161.35.227.49/privkey.pem;
    # ... rest of config
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    return 301 https://$host$request_uri;
```text
```


##

## Health Monitoring

### Create a Monitoring Script

```bash
#!/bin/bash

# save as check-health.sh

echo "=== Container Status ==="
docker compose ps

echo ""
echo "=== API Health ==="
curl -s http://161.35.227.49:8000/health || echo "FAILED"

echo ""
echo "=== Frontend Health ==="
curl -s http://161.35.227.49:3000 | head -20 || echo "FAILED"

echo ""
echo "=== Disk Usage ==="
```text
```



Run it regularly:

```bash
chmod +x check-health.sh
./check-health.sh

# Or set up a cron job to check every hour
crontab -e

# Add: 0 * * * * /root/saoriverse-console/check-health.sh >> /var/log/saoriverse-health.log 2>&1
```


##

## Next Steps

1. ✅ Run `./docker-setup.sh` to get everything started
2. ✅ Verify all services are running: `docker compose ps`
3. ✅ Check your app works: Visit http://161.35.227.49:3000
4. ✅ Monitor logs: `docker compose logs -f`
5. ✅ Set up SSL (optional): Use Let's Encrypt
6. ✅ Configure backups if needed
7. ✅ Set up monitoring/health checks
##

## Support & Documentation

- **Docker Docs**: https://docs.docker.com/
- **Docker Compose Docs**: https://docs.docker.com/compose/
- **Nginx Docs**: https://nginx.org/en/docs/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
##

**Your deployment is ready! 🚀**

Start with: `./docker-setup.sh`

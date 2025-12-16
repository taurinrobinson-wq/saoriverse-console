# Docker Setup & Deploy Guide for Ubuntu (DigitalOcean 161.35.227.49)

This guide walks you through setting up Docker on your fresh Ubuntu installation and deploying the FirstPerson web build to your DigitalOcean droplet.
##

## Part 1: Install Docker Desktop on Ubuntu

### Step 1a: Install Docker Engine (Foundation)

```bash

# Update package index
sudo apt update
sudo apt upgrade -y

# Install Docker dependencies
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index again
sudo apt update

# Install Docker Engine
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verify installation
docker --version
```



### Step 1b: Post-Installation Setup (Optional but Recommended)

```bash

# Allow running docker without sudo
sudo usermod -aG docker $USER

# Apply group changes (you may need to log out and back in)
newgrp docker

# Verify you can run docker without sudo
docker ps
```



### Step 1c: Start Docker Service

```bash

# Enable Docker to start on boot
sudo systemctl enable docker

# Start Docker if not already running
sudo systemctl start docker

# Check status
sudo systemctl status docker
```


##

## Part 2: Install Docker Compose (if not included)

```bash

# Check if docker-compose already installed
docker compose version

# If not, install it
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker compose version
```


##

## Part 3: Prepare Your Project for Docker

### Create Docker Configuration Files

#### 3a. Create `Dockerfile` (Backend - Python/FastAPI)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p /app/data_local

EXPOSE 8000

# Run FastAPI server
CMD ["uvicorn", "core.start:app", "--host", "0.0.0.0", "--port", "8000"]
```



#### 3b. Create `Dockerfile.frontend` (Frontend - React/Expo)

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY firstperson/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend code
COPY firstperson/src ./src
COPY firstperson/*.js ./
COPY firstperson/*.json ./

# Expose port (for development; production uses different setup)
EXPOSE 3000

# Start Expo
CMD ["npx", "expo", "start", "--web"]
```



#### 3c. Create `docker-compose.yml`

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - PORT=8000
    volumes:
      - ./data:/app/data_local
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - saoriverse

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_SAOYNX_API_URL=http://backend:8000
    depends_on:
      - backend
    networks:
      - saoriverse

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deploy/nginx.conf:/etc/nginx/nginx.conf:ro
      # - ./certs:/etc/nginx/certs:ro  # uncomment when using SSL
    depends_on:
      - backend
      - frontend
    networks:
      - saoriverse

networks:
  saoriverse:
    driver: bridge
```



#### 3d. Create `.dockerignore`

```
.git
.gitignore
.venv
venv
__pycache__
*.pyc
.pytest_cache
.mypy_cache
node_modules
.env.local
.DS_Store
.idea
.vscode
```


##

## Part 4: Deploy to Your DigitalOcean Droplet (161.35.227.49)

### 4a: Clone Your Repository on the Droplet

```bash

# SSH into your droplet
ssh root@161.35.227.49

# Clone the repository
git clone https://github.com/taurinrobinson-wq/saoriverse-console.git
cd saoriverse-console
```



### 4b: Configure Environment Variables

```bash

# Create .env file from template
cp .env.example .env

# Edit with your settings
nano .env
```



Add/update these variables:

```env

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_URL=http://161.35.227.49:8000

# Frontend Configuration
FRONTEND_URL=http://161.35.227.49

# Database (if needed)
DATABASE_URL=sqlite:///./data_local/app.db

# Other configs as needed from your .env.example
```



### 4c: Build and Start Containers

```bash

# Build images
docker compose build

# Start containers in background
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f

# View backend logs only
docker compose logs -f backend

# View frontend logs only
docker compose logs -f frontend
```



### 4d: Verify Deployment

```bash

# Test backend API
curl http://161.35.227.49:8000/health

# Test frontend
curl http://161.35.227.49:3000

# Check container health
docker compose ps
```


##

## Part 5: Nginx Configuration (Reverse Proxy)

Update `deploy/nginx.conf` to route traffic:

```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}

server {
    listen 80;
    server_name 161.35.227.49;

    # API routes
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```


##

## Part 6: Common Docker Commands

```bash

# View all containers
docker ps -a

# View running containers
docker ps

# Start containers
docker compose start

# Stop containers
docker compose stop

# Restart containers
docker compose restart

# Remove containers and volumes
docker compose down

# Remove containers and volumes and images
docker compose down --rmi all

# View logs (all services)
docker compose logs

# View logs (specific service)
docker compose logs backend

# Follow logs in real-time
docker compose logs -f

# Execute command in running container
docker compose exec backend bash

# Check resource usage
docker stats
```


##

## Part 7: Maintenance & Updates

### Update Application Code

```bash

# Pull latest changes
git pull origin main

# Rebuild images
docker compose build

# Restart with new code
docker compose up -d
```



### View Application Logs

```bash

# All services
docker compose logs -f

# Last 100 lines
docker compose logs --tail 100
```



### Backup Data

```bash

# Backup SQLite database
docker compose exec backend cp data_local/app.db data_local/app.db.backup

# Or tar everything
docker compose exec backend tar -czf /tmp/backup.tar.gz data_local/
docker cp <container_id>:/tmp/backup.tar.gz ./backup.tar.gz
```


##

## Part 8: Troubleshooting

### Container won't start

```bash

# Check logs
docker compose logs backend

# Rebuild and restart
docker compose down
docker compose up --build
```



### Port conflicts

```bash

# Check what's using port 8000
sudo netstat -tlnp | grep 8000

# Kill process (if needed)
sudo kill -9 <PID>
```



### Network issues

```bash

# Check network
docker network ls
docker network inspect saoriverse-console_saoriverse

# Rebuild network
docker compose down
docker compose up -d --remove-orphans
```



### Out of disk space

```bash

# Check disk usage
docker system df

# Clean up unused images/containers/networks
docker system prune -a
```


##

## Part 9: SSL/HTTPS Setup (Optional)

### Using Let's Encrypt with Certbot

```bash

# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --standalone -d 161.35.227.49

# Update nginx.conf with SSL

# Then: docker compose restart nginx
```


##

## Quick Reference Summary

| Task | Command |
|------|---------|
| Install Docker | `curl -fsSL https://get.docker.com \| sh` |
| Clone repo | `git clone https://github.com/taurinrobinson-wq/saoriverse-console.git` |
| Build & start | `docker compose up -d --build` |
| Check status | `docker compose ps` |
| View logs | `docker compose logs -f` |
| Stop everything | `docker compose down` |
| Test API | `curl http://161.35.227.49:8000/health` |
| Test frontend | `curl http://161.35.227.49:3000` |
##

## Support & Next Steps

1. **Run through Part 1** - Install Docker on your Ubuntu machine
2. **Run through Part 3** - Create Docker config files in your repo
3. **Run through Part 4** - Deploy to DigitalOcean droplet
4. **Run through Part 5** - Set up Nginx for routing
5. **Verify** - Test both API and frontend endpoints
6. **Monitor** - Use `docker compose logs -f` to watch for issues

Good luck! 🚀

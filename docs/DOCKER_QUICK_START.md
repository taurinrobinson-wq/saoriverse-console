# 🚀 Quick Start Reference - Docker Deployment

**DigitalOcean IP**: 161.35.227.49
**Status**: Ready to deploy!

##

## One-Liner Deployment

```bash
```text
```text
```

##

## Step-by-Step (5 minutes)

```bash


# 1. Connect
ssh root@161.35.227.49

# 2. Clone & setup
git clone https://github.com/taurinrobinson-wq/saoriverse-console.git
cd saoriverse-console
chmod +x docker-setup.sh

# 3. Run setup
./docker-setup.sh

# 4. Verify
docker compose ps

```text
```

##

## Access Your App

| URL | Purpose |
|-----|---------|
| `http://161.35.227.49:3000` | 🌐 Web App (Frontend) |
| `http://161.35.227.49:8000` | ⚙️ API Server |
| `http://161.35.227.49:80` | 🔄 Nginx Proxy |
| `http://161.35.227.49:8000/health` | 💚 Health Check |

##

## Most Common Commands

```bash

# View all containers
docker compose ps

# View logs (follow updates in real-time)
docker compose logs -f

# Just backend logs
docker compose logs -f backend

# Just frontend logs
docker compose logs -f frontend

# Stop everything
docker compose stop

# Restart everything
docker compose restart

# Pull latest code and restart
git pull && docker compose up -d --build

# Shell access to backend
docker compose exec backend bash

# Check disk usage
```text
```text
```

##

## What Got Deployed

```

saoriverse-console/
├── Dockerfile              ← Backend (Python/FastAPI)
├── Dockerfile.frontend     ← Frontend (React/Expo)
├── docker-compose.yml      ← Orchestration
├── docker-setup.sh         ← Setup automation
├── deploy/nginx.conf       ← Reverse proxy config
│
├── .env                    ← Configuration (copy from .env.example)
├── requirements.txt        ← Python dependencies
├── core/start.py           ← FastAPI entry point
│
├── firstperson/            ← React/Expo frontend
│   ├── src/config.js       ← API configuration
│   └── package.json        ← Node dependencies
│

```text
```

##

## If Something Goes Wrong

### Service won't start

```bash
docker compose logs

# Read the error message, then:
docker compose down
docker compose build --no-cache
```text
```text
```

### Port already in use

```bash


# Kill the process using the port
sudo lsof -i :8000
sudo kill -9 <PID>

```sql
```

### Can't connect to backend from frontend

```bash

# Check if backend is healthy
docker compose ps

# Status column should say "healthy"

# Test from inside frontend container
```text
```text
```

### Disk full

```bash

docker system df
docker system prune -a

```

##

## Deployment Checklist

- [ ] SSH access to 161.35.227.49
- [ ] Git installed on droplet
- [ ] Docker setup: `./docker-setup.sh`
- [ ] All containers running: `docker compose ps`
- [ ] API responding: `curl http://161.35.227.49:8000/health`
- [ ] Frontend accessible: `curl http://161.35.227.49:3000`
- [ ] .env configured properly
- [ ] Data directory created: `/app/data_local`
- [ ] Logs are clean: `docker compose logs`
- [ ] (Optional) SSL/HTTPS configured with certbot

##

## Next: Advanced Setup

See these guides for more:

- **Full Docker Setup**: `DOCKER_UBUNTU_SETUP.md`
- **Detailed Deployment**: `DIGITALOCEAN_DEPLOYMENT_GUIDE.md`
- **Troubleshooting**: `DIGITALOCEAN_DEPLOYMENT_GUIDE.md#troubleshooting`

##

## File Reference

| File | Purpose |
|------|---------|
| `docker-setup.sh` | Automated setup script (run this first) |
| `Dockerfile` | Backend container definition |
| `Dockerfile.frontend` | Frontend container definition |
| `docker-compose.yml` | Multi-container orchestration |
| `.env` | Configuration variables |
| `deploy/nginx.conf` | Reverse proxy routing |
| `requirements.txt` | Python dependencies |
| `firstperson/package.json` | Node.js dependencies |

##

## Key URLs

- GitHub: <https://github.com/taurinrobinson-wq/saoriverse-console>
- DigitalOcean IP: 161.35.227.49
- Frontend: <http://161.35.227.49:3000>
- API: <http://161.35.227.49:8000>

##

**Total setup time**: ~5 minutes
**Complexity**: Easy (just run the script!)
**Risk level**: Very low

##

💡 **Pro Tip**: Bookmark `docker compose logs -f` as your best friend for debugging!

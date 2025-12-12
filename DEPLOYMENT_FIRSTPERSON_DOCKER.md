# FirstPerson.Chat Deployment Guide - DigitalOcean

## Quick Answer: Same Droplet or New Droplet?

**You can use the SAME droplet.** Both `velinor.firstperson.chat` and `firstperson.chat` can run on one machine using Docker containers with a shared nginx reverse proxy.

---

## Architecture Overview

```
Internet (HTTPS)
    |
    v
Nginx (Port 80/443) - Single entry point
    |
    +---> velinor.firstperson.chat  → Container (velinor:8000)
    |
    +---> firstperson.chat           → Container (firstperson:8000 & :3001)
```

---

## Step 1: Access Your DigitalOcean Droplet

**IP Address:** `161.35.227.49`

Option A - SSH (if keys configured):
```bash
ssh root@161.35.227.49
```

Option B - DigitalOcean Console (Recommended for first-time setup):
1. Go to DigitalOcean Dashboard
2. Click your droplet
3. Click "Console" button
4. This opens a browser-based terminal

---

## Step 2: Run the Automated Deployment Script

Copy and paste this into your droplet console:

```bash
bash <(curl -s https://raw.githubusercontent.com/taurinrobinson-wq/saoriverse-console/main/deploy.sh)
```

**OR** run the script manually:

```bash
cd /root/saoriverse-console
git pull origin main
bash deploy.sh
```

---

## Step 3: Update DNS Records

Point these domains to your droplet at `161.35.227.49`:

```
firstperson.chat       A  161.35.227.49
www.firstperson.chat   A  161.35.227.49
velinor.firstperson.chat  A  161.35.227.49  (should already exist)
```

**Where to update DNS:**
- Wherever your domain registrar is (GoDaddy, Namecheap, etc.)
- Or in DigitalOcean's DNS dashboard if using their nameservers

Wait 5-15 minutes for DNS to propagate before testing.

---

## Step 4: Set Up SSL Certificates for firstperson.chat

The deployment script will try to auto-generate SSL certificates. If it fails or you want to do it manually:

```bash
certbot certonly --standalone \
  -d firstperson.chat \
  -d www.firstperson.chat \
  -m your-email@example.com \
  --agree-tos
```

Your certificates will be at: `/etc/letsencrypt/live/firstperson.chat/`

---

## Step 5: Deploy with Docker Compose

If you ran the automated script above, this is already done! Otherwise, run manually:

```bash
cd /root/saoriverse-console
docker-compose -f docker-compose.prod.all.yml up -d
```

---

## Step 6: Verify Services are Running

```bash
# Check running containers
docker ps

# Test FirstPerson backend
curl -s https://firstperson.chat/health

# Test FirstPerson frontend
curl -s https://firstperson.chat/

# Test Velinor
curl -s https://velinor.firstperson.chat/health

# View all logs
docker-compose -f docker-compose.prod.all.yml logs -f
```

---

## Environment Variables for FirstPerson

Create/update `.env` in the project root:

```bash
# Backend configuration
BACKEND_URL=https://firstperson.chat
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Frontend configuration
NEXT_PUBLIC_API_URL=https://firstperson.chat/api
NEXT_PUBLIC_BACKEND_URL=https://firstperson.chat
```

Add to docker-compose to pass these to containers:

```yaml
firstperson:
  environment:
    - BACKEND_URL=https://firstperson.chat
    - SUPABASE_URL=${SUPABASE_URL}
    - SUPABASE_KEY=${SUPABASE_KEY}
```

---

## Troubleshooting

### Container not starting?
```bash
docker-compose -f docker-compose.prod.all.yml logs firstperson
```

### Port already in use?
```bash
# Kill the old container
docker stop firstperson_prod
docker rm firstperson_prod

# Then restart
docker-compose -f docker-compose.prod.all.yml up -d firstperson
```

### SSL certificate issues?
```bash
# Check certificate status
certbot certificates

# Renew if needed
certbot renew --dry-run
```

### Clear cache and rebuild
```bash
docker-compose -f docker-compose.prod.all.yml down
docker system prune -a
docker-compose -f docker-compose.prod.all.yml up -d --build
```

---

## File Structure for Deployment

Make sure these files are in your repo root:
- `Dockerfile` (for Velinor)
- `Dockerfile.firstperson` (for FirstPerson) ✓ Just created
- `docker-compose.prod.all.yml` ✓ Just created
- `nginx.prod.firstperson.conf` ✓ Just created
- `entrypoint.firstperson.sh` ✓ Just created
- `requirements.txt` (Python deps)
- `firstperson_backend.py`
- `firstperson-web/` (Next.js frontend)

---

## Useful Commands

```bash
# View logs
docker-compose -f docker-compose.prod.all.yml logs -f firstperson
docker-compose -f docker-compose.prod.all.yml logs -f velinor
docker-compose -f docker-compose.prod.all.yml logs -f nginx-ssl

# Restart services
docker-compose -f docker-compose.prod.all.yml restart firstperson
docker-compose -f docker-compose.prod.all.yml restart nginx-ssl

# Execute commands in container
docker exec firstperson_prod python -c "import firstperson_backend; print('OK')"

# Stop all
docker-compose -f docker-compose.prod.all.yml down

# Remove volumes (clean slate)
docker-compose -f docker-compose.prod.all.yml down -v
```

---

## Cost Considerations

- **Same Droplet**: Shared resources, lower cost (~$40-60/month for a decent droplet)
- **Separate Droplet**: More resources, higher cost (~$40-60 each, so $80-120/month total)

**Recommendation**: Start with the same droplet. If you need more resources, upgrade the droplet size or split later.

---

## Next Steps

1. ✅ Docker files created
2. ✅ Deployment script created (`deploy.sh`)
3. **ACTION: Update DNS** to point to 161.35.227.49
4. **ACTION: Run the deployment script** in your droplet console
5. **ACTION: Wait for SSL certificate generation** (5-10 minutes)
6. **ACTION: Test endpoints** once DNS propagates (5-15 minutes)

---

## Quick Reference: Common Commands on Your Droplet

```bash
# View all running containers
docker ps

# View logs for a service
docker-compose -f docker-compose.prod.all.yml logs -f firstperson
docker-compose -f docker-compose.prod.all.yml logs -f velinor
docker-compose -f docker-compose.prod.all.yml logs -f nginx-ssl

# Restart a service
docker-compose -f docker-compose.prod.all.yml restart firstperson

# Rebuild and deploy (if you update code)
git pull origin main
docker-compose -f docker-compose.prod.all.yml down
docker-compose -f docker-compose.prod.all.yml up -d --build

# Check SSL certificate status
certbot certificates

# Renew SSL certificates (runs automatically, but manual if needed)
certbot renew --dry-run
certbot renew
```

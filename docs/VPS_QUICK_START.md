# 🚀 Velinor VPS Quick Start

Copy-paste commands to get Velinor running on DigitalOcean.
##

## 1️⃣ Local: Generate SSH Key (One-Time)

```bash
ssh-keygen -t ed25519 -f ~/.ssh/velinor -C "velinor@firstperson"
```



Save the public key output - you'll paste it into DigitalOcean.
##

## 2️⃣ DigitalOcean: Create Droplet

**Dashboard**: Create → Droplets

- **Image**: Ubuntu 22.04 LTS
- **Plan**: Basic, $6/month
- **Region**: Pick your region
- **SSH Key**: Paste from Step 1
- **Hostname**: `velinor-server`

**📝 Save the Droplet IP when it's created** (e.g., `123.45.67.89`)
##

## 3️⃣ Namecheap: Add DNS Record

**firstperson.chat → Advanced DNS**

Add A Record:
- **Host**: `velinor`
- **Value**: Your Droplet IP
- **TTL**: 30 min

Click **Save** and wait 5-10 minutes.
##

## 4️⃣ VPS: Run Setup Script

```bash
ssh root@YOUR_DROPLET_IP
```



Replace `YOUR_DROPLET_IP` with your actual IP.

Then copy-paste this entire block:

```bash
#!/bin/bash
set -e

# Update system
apt-get update && apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Install Docker Compose
apt-get install -y docker-compose-plugin

# Install certbot for SSL
apt-get install -y certbot python3-certbot-nginx

# Create deployment directory
mkdir -p /opt/velinor
cd /opt/velinor

# Clone repo (replace with your repo URL)
git clone https://github.com/YOUR_USERNAME/saoriverse-console.git .

# Build and start
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# Get SSL certificate
certbot certonly --standalone \
  -d velinor.firstperson.chat \
  --email your-email@example.com \
  --agree-tos \
  --non-interactive

# Restart nginx with SSL
docker compose -f docker-compose.prod.yml restart nginx-ssl

echo "✅ Velinor is live at https://velinor.firstperson.chat"
```


##

## 5️⃣ Test It

```bash
curl https://velinor.firstperson.chat
```



Or visit: **https://velinor.firstperson.chat** in your browser
##

## 6️⃣ Auto-Deploy (Optional)

To deploy automatically on `git push main`:

### A. Create deploy key on VPS:

```bash
ssh root@YOUR_DROPLET_IP
ssh-keygen -t ed25519 -f /root/.ssh/velinor_deploy -C "velinor-deploy" -N ""
cat /root/.ssh/velinor_deploy.pub
```



Copy the output.

### B. Add to GitHub:

**Repo → Settings → Deploy Keys → Add deploy key**
- **Title**: `Velinor VPS Deploy`
- **Key**: Paste from above
- ✅ **Allow write access**

### C. Create deploy script on VPS:

```bash
ssh root@YOUR_DROPLET_IP

cat > /opt/velinor/deploy.sh << 'EOF'
#!/bin/bash
set -e

echo "[$(date)] Starting Velinor deployment..."
cd /opt/velinor
git pull origin main
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

sleep 10

if docker compose -f docker-compose.prod.yml ps | grep -q "velinor_prod.*running"; then
  echo "[$(date)] ✅ Deployment successful!"
else
  echo "[$(date)] ❌ Deployment failed!"
  exit 1
fi
EOF

chmod +x /opt/velinor/deploy.sh
```



### D. Add GitHub Secrets:

**Repo → Settings → Secrets and variables → Actions**

Add two secrets:
- **VPS_HOST**: Your Droplet IP (e.g., `123.45.67.89`)
- **VPS_SSH_KEY**: Content of `/root/.ssh/velinor_deploy` (the **private** key)

The `.github/workflows/deploy.yml` file is already in your repo and will auto-trigger on push! 🚀
##

## 📊 Check Status

```bash
ssh root@YOUR_DROPLET_IP
docker compose -f docker-compose.prod.yml ps
```


##

## 🆘 Troubleshooting

**Can't SSH**: Wait 30 seconds after droplet creation, or check SSH key name matches

**DNS not resolving**: Wait 10 minutes, then run `nslookup velinor.firstperson.chat`

**Site shows nginx error**: Check containers are running with command above, or view logs:

```bash
docker compose -f docker-compose.prod.yml logs
```



**SSL certificate issue**:

```bash
ls /etc/letsencrypt/live/velinor.firstperson.chat/
```



If empty, domain name might be wrong - verify DNS is working first.
##

**Total time**: ~15 minutes ⏱️
**Total cost**: $6/month 💰
**Reliability**: 99.9% uptime ✅

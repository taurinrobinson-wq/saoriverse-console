#!/bin/bash
set -e

echo "================================"
echo "FirstPerson + Velinor Setup"
echo "DigitalOcean Deployment"
echo "================================"

# Update system
echo ""
echo "Step 1: Updating system packages..."
apt-get update && apt-get upgrade -y

# Install Docker
echo ""
echo "Step 2: Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    bash get-docker.sh
    rm get-docker.sh
else
    echo "Docker already installed"
fi

# Install Docker Compose
echo ""
echo "Step 3: Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
else
    echo "Docker Compose already installed"
fi

# Clone/update repo
echo ""
echo "Step 4: Cloning/Updating repository..."
if [ ! -d "/root/saoriverse-console" ]; then
    cd /root
    git clone https://github.com/taurinrobinson-wq/saoriverse-console.git
else
    cd /root/saoriverse-console
    git pull origin main
fi

cd /root/saoriverse-console

# Install Certbot for SSL
echo ""
echo "Step 5: Installing Certbot for SSL certificates..."
apt-get install -y certbot

# Generate SSL certificates for firstperson.chat
echo ""
echo "Step 6: Setting up SSL certificates for firstperson.chat..."
echo "NOTE: Make sure your DNS is pointing to 161.35.227.49 first!"
echo ""

# Check if certificate already exists
if [ ! -f "/etc/letsencrypt/live/firstperson.chat/fullchain.pem" ]; then
    echo "Please ensure your DNS records point to 161.35.227.49:"
    echo "  - firstperson.chat A 161.35.227.49"
    echo "  - www.firstperson.chat A 161.35.227.49"
    echo ""
    read -p "Press ENTER once DNS is set up, or wait 60 seconds..."
    
    certbot certonly --standalone \
      -d firstperson.chat \
      -d www.firstperson.chat \
      -m admin@firstperson.chat \
      --agree-tos \
      --non-interactive \
      || echo "Certificate generation failed - you may need to generate manually later"
else
    echo "SSL certificate for firstperson.chat already exists"
fi

# Verify Velinor certificate exists
echo ""
echo "Step 7: Checking Velinor SSL certificate..."
if [ ! -f "/etc/letsencrypt/live/velinor.firstperson.chat/fullchain.pem" ]; then
    echo "WARNING: Velinor certificate not found. It should exist from previous setup."
else
    echo "✓ Velinor certificate found"
fi

# Create logs directory
echo ""
echo "Step 8: Creating log directories..."
mkdir -p /root/saoriverse-console/logs/velinor
mkdir -p /root/saoriverse-console/logs/firstperson

# Deploy with Docker Compose
echo ""
echo "Step 9: Starting Docker containers..."
docker-compose -f docker-compose.prod.all.yml down 2>/dev/null || true
docker-compose -f docker-compose.prod.all.yml up -d

# Wait for services to start
echo ""
echo "Step 10: Waiting for services to start (30 seconds)..."
sleep 30

# Verify services
echo ""
echo "Step 11: Verifying services..."
echo ""

if docker ps | grep -q "velinor_prod"; then
    echo "✓ Velinor container is running"
else
    echo "✗ Velinor container failed to start"
fi

if docker ps | grep -q "firstperson_prod"; then
    echo "✓ FirstPerson container is running"
else
    echo "✗ FirstPerson container failed to start"
fi

if docker ps | grep -q "nginx_ssl_proxy"; then
    echo "✓ Nginx container is running"
else
    echo "✗ Nginx container failed to start"
fi

# Show status
echo ""
echo "================================"
echo "Deployment Status"
echo "================================"
echo ""
docker ps --format "table {{.Names}}\t{{.Status}}"

echo ""
echo "================================"
echo "Next Steps"
echo "================================"
echo ""
echo "1. Update DNS if not already done:"
echo "   firstperson.chat A 161.35.227.49"
echo "   www.firstperson.chat A 161.35.227.49"
echo ""
echo "2. Test services:"
echo "   curl https://firstperson.chat/health"
echo "   curl https://velinor.firstperson.chat/health"
echo ""
echo "3. View logs:"
echo "   docker-compose -f docker-compose.prod.all.yml logs -f"
echo ""
echo "4. Configuration:"
echo "   - Edit .env for environment variables"
echo "   - Check docker-compose.prod.all.yml for service config"
echo ""

echo "✓ Setup complete!"

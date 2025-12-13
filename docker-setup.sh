#!/bin/bash

# SaoriVerse Console - Docker Deployment Quick Start
# This script sets up Docker and deploys to your DigitalOcean droplet

set -e

echo "========================================"
echo "SaoriVerse Console - Docker Setup"
echo "========================================"
echo ""

# Step 1: Install Docker
echo "Step 1: Installing Docker..."
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Installing..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    newgrp docker
else
    echo "✓ Docker already installed: $(docker --version)"
fi

# Step 2: Install Docker Compose
echo ""
echo "Step 2: Installing Docker Compose..."
if ! docker compose version &> /dev/null; then
    echo "Docker Compose not found. Installing..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    echo "✓ Docker Compose already installed: $(docker compose version)"
fi

# Step 3: Clone repository (if not already present)
echo ""
echo "Step 3: Cloning repository..."
if [ ! -d "saoriverse-console" ]; then
    git clone https://github.com/taurinrobinson-wq/saoriverse-console.git
    cd saoriverse-console
else
    echo "✓ Repository already exists"
    cd saoriverse-console
fi

# Step 4: Create .env file
echo ""
echo "Step 4: Creating environment file..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_URL=http://161.35.227.49:8000

# Frontend Configuration
FRONTEND_URL=http://161.35.227.49

# Database Configuration
DATABASE_URL=sqlite:///./data_local/app.db

# Environment
ENV=production
EOF
    echo "✓ Created .env file"
    echo "⚠️  Edit .env file with your specific settings:"
    echo "    nano .env"
else
    echo "✓ .env file already exists"
fi

# Step 5: Build Docker images
echo ""
echo "Step 5: Building Docker images..."
echo "This may take a few minutes..."
docker compose build --no-cache

# Step 6: Start containers
echo ""
echo "Step 6: Starting containers..."
docker compose up -d

# Step 7: Wait for containers to be healthy
echo ""
echo "Step 7: Waiting for services to start..."
sleep 10

# Step 8: Verify deployment
echo ""
echo "Step 8: Verifying deployment..."
echo ""

# Check containers
echo "Running containers:"
docker compose ps
echo ""

# Test backend
echo "Testing API backend..."
if curl -f http://localhost:8000/health 2>/dev/null; then
    echo "✓ Backend API is responding"
else
    echo "⚠️  Backend API not responding yet (give it a moment)"
fi

# Test frontend
echo ""
echo "Testing frontend..."
if curl -f http://localhost:3000 2>/dev/null > /dev/null; then
    echo "✓ Frontend is responding"
else
    echo "⚠️  Frontend not responding yet (give it a moment)"
fi

# Summary
echo ""
echo "========================================"
echo "✓ Setup Complete!"
echo "========================================"
echo ""
echo "Your application is now running on:"
echo ""
echo "Frontend:  http://161.35.227.49:3000"
echo "API:       http://161.35.227.49:8000"
echo "Nginx:     http://161.35.227.49:80"
echo ""
echo "Useful commands:"
echo "  docker compose ps              - Show running containers"
echo "  docker compose logs -f         - Follow all logs"
echo "  docker compose logs -f backend - Follow backend logs"
echo "  docker compose stop            - Stop all services"
echo "  docker compose down            - Remove all services"
echo ""
echo "Next steps:"
echo "1. Update .env with your configuration (if needed)"
echo "2. Check logs: docker compose logs -f"
echo "3. Test endpoints: curl http://localhost:8000/health"
echo "4. Visit your app in browser"
echo ""

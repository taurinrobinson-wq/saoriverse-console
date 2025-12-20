#!/bin/sh
# Bootstrap script to run on a fresh DigitalOcean droplet (Ubuntu 22.04+)
# Usage: run as root or a sudo-capable user
set -e
if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
  echo "Usage: DOMAIN=velinor.firstperson.chat EMAIL=you@domain.com $0"
  exit 1
fi

# Update and install dependencies
apt-get update
apt-get -y upgrade
apt-get install -y ca-certificates curl gnupg lsb-release git

# Install Docker
if ! command -v docker >/dev/null 2>&1; then
  mkdir -p /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
  apt-get update
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
fi

# Create deploy user (optional) and set up directory
APP_DIR=/opt/saoriverse-console
if [ ! -d "$APP_DIR" ]; then
  mkdir -p "$APP_DIR"
  chown "$SUDO_USER:$SUDO_USER" "$APP_DIR" || true
fi

# Clone the repo into APP_DIR if empty
if [ -z "$(ls -A "$APP_DIR")" ]; then
  echo "Cloning repository into $APP_DIR"
  git clone https://github.com/taurinrobinson-wq/saoriverse-console.git "$APP_DIR"
fi

cd "$APP_DIR"
# Ensure scripts are executable
chmod +x ./scripts/init-letsencrypt.sh || true

# Start the stack (nginx and velinor will start, certbot container runs renew loop)
docker compose -f docker-compose.prod.yml up -d --build

# Run certbot once via the helper to obtain certificates
DOMAIN="$DOMAIN" EMAIL="$EMAIL" ./scripts/init-letsencrypt.sh

# Reload nginx to pick up new certs
docker compose -f docker-compose.prod.yml exec nginx-ssl nginx -s reload || true

echo "Bootstrap complete. Visit https://$DOMAIN when DNS points to this droplet."
#!/bin/sh
# Usage: DOMAIN=velinor.firstperson.chat EMAIL=you@example.com ./scripts/init-letsencrypt.sh
set -e
if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
  echo "Usage: DOMAIN=velinor.firstperson.chat EMAIL=you@example.com $0"
  exit 1
fi
# Run a one-shot certbot to obtain certificates into the compose volume.
# Requires Docker Engine on the host and that DNS for $DOMAIN points to this host.

docker compose -f docker-compose.prod.yml run --rm \
  --entrypoint "certbot" certbot certonly --webroot -w /var/www/certbot \
  -d "$DOMAIN" --agree-tos --no-eff-email --email "$EMAIL"

echo "Certificate request complete. Start the nginx proxy with:\n  docker compose -f docker-compose.prod.yml up -d nginx-ssl velinor certbot\nThen check logs: docker compose -f docker-compose.prod.yml logs -f nginx-ssl" 

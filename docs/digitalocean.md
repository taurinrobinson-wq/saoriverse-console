DigitalOcean quickstart for `velinor.firstperson.chat`

This guide shows how to provision a droplet, bootstrap it, and deploy the `saoriverse-console` compose stack.

Prerequisites
- `doctl` configured locally (`doctl auth init`) or use the DigitalOcean control panel.
- An SSH public key added to your DigitalOcean account (view fingerprints with `doctl compute ssh-key list`).

1) Create a droplet with `doctl` (replace region/size/ssh-key as needed)

```bash
DROPLET_NAME=velinor-do
REGION=nyc3
SIZE=s-1vcpu-1gb
IMAGE=ubuntu-22-04-x64
SSH_KEY_FINGERPRINT="your-ssh-key-fingerprint"

doctl compute droplet create "$DROPLET_NAME" \
  --region "$REGION" --size "$SIZE" --image "$IMAGE" \
  --ssh-keys "$SSH_KEY_FINGERPRINT" --wait --format ID,Name,PublicIPv4
```

2) SSH to the droplet and run the bootstrap script

```bash
# from your local machine
DROPLET_IP=203.0.113.10   # replace with droplet IP from the previous command
ssh root@$DROPLET_IP
# on the droplet, inside $HOME
curl -fsSL https://raw.githubusercontent.com/taurinrobinson-wq/saoriverse-console/main/scripts/bootstrap-droplet.sh -o /tmp/bootstrap-droplet.sh
chmod +x /tmp/bootstrap-droplet.sh
# run with your domain/email
DOMAIN=velinor.firstperson.chat EMAIL=you@domain.com /tmp/bootstrap-droplet.sh
```

3) Point DNS
- Create an `A` record for `velinor.firstperson.chat` pointing to the droplet public IP.
- Wait for DNS propagation and then visit `https://velinor.firstperson.chat`.

Notes
- The bootstrap script installs Docker and `docker compose` plugin, clones the repo into `/opt/saoriverse-console`, starts the stack, then runs the included `scripts/init-letsencrypt.sh` to obtain certs into the Docker volume.
- If you prefer to let GitHub Actions deploy, set the SSH secrets in the repo and use the existing `deploy.yml` workflow.

Troubleshooting
- If certbot fails, inspect logs:
  ```bash
  docker compose -f docker-compose.prod.yml logs certbot
  docker compose -f docker-compose.prod.yml logs nginx-ssl
  ```
- Ensure ports 80 and 443 are open in your droplet firewall/security group.

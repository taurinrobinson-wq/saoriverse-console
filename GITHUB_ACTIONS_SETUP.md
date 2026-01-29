# GitHub Actions Deployment Setup for Velinor

This document walks you through setting up automatic Docker builds and deployments to your droplet using GitHub Actions.

## Prerequisites

1. **Docker Hub Account** (free)
   - Sign up at https://hub.docker.com
   - Create a personal access token (Settings → Security → Personal access tokens)

2. **SSH Access to Droplet** (161.35.227.49)
   - You already have this, but make sure you have your private SSH key locally

3. **GitHub Repository Access**
   - You're already here, but make sure you have admin access to the repo

---

## Step 1: Add Secrets to GitHub

Your workflow needs credentials stored securely as "Secrets" in GitHub.

1. Go to your GitHub repo: https://github.com/taurinrobinson-wq/saoriverse-console
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add these four:

### Secret 1: `DOCKER_USERNAME`
- **Value:** Your Docker Hub username
- **Example:** `taurinrobinson`

### Secret 2: `DOCKER_PASSWORD`
- **Value:** Your Docker Hub personal access token (NOT your password)
- **How to get it:**
  - Go to https://hub.docker.com/settings/security
  - Click "New Access Token"
  - Give it a name like "GitHub Actions"
  - Copy the token

### Secret 3: `DEPLOY_HOST`
- **Value:** `161.35.227.49`

### Secret 4: `DEPLOY_USER`
- **Value:** Your SSH username on the droplet
- **Example:** `root` or `ubuntu` (whatever you use to SSH)

### Secret 5: `DEPLOY_KEY`
- **Value:** Your private SSH key (the whole key, exactly as-is)
- **How to get it:**
  - Open your SSH private key file (usually `~/.ssh/id_rsa` on your local machine)
  - Copy the **entire contents** (including `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----`)
  - Paste it into the secret

---

## Step 2: Test the Setup

1. Make a small change to a file in `velinor-web/` (e.g., add a comment)
2. Commit and push to `main`
3. Go to **Actions** tab in your GitHub repo
4. Watch the workflow run:
   - **Build and push** should take 2-3 minutes
   - **Deploy to droplet** should take 1-2 minutes

If it fails, check the logs—they'll tell you exactly what went wrong.

---

## How It Works

**When you push to `main` (changes in `velinor-web/`):**

1. GitHub Actions spins up a Ubuntu machine
2. Checks out your code
3. Builds a Docker image of Velinor
4. Pushes the image to Docker Hub
5. SSHes into your droplet (161.35.227.49)
6. Pulls the new image
7. Stops the old container
8. Starts a new container with the latest image
9. Done!

**No manual steps. No SSH terminal. Just push → deploy.**

---

## Viewing Logs & Debugging

To see what's happening during a deployment:

1. Go to **Actions** tab
2. Click the latest workflow run
3. Click **build-and-deploy**
4. Expand any failed step to see detailed error messages

Common issues:

- **"Permission denied" SSH errors**: Your `DEPLOY_KEY` might be missing the proper newlines. Re-copy it carefully.
- **Docker auth failed**: Check your `DOCKER_PASSWORD` is actually a personal access token, not your password.
- **Connection timeout**: Check that 161.35.227.49 is reachable and your `DEPLOY_USER` is correct.

---

## Future Deployments

From now on, deploying Velinor is as simple as:

```bash
# Make changes locally
git commit -am "Update Velinor dialogue"
git push origin main
```

Then check the **Actions** tab to watch it deploy automatically.

---

## Monitoring Your Droplet

To check if Velinor is running:

```bash
ssh root@161.35.227.49
docker ps  # List running containers
docker logs velinor  # View container logs
```

---

## Scaling Up

Once this works, you can:

1. Add more workflows for other services (draftshift, etc.)
2. Add environment variables (database connections, API keys) as secrets
3. Add notifications (Slack, email) when deployments succeed/fail
4. Create staging deployments (test before production)

But for now, just get Velinor deploying automatically. That's the big win.

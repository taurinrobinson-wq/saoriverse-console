Local testing guide

This repository can be tested locally in two ways:

1) Quick dev (fast iteration with hot reload) — recommended while developing

- Uses `docker-compose.dev.yml` to run:
  - `frontend` (Next dev server) on port 3000
  - `backend` (uvicorn with --reload) on port 8000

PowerShell commands:

```powershell

# from repo root

# start dev services (builds and installs dependencies inside containers)
docker compose -f docker-compose.dev.yml up --build

# Open frontend: http://localhost:3000

# Open API health: http://localhost:8000/health

# to stop:
ctrl+c
```text
```text
```



Notes:
- The backend runs with `--reload` so Python code changes are reflected immediately.
- The frontend runs Next.js in dev mode (fast), so edits to `velinor-web` reflect immediately.
- The compose file mounts the repository into both containers using volumes; this speeds iteration.


2) Production-like test (build the same Docker image Railway will build)

- Uses `docker-compose.yml` which builds the same multi-stage image (the same `Dockerfile`).
- This runs the image exactly like Railway (nginx + Next.js + API started by the entrypoint script).

PowerShell commands:

```powershell


# build and run production-like container (may take longer)
docker compose up --build

# open the site at: http://localhost:8080  (host port 8080 mapped to container port 8000)

# check health endpoint: http://localhost:8080/health

# to stop:
ctrl+c

```text
```




Tips to speed up cycles

- Use `docker-compose.dev.yml` while developing - it's much faster than building the whole image.
- When you need to validate the production image (for example nginx behavior), run the production-like compose before pushing.
- Use `docker compose build --pull --progress=plain` to see detailed build logs.
- Tail logs from containers:

```powershell

# list containers
docker ps

# then tail logs
docker logs -f saoriverse-console-local

# or for dev containers
docker logs -f <container_name>
```




If you want, I can also add a small `Makefile` or PowerShell script to wrap these commands.

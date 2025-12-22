# Emotional OS API (MVP)

Run the minimal FastAPI-based Emotional OS API locally.

Quick start (from `emotional_os_api`):

```
python -m pip install -r requirements.txt
uvicorn app:app --reload
```

Docker build:

```
docker build -t emotional-os-api:latest .
docker run -p 8000:8000 emotional-os-api:latest
```

Endpoints:
- `GET /health` — health check
- `POST /infer` — inference stub; JSON body: `{ "user_id": "u1", "text": "hello" }`

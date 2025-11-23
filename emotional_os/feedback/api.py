from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

from . import store

app = FastAPI(title="Emotional OS Feedback Ingest")


class FeedbackPayload(BaseModel):
    message: str
    rating: int = 0
    metadata: Dict[str, Any] = {}


@app.post("/ingest")
def ingest(feedback: FeedbackPayload):
    try:
        # Convert to simple dict and append
        store.append_feedback(feedback.dict())
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}

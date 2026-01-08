from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from . import store

app = FastAPI(title="Emotional OS Feedback Ingest")


class FeedbackPayload(BaseModel):
    message: str
    rating: int = 0
    metadata: Dict[str, Any] = {}


@app.post("/ingest")
def ingest(feedback: FeedbackPayload):
    try:
        # Convert to simple dict and append (Pydantic v2: use model_dump)
        # `model_dump()` replaces the deprecated `dict()` method.
        store.append_feedback(feedback.model_dump())
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}

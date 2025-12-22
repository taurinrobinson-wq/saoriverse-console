from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os

# Import the canonical adapter implementation
from .engine_adapter import EngineAdapter


app = FastAPI(title="Emotional OS API (MVP)")


class SignalOverrides(BaseModel):
    warmth: Optional[float] = None
    assertiveness: Optional[float] = None
    playfulness: Optional[float] = None
    formality: Optional[float] = None


class DemoRequest(BaseModel):
    text: str
    user_id: str
    signals: Optional[SignalOverrides] = None


class PoeticModulation(BaseModel):
    temperature: float
    imagery: float
    cadence: float


class ResponseBlock(BaseModel):
    text: str
    style: str
    poetic_modulation: PoeticModulation


class StateBlock(BaseModel):
    mood: str
    intensity: float
    traits: dict
    memory: dict


class MetaBlock(BaseModel):
    user_id: str
    timestamp: str
    engine_version: str


class DemoResponse(BaseModel):
    response: ResponseBlock
    state: StateBlock
    meta: MetaBlock


# No global adapter/API key read at import time — evaluate at request time so
# tests can monkeypatch env variables before making requests.




@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/demo", response_model=DemoResponse)
def demo_endpoint(payload: DemoRequest, x_api_key: str = Header(None)):
    api_key = os.environ.get("EMOTIONAL_OS_API_KEY", "dev-key-change-me")
    if x_api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    signal_overrides = payload.signals.dict() if payload.signals else None

    adapter = EngineAdapter(storage_path=os.environ.get("EMOTIONAL_OS_STORAGE_PATH"))
    engine_output = adapter.process(
        text=payload.text,
        user_id=payload.user_id,
        signals=signal_overrides,
    )

    # Normalize and return
    meta_ts = engine_output.get("meta", {}).get("timestamp") or datetime.utcnow().isoformat() + "Z"

    response_block = engine_output.get("response", {})
    state_block = engine_output.get("state", {})
    meta_block = {
        "user_id": payload.user_id,
        "timestamp": meta_ts,
        "engine_version": engine_output.get("meta", {}).get("engine_version", "0.1.0"),
    }

    return DemoResponse(
        response=response_block,
        state=state_block,
        meta=meta_block,
    )


@app.post("/infer")
def infer_stub(payload: dict):
    adapter = EngineAdapter(storage_path=os.environ.get("EMOTIONAL_OS_STORAGE_PATH"))
    text = payload.get("text", "")
    user_id = payload.get("user_id", "anonymous")
    out = adapter.process(text=text, user_id=user_id, signals=None)
    return {"response": out.get("response", {}).get("text", "")}

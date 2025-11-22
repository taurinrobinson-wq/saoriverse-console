from fastapi import FastAPI
from emotional_os.feedback.api import router as feedback_router

app = FastAPI()
app.include_router(feedback_router, prefix="/feedback")

__all__ = ["app"]

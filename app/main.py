from fastapi import FastAPI
from celery import Celery
from app.api import routes
from app.core.config import settings


app = FastAPI(title="Leedflow Names Predictor", version="1.0.0")

app.include_router(routes.router, prefix="/api/v1", tags=["names"])


@app.get("/")
async def root():
    return {"message": "Welcome to the leedflow names predictor!"}

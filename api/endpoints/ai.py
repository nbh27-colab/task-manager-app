from fastapi import APIRouter
from pydantic import BaseModel
from models.time_estimator import estimate_time
from models.ai.llm_chains import classify_task
from database.vectordb import embed_and_store_task


router = APIRouter()


class AIRequest(BaseModel):
    task_id: str
    description: str


@router.post("/classify")
def classify(req: AIRequest):
    category = classify_task(req.description)
    return {"category": category}


@router.post("/estimate-time")
def estimate(req: AIRequest):
    minutes = estimate_time(req.description)
    return {"estimated_minutes": minutes}


@router.post("/embed")
def embed(req: AIRequest):
    embed_and_store_task(req.task_id, req.description)
    return {"message": "embedding stored"}
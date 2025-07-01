from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.handlers.similarity_query import get_search_results, start_search_handler

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1)
    min_score: float = Field(default=0.5, ge=0.0, le=1.0)


@router.post("/")
async def start_similarity_search(request: QueryRequest):
    try:
        return await start_search_handler(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}")
async def get_similarity_search_results(job_id: str):
    try:

        return await get_search_results(job_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.tasks.background_tasks import celery_app, semantic_search

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1)
    min_score: float = Field(default=0.5, ge=0.0, le=1.0)

@router.post("/similarity_search")
async def start_similarity_search(request: QueryRequest):
    try:
        job = semantic_search.delay(request.query, request.top_k, request.min_score)
        return {"job_id": job.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/similarity_search/{job_id}")
async def get_similarity_search_results(job_id: str):
    try:
        result = celery_app.AsyncResult(job_id)

        if result.successful():
            return {
                "status": "completed",
                "result": result.get(),
            }
        elif result.state == "PENDING":
            return {"status": f"Task {job_id} is pending"}
        elif result.state == "FAILURE":
            return {
                "status": f"Task {job_id} failed",
                "error": str(result.info),
            }
        else:
            return {
                "status": f"Task {job_id} not completed yet",
                "state": result.state,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
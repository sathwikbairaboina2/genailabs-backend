from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.tasks.background_tasks import celery_app, semantic_search

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/similarity_search")
async def get_embeddings(request: QueryRequest):
    try:
        job = semantic_search.delay(request.query)
        return {"job_id": job.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/similarity_search/{job_id}")
async def get_job_results(job_id: str):
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

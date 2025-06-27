from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.tasks.background_tasks import celery_app, query_embeddings

router = APIRouter()

class EmbeddingRequest(BaseModel):
    x: str
    y: str

@router.post("/similarity_search")
async def get_predicted_names_vector(request: EmbeddingRequest):
    try:
        job = query_embeddings.delay(request.x, request.y)
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
            return {"status": f"Task {job_id} not completed yet", "state": result.state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, HttpUrl
from app.core.logging import get_logger
from app.handlers.journal import get_all_chunks_by_journal_id
from app.handlers.upsert_embeddings import (
    handle_vector_upsert,
    handle_vector_upsert_status,
)
from app.tasks.background_tasks import celery_app, semantic_search
from app.utils.helpers import (
    get_celery_job_status,
    load_data_from_file_or_url,
)

router = APIRouter()
logger = get_logger(__name__)


class QueryRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1)
    min_score: float = Field(default=0.5, ge=0.0, le=1.0)


@router.put("/upload/")
async def upload_json_file_or_url(
    file: Optional[UploadFile] = File(None),
    file_url: Optional[HttpUrl] = Form(None),
    schema_version: str = Form(...),
):
    try:
        data = await load_data_from_file_or_url(file, file_url)
        logger.info(f"Received data: {data}")
        job = await handle_vector_upsert(data, schema_version)
    except Exception as e:
        logger.exception("Unexpected error during upload processing.")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    return JSONResponse(
        status_code=202,
        content={"detail": "Accepted for processing", "job_id": job["job_id"]},
    )


@router.get("/embeddings/{job_id}")
async def get_embeddings(job_id: str):
    try:
        result = await handle_vector_upsert_status(job_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        result = await get_celery_job_status(job_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{journal_id}")
async def get_journal_chunks(journal_id: str):
    try:
        result = await get_all_chunks_by_journal_id(journal_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# optional end point post ui to impliment small ai agent

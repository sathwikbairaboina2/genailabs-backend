from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import HttpUrl
from app.core.logging import get_logger
from app.handlers.journal import get_all_chunks_by_journal_id
from app.handlers.upsert_embeddings import (
    handle_vector_upsert,
    handle_vector_upsert_status,
)
from app.utils.helpers import load_data_from_file_or_url

router = APIRouter()
logger = get_logger(__name__)


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
        content={
            "detail": "Accepted for processing",
            "job_id": job["job_id"],
        },
        status_code=202,
    )


@router.get("/{job_id}")
async def get_embeddings(job_id: str):
    try:
        result = await handle_vector_upsert_status(job_id)

        logger.info(f"Received data get: {result}")

        return JSONResponse(
            content=result,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/journal/{journal_id}")
async def get_journal_chunks(journal_id: str):
    try:
        result = await get_all_chunks_by_journal_id(journal_id)

        logger.info(f"Received chunks get: {result}")

        return JSONResponse(
            content={"chunks": result},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

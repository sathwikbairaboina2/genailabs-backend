from fastapi import HTTPException
from app.core.logging import get_logger
from pymongo.errors import BulkWriteError
from typing import Dict, List, Optional
import json
import aiohttp
from fastapi import UploadFile, HTTPException
from pydantic import HttpUrl

from celery.result import AsyncResult
from app.tasks.background_tasks import celery_app

logger = get_logger(__name__)


def build_bulk_write_response(inserted_ids, duplicates_skipped):
    return {
        "inserted_count": len(inserted_ids),
        "inserted_ids": [str(_id) for _id in inserted_ids],
        "duplicates_skipped": duplicates_skipped,
    }


def handle_bulk_write_error(error: BulkWriteError, inserted_docs: List[dict]) -> dict:
    errors = error.details.get("writeErrors", [])
    duplicates = [e for e in errors if e.get("code") == 11000]
    others = [e for e in errors if e.get("code") != 11000]

    if others:
        raise HTTPException(
            status_code=500, detail=f"Write error: {others[0].get('errmsg')}"
        )

    # Extract inserted count
    inserted_count = error.details.get("nInserted", 0)
    inserted_ids = [doc["_id"] for doc in inserted_docs[:inserted_count]]

    return build_bulk_write_response(inserted_ids, len(duplicates))


async def parse_uploaded_file(file: UploadFile) -> dict:
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only .json files are allowed.")

    contents = await file.read()
    try:
        return json.loads(contents)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file format.")


async def fetch_json_from_url(file_url: HttpUrl) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=400, detail="Failed to fetch file from URL."
                )
            try:
                return json.loads(await response.text())
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400, detail="Invalid JSON fetched from URL."
                )


async def load_data_from_file_or_url(
    file: Optional[UploadFile], file_url: Optional[HttpUrl]
) -> List[Dict]:
    """
    Validate and load JSON data from uploaded file or URL.
    """
    if not file and not file_url:
        raise HTTPException(
            status_code=400, detail="Either 'file' or 'file_url' must be provided."
        )
    if file and file_url:
        raise HTTPException(
            status_code=400, detail="Provide only one of 'file' or 'file_url'."
        )

    try:
        return await (
            parse_uploaded_file(file) if file else fetch_json_from_url(file_url)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")


def get_celery_job_status(job_id: str) -> dict:

    try:

        result: AsyncResult = celery_app.AsyncResult(job_id)
        logger.info(f"Fetching status for job {result}")
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
        return {
            "status": "error",
            "error": f"Failed to fetch status for job {job_id}: {str(e)}",
        }


def serialize_chunks(data):
    return [{k: v for k, v in doc.items() if k != "_id"} for doc in data]

from typing import List

from fastapi import HTTPException

from app.core.logging import get_logger
from app.modals.journal import Journal
from app.services.chunk_service import add_chunks
from app.services.journal_service import add_journal, update_journal_status
from app.tasks.background_tasks import update_vector_embeddings
from app.utils.helpers import get_celery_job_status
import uuid

logger = get_logger(__name__)


async def handle_vector_upsert(data: List[dict], schema_version: str):
    if not data:
        raise ValueError("Input data cannot be empty")

    metadata = data[0]

    try:
        job = update_vector_embeddings.delay(data)
        journal_id = job.id
        if journal_id:
            journal = Journal(
                source_doc_id=metadata["source_doc_id"],
                publish_year=metadata["publish_year"],
                field=metadata.get("field", "general"),
                chunk_ids=[chunk["id"] for chunk in data],
                status="in-progress",
                schema_version=schema_version,
                journal_id=journal_id,
            )

            journal_id = job.id
            add_journal(journal)
            add_chunks(data, journal_id)

            return {"job_id": job.id}

    except Exception as e:

        raise RuntimeError(f"Failed to upsert vector data for journal '{e}'") from e


async def handle_vector_upsert_status(job_id: str):
    try:
        result = get_celery_job_status(job_id)
        logger.info(f"Fetching status for job {result}")
        if result["status"] == "completed":
            updated_result = update_journal_status(
                journal_id=job_id, status="completed"
            )
            return {
                "status": "completed",
                "chunks_embedeed": updated_result["chunk_ids"],
            }
        else:
            return result

    except Exception as e:
        logger.info(f"Fetching status for job {e}")
        raise HTTPException(status_code=500, detail=str(e))

from typing import List

from app.modals.journal import Journal
from app.services.chunk_service import add_chunks
from app.services.journal_service import add_journal
from app.tasks.background_tasks import update_vector_embeddings
from app.utils.helpers import get_celery_job_status


async def handle_vector_upsert(data: List[dict], schema_version: str):
    if not data:
        raise ValueError("Input data cannot be empty")

    metadata = data[0]

    journal = Journal(
        id=metadata["journal"],
        doi=metadata.get("doi", ""),
        source_doc_id=metadata["source_doc_id"],
        publish_year=metadata["publish_year"],
        field=metadata.get("field", "general"),
        chunk_ids=[chunk["id"] for chunk in data],
        status="in-progress",
        schema_version=schema_version,
    )

    try:
        await add_journal(journal)
        await add_chunks(data)
        job = update_vector_embeddings.delay(data)
        return {"job_id": job.id}
    except Exception as e:

        raise RuntimeError(
            f"Failed to upsert vector data for journal '{journal.id}'"
        ) from e


async def handle_vector_upsert_status(job_id: str):
    # result = await get_celery_job_status(job_id)
    # update_journal_status(journal_id=journal_id, status=result)
    return await get_celery_job_status(job_id)

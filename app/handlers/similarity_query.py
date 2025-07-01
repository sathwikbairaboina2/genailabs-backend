from datetime import datetime
from typing import List
from fastapi import HTTPException
from app.core.logging import get_logger
from app.modals.similarity import QueryLog
from app.schemas.similarity import SimilarityRequest
from app.services.journal_service import update_journal_status
from app.services.similarity_service import add_query_log, update_query_log
from app.tasks.background_tasks import semantic_search
from app.utils.helpers import get_celery_job_status

logger = get_logger(__name__)


async def start_search_handler(request: SimilarityRequest):

    try:
        logger.info(f"Starting similarity search for query: {request.query}")

        job = semantic_search.delay(request.query, request.top_k, request.min_score)
        logger.info(f"Starting similarrerererity search for query: {request.query}")
        job_id = job.id
        querylog = QueryLog(
            query=request.query,
            top_k=request.top_k,
            min_score=request.min_score,
            created_at=datetime.utcnow(),
            _id=job_id,
        )

        add_query_log(querylog)
        return {"job_id": job_id}
    except Exception as e:
        logger.error(f"Failed to start similarity search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def get_search_results(job_id: str):
    try:
        result = get_celery_job_status(job_id)
        if result["status"] == "completed":
            similarity_search_results = result["result"]
            chunk_ids = [item["_id"] for item in similarity_search_results]
            # update_query_log(journal_id=job_id, status="completed", chunk_ids=chunk_ids)
            return {"results": similarity_search_results}
        else:
            return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

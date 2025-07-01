from fastapi import HTTPException
from app.core.logging import get_logger
from app.services.chunk_service import get_chunks_by_journal
from app.utils.helpers import serialize_chunks


logger = get_logger(__name__)


async def get_all_chunks_by_journal_id(journal_id: str):
    try:
        chunks = get_chunks_by_journal(journal_id)
        return serialize_chunks(chunks)
    except Exception as e:
        logger.error(f"Fer journal {e}")
        raise HTTPException(status_code=500, detail=str(e))

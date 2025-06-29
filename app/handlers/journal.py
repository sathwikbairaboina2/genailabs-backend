from fastapi import HTTPException
from app.services.chunk_service import get_chunks_by_ids
from app.services.journal_service import get_journal_by_id


async def get_all_chunks_by_journal_id(journal_id: str):
    try:
        result = await get_journal_by_id(journal_id)
        chunk_ids = result.get("chunk_ids", [])
        chunks = await get_chunks_by_ids(chunk_ids)
        return chunks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

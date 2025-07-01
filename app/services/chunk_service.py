from typing import List

from bson import ObjectId
from app.core.logging import get_logger
from app.core.mongodb import get_db
from app.modals.chunk import Chunk
from app.utils.helpers import build_bulk_write_response, handle_bulk_write_error
from pymongo.collection import Collection
from fastapi import HTTPException

from pymongo.errors import BulkWriteError

db = get_db()
chunk_collection: Collection = db.chunks

logger = get_logger(__name__)


def update_usage_count(chunk_id: str, increment: int = 1):
    try:
        result = chunk_collection.update_one(
            {"_id": chunk_id}, {"$inc": {"usage_count": increment}}
        )
        if result.modified_count == 0:
            raise HTTPException(
                status_code=404, detail="Chunk not found or not updated"
            )
        return {"updated": True, "chunk_id": chunk_id}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update usage count: {str(e)}"
        )


def get_chunks_by_journal(journal_id: str):
    try:
        cursor = chunk_collection.find({"journal_id": journal_id})
        chunks = list(cursor)  # Convert cursor to list of documents (dicts)
        logger.info(
            f"Fetching chunks for journal {journal_id}, Found: {len(chunks)} chunks"
        )
        return chunks
    except Exception as e:
        logger.error(f"Failed to fetch chunks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch chunks: {str(e)}")


def add_chunks(chunks: List[dict], journal_id: str) -> dict:
    try:
        docs = []

        for chunk_data in chunks:
            if "id" in chunk_data:
                chunk_data["chunk_id"] = chunk_data.pop("id")

            chunk_data["journal_id"] = journal_id
            chunk = Chunk(**chunk_data)
            docs.append(chunk.dict())

        result = chunk_collection.insert_many(docs, ordered=False)
        return build_bulk_write_response(result.inserted_ids, 0)

    except BulkWriteError as e:
        return handle_bulk_write_error(e, docs)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"chunks insertion failed: {str(e)}"
        )

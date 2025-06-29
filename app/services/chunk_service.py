from typing import List
from app.core.mongodb import get_db
from app.modals.chunk import Chunk
from app.utils.helpers import build_bulk_write_response, handle_bulk_write_error
from pymongo.collection import Collection
from fastapi import HTTPException

from pymongo.errors import BulkWriteError

db = get_db()
chunk_collection: Collection = db.chunks


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


def get_chunks_by_ids(chunk_ids: List[str]) -> List[Chunk]:
    try:
        docs = chunk_collection.find({"_id": {"$in": chunk_ids}})
        return [Chunk(**doc) for doc in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch chunks: {str(e)}")


def add_chunks(chunks: List[Chunk]) -> dict:
    try:
        docs = [chunk.dict(by_alias=True) for chunk in chunks]
        result = chunk_collection.insert_many(docs, ordered=False)
        return build_bulk_write_response(result.inserted_ids, 0)
    except BulkWriteError as e:
        return handle_bulk_write_error(e, chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insertion failed: {str(e)}")

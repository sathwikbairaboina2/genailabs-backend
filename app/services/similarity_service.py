from typing import List
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from fastapi import HTTPException
from app.core.mongodb import get_db
from app.core.logging import get_logger
from app.modals.similarity import QueryLog

logger = get_logger(__name__)

db = get_db()
query_logs_collection: Collection = db.query_logs


def add_query_log(log: QueryLog):
    try:
        logger.info(f"Inserted QueryL")
        log_dict = log.dict(by_alias=True)
        result = query_logs_collection.insert_one(log_dict)
        logger.info(f"Inserted QueryLog with id: {result.inserted_id}")
        return {"inserted_id": str(result.inserted_id)}
    except PyMongoError as e:
        logger.error(f"Failed to add query log: {e}")
        raise HTTPException(status_code=500, detail="Internal DB error.")


def get_all_logs():
    try:
        logs = list(query_logs_collection.find())
        return logs
    except PyMongoError as e:
        logger.error(f"Failed to retrieve query logs: {e}")
        raise HTTPException(status_code=500, detail="Internal DB error.")


def update_query_log(job_id: str, status: dict, chunk_ids: List[str]):

    try:
        update_fields = {"status": status, "chunk_ids": chunk_ids}
        update_query = {"$set": update_fields}

        result = query_logs_collection.update_one({"_id": job_id}, update_query)

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Journal not found.")

        return "result"
    except PyMongoError as e:
        logger.error(f"Failed to update journal {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal DB error.")

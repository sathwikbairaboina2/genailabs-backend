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
        result = query_logs_collection.insert_one(log)
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

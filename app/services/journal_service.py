from pymongo.collection import Collection
from pymongo.errors import PyMongoError, DuplicateKeyError
from fastapi import HTTPException
from app.core.mongodb import get_db
from app.core.logging import get_logger
from app.modals.journal import Journal

logger = get_logger(__name__)

db = get_db()
journals_collection: Collection = db.journals


def add_journal(journal: Journal):
    try:
        return journals_collection.insert_one(journal)
    except DuplicateKeyError:
        logger.warning(f"Journal with id {journal['_id']} already exists.")
        raise HTTPException(status_code=409, detail="Journal already exists.")
    except PyMongoError as e:
        logger.error(f"Failed to add journal: {e}")
        raise HTTPException(status_code=500, detail="Internal DB error.")


def get_journal_by_id(journal_id: str):

    try:
        journal = journals_collection.find_one({"_id": journal_id})
        if not journal:
            raise HTTPException(status_code=404, detail="Journal not found.")
        return journal
    except PyMongoError as e:
        logger.error(f"Error fetching journal {journal_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal DB error.")


def update_journal_status(journal_id: str, status: dict):

    try:
        update_fields = {"status": status}
        update_query = {"$set": update_fields}

        result = journals_collection.update_one({"_id": journal_id}, update_query)

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Journal not found.")

        return result
    except PyMongoError as e:
        logger.error(f"Failed to update journal {journal_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal DB error.")

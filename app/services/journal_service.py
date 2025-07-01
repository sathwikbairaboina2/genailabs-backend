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
        journal_dict = journal.dict()
        logger.info
        return journals_collection.insert_one(journal_dict)
    except DuplicateKeyError:
        logger.warning(f"Journal with id {journal['_id']} already exists.")
        raise HTTPException(status_code=409, detail="Journal already exists.")
    except PyMongoError as e:
        logger.error(f"Failed to add journal: {e}")
        raise HTTPException(status_code=500, detail="Internal DB error.")


def get_journal_by_id(journal_id: str):

    try:
        journal = journals_collection.find_one({"journal_id": journal_id})
        logger.info(f"Fetchinjournal_id {journal}")
        if not journal:
            raise HTTPException(status_code=404, detail="Journal not found.")
        return journal
    except PyMongoError as e:
        logger.error(f"Error fetching journal {journal_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal DB error.")


def update_journal_status(journal_id: str, status: str, result: dict = None):

    try:
        logger.info(f"Updating journal {journal_id} with status: {status}")
        db_result = journals_collection.update_one(
            {"journal_id": journal_id}, {"$set": {"status": status}}
        )
        if db_result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Journal not found.")
        logger.info(f"Updated jrnl {journal_id}  {db_result}")

        return get_journal_by_id(journal_id)

    except PyMongoError as e:
        logger.error(f"Failed to update journal {journal_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal DB error.")

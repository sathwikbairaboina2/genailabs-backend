from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from fastapi import HTTPException
from app.core.mongodb import get_db
from app.core.logging import get_logger
from app.modals.ai_conversation import AIConversation

logger = get_logger(__name__)

db = get_db()
ai_conversations_collection: Collection = db.ai_conversations


def add_conversation(convo: AIConversation):
    """
    Add a new AI conversation to the database.
    """
    try:
        result = ai_conversations_collection.insert_one(convo)
        logger.info(f"Inserted AIConversation with id: {result.inserted_id}")
        return {"inserted_id": str(result.inserted_id)}
    except PyMongoError as e:
        logger.error(f"Failed to add conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal DB error.")


def get_all_history_sorted_by_date():
    """
    Retrieve all conversations sorted by 'created_at' in descending order.
    """
    try:
        conversations = list(ai_conversations_collection.find().sort("created_at", -1))
        return conversations
    except PyMongoError as e:
        logger.error(f"Failed to retrieve AI conversation history: {e}")
        raise HTTPException(status_code=500, detail="Internal DB error.")

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.core.config import settings
from app.core.logging import get_logger
from pymongo import ASCENDING, DESCENDING
from pymongo.collection import Collection


logger = get_logger(__name__)

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB_NAME]
chunk_collection: Collection = db.chunks


def get_db():
    return db


def create_chunk_indexes():
    chunk_collection.create_index([("journal", ASCENDING)])
    chunk_collection.create_index([("usage_count", DESCENDING)])


def test_mongo_connection():
    try:
        test_client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=3000)
        test_client.server_info()
        logger.info("MongoDB connection successful.")
    except ConnectionFailure as e:
        logger.error("Failed to connect to MongoDB: %s", e)

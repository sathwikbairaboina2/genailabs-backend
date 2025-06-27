import os

from celery import Celery, signals

from app.core.logging import get_logger
logger = get_logger(__name__)


broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

celery_app = Celery("worker", broker=broker_url, backend=result_backend)

@signals.worker_process_init.connect
def on_worker_start(**kwargs):
    logger.info("Celery worker has started and is ready.")

@celery_app.task(name="addembeddings")
def update_embeddings(x, y):
    """Add embeddings to the database."""
    logger.info("Celery task triggered.")
    return "success"
@celery_app.task
def query_embeddings(x, y):
    logger.info("celry task triggered")
    return "sucess"

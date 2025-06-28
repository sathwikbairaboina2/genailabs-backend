import os

from celery import Celery, signals

from app.core.logging import get_logger
from sentence_transformers import SentenceTransformer
logger = get_logger(__name__)


broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

celery_app = Celery("worker", broker=broker_url, backend=result_backend)


model = None
index = None
raw_df = None

@signals.worker_process_init.connect
def on_worker_start(**kwargs):
    logger.info("Celery worker has started and is ready.")
    def setup_model(**kwargs):
    global model, index, raw_df

    model = SentenceTransformer("all-MiniLM-L6-v2")

    with open("app/utils/dataset.json", "r") as f:
        records = json.load(f)

    raw_df = pd.DataFrame(records)

    def combine_fields(record):
        return " | ".join(f"{k}: {v}" for k, v in record.items())

    raw_df["combined_text"] = raw_df.apply(lambda row: combine_fields(row), axis=1)

    texts = raw_df["combined_text"].tolist()
    embeddings = model.encode(texts, convert_to_numpy=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype("float32"))

@celery_app.task(name="addembeddings")
def update_embeddings(x, y):
    """Add embeddings to the database."""
    logger.info("Celery task triggered.")
    return "success"
@celery_app.task
def query_embeddings(x, y):
    logger.info("celry task triggered")
    return "sucess"

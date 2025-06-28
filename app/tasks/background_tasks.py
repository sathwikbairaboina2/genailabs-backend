import json
import os
from celery import Celery, signals
import faiss
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

model = None
index = None
raw_df = None

broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

celery_app = Celery("worker", backend=result_backend, broker=broker_url)

@signals.worker_process_init.connect
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

@celery_app.task
def semantic_search(query: str, top_k: int = 3):
    global model, index, raw_df

    query_vec = model.encode([query], convert_to_numpy=True).astype("float32")
    distances, indices = index.search(query_vec, top_k)

    results = raw_df.iloc[indices[0]].copy()
    results["similarity_score"] = 1 / (1 + distances[0])

    return results.drop(columns=["combined_text"]).to_dict(orient="records")

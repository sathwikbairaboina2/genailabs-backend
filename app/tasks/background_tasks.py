import os
import json
import pandas as pd
from typing import List, Dict, Optional, Any
from celery import Celery, signals
from sentence_transformers import SentenceTransformer
from langchain.docstore.document import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, Range


model = None
vector_store = None
raw_df = None


broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379")
result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379")
qdrant_host = os.environ.get("QDRANT_HOST", "http://qdrant:6333")

celery_app = Celery("worker", backend=result_backend, broker=broker_url)

@signals.worker_process_init.connect
def setup_vector_store(**kwargs):
    global model, vector_store, raw_df

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    sparse_embedder = FastEmbedSparse(model_name="Qdrant/bm25")

    with open("app/utils/dataset.json", "r") as f:
        records = json.load(f)

    raw_df = pd.DataFrame(records)

    documents = [
        Document(
            page_content=row["text"],
            metadata={k: v for k, v in row.items() if k != "text"}
        )
        for row in records if "text" in row
    ]

    vector_store = QdrantVectorStore.from_documents(
        documents=documents,
        embedding=embedder,
        sparse_embedding=sparse_embedder,
        url=qdrant_host,
        collection_name="my_collection",
        prefer_grpc=False,
        force_recreate=True,
        retrieval_mode=RetrievalMode.HYBRID
    )

@celery_app.task
def semantic_search(
    query: str,
    top_k: int = 5,
    min_score: float = 0.5,
    metadata_filter: Optional[Dict[str, Any]] = None
) -> List[Dict]:
    global vector_store

    filter_conditions = []
    if metadata_filter:
        for key, val in metadata_filter.items():
            if isinstance(val, list):
                for v in val:
                    filter_conditions.append(FieldCondition(key=key, match=MatchValue(value=v)))
            elif isinstance(val, dict) and "gte" in val:
                filter_conditions.append(FieldCondition(key=key, range=Range(**val)))
            else:
                filter_conditions.append(FieldCondition(key=key, match=MatchValue(value=val)))

    qdrant_filter = Filter(must=filter_conditions) if filter_conditions else None

    results = vector_store.similarity_search_with_score(query, k=top_k, filter=qdrant_filter)

    filtered = []
    for doc, score in results:
        if score >= min_score:
            filtered.append({
                "similarity_score": round(score, 4),
                **doc.metadata,
                "text": doc.page_content
            })

    return filtered

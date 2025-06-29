import os
import json
import pandas as pd
from typing import List, Dict, Optional, Any
from celery import Celery, signals
from sentence_transformers import SentenceTransformer
from langchain.docstore.document import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, Range
from qdrant_client.http.exceptions import UnexpectedResponse

broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379")
qdrant_host = os.getenv("QDRANT_HOST", "http://qdrant:6333")

celery_app = Celery("worker", backend=result_backend, broker=broker_url)


vector_store = None


@signals.worker_process_init.connect
def init_vector_store(**_):
    global vector_store

    try:
        embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        sparse = FastEmbedSparse(model_name="Qdrant/bm25")

        with open("app/utils/dataset.json") as f:
            data = json.load(f)

        docs = [
            Document(
                page_content=row["text"],
                metadata={k: v for k, v in row.items() if k != "text"},
            )
            for row in data
            if "text" in row
        ]

        vector_store = QdrantVectorStore.from_documents(
            documents=docs,
            embedding=embedder,
            sparse_embedding=sparse,
            url=qdrant_host,
            collection_name="my_collection",
            retrieval_mode=RetrievalMode.HYBRID,
            force_recreate=False,
            prefer_grpc=False,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to initialize vector store: {e}")


@celery_app.task
def semantic_search(
    query: str,
    top_k: int = 5,
    min_score: float = 0.5,
    metadata_filter: Optional[Dict[str, Any]] = None,
) -> List[Dict]:
    global vector_store

    try:
        filters = []
        if metadata_filter:
            for key, val in metadata_filter.items():
                if isinstance(val, list):
                    filters += [
                        FieldCondition(key=key, match=MatchValue(value=v)) for v in val
                    ]
                elif isinstance(val, dict) and "gte" in val:
                    filters.append(FieldCondition(key=key, range=Range(**val)))
                else:
                    filters.append(FieldCondition(key=key, match=MatchValue(value=val)))

        qdrant_filter = Filter(must=filters) if filters else None
        results = vector_store.similarity_search_with_score(
            query, k=top_k, filter=qdrant_filter
        )

        return [
            {
                "similarity_score": round(score, 4),
                "text": doc.page_content,
                **doc.metadata,
            }
            for doc, score in results
            if score >= min_score
        ]
    except Exception as e:
        return [{"error": f"Semantic search failed: {str(e)}"}]


@celery_app.task
def update_vector_embeddings(records: List[Dict[str, Any]]) -> str:
    global vector_store

    collection_name = "my_collection"
    client = vector_store._client

    try:
        """Get existing document IDs"""
        existing_ids = set()
        offset = None
        while True:
            points, next_offset = client.scroll(
                collection_name=collection_name,
                offset=offset,
                limit=1000,
                with_payload=True,
                with_vectors=False,
            )
            if not points:
                break
            for point in points:
                doc_id = point.payload.get("source_doc_id")
                if doc_id:
                    existing_ids.add(doc_id)
            if next_offset is None:
                break
            offset = next_offset

        # filter and prepare docs
        new_docs = []
        docs_to_delete = []
        for record in records:
            doc_id = record.get("source_doc_id")
            if not doc_id or "text" not in record:
                continue
            new_docs.append(
                Document(
                    page_content=record["text"],
                    metadata={k: v for k, v in record.items() if k != "text"},
                )
            )
            if doc_id in existing_ids:
                docs_to_delete.append(doc_id)

        # delete existing docs
        if docs_to_delete:
            try:
                client.delete(
                    collection_name=collection_name,
                    points_selector={"points": docs_to_delete},
                )
            except UnexpectedResponse as ue:
                raise RuntimeError(f"Qdrant deletion failed: {ue}")

        #
        if new_docs:
            vector_store.add_documents(new_docs)
            return f"Upserted {len(new_docs)} documents ({len(docs_to_delete)} replaced, {len(new_docs) - len(docs_to_delete)} new)."

        return "No documents upserted."

    except Exception as e:
        raise RuntimeError(f"Vector embedding update failed: {str(e)}")

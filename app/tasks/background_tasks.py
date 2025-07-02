import os
import json
import uuid
from typing import List, Dict, Optional, Any
from celery import Celery, signals
from langchain.docstore.document import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, Range


def is_valid_uuid(val: str) -> bool:
    try:
        uuid.UUID(str(val))
        return True
    except (ValueError, TypeError):
        return False


from app.core.logging import get_logger

logger = get_logger(__name__)

broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")
qdrant_host = os.environ.get("QDRANT_HOST", "http://localhost:6333")


celery_app = Celery("worker", backend=result_backend, broker=broker_url)


vector_store = None
research_assistant_collection = "genailabs_research_assistant"


@signals.worker_process_init.connect
def setup_vector_store(**kwargs):
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
            collection_name=research_assistant_collection,
            retrieval_mode=RetrievalMode.HYBRID,
            force_recreate=False,
            prefer_grpc=False,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to initialize vector store: {e}")


def semantic_search_with_filters(
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

        logger.info(f"Semantic search results: {results}")

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
def semantic_search(
    query: str,
    top_k: int = 5,
    min_score: float = 0.5,
):
    return semantic_search_with_filters(query, top_k, min_score)


@celery_app.task
def update_vector_embeddings(records: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    global vector_store

    collection_name = research_assistant_collection
    client = vector_store.client
    succeeded_ids = []
    failed_ids = []
    points = []

    try:
        for record in records:
            id = record.get("id")
            text = record.get("text")

            if not id or not text or not is_valid_uuid(id):
                failed_ids.append(id or "MISSING_ID")
                continue

            # Embed vector
            try:
                vector = vector_store._build_vectors([text])[0]
                point = {
                    "id": id,
                    "vector": vector,
                    "payload": {
                        "page_content": text,
                        "source_doc_id": record.get("source_doc_id"),
                        "publish_year": record.get("publish_year"),
                        "field": record.get("field"),
                        "chunk_index": record.get("chunk_index"),
                        "section_heading": record.get("section_heading"),
                        "attributes": record.get("attributes"),
                        "link": record.get("link"),
                    },
                }
                points.append(point)
                succeeded_ids.append(id)
            except Exception as embed_err:
                logger.error(f"Failed embedding for id={id}: {embed_err}")
                failed_ids.append(id)

        if points:
            result = client.upsert(collection_name=collection_name, points=points)

            logger.info(f"Upsert result: {result}")
        else:
            logger.info("No valid documents to upsert.")

        return {"succeeded_ids": succeeded_ids, "failed_ids": failed_ids}

    except Exception as e:
        logger.error(f"Exception during vector embedding update: {e}")
        raise RuntimeError(f"Failed to update vector embeddings: {e}")


def search_vectorstore_by_metadata(doc_ids: List[str]):
    global vector_store
    client = vector_store.client

    results = client.scroll(
        collection_name=research_assistant_collection,
        filter=Filter(must=[FieldCondition(key="id", match=MatchValue(value=doc_ids))]),
    )

    logger.info(f"Search results: {results}")

    return results

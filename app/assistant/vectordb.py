import os
from typing import List, Dict


from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

from typing import List, Dict
from qdrant_client.models import Filter
import numpy as np

from app.core.logging import get_logger
from sentence_transformers import SentenceTransformer

sentences = ["This is an example sentence", "Each sentence is converted"]

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


qdrant_host = os.environ.get("QDRANT_HOST")
client = QdrantClient(host=qdrant_host, port=6333)

research_assistant_collection = "genailabs_research_assistant"

logger = get_logger(__name__)


def search_vectorstore_by_metadata(doc_id: str):
    try:
        logger.info(f"Searching vectorstore for doc_ids: {doc_id}")
        all_records = []
        offset = None
        while True:
            scroll_result = client.scroll(
                collection_name=research_assistant_collection,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="source_doc_id",
                            match=MatchValue(value=doc_id),
                        )
                    ]
                ),
                limit=100,
                offset=offset,
            )
            records, next_page_offset = scroll_result
            all_records.extend(records)
            logger.info(f"Retrieved {len(records)} records, total: {len(all_records)}")
            if not next_page_offset:
                break
            offset = next_page_offset
        logger.info(f"Search results: {all_records}")
        return all_records
    except Exception as e:
        logger.error(f"Metadata search failed for doc_ids {doc_id}: {str(e)}")


def semantic_search(
    query: str,
    top_k: int = 5,
    min_score: float = 0.5,
) -> List[Dict]:
    try:
        vector_query = model.encode(query)
        results = client.search(
            collection_name=research_assistant_collection,
            query_vector=vector_query,
            limit=5,
            with_payload=True,
            score_threshold=0.0,
        )

        logger.info(f"Raw semantic search results: {results}")

        filtered_results = [
            {
                "similarity_score": round(result.score, 4),
                "text": result.payload.get("text", ""),
                **result.payload,
            }
            for result in results
        ]

        logger.info(
            f"Filtered semantic search results (score >= {min_score}): {filtered_results}"
        )

        return filtered_results

    except Exception as e:
        logger.error(f"Semantic search failed for query '{query}': {str(e)}")

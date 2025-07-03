from app.core.logging import get_logger
from app.schemas.agent_state import AgentState

logger = get_logger(__name__)


def context_builder_rag(results):
    if not results:
        logger.warning("Empty result list received by context_builder_rag.")
        return ""

    try:
        context = "\n\n".join(
            f"""### Document ID: {doc.get('source_doc_id', 'N/A')}
Similarity Score: {doc.get('similarity_score', 0):.2f}
Link: {doc.get('link', 'N/A')}/{doc.get('_id', '')}

{doc.get('page_content', '')}"""
            for doc in results
        )
        return context
    except Exception as e:
        logger.error(f"Error building context from results: {e}", exc_info=True)
        return "Error building context from results"


def context_builder_summerizer_rag(results):
    if not results:
        logger.warning("Empty result list received by context_builder_rag.")
        return "No document with given id to summerise"

    try:
        source_doc_id = results[0].payload.get("source_doc_id", "")
        all_text = "\n".join(
            record.payload.get("page_content", "") for record in results
        )
        return f"Document: {source_doc_id}\n{all_text}"
    except Exception as e:
        logger.error(f"Error building context from results: {e}", exc_info=True)
        return "No document with given id to summerise"

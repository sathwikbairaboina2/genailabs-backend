from app.assistant.context_builder import context_builder_rag
from app.core.logging import get_logger
from app.schemas.agent_state import AgentState
from app.tasks.background_tasks import (
    search_vectorstore_by_metadata,
    semantic_search_with_filters,
)

logger = get_logger(__name__)


def retriever_qa_rag(state: AgentState):
    try:
        results = semantic_search_with_filters(state["question"], 5, 0.5)
        logger.info(f"Retrieving for QA: {state}")
        context = context_builder_rag(results)
        return {"context": context}
    except Exception as e:
        logger.error(f"Error in retriever_qa_rag: {e}", exc_info=True)
        return {"context": context_builder_rag(results)}


def retriever_summarizer_rag(state: AgentState):
    try:
        logger.info(f"Retrieving for Summarizer: {state}")
        results = search_vectorstore_by_metadata(state["doc_ids"])
        context = context_builder_rag(results)
        return {"context": context}
    except Exception as e:
        logger.error(f"Error in retriever_summarizer_rag: {e}", exc_info=True)
        return {"context": context_builder_rag(results)}


def retriever_compare_docs_rag(state: AgentState):
    try:
        logger.info(f"Retrieving for Compare: {state}")
        results = search_vectorstore_by_metadata(state["doc_ids"])
        context = context_builder_rag(results)
        return {"context": context}
    except Exception as e:
        logger.error(f"Error in retriever_compare_docs_rag: {e}", exc_info=True)
        return {"context": context_builder_rag(results)}

from app.assistant.context_builder import (
    context_builder_rag,
    context_builder_summerizer_rag,
)
from app.core.logging import get_logger
from app.schemas.agent_state import AgentState
from app.assistant.vectordb import (
    search_vectorstore_by_metadata,
    semantic_search,
)

logger = get_logger(__name__)


def retriever_qa_rag(state: AgentState):
    try:
        results = semantic_search(state["question"], 5, 0.5)
        logger.info(f"Retrieving for QA: {state , results}")
        logger.info(f"Retrieved context: {results}")
        context = context_builder_rag(results)
        return {"context": context}
    except Exception as e:
        logger.error(f"Error in retriever_qa_rag: {e}", exc_info=True)


def retriever_summarizer_rag(state: AgentState):
    try:
        logger.info(f"Retrieving for Summarizer: {state}")
        results = search_vectorstore_by_metadata(state["doc_ids"][0])
        context = context_builder_summerizer_rag(results)
        logger.info(f"Retrieved context: {context,results}")
        return {"context": context}
    except Exception as e:
        logger.error(f"Error in retriever_summarizer_rag: {e}", exc_info=True)


def retriever_compare_docs_rag(state: AgentState):
    try:
        logger.info(f"Retrieving for Compare: {state}")
        doc1 = search_vectorstore_by_metadata(state["doc_ids"][0])
        doc2 = search_vectorstore_by_metadata(state["doc_ids"][1])
        context = context_builder_summerizer_rag(doc1) + context_builder_summerizer_rag(
            doc2
        )
        return {"context": context}
    except Exception as e:
        logger.error(f"Error in retriever_compare_docs_rag: {e}", exc_info=True)

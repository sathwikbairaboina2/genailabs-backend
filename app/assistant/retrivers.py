from app.core.logging import get_logger
from app.schemas.agent_state import AgentState

logger = get_logger(__name__)


def retriever_qa_rag(state: AgentState):
    logger.info(f"Retrieving for QA: {state}")
    return {"context": ["QA context based on " + ", ".join(state["doc_ids"])]}


def retriever_summarizer_rag(state: AgentState):
    logger.info(f"Retrieving for Summarizer: {state}")
    print(f"Retrieving for Summarizer: {state['doc_ids']}")
    return {"context": ["Summarization context for " + ", ".join(state["doc_ids"])]}


def retriever_compare_docs_rag(state: AgentState):
    logger.info(f"Retrieving for Compare: {state}")
    print(f"Retrieving for Compare: {state['doc_ids']}")
    return {"context": ["Comparison context for " + ", ".join(state["doc_ids"])]}

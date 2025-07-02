from app.assistant.context_builder import context_builder_rag
from app.core.logging import get_logger
from app.schemas.agent_state import AgentState

logger = get_logger(__name__)

results = [
    {
        "similarity_score": 0.8333,
        "text": "Velvet bean–Mucuna pruriens var. utilis, also known as mucuna—is a twining annual leguminous vine...",
        "_id": "550e8400-e29b-41d4-a716-446655440001",
        "_collection_name": "genailabs_research_assistant",
        "link": "https://cgspace.cgiar.org/server/api/core/bitstreams/68bfaec0-8d32-4567-9133-7df9ec7f3e23/content",
    },
    {
        "similarity_score": 0.75,
        "text": "Mucuna is susceptible to fungal infections and pest attacks. Integrated pest management practices are recommended...",
        "_id": "550e8400-e29b-41d4-a716-446655440005",
        "_collection_name": "genailabs_research_assistant",
        "link": "https://cgspace.cgiar.org/server/api/core/bitstreams/68bfaec0-8d32-4567-9133-7df9ec7f3e23/content",
    },
]


def retriever_qa_rag(state: AgentState):
    try:
        logger.info(f"Retrieving for QA: {state}")
        context = context_builder_rag(results)
        return {"context": context}
    except Exception as e:
        logger.error(f"Error in retriever_qa_rag: {e}", exc_info=True)
        return {"context": context_builder_rag(results)}


def retriever_summarizer_rag(state: AgentState):
    try:
        logger.info(f"Retrieving for Summarizer: {state}")
        print(f"Retrieving for Summarizer: {state['doc_ids']}")
        context = context_builder_rag(results)
        return {"context": context}
    except Exception as e:
        logger.error(f"Error in retriever_summarizer_rag: {e}", exc_info=True)
        return {"context": context_builder_rag(results)}


def retriever_compare_docs_rag(state: AgentState):
    try:
        logger.info(f"Retrieving for Compare: {state}")
        print(f"Retrieving for Compare: {state['doc_ids']}")
        context = context_builder_rag(results)
        return {"context": context}
    except Exception as e:
        logger.error(f"Error in retriever_compare_docs_rag: {e}", exc_info=True)
        return {"context": context_builder_rag(results)}

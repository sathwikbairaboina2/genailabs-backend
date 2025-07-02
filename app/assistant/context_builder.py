from app.core.logging import get_logger
from app.schemas.agent_state import AgentState

logger = get_logger(__name__)

# results = [
#     {
#         "similarity_score": 0.8333,
#         "text": "Velvet bean–Mucuna pruriens var. utilis, also known as mucuna—is a twining annual leguminous vine...",
#         "_id": "550e8400-e29b-41d4-a716-446655440001",
#         "_collection_name": "genailabs_research_assistant",
#         "link": "https://cgspace.cgiar.org/server/api/core/bitstreams/68bfaec0-8d32-4567-9133-7df9ec7f3e23/content",
#     },
#     {
#         "similarity_score": 0.75,
#         "text": "Mucuna is susceptible to fungal infections and pest attacks. Integrated pest management practices are recommended...",
#         "_id": "550e8400-e29b-41d4-a716-446655440005",
#         "_collection_name": "genailabs_research_assistant",
#         "link": "https://cgspace.cgiar.org/server/api/core/bitstreams/68bfaec0-8d32-4567-9133-7df9ec7f3e23/content",
#     },
# ]


def context_builder_rag(results):

    if not results:
        logger.warning("Empty result list received by context_builder_rag.")
        return ""

    try:
        context = "\n\n".join(
            f"""### Document ID: {doc.get('_id', 'N/A')}
Similarity Score: {doc.get('similarity_score', 0):.2f}
Link: {doc.get('link', 'N/A')}/{doc.get('_id', '')}

{doc.get('text', '')}"""
            for doc in results
        )
        return context
    except Exception as e:
        logger.error(f"Error building context from results: {e}", exc_info=True)
        return ""

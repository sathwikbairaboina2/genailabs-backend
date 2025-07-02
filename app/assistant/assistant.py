from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from app.assistant.retrivers import (
    retriever_compare_docs_rag,
    retriever_qa_rag,
    retriever_summarizer_rag,
)
from app.core.langgrapgh import llm
from app.core.logging import get_logger
from app.schemas.agent_state import AgentState
from app.assistant.prompts import prompt_template_qa
from app.assistant.chains import extract_intent_chain, generatorLLMchain


# {
#   "results": [
#     {
#       "similarity_score": 0.8333,
#       "text": "Velvet bean–Mucuna pruriens var. utilis, also known as mucuna—is a twining annual leguminous vine...",
#       "_id": "550e8400-e29b-41d4-a716-446655440001",
#       "_collection_name": "genailabs_research_assistant"
#     },
#     {
#       "similarity_score": 0.75,
#       "text": "Mucuna is susceptible to fungal infections and pest attacks. Integrated pest management practices are recommended...",
#       "_id": "550e8400-e29b-41d4-a716-446655440005",
#       "_collection_name": "genailabs_research_assistant"
#     }
#   ]
# }

import json


logger = get_logger(__name__)


def extract_intent_and_docs(state: AgentState):
    logger.info(f"Extracting intent and docs for question: {state}")
    parsed = extract_intent_chain.invoke({"question": state["question"]})

    parsed_json = json.loads(parsed)
    logger.info(f"Extracted intent: {parsed_json}")
    return {
        "intent": parsed_json["intent"],
        "doc_ids": parsed_json["doc_ids"],
        "question": state["question"],
    }


def context_builder(state: AgentState):
    logger.info(f"Building context for question: {state}")
    return "\n\n".join(state.get("context", []))


def generator(state: AgentState):
    logger.info(f"Generating answer for question: {state}")
    context = context_builder(state)
    prompt = prompt_template_qa.invoke(
        {"question": state["question"], "context": context}
    )
    response = generatorLLMchain.invoke(prompt)
    logger.info(f"Generated answer: {response  , prompt}")
    return ({"answer": response},)


def route_by_intent(state: AgentState):
    return state["intent"]


graph = StateGraph(AgentState)


graph.add_node("extract", extract_intent_and_docs)
graph.add_node("qa_retrieve", retriever_qa_rag)
graph.add_node("summarize_retrieve", retriever_summarizer_rag)
graph.add_node("compare_retrieve", retriever_compare_docs_rag)
graph.add_node("generate", generator)
graph
graph.add_conditional_edges(
    "extract",
    route_by_intent,
    {
        "qa": "qa_retrieve",
        "summarize": "summarize_retrieve",
        "compare": "compare_retrieve",
    },
)

graph.set_entry_point("extract")
graph.add_edge("qa_retrieve", "generate")
graph.add_edge("summarize_retrieve", "generate")
graph.add_edge("compare_retrieve", "generate")
graph.add_edge("generate", END)


workflow = graph.compile()

# print(workflow.get_graph().draw_ascii())


def ask_genailabs_ai(question: str):
    return workflow.invoke({"question": question})

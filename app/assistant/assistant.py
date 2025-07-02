from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from app.assistant.context_builder import context_builder_rag
from app.assistant.retrivers import (
    retriever_compare_docs_rag,
    retriever_qa_rag,
    retriever_summarizer_rag,
)
from app.core.langgrapgh import llm
from app.core.logging import get_logger
from app.schemas.agent_state import AgentState
from app.assistant.chains import extract_intent_chain, generatorLLMchain


import json


logger = get_logger(__name__)


def context_builder(state: AgentState):

    logger.info(f"Building context for question: {state}")
    context = context_builder_rag(state)
    return context


def extract_intent_from_user_input(state: AgentState):
    logger.info(f"Extracting intent and docs for question: {state}")
    parsed = extract_intent_chain.invoke({"question": state["question"]})

    parsed_json = json.loads(parsed)
    logger.info(f"Extracted intent: {parsed_json}")
    return {
        "intent": parsed_json["intent"],
        "doc_ids": parsed_json["doc_ids"],
        "question": state["question"],
    }


def generator(state: AgentState):
    try:
        logger.info(f"Generating answer for question: {state}")
        context = context_builder(state)
        response = generatorLLMchain.invoke(
            {"question": state["question"], "context": context}
        )
        parsed_response = json.loads(response)
        logger.info(f"Generated answer: {parsed_response}")
        return {
            "answer": {
                "answer": parsed_response["answer"],
                "document_ids": parsed_response["document_ids"],
                "references": parsed_response["references"],
            }
        }
    except Exception as e:
        logger.error(f"Error in generator: {e}", exc_info=True)


def route_by_intent(state: AgentState):
    return state["intent"]


graph = StateGraph(AgentState)


graph.add_node("extract", extract_intent_from_user_input)
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
    try:
        return workflow.invoke({"question": question})
    except Exception as e:
        logger.error(f"Error in ask_genailabs_ai: {e}", exc_info=True)

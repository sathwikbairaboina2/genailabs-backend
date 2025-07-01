from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END, START
from app.agent.retrivers import (
    retriever_compare_docs_rag,
    retriever_qa_rag,
    retriever_summarizer_rag,
)
from app.core.langgrapgh import llm
from app.schemas.agent_state import AgentState
from app.utils.prompts import prompt_template_qa, intent_analysis_prompt


extract_chain = intent_analysis_prompt | llm | StrOutputParser()


# 3. Intent + doc ID extractor node
def extract_intent_and_docs(state: AgentState):
    parsed = extract_chain.invoke({"question": state["question"]})
    print(f"[Intent Extraction] LLM parsed: {parsed}")
    import json

    parsed_json = json.loads(parsed)
    return {
        "intent": parsed_json["intent"],
        "doc_ids": parsed_json["doc_ids"],
        "question": state["question"],
    }


generatorLLMchain = prompt_template_qa | llm | StrOutputParser()


def context_builder(state: AgentState):
    return "\n\n".join(state.get("context", []))


def generator(state: AgentState):
    context = context_builder(state)
    prompt = prompt_template_qa.invoke(
        {"question": state["question"], "context": context}
    )
    response = generatorLLMchain.invoke(prompt)
    return {"answer": response}


def route_by_intent(state: AgentState):
    return state["intent"]


graph = StateGraph(AgentState)


graph.add_node("extract", extract_intent_and_docs)
graph.add_node("qa_retrieve", retriever_qa_rag)
graph.add_node("summarize_retrieve", retriever_summarizer_rag)
graph.add_node("compare_retrieve", retriever_compare_docs_rag)
graph.add_node("generate", generator)

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


def ask_genailabs_ai(question: str):
    return workflow.invoke({"question": question})

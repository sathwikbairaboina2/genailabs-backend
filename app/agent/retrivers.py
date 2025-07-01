def retriever_qa_rag(state: AgentState):
    print(f"Retrieving for QA: {state['doc_ids']}")
    return {"context": ["QA context based on " + ", ".join(state["doc_ids"])]}


def retriever_summarizer_rag(state: AgentState):
    print(f"Retrieving for Summarizer: {state['doc_ids']}")
    return {"context": ["Summarization context for " + ", ".join(state["doc_ids"])]}


def retriever_compare_docs_rag(state: AgentState):
    print(f"Retrieving for Compare: {state['doc_ids']}")
    return {"context": ["Comparison context for " + ", ".join(state["doc_ids"])]}

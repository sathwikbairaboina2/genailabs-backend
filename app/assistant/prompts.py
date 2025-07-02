from langchain_core.prompts import ChatPromptTemplate

from langchain_core.prompts import ChatPromptTemplate

prompt_template_qa = ChatPromptTemplate.from_template(
    """You are an AI research assistant helping users understand scientific journal content.
Use only the information provided in the journal context to answer the user's question.

Journal Context:
{context}

User Question:
{question}

Guidelines:
- Your response must be grounded in the provided context. Do not rely on external knowledge.
- If the answer cannot be found in the context, reply with: "The context does not contain enough information to answer the question."
- Provide clear, concise, and informative answers suitable for a research audience.

Now provide your answer based solely on the journal context above."""
)


intent_analysis_prompt = ChatPromptTemplate.from_template(
    """You are a helpful assistant. Given a user's question, do the following:

1. **Determine the intent** of the question. It should be one of:
   - "qa": if the user is asking a question and expecting a factual answer from a document.
   - "summarize": if the user wants a summary of a document or documents.
   - "compare": if the user wants a comparison between two or more documents.

2. **Extract doc_ids**: Look for any document IDs mentioned or implied in the question. If none are found, return an empty list (`[]`).

Your response must be valid JSON in the following format:
{{
  "intent": "qa" | "summarize" | "compare",
  "doc_ids": ["..."]
}}

Question: {question}
"""
)

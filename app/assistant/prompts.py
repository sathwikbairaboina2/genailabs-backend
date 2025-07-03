from langchain_core.prompts import ChatPromptTemplate

from langchain_core.prompts import ChatPromptTemplate

prompt_template_genaerator = ChatPromptTemplate.from_template(
    """You are an AI research assistant helping users understand scientific journal content.
Use the information provided in the journal context to answer the user's question. Rely primarily on the context. If the answer can be reasonably inferred, answer cautiously and make it clear.

---

Journal Context:
{context}

---

User Question:
{question}

---

Guidelines:
- Your response must be based on the journal context.
- Do NOT include document IDs , like _mucuna.pdf , or document links inside the "answer" text.
- Instead, list supporting document IDs and references separately in their respective fields.
- If no relevant information is found in the context, return exactly:
  {{
    "answer": "The context does not contain enough information to answer the question.",
    "document_ids": [],
    "references": []
  }}

---

Respond strictly in the following valid JSON format:
{{
  "answer": "<your generated answer here>",
  "document_ids": ["<document_id_1>", "<document_id_2>", ...],
  "references": ["<document_link_1>", "<document_link_2>", ...]
}}
"""
)


prompt_template_summarize = ChatPromptTemplate.from_template(
    """You are an AI research assistant tasked with summarizing scientific journal content.

---

Journal Context:
{context}

---

Guidelines:
- Your summary should capture the main points of the journal context.
- Use concise language to convey essential information.
- Avoid excessive technical jargon unless crucial for accuracy.

---

Respond in the following valid JSON format:
{{
  "answer": "<your generated summary here>"
}}
"""
)

prompt_template_compare = ChatPromptTemplate.from_template(
    """You are an AI research assistant tasked with comparing scientific journal content.

---

based on attached socumets content
{context}

---

Guidelines:
- Your comparison should highlight similarities and differences between the two journal contexts.
- Provide insights into how these contexts relate or contrast.
- Avoid unnecessary details and focus on significant aspects.

---

Respond in the following valid JSON format:
{{
  "answer": "<your generated comparison here>"
}}
"""
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

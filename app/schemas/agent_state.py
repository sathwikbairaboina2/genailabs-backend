from typing import Any, List, TypedDict, Literal, Optional


class AnswerPayload(TypedDict):
    answer: str
    document_ids: List[str]
    references: List[str]


class AgentState(TypedDict):
    question: str
    intent: Optional[Literal["qa", "summarize", "compare"]]
    doc_ids: Optional[List[str]]
    context: Optional[List[str]]
    answer: Optional[AnswerPayload]

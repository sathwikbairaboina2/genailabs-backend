from typing import List, TypedDict, Literal, Optional


class AgentState(TypedDict):
    question: str
    intent: Optional[Literal["qa", "summarize", "compare"]]
    doc_ids: Optional[List[str]]
    context: Optional[List[str]]
    answer: Optional[str]

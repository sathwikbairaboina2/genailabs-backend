from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class QueryLog(BaseModel):
    id: str = Field(default_factory=str, alias="_id")
    query: str
    top_k: int
    min_score: float
    referenced_chunk_ids: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

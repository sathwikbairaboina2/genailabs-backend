from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class QueryLog(BaseModel):
    _id: str
    query: str
    top_k: int
    min_score: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

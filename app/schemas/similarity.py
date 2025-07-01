from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class SimilarityRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1)
    min_score: float = Field(default=0.5, ge=0.0, le=1.0)

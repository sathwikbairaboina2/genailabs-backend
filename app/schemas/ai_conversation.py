from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class AIConversation(BaseModel):
    user_query: str
    ai_answer: str
    refered_chunk_ids: List[str]
    category: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    citation: str
    source_doc_ids: List[str]
    celery_job_id: str
    status: str

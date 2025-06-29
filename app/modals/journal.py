from pydantic import BaseModel, Field
from typing import List, Optional


class Journal(BaseModel):
    id: str = Field(..., alias="_id")
    doi: str
    source_doc_id: str
    publish_year: int
    field: str
    chunk_ids: List[str] = []
    status: str
    schema_version: str

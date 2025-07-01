from pydantic import BaseModel, Field
from typing import List, Optional


class Journal(BaseModel):
    doi: str
    journal_id: str
    source_doc_id: str
    publish_year: int
    field: str
    chunk_ids: List[str] = []
    status: str
    schema_version: str

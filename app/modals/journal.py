from pydantic import BaseModel, Field
from typing import List


class Journal(BaseModel):
    _id: str
    source_doc_id: str
    publish_year: int
    field: str
    chunk_ids: List[str] = []
    status: str
    schema_version: str
    journal_id: str

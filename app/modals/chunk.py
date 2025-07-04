from pydantic import BaseModel, Field
from typing import List


class Chunk(BaseModel):
    _id: str
    journal: str
    chunk_index: int
    section_heading: str
    usage_count: int = 0
    attributes: List[str]
    link: str
    text: str
    source_doc_id: str
    journal_id: str
    chunk_id: str

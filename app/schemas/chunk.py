from pydantic import BaseModel, Field
from typing import List


class Chunk(BaseModel):
    id: str
    journal: str
    chunk_index: int
    section_heading: str
    usage_count: int = 0
    attributes: List[str]
    link: str
    text: str
    source_doc_id: str

from typing import List, Optional

from pydantic import BaseModel


class Document(BaseModel):
    id: str
    name: str
    content: str
    url: Optional[str]
    mime_type: str
    metadata: Optional[dict] = {}
    keywords: Optional[List[str]] = []
from typing import List, Optional, TypedDict

from pydantic import BaseModel


class Document(BaseModel):
    id: str
    name: str
    content: str
    url: Optional[str]
    mime_type: str


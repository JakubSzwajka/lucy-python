from typing import List, Optional, TypedDict

from pydantic import BaseModel

class Document(BaseModel):
    id: str
    name: str
    content: str
    url: Optional[str]
    mime_type: str


class ThoughtsDoc(Document):
    _thoughts: List[str]

    @property
    def content(self):
        return "\n\n".join(self._thoughts)

    def add_thought(self, thought: str):
        self._thoughts.append(thought)

from datetime import datetime
from enum import StrEnum
from typing import List


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class Message:
    def __init__(
        self, role: MessageRole, content: str, created_at: datetime = datetime.now()
    ):
        self.role = role
        self.content = content
        self.created_at = created_at


class MessageService:
    def __init__(self):
        self.db = {}

    def get_conversation(self, conversation_id: str) -> List[Message]:
        if conversation_id not in self.db:
            self.db[conversation_id] = []
        return self.db[conversation_id]

    def add_message(self, conversation_id: str, message: Message):
        if conversation_id not in self.db:
            self.db[conversation_id] = []
        self.db[conversation_id].append(message)

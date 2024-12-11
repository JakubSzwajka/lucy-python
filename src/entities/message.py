from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import json
from typing import Optional
from uuid import uuid4


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Usage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class Message:
    def __init__(
        self,
        text: str,
        role: MessageRole,
        json_mode: bool = False,
        usage: Optional[Usage] = None,
    ):
        self.text = text
        self.role = role
        self.json_mode = json_mode

    def to_dict(self) -> dict:
        if not self.json_mode:
            raise ValueError("Message is not in JSON mode")
        return json.loads(self.text)

    def to_open_ai_dict(self) -> dict:
        return {
            "id": "chatcmpl-" + str(datetime.now()),
            "object": "chat.completion",
            "created": datetime.now().timestamp(),
            "model": "gpt-4o-mini",
            "system_fingerprint": "fp_" + str(uuid4()),
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": self.text},
                    "finish_reason": "stop",
                }
            ],
        }

    def __repr__(self) -> str:
        return (
            f"Message(text={self.text}, role={self.role}, json_mode={self.json_mode})"
        )


#   return {
#     id: 'chatcmpl-' + Date.now(),
#     object: 'chat.completion',
#     created: Math.floor(Date.now() / 1000),
#     model,
#     system_fingerprint: 'fp_' + Math.random().toString(36).substring(2, 15),
#     choices: [
#       {
#         index: 0,
#         message: {
#           role: 'assistant',
#           content: response,
#         },
#         finish_reason: 'stop'
#       }
#     ],
#     usage: usage
#       ? {
#           prompt_tokens: usage.promptTokens ?? 0,
#           completion_tokens: usage.completionTokens ?? 0,
#           total_tokens: usage.totalTokens ?? 0
#         }
#       : {
#           prompt_tokens: 0,
#           completion_tokens: 0,
#           total_tokens: 0
#         }
#   };

from dataclasses import dataclass
from prompts.prompt_service import Prompt
from providers.LLM.open_ai import OpenAI, OpenAIModels
from entities.message import Message, MessageRole
from langfuse.client import StatefulClient


@dataclass
class LLMCompletionResponse:
    text: str
    model: str
    usage: str
    system_fingerprint: str
    choices: str


class LLMService:
    def __init__(self):
        self.open_ai = OpenAI()

    def completion(
        self,
        query: str,
        prompt: Prompt,
        trace: StatefulClient,
        json_mode: bool = False,
        completion_name: str = "completion",
        model: str = OpenAIModels.GPT_4O,
    ) -> Message:
        response = self.open_ai.completion(
            query=query,
            prompt=prompt,
            json_mode=json_mode,
            model=model,
            trace=trace,
            completion_name=completion_name,
        )

        text = response.choices[0].message.content or ""
        return Message(text, MessageRole.ASSISTANT, json_mode)

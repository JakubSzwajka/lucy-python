from enum import StrEnum
from typing import Iterable
from openai import OpenAI as OpenAIClient
from langfuse.client import StatefulClient
from prompts.prompt_service import Prompt
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

class OpenAIModels(StrEnum):
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"


class OpenAI:
    def __init__(self):
        self.client = OpenAIClient()

    def completion(
            self,
            query: str,
            prompt: Prompt,
            trace: StatefulClient,
            json_mode: bool = False,
            model: str = OpenAIModels.GPT_4O,
            completion_name: str = "completion"
        ):

        messages: Iterable[ChatCompletionMessageParam] = [
                    {"role": "system", "content": prompt.prompt},
                    {"role": "user", "content": query},
        ]
        generation = trace.generation(
            name=completion_name,
            input=messages,
            model_parameters={"json_mode": json_mode},
            model=model
        )


        if json_mode:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"},
            )
        else:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages
            )

        generation.end(output=response.choices, usage=response.usage, model=model)
        return response

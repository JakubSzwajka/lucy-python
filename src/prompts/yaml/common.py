from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class PromptRules:
    rules: List[str]


@dataclass
class PromptExample:
    user_input: str
    environment: str
    ai_response: str


@dataclass
class PromptBase:
    header: str
    prompt_objective: str
    prompt_rules: PromptRules
    prompt_examples: List[PromptExample]


def current_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

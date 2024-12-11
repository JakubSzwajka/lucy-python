from datetime import datetime

from agent import Context
from config import GlobalConfig

from enum import StrEnum

from prompts.xml.action_prompt import get_action_prompt
from prompts.xml.final_answer_prompt import get_final_answer_prompt
from prompts.xml.master_prompt import get_master_prompt
from prompts.xml.personality_prompt import get_personality_prompt
from prompts.xml.reflection_environment_prompt import get_reflection_environment_prompt
from prompts.xml.reflection_memory_prompt import get_reflection_memory_prompt
from prompts.xml.reflection_personality_prompt import get_reflection_personality_prompt
from prompts.xml.reflection_tools_prompt import get_reflection_tools_prompt
from prompts.xml.task_prompt import get_task_prompt


class PromptName(StrEnum):
    MASTER = "MASTER"
    WEB_SEARCH_ANSWER = "WEB_SEARCH_ANSWER"
    PERSONALITY = "PERSONALITY"
    REFLECTION_ENVIRONMENT = "REFLECTION_ENVIRONMENT"
    REFLECTION_PERSONALITY = "REFLECTION_PERSONALITY"
    REFLECTION_TOOLS = "REFLECTION_TOOLS"
    REFLECTION_MEMORY = "REFLECTION_MEMORY"
    TASK = "TASK"
    ACTION = "ACTION"
    FINAL_ANSWER = "FINAL_ANSWER"

class Prompt:
    def __init__(self, name: PromptName, prompt: str):
        self.name = name
        self.prompt = prompt

    @property
    def personality(self) -> str:
        return get_personality_prompt(assistant_name=GlobalConfig.ASSISTANT_NAME)

    @property
    def current_datetime(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def json_mode_reminder(self) -> str:
        return """
        <json_mode_reminder>
            ALWAYS output a valid JSON object.
            Start with the opening brace '{' and end with the closing brace '}'.
            Ensure all properties and values are properly enclosed in double quotes.
            Do not include any additional text or formatting.
            Do not start with '```json' or '```' or any other JSON formatting.
            Never use xml format. NEVER. This is important to USE JSON ONLY!
        </json_mode_reminder>
        """


class ReflectionMemoryPrompt(Prompt):
    def __init__(self, context: Context):
        content = get_reflection_memory_prompt(
            assistant_name=GlobalConfig.ASSISTANT_NAME,
            user_name=GlobalConfig.USER_NAME,
            current_datetime=self.current_datetime,
            personality=self.personality,
            environment=context.thoughts_environment,
            memory_categories="",
            format=self.json_mode_reminder,
        )
        super().__init__(PromptName.REFLECTION_MEMORY, content)


class ReflectionToolsPrompt(Prompt):
    def __init__(self, context: Context):
        content = get_reflection_tools_prompt(
            assistant_name=GlobalConfig.ASSISTANT_NAME,
            user_name=GlobalConfig.USER_NAME,
            current_datetime=self.current_datetime,
            personality=self.personality,
            environment=context.thoughts_environment,
            tools=context.thoughts_tools,
            format=self.json_mode_reminder,
        )
        super().__init__(PromptName.REFLECTION_TOOLS, content)


class ReflectionPersonalityPrompt(Prompt):
    def __init__(self, context: Context):
        content = get_reflection_personality_prompt(
            assistant_name=GlobalConfig.ASSISTANT_NAME,
            user_name=GlobalConfig.USER_NAME,
            personality=self.personality,
            format=self.json_mode_reminder,
        )
        super().__init__(PromptName.REFLECTION_PERSONALITY, content)


class ReflectionEnvironmentPrompt(Prompt):
    def __init__(self, context: Context):
        content = get_reflection_environment_prompt(
            assistant_name=GlobalConfig.ASSISTANT_NAME,
            user_name=GlobalConfig.USER_NAME,
            current_environment="",
            current_datetime=self.current_datetime,
            format=self.json_mode_reminder,
        )
        super().__init__(PromptName.REFLECTION_ENVIRONMENT, content)


class TaskPrompt(Prompt):
    def __init__(self, context: Context):
        content = get_task_prompt(
            personality=self.personality,
            environment=context.thoughts_environment,
            tools=context.thoughts_tools,
            memories="",
            tasks=str(context.tasks),
            memory_thoughts=context.thoughts_memory,
            tool_thoughts=context.thoughts_tools,
            format=self.json_mode_reminder,
        )
        super().__init__(PromptName.TASK, content)


class ActionPrompt(Prompt):
    def __init__(self, context: Context):
        content = get_action_prompt(
            personality=self.personality,
            environment=context.thoughts_environment,
            tools=context.thoughts_tools,
            memories=context.thoughts_memory,
            tasks_with_actions=str(context.tasks),
            format=self.json_mode_reminder,
        )
        super().__init__(PromptName.ACTION, content)


class MasterPrompt(Prompt):
    def __init__(self, context: Context):
        content = get_master_prompt(
            assistant_name=GlobalConfig.ASSISTANT_NAME,
            user_name=GlobalConfig.USER_NAME,
            personality=self.personality,
        )
        super().__init__(PromptName.MASTER, content)

class FinalAnswerPrompt(Prompt):
    def __init__(self, context: Context):
        content = get_final_answer_prompt(context=context, current_datetime=self.current_datetime)
        super().__init__(PromptName.FINAL_ANSWER, content)

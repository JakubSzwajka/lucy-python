import asyncio
from datetime import datetime
from uuid import uuid4
from context import (
    Action,
    ActionStatus,
    Context,
    Task,
    TaskStatus,
    Thought,
    ThoughtType,
)
from entities.message import Message
from event_bus import Event, EventBus
from modules.planner import Planner
from prompts.prompt_service import (
    ActionPrompt,
    FinalAnswerPrompt,
    MasterPrompt,
    ReflectionEnvironmentPrompt,
    ReflectionMemoryPrompt,
    ReflectionPersonalityPrompt,
    ReflectionToolsPrompt,
    TaskPrompt,
)
from services.message_service import MessageService
from services.tracing_service import TracingService
from providers.LLM.LLMService import LLMService
from langfuse.decorators import observe
from langfuse.client import StatefulClient


class ReflectionModule:
    def __init__(self):
        self.llm_service = LLMService()
        self.event_bus = EventBus(self.__class__.__name__)

    async def think_about_user_environment(
        self, query: str, context: Context, trace: StatefulClient
    ) -> None:
        environment_thoughts = self.llm_service.completion(
            query,
            ReflectionEnvironmentPrompt(context),
            trace,
            json_mode=True,
            completion_name="environment_thoughts",
        )
        context.add_thought(Thought(ThoughtType.ENVIRONMENT, environment_thoughts.text))
        self.event_bus.emit(
            Event.THOUGHT_ADDED,
            {
                "type": ThoughtType.ENVIRONMENT,
            },
        )

    async def think_about_user_personality(
        self, query: str, context: Context, trace: StatefulClient
    ) -> None:
        personality_thoughts = self.llm_service.completion(
            query,
            ReflectionPersonalityPrompt(context),
            trace,
            json_mode=True,
            completion_name="personality_thoughts",
        )
        context.add_thought(Thought(ThoughtType.PERSONALITY, personality_thoughts.text))
        self.event_bus.emit(
            Event.THOUGHT_ADDED,
            {
                "type": ThoughtType.PERSONALITY,
            },
        )

    async def think_about_available_memory_about_user(
        self, query: str, context: Context, trace: StatefulClient
    ) -> None:
        memory_thoughts = self.llm_service.completion(
            query,
            ReflectionMemoryPrompt(context),
            trace,
            json_mode=True,
            completion_name="memory_thoughts",
        )
        context.add_thought(Thought(ThoughtType.MEMORY, memory_thoughts.text))
        self.event_bus.emit(
            Event.THOUGHT_ADDED,
            {
                "type": ThoughtType.MEMORY,
            },
        )

    async def think_about_available_tools(
        self, query: str, context: Context, trace: StatefulClient
    ) -> None:
        tools_thoughts = self.llm_service.completion(
            query,
            ReflectionToolsPrompt(context),
            trace,
            json_mode=True,
            completion_name="tools_thoughts",
        )
        context.add_thought(Thought(ThoughtType.TOOLS, tools_thoughts.text))
        self.event_bus.emit(
            Event.THOUGHT_ADDED,
            {
                "type": ThoughtType.TOOLS,
            },
        )

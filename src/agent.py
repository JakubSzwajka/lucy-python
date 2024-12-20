import asyncio
from context import (
    Context,
    Thought,
    ThoughtType,
)
from entities.message import Message
from event_bus import Event, EventBus
from modules.planner import Planner
from prompts.prompt_service import (
    FinalAnswerPrompt,
    ReflectionEnvironmentPrompt,
    ReflectionMemoryPrompt,
    ReflectionPersonalityPrompt,
    ReflectionToolsPrompt,
)
from services.message_service import MessageService
from services.tracing_service import TracingService
from providers.LLM.LLMService import LLMService
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


class Agent:
    def __init__(self):
        self.tracing_service = TracingService()
        self.llm_service = LLMService()

        self.reflection_module = ReflectionModule()
        self.planning_module = Planner()
        self.message_service = MessageService()

    async def talk(self, query: str, user_id: str, conversation_id: str) -> Message:
        trace = self.tracing_service.start_trace(
            conversation_id, user_id=user_id, query=query
        )
        context = Context(conversation_id=conversation_id)

        await self._reflect(context, query, trace)
        while not context.iteration_exceeded():
            self._plan(context, query, trace)
            # self._action(context, query)

            if context.can_do_final_answer():
                break
            context.complete_iteration()

        message = self.llm_service.completion(
            query,
            FinalAnswerPrompt(context),
            trace,
            json_mode=False,
            completion_name="final_answer",
        )

        trace.update(output={"message": message.text, "context": context.as_dict()})
        self.tracing_service.finalize_trace()
        return message

    async def _reflect(
        self, context: Context, query: str, trace: StatefulClient
    ) -> None:
        span = trace.span(
            name="reflect", input={"query": query, "context": context.as_dict()}
        )

        await asyncio.gather(
            self.reflection_module.think_about_user_environment(query, context, span),
            self.reflection_module.think_about_user_personality(query, context, span),
        )

        await asyncio.gather(
            self.reflection_module.think_about_available_memory_about_user(
                query, context, span
            ),
            self.reflection_module.think_about_available_tools(query, context, span),
        )

        span.end(output={"context": context.as_dict()})

    def _plan(self, context: Context, query: str, trace: StatefulClient) -> None:
        # ------------------------ TASK PLANNING PHASE ------------------------
        span = trace.span(
            name=f"plan_iteration_{context.current_iteration}",
            input={"query": query, "context": context.as_dict()},
        )
        self.planning_module.plan_tasks(query, context, span)
        span.end(output={"context": context.as_dict()})

        # ------------------------ ACTION PLANNING PHASE ------------------------
        span = trace.span(
            name=f"plan_iteration_{context.current_iteration}",
            input={"query": query, "context": context.as_dict()},
        )
        self.planning_module.plan_actions(query, context, span)
        span.end(output={"context": context.as_dict()})

    def _action(self, context: Context, query: str) -> None:
        # use_thoughts = self.llm_service.completion(query, ActionThoughtsPrompt(context), json_mode=True)
        pass

    def _generate_response(self, context: Context, query: str) -> str:
        return "response"

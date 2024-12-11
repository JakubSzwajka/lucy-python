from datetime import datetime
from uuid import uuid4
from context import Action, ActionStatus, Context, Task, TaskStatus, Thought, ThoughtType
from entities.message import Message
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
from services.tracing_service import TracingService
from providers.LLM.LLMService import LLMService
from langfuse.decorators import observe
from langfuse.client import StatefulClient

class Planner:
    def __init__(self):
        self.llm_service = LLMService()

    def plan_tasks(self, query: str, context: Context, trace: StatefulClient) -> None:
        task_thoughts = self.llm_service.completion(
            query, TaskPrompt(context), trace, json_mode=True, completion_name="tasks_planning"
        )
        task_reflection = task_thoughts.to_dict().get("result", [])

        updated_tasks = []
        for task in task_reflection:
            if task_id := task.get("uuid"):
                # update existing task
                existing_task = context.get_task_by_id(task_id)
                if existing_task and existing_task.status == TaskStatus.PENDING:
                    existing_task.name = task.get("name")
                    existing_task.description = task.get("description")
                    updated_tasks.append(existing_task)

            else:
                # create new task
                updated_tasks.append(
                    Task(
                        id=str(uuid4()),
                        name=task.get("name"),
                        description=task.get("description"),
                        status=task.get("status"),
                        actions=[],
                    )
                )
        context.tasks = updated_tasks
        if first_pending_task := context.get_first_pending_task():
            context.current_task_id = first_pending_task.id

    def plan_actions(self, query: str, context: Context, trace: StatefulClient) -> None:
        action_thoughts = self.llm_service.completion(
            query, ActionPrompt(context), trace, json_mode=True, completion_name="actions_planning"
        )
        action_reflection = action_thoughts.to_dict().get("result", None)

        if action_reflection:
            task_to_update = context.get_task_by_id(action_reflection.get("task_uuid"))
            if task_to_update:
                action = Action(
                    id=str(uuid4()),
                    name=action_reflection.get("name"),
                    tool_name=action_reflection.get("tool_name"),
                    task_uuid=action_reflection.get("task_uuid"),
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    payload={},
                    result=None,
                    status=ActionStatus.PENDING,
                )
                task_to_update.add_action(action)
                context.current_task_id = task_to_update.id
                context.current_action_id = action.id



class ReflectionModule:
    def __init__(self):
        self.llm_service = LLMService()

    def think_about_user_environment(self, query: str, context: Context, trace: StatefulClient) -> None:
        environment_thoughts = self.llm_service.completion(
            query, ReflectionEnvironmentPrompt(context), trace, json_mode=True, completion_name="environment_thoughts"
        )
        context.add_thought(Thought(ThoughtType.ENVIRONMENT, environment_thoughts.text))

    def think_about_user_personality(self, query: str, context: Context, trace: StatefulClient) -> None:
        personality_thoughts = self.llm_service.completion(
            query, ReflectionPersonalityPrompt(context), trace, json_mode=True, completion_name="personality_thoughts"
        )
        context.add_thought(Thought(ThoughtType.PERSONALITY, personality_thoughts.text))
    def think_about_available_memory_about_user(self, query: str, context: Context, trace: StatefulClient) -> None:
        memory_thoughts = self.llm_service.completion(
            query, ReflectionMemoryPrompt(context), trace, json_mode=True, completion_name="memory_thoughts"
        )
        context.add_thought(Thought(ThoughtType.MEMORY, memory_thoughts.text))

    def think_about_available_tools(self, query: str, context: Context, trace: StatefulClient) -> None:
        tools_thoughts = self.llm_service.completion(
            query, ReflectionToolsPrompt(context), trace, json_mode=True, completion_name="tools_thoughts"
        )
        context.add_thought(Thought(ThoughtType.TOOLS, tools_thoughts.text))

class Agent:
    def __init__(self):
        self.tracing_service = TracingService()
        self.llm_service = LLMService()

        self.reflection_module = ReflectionModule()
        self.planning_module = Planner()

    def _log(self, message: str) -> None:
        # pass
        print(message)

    def talk(self, query: str, user_id: str, conversation_id: str) -> Message:
        trace = self.tracing_service.start_trace(conversation_id, user_id=user_id, query=query)

        context = Context()
        self._reflect(context, query, trace)
        while not context.iteration_exceeded():
            self._plan(context, query, trace)
            # self._action(context, query)

            if context.can_do_final_answer():
                break
            context.complete_iteration()

        self._log("========== Final Answer ============")
        self._log(str(context))

        message = self.llm_service.completion(
            query, FinalAnswerPrompt(context), trace, json_mode=False, completion_name="final_answer"
        )

        trace.update(output={
            "message": message.text,
            "context": context.as_dict()
        })
        self.tracing_service.finalize_trace()
        return message

    def _reflect(self, context: Context, query: str, trace: StatefulClient) -> None:
        span = trace.span(name="reflect", input={"query": query, "context": context.as_dict()})

        self.reflection_module.think_about_user_environment(query, context, span)
        self.reflection_module.think_about_user_personality(query, context, span)
        self.reflection_module.think_about_available_memory_about_user(query, context, span)
        self.reflection_module.think_about_available_tools(query, context, span)

        span.end(output={"context": context.as_dict()})

    def _plan(self, context: Context, query: str, trace: StatefulClient) -> None:
        # ------------------------ TASK PLANNING PHASE ------------------------
        span = trace.span(name=f"plan_iteration_{context.current_iteration}", input={"query": query, "context": context.as_dict()})
        self.planning_module.plan_tasks(query, context, span)
        span.end(output={"context": context.as_dict()})

        # ------------------------ ACTION PLANNING PHASE ------------------------
        span = trace.span(name=f"plan_iteration_{context.current_iteration}", input={"query": query, "context": context.as_dict()})
        self.planning_module.plan_actions(query, context, span)
        span.end(output={"context": context.as_dict()})


    def _action(self, context: Context, query: str) -> None:
        self._log("========== Action Phase ============")
        self._log("No action implemented yet...")
        # use_thoughts = self.llm_service.completion(query, ActionThoughtsPrompt(context), json_mode=True)

    def _generate_response(self, context: Context, query: str) -> str:
        return "response"

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
from event_bus import Event, EventBus
from prompts.prompt_service import (
    ActionPrompt,
    TaskPrompt,
)
from providers.LLM.LLMService import LLMService
from langfuse.decorators import observe
from langfuse.client import StatefulClient


class Planner:
    def __init__(self):
        self.llm_service = LLMService()
        self.event_bus = EventBus(self.__class__.__name__)

    def plan_tasks(self, query: str, context: Context, trace: StatefulClient) -> None:
        task_thoughts = self.llm_service.completion(
            query,
            TaskPrompt(context),
            trace,
            json_mode=True,
            completion_name="tasks_planning",
        )
        self.event_bus.emit(Event.TASKS_PLANNED, {})
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

        self.event_bus.emit(
            Event.TASKS_UPDATED,
            {
                "current_task_id": context.current_task_id,
                "current_action_id": context.current_action_id,
            },
        )

    def plan_actions(self, query: str, context: Context, trace: StatefulClient) -> None:
        action_thoughts = self.llm_service.completion(
            query,
            ActionPrompt(context),
            trace,
            json_mode=True,
            completion_name="actions_planning",
        )
        self.event_bus.emit(Event.ACTIONS_PLANNED, {})
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

        self.event_bus.emit(
            Event.ACTIONS_UPDATED,
            {
                "current_task_id": context.current_task_id,
                "current_action_id": context.current_action_id,
            },
        )

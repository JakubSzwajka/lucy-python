from dataclasses import dataclass, asdict
from datetime import datetime
from enum import StrEnum
from typing import List
from dict2xml import dict2xml, DataSorter

from event_bus import Event, EventBus
from services.message_service import MessageService


def dataclass_to_xml(instance) -> str:
    return dict2xml(
        asdict(instance),
        wrap=instance.__class__.__name__.lower(),
        indent="  ",
        data_sorter=DataSorter.never(),
    )


class ThoughtType(StrEnum):
    REFLECTION = "reflection"
    MEMORY = "memory"
    TOOLS = "tools"
    ENVIRONMENT = "environment"
    PERSONALITY = "personality"


class TaskStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"


class ActionStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"


@dataclass
class Thought:
    type: ThoughtType
    content: str

    def __repr__(self) -> str:
        return dataclass_to_xml(self)


@dataclass
class Action:
    id: str
    name: str
    tool_name: str
    task_uuid: str
    created_at: datetime
    updated_at: datetime
    payload: dict
    result: str | None
    status: ActionStatus

    def __repr__(self) -> str:
        return dataclass_to_xml(self)


@dataclass
class Task:
    id: str
    status: TaskStatus
    name: str
    description: str
    actions: List[Action]

    def add_action(self, action: Action) -> None:
        self.actions.append(action)

    def get_action_by_id(self, id: str | None) -> Action | None:
        if not id:
            raise ValueError("Action ID is required")
        return next((action for action in self.actions if action.id == id), None)

    def __repr__(self) -> str:
        return dataclass_to_xml(self)


class Context:
    def __init__(self, conversation_id: str):
        self.current_iteration = 0
        self.max_iterations = 5
        self.iterations = {}
        self.thoughts = {}
        self.tasks: List[Task] = []

        self.current_task_id: str | None = None
        self.current_action_id: str | None = None

        self.event_bus = EventBus(self.__class__.__name__)
        self.message_service = MessageService()
        self.conversation = self.message_service.get_conversation(conversation_id)

    @property
    def current_task(self) -> Task | None:
        if not self.current_task_id:
            return None
        return self.get_task_by_id(self.current_task_id)

    @property
    def current_action(self) -> Action | None:
        if not self.current_action_id:
            return None
        if current_task := self.current_task:
            return current_task.get_action_by_id(self.current_action_id)
        return None

    @property
    def thoughts_environment(self) -> str:
        return str(self.thoughts.get(ThoughtType.ENVIRONMENT)) or ""

    @property
    def thoughts_personality(self) -> str:
        return str(self.thoughts.get(ThoughtType.PERSONALITY)) or ""

    @property
    def thoughts_memory(self) -> str:
        return str(self.thoughts.get(ThoughtType.MEMORY)) or ""

    @property
    def thoughts_tools(self) -> str:
        return str(self.thoughts.get(ThoughtType.TOOLS)) or ""

    def get_task_by_id(self, id: str | None) -> Task | None:
        if not id:
            raise ValueError("Task ID is required")
        return next((task for task in self.tasks if task.id == id), None)

    def get_first_pending_task(self) -> Task | None:
        return next(
            (task for task in self.tasks if task.status == TaskStatus.PENDING), None
        )

    def add_thought(self, thought: Thought) -> None:
        self.thoughts[thought.type] = thought

    def complete_iteration(self) -> None:
        self.current_iteration += 1
        self.event_bus.emit(
            Event.ITERATION_COMPLETED,
            {
                "current_iteration": self.current_iteration,
                "max_iterations": self.max_iterations,
            },
        )

    def iteration_exceeded(self) -> bool:
        is_exceeded = self.current_iteration >= self.max_iterations
        if not is_exceeded:
            self.event_bus.emit(
                Event.ITERATION_STARTED,
                {
                    "current_iteration": self.current_iteration,
                    "max_iterations": self.max_iterations,
                },
            )

        return is_exceeded

    def set_step_result(self, step_result: str) -> None:
        self.iterations[self.current_iteration].set_step_result(step_result)

    def can_do_final_answer(self) -> bool:
        result = False

        if not self.current_task_id or not self.current_action_id:
            return True

        current_task = self.get_task_by_id(self.current_task_id)
        if current_task:
            current_action = current_task.get_action_by_id(self.current_action_id)
            if current_action:
                result = current_action.tool_name == "final_answer"

        if result:
            self.event_bus.emit(
                Event.FINAL_ANSWER_READY,
                {
                    "current_task_id": self.current_task_id,
                    "current_action_id": self.current_action_id,
                },
            )

        return result

    def get_performed_tasks(self) -> str:
        return "No tasks are available"

    def as_dict(self) -> dict:
        return {
            "current_iteration": self.current_iteration,
            "max_iterations": self.max_iterations,
            "thoughts": [asdict(thought) for thought in self.thoughts.values()],
            "tasks": [asdict(task) for task in self.tasks],
            "current_task": asdict(self.current_task) if self.current_task else None,
            "current_action": asdict(self.current_action)
            if self.current_action
            else None,
        }

    def __repr__(self) -> str:
        data = self.as_dict()
        return dict2xml(
            data, wrap="context", indent="  ", data_sorter=DataSorter.never()
        )

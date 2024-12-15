from logging import getLogger
from enum import StrEnum


class Event(StrEnum):
    THOUGHT_ADDED = "thought_added"
    ITERATION_STARTED = "iteration_started"
    ITERATION_COMPLETED = "iteration_completed"
    TASKS_PLANNED = "tasks_planned"
    TASKS_UPDATED = "tasks_updated"
    ACTIONS_PLANNED = "actions_planned"
    ACTIONS_UPDATED = "actions_updated"

    FINAL_ANSWER_READY = "final_answer_ready"


class EventBus:
    def __init__(self, name: str):
        self.logger = getLogger(name)

    def emit(self, event: Event, data: dict):
        self.logger.info(f"[{event}]: {data}")

import os
from typing import Optional
from todoist_api_python.api import TodoistAPI
from agents.logger import get_logger


class TodoistClient:
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        token = os.getenv("TODOIST_LUCY_TOKEN")
        if token is None:
            raise ValueError("TODOIST_LUCY_TOKEN is not set")
        self.logger.info("Initializing Todoist client")
        self.client = TodoistAPI(token=token)

    def get_tasks(self, filter: str):
        self.logger.info("Getting tasks with filter: %s", filter)
        return self.client.get_tasks(filter=filter)

    def add_task(self, name: str, due_date: str, description: Optional[str] = None):
        self.logger.info("Adding task: %s", name)
        return self.client.add_task(
            content=name, due_date=due_date, description=description
        )

    def complete_task(self, task_id: str):
        self.logger.info("Completing task: %s", task_id)
        return self.client.close_task(task_id)

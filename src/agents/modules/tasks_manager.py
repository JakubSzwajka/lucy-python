import os
from typing import Optional
from todoist_api_python.api import TodoistAPI


class TodoistClient:
    def __init__(self):
        token = os.getenv("TODOIST_LUCY_TOKEN")
        if token is None:
            raise ValueError("TODOIST_LUCY_TOKEN is not set")
        self.client = TodoistAPI(token=token)

    def get_tasks(self, filter: str):
        return self.client.get_tasks(
            filter=filter
        )

    def add_task(self, name: str, due_date: str, description: Optional[str] = None):
        return self.client.add_task(content=name, due_date=due_date, description=description)

    def complete_task(self, task_id: str):
        return self.client.close_task(task_id)

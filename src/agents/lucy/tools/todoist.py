from pydantic import BaseModel, Field
from typing import List, Optional, Type
from langchain_core.runnables.config import RunnableConfig
from agents.services.todoist_manager import TodoistClient
from langchain.tools import BaseTool

from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)


TODOIST_DESCRIPTION = """
Todoist is used for personal tasks and reminders management.
Example topics covered in todoist:
- Personal tasks
- Reminders
- Shopping lists
- Appointments
- Events
- Goals
- Quick notes
"""


class ListTasksFilters(BaseModel):
    filter: str = Field(
        description="Filter for the tasks in todoist application. Can be 'overdue', 'due_today', 'today | overdue'. The main and most important view is: 'due today | overdue | @fake_date'"
    )


class ListTasksTool(BaseTool):
    name: str = "list_tasks"
    description: str = f"List all tasks from todoist application. {TODOIST_DESCRIPTION} ALWAYS check for overdue tasks to know if you should do something about them."
    args_schema: Type[BaseModel] = ListTasksFilters

    def _run(
        self,
        filter: str,
        config: RunnableConfig,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> List[dict]:
        tasks = TodoistClient().get_tasks(filter)
        return [t.to_dict() for t in tasks]


class CreateTaskPayload(BaseModel):
    name: str = Field(
        description="The name of the task. ALWAYS started with emoji. Example: 🛒 Buy groceries, 📚 Read a book, 📅 Schedule a meeting"
    )
    due_date: str = Field(description="The due date of the task. Format: YYYY-MM-DD")
    description: Optional[str] = Field(description="The description of the task")


class CreateTaskTool(BaseTool):
    name: str = "create_task"
    description: str = (
        f"Create a new task in todoist application. {TODOIST_DESCRIPTION}"
    )
    args_schema: Type[BaseModel] = CreateTaskPayload

    def _run(
        self,
        name: str,
        due_date: str,
        config: RunnableConfig,
        description: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict:
        task = TodoistClient().add_task(name, due_date, description)
        return task.to_dict()


class CompleteTaskPayload(BaseModel):
    task_id: str = Field(
        description="The id of the task to complete. ALWAYS use the id of the task if you know one. If not first use the list_tasks function to get the id of the task."
    )


class CompleteTaskTool(BaseTool):
    name: str = "complete_task"
    description: str = f"Complete a task in todoist application. {TODOIST_DESCRIPTION}"
    args_schema: Type[BaseModel] = CompleteTaskPayload

    def _run(
        self,
        task_id: str,
        config: RunnableConfig,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict:
        TodoistClient().complete_task(task_id)
        return {"status": "success"}

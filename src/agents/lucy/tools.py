from pydantic import BaseModel, Field
from typing import List, Optional, Type
from langchain_core.tools import tool
from langchain_core.runnables.config import RunnableConfig
import tiktoken
from langchain_core.messages import get_buffer_string
from agents.modules.tasks_manager import TodoistClient
from agents.state import AgentState
from agents.common import get_user_id
from langchain.tools import tool, BaseTool
from agents.modules.memory_manager import KnowledgeTriple, MemoryManager

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

class MessageWithMemory(BaseModel):
    message: str = Field(description="The message that was just received")
    context: str = Field(description="The context of the message based on the current conversation")
    memories: List[KnowledgeTriple] = Field(description="The memories that were retrieved from the vectorstore. Never empty list. I called at least one memory should be retrieved from user message.")


class SaveMemoryTool(BaseTool):
    name: str = "save_memory"
    description: str = "Save memory to vectorstore for later semantic retrieval."
    args_schema: Type[BaseModel] = MessageWithMemory

    def _run(self, message: str, context: str, memories: List[KnowledgeTriple], config: RunnableConfig, run_manager: Optional[CallbackManagerForToolRun] = None) -> MessageWithMemory:
        print("Saving memory", memories)
        MemoryManager().save_memories(memories, context, get_user_id(config))
        return MessageWithMemory(message=message, context=context, memories=memories)


class RecallMemoriesTool(BaseTool):
    name: str = "recall_memories"
    description: str = "Search for relevant memories about the user."

    def _run(self, query: str, config: RunnableConfig, run_manager: Optional[CallbackManagerForToolRun] = None) -> List[dict]:
        user_id = get_user_id(config)
        documents = MemoryManager().recall_memories(query, user_id)
        return documents



def load_memories(state: AgentState, config: RunnableConfig) -> AgentState:
    """Load memories for the current conversation.

    Args:
        state (schemas.State): The current state of the conversation.
        config (RunnableConfig): The runtime configuration for the agent.

    Returns:
        State: The updated state with loaded memories.
    """

    tokenizer = tiktoken.encoding_for_model("gpt-4o")
    convo_str = get_buffer_string(state["messages"])
    convo_str = tokenizer.decode(tokenizer.encode(convo_str)[:2048])
    memories = MemoryManager().recall_memories(convo_str, get_user_id(config))
    return {
        "recall_memories": memories,
        "messages": state["messages"],
    }


class ListTasksFilters(BaseModel):
    filter: str = Field(description="Filter for the tasks. Can be 'overdue', 'due_today', 'today | overdue'")

class ListTasksTool(BaseTool):
    name: str = "list_tasks"
    description: str = "List all tasks from todoist application. ALWAYS check for overdue tasks to know if you should do something about them."
    args_schema: Type[BaseModel] = ListTasksFilters

    def _run(self, filter: str, config: RunnableConfig, run_manager: Optional[CallbackManagerForToolRun] = None) -> List[dict]:
        print("--------------> Calling list_tasks tool", filter)
        tasks = TodoistClient().get_tasks(filter)
        return [t.to_dict() for t in tasks]

class CreateTaskPayload(BaseModel):
    name: str = Field(description="The name of the task. ALWAYS started with emoji. Example: 🛒 Buy groceries, 📚 Read a book, 📅 Schedule a meeting")
    due_date: str = Field(description="The due date of the task. Format: YYYY-MM-DD")
    description: Optional[str] = Field(description="The description of the task")

class CreateTaskTool(BaseTool):
    name: str = "create_task"
    description: str = "Create a new task in todoist application."
    args_schema: Type[BaseModel] = CreateTaskPayload

    def _run(self, name: str, due_date: str, config: RunnableConfig, description: Optional[str] = None, run_manager: Optional[CallbackManagerForToolRun] = None) -> dict:
        task = TodoistClient().add_task(name, due_date, description)
        return task.to_dict()


TOOLS = [SaveMemoryTool(), RecallMemoriesTool(), ListTasksTool(), CreateTaskTool()]
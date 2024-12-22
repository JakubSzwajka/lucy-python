from pydantic import BaseModel, Field
from typing import List, Optional, Type
from langchain_core.runnables.config import RunnableConfig
import tiktoken
from langchain_core.messages import get_buffer_string
from agents.modules.tasks_manager import TodoistClient
from agents.modules.trello_manager import TrelloManager
from agents.state import AgentState
from agents.common import get_user_id
from langchain.tools import BaseTool
from agents.modules.memory_manager import KnowledgeTriple, MemoryManager

from langchain.callbacks.manager import (
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
        print("NEW MEMORY", memories)
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

class CompleteTaskPayload(BaseModel):
    task_id: str = Field(description="The id of the task to complete. ALWAYS use the id of the task if you know one. If not first use the list_tasks function to get the id of the task.")

class CompleteTaskTool(BaseTool):
    name: str = "complete_task"
    description: str = "Complete a task in todoist application."
    args_schema: Type[BaseModel] = CompleteTaskPayload

    def _run(self, task_id: str, config: RunnableConfig, run_manager: Optional[CallbackManagerForToolRun] = None) -> dict:
        TodoistClient().complete_task(task_id)
        return {"status": "success"}



class ListProjectsTool(BaseTool):
    name: str = "list_projects"
    description: str = "List all projects."

    def _run(self, config: RunnableConfig, run_manager: Optional[CallbackManagerForToolRun] = None) -> List[dict]:
        client = TrelloManager()
        boards = client.list_boards_in_workspace()
        return [{
            "id": b.id,
            "name": b.name,
            "description": b.description,
            "url": b.url,
        } for b in boards]

class GetBoardToolPayload(BaseModel):
    board_id: str = Field(description="The id of the board (project) to get. If you don't know the id, use the list_projects function to get the id of a board.")

class GetBoardTool(BaseTool):
    name: str = "get_board"
    description: str = "Get a board by its id. Return all lists and cards in the board."
    args_schema: Type[BaseModel] = GetBoardToolPayload

    def _run(self, board_id: str, config: RunnableConfig, run_manager: Optional[CallbackManagerForToolRun] = None) -> dict:
        client = TrelloManager()
        board = client.get_board(board_id)
        lists = board.all_lists()
        cards = board.all_cards()
        return {
            "id": board.id,
            "name": board.name,
            "description": board.description,
            "url": board.url,
            "lists": [{
                "id": l.id,
                "name": l.name,
            } for l in lists],
            "cards": [{
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "due_date": c.due,
                "archived": c.closed,
                "url": c.url,
            } for c in cards],
        }

class CreateCardPayload(BaseModel):
    list_id: str = Field(description="The id of the list to create the card in. If you don't know the id, use the get_board function to get the id of a list.")
    name: str = Field(description="The name of the card. ALWAYS started with emoji. Example: 🛒 Buy groceries, 📚 Read a book, 📅 Schedule a meeting")
    description: str = Field(description="The description of the card")
    due_date: Optional[str] = Field(description="The due date of the card. Format: YYYY-MM-DD")

class CreateCardTool(BaseTool):
    name: str = "create_card"
    description: str = "Create a new card in a list."
    args_schema: Type[BaseModel] = CreateCardPayload

    def _run(self, config: RunnableConfig, list_id: str, name: str, description: str, due_date: Optional[str] = None, run_manager: Optional[CallbackManagerForToolRun] = None) -> dict:
        client = TrelloManager()
        card = client.create_card_in_list(list_id, name, description, due=due_date)
        return {
            "id": card.id,
            "name": card.name,
            "description": card.description,
            "due_date": card.due,
            "closed": card.closed,
            "url": card.url,
        }

class UpdateCardPayload(BaseModel):
    card_id: str = Field(description="The id of the card to update. If you don't know the id, use the get_board function to get the id of a card.")
    name: Optional[str] = Field(description="The name of the card. ALWAYS started with emoji. Example: 🛒 Buy groceries, 📚 Read a book, 📅 Schedule a meeting")
    description: Optional[str] = Field(description="The description of the card")
    due_date: Optional[str] = Field(description="The due date of the card. Format: YYYY-MM-DD")
    closed: Optional[bool] = Field(description="The closed (done) status of the card. True if the card is closed (done), False otherwise.")
    new_list_id: Optional[str] = Field(description="The id of the new list to move the card to. If you don't know the id, use the get_board function to get the id of a list.")

class UpdateCardTool(BaseTool):
    name: str = "update_card"
    description: str = "Update a card in a list."
    args_schema: Type[BaseModel] = UpdateCardPayload


    def _run(self, config: RunnableConfig, card_id: str, name: Optional[str] = None, description: Optional[str] = None, due_date: Optional[str] = None, closed: Optional[bool] = None, new_list_id: Optional[str] = None, run_manager: Optional[CallbackManagerForToolRun] = None) -> dict:
        client = TrelloManager()
        card = client.update_card(card_id, name, description, due_date, closed, new_list_id)
        return {
            "id": card.id,
            "name": card.name,
            "description": card.description,
            "due_date": card.due,
            "closed": card.closed,
            "url": card.url,
        }

TOOLS = [
    SaveMemoryTool(),
    RecallMemoriesTool(),
    ListTasksTool(),
    CreateTaskTool(),
    CompleteTaskTool(),
    ListProjectsTool(),
    GetBoardTool(),
    CreateCardTool(),
]


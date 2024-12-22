from pydantic import BaseModel, Field
from typing import List, Optional, Type
from langchain_core.runnables.config import RunnableConfig
from agents.services.trello_manager import (
    TrelloBoard,
    TrelloCard,
    TrelloCheckListItem,
    TrelloManager,
)
from langchain.tools import BaseTool

from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)

TRELLO_DESCRIPTION = """
Trello is used for project management (trello boards). All projects user has access to are listed here. Projects might cover different topics like:
- Personal projects
- Work projects
- Family projects
- Home projects
- Health projects

In general the difference is that project is more long term then single todoist task.
Each project (board) has multiple lists (columns) and each list has multiple cards (tasks).
In most of cases, lists represent different stages/statuses of the card.

Additionaly, each card can have multiple checklists. Checklists are used to track the progress of the card.
Each checklist has multiple items. Each item can be checked or unchecked. Tread this as some kind of sub-tasks.
For simplicity lets ALWAYS use only one checklist per card.
"""


class ListProjectsTool(BaseTool):
    name: str = "list_projects"
    description: str = f"List all projects. {TRELLO_DESCRIPTION}"

    def _run(
        self,
        config: RunnableConfig,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> List[TrelloBoard]:
        client = TrelloManager()
        boards = client.list_boards_in_workspace()
        return boards


class GetBoardToolPayload(BaseModel):
    board_id: str = Field(
        description="The id of the board (project) to get. If you don't know the id, use the list_projects function to get the id of a board."
    )


class GetBoardTool(BaseTool):
    name: str = "get_board"
    description: str = f"Get a board by its id. Return all lists and cards in the board. {TRELLO_DESCRIPTION}"
    args_schema: Type[BaseModel] = GetBoardToolPayload

    def _run(
        self,
        board_id: str,
        config: RunnableConfig,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> TrelloBoard:
        client = TrelloManager()
        board = client.get_board(board_id)
        return board


class CreateCardPayload(BaseModel):
    list_id: str = Field(
        description="The id of the list to create the card in. If you don't know the id, use the get_board function to get the id of a list."
    )
    name: str = Field(
        description="The name of the card. ALWAYS started with emoji. Example: 🛒 Buy groceries, 📚 Read a book, 📅 Schedule a meeting"
    )
    description: str = Field(description="The description of the card")
    due_date: Optional[str] = Field(
        description="The due date of the card. Format: YYYY-MM-DD"
    )


class CreateCardTool(BaseTool):
    name: str = "create_card"
    description: str = f"Create a new card in a list. {TRELLO_DESCRIPTION}"
    args_schema: Type[BaseModel] = CreateCardPayload

    def _run(
        self,
        config: RunnableConfig,
        list_id: str,
        name: str,
        description: str,
        due_date: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> TrelloCard:
        client = TrelloManager()
        card = client.create_card_in_list(list_id, name, description, due=due_date)
        return card


class UpdateCardPayload(BaseModel):
    card_id: str = Field(
        description="The id of the card to update. If you don't know the id, use the get_board function to get the id of a card."
    )
    name: Optional[str] = Field(
        description="The name of the card. ALWAYS started with emoji. Example: 🛒 Buy groceries, 📚 Read a book, 📅 Schedule a meeting"
    )
    description: Optional[str] = Field(description="The description of the card")
    due_date: Optional[str] = Field(
        description="The due date of the card. Format: YYYY-MM-DD"
    )
    closed: Optional[bool] = Field(
        description="The closed (done) status of the card. True if the card is closed (done), False otherwise."
    )
    new_list_id: Optional[str] = Field(
        description="The id of the new list to move the card to. If you don't know the id, use the get_board function to get the id of a list."
    )

    checklist_items: Optional[List[TrelloCheckListItem]] = Field(
        description="The items of the default checklist to be updated. Consist of name and checked fields. If no item with given name exists, it will be added so please keep exact name if you want to update it."
    )


class UpdateCardTool(BaseTool):
    name: str = "update_card"
    description: str = f"Update a card in a list. {TRELLO_DESCRIPTION}"
    args_schema: Type[BaseModel] = UpdateCardPayload

    def _run(
        self,
        config: RunnableConfig,
        card_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
        closed: Optional[bool] = None,
        new_list_id: Optional[str] = None,
        checklist_items: Optional[List[TrelloCheckListItem]] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> TrelloCard:
        client = TrelloManager()
        card = client.update_card(
            card_id=card_id,
            name=name,
            desc=description,
            due=due_date,
            archived=closed,
            new_list_id=new_list_id,
            checklist_items=checklist_items,
        )
        return card

import os
from typing import Optional, TypedDict, List
from trello import TrelloClient, Board, Card, Checklist

# The "slug"/ID of the workspace (organization) you want to get boards from
ORGANIZATION_NAME_OR_ID = "kuba_szwajka"


class TrelloCheckListItem(TypedDict):
    name: str
    checked: bool


class TrelloCheckList(TypedDict):
    id: str
    name: str
    items: List[TrelloCheckListItem]


class TrelloCard(TypedDict):
    id: str
    name: str
    description: str
    due_date: str
    closed: bool
    url: str
    checklists: List[TrelloCheckList]


class TrelloList(TypedDict):
    id: str
    name: str
    cards: List[TrelloCard]


class TrelloBoard(TypedDict):
    id: Optional[str]
    name: str
    description: str
    url: str
    lists: List[TrelloList]


class TrelloManager:
    def __init__(self):
        self.client = TrelloClient(
            api_key=os.getenv("TRELLO_API_KEY"),
            api_secret=os.getenv("TRELLO_SECRET_KEY"),
            token=os.getenv("TRELLO_LUCY_TOKEN"),
        )

    def list_boards_in_workspace(self) -> List[TrelloBoard]:
        """
        Returns all boards in the specified workspace.
        """
        organization = self.client.get_organization(ORGANIZATION_NAME_OR_ID)
        boards = organization.all_boards()
        return [
            TrelloBoard(
                id=b.id,
                name=b.name,
                description=b.description,
                url=b.url,
                lists=[],
            )
            for b in boards
        ]

    def get_board(self, board_id: str) -> TrelloBoard:
        """
        Returns a board by its ID.
        """
        board = self.client.get_board(board_id)
        return TrelloBoard(
            id=board.id,
            name=board.name,
            description=board.description,
            url=board.url,
            lists=[
                TrelloList(
                    id=l.id,
                    name=l.name,
                    cards=[
                        TrelloCard(
                            id=c.id,
                            name=c.name,
                            description=c.description,
                            due_date=c.due,
                            closed=c.closed,
                            url=c.url,
                            checklists=[
                                TrelloCheckList(
                                    id=cl.id,
                                    name=cl.name,
                                    items=[
                                        TrelloCheckListItem(
                                            name=item["name"],
                                            checked=item["state"],
                                        )
                                        for item in cl.items
                                    ],
                                )
                                for cl in c.checklists
                            ],
                        )
                        for c in l.list_cards()
                    ],
                )
                for l in board.all_lists()
            ],
        )

    def create_card_in_list(
        self, list_id: str, name: str, desc: str = "", due: Optional[str] = None
    ) -> TrelloCard:
        """
        Creates a new Trello card in the specified list.

        :param list_id: ID of the Trello list where the card will be created.
        :param name: Name (title) of the card to create.
        :param desc: Optional description for the card.
        :return: The newly created Card object.
        """
        trello_list = self.client.get_list(list_id)
        card = trello_list.add_card(name=name, desc=desc, due=due or "")
        return TrelloCard(
            id=card.id,
            name=card.name,
            description=card.description,
            due_date=card.due,
            closed=card.closed,
            url=card.url,
            checklists=[
                TrelloCheckList(
                    id=cl.id,
                    name=cl.name,
                    items=[
                        TrelloCheckListItem(
                            name=item["name"],
                            checked=item["state"],
                        )
                        for item in card.checklists[0].items
                    ],
                )
                for cl in card.checklists
            ],
        )

    def update_card(
        self,
        card_id: str,
        name: Optional[str] = None,
        desc: Optional[str] = None,
        due: Optional[str] = None,
        archived: Optional[bool] = None,
        new_list_id: Optional[str] = None,
        checklist_items: Optional[List[TrelloCheckListItem]] = None,
    ) -> TrelloCard:
        card = self.client.get_card(card_id)
        if name:
            card.set_name(name)
        if desc:
            card.set_description(desc)
        if due:
            card.set_due(due)
        if archived:
            card.set_closed(archived)
        if new_list_id:
            card.change_list(new_list_id)

        if checklist_items:
            if len(card.checklists) == 0:
                checklist = card.add_checklist("Default", items=[])
            else:
                checklist = card.checklists[0]

            for item in checklist_items:
                existing_item = next(
                    (i for i in checklist.items if i["name"] == item["name"]), None
                )
                if existing_item:
                    checklist.set_checklist_item(existing_item["name"], item["checked"])
                else:
                    checklist.add_checklist_item(item["name"], item["checked"])

        return TrelloCard(
            id=card.id,
            name=card.name,
            description=card.description,
            due_date=card.due,
            closed=card.closed,
            url=card.url,
            checklists=[
                TrelloCheckList(
                    id=cl.id,
                    name=cl.name,
                    items=[
                        TrelloCheckListItem(
                            name=item["name"],
                            checked=item["state"],
                        )
                        for item in cl.items
                    ],
                )
                for cl in card.checklists
            ],
        )

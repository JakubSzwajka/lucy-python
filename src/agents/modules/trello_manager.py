import os
from typing import Optional
from trello import TrelloClient, Board, Card, List

# The "slug"/ID of the workspace (organization) you want to get boards from
ORGANIZATION_NAME_OR_ID = "kuba_szwajka"


class TrelloManager:
    def __init__(self):
        self.client = TrelloClient(
            api_key=os.getenv("TRELLO_API_KEY"),
            api_secret=os.getenv("TRELLO_SECRET_KEY"),
            token=os.getenv("TRELLO_LUCY_TOKEN")
        )

    def list_boards_in_workspace(self):
        """
        Returns all boards in the specified workspace.
        """
        organization = self.client.get_organization(ORGANIZATION_NAME_OR_ID)
        return organization.all_boards()

    def get_board(self, board_id: str):
        """
        Returns a board by its ID.
        """
        return self.client.get_board(board_id)

    def create_card_in_list(self, list_id: str, name: str, desc: str = "", due: Optional[str] = None) -> Card:
        """
        Creates a new Trello card in the specified list.

        :param list_id: ID of the Trello list where the card will be created.
        :param name: Name (title) of the card to create.
        :param desc: Optional description for the card.
        :return: The newly created Card object.
        """
        trello_list = self.client.get_list(list_id)
        return trello_list.add_card(name=name, desc=desc, due=due or "")

    def update_card(self, card_id: str, name: Optional[str] = None, desc: Optional[str] = None, due: Optional[str] = None, archived: Optional[bool] = None, new_list_id: Optional[str] = None) -> Card:
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
        return card

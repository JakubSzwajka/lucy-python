from langgraph.graph import  MessagesState
from typing import List

from agents.lucy.document import  ThoughtsDoc


class AgentState(MessagesState):
    recall_memories: List[dict]
    thoughts_doc: ThoughtsDoc
    thoughts: str

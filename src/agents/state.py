from langgraph.graph import MessagesState
from typing import List


class AgentState(MessagesState):
    recall_memories: List[dict]
    thoughts: str

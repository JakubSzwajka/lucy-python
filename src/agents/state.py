from langgraph.graph import START, END, MessagesState, StateGraph
from typing import List


class AgentState(MessagesState):
    recall_memories: List[dict]

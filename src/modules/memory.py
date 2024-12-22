from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class MemoryState(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(MemoryState)

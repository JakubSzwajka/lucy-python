from typing import Literal, Optional, TypedDict
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langgraph.graph import MessagesState, END
from langgraph.types import Command
from langchain_core.runnables.config import RunnableConfig

from agents.state import AgentState


def get_user_id(config: RunnableConfig):
    configurable = config.get("configurable")
    if configurable is None:
        raise ValueError("Configurable is not set")
    user_id = configurable.get("user_id")
    if user_id is None:
        raise ValueError("User ID is not set")
    return user_id


def make_supervisor_node(
    llm: BaseChatModel, members: list[str], prompt: Optional[str] = None
):
    options = ["FINISH"] + members
    system_prompt = (
        prompt
        or """
You are a supervisor tasked with managing a conversation between the
following workers: {members}. Given the following user request,
respond with the worker to act next. Each worker will perform a
task and respond with their results and status. When finished,
respond with FINISH."

    """
    )

    class Router(TypedDict):
        """Worker to route to next. If no workers needed, route to FINISH."""

        next: Literal[*options]  # type: ignore

    def supervisor_node(state: MessagesState) -> Command[Literal[*members, "__end__"]]:  # type: ignore
        """An LLM-based router."""
        messages = [
            {"role": "system", "content": system_prompt},
        ] + state["messages"]
        response = llm.with_structured_output(Router).invoke(messages)
        goto = response["next"]  # type: ignore
        if goto == "FINISH":
            goto = END

        return Command(goto=goto)

    return supervisor_node


def get_tool_router(tool_node: str, else_node: str):
    """Determine whether to use tools or end the conversation based on the last message.

    Args:
        state (schemas.State): The current state of the conversation.

    Returns:
        Literal["tools", "__end__"]: The next step in the graph.
    """

    def router(state: AgentState):
        msg = state["messages"][-1]
        if isinstance(msg, AIMessage) and msg.tool_calls:
            return tool_node
        return else_node

    return router

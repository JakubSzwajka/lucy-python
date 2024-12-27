from pydantic import BaseModel
from typing import Optional, Type
from langchain_core.runnables.config import RunnableConfig
from agents.state import AgentState
from langchain.tools import BaseTool
from langgraph.types import Command
from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from langchain_core.messages import AIMessage, BaseMessage


class ConversationDocContentUpdatePayload(BaseModel):
    content: str


class UpdateConversationDocTool(BaseTool):
    name: str = "update_conversation_doc"
    description: str = "Update the conversation document with the latest message and context. Use this tool quite often to keep track of key takeaways from the conversation. Put your thougts and reflextions about the interaction with the user here. Treat it as your personal notebook."
    args_schema: Type[BaseModel] = ConversationDocContentUpdatePayload

    def _run(
        self,
        state: AgentState,
        content: str,
        config: RunnableConfig,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ):
        pass


def make_reflection(message: BaseMessage, state: AgentState):
    doc = state.get("thoughts_doc", None)

    if isinstance(message, AIMessage):
        for tool_call in message.tool_calls:
            if tool_call["name"] == "update_conversation_doc":
                content = tool_call["args"]["content"]
                doc.add_thought(content)
    return doc


SUZIE_TOOLS = [
    UpdateConversationDocTool(),
]

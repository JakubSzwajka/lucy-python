import uuid
from pydantic import BaseModel, Field
from typing import List, Optional, Type
from langchain_core.runnables.config import RunnableConfig
import tiktoken
from langchain_core.messages import get_buffer_string
from agents.state import AgentState
from agents.common import get_user_id
from langchain.tools import BaseTool
from agents.services.qdrant_manager import KnowledgeTriple, MemoryManager
from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)

from agents.services.airtable_manager import AirtableManager


class MessageWithMemory(BaseModel):
    message: str = Field(description="The message that was just received")
    context: str = Field(
        description="The context of the message based on the current conversation"
    )
    memories: List[KnowledgeTriple] = Field(
        description="The memories that were retrieved from the vectorstore. Never empty list. I called at least one memory should be retrieved from user message."
    )


class SaveMemoryTool(BaseTool):
    name: str = "save_memory"
    description: str = "Save memory to vectorstore for later semantic retrieval. Use this tool to save memories about the user to better understand his needs, relations, facts about him etc. All stuff that might help to provide better conversation experience."
    args_schema: Type[BaseModel] = MessageWithMemory

    def _run(
        self,
        message: str,
        context: str,
        memories: List[KnowledgeTriple],
        config: RunnableConfig,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> MessageWithMemory:
        print("NEW MEMORY", memories)
        MemoryManager().save_memories(memories, context, get_user_id(config))
        AirtableManager().add_to_memories(memories, context)
        return MessageWithMemory(message=message, context=context, memories=memories)


class RecallMemoriesTool(BaseTool):
    name: str = "recall_memories"
    description: str = "Search for relevant memories about the user."

    def _run(
        self,
        query: str,
        config: RunnableConfig,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> List[dict]:
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

    # ----------- conversation doc ------------
    thread_id = config.get("metadata", {}).get("thread_id", None)
    if not thread_id:
        thread_id = str(uuid.uuid4())

    return {
        "recall_memories": memories,
        "messages": state["messages"],
        "thoughts": "",
    }

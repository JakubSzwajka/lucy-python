from datetime import datetime
from enum import StrEnum
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import ToolNode
from agents.state import AgentState
from agents.lucy.prompts import MASTER_PROMPT
from agents.lucy.tools import load_memories, TOOLS
from config import GlobalConfig
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import tools_condition
from agents.common import route_tools
from langchain_core.messages import AIMessageChunk, ToolCallChunk, AIMessage

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", MASTER_PROMPT),
        ("placeholder", "{messages}"),
    ]
)

class Agents(StrEnum):
    LUCY = "lucy"

class ToolNodes(StrEnum):
    LOAD_MEMORIES = "load_memories"
    SAVE_MEMORY = "save_memory"
    RECALL_MEMORIES = "recall_memories"

class Lucy:
    def __init__(self, checkpointer: AsyncPostgresSaver):
        self.tools = TOOLS
        self.model = ChatOpenAI(model="gpt-4o")
        self.model_with_tools = self.model.bind_tools(self.tools)
        self.agent = self._get_agent(checkpointer)

    def _get_agent(self, checkpointer: AsyncPostgresSaver):
        model = ChatOpenAI(model="gpt-4o")
        model_with_tools = model.bind_tools(self.tools)

        async def _call_model(state: AgentState):
            memories_str = ""
            for memory in state["recall_memories"]:
                memories_str += f"""<memory>
    <id>{memory.get('id')}</id>
    <subject>{memory.get('subject')}</subject>
    <predicate>{memory.get('predicate')}</predicate>
    <object>{memory.get('object_')}</object>
    <context>{memory.get('context')}</context>
    <created_at>{memory.get('created_at')}</created_at>
    <updated_at>{memory.get('updated_at')}</updated_at>
</memory>\n"""
            memories_str = f"<recall_memory>\n{memories_str}\n</recall_memory>"
            chain = prompt | model_with_tools
            invoke_data = {
                "messages": state["messages"],
                "recalled_memories": memories_str,
                "assistant_name": GlobalConfig.ASSISTANT_NAME,
                "user_name": GlobalConfig.USER_NAME,
                "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "current_weekday": datetime.now().strftime("%A"),
                "tools_description": self._get_tools_description_string(),
            }

            # Switch to an async invoke method so we don't block
            # response = await chain.ainvoke(invoke_data)
            # return {"messages": response}
            # async for chunk in chain.astream(invoke_data):
            #     yield chunk

            response = await chain.ainvoke(invoke_data)
            return {"messages": response}

        main_graph = StateGraph(state_schema=AgentState)
        main_graph.add_node(ToolNodes.LOAD_MEMORIES, load_memories)
        main_graph.add_node(Agents.LUCY, _call_model)
        main_graph.add_node("tools", ToolNode(self.tools))

        main_graph.add_edge(START, ToolNodes.LOAD_MEMORIES)
        main_graph.add_edge(ToolNodes.LOAD_MEMORIES, Agents.LUCY)
        main_graph.add_conditional_edges(Agents.LUCY, route_tools, ["tools", END])
        main_graph.add_edge("tools", Agents.LUCY)

        app = main_graph.compile(checkpointer=checkpointer)
        return app

    def _get_tools_description_string(self):
        tools_info = ""
        for tool in self.tools:
            tools_info += f"""<tool>
                <name>{tool.name}</name>
                <description>{tool.description}</description>
            </tool>\n"""
        return tools_info


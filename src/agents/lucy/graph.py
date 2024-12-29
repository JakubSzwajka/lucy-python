from datetime import datetime
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import ToolNode
from agents.state import AgentState
from agents.lucy.prompts.master_prompt import MASTER_PROMPT
from agents.lucy.prompts.reflection_prompt import REFLECTION_MASTER_PROMPT
from agents.lucy.tools import LUCY_TOOLS
from agents.lucy.tools.memory import load_memories
from config import GlobalConfig
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from agents.common import get_tool_router

from agents import Agents, ToolNodes

lucy_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", MASTER_PROMPT),
        ("placeholder", "{messages}"),
    ]
)

reflection_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", REFLECTION_MASTER_PROMPT),
        ("placeholder", "{messages}"),
    ]
)


class Lucy:
    def __init__(self, checkpointer: AsyncPostgresSaver):
        self.model = ChatOpenAI(model="gpt-4o")
        self.model_with_tools = self.model.bind_tools(LUCY_TOOLS)
        self.agent = self._get_agent(checkpointer)

    def _get_memories_string(self, state: AgentState):
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
        return f"<recall_memory>\n{memories_str}\n</recall_memory>"

    def _get_invoke_data(self, state: AgentState, tools):
        memories_str = self._get_memories_string(state)
        return {
            "messages": state["messages"],
            "recalled_memories": memories_str,
            "assistant_name": GlobalConfig.ASSISTANT_NAME,
            "user_name": GlobalConfig.USER_NAME,
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "current_weekday": datetime.now().strftime("%A"),
            "tools_description": self._get_tools_description_string(tools),
            "thoughts_and_observations": state["thoughts"],
        }

    def _get_agent(self, checkpointer: AsyncPostgresSaver):
        lucy_model = ChatOpenAI(model="gpt-4o")
        lucy_model = lucy_model.bind_tools(LUCY_TOOLS)
        lucy_model = lucy_model.with_config(tags=["lucy"])

        reflection_model = ChatOpenAI(model="gpt-4o")

        async def _call_reflection(state: AgentState):
            chain = reflection_prompt | reflection_model
            invoke_data = self._get_invoke_data(state, [])
            response = chain.invoke(invoke_data)
            return {"thoughts": response.content}

        async def _call_lucy(state: AgentState):
            chain = lucy_prompt | lucy_model
            invoke_data = self._get_invoke_data(state, LUCY_TOOLS)

            response = await chain.ainvoke(invoke_data)
            return {"messages": response}

        main_graph = StateGraph(state_schema=AgentState)
        main_graph.add_node(ToolNodes.LOAD_MEMORIES, load_memories)
        main_graph.add_node(Agents.LUCY, _call_lucy)
        main_graph.add_node(ToolNodes.REFLECT_ON_INTERACTION, _call_reflection)
        main_graph.add_node(ToolNodes.LUCY_TOOLS, ToolNode(LUCY_TOOLS))

        main_graph.add_edge(START, ToolNodes.LOAD_MEMORIES)
        main_graph.add_edge(ToolNodes.LOAD_MEMORIES, ToolNodes.REFLECT_ON_INTERACTION)
        main_graph.add_edge(ToolNodes.REFLECT_ON_INTERACTION, Agents.LUCY)

        main_graph.add_conditional_edges(
            Agents.LUCY,
            get_tool_router(ToolNodes.LUCY_TOOLS, END),
            [ToolNodes.LUCY_TOOLS, END],
        )

        main_graph.add_edge(ToolNodes.LUCY_TOOLS, Agents.LUCY)

        main_graph.add_edge(Agents.LUCY, END)

        app = main_graph.compile(checkpointer=checkpointer)
        return app

    def _get_tools_description_string(self, tools):
        tools_info = ""
        for tool in tools:
            tools_info += f"""<tool>
                <name>{tool.name}</name>
                <description>{tool.description}</description>
            </tool>\n"""
        return tools_info

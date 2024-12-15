from typing_extensions import TypedDict
from IPython.display import Image, display
import os
from typing import List
import uuid
from getpass import getpass
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore, VectorStore
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, MessagesState, StateGraph
from langchain_core.runnables.config import RunnableConfig
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
import tiktoken
from langchain_core.messages import get_buffer_string
from langgraph.prebuilt import ToolNode
import matplotlib.pyplot as plt
import networkx as nx


tokenizer = tiktoken.encoding_for_model("gpt-4o")


class _RecallVectorStoreSingleton:
    _instance = None

    @staticmethod
    def get_instance():
        if _RecallVectorStoreSingleton._instance is None:
            _RecallVectorStoreSingleton._instance = InMemoryVectorStore(OpenAIEmbeddings())
        return _RecallVectorStoreSingleton._instance

recall_vector_store = _RecallVectorStoreSingleton.get_instance()

class State(MessagesState):
    # add memories that will be retrieved based on the conversation context
    recall_memories: List[str]

# Define the prompt template for the agent
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant with advanced long-term memory"
            " capabilities. Powered by a stateless LLM, you must rely on"
            " external memory to store information between conversations."
            " Utilize the available memory tools to store and retrieve"
            " important details that will help you better attend to the user's"
            " needs and understand their context.\n\n"
            "Memory Usage Guidelines:\n"
            "1. Actively use memory tools (save_core_memory, save_recall_memory)"
            " to build a comprehensive understanding of the user.\n"
            "2. Make informed suppositions and extrapolations based on stored"
            " memories.\n"
            "3. Regularly reflect on past interactions to identify patterns and"
            " preferences.\n"
            "4. Update your mental model of the user with each new piece of"
            " information.\n"
            "5. Cross-reference new information with existing memories for"
            " consistency.\n"
            "6. Prioritize storing emotional context and personal values"
            " alongside facts.\n"
            "7. Use memory to anticipate needs and tailor responses to the"
            " user's style.\n"
            "8. Recognize and acknowledge changes in the user's situation or"
            " perspectives over time.\n"
            "9. Leverage memories to provide personalized examples and"
            " analogies.\n"
            "10. Recall past challenges or successes to inform current"
            " problem-solving.\n\n"
            "When asked to show memory use show_memory tool. \n"
            "## Recall Memories\n"
            "Recall memories are contextually retrieved based on the current"
            " conversation:\n{recall_memories}\n\n"
            "## Instructions\n"
            "Engage with the user naturally, as a trusted colleague or friend."
            " There's no need to explicitly mention your memory capabilities."
            " Instead, seamlessly incorporate your understanding of the user"
            " into your responses. Be attentive to subtle cues and underlying"
            " emotions. Adapt your communication style to match the user's"
            " preferences and current emotional state. Use tools to persist"
            " information you want to retain in the next conversation. If you"
            " do call tools, all text preceding the tool call is an internal"
            " message. Respond AFTER calling the tool, once you have"
            " confirmation that the tool completed successfully.\n\n",
        ),
        ("placeholder", "{messages}"),
    ]
)
# Set OpenAI API Key
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass("Enter your OpenAI API key: ")

class KnowledgeTriple(TypedDict):
    subject: str
    predicate: str
    object_: str


@tool
def save_recall_memory(memories: List[KnowledgeTriple], config: RunnableConfig) -> str:
    """Save memory to vectorstore for later semantic retrieval."""
    user_id = get_user_id(config)
    print('---------------> saving memory:', memories)
    for memory in memories:
        serialized = " ".join(memory.values())
        document = Document(
            serialized,
            id=str(uuid.uuid4()),
            metadata={
                "user_id": user_id,
                **memory,
            },
        )
        recall_vector_store.add_documents([document])
    return memories


@tool
def search_recall_memories(query: str, config: RunnableConfig) -> List[str]:
    """Search for relevant memories."""
    user_id = get_user_id(config)

    print('---------------> searching memories for query:', query)

    def _filter_function(doc: Document) -> bool:
        return doc.metadata.get("user_id") == user_id

    documents = recall_vector_store.similarity_search(
        query, k=3, filter=_filter_function
    )
    return [document.page_content for document in documents]

def show_memory():
    """Show all memories."""
    # Fetch records

    records = recall_vector_store.similarity_search(
        "Kuba", k=10
    )

    # Plot graph
    plt.figure(figsize=(6, 4), dpi=80)
    G = nx.DiGraph()

    for record in records:
        G.add_edge(
            record.metadata["subject"],
            record.metadata["object_"],
            label=record.metadata["predicate"],
        )

    pos = nx.spring_layout(G)
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=3000,
        node_color="lightblue",
        font_size=10,
        font_weight="bold",
        arrows=True,
    )
    edge_labels = nx.get_edge_attributes(G, "label")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red")
    plt.show()
    return "Memory graph plotted"

def get_user_id(config: RunnableConfig) -> str:
    # user_id = config["configurable"].get("user_id")
    # if user_id is None:
    #     raise ValueError("User ID needs to be provided to save a memory.")

    # return user_id
    return "abc123"

def load_memories(state: State, config: RunnableConfig) -> State:
    """Load memories for the current conversation.

    Args:
        state (schemas.State): The current state of the conversation.
        config (RunnableConfig): The runtime configuration for the agent.

    Returns:
        State: The updated state with loaded memories.
    """

    print('---------------> loading memories')

    convo_str = get_buffer_string(state["messages"])
    convo_str = tokenizer.decode(tokenizer.encode(convo_str)[:2048])
    recall_memories = search_recall_memories.invoke(convo_str, config)
    return {
        "recall_memories": recall_memories,
        "messages": state["messages"],
    }

def route_tools(state: State):
    """Determine whether to use tools or end the conversation based on the last message.

    Args:
        state (schemas.State): The current state of the conversation.

    Returns:
        Literal["tools", "__end__"]: The next step in the graph.
    """
    msg = state["messages"][-1]
    if isinstance(msg, AIMessage) and msg.tool_calls:
        return "tools"

    return END

def get_agent():
    tools = [save_recall_memory, search_recall_memories]

    model = ChatOpenAI(model="gpt-4o")
    model_with_tools = model.bind_tools(tools)

    # Define a new graph

    # Define the function that calls the model
    def call_model(state: State):
        bound = prompt | model_with_tools
        recall_str = (
            "<recall_memory>\n" + "\n".join(state["recall_memories"]) + "\n</recall_memory>"
        )
        response = bound.invoke({"messages": state["messages"], "recall_memories": recall_str})
        return {"messages": response}


    workflow = StateGraph(state_schema=State)
    # Define the (single) node in the graph
    workflow.add_node(load_memories)
    workflow.add_node(call_model)
    workflow.add_node("tools", ToolNode(tools))


    # --------------------
    workflow.add_edge(START, "load_memories")
    workflow.add_edge("load_memories", "call_model")
    workflow.add_conditional_edges("call_model", route_tools, ["tools", END])
    workflow.add_edge("tools", "call_model")




    # Add memory
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    # print('---------------')
    # print(app.get_graph().draw_mermaid())
    # print('---------------')
    return app

from enum import StrEnum

class Agents(StrEnum):
    LUCY = "lucy"

class ToolNodes(StrEnum):
    LOAD_MEMORIES = "load_memories"
    REFLECT_ON_INTERACTION = "reflect_on_interaction"
    LUCY_TOOLS = "lucy_tools"
    SUZIE_TOOLS = "suzie_tools"


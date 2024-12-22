from agents.lucy.tools.emails import SendEmailTool
from .memory import SaveMemoryTool, RecallMemoriesTool
from .todoist import ListTasksTool, CreateTaskTool, CompleteTaskTool
from .trello import GetBoardTool, CreateCardTool, ListProjectsTool, UpdateCardTool

TOOLS = [
    SaveMemoryTool(),
    RecallMemoriesTool(),
    ListTasksTool(),
    CreateTaskTool(),
    CompleteTaskTool(),
    ListProjectsTool(),
    GetBoardTool(),
    CreateCardTool(),
    UpdateCardTool(),
    SendEmailTool(),
]

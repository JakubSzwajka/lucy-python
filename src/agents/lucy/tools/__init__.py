from .web_search import WebSearchTool
from .calendar import CalendarCreateEventTool, CalendarGetUpcomingEventsTool
from .emails import SendEmailTool
from .drive import GetFilesTool, ListFilesTool
from .memory import SaveMemoryTool, RecallMemoriesTool
from .todoist import ListTasksTool, CreateTaskTool, CompleteTaskTool
from .trello import GetBoardTool, CreateCardTool, ListProjectsTool, UpdateCardTool

LUCY_TOOLS = [
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
    ListFilesTool(),
    GetFilesTool(),
    CalendarGetUpcomingEventsTool(),
    CalendarCreateEventTool(),
    WebSearchTool(),
]

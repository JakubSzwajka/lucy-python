from .calendar import CalendarGetUpcomingEventsTool
from .emails import SendEmailTool
from .drive import GetFilesTool, ListFilesTool
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
    ListFilesTool(),
    GetFilesTool(),
    CalendarGetUpcomingEventsTool(),
]

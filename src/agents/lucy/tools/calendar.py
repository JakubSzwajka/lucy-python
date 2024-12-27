from typing import Optional, Type
from langchain_core.runnables.config import RunnableConfig
from langchain.tools import BaseTool
from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from pydantic import BaseModel, Field

from agents.services.google_calendar_manager import GoogleCalendarManager


CALENDAR_DESCRIPTION = """
Calendar is used to get the events from the user's calendar.
Events might be part of multiple calendars.
- kuba.szwajka@sofomo.com is work calendar.
- szwajkajakub@gmail.com is personal calendar.
- dominika.rogoz@aion.eu is Dominika's work calendar to know when she is available.
- Domi calendar is my calendar to mark when Dominika has some private time blocked.

"""


class CalendarGetUpcomingEventsToolPayload(BaseModel):
    days: int = Field(description="The number of days to get the events for.")


class CalendarGetUpcomingEventsTool(BaseTool):
    name: str = "calendar_get_upcoming_events"
    description: str = CALENDAR_DESCRIPTION
    args_schema: Type[BaseModel] = CalendarGetUpcomingEventsToolPayload

    def _run(
        self,
        days: int,
        config: RunnableConfig,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ):
        gd = GoogleCalendarManager()
        return gd.get_upcoming_events(days=days)

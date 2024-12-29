from datetime import datetime
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

Calendar is also used to create events in the user's calendar. By default put all events in the personal szwajkajakub@gmail.com calendar.
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


class TimeObject(BaseModel):
    date_time: datetime = Field(
        description="The date time of the event. Time zone aware! Use ISO format."
    )
    timezone: str = Field(
        description="The timezone of the event. By default use Europe/Warsaw."
    )


class CalendarCreateEventPayload(BaseModel):
    summary: str = Field(
        description="The title of the event. Short meaningfull but with emoji at the very beginning."
    )
    start: TimeObject = Field(description="The start time of the event.")
    end: TimeObject = Field(
        description="The end time of the event. Put all events by default for 1h after start time."
    )
    description: str = Field(description="The description of the event.")
    location: Optional[str] = Field(
        description="The location of the event. Only if you know it. Otherwise leave empty.",
        default=None,
    )
    attendees: Optional[list[str]] = Field(
        description="The list of attendees. Only if you know it. Use only email addresses. Otherwise leave empty.",
        default=None,
    )


class CalendarCreateEventTool(BaseTool):
    name: str = "calendar_create_event"
    description: str = CALENDAR_DESCRIPTION
    args_schema: Type[BaseModel] = CalendarCreateEventPayload

    def _run(
        self,
        summary: str,
        start: TimeObject,
        end: TimeObject,
        description: str,
        location: Optional[str],
        attendees: Optional[list[str]],
        config: RunnableConfig,
    ):
        gd = GoogleCalendarManager()
        return gd.create_event(
            summary=summary,
            start_date_time=start.date_time,
            start_time_zone=start.timezone,
            end_date_time=end.date_time,
            end_time_zone=end.timezone,
            description=description,
            location=location,
            attendees=attendees,
        )

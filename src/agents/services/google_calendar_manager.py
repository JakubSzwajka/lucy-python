from datetime import datetime, timedelta
from typing import Optional, TypedDict
from googleapiclient.discovery import build
from agents.logger import get_logger

from agents.services.google_scopes import GoogleManagerBase

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]


class Event(TypedDict):
    id: str
    summary: str
    start: str
    end: str
    calendar_id: str
    calendar_name: str


class GoogleCalendarManager(GoogleManagerBase):
    def __init__(self):
        super().__init__("calendar", SCOPES)
        self.service = build("calendar", "v3", credentials=self.creds)
        self.logger = get_logger(self.__class__.__name__)

    def get_upcoming_events(self, days: int):
        self.logger.info("Getting upcoming events for %d days", days)
        time_min = datetime.now().isoformat() + "Z"
        time_max = (datetime.now() + timedelta(days=days)).isoformat() + "Z"

        calendars = self.service.calendarList().list().execute()
        final_events = []

        for cal in calendars["items"]:
            if cal["summary"] in ["Todoist"]:
                continue
            events_result = (
                self.service.events()
                .list(
                    calendarId=cal["id"],
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=10,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])
            for event in events:
                if type(event["start"]) == dict:
                    start = event["start"].get("dateTime", event["start"].get("date"))
                else:
                    start = event["start"]

                if type(event["end"]) == dict:
                    end = event["end"].get("dateTime", event["end"].get("date"))
                else:
                    end = event["end"]

                final_events.append(
                    Event(
                        id=event.get("id", ""),
                        summary=event.get("summary", ""),
                        start=start,
                        end=end,
                        calendar_id=cal["id"],
                        calendar_name=cal["summary"],
                    )
                )
        return final_events

    def create_event(
        self,
        summary: str,
        start_date_time: datetime,
        start_time_zone: str,
        end_date_time: datetime,
        end_time_zone: str,
        description: str,
        location: Optional[str],
        attendees: Optional[list[str]],
    ):
        event = {
            "summary": summary,
            "location": location,
            "attendees": [{"email": attendee} for attendee in attendees]
            if attendees
            else None,
            "start": {
                "dateTime": start_date_time.isoformat(),
                "timeZone": start_time_zone,
            },
            "end": {"dateTime": end_date_time.isoformat(), "timeZone": end_time_zone},
            "description": description,
        }
        self.logger.info("Creating event: %s", event)
        return (
            self.service.events()
            .insert(calendarId="szwajkajakub@gmail.com", body=event)
            .execute()
        )

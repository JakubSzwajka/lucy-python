from typing import TypedDict

from googleapiclient.discovery import build
from agents.services.google_scopes import GoogleManagerBase


class Document(TypedDict):
    id: str
    name: str
    url: str
    mime_type: str
    metadata: dict

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/drive",
]


class GoogleDriveManager(GoogleManagerBase):
    def __init__(self):
        super().__init__("drive", SCOPES)
        self.service = build("drive", "v3", credentials=self.creds)

    def list_files(self):
        # Call the Drive v3 API
        results = (
            self.service.files()
            .list(pageSize=100, fields="nextPageToken, files(id, name, mimeType, webViewLink)")
            .execute()
        )
        items = results.get("files", [])
        return [Document(
            id=item["id"],
            name=item["name"],
            url=item["webViewLink"],
            mime_type=item["mimeType"],
            metadata={}
        ) for item in items]


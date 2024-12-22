import os.path
from typing import TypedDict

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    # "https://www.googleapis.com/auth/drive.metadata",
    # "https://www.googleapis.com/auth/drive.file",
]


class Document(TypedDict):
    id: str
    name: str
    url: str
    mime_type: str
    metadata: dict



class GoogleDriveManager:
    def __init__(self):
        self.creds = self._configure_credentials()
        self.service = build("drive", "v3", credentials=self.creds)

    def _configure_credentials(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("creds/token.json"):
            creds = Credentials.from_authorized_user_file("creds/token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "creds/credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
            with open("creds/token.json", "w") as token:
                token.write(creds.to_json())

        return creds


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


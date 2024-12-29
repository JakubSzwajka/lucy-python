import io
from typing import TypedDict

from googleapiclient.discovery import build
from agents.services.google_scopes import GoogleManagerBase
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload
from agents.logger import get_logger



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
        self.logger = get_logger(self.__class__.__name__)

    def list_files(self):
        # Call the Drive v3 API
        results = (
            self.service.files()
            .list(
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, webViewLink)",
            )
            .execute()
        )
        items = results.get("files", [])
        return [
            Document(
                id=item["id"],
                name=item["name"],
                url=item["webViewLink"],
                mime_type=item["mimeType"],
                metadata={},
            )
            for item in items
        ]

    def update_file(self, file_id: str, name: str, mime_type: str, content: str):
        file_metadata = {
            "name": name,
            "mimeType": mime_type,
        }
        body = MediaFileUpload(
            filename=name,
            mimetype=mime_type,
        )

        file = (
            self.service.files()
            .update(
                fileId=file_id,
                body=file_metadata,
                media_body=body,
            )
            .execute()
        )
        return file

    def get_file_content(self, file_id: str):
        request = self.service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk()
            # print(f"Download {int(status.progress() * 100)}.")

        return file.getvalue().decode("utf-8")

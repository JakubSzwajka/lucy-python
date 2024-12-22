from typing import List, Optional, Type
from langchain_core.runnables.config import RunnableConfig
from langchain.tools import BaseTool
from pathlib import Path

from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from pydantic import BaseModel, Field

from agents.services.google_drive_manager import GoogleDriveManager
from langchain_community.document_loaders import UnstructuredFileIOLoader
from langchain_google_community import GoogleDriveLoader


GOOGLE_DRIVE_DESCRIPTION = """
Google Drive is used for personal documents and files management.
It stores all the files that agent has access to.
To understand the file context follow directory structure and its names.
"""


class ListFilesTool(BaseTool):
    name: str = "list_files"
    description: str = f"List all files from google drive. {GOOGLE_DRIVE_DESCRIPTION}"

    def _run(self, config: RunnableConfig, run_manager: Optional[CallbackManagerForToolRun] = None):
        return GoogleDriveManager().list_files()


class FileToLoad(BaseModel):
    id: str = Field(description="The id of the file to load. If unknown, use list_files tool to get the list of files.")
    mime_type: str = Field(description="The mime type of the file to load. If unknown, use list_files tool to get the list of files.")

class GetFileToolPayload(BaseModel):
    files: List[FileToLoad] = Field(description="List of files to load with their ids and mime types.")

class GetFilesTool(BaseTool):
    name: str = "get_files"
    description: str = f"Get files from google drive. {GOOGLE_DRIVE_DESCRIPTION}"
    args_schema: Type[BaseModel] = GetFileToolPayload

    def _run(
        self,
        files: List[FileToLoad],
        config: RunnableConfig,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ):
        others = []
        sheets = []
        final_docs = []
        for file in files:
            if file.mime_type == "application/vnd.google-apps.spreadsheet":
                sheets.append(file)
            else:
                others.append(file)

        if others:
            loader = GoogleDriveLoader(
                token_path=Path("creds/token.json"),
                file_ids=[file.id for file in others],
            )
            docs = loader.load()
            final_docs.extend(docs)
        if sheets:
            loader = GoogleDriveLoader(
                token_path=Path("creds/token.json"),
                file_ids=[file.id for file in sheets],
            )
            sheets_docs = []
            for sheet in sheets:
                sheets_docs.extend(loader._load_sheet_from_id(sheet.id))
            final_docs.extend(sheets_docs)
        return final_docs

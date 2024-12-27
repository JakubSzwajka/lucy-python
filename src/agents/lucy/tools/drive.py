from typing import Iterator, List, Optional, Type
from langchain_core.runnables.config import RunnableConfig
from langchain.tools import BaseTool
from pathlib import Path

from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from pydantic import BaseModel, Field
import yaml

from agents.services.google_drive_manager import GoogleDriveManager
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders.base import BaseLoader
from langchain_core.documents import Document as LangchainDocument

from langchain_google_community import GoogleDriveLoader

from agents.lucy.document import Document


class MarkdownLoaderFromString(BaseLoader):
    def __init__(self, content: str, metadata: dict):
        self.content = content
        self.metadata = metadata

    def lazy_load(self) -> Iterator[LangchainDocument]:
        yield LangchainDocument(page_content=self.content, metadata=self.metadata)


GOOGLE_DRIVE_DESCRIPTION = """
Google Drive is used for personal documents and files management.
It stores all the files that agent has access to.
To understand the file context follow directory structure and its names.
"""


class ListFilesTool(BaseTool):
    name: str = "list_files"
    description: str = f"List all files from google drive. {GOOGLE_DRIVE_DESCRIPTION}"

    def _run(
        self,
        config: RunnableConfig,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ):
        return GoogleDriveManager().list_files()


class FileToLoad(BaseModel):
    id: str = Field(
        description="The id of the file to load. If unknown, use list_files tool to get the list of files."
    )
    name: str = Field(
        description="The name of the file to load. If unknown, use list_files tool to get the list of files."
    )
    mime_type: str = Field(
        description="The mime type of the file to load. If unknown, use list_files tool to get the list of files."
    )
    url: str = Field(
        description="The url of the file to load. If unknown, use list_files tool to get the list of files."
    )


class GetFileToolPayload(BaseModel):
    files: List[FileToLoad] = Field(
        description="List of files to load with their ids and mime types."
    )


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
        markdown_files = []
        final_docs = []
        for file in files:
            if file.mime_type == "application/vnd.google-apps.spreadsheet":
                sheets.append(file)
            if file.mime_type == "text/x-markdown":
                markdown_files.append(file)
            else:
                others.append(file)

        if others:
            loader = GoogleDriveLoader(
                token_path=Path("creds/drive_token.json"),
                file_ids=[file.id for file in others],
            )
            docs = loader.load()
            final_docs.extend(docs)

        if sheets:
            loader = GoogleDriveLoader(
                token_path=Path("creds/drive_token.json"),
                file_ids=[file.id for file in sheets],
            )
            sheets_docs = []
            for sheet in sheets:
                sheets_docs.extend(loader._load_sheet_from_id(sheet.id))
            final_docs.extend(sheets_docs)

        if markdown_files:
            for f in markdown_files:
                content = GoogleDriveManager().get_file_content(f.id)
                loader = MarkdownLoaderFromString(
                    content,
                    metadata={
                        "google_drive_id": f.id,
                        "mime_type": f.mime_type,
                        "url": f.url,
                        "name": f.name,
                    },
                )
                docs = loader.load()
                final_docs.extend(docs)
        print(final_docs)
        return [
            Document(
                id=doc.metadata.get("google_drive_id", "unknown"),
                name=doc.metadata.get("name", "unknown"),
                content=doc.page_content,
                url=doc.metadata.get("url", "unknown"),
                mime_type=doc.metadata.get("mime_type", "unknown"),
                # metadata=doc.metadata,
            )
            for doc in final_docs
        ]


# class UpdateFileToolPayload(BaseModel):
#     file_id: str = Field(description="The id of the file to update. If unknown, use list_files tool to get the list of files.")
#     name: str = Field(description="The name of the file to update.")
#     mime_type: str = Field(description="The mime type of the file to update.")
#     content: str = Field(description="The content of the file to update.")

# class UpdateFileTool(BaseTool):
#     name: str = "update_file"
#     description: str = f"Update file in google drive. {GOOGLE_DRIVE_DESCRIPTION}"
#     args_schema: Type[BaseModel] = UpdateFileToolPayload

#     def _run(
#         self,
#         file_id: str,
#         name: str,
#         mime_type: str,
#         content: str,
#         config: RunnableConfig,
#         run_manager: Optional[CallbackManagerForToolRun] = None,
#     ):
#         return GoogleDriveManager().update_file(
#             file_id=file_id,
#             name=name,
#             mime_type=mime_type,
#             content=content
#         )

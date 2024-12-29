from pydantic import BaseModel, Field
from typing import  Optional, Type
from langchain_core.runnables.config import RunnableConfig
from langchain.tools import BaseTool

from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)

from agents.services.firecrawl_manager import FireCrawlManager


WEB_SEARCH_DESCRIPTION = """
Web search is used to search the web for information. Always include the link to the page where the information is from.
"""


class WebSearchToolPayload(BaseModel):
    query: str = Field(
        description="The query to search the web for. Based on the user's message, things you might want to put in search engine query."
    )


class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = f"Web search. {WEB_SEARCH_DESCRIPTION}"
    args_schema: Type[BaseModel] = WebSearchToolPayload

    def _run(
        self,
        query: str,
        config: RunnableConfig,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ):
        return FireCrawlManager().search_web(query)


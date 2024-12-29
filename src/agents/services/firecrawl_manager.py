from firecrawl import FirecrawlApp
from typing import List
from langchain_community.document_loaders.firecrawl import FireCrawlLoader
import requests

from config import GlobalConfig
from langchain_core.documents import Document
from agents.logger import get_logger


class FireCrawlManager:
    def __init__(self):
        self.client = FirecrawlApp(api_key=GlobalConfig.get_firecrawl_api_key())
        self.logger = get_logger(self.__class__.__name__)

    def load_page(self, url: str) -> List[Document]:
        loader = FireCrawlLoader(
            api_key=GlobalConfig.get_firecrawl_api_key(), url=url, mode="scrape"
        )
        docs = loader.load()
        return docs

    def search_web(self, query: str) -> List[Document]:
        self.logger.info("Searching the web for: %s", query)
        url = "https://api.firecrawl.dev/v0/search"
        search_results = []
        response = requests.post(
            url,
            json={
                "query": query,
                "searchOptions": {"limit": 3, 'format': 'markdown'},
                "pageOptions": {"fetchPageContent": False},
            },
            headers={"Authorization": f"Bearer {GlobalConfig.get_firecrawl_api_key()}"},
        )
        response_json = response.json()
        pages = response_json['data']
        for page in pages:
            self.logger.info("Loading page: %s", page['url'])
            docs = self.load_page(page['url'])
            search_results.extend(docs)

        return search_results
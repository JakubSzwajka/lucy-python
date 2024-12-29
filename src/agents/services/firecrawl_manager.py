import uuid
from firecrawl import FirecrawlApp
from typing import List
from langchain_community.document_loaders.firecrawl import FireCrawlLoader
import requests

from config import GlobalConfig
# from agents.document import Document
from langchain_core.documents import Document


class FireCrawlManager:
    def __init__(self):
        self.client = FirecrawlApp(api_key=GlobalConfig.get_firecrawl_api_key())

    def load_page(self, url: str) -> List[Document]:
        loader = FireCrawlLoader(
            api_key=GlobalConfig.get_firecrawl_api_key(), url=url, mode="scrape"
        )
        docs = loader.load()
        return docs

    def search_web(self, query: str) -> List[Document]:
        print('[TOOL:WEB_SEARCH] Searching the web for:', query)
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
            print('[TOOL:WEB_SEARCH] Loading page:', page['url'])
            docs = self.load_page(page['url'])
            search_results.extend(docs)

        return search_results
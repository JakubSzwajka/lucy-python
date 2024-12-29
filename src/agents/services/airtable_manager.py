from typing import List
from pyairtable import Api
from agents.services.qdrant_manager import KnowledgeTriple
from config import GlobalConfig


class AirtableManager:
    def __init__(self):
        self.client = Api(GlobalConfig.get_airtable_api_key())
        self.base_id = "apptRld5563ZpjbTr"
        self.memories_table_id = "tblyvASa0o2xDnWSQ"

    def add_to_memories(self, memories: List[KnowledgeTriple], context: str):
        table = self.client.table(self.base_id, self.memories_table_id)
        for memory in memories:
            payload = memory.model_dump(mode="json")
            payload["context"] = context
            table.create(payload)

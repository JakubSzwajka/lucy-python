from typing import List
from pyairtable import Api
from agents.services.qdrant_manager import KnowledgeTriple
from config import GlobalConfig
from agents.logger import get_logger

class AirtableManager:
    def __init__(self):
        self.client = Api(GlobalConfig.get_airtable_api_key())
        self.base_id = "apptRld5563ZpjbTr"
        self.memories_table_id = "tblyvASa0o2xDnWSQ"
        self.logger = get_logger(self.__class__.__name__)

    def add_to_memories(self, memories: List[KnowledgeTriple], context: str):
        table = self.client.table(self.base_id, self.memories_table_id)
        for memory in memories:
            payload = memory.model_dump(mode="json")
            payload["context"] = context
            self.logger.info("Adding memory to Airtable: %s", payload)
            table.create(payload)

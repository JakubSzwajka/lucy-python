from datetime import datetime
from pydantic import BaseModel, Field
from typing import List
import uuid
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from qdrant_client import QdrantClient
import matplotlib.pyplot as plt
import networkx as nx
from qdrant_client.http.models import VectorParams
from qdrant_client.http.models import Distance

from config import GlobalConfig


class _RecallVectorStoreSingleton:
    _instance = None
    _client = None

    @staticmethod
    def get_instance():
        collection_name = "lucy"

        if _RecallVectorStoreSingleton._instance is None:
            _RecallVectorStoreSingleton._ensure_collection()

            _RecallVectorStoreSingleton._instance = (
                QdrantVectorStore.from_existing_collection(
                    url=GlobalConfig.get_qdrant_url(),
                    collection_name=collection_name,
                    embedding=OpenAIEmbeddings(model="text-embedding-3-large"),
                )
            )
        return _RecallVectorStoreSingleton._instance

    @staticmethod
    def _ensure_collection():
        client = QdrantClient(url=GlobalConfig.get_qdrant_url())
        collection_name = "lucy"
        collection_list = client.get_collections()
        if not any(
            collection.name == collection_name
            for collection in collection_list.collections
        ):
            print("Creating collection", collection_name)
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
            )


class KnowledgeTriple(BaseModel):
    subject: str = Field(
        description="""
The subject of the memory. Single word, person, place, thing or concept.
Example: "Kuba", "Dominika", "Wrocław", "Programowanie", "Python", "AI"
IMPORTANT: if memory is about more then one person, place, thing or concept, split it into multiple memories about each and connect them with predicate accordingly.
Example: "Kuba" and "Dominika" are two different subjects.
"""
    )
    predicate: str = Field(description="The predicate of the memory")
    object_: str = Field(
        description="The object of the memory. Single word, person, place, thing or concept."
    )


class MemoryManager:
    def __init__(self):
        self.vectorstore = _RecallVectorStoreSingleton.get_instance()

    def save_memories(
        self, memories: List[KnowledgeTriple], context: str, user_id: str
    ):
        documents = []
        for memory in memories:
            dump = memory.model_dump(mode="json")
            dump["context"] = context
            serialized = " ".join(dump.values())  # type: ignore
            dump["created_at"] = datetime.now().isoformat()
            dump["updated_at"] = datetime.now().isoformat()
            document = Document(
                serialized,
                id=str(uuid.uuid4()),
                metadata={
                    "user_id": user_id,
                    **dump,
                },
            )
            documents.append(document)
        self.vectorstore.add_documents(documents)

    def recall_memories(self, query: str, user_id: str):
        documents = self.vectorstore.similarity_search(query, k=10)
        return [document.metadata for document in documents]

    def plot_memories(self):
        records = self.vectorstore.similarity_search("", k=100)

        # Plot graph
        plt.figure(figsize=(6, 4), dpi=80)
        G = nx.DiGraph()

        for record in records:
            G.add_edge(
                record.metadata["subject"],
                record.metadata["object_"],
                label=record.metadata["predicate"],
            )

        pos = nx.spring_layout(G)
        nx.draw(
            G,
            pos,
            with_labels=True,
            node_size=3000,
            node_color="lightblue",
            font_size=10,
            font_weight="bold",
            arrows=True,
        )
        edge_labels = nx.get_edge_attributes(G, "label")
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red")
        plt.show()
        return "Memory graph plotted"

    def dump_memories(self):
        points = self.vectorstore.client.scroll(
            collection_name="lucy",
            limit=1000,
            with_payload=True,
            with_vectors=False,
        )
        return points[0]

from enum import StrEnum
import os
from typing_extensions import TypedDict


class User(TypedDict):
    id: str
    name: str


class GlobalConfig:
    ASSISTANT_NAME = "Lucy"
    USER_NAME = "Kuba"

    # APP_URL = "http://localhost:8000"

    USERS = [
        User(id="recB4CxsAvykFwcAs", name="Kuba"),
        User(id="recc8JOHDhduumYWz", name="Lucy"),
    ]

    @staticmethod
    def get_db_url() -> str:
        url = os.getenv("DB_URL")
        if not url:
            raise ValueError("DB_URL is not set")
        return url

    @staticmethod
    def get_qdrant_url() -> str:
        url = os.getenv("QDRANT_URL")
        if not url:
            raise ValueError("QDRANT_URL is not set")
        return url

    @staticmethod
    def get_qdrant_api_key() -> str:
        api_key = os.getenv("QDRANT_API_KEY")
        if not api_key:
            raise ValueError("QDRANT_API_KEY is not set")
        return api_key

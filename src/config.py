from enum import StrEnum
import os
from typing_extensions import TypedDict

class User(TypedDict):
    id: str
    name: str


class GlobalConfig:
    ASSISTANT_NAME = "Lucy"
    USER_NAME = "Kuba"

    APP_URL = "http://localhost:8000"

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

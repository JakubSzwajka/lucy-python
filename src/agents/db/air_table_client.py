import os
from pyairtable import Api

class DbClient:
    def __init__(self):
        token = os.getenv("AIRTABLE_API_KEY")
        if token is None:
            raise ValueError("AIRTABLE_API_KEY is not set")
        self.client = Api(api_key=token)


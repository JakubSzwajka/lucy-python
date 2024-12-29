import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from agents.logger import get_logger


class GoogleManagerBase:
    def __init__(self, token_name: str, scopes: list[str]):
        self.token_name = token_name
        self.scopes = scopes
        self.creds = self._configure_credentials()
        self.logger = get_logger(self.__class__.__name__)

    def _configure_credentials(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        self.logger.info("Configuring credentials for %s", self.token_name)

        if os.path.exists(f"creds/{self.token_name}_token.json"):
            self.logger.info("Loading credentials from file")
            creds = Credentials.from_authorized_user_file(
                f"creds/{self.token_name}_token.json", self.scopes
            )
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            self.logger.info("No valid credentials available, logging in")
            if creds and creds.expired and creds.refresh_token:
                self.logger.info("Refreshing credentials")
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "creds/credentials.json", self.scopes
                )
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                self.logger.info("Saving credentials to file")
            with open(f"creds/{self.token_name}_token.json", "w") as token:
                token.write(creds.to_json())

        return creds

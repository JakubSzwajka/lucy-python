import os
from typing import List
import resend
from agents.logger import get_logger


class ResendEmailService:
    def __init__(self):
        self.api_key = os.getenv("RESEND_TOKEN")
        resend.api_key = self.api_key
        self.logger = get_logger(self.__class__.__name__)

    def send_email(
        self, from_email: str, to_emails: List[str], subject: str, html: str, text: str
    ):
        self.logger.info("Sending email from %s to %s", from_email, to_emails)
        return resend.Emails.send(
            {
                "from": from_email,
                "to": to_emails,
                "subject": subject,
                "html": html,
                "text": text,
            }
        )

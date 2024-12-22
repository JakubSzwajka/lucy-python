import os
from typing import List
import resend


class ResendEmailService:
    def __init__(self):
        self.api_key = os.getenv("RESEND_TOKEN")
        resend.api_key = self.api_key

    def send_email(
        self, from_email: str, to_emails: List[str], subject: str, html: str, text: str
    ):
        return resend.Emails.send(
            {
                "from": from_email,
                "to": to_emails,
                "subject": subject,
                "html": html,
                "text": text,
            }
        )

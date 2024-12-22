from pydantic import BaseModel, Field
from typing import List, Optional, Type, TypedDict
from langchain_core.runnables.config import RunnableConfig
from agents.services.resend_email import ResendEmailService
from langchain.tools import BaseTool
from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)


EMAIL_DESCRIPTION = """
Emails are used to send messages to the user. Right now the only supported email is szwajkajakub@gmail.com.
"""


class SendEmailToolPayload(BaseModel):
    to_emails: List[str] = Field(
        description="The emails to send the message to. Must be a list of valid email addresses."
    )
    subject: str = Field(description="The subject of the email.")
    html: str = Field(description="The HTML content of the email.")
    text: str = Field(description="The text content of the email.")


class SendEmailTool(BaseTool):
    name: str = "send_email"
    description: str = EMAIL_DESCRIPTION
    args_schema: Type[BaseModel] = SendEmailToolPayload

    def _run(
        self,
        to_emails: List[str],
        subject: str,
        html: str,
        text: str,
        config: RunnableConfig,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ):
        from_email = "lucy@kubaszwajka.com"
        to_emails = ['szwajkajakub@gmail.com'] # force to send only to me
        return ResendEmailService().send_email(
            from_email, to_emails, subject, html, text
        )

"""Sends SMS and email notifications via Twilio and SendGrid."""

import asyncio

import anthropic
import structlog
from pydantic import BaseModel
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from app.config import settings
from app.detector import EventDetectionResult

logger = structlog.get_logger()


class NotificationContent(BaseModel):
    sms: str           # max 160 chars, plain text
    email_subject: str
    email_body: str    # HTML


class Notifier:
    def __init__(self):
        self._twilio = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        self._sendgrid = SendGridAPIClient(settings.sendgrid_api_key)
        self._anthropic = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def compose_notification(self, result: EventDetectionResult) -> NotificationContent:
        event_details = "\n".join(
            f"- {e.day} at {e.location} (organizer: {e.organizer}, "
            f"open: {e.is_open}, details: {e.details})"
            for e in result.events
        )

        response = await self._anthropic.messages.parse(
            model="claude-opus-4-7",
            max_tokens=1024,
            system=(
                "You write short, friendly sports notification messages. "
                "Respond only with the requested JSON structure."
            ),
            messages=[{
                "role": "user",
                "content": (
                    "Write a notification for these badminton events that are now open "
                    "for registration:\n\n"
                    f"{event_details}\n\n"
                    "Rules:\n"
                    "- sms: plain text, max 160 chars, include 🏸 emoji, friendly and urgent\n"
                    "- email_subject: short and clear, mention NWBA and that spots are open\n"
                    "- email_body: HTML, include all event details (day, location, open status), "
                    "end with a strong reminder to register immediately"
                ),
            }],
            output_format=NotificationContent,
        )

        if response.parsed_output is None:
            raise RuntimeError("Claude returned no structured output for notification")

        content = response.parsed_output
        logger.info(
            "notification composed",
            sms_chars=len(content.sms),
            subject=content.email_subject,
        )
        return content

    async def send_sms(self, message: str) -> None:
        try:
            msg = await asyncio.to_thread(
                self._twilio.messages.create,
                body=message,
                from_=f"whatsapp:{settings.twilio_from_number}",
                to=f"whatsapp:{settings.twilio_to_number}",
            )
            logger.info("whatsapp sent", sid=msg.sid, to=settings.twilio_to_number)
        except TwilioRestException as e:
            logger.error("sms failed", code=e.code, error=str(e))
            raise

    async def send_email(self, subject: str, body: str) -> None:
        mail = Mail(
            from_email=settings.sendgrid_from_email,
            to_emails=settings.sendgrid_to_email,
            subject=subject,
            html_content=body,
        )
        try:
            response = await asyncio.to_thread(self._sendgrid.send, mail)
            logger.info(
                "email sent",
                status_code=response.status_code,
                to=settings.sendgrid_to_email,
            )
        except Exception as e:
            logger.error("email failed", error=str(e))
            raise

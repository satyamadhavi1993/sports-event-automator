"""Sends SMS and email notifications via Twilio and SendGrid."""

import asyncio

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
    sms: str
    email_subject: str
    email_body: str


class Notifier:
    def __init__(self):
        self._twilio = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        self._sendgrid = SendGridAPIClient(settings.sendgrid_api_key)

    def compose_notification(self, result: EventDetectionResult) -> NotificationContent:
        open_events = [e for e in result.events if e.is_open]

        parts = [
            f"{e.day[:3]} @ {e.location}"
            for e in open_events
        ]
        sms = f"🏸 {settings.event_organiser_name} events open! {', '.join(parts)}. Register now: {settings.platform_events_url}"

        rows = "".join(
            f"<tr><td><b>{e.day}</b></td><td>{e.location}</td>"
            f"<td>{'✅ Open' if e.is_open else '❌ Closed'}</td>"
            f"<td>{e.details}</td></tr>"
            for e in result.events
        )
        email_body = (
            f"<h2>🏸 {settings.event_organiser_name} Events Open for Registration</h2>"
            "<table border='1' cellpadding='8' cellspacing='0'>"
            "<tr><th>Day</th><th>Location</th><th>Status</th><th>Details</th></tr>"
            f"{rows}"
            "</table>"
            "<br><p><strong>Register immediately before spots fill up!</strong></p>"
        )

        content = NotificationContent(
            sms=sms,
            email_subject=f"{settings.event_organiser_name} Events Open for Registration",
            email_body=email_body,
        )
        logger.info("notification composed", sms_chars=len(content.sms), subject=content.email_subject)
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

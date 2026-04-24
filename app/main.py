"""Entry point for the Badminton Tournament Monitor."""

import asyncio
import structlog
from app.config import configure_logging, settings  # noqa: F401 — settings import validates env vars on startup
from app.monitor import UBRClient
from app.detector import EventDetector
from app.notifier import Notifier

configure_logging()
logger = structlog.get_logger()


async def run():
    client = UBRClient()
    detector = EventDetector()
    notifier = Notifier()
    try:
        await client.login()
        text = await client.fetch_events()
        result = detector.detect_events(text)
        open_events = [e for e in result.events if e.is_open]

        if open_events:
            content = notifier.compose_notification(result)
            await asyncio.gather(
                notifier.send_sms(content.sms),
                notifier.send_email(content.email_subject, content.email_body),
            )
            logger.info("notifications sent", sms=content.sms, subject=content.email_subject)

            # Phase 5 - Auto registration
            # TODO: Call registrar.register_for_events() here
            # TODO: Call registrar.verify_registration() here
            # TODO: Send success/failure notification
            # Will be implemented and tested next Sunday
        else:
            logger.info("no open events found — no notifications sent", summary=result.summary)
    finally:
        await client.close()


def main():
    logger.info("Badminton monitor starting...")
    asyncio.run(run())


if __name__ == "__main__":
    main()

"""Entry point for the Badminton Tournament Monitor."""

import asyncio
import structlog
from app.config import settings  # noqa: F401 — validates env vars on startup
from app.monitor import UBRClient
from app.detector import EventDetector
from app.notifier import Notifier

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),
)

logger = structlog.get_logger()


async def run():
    client = UBRClient()
    detector = EventDetector()
    notifier = Notifier()
    try:
        await client.login()
        html = await client.fetch_events()
        result = await detector.detect_events(html)

        if result.events_found:
            content = await notifier.compose_notification(result)
            await asyncio.gather(
                notifier.send_sms(content.sms),
                notifier.send_email(content.email_subject, content.email_body),
            )
            logger.info("notifications sent", sms=content.sms, subject=content.email_subject)
        else:
            logger.info("no open events found — no notifications sent")
    finally:
        await client.close()


def main():
    logger.info("Badminton monitor starting...")
    asyncio.run(run())


if __name__ == "__main__":
    main()

"""Detects and performs event check-in on the UBR website."""

import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

import structlog

from app.config import configure_logging, settings
from app.events import DAY_TO_LOCATION, EVENTS_PARAMS, EVENTS_PATH, LOCATION_PREFIX
from app.monitor import UBRClient
from app.notifier import Notifier

configure_logging()
logger = structlog.get_logger()

PACIFIC = ZoneInfo("America/Los_Angeles")


class CheckInMonitor:
    def __init__(self, client: UBRClient):
        self._client = client
        self._notifier = Notifier()

    async def run(self) -> None:
        day_name = datetime.now(PACIFIC).strftime("%A")
        location = DAY_TO_LOCATION.get(day_name)

        if not location:
            logger.info("not a check-in day", day=day_name)
            return

        logger.info("check-in day detected", day=day_name, location=location)

        page = self._client.page
        url = settings.ubr_base_url + EVENTS_PATH + EVENTS_PARAMS
        await page.goto(url, wait_until="networkidle")

        # Find the event section containing our target location,
        # then look for a Check In link within it
        event_section = page.locator("tr, li, div").filter(has_text=location)
        checkin_button = event_section.get_by_text("Check In").first

        if not await checkin_button.is_enabled():
            logger.info("check-in not yet enabled — will retry", location=location)
            return

        logger.info("check-in button found — clicking", location=location)
        await checkin_button.click()

        # Handle confirmation popup if one appears
        try:
            confirm = page.get_by_role("button", name="Confirm")
            await confirm.wait_for(timeout=3000)
            await confirm.click()
            logger.info("confirmation popup handled")
        except Exception:
            pass  # no popup — that's fine

        await page.wait_for_load_state("networkidle")

        # Verify success — after check-in, "Withdraw" should appear on the page
        page_text = await page.inner_text("body")
        if "withdraw" not in page_text.lower():
            raise RuntimeError(
                f"Check-in clicked but success not confirmed for {location}. "
                f"Page snippet: {page_text[:300]}"
            )

        logger.info("check-in successful", location=location, day=day_name)

        sms = f"✅ Checked in for tonight's NWBA event at {location.replace(LOCATION_PREFIX, '')}!"
        email_body = (
            "<h2>✅ Check-in Confirmed</h2>"
            "<p>You are checked in for tonight's event:</p>"
            f"<ul><li><b>Day:</b> {day_name}</li>"
            f"<li><b>Location:</b> {location}</li></ul>"
            "<p>See you on the court! 🏸</p>"
        )
        await asyncio.gather(
            self._notifier.send_sms(sms),
            self._notifier.send_email(
                subject=f"Check-in Confirmed — {location}",
                body=email_body,
            ),
        )


async def _run():
    client = UBRClient()
    monitor = CheckInMonitor(client)
    try:
        await client.login()
        await monitor.run()
    finally:
        await client.close()


if __name__ == "__main__":
    logger.info("check-in monitor starting...")
    asyncio.run(_run())

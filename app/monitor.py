"""Fetches and tracks live tournament data."""

import structlog
from playwright.async_api import async_playwright

from app.config import settings
from app.events import EVENTS_PARAMS, EVENTS_PATH, LOGIN_PATH

logger = structlog.get_logger()


class UBRClient:
    def __init__(self):
        self._playwright = None
        self._browser = None
        self._page = None

    @property
    def page(self):
        return self._page

    async def login(self) -> None:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)
        self._page = await self._browser.new_page()

        await self._page.goto(settings.ubr_base_url + LOGIN_PATH)
        await self._page.fill('input[name="user[email]"]', settings.ubr_email)
        await self._page.fill('input[name="user[password]"]', settings.ubr_password)
        await self._page.click('input[type="submit"]')
        await self._page.wait_for_url("**/users/**")

        logger.info("login successful", url=self._page.url)

    async def fetch_events(self) -> str:
        url = settings.ubr_base_url + EVENTS_PATH + EVENTS_PARAMS
        await self._page.goto(url, wait_until="networkidle")

        text = await self._page.inner_text("body")
        logger.info("events page fetched", url=self._page.url, chars=len(text))
        return text

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

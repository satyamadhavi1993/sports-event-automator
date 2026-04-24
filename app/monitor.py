"""Fetches and tracks live tournament data."""

import structlog
from playwright.async_api import async_playwright

from app.config import settings

logger = structlog.get_logger()

class PlatformClient:
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

        await self._page.goto(settings.platform_login_url)
        await self._page.fill('input[name="user[email]"]', settings.platform_email)
        await self._page.fill('input[name="user[password]"]', settings.platform_password)
        async with self._page.expect_navigation(wait_until="networkidle"):
            await self._page.click('input[type="submit"]')

        if self._page.url == settings.platform_login_url:
            raise RuntimeError(
                f"Login failed — still on login page after submit. "
                f"Check credentials or form selectors. Current URL: {self._page.url}"
            )

        logger.info("login successful", url=self._page.url)

    async def fetch_events(self) -> str:
        await self._page.goto(settings.platform_events_url, wait_until="networkidle")

        text = await self._page.inner_text("body")
        logger.info("events page fetched", url=self._page.url, chars=len(text))
        return text

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

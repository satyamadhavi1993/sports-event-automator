"""Fetches and tracks live tournament data."""

import httpx
import structlog

from app.config import settings

logger = structlog.get_logger()

LOGIN_PATH = "/users/sign_in"
EVENTS_PATH = "/badminton_events"


class UBRClient:
    def __init__(self):
        self._client = httpx.AsyncClient(
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"},
        )

    async def login(self) -> None:
        login_url = settings.ubr_base_url + LOGIN_PATH

        # Fetch the login page first to get the CSRF token
        response = await self._client.get(login_url)
        response.raise_for_status()

        csrf_token = self._extract_csrf_token(response.text)
        if not csrf_token:
            raise RuntimeError("Could not find CSRF token on login page")

        payload = {
            "user[email]": settings.ubr_email,
            "user[password]": settings.ubr_password,
            "authenticity_token": csrf_token,
        }

        response = await self._client.post(login_url, data=payload)
        response.raise_for_status()

        if "sign_in" in str(response.url):
            raise RuntimeError("Login failed — still on sign-in page after POST")

        logger.info("login successful", url=str(response.url))

    def _extract_csrf_token(self, html: str) -> str | None:
        import re
        match = re.search(
            r'<meta[^>]+name="csrf-token"[^>]+content="([^"]+)"', html
        )
        return match.group(1) if match else None

    async def fetch_events(self) -> str:
        events_url = settings.ubr_base_url + EVENTS_PATH

        response = await self._client.get(
            events_url,
            params={"rp": "nextweek", "region": "seattle"},
        )
        response.raise_for_status()

        logger.info("events page fetched", url=str(response.url), bytes=len(response.content))
        return response.text

    async def close(self) -> None:
        await self._client.aclose()

"""Uses the Anthropic API to detect significant match events."""

import anthropic
import structlog
from anthropic import APIConnectionError, APIStatusError, RateLimitError
from pydantic import BaseModel, ValidationError

from app.config import settings

logger = structlog.get_logger()


class Event(BaseModel):
    day: str
    location: str
    organizer: str
    is_open: bool
    details: str


class EventDetectionResult(BaseModel):
    events_found: bool
    events: list[Event]
    summary: str


class EventDetector:
    def __init__(self):
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def detect_events(self, text: str) -> EventDetectionResult:
        if not text.strip():
            raise ValueError("Empty page content provided")

        # guard: if content is too short, the page is probably a login redirect
        if len(text) < 200:
            raise ValueError(
                f"Page content too short ({len(text)} chars) — "
                "session may have expired or page failed to load"
            )

        logger.info("detecting events", content_chars=len(text))

        user_message = (
            "Analyze this sports event page and find specific events "
            "from organizer 'Northwest Badminton Academy' in the Seattle region.\n\n"
            "I am looking for exactly these two events:\n"
            "1. Wednesday event at location 'NWBA - Kirkland'\n"
            "2. Thursday event at location 'NWBA - Bel-Red'\n\n"
            "For each event found, check if it is open for registration.\n\n"
            "Return ONLY a JSON response with this structure:\n"
            "{\n"
            "  'events_found': true/false,\n"
            "  'events': [\n"
            "    {\n"
            "      'day': 'Wednesday or Thursday',\n"
            "      'location': 'exact location from page',\n"
            "      'organizer': 'organizer name',\n"
            "      'is_open': true/false,\n"
            "      'details': 'any other relevant details'\n"
            "    }\n"
            "  ],\n"
            "  'summary': 'one line human readable summary'\n"
            "}\n\n"
            "If neither event is found return events_found as false "
            "and empty events list.\n\n"
            f"{text}"
        )

        try:
            response = await self._client.messages.parse(
                model="claude-opus-4-7",
                max_tokens=2048,
                system=(
                    "You analyze sports event pages. When asked about events, "
                    "respond only with the requested JSON structure."
                ),
                messages=[{"role": "user", "content": user_message}],
                output_format=EventDetectionResult,
            )
        except RateLimitError:
            logger.error("anthropic rate limit hit — too many requests")
            raise
        except APIConnectionError as e:
            logger.error("could not reach anthropic api", error=str(e))
            raise
        except APIStatusError as e:
            logger.error("anthropic api error", status_code=e.status_code, error=str(e))
            raise
        except ValidationError as e:
            logger.error("claude response did not match expected schema", error=str(e))
            raise

        if response.parsed_output is None:
            raise RuntimeError("Claude returned no structured output — possible refusal")

        result = response.parsed_output
        logger.info(
            "events detected",
            events_found=result.events_found,
            count=len(result.events),
            summary=result.summary,
        )
        return result

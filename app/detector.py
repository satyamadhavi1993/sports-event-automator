"""Parses event page text to find NWBA events."""

import structlog
from pydantic import BaseModel

from app.events import ORGANIZER, TARGETS

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
    def detect_events(self, text: str) -> EventDetectionResult:
        if not text.strip():
            raise ValueError("Empty page content provided")

        if len(text) < 200:
            raise ValueError(
                f"Page content too short ({len(text)} chars) — "
                "session may have expired or page failed to load"
            )

        logger.info("parsing events", content_chars=len(text))

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        events = []

        for target in TARGETS:
            location = target["location"]

            for i, line in enumerate(lines):
                if location not in line:
                    continue

                # Grab a window of lines around the location match for context
                window = lines[max(0, i - 5) : i + 10]
                window_text = "\n".join(window).lower()

                # Open = "register" link present; check-in alone means already registered
                is_open = "register" in window_text

                details = " | ".join(window[:8])

                events.append(Event(
                    day=target["day"],
                    location=location,
                    organizer=ORGANIZER,
                    is_open=is_open,
                    details=details,
                ))
                break  # stop after first match for this location

        events_found = len(events) > 0
        if events_found:
            summary = ", ".join(
                f"{e.day} at {e.location} ({'open' if e.is_open else 'closed'})"
                for e in events
            )
        else:
            summary = "No NWBA Kirkland or Bel-Red events found for next week"

        result = EventDetectionResult(
            events_found=events_found,
            events=events,
            summary=summary,
        )
        logger.info("events parsed", events_found=events_found, count=len(events), summary=summary)
        return result

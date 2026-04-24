"""Domain constants derived from configuration."""

from app.config import settings

ORGANIZER = settings.event_organiser_name

DAY_TO_LOCATION = {
    "Wednesday": settings.event_location_wed,
    "Thursday":  settings.event_location_thu,
}

TARGETS = [
    {"day": day, "location": location}
    for day, location in DAY_TO_LOCATION.items()
]

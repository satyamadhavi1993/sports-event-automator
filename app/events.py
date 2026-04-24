"""Domain constants — event locations, URL paths, and query params."""

ORGANIZER = "Northwest Badminton Academy"
LOCATION_PREFIX = "NWBA - "

DAY_TO_LOCATION = {
    "Wednesday": "NWBA - Kirkland",
    "Thursday":  "NWBA - Bel-Red",
}

TARGETS = [
    {"day": day, "location": location}
    for day, location in DAY_TO_LOCATION.items()
]

LOGIN_PATH    = "/users/sign_in"
EVENTS_PATH   = "/badminton_events"

EVENTS_PARAMS = "?rp=nextweek&region=seattle"

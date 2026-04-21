"""Entry point for the Badminton Tournament Monitor."""

import structlog
from app.config import settings

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO level
)

logger = structlog.get_logger()


def main():
    logger.info("Badminton monitor starting...")


if __name__ == "__main__":
    main()

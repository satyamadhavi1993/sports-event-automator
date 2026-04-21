# Badminton Tournament Monitor

Monitors live badminton tournament scores and sends SMS/email alerts for significant match events, powered by the Anthropic API.

## Tech Stack

- **Python 3.11+**
- **httpx** — HTTP requests to tournament data sources
- **Anthropic API** — AI-powered detection of significant match events
- **Twilio** — SMS notifications
- **SendGrid** — Email notifications
- **Redis** — State management to avoid duplicate alerts
- **structlog** — Structured logging
- **Sentry** — Error tracking
- **Pytest** — Testing
- **GitHub Actions** — Scheduled monitoring runs

## Setup

### 1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
.venv\Scripts\activate           # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your credentials:

| Variable | Description |
|---|---|
| `UBR_EMAIL` | Your UBR account email |
| `UBR_PASSWORD` | Your UBR account password |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `TWILIO_ACCOUNT_SID` | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | Twilio auth token |
| `TWILIO_FROM_NUMBER` | Twilio phone number to send from |
| `TWILIO_TO_NUMBER` | Phone number to receive SMS alerts |
| `SENDGRID_API_KEY` | SendGrid API key |
| `SENDGRID_FROM_EMAIL` | Verified sender email address |
| `SENDGRID_TO_EMAIL` | Email address to receive alerts |
| `REDIS_URL` | Redis connection URL (default: `redis://localhost:6379`) |
| `SENTRY_DSN` | Sentry DSN for error tracking (optional) |

### 4. Run locally

```bash
python -m app.main
```

## Running Tests

```bash
pytest
```

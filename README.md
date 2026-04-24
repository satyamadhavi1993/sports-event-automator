# Badminton Tournament Monitor

Monitors NWBA (Northwest Badminton Academy) events on the UBR platform and sends WhatsApp and email notifications when events open for registration. A separate workflow handles automatic check-in on event day.

## How It Works

1. **Event monitor** — Runs hourly from Sunday evening through Tuesday morning (PDT). Logs in to UBR, fetches the Seattle events page, parses the page for NWBA Kirkland (Wednesday) and NWBA Bel-Red (Thursday) events, and sends notifications when either event opens for registration.

2. **Check-in monitor** — Runs every 10 minutes on Wednesday and Thursday evenings (7PM–10PM PDT). Logs in, detects today's event, and clicks the Check In button as soon as it becomes available.

## Tech Stack

- **Python 3.11+**
- **Playwright** — Browser automation for login, navigation, and check-in
- **Twilio** — WhatsApp notifications
- **SendGrid** — Email notifications
- **structlog** — Structured logging
- **GitHub Actions** — Scheduled monitoring runs

## Project Structure

```
app/
  events.py     — shared event constants and logging setup
  config.py     — environment variable loading via pydantic-settings
  monitor.py    — UBRClient: login and page navigation
  detector.py   — EventDetector: parses page text for open events
  notifier.py   — Notifier: composes and sends WhatsApp + email alerts
  check_in.py   — CheckInMonitor: detects and performs check-in
  main.py       — entry point for event monitoring workflow
```

## Setup

### 1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `UBR_BASE_URL` | UBR platform base URL |
| `UBR_EMAIL` | Your UBR account email |
| `UBR_PASSWORD` | Your UBR account password |
| `TWILIO_ACCOUNT_SID` | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | Twilio auth token |
| `TWILIO_FROM_NUMBER` | Twilio WhatsApp sandbox number |
| `TWILIO_TO_NUMBER` | Your phone number to receive alerts |
| `SENDGRID_API_KEY` | SendGrid API key |
| `SENDGRID_FROM_EMAIL` | Verified sender email address |
| `SENDGRID_TO_EMAIL` | Email address to receive alerts |

### 4. Run locally

```bash
# Event monitor
python -m app.main

# Check-in monitor
python -m app.check_in
```

## GitHub Actions

Two workflows run automatically — no server required.

| Workflow | Schedule | Purpose |
|---|---|---|
| `event_monitor.yml` | Hourly, Sun 6PM – Tue 3AM PDT | Detects open registration |
| `checkin_monitor.yml` | Every 10 min, Wed/Thu 7PM–10PM PDT | Performs check-in |

Add all variables from the table above as repository secrets under **Settings → Secrets and variables → Actions**.

# Sports Event Monitor

An automated sports event monitoring system that detects when registration opens, sends instant WhatsApp and email alerts, and handles event check-in — built with Python, Playwright, Twilio, SendGrid, and GitHub Actions.

## How It Works

1. **Event monitor** — Runs on a schedule. Logs in to the platform, fetches the events page, parses it for configured Wednesday and Thursday events, and sends notifications when either event opens for registration.

2. **Check-in monitor** — Runs every 10 minutes on event evenings. Logs in, detects today's event based on day of week, and clicks the Check In button as soon as it becomes available.

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
  events.py     — domain constants derived from config (locations, targets)
  config.py     — environment variable loading and logging setup
  monitor.py    — login and page navigation
  detector.py   — parses page text to find open events
  notifier.py   — composes and sends WhatsApp and email alerts
  check_in.py   — detects and performs event check-in
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
| `PLATFORM_URL` | Base URL of the sports platform |
| `PLATFORM_LOGIN_URL` | Full URL of the login page |
| `PLATFORM_EVENTS_URL` | Full URL of the events page with filters |
| `PLATFORM_EMAIL` | Your platform account email |
| `PLATFORM_PASSWORD` | Your platform account password |
| `EVENT_ORGANISER_NAME` | Name of the event organiser to monitor |
| `EVENT_LOCATION_WED` | Wednesday event location name as shown on the platform |
| `EVENT_LOCATION_THU` | Thursday event location name as shown on the platform |
| `TWILIO_ACCOUNT_SID` | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | Twilio auth token |
| `TWILIO_FROM_NUMBER` | Twilio WhatsApp sender number |
| `TWILIO_TO_NUMBER` | Your number to receive alerts |
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
| `event_monitor.yml` | Hourly during configured window | Detects open registration |
| `checkin_monitor.yml` | Every 10 min on event evenings | Performs check-in |

Add all variables from the table above as repository secrets under **Settings → Secrets and variables → Actions**.

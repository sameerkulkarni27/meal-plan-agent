# Meal Plan Scheduler

A FastAPI-based event scheduler that sends email notifications to users at specified times. Supports one-time and recurring daily notifications.

## Features

- Schedule email notifications for specific users
- Support for one-time notifications or daily recurring schedules
- RESTful API endpoints for managing events
- Background job scheduling with APScheduler
- Email delivery using SMTP (Gmail-compatible)

## Project Structure

```
meal-plan-agent/
├── server/                          # Backend (Python/FastAPI)
│   ├── main.py                      # FastAPI application entry point
│   ├── models.py                    # Pydantic request/response models
│   ├── scheduler.py                 # APScheduler configuration and management
│   ├── email_service.py             # Email sending functionality
│   ├── config.py                    # Application settings
│   ├── pyproject.toml               # uv project configuration
│   ├── .env                         # Environment variables (local, not committed)
│   ├── .env.example                 # Environment variables template
│   ├── .gitignore                   # Python-specific git ignore rules
│   └── .venv/                       # Virtual environment (auto-created by uv)
├── frontend/                        # Frontend (optional - different stack)
├── .gitignore                       # Root-level git ignore rules
└── README.md                        # This file
```

## Setup

### Backend (Server) Setup

Navigate to the server directory:

```bash
cd server
```

#### 1. Install Dependencies

Using `uv` (recommended):

```bash
# Install uv if you haven't already
pip install uv

# Install dependencies
uv sync
```

#### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your SMTP credentials:

```bash
cp .env.example .env
```

Edit `.env` with your email configuration:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SENDER_EMAIL=your-email@gmail.com
```

**Note for Gmail users:** Use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password for `SMTP_PASSWORD`.

#### 3. Run the Server

Using `uv`:

```bash
uv run -m uvicorn main:app --reload
```

Or directly:

```bash
python main.py
```

The server will start at `http://localhost:8000`

## API Endpoints

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "app": "Meal Plan Scheduler"
}
```

### Schedule an Event

**POST** `/schedule-event`

Schedule a new email notification event.

```bash
curl -X POST http://localhost:8000/schedule-event \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "time": "14:30:00",
    "repeated": "daily",
    "email": "user@example.com"
  }'
```

**Request Parameters:**
- `user_id` (string, required): Unique identifier for the user
- `time` (string, required): Time for notification in one of two formats:
  - `HH:MM:SS` for daily recurring notifications (e.g., "14:30:00")
  - ISO format with date `YYYY-MM-DDTHH:MM:SS` for one-time notifications (e.g., "2024-12-27T14:30:00")
- `repeated` (string, required): `"daily"` or `"none"`
- `email` (string, required): Valid email address for receiving notifications

**Response:**
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "scheduled_time": "14:30:00",
  "repeated": "daily",
  "status": "scheduled",
  "message": "Event scheduled successfully. Next run: 2024-12-27 14:30:00"
}
```

### One-Time Notification Example

```bash
curl -X POST http://localhost:8000/schedule-event \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user456",
    "time": "2024-12-27T16:45:00",
    "repeated": "none",
    "email": "user456@example.com"
  }'
```

### Get User Events

**GET** `/events/{user_id}`

Retrieve all scheduled events for a specific user.

```bash
curl http://localhost:8000/events/user123
```

Response:
```json
{
  "user_id": "user123",
  "events": [
    {
      "event_id": "550e8400-e29b-41d4-a716-446655440000",
      "is_active": true,
      "next_run_time": "2024-12-28T14:30:00",
      "scheduled_time": "14:30:00",
      "repeated": "daily"
    }
  ],
  "count": 1
}
```

### Get Event Details

**GET** `/events/{user_id}/{event_id}`

Get detailed information about a specific event.

```bash
curl http://localhost:8000/events/user123/550e8400-e29b-41d4-a716-446655440000
```

Response:
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "is_active": true,
  "next_run_time": "2024-12-28T14:30:00",
  "scheduled_time": "14:30:00",
  "repeated": "daily"
}
```

### Delete Event

**DELETE** `/events/{user_id}/{event_id}`

Remove a scheduled event.

```bash
curl -X DELETE http://localhost:8000/events/user123/550e8400-e29b-41d4-a716-446655440000
```

Response:
```json
{
  "status": "deleted",
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Event deleted successfully"
}
```

## Usage Examples

### Example 1: Daily Notification at 9:00 AM

```bash
curl -X POST http://localhost:8000/schedule-event \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "john_doe",
    "time": "09:00:00",
    "repeated": "daily",
    "email": "john@example.com"
  }'
```

### Example 2: One-Time Notification Tomorrow at 3 PM

```bash
curl -X POST http://localhost:8000/schedule-event \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "jane_smith",
    "time": "2024-12-28T15:00:00",
    "repeated": "none",
    "email": "jane@example.com"
  }'
```

### Example 3: List All Events for a User

```bash
curl http://localhost:8000/events/john_doe
```

### Example 4: Cancel a Daily Notification

First, get the event ID from the user's events list, then delete it:

```bash
curl -X DELETE http://localhost:8000/events/john_doe/550e8400-e29b-41d4-a716-446655440000
```

## Technical Details

### Scheduler
- **Library**: APScheduler (Advanced Python Scheduler)
- **Type**: Background scheduler running in a separate thread
- **Storage**: In-memory event storage (events are lost on server restart)

### Email Service
- **Library**: aiosmtplib (async SMTP)
- **Protocol**: SMTP with TLS support
- **Default**: Gmail (compatible with other SMTP servers)

### Request Validation
- Uses Pydantic models for strict request validation
- Email validation ensures valid email addresses
- Enum validation for the `repeated` field

## Error Handling

### 400 Bad Request
- Invalid request format or parameters
- Invalid time format
- Invalid email address

### 404 Not Found
- Event not found
- User has no events

### 500 Internal Server Error
- SMTP connection issues
- Scheduler errors

## Notes

- Events are stored in memory and will be lost if the server is restarted
- For production, consider implementing persistent storage (database)
- Daily recurring events use the same time each day
- Email credentials must be valid for notifications to work
- The scheduler runs in background; the API remains responsive

## Future Enhancements

- Database persistence for events
- Event logging and history
- Multiple notification types (SMS, push notifications)
- Webhook support for custom actions
- Event templates and customization
- Timezone support

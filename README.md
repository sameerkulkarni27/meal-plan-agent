# Meal Plan Scheduler Agent

A FastAPI-based meal planning agent that sends personalized email notifications to users at specified meal times. Supports one-time and recurring daily notifications.

## Features

- Conversational agent with memory that schedules meal reminders
- Automatic time format conversion (5:30 PM → 17:30:00)
- Custom emails with meal names and types
- Support for one-time and daily recurring reminders
- SMTP delivery (Gmail-compatible)
- Schedule, view, and delete events programmatically
- Background job scheduling with APScheduler

## Project Structure

```
meal-plan-agent/
├── server/
│   ├── main.py                      # FastAPI application
│   ├── models.py                    # Request/response models
│   ├── scheduler.py                 # APScheduler management
│   ├── email_service.py             # Email functionality
│   ├── config.py                    # Application settings
│   ├── agent/                       # AI Agent
│   │   ├── agent.py                 # LangChain agent setup
│   │   ├── tools.py                 # Agent tools
│   │   └── prompt.py                # System prompts
│   └── pyproject.toml               # Server dependencies
├── requirements-agent.txt           # Agent dependencies
├── requirements-server.txt          # Server dependencies
└── README.md
```

## Setup

### Prerequisites
- Python 3.11+
- Gmail account with [App Password](https://support.google.com/accounts/answer/185833)
- OpenAI API key

### 1. Clone & Install
```bash
git clone 
cd meal-plan-agent
```

**Server Environment:**
```bash
python -m venv server-env
source server-env/bin/activate
pip install -r requirements-server.txt
```

**Agent Environment:**
```bash
python -m venv agent-env
source agent-env/bin/activate 
pip install -r requirements-agent.txt
```

### 2. Configure Environment

**Create `server/.env`:**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
SENDER_EMAIL=your-email@gmail.com
```

**Note for Gmail users:** Use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password for `SMTP_PASSWORD`.

**Create `.env` in project root:**
```env
OPENAI_API_KEY=your-openai-api-key
```

### 3. Run

**Terminal 1 - Start Server:**
```bash
source server-env/bin/activate
cd server
python main.py
```
Server runs at `http://localhost:8000`

**Terminal 2 - Start Agent:**
```bash
source agent-env/bin/activate
python server/agent/agent.py
```
## Using the AI Agent

### Example Conversation
```
🍽️ Meal Reminder Scheduling Assistant
Enter your user ID: john_doe
Enter your email: john@example.com

You: I want a dinner reminder at 6pm
Agent: What's the name of your dinner?

You: Grilled Salmon
Agent: ✓ Scheduled daily dinner reminder: 'Grilled Salmon' at 18:00:00
      Is there anything else I can help you schedule?

You: No thanks
Agent: Your reminders are scheduled. Have a great day! 👋
```
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

### Schedule Event

**POST** `/schedule-event`
```bash
curl -X POST http://localhost:8000/schedule-event \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "time": "18:00:00",
    "repeated": "daily",
    "email": "user@example.com",
    "meal_name": "Chicken Alfredo",
    "meal_type": "dinner"
  }'
```

**Parameters:**
- `user_id` (string): Unique identifier
- `time` (string): `HH:MM:SS` for daily, `YYYY-MM-DDTHH:MM:SS` for one-time
- `repeated` (string): `"daily"` or `"none"`
- `email` (string): Valid email address
- `meal_name` (string): Name of the meal
- `meal_type` (string): Type (breakfast, lunch, dinner)

**Response:**
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "scheduled_time": "18:00:00",
  "repeated": "daily",
  "status": "scheduled",
  "message": "Event scheduled successfully. Next run: 2025-11-29 18:00:00"
}
```

### Get User Events

**GET** `/events/{user_id}`
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
      "next_run_time": "2025-11-29T18:00:00",
      "scheduled_time": "18:00:00",
      "repeated": "daily"
    }
  ],
  "count": 1
}
```

### Get Event Details

**GET** `/events/{user_id}/{event_id}`
```bash
curl http://localhost:8000/events/user123/550e8400-e29b-41d4-a716-446655440000
```

Response:
```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "is_active": true,
  "next_run_time": "2025-11-29T18:00:00",
  "scheduled_time": "18:00:00",
  "repeated": "daily"
}
```

### Delete Event

**DELETE** `/events/{user_id}/{event_id}`
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

## Email Format

Personalized emails include:
- **Subject**: "Meal Plan Notification"
- **Body**: "It's time for your dinner!"
- **Meal**: "Chicken Alfredo" (prominently displayed)

## Notes

- Events stored in-memory (lost on restart)
- Gmail requires App Password, not regular password
- Two separate virtual environments for server/agent due to dependency conflicts

## Future Enhancements

- Frontend UI
- Meal ideas based on ingredients/allergies
- Weekly meal planning
- Shopping integration
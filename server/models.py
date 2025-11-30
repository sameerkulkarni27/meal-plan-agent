from pydantic import BaseModel, EmailStr
from typing import Literal
from datetime import datetime


class ScheduleEventRequest(BaseModel):
    """Request model for scheduling an event."""

    user_id: str
    time: str  # ISO format: "2024-12-27T14:30:00" or time format "14:30:00"
    repeated: Literal["daily", "none"] = "none"
    email: EmailStr  # User's email address for notifications
    meal_name: str 
    meal_type: str


class ScheduleEventResponse(BaseModel):
    """Response model for scheduled event."""

    event_id: str
    user_id: str
    scheduled_time: str
    repeated: str
    status: str
    message: str


class EventStatus(BaseModel):
    """Event status information."""

    event_id: str
    user_id: str
    is_active: bool
    next_run_time: str | None
    scheduled_time: str
    repeated: str

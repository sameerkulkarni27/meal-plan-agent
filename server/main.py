from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from models import ScheduleEventRequest, ScheduleEventResponse, EventStatus
from scheduler import (
    start_scheduler,
    shutdown_scheduler,
    add_event,
    remove_event,
    get_event_status,
    get_user_events,
)
from email_service import send_email_notification_sync
from config import settings


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler()
    yield
    # Shutdown
    shutdown_scheduler()


# Create FastAPI app
app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "app": settings.app_name}


@app.post("/schedule-event", response_model=ScheduleEventResponse)
async def schedule_event(request: ScheduleEventRequest):
    """
    Schedule an email notification event for a user.

    Args:
        request: ScheduleEventRequest containing:
            - user_id: Unique identifier for the user
            - time: Time to send notification (ISO format or HH:MM:SS)
            - repeated: "daily" for daily notifications, "none" for one-time
            - email: User's email address for notifications

    Returns:
        ScheduleEventResponse with event details and confirmation
    """
    try:
        event_id, next_run_time = add_event(
            user_id=request.user_id,
            time_str=request.time,
            repeated=request.repeated,
            notification_func=send_email_notification_sync,
            email=request.email,
            meal_name=request.meal_name,
            meal_type=request.meal_type
        )

        return ScheduleEventResponse(
            event_id=event_id,
            user_id=request.user_id,
            scheduled_time=request.time,
            repeated=request.repeated,
            status="scheduled",
            message=f"Event scheduled successfully. Next run: {next_run_time}",
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/events/{user_id}")
async def get_user_events_endpoint(user_id: str):
    """Get all scheduled events for a specific user."""
    try:
        events = get_user_events(user_id)
        return {
            "user_id": user_id,
            "events": events,
            "count": len(events),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/events/{user_id}/{event_id}", response_model=EventStatus)
async def get_event_details(user_id: str, event_id: str):
    """Get details of a specific event."""
    try:
        event_status = get_event_status(event_id)
        if not event_status or event_status["user_id"] != user_id:
            raise HTTPException(status_code=404, detail="Event not found")

        return EventStatus(**event_status)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/events/{user_id}/{event_id}")
async def delete_event(user_id: str, event_id: str):
    """Delete a scheduled event."""
    try:
        event_status = get_event_status(event_id)
        if not event_status or event_status["user_id"] != user_id:
            raise HTTPException(status_code=404, detail="Event not found")

        if remove_event(event_id):
            return {"status": "deleted", "event_id": event_id, "message": "Event deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Event not found")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

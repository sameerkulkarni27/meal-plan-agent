from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime
import uuid
from typing import Dict

scheduler = BackgroundScheduler()
scheduled_events: Dict[str, dict] = {}


def start_scheduler():
    """Start the background scheduler."""
    if not scheduler.running:
        scheduler.start()
        print("Scheduler started successfully")


def shutdown_scheduler():
    """Shutdown the background scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        print("Scheduler shut down")


def add_event(
    user_id: str,
    time_str: str,
    repeated: str,
    notification_func,
    email: str,
    meal_name: str,
    meal_type: str
):
    """
    Add a scheduled event to the scheduler.

    Args:
        user_id: User identifier
        time_str: Time in ISO format (2024-12-27T14:30:00) or HH:MM:SS format
        repeated: "daily" or "none"
        notification_func: Callable function to execute
        email: User's email address

    Returns:
        event_id: Unique identifier for the scheduled event
    """
    event_id = str(uuid.uuid4())

    try:
        # Parse the time string
        if "T" in time_str:  # ISO format with date
            scheduled_time = datetime.fromisoformat(time_str)
            trigger = DateTrigger(run_date=scheduled_time)
        else:  # Just time format HH:MM:SS
            time_parts = time_str.split(":")
            hour = int(time_parts[0])
            minute = int(time_parts[1]) if len(time_parts) > 1 else 0
            second = int(time_parts[2]) if len(time_parts) > 2 else 0

            trigger = CronTrigger(hour=hour, minute=minute, second=second)
            scheduled_time = f"{hour:02d}:{minute:02d}:{second:02d}"

        # Add job to scheduler
        job = scheduler.add_job(
            notification_func,
            trigger=trigger,
            args=[user_id, email, meal_name, meal_type],
            id=event_id,
            name=f"Notification for {user_id}",
            replace_existing=False,
        )

        # Store event metadata
        scheduled_events[event_id] = {
            "user_id": user_id,
            "email": email,
            "time": scheduled_time,
            "repeated": repeated,
            "meal_name": meal_name,    
            "meal_type": meal_type,

            "created_at": datetime.now().isoformat(),
            "job_id": event_id,
        }

        print(f"[SCHEDULER] Event {event_id} scheduled for user {user_id} at {job.next_run_time}")
        return event_id, job.next_run_time

    except Exception as e:
        raise ValueError(f"Failed to schedule event: {str(e)}")


def remove_event(event_id: str):
    """Remove a scheduled event."""
    if event_id in scheduled_events:
        try:
            scheduler.remove_job(event_id)
            del scheduled_events[event_id]
            return True
        except Exception as e:
            raise ValueError(f"Failed to remove event: {str(e)}")
    return False


def get_event_status(event_id: str):
    """Get the status of a scheduled event."""
    if event_id not in scheduled_events:
        return None

    try:
        job = scheduler.get_job(event_id)
        event_data = scheduled_events[event_id]

        return {
            "event_id": event_id,
            "user_id": event_data["user_id"],
            "is_active": job is not None,
            "next_run_time": job.next_run_time.isoformat() if job else None,
            "scheduled_time": event_data["time"],
            "repeated": event_data["repeated"],
        }
    except Exception as e:
        raise ValueError(f"Failed to get event status: {str(e)}")


def get_user_events(user_id: str):
    """Get all events for a specific user."""
    user_events = []
    for event_id, event_data in scheduled_events.items():
        if event_data["user_id"] == user_id:
            try:
                job = scheduler.get_job(event_id)
                user_events.append(
                    {
                        "event_id": event_id,
                        "is_active": job is not None,
                        "next_run_time": job.next_run_time.isoformat() if job else None,
                        "scheduled_time": event_data["time"],
                        "repeated": event_data["repeated"],
                    }
                )
            except Exception:
                pass

    return user_events

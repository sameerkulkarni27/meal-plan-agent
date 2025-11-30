from langchain_core.tools import tool
from typing import Literal
import httpx

@tool(
    "meal_reminder_scheduler",
    parse_docstring=True,
    description=(
        "Schedule meal reminder emails for meals at given times. "
        "Use this whenever user wants to set up meal notifications in their email. "
        "IMPORTANT: Always use the user_id and email from the conversation context."
    ),
)
async def schedule_meal_reminder(
    user_id: str,
    email: str,
    time: str,
    meal_name: str,
    meal_type: Literal["breakfast", "lunch", "dinner"],
    repeated: Literal["daily", "none"] = "daily"
) -> str:
    """
    Schedule a meal reminder email (daily by default).
    
    Args:
        user_id: User identifier from context
        email: User email address from context
        time: Time for meal in two formats: HH:MM:SS or YYYY-MM-DDTHH:MM:SS
        meal_name: Name of the meal
        meal_type: Type of the meal (breakfast, lunch, dinner)
        repeated: Schedule meal reminder email with 'daily' by default or 'none' for one-time
    
    Returns:
        Success message or error message
    """
    
    try:
        async with httpx.AsyncClient() as client:
            payload = {
                "user_id": user_id,
                "time": time,
                "repeated": repeated,
                "email": email,
                "meal_name": meal_name,
                "meal_type": meal_type
            }
            
            response = await client.post(
                "http://localhost:8000/schedule-event",
                json=payload,
                timeout=10.0
            )
            
            response.raise_for_status()
            result = response.json()
            
            repeated_text = "daily" if repeated == "daily" else "one-time"
            return f"Scheduled {repeated_text} {meal_type} reminder: '{meal_name}' at {time}"
    
    except httpx.HTTPError as e:
        error_msg = f"HTTP Error: {str(e)}"
        return f"[SCHEDULE ERROR] {error_msg}"
    except Exception as e:
        error_msg = f"Failed: {str(e)}"
        return f"[SCHEDULE ERROR] {error_msg}"

@tool(
    "end_conversation",
    description=(
        "End the conversation gracefully when the user is done scheduling. "
        "Use this when the user says no/nothing/that's all."
    ),
)
def end_conversation() -> str:
    """End the conversation."""
    return "CONVERSATION_COMPLETE"
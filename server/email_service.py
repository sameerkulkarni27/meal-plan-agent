import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings
import asyncio


async def send_email_notification(
    user_id: str,
    recipient_email: str,
    meal_name: str,
    meal_type: str
):
    """
    Send an email notification to the user.

    Args:
        user_id: User identifier
        recipient_email: Email address to send notification to
    """
    try:
        # Debug: Check if credentials are loaded
        if not settings.smtp_user or not settings.smtp_password:
            raise ValueError("SMTP credentials not configured in .env file")

        print(f"[EMAIL DEBUG] Using SMTP user: {settings.smtp_user}")
        print(f"[EMAIL DEBUG] Password length: {len(settings.smtp_password)}")
        # Create email message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Meal Plan Notification"
        message["From"] = settings.sender_email
        message["To"] = recipient_email

        # Email body
        text = f"Hello! This is your scheduled meal plan notification for user ID: {user_id}"
        html = f"""\
        <html>
          <body>
            <h2>Hello!</h2>
            <p>This is your scheduled meal plan notification.</p>
            <p><strong>User ID:</strong> {user_id}</p>

            <p>It's time for your {meal_type}!</p>
            <h3>{meal_name}</h3>
            <br>
            <p>Best regards,<br>Meal Plan Agent</p>
          </body>
        </html>
        """

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        message.attach(part1)
        message.attach(part2)

        # Send email
        async with aiosmtplib.SMTP(hostname=settings.smtp_host, port=settings.smtp_port, use_tls=True) as smtp:
            await smtp.login(settings.smtp_user, settings.smtp_password)
            await smtp.send_message(message)

        print(f"Email notification sent to {recipient_email} for user {user_id}")
        return True

    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email notification: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def send_email_notification_sync(
    user_id: str,
    recipient_email: str,
    meal_name: str,
    meal_type: str
):
    """
    Synchronous wrapper for sending email notifications.
    Used by APScheduler which doesn't support async directly.
    """
    try:
        print(f"[EMAIL] Starting to send notification to {recipient_email} for user {user_id}")
        asyncio.run(send_email_notification(
            user_id,
            recipient_email,
            meal_name,
            meal_type
        ))
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send: {str(e)}")
        import traceback
        traceback.print_exc()

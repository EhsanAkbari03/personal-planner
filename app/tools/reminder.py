from datetime import datetime

def create_reminder(title: str, remind_at: str) -> dict:
    """
    Create a reminder for the user.

    Args:
        title: The reminder title.
        remind_at: Reminder date and time in ISO 8601 format.
                   Example: 2026-08-30T15:00:00

    Returns:
        A dictionary containing the reminder information.
    """

    reminder = {
        "title": title,
        "remind_at": remind_at,
        "created_at": datetime.now().isoformat()
    }

    print("Reminder created:", reminder)

    return {
        "success": True,
        "message": f"Reminder '{title}' created successfully.",
        "reminder": reminder
    }
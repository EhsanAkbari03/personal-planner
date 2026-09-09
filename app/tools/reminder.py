from datetime import datetime

from app.services.task_services import TaskService
from app.repositories.task_repository import TaskRepository
from app.database.connection import get_db

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









def delete_reminder():
    print("Reminder deleted.")
def update_reminder():
    print("Reminder updated.")

def create_task(
        title: str,
    description: str | None,
    start_at: str,
    end_at: str | None,
    priority: int = 1
)-> dict:
    """
    Create a new task for the user.

    Args:
        title: Task title.
        description: Optional task description.
        start_at: Task start date and time in ISO 8601 format.
        end_at: Optional task end date and time in ISO 8601 format.
        priority: Task priority from 1 to 5.

    Returns:
        A dictionary containing the created task information.
    """
    print("Task created.")
def complete_task():
    print("Task completed.")

def delete_task():
    print("Task deleted.")
def update_task():
    print("Task updated.")

def get_today_tasks():
    print("Fetching today's tasks.")
def get_tomorrow_tasks():
    print("Fetching tomorrow's tasks.")

def create_schedule():
    print("Schedule created.")
def update_schedule():
    print("Schedule updated.")

def get_free_time():
    print("Fetching free time.")

def find_tasks_for_time():
    print("Finding tasks for the specified time.")

def add_habit():
    print("Habit added.")
def complete_habit():
    print("Habit completed.")

def get_daily_plan():
    print("Fetching daily plan.")
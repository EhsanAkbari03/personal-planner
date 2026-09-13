from datetime import datetime

from app.services.task_services import TaskService



task_service = TaskService()


def create_task(
    title: str,
    user_id: int, 
    description: str | None,
    start_at: str,
    end_at: str | None,
    priority: int = 1
) -> dict:


    """
    Create a new task for the user.

    Use this function when the user asks to create,
    add, or schedule a task.

    Args:
        title:
            The title of the task.

        description:
            Optional additional details about the task.

        start_at:
            The date and time when the task starts.
            Must be in ISO 8601 format.
            Example: 2026-09-03T15:00:00

        end_at:
            Optional end date and time of the task.
            Must be in ISO 8601 format if provided.

        priority:
            Task priority from 1 to 5.
            1 is the lowest priority and 5 is the highest.

    Returns:
        A dictionary containing the created task information.
    """

    task = task_service.create_task(
        title=title,
        user_id=user_id, 
        description=description,
        start_at=datetime.fromisoformat(start_at),
        end_at=(
            datetime.fromisoformat(end_at)
            if end_at
            else None
        ),
        priority=priority
    )

    return {
        "success": True,
        "task_id": task.id,
        "title": task.title,
        "description": task.description,
        "start_at": task.start_at.isoformat(),
        "end_at": (
            task.end_at.isoformat()
            if task.end_at
            else None
        ),
        "priority": task.priority,
        "status": task.status
    }



def delete_task(
    task_id: int,
    user_id: int
) -> dict:

    """
    Delete an existing task.

    Use this function when the user explicitly asks
    to delete or remove a task.

    Args:
        task_id:
            The unique ID of the task to delete.

        user_id:
            The ID of the user who owns the task.

    Returns:
        A dictionary indicating whether the task
        was deleted successfully.
    """

    deleted = task_service.delete_task(
        task_id=task_id,
        user_id=user_id
    )

    if deleted:
        return {
            "success": True,
            "task_id": task_id,
            "message": "Task deleted successfully."
        }

    return {
        "success": False,
        "task_id": task_id,
        "message": "Task not found."
    }


def get_tasks_by_date( date: str, user_id: int) -> dict:
    """
    Get all tasks scheduled for a specific date for the current user.

    This tool should be used when the user asks:
    - What do I have today?
    - What are my tasks tomorrow?
    - Show 10/3's schedule.
    - What is my plan for Saturday?
    """

    tasks = task_service.get_tasks_by_date(date, user_id)

    return {
        "success": True,
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "start_at": task.start_at.isoformat(),
                "end_at": (
                    task.end_at.isoformat()
                    if task.end_at
                    else None
                ),
                "priority": task.priority,
                "status": task.status
            }
            for task in tasks
        ]
    }


def find_tasks_by_title(title: str, user_id: int) -> dict:
    """
    Find tasks by title or keyword for the current user.
    """
    try:
        tasks = task_service.find_tasks_by_title(title=title, user_id=user_id)

        formatted_tasks = []
        for task in tasks:
            # تبدیل ایمن تاریخ به رشته ISO
            start_str = (
                task.start_at.isoformat()
                if hasattr(task.start_at, "isoformat")
                else str(task.start_at)
            )
            
            end_str = None
            if task.end_at:
                end_str = (
                    task.end_at.isoformat()
                    if hasattr(task.end_at, "isoformat")
                    else str(task.end_at)
                )

            formatted_tasks.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "start_at": start_str,
                "end_at": end_str,
                "priority": task.priority,
                "status": task.status,
            })

        return {
            "success": True,
            "tasks": formatted_tasks,
            "count": len(formatted_tasks),
        }

    except Exception as e:
        # جلوگیری از کرش ابزار و ارسال پیغام خطا به LLM
        return {
            "success": False,
            "error": str(e),
            "tasks": [],
        }
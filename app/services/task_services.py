from datetime import datetime

from app.models.task import Task
from app.repositories.task_repository import TaskRepository
from app.database.connection import get_db
from datetime import datetime


class TaskService:

    def __init__(self):
        self.repository = TaskRepository(get_db())

    def create_task(
        self,
        user_id: int,
        title: str,
        description: str | None,
        start_at: datetime,
        end_at: datetime | None,
        priority: int = 1
    ) -> Task:

        # -------------------------
        # Validation
        # -------------------------

        if not title or not title.strip():
            raise ValueError("Task title cannot be empty.")

        if priority < 1 or priority > 5:
            raise ValueError(
                "Priority must be between 1 and 5."
            )

        if end_at is not None and end_at <= start_at:
            raise ValueError(
                "end_at must be after start_at."
            )

        # -------------------------
        # Create Task Object
        # -------------------------

        task = Task(
            id=None,
            user_id=user_id,
            title=title.strip(),
            description=description,
            start_at=start_at,
            end_at=end_at,
            priority=priority,
            status="pending"
        )

        # -------------------------
        # Save to Database
        # -------------------------

        return self.repository.create(task)

    def get_task(self, task_id: int) -> Task | None:

        return self.repository.get_by_id(task_id)


    def delete_task(
        self,
        task_id: int,
        user_id: int
    ) -> bool:

        if task_id <= 0:
            raise ValueError("Invalid task_id.")

        if user_id <= 0:
            raise ValueError("Invalid user_id.")

        return self.repository.delete(
            task_id=task_id,
            user_id=user_id
        )




    def get_tasks_by_date(self,
                           date: str,user_id: int) -> list[Task]:

        if user_id <= 0:
            raise ValueError("Invalid user_id.")

        return self.repository.get_tasks_by_date(date=date, user_id=user_id)

    # =========================================================
    # Find tasks by title
    # =========================================================

    def find_tasks_by_title(
        self,
        title: str,
        user_id: int
    ) -> list[Task]:

        if user_id <= 0:
            raise ValueError("Invalid user_id.")

        if not title or not title.strip():
            raise ValueError("Task title cannot be empty.")

        return self.repository.find_by_title(
            title=title.strip(),
            user_id=user_id
        )
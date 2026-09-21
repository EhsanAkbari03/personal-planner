from app.repositories.habit_log_repository import HabitLogRepository


class HabitLogService:

    def __init__(self, db):
        self.repository = HabitLogRepository(db)

    def create_log(
        self,
        habit_id: int,
        scheduled_date,
        status: str,
        points_earned: int = 0
    ):

        if status not in ["completed", "missed"]:
            raise ValueError(
                "status must be completed or missed"
            )

        if status == "missed":
            points_earned = 0

        return self.repository.create(
            habit_id=habit_id,
            scheduled_date=scheduled_date,
            status=status,
            points_earned=points_earned
        )
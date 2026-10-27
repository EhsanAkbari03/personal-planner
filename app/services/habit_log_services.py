
from app.repositories.habit_log_repository import HabitLogRepository
from app.repositories.habit_repository import HabitRepository


class HabitLogService:

    def __init__(self, db):
        self.db = db
        self.repository = HabitLogRepository(db)
        self.habit_repository = HabitRepository(db)

    @staticmethod
    def calculate_consistency(logs):
        score = 100

        for scheduled_date, status in logs:
            if status == "missed":
                score = round(score * 0.9)
            elif status == "completed":
                score = min(100, score + 10)

        return max(0, min(100, score))

    def create_log(
        self,
        habit_id: int,
        user_id: int,
        scheduled_date,
        status: str,
    ):
        if status not in ("completed", "missed"):
            raise ValueError(
                "status must be completed or missed"
            )

        try:
            habit = self.habit_repository.get_for_user(
                habit_id=habit_id,
                user_id=user_id,
            )

            if not habit:
                raise LookupError("Habit not found")

            points_earned = (
                habit["points"] if status == "completed" else 0
            )

            log = self.repository.upsert(
                habit_id=habit_id,
                scheduled_date=scheduled_date,
                status=status,
                points_earned=points_earned,
            )

            logs = self.repository.get_all_statuses(habit_id)
            score = self.calculate_consistency(logs)

            self.habit_repository.update_consistency_score(
                habit_id=habit_id,
                score=score,
            )

            print(f"Habit {habit_id} consistency score: {score}")

            self.db.commit()

            return {
                "success": True,
                "log": {
                    "id": log[0],
                    "habit_id": log[1],
                    "scheduled_date": log[2],
                    "status": log[3],
                    "points_earned": log[4],
                },
                "consistency_score": score,
            }

        except Exception:
            self.db.rollback()
            raise

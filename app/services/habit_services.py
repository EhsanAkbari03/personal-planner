
from app.repositories.habit_repository import HabitRepository
from app.models.habit import HabitCreate
from app.models.habit import VALID_CATEGORIES
from app.database.connection import get_db



class HabitService:

    def __init__(self, db):
        self.repository = HabitRepository(db)

    def create_habit(
        self,
        user_id: int,
        habit: HabitCreate,
    ):

        valid_frequency_types = [
            "daily",
            "weekly",
            "monthly",
            "yearly",
        ]

        # Validate frequency type
        if habit.frequency_type not in valid_frequency_types:
            raise ValueError(
                "frequency_type نامعتبر است."
            )

        # Validate category
        if habit.category not in VALID_CATEGORIES:
            raise ValueError(
                "دسته‌بندی عادت نامعتبر است."
            )

        # Weekly validation
        if habit.frequency_type == "weekly":

            if not habit.weekdays:
                raise ValueError(
                    "برای عادت هفتگی باید روزهای هفته مشخص شود."
                )

            for day in habit.weekdays:
                if day < 0 or day > 6:
                    raise ValueError(
                        "روز هفته باید بین 0 تا 6 باشد."
                    )

        # Monthly validation
        if habit.frequency_type == "monthly":

            if habit.day_of_month is None:
                raise ValueError(
                    "برای عادت ماهانه باید روز ماه مشخص شود."
                )

            if not 1 <= habit.day_of_month <= 31:
                raise ValueError(
                    "روز ماه باید بین 1 تا 31 باشد."
                )

        return self.repository.create(
            user_id=user_id,
            title=habit.title,
            description=habit.description,
            frequency_type=habit.frequency_type,
            weekdays=habit.weekdays,
            day_of_month=habit.day_of_month,
            month_of_year=habit.month_of_year,
            reminder_time=habit.reminder_time,
            checkin_time=habit.checkin_time,
            points=habit.points,
            category=habit.category,
        )

    def get_habits_by_date(self, user_id: int, date: str):

        habits = self.repository.get_habits_by_date(
            user_id=user_id,
            date=date
        )

        for habit in habits:

            if habit["log_id"] is None:
                habit["status"] = "pending"
                habit["points_earned"] = 0

        return habits

    def delete_habit_by_title(user_id: int, title: str) -> dict:
        db = get_db()

        try:
            repo = HabitRepository(db)

            habits = repo.find_habits_by_title(
                user_id=user_id,
                title=title
            )

            if not habits:
                return {
                    "success": False,
                    "message": f"عادت «{title}» پیدا نشد."
                }

            if len(habits) > 1:
                return {
                    "success": False,
                    "requires_clarification": True,
                    "message": "چند عادت مشابه پیدا شد. کدام را حذف کنم؟",
                    "candidates": [
                        habit["title"] for habit in habits
                    ]
                }

            habit = habits[0]

            deleted = repo.delete_habit_and_logs(
                user_id=user_id,
                habit_id=habit["habit_id"]
            )

            if not deleted:
                return {
                    "success": False,
                    "message": "عادت پیدا نشد یا قبلاً حذف شده است."
                }

            return {
                "success": True,
                "message": f"عادت «{habit['title']}» و تمام سوابق آن حذف شدند."
            }

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()
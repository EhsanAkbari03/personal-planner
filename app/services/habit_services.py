# app/services/habit_service.py

from app.repositories.habit_repository import HabitRepository
from app.models.habit import HabitCreate


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

        if habit.frequency_type not in valid_frequency_types:
            raise ValueError(
                "frequency_type نامعتبر است."
            )

        # weekly
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

        # monthly
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
        )
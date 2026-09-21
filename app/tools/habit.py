# app/tools/habit.py

from app.models.habit import HabitCreate
from app.services.habit_services import HabitService
from app.database.connection import get_db


def create_habit(
    user_id: int,
    title: str,
    frequency_type: str,
    description: str | None = None,
    weekdays: list[int] | None = None,
    day_of_month: int | None = None,
    month_of_year: int | None = None,
    reminder_time: str | None = None,
    checkin_time: str | None = None,
    points: int = 10,
):

    db = get_db()

    service = HabitService(db)

    habit = HabitCreate(
        title=title,
        description=description,
        frequency_type=frequency_type,
        weekdays=weekdays,
        day_of_month=day_of_month,
        month_of_year=month_of_year,
        reminder_time=reminder_time,
        checkin_time=checkin_time,
        points=points,
    )

    result = service.create_habit(
        user_id=user_id,
        habit=habit,
    )

    return {
        "success": True,
        "message": "عادت با موفقیت ایجاد شد.",
        "habit": {
            "title": title,
            "frequency_type": frequency_type,
            "weekdays": weekdays,
            "day_of_month": day_of_month,
            "reminder_time": reminder_time,
            "checkin_time": checkin_time,
        }
    }
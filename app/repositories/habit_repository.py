# app/repositories/habit_repository.py

class HabitRepository:

    def __init__(self, db):
        self.db = db


    def create(
        self,
        user_id: int,
        title: str,
        description: str | None,
        frequency_type: str,
        weekdays: list[int] | None,
        day_of_month: int | None,
        month_of_year: int | None,
        reminder_time: str | None,
        checkin_time: str | None,
        points: int = 10,
    ):

        with self.db.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO habits (
                    user_id,
                    title,
                    description,
                    frequency_type,
                    weekdays,
                    day_of_month,
                    month_of_year,
                    reminder_time,
                    checkin_time,
                    points
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
                RETURNING
                    id,
                    title,
                    description,
                    frequency_type,
                    weekdays,
                    day_of_month,
                    month_of_year,
                    reminder_time,
                    checkin_time,
                    points,
                    active,
                    created_at
                """,
                (
                    user_id,
                    title,
                    description,
                    frequency_type,
                    weekdays,
                    day_of_month,
                    month_of_year,
                    reminder_time,
                    checkin_time,
                    points,
                )
            )

            habit = cursor.fetchone()

            self.db.commit()

            return habit
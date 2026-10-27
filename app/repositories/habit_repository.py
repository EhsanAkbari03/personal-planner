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
        category: str | None = None
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
                    points,
                    category
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
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
                    created_at,
                    category
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
                    category
                )
            )

            habit = cursor.fetchone()

            self.db.commit()

            return habit

    def get_for_user(self, habit_id: int, user_id: int):
     with self.db.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, user_id, points, consistency_score
            FROM habits
            WHERE id = %s AND user_id = %s
            """,
            (habit_id, user_id)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "user_id": row[1],
            "points": row[2],
            "consistency_score": row[3],
        }


    def update_consistency_score(self, habit_id: int, score: int):
        with self.db.cursor() as cursor:
            cursor.execute(
                """
                UPDATE habits
                SET consistency_score = %s
                WHERE id = %s
                RETURNING id, consistency_score
                """,
                (score, habit_id)
            )

            result = cursor.fetchone()
            print("Updated habit row:", result)
            return result
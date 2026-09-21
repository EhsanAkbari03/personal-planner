import psycopg


class HabitLogRepository:

    def __init__(self, db):
        self.db = db

    def create(
        self,
        habit_id: int,
        scheduled_date,
        status: str,
        points_earned: int
    ):

        try:

            with self.db.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO habit_logs (
                        habit_id,
                        scheduled_date,
                        status,
                        points_earned
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING
                        id,
                        habit_id,
                        scheduled_date,
                        status,
                        points_earned
                    """,
                    (
                        habit_id,
                        scheduled_date,
                        status,
                        points_earned
                    )
                )

                result = cursor.fetchone()

                self.db.commit()

                return result

        except psycopg.errors.UniqueViolation:

            self.db.rollback()

            raise ValueError(
                "برای این عادت در این تاریخ، Habit Log قبلاً ثبت شده است."
            )
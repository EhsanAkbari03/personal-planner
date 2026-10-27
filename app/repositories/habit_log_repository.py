
import psycopg


class HabitLogRepository:

    def __init__(self, db):
        self.db = db

    def upsert(
        self,
        habit_id: int,
        scheduled_date,
        status: str,
        points_earned: int,
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
                    ON CONFLICT (habit_id, scheduled_date)
                    DO UPDATE SET
                        status = EXCLUDED.status,
                        points_earned = EXCLUDED.points_earned
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
                        points_earned,
                    ),
                )

                return cursor.fetchone()

        except psycopg.Error:
            raise

    def get_all_statuses(self, habit_id: int):
     with self.db.cursor() as cursor:
        cursor.execute(
            """
            SELECT scheduled_date, status
            FROM habit_logs
            WHERE habit_id = %s
            ORDER BY scheduled_date ASC
            """,
            (habit_id,)
        )
        return cursor.fetchall()

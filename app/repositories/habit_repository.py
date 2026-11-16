# app/repositories/habit_repository.py

from app.database.connection import get_db


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

    def get_habits_by_date(self, user_id: int, date: str):

        query = """
            SELECT
                h.id AS habit_id,
                h.title,
                h.description,
                h.frequency_type,
                h.weekdays,
                h.day_of_month,
                h.month_of_year,
                h.reminder_time,
                h.checkin_time,
                h.points,
                h.category,
                h.consistency_score,
                h.is_active,

                hl.id AS log_id,
                hl.scheduled_date,
                hl.status,
                hl.points_earned

            FROM habits h

            LEFT JOIN habit_logs hl
                ON hl.habit_id = h.id
                AND hl.scheduled_date = %s::date

            WHERE h.user_id = %s
            AND h.is_active = TRUE

            AND (
                    h.frequency_type = 'daily'

                    OR (
                        h.frequency_type = 'weekly'
                        AND (
                            (EXTRACT(ISODOW FROM %s::date)::int + 5) %% 7
                        ) = ANY(h.weekdays)
                    )

                    OR (
                        h.frequency_type = 'monthly'
                        AND EXTRACT(DAY FROM %s::date)::int = h.day_of_month
                    )

                    OR (
                        h.frequency_type = 'yearly'
                        AND EXTRACT(MONTH FROM %s::date)::int = h.month_of_year
                        AND EXTRACT(DAY FROM %s::date)::int = h.day_of_month
                    )
            )

            ORDER BY h.title ASC;
        """

        with self.db.cursor() as cur:
            cur.execute(
                query,
                (date, user_id, date, date, date, date)
            )

            rows = cur.fetchall()

            columns = [desc.name for desc in cur.description]

            return [
                dict(zip(columns, row))
                for row in rows
            ]

    
    def find_habits_by_title(self, user_id: int, title: str) -> list:
        words = title.strip().split()

        if not words:
            return []

        # ابتدا جست‌وجوی دقیق عنوان
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT id, title
                FROM habits
                WHERE user_id = %s
                  AND LOWER(TRIM(title)) = LOWER(TRIM(%s))
                ORDER BY id
                """,
                (user_id, title)
            )

            rows = cur.fetchall()

            if rows:
                return [
                    {"habit_id": row[0], "title": row[1]}
                    for row in rows
                ]

            # جست‌وجوی کلمه‌ای؛ وجود حداقل یکی از کلمات کافی است
            conditions = " OR ".join(
                ["title ILIKE %s" for _ in words]
            )

            query = f"""
                SELECT id, title
                FROM habits
                WHERE user_id = %s
                  AND ({conditions})
                ORDER BY title
            """

            params = [user_id] + [
                f"%{word}%"
                for word in words
            ]

            cur.execute(query, params)
            rows = cur.fetchall()

            return [
                {"habit_id": row[0], "title": row[1]}
                for row in rows
            ]


    def delete_habit_and_logs(
        self,
        user_id: int,
        habit_id: int
    ) -> bool:

        try:
            with self.db.cursor() as cur:

                cur.execute(
                    """
                    SELECT id
                    FROM habits
                    WHERE id = %s AND user_id = %s
                    FOR UPDATE
                    """,
                    (habit_id, user_id)
                )

                habit = cur.fetchone()

                if not habit:
                    return False

                # حذف Logهای عادت
                cur.execute(
                    """
                    DELETE FROM habit_logs
                    WHERE habit_id = %s
                    """,
                    (habit_id,)
                )

                # حذف خود عادت
                cur.execute(
                    """
                    DELETE FROM habits
                    WHERE id = %s AND user_id = %s
                    """,
                    (habit_id, user_id)
                )

                if cur.rowcount != 1:
                    raise Exception("Habit deletion failed")

            self.db.commit()
            return True

        except Exception:
            self.db.rollback()
            raise

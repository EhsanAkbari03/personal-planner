
class AnalyticsRepository:
    def __init__(self, db):
        self.db = db

    def get_weekly_task_stats(self, user_id, start_date, end_date):
        with self.db.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    created_at::date AS task_date,
                    COUNT(*) AS total,
                    COUNT(*) FILTER (
                        WHERE status = 'completed'
                    ) AS completed
                FROM tasks
                WHERE user_id = %s
                  AND created_at::date BETWEEN %s AND %s
                GROUP BY created_at::date
                ORDER BY task_date;
                """,
                (user_id, start_date, end_date),
            )
            return cursor.fetchall()

    def get_habit_log_stats(self, user_id, start_date, end_date):
        with self.db.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    COUNT(*) FILTER (
                        WHERE hl.status = 'completed'
                    ) AS completed,
                    COUNT(*) FILTER (
                        WHERE hl.status = 'missed'
                    ) AS missed
                FROM habit_logs hl
                JOIN habits h ON h.id = hl.habit_id
                WHERE h.user_id = %s
                  AND hl.scheduled_date BETWEEN %s AND %s;
                """,
                (user_id, start_date, end_date),
            )
            return cursor.fetchone()

    def get_habits_progress(self, user_id, start_date, end_date):
     with self.db.cursor() as cursor:
        cursor.execute("""
            SELECT
                h.id,
                h.title,
                h.points,
                COUNT(hl.id) FILTER (
                    WHERE hl.status IN ('completed', 'missed')
                ) AS total_logs,
                COUNT(hl.id) FILTER (
                    WHERE hl.status = 'completed'
                ) AS completed_logs
            FROM habits h
            LEFT JOIN habit_logs hl
                ON hl.habit_id = h.id
                AND hl.scheduled_date BETWEEN %s AND %s
            WHERE h.user_id = %s
              AND h.active = TRUE
            GROUP BY
                h.id,
                h.title,
                h.points
            ORDER BY h.id;
        """, (start_date, end_date, user_id))

        return cursor.fetchall()

    def get_habits_analytics(self, user_id, start_date, end_date):
        with self.db.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    h.id,
                    h.title,
                    h.consistency_score,

                    COUNT(hl.id) FILTER (
                        WHERE hl.status IN ('completed', 'missed')
                    ) AS total_sessions,

                    COUNT(hl.id) FILTER (
                        WHERE hl.status = 'completed'
                    ) AS completed_sessions,

                    COUNT(hl.id) FILTER (
                        WHERE hl.status = 'missed'
                    ) AS missed_sessions,

                    COUNT(hl.id) FILTER (
                        WHERE hl.status = 'completed'
                        AND hl.scheduled_date BETWEEN %s AND %s
                    ) AS weekly_completed,

                    COUNT(hl.id) FILTER (
                        WHERE hl.status = 'missed'
                        AND hl.scheduled_date BETWEEN %s AND %s
                    ) AS weekly_missed

                FROM habits h
                LEFT JOIN habit_logs hl
                    ON hl.habit_id = h.id

                WHERE h.user_id = %s
                AND h.active = TRUE

                GROUP BY
                    h.id,
                    h.title,
                    h.consistency_score

                ORDER BY h.id;
                """,
                (
                    start_date,
                    end_date,
                    start_date,
                    end_date,
                    user_id,
                ),
            )

            return cursor.fetchall()
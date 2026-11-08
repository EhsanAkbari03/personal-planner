class PreferenceRepository:

    def __init__(self, db):
        self.db = db

    def get_user_preferences(self, user_id: int):
        with self.db.cursor() as cur:
            cur.execute("""
                SELECT *
                FROM user_preferences
                WHERE user_id = %s
            """, (user_id,))

            row = cur.fetchone()

            if row is None:
                return None

            columns = [desc.name for desc in cur.description]
            return dict(zip(columns, row))

    def update_user_preferences(self, user_id: int, preferences: dict):

        allowed_fields = {
            "wake_up_time",
            "sleep_time",
            "day_start_time",
            "day_end_time",
            "preferred_work_start",
            "preferred_work_end",
            "focus_duration_minutes",
            "break_duration_minutes",
            "planning_style",
            "max_daily_tasks",
            "preferred_exercise_time"
        }

        updates = {
            key: value
            for key, value in preferences.items()
            if key in allowed_fields
        }

        if not updates:
            return False

        columns = list(updates.keys())

        set_clause = ", ".join(
            f"{column} = %s" for column in columns
        )

        values = list(updates.values())

        try:
            with self.db.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO user_preferences (
                        user_id, {", ".join(columns)}
                    )
                    VALUES (%s, {", ".join(["%s"] * len(columns))})
                    ON CONFLICT (user_id)
                    DO UPDATE SET
                        {set_clause},
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    [user_id] + values + values
                )

            self.db.commit()
            return True

        except Exception:
            self.db.rollback()
            raise
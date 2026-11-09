import psycopg

POSTGRES_URL = "postgresql://postgres:futOnc9vCcHYLp4wMR6l@remote-pishgaman.runflare.com:31589/habitodbhtr_db"

try:
    with psycopg.connect(POSTGRES_URL) as conn:
        with conn.cursor() as cur:

            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id SERIAL PRIMARY KEY,

                    user_id INTEGER NOT NULL UNIQUE
                        REFERENCES users(id) ON DELETE CASCADE,

                    wake_up_time TIME,
                    sleep_time TIME,

                    day_start_time TIME DEFAULT '07:00',
                    day_end_time TIME DEFAULT '23:00',

                    preferred_work_start TIME,
                    preferred_work_end TIME,

                    focus_duration_minutes INTEGER DEFAULT 50,
                    break_duration_minutes INTEGER DEFAULT 10,

                    planning_style VARCHAR(30) DEFAULT 'balanced',
                    max_daily_tasks INTEGER DEFAULT 5,

                    preferred_exercise_time TIME,

                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    CONSTRAINT valid_focus_duration
                        CHECK (focus_duration_minutes > 0),

                    CONSTRAINT valid_break_duration
                        CHECK (break_duration_minutes >= 0),

                    CONSTRAINT valid_max_daily_tasks
                        CHECK (max_daily_tasks > 0)
                );
            """)

    print("user_preferences table created successfully!")

except Exception as e:
    print(f"Error: {e}")



POSTGRES_URL = "postgresql://postgres:futOnc9vCcHYLp4wMR6l@remote-pishgaman.runflare.com:31589/habitodbhtr_db"


import psycopg

POSTGRES_URL = "postgresql://postgres:futOnc9vCcHYLp4wMR6l@remote-pishgaman.runflare.com:31589/habitodbhtr_db"

reset_db_sql = """
-- ۱. حذف جداول قدیمی (CASCADE باعث میشه وابستگی‌ها هم پاک بشن)
DROP TABLE IF EXISTS habit_logs CASCADE;
DROP TABLE IF EXISTS habits CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;
DROP TABLE IF EXISTS password_reset_codes CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ۲. ساخت جداول جدید با ساختار کامل

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    timezone VARCHAR(50),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    profile_image_uri TEXT,
    subscription_level VARCHAR(50) DEFAULT 'عادی',
    active_days_streak INTEGER DEFAULT 0,
    last_login_date DATE
);

CREATE TABLE password_reset_codes (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    code VARCHAR(10),
    expires_at TIMESTAMP WITHOUT TIME ZONE,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_at TIMESTAMP WITHOUT TIME ZONE,
    end_at TIMESTAMP WITHOUT TIME ZONE,
    priority INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE habits (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    streak_count INTEGER DEFAULT 0,
    last_completed_date DATE,
    frequency_type VARCHAR(50),
    weekdays INTEGER[],
    day_of_month INTEGER,
    month_of_year INTEGER,
    reminder_time VARCHAR(10),
    checkin_time VARCHAR(10),
    points INTEGER DEFAULT 0,
    description TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE habit_logs (
    id SERIAL PRIMARY KEY,
    habit_id INTEGER REFERENCES habits(id) ON DELETE CASCADE,
    scheduled_date DATE,
    status VARCHAR(20),
    points_earned INTEGER DEFAULT 0
);
"""

try:
    print("Connecting to database and resetting tables...")
    with psycopg.connect(POSTGRES_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(reset_db_sql)
            conn.commit()
    print("✅ جداول قدیمی پاک شدند و دیتابیس با ساختار جدید با موفقیت ساخته شد!")
except Exception as e:
    print(f"❌ خطا در عملیات دیتابیس: {e}")
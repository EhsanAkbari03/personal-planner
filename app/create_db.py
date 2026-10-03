import psycopg

# لینک دیتابیس رانفلر خود را دقیقاً اینجا قرار دهید
POSTGRES_URL = "postgresql://postgres:futOnc9vCcHYLp4wMR6l@remote-pishgaman.runflare.com:31589/habitodbhtr_db"

create_tables_sql = """
-- ساخت جدول کاربران
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    password_hash TEXT,
    timezone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    profile_image_uri TEXT,
    subscription_level VARCHAR(50) DEFAULT 'عادی',
    active_days_streak INTEGER DEFAULT 0,
    last_login_date DATE
);

-- ساخت جدول تسک‌ها
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    start_at TIMESTAMP WITH TIME ZONE,
    end_at TIMESTAMP WITH TIME ZONE,
    priority INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'pending'
);

-- ساخت جدول هابیت‌ها (عادت‌ها)
CREATE TABLE IF NOT EXISTS habits (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    streak_count INTEGER DEFAULT 0,
    last_completed_date DATE
);
"""

try:
    print("Connecting to database...")
    with psycopg.connect(POSTGRES_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(create_tables_sql)
            conn.commit()
    print("✅ جداول با موفقیت در دیتابیس رانفلر ساخته شدند!")
except Exception as e:
    print(f"❌ خطا در ساخت جداول: {e}")
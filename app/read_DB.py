




import psycopg
import os

POSTGRES_URL = "postgresql://postgres:futOnc9vCcHYLp4wMR6l@remote-pishgaman.runflare.com:31589/habitodbhtr_db"

try:
    with psycopg.connect(POSTGRES_URL) as conn:
        with conn.cursor() as cur:
            # اضافه کردن ستون، فقط اگر وجود نداشته باشد
            cur.execute("""
                ALTER TABLE habits
                ADD COLUMN IF NOT EXISTS category TEXT;
            """)

            # مقداردهی به عادت‌های قبلی
            cur.execute("""
                UPDATE habits
                SET category = 'routines_goals'
                WHERE category IS NULL;
            """)

            # تعیین مقدار پیش‌فرض و اجباری بودن ستون
            cur.execute("""
                ALTER TABLE habits
                ALTER COLUMN category SET DEFAULT 'routines_goals',
                ALTER COLUMN category SET NOT NULL;
            """)

    print("ستون category به جدول habits اضافه شد.")

except Exception as e:
    print(f"خطا: {e}")










POSTGRES_URL = "postgresql://postgres:futOnc9vCcHYLp4wMR6l@remote-pishgaman.runflare.com:31589/habitodbhtr_db"


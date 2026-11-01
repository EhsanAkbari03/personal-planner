




import psycopg
import os

POSTGRES_URL = "postgresql://postgres:futOnc9vCcHYLp4wMR6l@remote-pishgaman.runflare.com:31589/habitodbhtr_db"

try:
    with psycopg.connect(POSTGRES_URL) as conn:
        with conn.cursor() as cur:
            # اضافه کردن ستون، فقط اگر وجود نداشته باشد
            cur.execute("""
                ALTER TABLE habits
ADD COLUMN IF NOT EXISTS consistency_score INTEGER NOT NULL DEFAULT 100;
            """)

    print("ستون category به جدول habits اضافه شد.")

except Exception as e:
    print(f"خطا: {e}")










POSTGRES_URL = "postgresql://postgres:futOnc9vCcHYLp4wMR6l@remote-pishgaman.runflare.com:31589/habitodbhtr_db"


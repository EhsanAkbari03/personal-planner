
import psycopg

POSTGRES_URL = "postgresql://postgres:futOnc9vCcHYLp4wMR6l@remote-pishgaman.runflare.com:31589/habitodbhtr_db"

try:
    with psycopg.connect(POSTGRES_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                ALTER TABLE habits
                ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;
            """)

    print("ستون is_active با موفقیت به جدول habits اضافه شد.")

except Exception as e:
    print(f"خطا: {e}")










POSTGRES_URL = "postgresql://postgres:futOnc9vCcHYLp4wMR6l@remote-pishgaman.runflare.com:31589/habitodbhtr_db"


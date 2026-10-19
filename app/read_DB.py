
import psycopg

POSTGRES_URL = "postgresql://postgres:futOnc9vCcHYLp4wMR6l@remote-pishgaman.runflare.com:31589/habitodbhtr_db"

try:
    with psycopg.connect(POSTGRES_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    table_name,
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_name IN ('tasks', 'habits')
                ORDER BY table_name, ordinal_position;
            """)

            result = cur.fetchall()

            print("اتصال موفق بود!")
            print("-" * 80)

            for row in result:
                table, column, data_type, nullable, default = row

                print(f"Table: {table}")
                print(f"Column: {column}")
                print(f"Type: {data_type}")
                print(f"Nullable: {nullable}")
                print(f"Default: {default}")
                print("-" * 80)

except Exception as e:
    print(f"خطا: {e}")

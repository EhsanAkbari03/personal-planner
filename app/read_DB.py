import psycopg

POSTGRES_URL = "postgresql://postgres:futOnc9vCcHYLp4wMR6l@remote-pishgaman.runflare.com:31589/habitodbhtr_db"

email = "ehsan.akbajj@gmail.com"

try:
    with psycopg.connect(POSTGRES_URL) as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT h.*
                FROM habits h
                JOIN users u ON h.user_id = u.id
                WHERE u.email = %s
                ORDER BY h.id;
            """, (email,))

            rows = cur.fetchall()

            columns = [desc.name for desc in cur.description]

            for row in rows:
                print(dict(zip(columns, row)))

except Exception as e:
    print("Error:", e)


POSTGRES_URL = "postgresql://postgres:futOnc9vCcHYLp4wMR6l@remote-pishgaman.runflare.com:31589/habitodbhtr_db"


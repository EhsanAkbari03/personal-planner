class PasswordResetRepository:

    def __init__(self, db):
        self.db = db

    def create(
        self,
        email: str,
        code: str,
        expires_at
    ):

        with self.db.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO password_reset_codes
                (
                    email,
                    code,
                    expires_at
                )
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (
                    email,
                    code,
                    expires_at
                )
            )

            result = cursor.fetchone()

            self.db.commit()

            return result[0]
        
    def verify_code(self, email: str, code: str):
      with self.db.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, email, code, expires_at, used
            FROM password_reset_codes
            WHERE email = %s
              AND code = %s
              AND used = FALSE
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (email, code)
        )

        result = cursor.fetchone()

        if not result:
            return None

        return result
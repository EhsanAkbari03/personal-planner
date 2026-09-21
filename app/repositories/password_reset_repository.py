class PasswordResetRepository:

    def __init__(self, db):
        self.db = db

    def create(
        self,
        user_id: int,
        code: str,
        expires_at
    ):

        with self.db.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO password_reset_codes
                (
                    user_id,
                    code,
                    expires_at
                )
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (
                    user_id,
                    code,
                    expires_at
                )
            )

            result = cursor.fetchone()

            self.db.commit()

            return result[0]
from app.models.user import User


class UserRepository:

    def __init__(self, db):
        self.db = db

    def create(self, user: User) -> User:
        query = """
            INSERT INTO users (
                username,
                email,
                password_hash,
                timezone
            )
            VALUES (%s, %s, %s, %s)
            RETURNING
                id,
                username,
                email,
                password_hash,
                timezone,
                created_at,
                updated_at;
        """

        values = (
            user.username,
            user.email,
            user.password_hash,
            user.timezone
        )

        with self.db.cursor() as cursor:
            cursor.execute(query, values)
            row = cursor.fetchone()

        self.db.commit()

        return User(
            id=row[0],
            username=row[1],
            email=row[2],
            password_hash=row[3],
            timezone=row[4],
            created_at=row[5],
            updated_at=row[6]
        )

    def get_by_id(self, user_id: int) -> User | None:
        query = """
            SELECT
                id,
                username,
                email,
                password_hash,
                timezone,
                created_at,
                updated_at
            FROM users
            WHERE id = %s;
        """

        with self.db.cursor() as cursor:
            cursor.execute(query, (user_id,))
            row = cursor.fetchone()

        if row is None:
            return None

        return User(
            id=row[0],
            username=row[1],
            email=row[2],
            password_hash=row[3],
            timezone=row[4],
            created_at=row[5],
            updated_at=row[6]
        )

    def get_by_email(self, email: str) -> User | None:
        query = """
            SELECT
                id,
                username,
                email,
                password_hash,
                timezone,
                created_at,
                updated_at
            FROM users
            WHERE email = %s;
        """

        with self.db.cursor() as cursor:
            cursor.execute(query, (email,))
            row = cursor.fetchone()

        if row is None:
            return None

        return User(
            id=row[0],
            username=row[1],
            email=row[2],
            password_hash=row[3],
            timezone=row[4],
            created_at=row[5],
            updated_at=row[6]
        )

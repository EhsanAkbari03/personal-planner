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
                timezone,
                subscription_level,
                active_days_streak,
                last_login_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_DATE)
            RETURNING
                id,
                username,
                email,
                password_hash,
                timezone,
                created_at,
                updated_at,
                profile_image_uri,
                subscription_level,
                active_days_streak,
                last_login_date;
        """

        values = (
            user.username,
            user.email,
            user.password_hash,
            user.timezone,
            user.subscription_level,
            user.active_days_streak
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
            updated_at=row[6],
            profile_image_uri=row[7],
            subscription_level=row[8],
            active_days_streak=row[9],
            last_login_date=row[10]
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
                updated_at,
                profile_image_uri,
                subscription_level,
                active_days_streak,
                last_login_date
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
            updated_at=row[6],
            profile_image_uri=row[7],
            subscription_level=row[8],
            active_days_streak=row[9],
            last_login_date=row[10]
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
                updated_at,
                profile_image_uri,
                subscription_level,
                active_days_streak,
                last_login_date
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
            updated_at=row[6],
            profile_image_uri=row[7],
            subscription_level=row[8],
            active_days_streak=row[9],
            last_login_date=row[10]
        )

    def change_password(self,user_id:int,new_password: str) -> str | None:
        print(new_password)
        query="""
        UPDATE users 
            SET password_hash = %s 
            WHERE id = %s
        """

        with self.db.cursor() as cursor :
            cursor.execute(query,(new_password,user_id))

            if cursor.rowcount == 0:
             self.db.rollback()
             return False

        self.db.commit()
        return "password changed"
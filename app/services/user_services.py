from app.security.password import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.database.connection import get_db
import time


class UserService:

    def __init__(self):
        self.repository = UserRepository(get_db())

    def create_user(
        self,
        username: str | None,
        email: str | None,
        password: str,
        timezone: str = "Asia/Tehran"
    ) -> User:

        if username is not None:
            username = username.strip()

            if not username:
                username = None

        if email is not None:
            email = email.strip().lower()

            if not email:
                email = None

        if not password:
            raise ValueError("Password cannot be empty.")

        if not timezone or not timezone.strip():
            raise ValueError("Timezone cannot be empty.")

        timezone = timezone.strip()

        # Check duplicate email
        if email is not None:
            existing_user = self.repository.get_by_email(email)

            if existing_user is not None:
                raise ValueError(
                    "A user with this email already exists."
                )

        # Hash password before storing
        password_hash = hash_password(password)

        user = User(
            id=None,
            username=username,
            email=email,
            password_hash=password_hash,
            timezone=timezone,
            created_at=None,
            updated_at=None
        )

        return self.repository.create(user)





    def login(self, email: str, password: str):
        t0 = time.time()
        
        if not email or not email.strip():
            raise ValueError("Email cannot be empty.")
        if not password:
            raise ValueError("Password cannot be empty.")

        email = email.strip().lower()

        # ۱. زمان استعلام از دیتابیس
        t1 = time.time()
        user = self.repository.get_by_email(email)
        print(f"📊 Database Lookup Time: {time.time() - t1:.4f} sec")

        if user is None:
            return None

        # ۲. زمان بررسی هش رمز عبور
        t2 = time.time()
        is_valid = verify_password(password, user.password_hash)
        print(f"🔑 Password Verification Time: {time.time() - t2:.4f} sec")

        if not is_valid:
            return None

        print(f"✅ Total Login Time: {time.time() - t0:.4f} sec")
        return user


    # def login(
    #     self,
    #     email: str,
    #     password: str
    # ) -> User | None:

    #     if not email or not email.strip():
    #         raise ValueError("Email cannot be empty.")

    #     if not password:
    #         raise ValueError("Password cannot be empty.")

    #     email = email.strip().lower()

    #     # Get user through repository instance
    #     user = self.repository.get_by_email(email)

    #     if user is None:
    #         return None

    #     # Verify plain password against stored hash
    #     if not verify_password(password, user.password_hash):
    #         return None

    #     return user




    



    def get_user(self, user_id: int) -> User | None:

        if user_id <= 0:
            raise ValueError("Invalid user_id.")

        return self.repository.get_by_id(user_id)
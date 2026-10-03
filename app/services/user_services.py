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

        if email is not None:
            existing_user = self.repository.get_by_email(email)
            if existing_user is not None:
                raise ValueError("A user with this email already exists.")

        password_hash = hash_password(password)

        user = User(
            id=None,
            username=username,
            email=email,
            password_hash=password_hash,
            timezone=timezone,
            created_at=None,
            updated_at=None,
            profile_image_uri=None,
            subscription_level="عادی",
            active_days_streak=1,
            last_login_date=None
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

        # 🌟 ۳. آپدیت کردن last_login_date و active_days_streak در دیتابیس و کامیت کردن آن
        try:
            with self.repository.db.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE users 
                    SET last_login_date = CURRENT_DATE,
                        active_days_streak = CASE 
                            WHEN last_login_date = CURRENT_DATE - 1 THEN active_days_streak + 1
                            WHEN last_login_date = CURRENT_DATE THEN active_days_streak
                            ELSE 1 
                        END
                    WHERE id = %s;
                    """,
                    (user.id,)
                )
            # حتماً باید تغییرات در دیتابیس ثبت (commit) شوند
            self.repository.db.commit()
        except Exception as e:
            self.repository.db.rollback()
            print(f"❌ Error updating login date: {e}")

        # دریافت اطلاعات بروزرسانی شده کاربر
        updated_user = self.repository.get_by_id(user.id)

        print(f"✅ Total Login Time: {time.time() - t0:.4f} sec")
        return updated_user

        
    def get_user(self, user_id: int) -> User | None:
        if user_id <= 0:
            raise ValueError("Invalid user_id.")
        return self.repository.get_by_id(user_id)

    
    def change_password(self,user_id:int,old_password: str,new_password: str):
        if not old_password :
            raise ValueError("Old password can not be empty.")
        if not new_password:
            raise ValueError("New password can not be empty.")

        user = self.repository.get_by_id(user_id=user_id)

        if not user :
            raise ValueError("User not found")

        is_valid = verify_password(old_password, user.password_hash)

        if not is_valid:
            raise ValueError("Old password is not correct")

        hashed_new_password = hash_password(new_password)

        return self.repository.change_password(user_id, hashed_new_password)
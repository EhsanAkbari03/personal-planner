from datetime import datetime, timedelta
from random import randint
from app.repositories.password_reset_repository import PasswordResetRepository
from app.services.email_services import send_reset_code
from passlib.context import CryptContext

# تنظیمات برای هش کردن رمز عبور جدید
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PasswordResetService:

    def __init__(self, db):
        self.db = db
        self.repository = PasswordResetRepository(db)

    def send_code(self, email: str):
        code = str(randint(100000, 999999))
        expires_at = datetime.now() + timedelta(minutes=10)

        self.repository.create(
            email=email,
            code=code,
            expires_at=expires_at
        )

        # ارسال ایمیل واقعی به کاربر
        send_reset_code(email=email, code=code)

        return {
            "success": True,
            "message": "کد تایید به ایمیل شما ارسال شد."
        }

    def verify_code(self, email: str, code: str):
        result = self.repository.verify_code(
            email=email,
            code=code
        )

        if not result:
            raise ValueError("کد وارد شده اشتباه است یا قبلاً استفاده شده است.")

        expires_at = result[3]

        if datetime.now() > expires_at:
            raise ValueError("کد منقضی شده است.")

        return {
            "success": True,
            "message": "کد صحیح است.",
            "reset_token": email  # 🌟 اندروید این ایمیل را به عنوان توکن ذخیره می‌کند
        }

    def reset_password(self, reset_token: str, new_password: str):
        email = reset_token 
        hashed_password = pwd_context.hash(new_password)
        
        with self.db.cursor() as cursor:
            # 🌟 آپدیت رمز عبور در دیتابیس (مطمئن شوید اسم ستون در دیتابیس شما hashed_password است)
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE email = %s",
                (hashed_password, email)
            )
            
            # 🌟 ابطال کدهای قبلی این ایمیل برای امنیت بیشتر
            cursor.execute(
                "UPDATE password_reset_codes SET used = TRUE WHERE email = %s",
                (email,)
            )
            
        self.db.commit()
        
        return {
            "success": True,
            "message": "رمز عبور با موفقیت تغییر کرد."
        }
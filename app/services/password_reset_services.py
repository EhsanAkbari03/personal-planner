from datetime import datetime, timedelta
from random import randint

from app.repositories.password_reset_repository import (
    PasswordResetRepository
)
from app.services.email_services import send_reset_code


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

        send_reset_code(
            email=email,
            code=code
        )

        return {
            "success": True,
            "message": "Reset code sent."
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
        "message": "کد صحیح است."
    }
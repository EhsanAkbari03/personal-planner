import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# 🌟 این خط برای خواندن فایل .env الزامی است
load_dotenv()

def send_reset_code(email: str, code: str):
    sender = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    # 🌟 اعتبارسنجی برای جلوگیری از ارورهای مبهم
    if not sender or not password:
        raise ValueError("ایمیل یا رمز عبور در فایل .env تنظیم نشده است!")

    message = EmailMessage()
    message["Subject"] = "کد بازیابی رمز عبور - Habito"
    message["From"] = sender
    message["To"] = email

    message.set_content(
        f"""
سلام،

کد بازیابی رمز عبور شما در اپلیکیشن هابیتو:

{code}

این کد تا ۱۰ دقیقه اعتبار دارد.
"""
    )

    # اتصال مستقیم و امن با SSL به گوگل
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(message)
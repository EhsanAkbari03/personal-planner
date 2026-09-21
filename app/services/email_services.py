import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


def send_reset_code(email: str, code: str):

    sender = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    message = EmailMessage()

    message["Subject"] = "Password Reset Code"
    message["From"] = sender
    message["To"] = email

    message.set_content(
        f"""
Your password reset code is:

{code}

This code is valid for 10 minutes.
"""
    )

    with smtplib.SMTP("smtp.gmail.com", 587) as server:

        server.starttls()

        server.login(sender, password)

        server.send_message(message)
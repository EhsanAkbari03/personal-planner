import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.tools.reminder import create_reminder


# =========================
# Load environment variables
# =========================

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError(
        "GOOGLE_API_KEY پیدا نشد. "
        "مقدار آن را در فایل .env قرار بده."
    )


# =========================
# Gemini Client
# =========================

client = genai.Client(
    api_key=api_key
)


# =========================
# Chat with Gemini
# =========================

def chat_with_llm(user_message: str):

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=user_message,

        config=types.GenerateContentConfig(

            system_instruction="""
تو یک دستیار برنامه‌ریزی شخصی هستی.

وظایف تو:

1. اگر کاربر درخواست ایجاد یک یادآوری کرد،
   از تابع create_reminder استفاده کن.

2. اگر کاربر درخواست ایجاد یادآوری نکرد،
   create_reminder را صدا نزن.

مثال:

کاربر:
فردا ساعت ۳ جلسه دارم، یادم بنداز.

در این حالت باید create_reminder را صدا بزنی.
""",

            tools=[create_reminder]
        )
    )

    return response
import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY is not set in .env")


client = genai.Client(api_key=api_key)


def ask_gemini(user_message: str) -> str:
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=user_message
    )

    return response.text
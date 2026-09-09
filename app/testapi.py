import os

from dotenv import load_dotenv
from google import genai


# Load .env
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found")


print("API key found.")
print("Creating Gemini client...")

client = genai.Client(
    api_key=api_key
)

print("Sending request to Gemini...")

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="سلام، فقط یک کلمه جواب بده: سلام"
)

print("Response received!")
print(response.text)


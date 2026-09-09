
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.tools.reminder import create_reminder
from app.tools.task import create_task, delete_task, get_today_tasks


# ==================================================
# Environment
# ==================================================

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError(
        "GOOGLE_API_KEY not found in .env"
    )


# ==================================================
# Gemini Client
# ==================================================

client = genai.Client(
    api_key=api_key
)


# ==================================================
# System Instruction
# ==================================================

SYSTEM_INSTRUCTION = """
You are a personal planning assistant.

Language Policy:
- Always communicate with the user in Persian (Farsi).

Tools:

1. create_reminder
Use this tool when the user explicitly asks to create
or set a reminder.

2. create_task
Use this tool when the user asks to create, add,
schedule, or plan a task.

3. delete_task
Use this tool when the user explicitly asks to delete
or remove a task.

Rules:

- Do not call tools unless the user's intent clearly
  requires it.
- Never invent or guess a task_id.
- Use the exact parameters required by each tool.
- Date and time parameters must be ISO 8601.
- After a tool is executed, explain the result to the
  user naturally in Persian.
"""


# ==================================================
# Chat Function
# ==================================================

def chat_with_llm(user_message: str, user_id: int):

    print(f"Sending request to Gemini for user_id={user_id}...")

    # --------------------------------------------------
    # Wrapper Functions (Injecting user_id securely)
    # --------------------------------------------------

    def create_task_wrapper(
        title: str,
        start_at: str,
        description: str | None = None,
        end_at: str | None = None,
        priority: int = 1
    ) -> dict:
        """Create, add, schedule, or plan a new task."""
        return create_task(
            title=title,
            user_id=user_id,
            start_at=start_at,
            description=description,
            end_at=end_at,
            priority=priority,
        )

    def delete_task_wrapper(task_id: int) -> dict:
        """Delete or remove an existing task by its ID."""
        return delete_task(
            task_id=task_id,
            user_id=user_id
        )

    def get_today_tasks_for_user() -> dict:
        return get_today_tasks(user_id=user_id)

    # --------------------------------------------------
    # Create Request-Scoped Chat Session
    # --------------------------------------------------

    chat = client.chats.create(
        model="gemini-3.5-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[
                create_reminder,
                create_task_wrapper,
                delete_task_wrapper,
                get_today_tasks_for_user
            ]
        )
    )

    # --------------------------------------------------
    # Send Message
    # --------------------------------------------------

    response = chat.send_message(user_message)

    print("Gemini response received!")

    return response
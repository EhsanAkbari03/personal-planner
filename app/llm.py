import os
from datetime import datetime

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.tools.reminder import create_reminder
from app.tools.task import create_task, delete_task, get_tasks_by_date

# ==================================================
# Environment
# ==================================================
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env")

# ==================================================
# Gemini Client
# ==================================================
client = genai.Client(api_key=api_key)

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
        print(f"🚀 [TOOL CALLED] create_task: {title} at {start_at}")
        
        try:
            # 🌟 پاس دادنِ مستقیم رشته‌های متنی به تابع قدرتمندِ خودتان
            create_task(
                title=title,
                user_id=user_id,
                start_at=start_at,
                description=description,
                end_at=end_at,
                priority=priority,
            )
            
            print("✅ ذخیره در دیتابیس با موفقیت انجام شد!")
            return {"status": "success", "message": "Task saved"}
            
        except Exception as e:
            print(f"❌ خطای مخفی پیدا شد: {e}")
            return {"status": "error", "message": str(e)}

            
    def delete_task_wrapper(task_id: int) -> dict:
        """Delete or remove an existing task by its ID."""
        print(f"🗑️ [TOOL CALLED] delete_task: ID {task_id}")
        success = delete_task(
            task_id=task_id,
            user_id=user_id
        )
        return {"status": "success" if success else "failed"}

    def get_today_tasks_for_user() -> dict:
        print("📅 [TOOL CALLED] get_tasks_by_date")
        tasks = get_tasks_by_date(user_id=user_id)
        return {"tasks": [{"id": t.id, "title": t.title, "start": str(t.start_at)} for t in tasks]}

    # --------------------------------------------------
    # Dynamic System Instruction
    # --------------------------------------------------
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    SYSTEM_INSTRUCTION = f"""
    You are a personal planning assistant.

    Language Policy:
    - Always communicate with the user in Persian (Farsi).

    Current System Time: {current_time}
    Use this exact time to calculate 'today', 'tomorrow', or any relative dates.

    CRITICAL RULES FOR TOOLS:
    - You MUST explicitly call the tools (e.g., create_task_wrapper) to save, delete, or fetch tasks.
    - NEVER claim you saved a task without actually calling the tool first.
    - Date and time parameters must be strictly ISO 8601 format based on the Current System Time.
    - After a tool returns success, then you can confidently tell the user the task was added.
    """

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
            ],
            temperature=0.1, # 🌟 کاهش شدید توهم و افزایش دقت لاجیک
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False) # 🌟 اجرای خودکار ابزارها توسط SDK
        )
    )

    # --------------------------------------------------
    # Send Message
    # --------------------------------------------------
    response = chat.send_message(user_message)

    print("Gemini final response received!")

    return response
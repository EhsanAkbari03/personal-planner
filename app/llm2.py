from turtle import title
from app.database.connection import get_db
from zoneinfo import ZoneInfo
from datetime import datetime

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_core.tools import tool

from app.tools.reminder import create_reminder
from app.tools.task import (
    create_task,
    get_tasks_by_date,
    delete_task,
    find_tasks_by_title,
)

from app.tools.habit import create_habit

# ============================================================
# انتخاب مدل
# ============================================================

#MODEL = "qwen"
#MODEL = "gemini"
#MODEL = "lamma"
MODEL = "groq"

# ============================================================
# System Prompt
# ============================================================

def get_system_instruction():

    # --------------------------------------------------------
    # Current date and time - Tehran
    # --------------------------------------------------------

    tehran_now = datetime.now(ZoneInfo("Asia/Tehran"))

    current_date = tehran_now.strftime("%Y-%m-%d")
    current_time = tehran_now.strftime("%H:%M")

    # --------------------------------------------------------
    # System Prompt
    # --------------------------------------------------------

    system_instruction = f"""
You are a personal planning assistant.
Your name is Habito "هابیتو".

Always communicate with the user in Persian (Farsi).

============================================================
CURRENT DATE AND TIME
============================================================

Today: {current_date}
Current time: {current_time}
Timezone: Asia/Tehran

IMPORTANT:
When the user asks for the current date or current time,
use ONLY the date and time provided above.

Current datetime:
{current_date} {current_time}

============================================================
DATE RULES
============================================================

- "امروز" = Today
- "فردا" = Tomorrow
- "دیروز" = Yesterday
- "پسفردا" = Day after tomorrow

Always interpret relative dates based on the current
Tehran date provided above.

============================================================
TOOLS
============================================================

1. create_task

Use this tool when the user wants to:
- create a task
- add a task
- schedule a task
- plan a task

Do NOT use create_task for recurring habits.


2. create_reminder

Use this tool ONLY when the user explicitly asks
for a reminder.


3. find_tasks_by_title

Use this tool when you need to find an existing task
by its title or name.


4. delete_task

Use this tool to delete an existing task.

If the user wants to delete a task by name/title:

1. First call find_tasks_by_title.
2. If exactly one task is found:
   - use its ID
   - then call delete_task
3. If multiple tasks are found:
   - ask the user which task they mean.
4. If no task is found:
   - tell the user that the task was not found.

Never guess task_id.


5. create_habit

Use this tool when the user wants to create:
- a recurring habit
- a routine
- a repeated activity

Examples:

- "من روزهای زوج میرم باشگاه"
- "هر روز صبح ورزش میکنم"
- "هر دوشنبه و چهارشنبه شنا دارم"
- "هر ماه روز 26 ام دکتر دارم"

Do NOT use create_task for recurring habits.


============================================================
HABIT RULES
============================================================

For weekly habits:

- frequency_type = "weekly"
- use weekdays


For monthly habits:

- frequency_type = "monthly"
- use day_of_month


For daily habits:

- frequency_type = "daily"


============================================================
USER ID
============================================================

Never ask the user for user_id.

user_id is handled internally by the backend.


============================================================
INTERNAL IDs
============================================================

Never reveal internal IDs to the user.

This includes:

- task_id
- user_id
- habit_id
- database IDs

Only reveal an internal ID if the user explicitly asks
for that ID.


============================================================
TOOL RESPONSE
============================================================

After using a tool, explain the result naturally
in Persian.

Do not expose internal implementation details.

Do not expose raw tool responses unless necessary.

============================================================
GENERAL BEHAVIOR
============================================================

- Always answer in Persian.
- Be concise and natural.
- Do not invent tasks, reminders, habits, dates, or IDs.
- If information is missing and cannot be determined safely,
  ask the user for clarification.
- Never guess an internal ID.
"""

    return system_instruction


# ============================================================
# انتخاب LLM
# ============================================================

if MODEL == "qwen":

    llm = ChatOllama(
        model="qwen2.5:3b",
        temperature=0,
    )

elif MODEL == "gemini":

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature=0,
    )

elif MODEL == "lamma":

    llm = ChatOllama(
        model="llama3.1",
        temperature=0,
    )

elif MODEL == "groq":

    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
    )

else:
    raise ValueError(
        "MODEL must be something"
    )


# ============================================================
# Chat
# ============================================================

def chat_with_llm(user_message: str, user_id: int):

    # 🌟 سیستم بررسی تداخل زمان‌بندی برای تسک‌ها
    def check_conflict_for_task(start_at_str: str) -> str | None:
        try:
            db = get_db()
            with db.cursor() as cursor:
                cursor.execute("SELECT title FROM tasks WHERE user_id=%s AND start_at=%s", (user_id, start_at_str))
                row = cursor.fetchone()
                if row:
                    return f"CONFLICT_ERROR: امکان ثبت وجود ندارد. شما در این ساعت برنامه '{row[0]}' را از قبل رزرو کرده‌اید."

                dt = datetime.fromisoformat(start_at_str)
                habit_day = (dt.weekday() + 2) % 7 
                hour_str = f"{dt.hour:02d}"

                cursor.execute("SELECT title FROM habits WHERE user_id=%s AND checkin_time LIKE %s AND %s = ANY(weekdays)", (user_id, f"{hour_str}%", habit_day))
                row2 = cursor.fetchone()
                if row2:
                    return f"CONFLICT_ERROR: امکان ثبت وجود ندارد. شما در این زمان عادت روتین '{row2[0]}' را دارید."
            return None
        except Exception:
            return None

    # 🌟 سیستم بررسی تداخل زمان‌بندی برای عادت‌ها
    def check_conflict_for_habit(checkin_time_str: str, weekdays_list: list) -> str | None:
        if not checkin_time_str or not weekdays_list:
            return None
        try:
            db = get_db()
            hour_str = checkin_time_str.split(':')[0].zfill(2)
            with db.cursor() as cursor:
                for day in weekdays_list:
                    cursor.execute("SELECT title FROM habits WHERE user_id=%s AND checkin_time LIKE %s AND %s = ANY(weekdays)", (user_id, f"{hour_str}%", day))
                    row = cursor.fetchone()
                    if row:
                        return f"امکان ثبت نیست. عادت '{row[0]}' با این زمان تداخل دارد."
            return None
        except Exception:
            return None

    # ========================================================
    # WRAPPERS WITH @tool
    # ========================================================

    @tool("create_task")
    def create_task_wrapper(
        title: str,
        start_at: str,
        description: str | None = None,
        end_at: str | None = None,
        priority: int = 1,
    ) -> dict:
        """
            Create a new task or planned activity in the user's personal planner.

             Use this tool when the user intends to add, create, save, register,
              schedule, or plan an activity, event, appointment, or task.
        """
        # 🌟 بررسی تداخل قبل از ثبت تسک
        conflict = check_conflict_for_task(start_at)
        if conflict:
            return {"success": False, "error": conflict}

        return create_task(
            title=title,
            description=description,
            start_at=start_at,
            end_at=end_at,
            priority=priority,
            user_id=user_id,
        )

    @tool("create_reminder")
    def create_reminder_wrapper(
        title: str,
        remind_at: str,
    ) -> dict:
        """Create a reminder for the current user."""
        return create_reminder(
            title=title,
            remind_at=remind_at,
            user_id=user_id,
        )

    @tool("find_tasks_by_title")
    def find_tasks_by_title_wrapper(title: str) -> dict:
        """Find, search, or retrieve tasks/classes by their title, name, or keyword."""
        return find_tasks_by_title(
            title=title,
            user_id=user_id,
        )

    @tool("delete_task")
    def delete_task_wrapper(task_id: int) -> dict:
        """Delete a task belonging to the current user by its ID."""
        return delete_task(
            task_id=task_id,
            user_id=user_id,
        )

    @tool("get_tasks_by_date")
    def get_tasks_by_date_wrapper(date: str) -> dict | list:
        """Get all tasks scheduled for a specific date."""
        return get_tasks_by_date(
            date=date,
            user_id=user_id
        )
    
    @tool("create_habit")
    def create_habit_wrapper(
        title: str,
        frequency_type: str,
        description: str | None = None,
        weekdays: list[int] | None = None,
        day_of_month: int | None = None,
        month_of_year: int | None = None,
        reminder_time: str | None = None,
        checkin_time: str | None = None,
        points: int = 10,
    ) -> dict:
        """Create a recurring habit for the current user."""
        
        # 🌟 بررسی تداخل قبل از ثبت عادت
        conflict = check_conflict_for_habit(checkin_time, weekdays)
        if conflict:
            return {"success": False, "error": conflict}

        return create_habit(
            title=title,
            description=description,
            frequency_type=frequency_type,
            weekdays=weekdays,
            day_of_month=day_of_month,
            month_of_year=month_of_year,
            reminder_time=reminder_time,
            checkin_time=checkin_time,
            points=points,
            user_id=user_id,
        )

    # ========================================================
    # TOOLS LIST & MAP
    # ========================================================

    tools = [
        create_task_wrapper,
        create_reminder_wrapper,
        find_tasks_by_title_wrapper,
        delete_task_wrapper,
        get_tasks_by_date_wrapper,
        create_habit_wrapper,
    ]

    tool_map = {
        "create_task": create_task_wrapper,
        "create_reminder": create_reminder_wrapper,
        "find_tasks_by_title": find_tasks_by_title_wrapper,
        "delete_task": delete_task_wrapper,
        "get_tasks_by_date": get_tasks_by_date_wrapper,
        "create_habit": create_habit_wrapper,
    }

    # ========================================================
    # LLM SETUP
    # ========================================================

    llm_with_tools = llm.bind_tools(tools)

    messages = [
        SystemMessage(content=get_system_instruction()),
        HumanMessage(content=user_message),
    ]

    # ========================================================
    # LLM LOOP
    # ========================================================

    while True:

        response = llm_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            if isinstance(response.content, list):
                return " ".join([
                    block.get("text", "") 
                    for block in response.content 
                    if isinstance(block, dict) and "text" in block
                ])
            return response.content

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]

            print(f"\n🛠️ [هوش مصنوعی] تصمیم گرفت ابزار زیر را اجرا کند:")
            print(f"🔸 نام ابزار: {tool_name}")
            print(f"🔸 اطلاعات ارسالی به دیتابیس: {tool_args}")

            selected_tool = tool_map.get(tool_name)

            if selected_tool is None:
                error_msg = f"Unknown tool: {tool_name}"
                print(f"❌ [خطا] ابزار پیدا نشد: {error_msg}")
                result = {
                    "success": False,
                    "error": error_msg,
                }
            else:
                try:
                    result = selected_tool.invoke(tool_args)
                    print(f"✅ [موفقیت] نتیجه ثبت در دیتابیس: {result}\n")
                except Exception as e:
                    print(f"❌ [خطای داخلی در اجرای ابزار {tool_name}]: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    print("\n")
                    
                    result = {
                        "success": False,
                        "error": str(e),
                    }

            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call_id,
                )
            )
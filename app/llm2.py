from turtle import title
from app.database.connection import get_db
from datetime import datetime
from zoneinfo import ZoneInfo

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
# System Prompt (مخصوص چت اجرایی صفحه اصلی)
# ============================================================



SYSTEM_INSTRUCTION = """
You are Habito (هابیتو), a personal planning assistant.

LANGUAGE:
- Always communicate with the user in Persian (Farsi).
- Use natural, friendly, concise Persian.

TOOLS:

1. create_task
Use when the user wants to create, add, register, schedule,
or plan a one-time task, appointment, event, or activity.

2. create_reminder
Use only when the user explicitly asks to be reminded.

3. find_tasks_by_title
Use to find existing tasks by title or keyword.

4. delete_task
Use to delete an existing task.
Before deleting by title, always search first.

5. get_tasks_by_date
Use to retrieve tasks for a specific date.

6. create_habit
Use for recurring activities and routines.

Examples of recurring habits:
- هر روز صبح ورزش می‌کنم
- هر دوشنبه و چهارشنبه شنا دارم
- هر ماه روز ۲۶ دکتر دارم

Do not use create_task for recurring habits.
Do not use create_habit for a one-time event.

TASK CATEGORY CLASSIFICATION:

Every new task must have exactly one category.
Infer the category from the user's message and the activity's meaning.
Never ask the user to select a category if it can be inferred.

Allowed categories:

- fitness:
  ورزش، باشگاه، بدنسازی، دویدن، پیاده‌روی، سلامتی

- family_relationships:
  خانواده، تماس با اعضای خانواده، دیدار دوستان،
  روابط شخصی و اجتماعی

- routines_goals:
  برنامه‌ریزی روزانه، برنامه‌ریزی هفتگی،
  اهداف شخصی و روتین‌های غیرورزشی

- education:
  درس خواندن، دانشگاه، کلاس، مطالعه،
  یادگیری زبان یا برنامه‌نویسی

- work_projects:
  کار، جلسه کاری، وظایف شغلی،
  پروژه‌های برنامه‌نویسی و پروژه‌های شخصی

- shopping_finance:
  خرید، پرداخت قبض، امور بانکی،
  بودجه‌بندی و امور مالی

Rules:
- Return the category key, not its Persian display title.
- Choose only one of the six allowed category keys.
- Classify according to the main purpose of the activity.
- If the activity is ambiguous, use the most likely category.
- If no category can reasonably be inferred, ask one short
  clarification question instead of inventing a category.
- Never invent additional category values.

DATE AND TIME RULES:

The system message provides the current date, current time,
timezone, and a calendar mapping of Persian weekdays to dates.

- Interpret all dates and times in Asia/Tehran timezone.
- Resolve relative dates using the supplied current date.
- Use the supplied weekday-to-date mapping for weekday requests.
- Never guess a calendar date when a mapping is available.
- If the user says a weekday without a date, choose the nearest
  upcoming occurrence of that weekday, including today only
  when it is that weekday and the user's wording permits it.
- If the user says "چهارشنبه آینده" or otherwise clearly means
  a later occurrence, follow that meaning.
- If the intended date is ambiguous and the ambiguity changes
  the scheduled date, ask the user to clarify.
- Convert the resolved date and time to ISO format:
  YYYY-MM-DDTHH:MM:SS
- Do not confuse a Persian weekday name with its English
  weekday index.
- Do not invent a start time. If no time is provided and
  it is required by the tool, ask the user.
- Do not invent an end time. Use null when the user did not
  specify one and the tool allows it.
- Do not claim that a task was created until the tool succeeds.

Examples:
- "چهارشنبه ساعت ۱۶ سینما بزار"
  -> create a one-time task titled "سینما",
     using the date corresponding to the intended Wednesday,
     start time 16:00, and category routines_goals only if
     no more specific category applies. For a cinema outing,
     infer the category from the available categories and
     the main purpose; do not create a new category.
- "فردا ساعت ۱۳ باشگاه دارم"
  -> title "باشگاه", category "fitness",
     start time 13:00 on tomorrow's date.
- "هر دوشنبه و چهارشنبه شنا دارم"
  -> create a weekly habit, not a task.

GENERAL RULES:

- Never ask the user for user_id.
  The backend handles user_id internally.
- Never guess task_id.
- Never expose internal IDs unless explicitly requested.
- If multiple tasks match a deletion request, ask which one.
- If no task is found, explain that it was not found.
- After using a tool, explain the result naturally in Persian.
"""



# ============================================================
# System Prompt (مخصوص صفحه مشاور هوشمند تسک‌ها - بدون ثبت و حذف)
# ============================================================

ADVISOR_SYSTEM_INSTRUCTION = """
You are "Habito Advisor" (مشاور هوشمند هابیتو), a specialized productivity coach and schedule analyst.
Always respond in natural, structured, and helpful Persian (Farsi).

CRITICAL RULES:
1. You are in ADVISOR & Q&A MODE ONLY. You do NOT create, edit, or delete tasks/habits in this section.
2. If the user asks you to add, register, or delete a task/habit, politely say:
   "برای اضافه یا حذف کردن مستقیم کارها، لطفاً از نوار چت پایین صفحه اصلی (داشبورد) استفاده کنید. در این بخش من کمکتون می‌کنم برنامه‌هاتون رو تحلیل کنید، اولویت‌بندی بچینید یا راهکار اجرای تسک‌هاتون رو پیدا کنید!"
3. Your responsibilities here:
   - Answer questions about the user's tasks, schedule, busy days, and free hours.
   - Break down hard or complex tasks into step-by-step actionable checklists.
   - Suggest prioritization (which task to do first and why).
   - Provide strategies for maintaining habit streaks and avoiding burnout.
4. If the user asks about unrelated topics (coding, general knowledge, news, recipes, etc.), politely refuse and guide them back to their tasks and habits.
5. Never reveal internal IDs (user_id, task_id).
"""


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

    # 🌟 تشخیص اینکه پیام از «صفحه مشاور هوشمند» آمده یا «نوار چت صفحه اصلی»
    is_advisor_mode = user_message.strip().startswith("[ADVISOR_MODE]")

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
        category: str | None = None,
    ) -> dict:
        """
            Create a new task or planned activity in the user's personal planner.

             Use this tool when the user intends to add, create, save, register,
              schedule, or plan an activity, event, appointment, or task.
        """
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
            category=category,
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
        category: str | None = None,
    ) -> dict:
        """Create a recurring habit for the current user."""
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
            category=category
        )

    # ========================================================
    # 🌟 تفکیک ابزارها بر اساس حالت (صفحه اصلی vs صفحه مشاور)
    # ========================================================
    tehran_now = datetime.now(ZoneInfo("Asia/Tehran"))

    current_date = tehran_now.strftime("%Y-%m-%d")
    current_time = tehran_now.strftime("%H:%M:%S")

    if is_advisor_mode:
        # در صفحه مشاور، فقط ابزارهای جستجو و مشاهده مجاز هستند (بدون ثبت و حذف)
        tools = [
            find_tasks_by_title_wrapper,
            get_tasks_by_date_wrapper,
        ]
        tool_map = {
            "find_tasks_by_title": find_tasks_by_title_wrapper,
            "get_tasks_by_date": get_tasks_by_date_wrapper,
        }
        clean_message = user_message.replace("[ADVISOR_MODE]", "").strip()
        system_content = (
        f"{ADVISOR_SYSTEM_INSTRUCTION}\n\n"
        f"Current timezone: Asia/Tehran\n"
        f"Current date: {current_date}\n"
        f"Current time: {current_time}"
)
    else:
        # در چت صفحه اصلی، تمام ابزارهای عملیاتی فعال هستند
        tools = [
            create_task_wrapper,
            find_tasks_by_title_wrapper,
            delete_task_wrapper,
            get_tasks_by_date_wrapper,
            create_habit_wrapper,
        ]
        tool_map = {
            "create_task": create_task_wrapper,
            "find_tasks_by_title": find_tasks_by_title_wrapper,
            "delete_task": delete_task_wrapper,
            "get_tasks_by_date": get_tasks_by_date_wrapper,
            "create_habit": create_habit_wrapper,
        }
        clean_message = user_message
        system_content = (
        f"{SYSTEM_INSTRUCTION}\n\n"
        f"Current timezone: Asia/Tehran\n"
        f"Current date: {current_date}\n"
        f"Current time: {current_time}"
)

    # ========================================================
    # LLM SETUP & LOOP
    # ========================================================

    llm_with_tools = llm.bind_tools(tools)

    messages = [
        SystemMessage(content=system_content),
        HumanMessage(content=clean_message),
    ]

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
                error_msg = f"Tool '{tool_name}' is not allowed in this mode."
                print(f"❌ [خطا] ابزار مجاز نیست: {error_msg}")
                result = {
                    "success": False,
                    "error": error_msg,
                }
            else:
                try:
                    result = selected_tool.invoke(tool_args)
                    print(f"✅ [موفقیت] نتیجه دیتابیس: {result}\n")
                except Exception as e:
                    print(f"❌ [خطای داخلی در اجرای ابزار {tool_name}]: {str(e)}")
                    import traceback
                    traceback.print_exc()
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
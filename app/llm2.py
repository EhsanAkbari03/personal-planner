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

SYSTEM_INSTRUCTION = """
You are a personal planning assistant.

Always communicate with the user in Persian (Farsi).

Tools:

1. create_task
Use this tool when the user wants to create, add,
schedule, or plan a task.

2. create_reminder
Use this tool when the user explicitly asks for a reminder.

3. find_tasks_by_title
Use this tool when you need to find an existing task
by its title.

4. delete_task
Use this tool to delete an existing task.

Important rules:

- Never guess task_id.
- If the user wants to delete a task by name/title,
  first use find_tasks_by_title.
- If exactly one task is found, use its ID and then
  call delete_task.
- If multiple tasks are found, ask the user which one
  they mean.
- If no task is found, tell the user that the task
  was not found.
- Never ask the user for user_id.
- user_id is handled internally by the backend.

After using a tool, explain the result naturally
in Persian.
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

    # ارسال API Key مستقیم یا خواندن خودکار از os.environ["GROQ_API_KEY"]
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
        """Create, add, schedule, or plan a new task."""
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
        """
        Find, search, or retrieve tasks/classes by their title, name, or keyword.
    Use this function when the user asks to find, get, or show a specific task, class, or event.
    Examples of user intent: 'کلاس فیزیک را برگردان', 'جستجوی جلسه', 'نمایش تسک فیزیک'

        Args:
        title: The exact name, title or keyword of the task (e.g., 'تنیس').
        """
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
        """
        Get all tasks scheduled for a specific date.
    
        This tool should be used when the user asks:
        - What do I have today?
        - What are my tasks tomorrow?
        - Show 10/3's schedule.
        - What is my plan for Saturday?
        -What tasks do I have on 2026-09-12

        Args:
        date (str): The target date in 'YYYY-MM-DD' format (e.g., '2026-09-12').Its required parameter.

        """
        
        print(f"[DEBUG LLM OUTPUT] Raw Value: {repr(date)} | Type: {type(date)}")
        return get_tasks_by_date(
            date=date,
            user_id=user_id
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
    ]

    tool_map = {
        "create_task": create_task_wrapper,
        "create_reminder": create_reminder_wrapper,
        "find_tasks_by_title": find_tasks_by_title_wrapper,
        "delete_task": delete_task_wrapper,
        "get_tasks_by_date": get_tasks_by_date_wrapper,
    }

    # ========================================================
    # LLM SETUP
    # ========================================================

    llm_with_tools = llm.bind_tools(tools)

    messages = [
        SystemMessage(content=SYSTEM_INSTRUCTION),
        HumanMessage(content=user_message),
    ]

    # ========================================================
    # LLM LOOP
    # ========================================================

    while True:

        response = llm_with_tools.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            return response.content

        for tool_call in response.tool_calls:

            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]

            # تغییر نام متغیر از tool به selected_tool جهت جلوگیری از UnboundLocalError
            selected_tool = tool_map.get(tool_name)

            if selected_tool is None:
                result = {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}",
                }
            else:
                try:
                    result = selected_tool.invoke(tool_args)
                except Exception as e:
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
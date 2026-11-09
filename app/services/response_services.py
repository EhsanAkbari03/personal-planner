from app.schemas.chat_response import ChatResponse


def success_response(response_type, message, data=None):
    return ChatResponse(
        success=True,
        type=response_type,
        message=message,
        data=data,
        error=None
    )


def error_response(message, error_code, details=None):
    return ChatResponse(
        success=False,
        type="error",
        message=message,
        data=None,
        error={
            "code": error_code,
            "details": details
        }
    )


def build_chat_response(message: str, tool_results: list):
    if not tool_results:
        return success_response(
            response_type="text",
            message=message
        )

    data = {}
    tool_names = set()

    # تبدیل نتایج ابزارها به ساختار مشخص
    tool_keys = {
        "get_tasks_by_date": "tasks",
        "get_tasks_by_range": "tasks",
        "find_tasks_by_title": "tasks",
        "get_habits_by_date": "habits",
        "get_free_slots": "free_slots",
        "get_user_preferences": "preferences",
        "create_task": "task",
        "create_habit": "habit",
        "delete_task": "task",
        "update_user_preferences": "preferences"
    }

    for item in tool_results:
        tool_name = item["tool"]
        result = item["result"]

        tool_names.add(tool_name)

        key = tool_keys.get(tool_name)

        if key:
            if key in data:
                if not isinstance(data[key], list):
                    data[key] = [data[key]]

                data[key].append(result)
            else:
                data[key] = result

    # تشخیص نوع پاسخ
    if "get_tasks_by_date" in tool_names and "get_habits_by_date" in tool_names:
        response_type = "daily_agenda"

    elif "get_free_slots" in tool_names:
        response_type = "free_slots"

    elif "get_tasks_by_date" in tool_names or "get_tasks_by_range" in tool_names:
        response_type = "task_list"

    elif "get_habits_by_date" in tool_names:
        response_type = "habit_list"

    elif "create_task" in tool_names:
        response_type = "task_created"

    elif "create_habit" in tool_names:
        response_type = "habit_created"

    elif "update_user_preferences" in tool_names:
        response_type = "preference_updated"

    elif "delete_task" in tool_names:
        response_type = "task_deleted"

    else:
        response_type = "text"

    # بررسی خطای اجرای ابزار
    failed_results = [
        item["result"]
        for item in tool_results
        if isinstance(item["result"], dict)
        and item["result"].get("success") is False
    ]

    if failed_results:
        return error_response(
            message=message,
            error_code="TOOL_EXECUTION_FAILED",
            details=str(failed_results)
        )

    return success_response(
        response_type=response_type,
        message=message,
        data=data
    )
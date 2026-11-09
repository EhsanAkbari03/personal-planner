from enum import Enum


class ResponseType(str, Enum):

    TEXT = "text"

    DAILY_AGENDA = "daily_agenda"

    TASK_LIST = "task_list"
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"

    HABIT_LIST = "habit_list"
    HABIT_CREATED = "habit_created"
    HABIT_UPDATED = "habit_updated"

    FREE_SLOTS = "free_slots"

    PREFERENCE_UPDATED = "preference_updated"

    CLARIFICATION = "clarification"

    ERROR = "error"
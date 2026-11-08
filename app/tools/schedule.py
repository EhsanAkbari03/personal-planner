from app.services.schedule_services import get_free_slots , update_user_preferences , get_user_preferences


def get_free_slots_tool(user_id: int, date: str):
    return get_free_slots(
        user_id=user_id,
        date=date
    )

def get_user_preferences_tool(user_id: int):
    return get_user_preferences(user_id=user_id)

def update_user_preferences_tool(user_id: int, preferences: dict):
    return update_user_preferences(
        user_id=user_id,
        preferences=preferences
    )

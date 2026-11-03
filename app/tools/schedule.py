from app.services.schedule_services import get_free_slots


def get_free_slots_tool(user_id: int, date: str):
    return get_free_slots(
        user_id=user_id,
        date=date
    )
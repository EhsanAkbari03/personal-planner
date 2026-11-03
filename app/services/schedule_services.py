
from datetime import datetime, date as Date, time, timedelta

from app.tools.task import get_tasks_by_date
from app.tools.habit import get_habits_by_date


def parse_date(value):
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, Date):
        return value

    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()


def parse_datetime(value):
    if isinstance(value, datetime):
        return value

    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def parse_time(value):
    if isinstance(value, time):
        return value

    return time.fromisoformat(str(value))


def get_free_slots(
    user_id: int,
    date: str,
    day_start: str = "07:00",
    day_end: str = "23:00",
    min_duration_minutes: int = 30
):
    target_date = parse_date(date)

    day_start_time = parse_time(day_start)
    day_end_time = parse_time(day_end)

    day_start_dt = datetime.combine(target_date, day_start_time)
    day_end_dt = datetime.combine(target_date, day_end_time)

    if day_end_dt <= day_start_dt:
        raise ValueError("day_end must be later than day_start")

    # 1. دریافت تسک‌ها و عادت‌ها
    tasks_result = get_tasks_by_date(user_id=user_id, date=target_date.isoformat())
    habits = get_habits_by_date(user_id=user_id, date=target_date.isoformat())

    tasks = tasks_result.get("tasks", [])

    # 2. جمع‌آوری تمام بازه‌های مشغول
    busy_slots = []

    # تسک‌ها
    for task in tasks:
        start_at = parse_datetime(task["start_at"])

        if task.get("end_at"):
            end_at = parse_datetime(task["end_at"])
        else:
            end_at = start_at + timedelta(minutes=60)

        if end_at <= start_at:
            continue

        busy_slots.append({
            "start": start_at,
            "end": end_at,
            "title": task.get("title", "Task"),
            "type": "task"
        })

    # عادت‌ها
    for habit in habits:
        scheduled_time = habit.get("scheduled_time")

        # عادتی که ساعت مشخص ندارد، زمان مشغول ایجاد نمی‌کند
        if not scheduled_time:
            continue

        start_time = parse_time(scheduled_time)

        duration = habit.get("estimated_duration_minutes") or 60
        duration = int(duration)

        if duration <= 0:
            continue

        start_at = datetime.combine(target_date, start_time)
        end_at = start_at + timedelta(minutes=duration)

        busy_slots.append({
            "start": start_at,
            "end": end_at,
            "title": habit.get("title", "Habit"),
            "type": "habit"
        })

    # 3. محدود کردن بازه‌های مشغول به محدوده روز
    clipped_slots = []

    for slot in busy_slots:
        start = max(slot["start"], day_start_dt)
        end = min(slot["end"], day_end_dt)

        if start < end:
            clipped_slots.append({
                **slot,
                "start": start,
                "end": end
            })

    # 4. مرتب‌سازی
    clipped_slots.sort(key=lambda x: x["start"])

    # 5. ادغام بازه‌های هم‌پوشان
    merged_slots = []

    for slot in clipped_slots:
        if not merged_slots:
            merged_slots.append({
                "start": slot["start"],
                "end": slot["end"],
                "items": [{
                    "title": slot["title"],
                    "type": slot["type"]
                }]
            })
            continue

        last = merged_slots[-1]

        if slot["start"] <= last["end"]:
            last["end"] = max(last["end"], slot["end"])

            last["items"].append({
                "title": slot["title"],
                "type": slot["type"]
            })
        else:
            merged_slots.append({
                "start": slot["start"],
                "end": slot["end"],
                "items": [{
                    "title": slot["title"],
                    "type": slot["type"]
                }]
            })

    # 6. محاسبه بازه‌های آزاد
    free_slots = []
    current_time = day_start_dt

    for slot in merged_slots:
        if slot["start"] > current_time:
            duration = int(
                (slot["start"] - current_time).total_seconds() / 60
            )

            if duration >= min_duration_minutes:
                free_slots.append({
                    "start": current_time.isoformat(),
                    "end": slot["start"].isoformat(),
                    "duration_minutes": duration
                })

        current_time = max(current_time, slot["end"])

    # زمان آزاد بعد از آخرین بازه مشغول
    if current_time < day_end_dt:
        duration = int(
            (day_end_dt - current_time).total_seconds() / 60
        )

        if duration >= min_duration_minutes:
            free_slots.append({
                "start": current_time.isoformat(),
                "end": day_end_dt.isoformat(),
                "duration_minutes": duration
            })

    return {
        "date": target_date.isoformat(),
        "busy_slots": [
            {
                "start": slot["start"].isoformat(),
                "end": slot["end"].isoformat(),
                "items": slot["items"]
            }
            for slot in merged_slots
        ],
        "free_slots": free_slots,
        "total_free_minutes": sum(
            slot["duration_minutes"] for slot in free_slots
        )
    }

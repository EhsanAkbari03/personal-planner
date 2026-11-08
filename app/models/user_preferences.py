
from dataclasses import dataclass
from datetime import time, datetime
from typing import Optional


@dataclass
class UserPreferences:

    user_id: int

    # Sleep and wake-up schedule
    wake_up_time: Optional[time] = None
    sleep_time: Optional[time] = None

    # Daily planning boundaries
    day_start_time: Optional[time] = time(7, 0)
    day_end_time: Optional[time] = time(23, 0)

    # Preferred working hours
    preferred_work_start: Optional[time] = None
    preferred_work_end: Optional[time] = None

    # Focus and break settings
    focus_duration_minutes: int = 50
    break_duration_minutes: int = 10

    # Planning preferences
    planning_style: str = "balanced"
    max_daily_tasks: int = 5

    # Exercise preference
    preferred_exercise_time: Optional[time] = None

    # Metadata
    updated_at: Optional[datetime] = None

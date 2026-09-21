# app/models/habit_model.py

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class HabitCreate:
    title: str

    description: Optional[str] = None

    # daily / weekly / monthly / yearly
    frequency_type: str = "daily"

    weekdays: Optional[List[int]] = None

    day_of_month: Optional[int] = None

    month_of_year: Optional[int] = None

    reminder_time: Optional[str] = None

    checkin_time: Optional[str] = None

    points: int = 10
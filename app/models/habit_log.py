from dataclasses import dataclass
from datetime import date


@dataclass
class HabitLogCreate:
    habit_id: int
    scheduled_date: date
    status: str


@dataclass
class HabitLog:
    id: int
    habit_id: int
    scheduled_date: date
    status: str
    points_earned: int
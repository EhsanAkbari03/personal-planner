
from dataclasses import dataclass
from datetime import datetime


VALID_CATEGORIES = {
    "fitness",
    "family_relationships",
    "routines_goals",
    "education",
    "work_projects",
    "shopping_finance",
}


@dataclass
class Task:
    id: int | None
    user_id: int
    title: str
    description: str | None
    start_at: datetime
    end_at: datetime | None
    priority: int
    status: str
    category: str = "routines_goals",

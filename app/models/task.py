from dataclasses import dataclass
from datetime import datetime
from typing import Optional


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
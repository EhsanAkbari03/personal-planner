from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: int | None
    username: str | None
    email: str | None
    password_hash: str | None
    timezone: str
    created_at: datetime | None
    updated_at: datetime | None


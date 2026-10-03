from dataclasses import dataclass
from datetime import datetime, date


@dataclass
class User:
    id: int | None
    username: str | None
    email: str | None
    password_hash: str | None
    timezone: str
    created_at: datetime | None
    updated_at: datetime | None
    profile_image_uri: str | None = None
    subscription_level: str = "عادی"
    active_days_streak: int = 0
    last_login_date: date | None = None
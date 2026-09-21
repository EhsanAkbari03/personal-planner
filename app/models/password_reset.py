from dataclasses import dataclass
from datetime import datetime


@dataclass
class PasswordResetCode:
    id: int
    user_id: int
    code: str
    expires_at: datetime
    used: bool
    created_at: datetime
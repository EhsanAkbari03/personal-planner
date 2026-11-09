from pydantic import BaseModel
from typing import Optional, Any


class ChatResponse(BaseModel):
    success: bool
    type: str
    message: str

    data: Optional[dict[str, Any]] = None
    error: Optional[dict[str, Any]] = None
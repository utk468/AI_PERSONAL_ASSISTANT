# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from typing import Optional


class ReminderRequest(BaseModel):
    text: str

class ReminderIntent(BaseModel):
    task: str
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    time_of_day: Optional[str] = None
    date_str: Optional[str] = None
    priority: str = "medium"
    extracted_datetime: Optional[str] = None

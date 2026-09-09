from typing import TypedDict, Optional
from datetime import datetime
from backend.schemas import ReminderIntent

class IntentState(TypedDict):
    text: str
    current_time: datetime
    intent: Optional[ReminderIntent]
    is_valid: bool
    error_msg: Optional[str]
    retries: int

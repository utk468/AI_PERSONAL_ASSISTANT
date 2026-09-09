# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
from typing import Optional

class ReminderDB(BaseModel):
    id: str = Field(..., description="Unique reminder ID.")
    task: str = Field(..., description="Core task of the reminder.")
    priority: str = Field(..., description="Priority level.")
    is_recurring: bool = Field(..., description="Whether recurring or not.")
    recurrence_pattern: Optional[str] = Field(None, description="Pattern description.")
    time_of_day: Optional[str] = Field(None, description="Time of day in HH:MM format.")
    date_str: Optional[str] = Field(None, description="Target run date.")
    next_run_time: str = Field(..., description="Next scheduled execution time (ISO YYYY-MM-DDTHH:MM:SS).")
    created_at: str = Field(..., description="Creation timestamp.")
    status: str = Field("active", description="Status of reminder: 'active', 'completed', 'disabled'.")
    original_text: str = Field(..., description="Original user text prompt.")

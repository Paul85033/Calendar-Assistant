from pydantic import BaseModel
from typing import Optional


class CalendarEvent(BaseModel):
    summary: str
    description: Optional[str]
    start: str  
    end: str    
    timezone: Optional[str] = "UTC"

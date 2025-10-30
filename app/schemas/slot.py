from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class SlotBase(BaseModel):
    employee_id: int
    date: date
    start_hour: int = Field(..., ge=0, le=23)
    start_minute: int = Field(0, ge=0, le=59)
    duration_hours: int = Field(1, ge=0, le=12)
    duration_minutes: int = Field(0, ge=0, le=59)
    title: str = Field(..., min_length=1, max_length=200)
    category: str = Field("a", pattern="^[apecol ms]$")
    comment: Optional[str] = Field(None, max_length=500)


class SlotCreate(SlotBase):
    pass


class SlotUpdate(BaseModel):
    employee_id: Optional[int] = None
    date: Optional[date] = None
    start_hour: Optional[int] = Field(None, ge=0, le=23)
    start_minute: Optional[int] = Field(None, ge=0, le=59)
    duration_hours: Optional[int] = Field(None, ge=0, le=12)
    duration_minutes: Optional[int] = Field(None, ge=0, le=59)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, pattern="^[apecol ms]$")
    comment: Optional[str] = Field(None, max_length=500)


class Slot(SlotBase):
    id: int
    created_at: datetime
    updated_at: datetime
    start_time_str: str
    end_time_str: str

    class Config:
        from_attributes = True


class WeekPlanningResponse(BaseModel):
    """Réponse pour une semaine de planning"""
    employee_id: int
    week_start: date
    slots: List[Slot]
    
    class Config:
        from_attributes = True

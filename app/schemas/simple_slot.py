from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class SimpleSlotBase(BaseModel):
    employee_id: int
    date: date
    day_of_week: int = Field(..., ge=0, le=6, description="0=Lundi, 6=Dimanche")
    start_time: int = Field(..., ge=0, lt=1440, description="Minutes depuis 00:00")
    end_time: int = Field(..., ge=0, lt=1440, description="Minutes depuis 00:00")
    title: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., pattern="^[apecol ms]$", description="Category code")
    comment: Optional[str] = Field(None, max_length=500)


class SimpleSlotCreate(SimpleSlotBase):
    pass


class SimpleSlotUpdate(BaseModel):
    employee_id: Optional[int] = None
    date: Optional[date] = None
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    start_time: Optional[int] = Field(None, ge=0, lt=1440)
    end_time: Optional[int] = Field(None, ge=0, lt=1440)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, pattern="^[apecol ms]$")
    comment: Optional[str] = Field(None, max_length=500)


class SimpleSlot(SimpleSlotBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WeekPlanningResponse(BaseModel):
    """Réponse pour une semaine de planning"""
    employee_id: int
    week_start: date
    slots: list[SimpleSlot]
    
    class Config:
        from_attributes = True
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date
from .slot import Slot
from .note import Note
from .employee import Employee
from .common import WeekTotals, CategoryRepartition


class WeekBase(BaseModel):
    employee_id: int
    kind_id: int
    vacation_id: Optional[int] = None
    week_start_date: date = Field(..., description="Monday of the week (ISO)")
    meta: Dict[str, Any] = Field(default_factory=dict)


# Nouveau schéma simplifié pour la création
class WeekCreateSimple(BaseModel):
    employee_id: int
    kind: str = Field(..., description="Week kind: type|current|next|vacation")
    vacation: Optional[str] = Field(None, description="Vacation period: Toussaint|Noel|Paques|Ete")
    week_start_date: date = Field(..., description="Monday of the week (ISO)")
    meta: Dict[str, Any] = Field(default_factory=dict)


class WeekCreate(WeekBase):
    pass


class WeekUpdate(BaseModel):
    employee_id: Optional[int] = None
    kind_id: Optional[int] = None
    vacation_id: Optional[int] = None
    week_start_date: Optional[date] = None
    meta: Optional[Dict[str, Any]] = None


class Week(WeekBase):
    id: int

    class Config:
        from_attributes = True


class WeekResponse(BaseModel):
    week: Week
    slots: List[Slot]
    notes: Optional[Note]
    totals: WeekTotals
    repartition: CategoryRepartition

    class Config:
        from_attributes = True
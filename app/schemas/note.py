from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class NoteBase(BaseModel):
    hours_total: Optional[Decimal] = Field(None, ge=0, le=168, description="Total hours for the week")
    comments: Optional[str] = Field(None, max_length=1000)
    last_edit_by: Optional[str] = Field(None, max_length=100)


class NoteCreate(NoteBase):
    week_id: int


class NoteUpdate(BaseModel):
    hours_total: Optional[Decimal] = Field(None, ge=0, le=168)
    comments: Optional[str] = Field(None, max_length=1000)
    last_edit_by: Optional[str] = Field(None, max_length=100)


class Note(NoteBase):
    id: int
    week_id: int
    last_edit_at: datetime

    class Config:
        from_attributes = True
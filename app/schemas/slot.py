from pydantic import BaseModel, Field, validator
from typing import Optional


class SlotBase(BaseModel):
    day_index: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    start_min: int = Field(..., ge=0, lt=1440, description="Minutes since 00:00")
    duration_min: int = Field(..., gt=0, description="Duration in minutes, multiple of 15")
    title: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., pattern="^[apecol ms]$", description="Category code")
    comment: Optional[str] = Field(None, max_length=500)

    @validator('duration_min')
    def duration_must_be_multiple_of_15(cls, v):
        if v % 15 != 0:
            raise ValueError('Duration must be a multiple of 15 minutes')
        return v

    @validator('category')
    def category_must_be_valid(cls, v):
        valid_categories = {'a', 'p', 'e', 'c', 'o', 'l', 'm', 's'}
        if v not in valid_categories:
            raise ValueError(f'Category must be one of: {valid_categories}')
        return v


class SlotCreate(SlotBase):
    week_id: int


class SlotUpdate(BaseModel):
    day_index: Optional[int] = Field(None, ge=0, le=6)
    start_min: Optional[int] = Field(None, ge=0, lt=1440)
    duration_min: Optional[int] = Field(None, gt=0)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, pattern="^[apecol ms]$")
    comment: Optional[str] = Field(None, max_length=500)

    @validator('duration_min')
    def duration_must_be_multiple_of_15(cls, v):
        if v is not None and v % 15 != 0:
            raise ValueError('Duration must be a multiple of 15 minutes')
        return v


class Slot(SlotBase):
    id: int
    week_id: int

    class Config:
        from_attributes = True

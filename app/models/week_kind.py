from sqlalchemy import Column, Integer, String, Enum
from app.database import Base
import enum


class WeekKindEnum(str, enum.Enum):
    TYPE = "type"
    CURRENT = "current"
    NEXT = "next"
    VACATION = "vacation"


class WeekKind(Base):
    __tablename__ = "week_kind"

    id = Column(Integer, primary_key=True, index=True)
    kind = Column(Enum(WeekKindEnum), unique=True, nullable=False)
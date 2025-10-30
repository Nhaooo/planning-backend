from sqlalchemy import Column, Integer, String
from app.database import Base
import enum


class VacationPeriodEnum(str, enum.Enum):
    TOUSSAINT = "Toussaint"
    NOEL = "Noel"
    PAQUES = "Paques"
    ETE = "Ete"


class VacationPeriod(Base):
    __tablename__ = "vacation_period"

    id = Column(Integer, primary_key=True, index=True)
    period = Column(String(50), unique=True, nullable=False)
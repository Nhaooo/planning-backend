from sqlalchemy import Column, Integer, ForeignKey, Date, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Week(Base):
    __tablename__ = "weeks"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    kind_id = Column(Integer, ForeignKey("week_kind.id"), nullable=False)
    vacation_id = Column(Integer, ForeignKey("vacation_period.id"), nullable=True)
    week_start_date = Column(Date, nullable=False)  # Lundi ISO
    meta = Column(JSON, default=dict)  # Ex: heures d'ouverture

    # Relations
    employee = relationship("Employee", backref="weeks")
    kind = relationship("WeekKind")
    vacation = relationship("VacationPeriod")
    slots = relationship("Slot", back_populates="week", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="week", cascade="all, delete-orphan")

    # Contrainte d'unicité
    __table_args__ = (
        UniqueConstraint('employee_id', 'kind_id', 'vacation_id', 'week_start_date', 
                        name='unique_employee_week'),
    )
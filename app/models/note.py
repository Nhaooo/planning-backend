from sqlalchemy import Column, Integer, ForeignKey, Text, DECIMAL, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    week_id = Column(Integer, ForeignKey("weeks.id"), nullable=False)
    hours_total = Column(DECIMAL(5, 2), nullable=True)
    comments = Column(Text, nullable=True)
    last_edit_by = Column(String(100), nullable=True)
    last_edit_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relations
    week = relationship("Week", back_populates="notes")
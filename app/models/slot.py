from sqlalchemy import Column, Integer, ForeignKey, String, Text, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Slot(Base):
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True, index=True)
    week_id = Column(Integer, ForeignKey("weeks.id"), nullable=False)
    day_index = Column(Integer, nullable=False)  # 0=Mon...6=Sun
    start_min = Column(Integer, nullable=False)  # Minutes depuis 00:00
    duration_min = Column(Integer, nullable=False)  # Multiple de 15
    title = Column(Text, nullable=False)
    category = Column(String(1), nullable=False)  # a,p,e,c,o,l,m,s
    comment = Column(Text, nullable=True)

    # Relations
    week = relationship("Week", back_populates="slots")

    # Contraintes
    __table_args__ = (
        CheckConstraint('day_index >= 0 AND day_index <= 6', name='valid_day_index'),
        CheckConstraint('start_min >= 0 AND start_min < 1440', name='valid_start_min'),
        CheckConstraint('duration_min % 15 = 0', name='duration_multiple_15'),
        CheckConstraint("category IN ('a','p','e','c','o','l','m','s')", name='valid_category'),
    )
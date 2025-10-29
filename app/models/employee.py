from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(50), unique=True, index=True, nullable=False)
    fullname = Column(String(100), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
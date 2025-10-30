from sqlalchemy import Column, Integer, String, Date, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class SimpleSlot(Base):
    """Modèle ultra-simple pour les créneaux de planning"""
    __tablename__ = "simple_slots"

    id = Column(Integer, primary_key=True, index=True)
    
    # Informations de base
    employee_id = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)  # Date du créneau (YYYY-MM-DD)
    day_of_week = Column(Integer, nullable=False)  # 0=Lundi, 6=Dimanche
    
    # Horaires (en minutes depuis 00:00)
    start_time = Column(Integer, nullable=False)  # Ex: 480 = 8h00
    end_time = Column(Integer, nullable=False)    # Ex: 600 = 10h00
    
    # Contenu
    title = Column(String(200), nullable=False)
    category = Column(String(1), nullable=False)  # a,p,e,c,o,l,m,s
    comment = Column(Text, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<SimpleSlot(id={self.id}, employee={self.employee_id}, date={self.date}, title='{self.title}')>"
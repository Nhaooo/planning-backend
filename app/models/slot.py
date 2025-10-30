from sqlalchemy import Column, Integer, String, Date, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Slot(Base):
    """Modèle ultra-simple pour les créneaux de planning"""
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True, index=True)
    
    # Informations de base
    employee_id = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)  # Date du créneau (YYYY-MM-DD)
    
    # Horaires (format simple)
    start_hour = Column(Integer, nullable=False)  # Heure de début (ex: 9 pour 9h)
    start_minute = Column(Integer, nullable=False, default=0)  # Minutes de début (ex: 30 pour 9h30)
    duration_hours = Column(Integer, nullable=False, default=1)  # Durée en heures
    duration_minutes = Column(Integer, nullable=False, default=0)  # Minutes supplémentaires
    
    # Contenu
    title = Column(String(200), nullable=False)
    category = Column(String(1), nullable=False, default='a')  # a,p,e,c,o,l,m,s
    comment = Column(Text, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Slot(id={self.id}, employee={self.employee_id}, date={self.date}, title='{self.title}')>"
    
    @property
    def start_time_str(self):
        """Retourne l'heure de début au format HH:MM"""
        return f"{self.start_hour:02d}:{self.start_minute:02d}"
    
    @property
    def end_time_str(self):
        """Retourne l'heure de fin au format HH:MM"""
        end_hour = self.start_hour + self.duration_hours
        end_minute = self.start_minute + self.duration_minutes
        
        if end_minute >= 60:
            end_hour += 1
            end_minute -= 60
            
        return f"{end_hour:02d}:{end_minute:02d}"
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.models.slot import Slot
from app.schemas.slot import SlotCreate, SlotUpdate, WeekPlanningResponse


class SlotService:
    
    @staticmethod
    def get_week_planning(db: Session, employee_id: int, week_start: date) -> WeekPlanningResponse:
        """Récupère le planning d'une semaine pour un employé"""
        
        # Calculer la fin de semaine (dimanche)
        week_end = week_start + timedelta(days=6)
        
        # Récupérer tous les créneaux de la semaine
        slots = db.query(Slot).filter(
            Slot.employee_id == employee_id,
            Slot.date >= week_start,
            Slot.date <= week_end
        ).order_by(Slot.date, Slot.start_hour, Slot.start_minute).all()
        
        return WeekPlanningResponse(
            employee_id=employee_id,
            week_start=week_start,
            slots=slots
        )
    
    @staticmethod
    def create_slot(db: Session, slot_data: SlotCreate) -> Slot:
        """Crée un nouveau créneau"""
        
        # Vérifier les chevauchements
        existing_slots = db.query(Slot).filter(
            Slot.employee_id == slot_data.employee_id,
            Slot.date == slot_data.date
        ).all()
        
        # Calculer les heures de début et fin en minutes pour comparaison
        new_start_minutes = slot_data.start_hour * 60 + slot_data.start_minute
        new_end_minutes = new_start_minutes + (slot_data.duration_hours * 60) + slot_data.duration_minutes
        
        for existing in existing_slots:
            existing_start = existing.start_hour * 60 + existing.start_minute
            existing_end = existing_start + (existing.duration_hours * 60) + existing.duration_minutes
            
            # Vérifier si les horaires se chevauchent
            if not (new_end_minutes <= existing_start or new_start_minutes >= existing_end):
                raise ValueError(f"Chevauchement détecté avec le créneau '{existing.title}'")
        
        # Créer le créneau
        db_slot = Slot(**slot_data.dict())
        db.add(db_slot)
        db.commit()
        db.refresh(db_slot)
        return db_slot
    
    @staticmethod
    def update_slot(db: Session, slot_id: int, slot_update: SlotUpdate) -> Optional[Slot]:
        """Met à jour un créneau"""
        
        db_slot = db.query(Slot).filter(Slot.id == slot_id).first()
        if not db_slot:
            return None
        
        # Appliquer les modifications
        update_data = slot_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_slot, field, value)
        
        # Vérifier les chevauchements si les horaires ont changé
        if any(field in update_data for field in ['start_hour', 'start_minute', 'duration_hours', 'duration_minutes', 'date']):
            existing_slots = db.query(Slot).filter(
                Slot.employee_id == db_slot.employee_id,
                Slot.date == db_slot.date,
                Slot.id != slot_id
            ).all()
            
            new_start_minutes = db_slot.start_hour * 60 + db_slot.start_minute
            new_end_minutes = new_start_minutes + (db_slot.duration_hours * 60) + db_slot.duration_minutes
            
            for existing in existing_slots:
                existing_start = existing.start_hour * 60 + existing.start_minute
                existing_end = existing_start + (existing.duration_hours * 60) + existing.duration_minutes
                
                if not (new_end_minutes <= existing_start or new_start_minutes >= existing_end):
                    raise ValueError(f"Chevauchement détecté avec le créneau '{existing.title}'")
        
        db.commit()
        db.refresh(db_slot)
        return db_slot
    
    @staticmethod
    def delete_slot(db: Session, slot_id: int) -> bool:
        """Supprime un créneau"""
        
        db_slot = db.query(Slot).filter(Slot.id == slot_id).first()
        if not db_slot:
            return False
        
        db.delete(db_slot)
        db.commit()
        return True
    
    @staticmethod
    def get_slot_by_id(db: Session, slot_id: int) -> Optional[Slot]:
        """Récupère un créneau par son ID"""
        return db.query(Slot).filter(Slot.id == slot_id).first()
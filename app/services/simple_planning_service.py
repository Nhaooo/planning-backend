from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.models.simple_slot import SimpleSlot
from app.schemas.simple_slot import SimpleSlotCreate, SimpleSlotUpdate, WeekPlanningResponse


class SimplePlanningService:
    
    @staticmethod
    def get_week_planning(db: Session, employee_id: int, week_start: date) -> WeekPlanningResponse:
        """Récupère le planning d'une semaine pour un employé"""
        
        # Calculer la fin de semaine (dimanche)
        week_end = week_start + timedelta(days=6)
        
        # Récupérer tous les créneaux de la semaine
        slots = db.query(SimpleSlot).filter(
            SimpleSlot.employee_id == employee_id,
            SimpleSlot.date >= week_start,
            SimpleSlot.date <= week_end
        ).order_by(SimpleSlot.date, SimpleSlot.start_time).all()
        
        return WeekPlanningResponse(
            employee_id=employee_id,
            week_start=week_start,
            slots=slots
        )
    
    @staticmethod
    def create_slot(db: Session, slot_data: SimpleSlotCreate, exclude_id: int = None) -> SimpleSlot:
        """Crée un nouveau créneau"""
        
        # Vérifier les chevauchements
        existing_slots = db.query(SimpleSlot).filter(
            SimpleSlot.employee_id == slot_data.employee_id,
            SimpleSlot.date == slot_data.date
        ).all()
        
        for existing in existing_slots:
            # Ignorer le créneau qu'on est en train de déplacer
            if exclude_id and existing.id == exclude_id:
                continue
                
            # Vérifier si les horaires se chevauchent
            if not (slot_data.end_time <= existing.start_time or slot_data.start_time >= existing.end_time):
                raise ValueError(f"Chevauchement détecté avec le créneau '{existing.title}'")
        
        # Créer le créneau
        db_slot = SimpleSlot(**slot_data.dict())
        db.add(db_slot)
        db.commit()
        db.refresh(db_slot)
        return db_slot
    
    @staticmethod
    def update_slot(db: Session, slot_id: int, slot_update: SimpleSlotUpdate) -> Optional[SimpleSlot]:
        """Met à jour un créneau"""
        
        db_slot = db.query(SimpleSlot).filter(SimpleSlot.id == slot_id).first()
        if not db_slot:
            return None
        
        # Appliquer les modifications
        update_data = slot_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_slot, field, value)
        
        # Vérifier les chevauchements si les horaires ont changé
        if 'start_time' in update_data or 'end_time' in update_data or 'date' in update_data:
            existing_slots = db.query(SimpleSlot).filter(
                SimpleSlot.employee_id == db_slot.employee_id,
                SimpleSlot.date == db_slot.date,
                SimpleSlot.id != slot_id
            ).all()
            
            for existing in existing_slots:
                if not (db_slot.end_time <= existing.start_time or db_slot.start_time >= existing.end_time):
                    raise ValueError(f"Chevauchement détecté avec le créneau '{existing.title}'")
        
        db.commit()
        db.refresh(db_slot)
        return db_slot
    
    @staticmethod
    def delete_slot(db: Session, slot_id: int) -> bool:
        """Supprime un créneau"""
        
        db_slot = db.query(SimpleSlot).filter(SimpleSlot.id == slot_id).first()
        if not db_slot:
            return False
        
        db.delete(db_slot)
        db.commit()
        return True
    
    @staticmethod
    def get_slot_by_id(db: Session, slot_id: int) -> Optional[SimpleSlot]:
        """Récupère un créneau par son ID"""
        return db.query(SimpleSlot).filter(SimpleSlot.id == slot_id).first()
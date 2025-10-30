from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import date
from app.models.week import Week
from app.models.slot import Slot
from app.models.note import Note
from app.schemas.week import WeekCreate, WeekCreateSimple, WeekUpdate, WeekResponse
from app.schemas.slot import SlotCreate, SlotUpdate
from app.services.calculation_service import CalculationService


class WeekService:
    
    @staticmethod
    def get_week_with_details(db: Session, week_id: int) -> Optional[WeekResponse]:
        """Récupère une semaine avec tous ses détails et calculs"""
        week = db.query(Week).filter(Week.id == week_id).first()
        if not week:
            return None
        
        slots = db.query(Slot).filter(Slot.week_id == week_id).all()
        note = db.query(Note).filter(Note.week_id == week_id).first()
        
        # Calculs automatiques
        totals = CalculationService.calculate_week_totals(slots)
        repartition = CalculationService.calculate_category_repartition(slots)
        
        return WeekResponse(
            week=week,
            slots=slots,
            notes=note,
            totals=totals,
            repartition=repartition
        )
    
    @staticmethod
    def get_weeks(db: Session, employee_id: Optional[int] = None, 
                  kind: Optional[str] = None, vacation: Optional[str] = None,
                  week_start: Optional[date] = None) -> List[WeekResponse]:
        """Récupère les semaines selon les filtres"""
        query = db.query(Week)
        
        if employee_id:
            query = query.filter(Week.employee_id == employee_id)
        if kind:
            # Jointure avec week_kind pour filtrer par type
            query = query.join(Week.kind).filter(Week.kind.has(kind=kind))
        if vacation:
            # Jointure avec vacation_period pour filtrer par période
            query = query.join(Week.vacation).filter(Week.vacation.has(period=vacation))
        if week_start:
            query = query.filter(Week.week_start_date == week_start)
        
        weeks = query.all()
        
        # Construire les réponses complètes
        results = []
        for week in weeks:
            slots = db.query(Slot).filter(Slot.week_id == week.id).all()
            note = db.query(Note).filter(Note.week_id == week.id).first()
            
            totals = CalculationService.calculate_week_totals(slots)
            repartition = CalculationService.calculate_category_repartition(slots)
            
            results.append(WeekResponse(
                week=week,
                slots=slots,
                notes=note,
                totals=totals,
                repartition=repartition
            ))
        
        return results
    
    @staticmethod
    def create_week(db: Session, week_data: WeekCreate) -> Week:
        """Crée une nouvelle semaine"""
        db_week = Week(**week_data.dict())
        db.add(db_week)
        db.commit()
        db.refresh(db_week)
        return db_week
    
    @staticmethod
    def create_week_simple(db: Session, week_data: WeekCreateSimple) -> Week:
        """Crée une nouvelle semaine avec conversion automatique des strings vers IDs"""
        # Mapping des strings vers IDs
        kind_mapping = {
            'type': 1,
            'current': 2,
            'next': 3,
            'vacation': 4
        }
        
        vacation_mapping = {
            'Toussaint': 1,
            'Noel': 2,
            'Paques': 3,
            'Ete': 4
        }
        
        # Conversion vers le format attendu par la base
        week_dict = {
            'employee_id': week_data.employee_id,
            'kind_id': kind_mapping.get(week_data.kind, 2),  # Default to 'current'
            'week_start_date': week_data.week_start_date,
            'meta': week_data.meta
        }
        
        # Ajouter vacation_id si spécifié
        if week_data.vacation and week_data.vacation in vacation_mapping:
            week_dict['vacation_id'] = vacation_mapping[week_data.vacation]
        
        db_week = Week(**week_dict)
        db.add(db_week)
        db.commit()
        db.refresh(db_week)
        return db_week
    
    @staticmethod
    def update_week(db: Session, week_id: int, week_update: WeekUpdate) -> Optional[WeekResponse]:
        """Met à jour une semaine"""
        db_week = db.query(Week).filter(Week.id == week_id).first()
        if not db_week:
            return None
        
        update_data = week_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_week, field, value)
        
        db.commit()
        db.refresh(db_week)
        
        return WeekService.get_week_with_details(db, week_id)
    
    @staticmethod
    def create_slot(db: Session, slot_data: SlotCreate) -> Optional[Slot]:
        """Crée un nouveau créneau avec vérification de chevauchement"""
        # Vérifier que la semaine existe
        week = db.query(Week).filter(Week.id == slot_data.week_id).first()
        if not week:
            return None
        
        # Récupérer les créneaux existants pour vérifier les chevauchements
        existing_slots = db.query(Slot).filter(Slot.week_id == slot_data.week_id).all()
        
        # Créer un objet temporaire pour la vérification
        temp_slot = Slot(**slot_data.dict())
        
        # Vérifier les chevauchements
        if CalculationService.check_slot_overlap(existing_slots, temp_slot):
            raise ValueError("Slot overlap detected")
        
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
        
        # Si on modifie la position/durée, vérifier les chevauchements
        update_data = slot_update.dict(exclude_unset=True)
        if any(field in update_data for field in ['day_index', 'start_min', 'duration_min']):
            # Appliquer temporairement les modifications
            temp_slot = Slot(**db_slot.__dict__)
            for field, value in update_data.items():
                setattr(temp_slot, field, value)
            
            # Récupérer les autres créneaux
            other_slots = db.query(Slot).filter(
                Slot.week_id == db_slot.week_id,
                Slot.id != slot_id
            ).all()
            
            if CalculationService.check_slot_overlap(other_slots, temp_slot):
                raise ValueError("Slot overlap detected")
        
        # Appliquer les modifications
        for field, value in update_data.items():
            setattr(db_slot, field, value)
        
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
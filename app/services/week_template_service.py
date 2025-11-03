from typing import Optional, List
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.week import Week
from app.models.slot import Slot
from app.models.note import Note
from app.schemas.week import WeekResponse, WeekCreateSimple
from app.services.week_service import WeekService
from app.services.calculation_service import CalculationService


class WeekTemplateService:
    """
    Service pour gérer la logique des 4 types de semaines selon les spécifications :
    
    1. Semaine type : Modèle principal et persistant pour chaque employé
    2. Semaine actuelle : Copie de la semaine type pour la semaine en cours
    3. Semaine suivante : Prévision de la semaine à venir, générée à partir de la semaine type
    4. Semaine vacances : Période spéciale basée sur la semaine type avec horaires spécifiques
    """
    
    @staticmethod
    def get_template_week(db: Session, employee_id: int) -> Optional[WeekResponse]:
        """Récupère la semaine type d'un employé (modèle persistant)"""
        template_week = db.query(Week).filter(
            Week.employee_id == employee_id,
            Week.kind_id == 1  # TYPE = 1
        ).first()
        
        if not template_week:
            return None
            
        return WeekService.get_week_with_details(db, template_week.id)
    
    @staticmethod
    def create_template_week(db: Session, employee_id: int) -> WeekResponse:
        """Crée une semaine type pour un employé (date fixe 2024-01-01)"""
        # Vérifier si une semaine type existe déjà
        existing = db.query(Week).filter(
            Week.employee_id == employee_id,
            Week.kind_id == 1
        ).first()
        
        if existing:
            return WeekService.get_week_with_details(db, existing.id)
        
        # Créer la semaine type avec date fixe
        week_data = WeekCreateSimple(
            employee_id=employee_id,
            kind='type',
            week_start_date=date(2024, 1, 1),  # Date fixe pour la semaine type
            meta={"is_template": True, "created_automatically": True}
        )
        
        db_week = WeekService.create_week_simple(db, week_data)
        return WeekService.get_week_with_details(db, db_week.id)
    
    @staticmethod
    def duplicate_from_template(db: Session, employee_id: int, target_kind: str, 
                               week_start: date, vacation_period: Optional[str] = None) -> WeekResponse:
        """
        Duplique la semaine type vers une autre semaine (actuelle, suivante, ou vacances)
        
        Args:
            employee_id: ID de l'employé
            target_kind: 'current', 'next', ou 'vacation'
            week_start: Date de début de la semaine cible
            vacation_period: Période de vacances si target_kind='vacation'
        """
        # Récupérer la semaine type
        template = WeekTemplateService.get_template_week(db, employee_id)
        if not template:
            # Créer automatiquement une semaine type vide si elle n'existe pas
            template = WeekTemplateService.create_template_week(db, employee_id)
        
        # Supprimer la semaine existante du même type et période si elle existe
        existing_query = db.query(Week).filter(
            Week.employee_id == employee_id,
            Week.week_start_date == week_start
        )
        
        if target_kind == 'current':
            existing_query = existing_query.filter(Week.kind_id == 2)
        elif target_kind == 'next':
            existing_query = existing_query.filter(Week.kind_id == 3)
        elif target_kind == 'vacation':
            existing_query = existing_query.filter(Week.kind_id == 4)
        
        existing = existing_query.first()
        if existing:
            # Supprimer les créneaux et notes existants
            db.query(Slot).filter(Slot.week_id == existing.id).delete()
            db.query(Note).filter(Note.week_id == existing.id).delete()
            db.delete(existing)
            db.commit()
        
        # Créer la nouvelle semaine
        week_data = WeekCreateSimple(
            employee_id=employee_id,
            kind=target_kind,
            week_start_date=week_start,
            vacation=vacation_period,
            meta={
                "duplicated_from_template": True,
                "template_week_id": template.week.id,
                "created_at": date.today().isoformat()
            }
        )
        
        new_week = WeekService.create_week_simple(db, week_data)
        
        # Dupliquer tous les créneaux de la semaine type
        for slot in template.slots:
            new_slot = Slot(
                week_id=new_week.id,
                day_index=slot.day_index,
                start_min=slot.start_min,
                duration_min=slot.duration_min,
                title=slot.title,
                category=slot.category,
                comment=slot.comment
            )
            db.add(new_slot)
        
        # Dupliquer les notes si elles existent
        if template.notes:
            new_note = Note(
                week_id=new_week.id,
                hours_total=template.notes.hours_total,
                comments=f"Copié depuis semaine type - {template.notes.comments or ''}",
                last_edit_by="system",
                last_edit_at=date.today()
            )
            db.add(new_note)
        
        db.commit()
        return WeekService.get_week_with_details(db, new_week.id)
    
    @staticmethod
    def reset_from_template(db: Session, week_id: int) -> Optional[WeekResponse]:
        """
        Remet à zéro une semaine en la dupliquant depuis la semaine type
        (Bouton 'Reprendre depuis la semaine type')
        """
        # Récupérer la semaine à réinitialiser
        target_week = db.query(Week).filter(Week.id == week_id).first()
        if not target_week:
            return None
        
        # Ne pas permettre de réinitialiser la semaine type elle-même
        if target_week.kind_id == 1:  # TYPE
            raise ValueError("Cannot reset template week from itself")
        
        # Déterminer le type de semaine
        kind_mapping = {1: 'type', 2: 'current', 3: 'next', 4: 'vacation'}
        target_kind = kind_mapping.get(target_week.kind_id, 'current')
        
        # Récupérer la période de vacances si applicable
        vacation_period = None
        if target_week.vacation_id:
            vacation_mapping = {1: 'Toussaint', 2: 'Noel', 3: 'Paques', 4: 'Ete'}
            vacation_period = vacation_mapping.get(target_week.vacation_id)
        
        # Dupliquer depuis la semaine type
        return WeekTemplateService.duplicate_from_template(
            db, 
            target_week.employee_id, 
            target_kind, 
            target_week.week_start_date,
            vacation_period
        )
    
    @staticmethod
    def copy_next_to_current(db: Session, employee_id: int, current_week_start: date) -> Optional[WeekResponse]:
        """
        Copie la semaine suivante vers la semaine actuelle
        (Utilisé en fin de semaine pour passer à la suivante)
        """
        # Calculer la date de la semaine suivante
        next_week_start = current_week_start + timedelta(days=7)
        
        # Récupérer la semaine suivante
        next_week = db.query(Week).filter(
            Week.employee_id == employee_id,
            Week.kind_id == 3,  # NEXT
            Week.week_start_date == next_week_start
        ).first()
        
        if not next_week:
            # Si pas de semaine suivante, créer depuis template
            return WeekTemplateService.duplicate_from_template(
                db, employee_id, 'current', current_week_start
            )
        
        # Supprimer la semaine actuelle existante
        existing_current = db.query(Week).filter(
            Week.employee_id == employee_id,
            Week.kind_id == 2,  # CURRENT
            Week.week_start_date == current_week_start
        ).first()
        
        if existing_current:
            db.query(Slot).filter(Slot.week_id == existing_current.id).delete()
            db.query(Note).filter(Note.week_id == existing_current.id).delete()
            db.delete(existing_current)
            db.commit()
        
        # Créer la nouvelle semaine actuelle
        week_data = WeekCreateSimple(
            employee_id=employee_id,
            kind='current',
            week_start_date=current_week_start,
            meta={
                "copied_from_next": True,
                "source_week_id": next_week.id,
                "created_at": date.today().isoformat()
            }
        )
        
        new_current = WeekService.create_week_simple(db, week_data)
        
        # Copier tous les créneaux de la semaine suivante
        next_slots = db.query(Slot).filter(Slot.week_id == next_week.id).all()
        for slot in next_slots:
            new_slot = Slot(
                week_id=new_current.id,
                day_index=slot.day_index,
                start_min=slot.start_min,
                duration_min=slot.duration_min,
                title=slot.title,
                category=slot.category,
                comment=slot.comment
            )
            db.add(new_slot)
        
        # Copier les notes
        next_note = db.query(Note).filter(Note.week_id == next_week.id).first()
        if next_note:
            new_note = Note(
                week_id=new_current.id,
                hours_total=next_note.hours_total,
                comments=f"Copié depuis semaine suivante - {next_note.comments or ''}",
                last_edit_by="system",
                last_edit_at=date.today()
            )
            db.add(new_note)
        
        db.commit()
        return WeekService.get_week_with_details(db, new_current.id)
    
    @staticmethod
    def ensure_template_exists(db: Session, employee_id: int) -> WeekResponse:
        """S'assure qu'une semaine type existe pour un employé"""
        template = WeekTemplateService.get_template_week(db, employee_id)
        if not template:
            template = WeekTemplateService.create_template_week(db, employee_id)
        return template
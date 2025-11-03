from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.week import WeekResponse
from app.services.week_template_service import WeekTemplateService

router = APIRouter()


@router.get("/template/{employee_id}", response_model=WeekResponse)
def get_template_week(employee_id: int, db: Session = Depends(get_db)):
    """Récupère la semaine type d'un employé (modèle persistant)"""
    template = WeekTemplateService.get_template_week(db, employee_id)
    if not template:
        # Créer automatiquement si n'existe pas
        template = WeekTemplateService.create_template_week(db, employee_id)
    return template


@router.post("/template/{employee_id}", response_model=WeekResponse)
def create_template_week(employee_id: int, db: Session = Depends(get_db)):
    """Crée ou récupère la semaine type d'un employé"""
    return WeekTemplateService.ensure_template_exists(db, employee_id)


@router.post("/duplicate-from-template", response_model=WeekResponse)
def duplicate_from_template(
    employee_id: int = Query(..., description="ID de l'employé"),
    target_kind: str = Query(..., description="Type de semaine cible: current|next|vacation"),
    week_start: date = Query(..., description="Date de début de semaine (lundi)"),
    vacation_period: Optional[str] = Query(None, description="Période de vacances si target_kind=vacation"),
    db: Session = Depends(get_db)
):
    """
    Duplique la semaine type vers une autre semaine
    
    - **current**: Semaine actuelle (copie modifiable)
    - **next**: Semaine suivante (prévision)
    - **vacation**: Semaine vacances (période spéciale)
    """
    if target_kind not in ['current', 'next', 'vacation']:
        raise HTTPException(status_code=400, detail="target_kind must be: current, next, or vacation")
    
    if target_kind == 'vacation' and not vacation_period:
        raise HTTPException(status_code=400, detail="vacation_period required when target_kind=vacation")
    
    try:
        return WeekTemplateService.duplicate_from_template(
            db, employee_id, target_kind, week_start, vacation_period
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reset-from-template/{week_id}", response_model=WeekResponse)
def reset_from_template(week_id: int, db: Session = Depends(get_db)):
    """
    Remet à zéro une semaine en la dupliquant depuis la semaine type
    (Bouton 'Reprendre depuis la semaine type')
    """
    try:
        result = WeekTemplateService.reset_from_template(db, week_id)
        if not result:
            raise HTTPException(status_code=404, detail="Week not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/copy-next-to-current", response_model=WeekResponse)
def copy_next_to_current(
    employee_id: int = Query(..., description="ID de l'employé"),
    current_week_start: date = Query(..., description="Date de début de la semaine actuelle"),
    db: Session = Depends(get_db)
):
    """
    Copie la semaine suivante vers la semaine actuelle
    (Utilisé en fin de semaine pour passer à la suivante)
    """
    try:
        result = WeekTemplateService.copy_next_to_current(db, employee_id, current_week_start)
        if not result:
            raise HTTPException(status_code=404, detail="Unable to create current week")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auto-create/{employee_id}")
def auto_create_weeks(
    employee_id: int,
    week_start: date = Query(..., description="Date de début de semaine"),
    db: Session = Depends(get_db)
):
    """
    Crée automatiquement toutes les semaines manquantes pour un employé
    (template, current, next) basées sur la semaine type
    """
    try:
        # S'assurer que la semaine type existe
        template = WeekTemplateService.ensure_template_exists(db, employee_id)
        
        results = {
            "template": template,
            "current": None,
            "next": None
        }
        
        # Créer semaine actuelle si manquante
        try:
            current = WeekTemplateService.duplicate_from_template(
                db, employee_id, 'current', week_start
            )
            results["current"] = current
        except Exception as e:
            print(f"Erreur création semaine actuelle: {e}")
        
        # Créer semaine suivante si manquante
        try:
            from datetime import timedelta
            next_week_start = week_start + timedelta(days=7)
            next_week = WeekTemplateService.duplicate_from_template(
                db, employee_id, 'next', next_week_start
            )
            results["next"] = next_week
        except Exception as e:
            print(f"Erreur création semaine suivante: {e}")
        
        return {
            "message": "Weeks auto-created successfully",
            "weeks": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
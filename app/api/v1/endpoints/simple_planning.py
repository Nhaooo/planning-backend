from typing import List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.simple_slot import SimpleSlot, SimpleSlotCreate, SimpleSlotUpdate, WeekPlanningResponse
from app.services.simple_planning_service import SimplePlanningService
from app.services.permissions import require_employee_or_admin, PermissionChecker

router = APIRouter()


@router.get("/week", response_model=WeekPlanningResponse)
def get_week_planning(
    employee_id: int = Query(..., description="ID de l'employé"),
    week_start: date = Query(..., description="Date de début de semaine (lundi)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_employee_or_admin)
):
    """Récupère le planning d'une semaine pour un employé"""
    # Vérifier les permissions d'accès aux données
    user_type = current_user.get("type")
    user_id = current_user.get("user_id")
    
    if not PermissionChecker.can_access_employee_data(user_type, user_id, employee_id):
        raise HTTPException(
            status_code=403, 
            detail="Accès refusé. Vous ne pouvez accéder qu'à vos propres données."
        )
    
    try:
        planning = SimplePlanningService.get_week_planning(db, employee_id, week_start)
        return planning
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/slots", response_model=SimpleSlot)
def create_slot(
    slot: SimpleSlotCreate, 
    exclude_id: int = Query(None), 
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_employee_or_admin)
):
    """Crée un nouveau créneau"""
    # Vérifier les permissions de modification
    user_type = current_user.get("type")
    user_id = current_user.get("user_id")
    
    if not PermissionChecker.can_modify_planning(user_type, user_id, slot.employee_id):
        raise HTTPException(
            status_code=403, 
            detail="Accès refusé. Vous ne pouvez modifier que vos propres plannings."
        )
    
    try:
        db_slot = SimplePlanningService.create_slot(db, slot, exclude_id)
        return db_slot
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/slots/{slot_id}", response_model=SimpleSlot)
def get_slot(slot_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_employee_or_admin)):
    """Récupère un créneau par son ID"""
    slot = SimplePlanningService.get_slot_by_id(db, slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Créneau non trouvé")
    
    # Vérifier les permissions d'accès aux données
    user_type = current_user.get("type")
    user_id = current_user.get("user_id")
    
    if not PermissionChecker.can_access_employee_data(user_type, user_id, slot.employee_id):
        raise HTTPException(
            status_code=403, 
            detail="Accès refusé. Vous ne pouvez accéder qu'à vos propres données."
        )
    
    return slot


@router.put("/slots/{slot_id}", response_model=SimpleSlot)
def update_slot(slot_id: int, slot_update: SimpleSlotUpdate, db: Session = Depends(get_db), current_user: dict = Depends(require_employee_or_admin)):
    """Met à jour un créneau"""
    # D'abord récupérer le slot pour vérifier les permissions
    existing_slot = SimplePlanningService.get_slot_by_id(db, slot_id)
    if not existing_slot:
        raise HTTPException(status_code=404, detail="Créneau non trouvé")
    
    # Vérifier les permissions de modification
    user_type = current_user.get("type")
    user_id = current_user.get("user_id")
    
    if not PermissionChecker.can_modify_planning(user_type, user_id, existing_slot.employee_id):
        raise HTTPException(
            status_code=403, 
            detail="Accès refusé. Vous ne pouvez modifier que vos propres plannings."
        )
    
    try:
        slot = SimplePlanningService.update_slot(db, slot_id, slot_update)
        if not slot:
            raise HTTPException(status_code=404, detail="Créneau non trouvé")
        return slot
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/slots/{slot_id}")
def delete_slot(slot_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_employee_or_admin)):
    """Supprime un créneau"""
    # D'abord récupérer le slot pour vérifier les permissions
    existing_slot = SimplePlanningService.get_slot_by_id(db, slot_id)
    if not existing_slot:
        raise HTTPException(status_code=404, detail="Créneau non trouvé")
    
    # Vérifier les permissions de modification
    user_type = current_user.get("type")
    user_id = current_user.get("user_id")
    
    if not PermissionChecker.can_modify_planning(user_type, user_id, existing_slot.employee_id):
        raise HTTPException(
            status_code=403, 
            detail="Accès refusé. Vous ne pouvez modifier que vos propres plannings."
        )
    
    success = SimplePlanningService.delete_slot(db, slot_id)
    if not success:
        raise HTTPException(status_code=404, detail="Créneau non trouvé")
    return {"message": "Créneau supprimé avec succès"}
from typing import List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.simple_slot import SimpleSlot, SimpleSlotCreate, SimpleSlotUpdate, WeekPlanningResponse
from app.services.simple_planning_service import SimplePlanningService

router = APIRouter()


@router.get("/week", response_model=WeekPlanningResponse)
def get_week_planning(
    employee_id: int = Query(..., description="ID de l'employé"),
    week_start: date = Query(..., description="Date de début de semaine (lundi)"),
    db: Session = Depends(get_db)
):
    """Récupère le planning d'une semaine pour un employé"""
    try:
        planning = SimplePlanningService.get_week_planning(db, employee_id, week_start)
        return planning
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/slots", response_model=SimpleSlot)
def create_slot(slot: SimpleSlotCreate, exclude_id: int = Query(None), db: Session = Depends(get_db)):
    """Crée un nouveau créneau"""
    try:
        db_slot = SimplePlanningService.create_slot(db, slot, exclude_id)
        return db_slot
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/slots/{slot_id}", response_model=SimpleSlot)
def get_slot(slot_id: int, db: Session = Depends(get_db)):
    """Récupère un créneau par son ID"""
    slot = SimplePlanningService.get_slot_by_id(db, slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Créneau non trouvé")
    return slot


@router.put("/slots/{slot_id}", response_model=SimpleSlot)
def update_slot(slot_id: int, slot_update: SimpleSlotUpdate, db: Session = Depends(get_db)):
    """Met à jour un créneau"""
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
def delete_slot(slot_id: int, db: Session = Depends(get_db)):
    """Supprime un créneau"""
    success = SimplePlanningService.delete_slot(db, slot_id)
    if not success:
        raise HTTPException(status_code=404, detail="Créneau non trouvé")
    return {"message": "Créneau supprimé avec succès"}
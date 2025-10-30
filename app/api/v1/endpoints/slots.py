from typing import List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.slot import Slot, SlotCreate, SlotUpdate, WeekPlanningResponse
from app.services.slot_service import SlotService

router = APIRouter()


@router.get("/week", response_model=WeekPlanningResponse)
def get_week_planning(
    employee_id: int = Query(..., description="ID de l'employé"),
    week_start: date = Query(..., description="Date de début de semaine (lundi)"),
    db: Session = Depends(get_db)
):
    """Récupère le planning d'une semaine pour un employé"""
    try:
        planning = SlotService.get_week_planning(db, employee_id, week_start)
        return planning
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/", response_model=Slot)
def create_slot(slot: SlotCreate, db: Session = Depends(get_db)):
    """Crée un nouveau créneau"""
    try:
        db_slot = SlotService.create_slot(db, slot)
        return db_slot
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{slot_id}", response_model=Slot)
def get_slot(slot_id: int, db: Session = Depends(get_db)):
    """Récupère un créneau par son ID"""
    slot = SlotService.get_slot_by_id(db, slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Créneau non trouvé")
    return slot


@router.put("/{slot_id}", response_model=Slot)
def update_slot(slot_id: int, slot_update: SlotUpdate, db: Session = Depends(get_db)):
    """Met à jour un créneau"""
    try:
        slot = SlotService.update_slot(db, slot_id, slot_update)
        if not slot:
            raise HTTPException(status_code=404, detail="Créneau non trouvé")
        return slot
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{slot_id}")
def delete_slot(slot_id: int, db: Session = Depends(get_db)):
    """Supprime un créneau"""
    success = SlotService.delete_slot(db, slot_id)
    if not success:
        raise HTTPException(status_code=404, detail="Créneau non trouvé")
    return {"message": "Créneau supprimé avec succès"}
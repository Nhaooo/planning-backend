from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.week import WeekResponse, WeekCreate, WeekUpdate
from app.schemas.slot import SlotCreate, SlotUpdate, Slot
from app.services.week_service import WeekService

router = APIRouter()


@router.get("/", response_model=List[WeekResponse])
def get_weeks(
    employee_id: Optional[int] = Query(None, description="Filter by employee ID"),
    kind: Optional[str] = Query(None, description="Filter by week kind (type|current|next|vacation)"),
    vacation: Optional[str] = Query(None, description="Filter by vacation period"),
    week_start: Optional[date] = Query(None, description="Filter by week start date"),
    db: Session = Depends(get_db)
):
    """Récupère les semaines selon les filtres"""
    weeks = WeekService.get_weeks(db, employee_id, kind, vacation, week_start)
    return weeks


@router.get("/{week_id}", response_model=WeekResponse)
def get_week(week_id: int, db: Session = Depends(get_db)):
    """Récupère une semaine avec tous ses détails"""
    week = WeekService.get_week_with_details(db, week_id)
    if not week:
        raise HTTPException(status_code=404, detail="Week not found")
    return week


@router.post("/", response_model=WeekResponse)
def create_week(week: WeekCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle semaine"""
    try:
        db_week = WeekService.create_week(db, week)
        return WeekService.get_week_with_details(db, db_week.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{week_id}", response_model=WeekResponse)
def update_week(week_id: int, week_update: WeekUpdate, db: Session = Depends(get_db)):
    """Met à jour une semaine"""
    week = WeekService.update_week(db, week_id, week_update)
    if not week:
        raise HTTPException(status_code=404, detail="Week not found")
    return week


@router.post("/{week_id}/slots", response_model=Slot)
def create_slot(week_id: int, slot: SlotCreate, db: Session = Depends(get_db)):
    """Crée un nouveau créneau dans une semaine"""
    # Forcer le week_id du slot
    slot.week_id = week_id
    
    try:
        db_slot = WeekService.create_slot(db, slot)
        if not db_slot:
            raise HTTPException(status_code=404, detail="Week not found")
        return db_slot
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{week_id}/slots/{slot_id}", response_model=Slot)
def update_slot(week_id: int, slot_id: int, slot_update: SlotUpdate, db: Session = Depends(get_db)):
    """Met à jour un créneau"""
    try:
        slot = WeekService.update_slot(db, slot_id, slot_update)
        if not slot:
            raise HTTPException(status_code=404, detail="Slot not found")
        return slot
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{week_id}/slots/{slot_id}")
def delete_slot(week_id: int, slot_id: int, db: Session = Depends(get_db)):
    """Supprime un créneau"""
    success = WeekService.delete_slot(db, slot_id)
    if not success:
        raise HTTPException(status_code=404, detail="Slot not found")
    return {"message": "Slot deleted successfully"}
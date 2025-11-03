from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.employee import Employee, EmployeeCreate, EmployeeUpdate
from app.services.employee_service import EmployeeService
from app.services.permissions import require_admin

router = APIRouter()


@router.get("/", response_model=List[Employee])
def get_employees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Récupère la liste des employés actifs (admin uniquement)"""
    employees = EmployeeService.get_all(db, skip=skip, limit=limit)
    return employees


@router.get("/{employee_id}", response_model=Employee)
def get_employee(employee_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Récupère un employé par son ID (admin uniquement)"""
    employee = EmployeeService.get_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.post("/", response_model=Employee)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Crée un nouvel employé (admin uniquement)"""
    # Vérifier que le slug n'existe pas déjà
    existing = EmployeeService.get_by_slug(db, employee.slug)
    if existing:
        raise HTTPException(status_code=400, detail="Employee slug already exists")
    
    return EmployeeService.create(db, employee)


@router.put("/{employee_id}", response_model=Employee)
def update_employee(employee_id: int, employee_update: EmployeeUpdate, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Met à jour un employé (admin uniquement)"""
    employee = EmployeeService.update(db, employee_id, employee_update)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.delete("/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db), current_user: dict = Depends(require_admin)):
    """Supprime (désactive) un employé (admin uniquement)"""
    success = EmployeeService.delete(db, employee_id)
    if not success:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}
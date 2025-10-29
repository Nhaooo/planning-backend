from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


class EmployeeService:
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Employee]:
        """Récupère tous les employés"""
        return db.query(Employee).filter(Employee.active == True).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_id(db: Session, employee_id: int) -> Optional[Employee]:
        """Récupère un employé par son ID"""
        return db.query(Employee).filter(Employee.id == employee_id).first()
    
    @staticmethod
    def get_by_slug(db: Session, slug: str) -> Optional[Employee]:
        """Récupère un employé par son slug"""
        return db.query(Employee).filter(Employee.slug == slug).first()
    
    @staticmethod
    def create(db: Session, employee: EmployeeCreate) -> Employee:
        """Crée un nouvel employé"""
        db_employee = Employee(**employee.dict())
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        return db_employee
    
    @staticmethod
    def update(db: Session, employee_id: int, employee_update: EmployeeUpdate) -> Optional[Employee]:
        """Met à jour un employé"""
        db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not db_employee:
            return None
        
        update_data = employee_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_employee, field, value)
        
        db.commit()
        db.refresh(db_employee)
        return db_employee
    
    @staticmethod
    def delete(db: Session, employee_id: int) -> bool:
        """Supprime (désactive) un employé"""
        db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not db_employee:
            return False
        
        db_employee.active = False
        db.commit()
        return True
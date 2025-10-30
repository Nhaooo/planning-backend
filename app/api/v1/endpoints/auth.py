from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.auth_service import AuthService
from app.services.employee_service import EmployeeService
from app.database import get_db
from app.config import settings

router = APIRouter()
security = HTTPBearer()


class AdminLoginRequest(BaseModel):
    pin: str


class EmployeeLoginRequest(BaseModel):
    employee_slug: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_type: str
    user_name: str
    user_id: int


@router.post("/login/admin", response_model=TokenResponse)
def login_admin(login_request: AdminLoginRequest):
    """Authentification administrateur par PIN"""
    if not AuthService.verify_pin(login_request.pin):
        raise HTTPException(status_code=401, detail="Invalid PIN")
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = AuthService.create_access_token(
        data={"sub": "admin", "type": "admin", "user_id": 0}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": "admin",
        "user_name": "Administrateur",
        "user_id": 0
    }


@router.post("/login/employee", response_model=TokenResponse)
def login_employee(login_request: EmployeeLoginRequest, db: Session = Depends(get_db)):
    """Authentification employé par slug"""
    employee = EmployeeService.get_by_slug(db, login_request.employee_slug)
    
    if not employee or not employee.active:
        raise HTTPException(status_code=401, detail="Employee not found or inactive")
    
    access_token_expires = timedelta(hours=8)  # Token plus long pour les employés
    access_token = AuthService.create_access_token(
        data={
            "sub": employee.slug, 
            "type": "employee", 
            "user_id": employee.id,
            "employee_slug": employee.slug
        }, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": "employee",
        "user_name": employee.fullname,
        "user_id": employee.id
    }


# Endpoint de compatibilité (garde l'ancien pour ne pas casser)
@router.post("/login", response_model=TokenResponse)
def login_legacy(login_request: AdminLoginRequest):
    """Authentification par PIN (compatibilité)"""
    return login_admin(login_request)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Vérifie le token JWT"""
    payload = AuthService.verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


def verify_backup_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Vérifie le token de backup"""
    if not AuthService.verify_backup_secret(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid backup secret")
    return True
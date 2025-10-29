from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.services.auth_service import AuthService
from app.config import settings

router = APIRouter()
security = HTTPBearer()


class LoginRequest(BaseModel):
    pin: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


@router.post("/login", response_model=TokenResponse)
def login(login_request: LoginRequest):
    """Authentification par PIN"""
    if not AuthService.verify_pin(login_request.pin):
        raise HTTPException(status_code=401, detail="Invalid PIN")
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = AuthService.create_access_token(
        data={"sub": "admin"}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


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
from functools import wraps
from typing import Optional, Callable
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import AuthService

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Vérifie le token JWT et retourne les informations utilisateur"""
    payload = AuthService.verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token invalide")
    return payload


def require_admin(current_user: dict = Depends(get_current_user)):
    """Vérifie que l'utilisateur est un administrateur"""
    if current_user.get("type") != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Accès refusé. Droits administrateur requis."
        )
    return current_user


def require_employee_or_admin(current_user: dict = Depends(get_current_user)):
    """Vérifie que l'utilisateur est un employé ou un administrateur"""
    user_type = current_user.get("type")
    if user_type not in ["admin", "employee"]:
        raise HTTPException(
            status_code=403, 
            detail="Accès refusé. Authentification requise."
        )
    return current_user


def require_own_data_or_admin(employee_id: int, current_user: dict = Depends(get_current_user)):
    """Vérifie que l'utilisateur accède à ses propres données ou est admin"""
    user_type = current_user.get("type")
    
    # Admin peut accéder à tout
    if user_type == "admin":
        return current_user
    
    # Employé ne peut accéder qu'à ses propres données
    if user_type == "employee":
        user_employee_id = current_user.get("user_id")
        if user_employee_id != employee_id:
            raise HTTPException(
                status_code=403, 
                detail="Accès refusé. Vous ne pouvez accéder qu'à vos propres données."
            )
        return current_user
    
    raise HTTPException(
        status_code=403, 
        detail="Accès refusé. Authentification requise."
    )


class PermissionChecker:
    """Classe utilitaire pour vérifier les permissions"""
    
    @staticmethod
    def can_manage_employees(user_type: str) -> bool:
        """Vérifie si l'utilisateur peut gérer les employés"""
        return user_type == "admin"
    
    @staticmethod
    def can_view_all_plannings(user_type: str) -> bool:
        """Vérifie si l'utilisateur peut voir tous les plannings"""
        return user_type == "admin"
    
    @staticmethod
    def can_access_employee_data(user_type: str, user_id: int, target_employee_id: int) -> bool:
        """Vérifie si l'utilisateur peut accéder aux données d'un employé"""
        if user_type == "admin":
            return True
        if user_type == "employee" and user_id == target_employee_id:
            return True
        return False
    
    @staticmethod
    def can_modify_planning(user_type: str, user_id: int, target_employee_id: int) -> bool:
        """Vérifie si l'utilisateur peut modifier un planning"""
        if user_type == "admin":
            return True
        if user_type == "employee" and user_id == target_employee_id:
            return True
        return False